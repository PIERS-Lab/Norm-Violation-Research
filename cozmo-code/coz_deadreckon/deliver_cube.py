import sys
import os
import math
import time
import subprocess
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
from dotenv import load_dotenv

# Load spatial configs from .env
load_dotenv()
INCH_TO_MM = 25.4


def sanitize_device_id(raw_value):
    """Normalizes serial strings loaded from .env or CLI args."""
    if raw_value is None:
        return None
    return raw_value.strip().strip('"').strip("'")

def get_coordinate_mm(prefix):
    """Safely pulls separate _X and _Y suffix variables out of the environment."""
    x_str = os.getenv(prefix + "_X")
    y_str = os.getenv(prefix + "_Y")
    
    if not x_str or not y_str:
        print("[ERROR] Missing X or Y component variables for: {}".format(prefix))
        print("Expected keys: {}_X and {}_Y in your .env".format(prefix, prefix))
        sys.exit(1)
        
    try:
        # No splitting or stripping required, raw values parse directly
        return float(x_str) * INCH_TO_MM, float(y_str) * INCH_TO_MM
    except ValueError:
        print("[ERROR] Non-numeric value found in environment variables for {}".format(prefix))
        sys.exit(1)

def calculate_relative_pose(start_x, start_y, target_x, target_y, angle_deg=0):
    """Calculates a target Pose relative to Cozmo's local coordinate frame."""
    delta_x = target_x - start_x
    delta_y = target_y - start_y
    return Pose(delta_x, delta_y, 0, angle_z=degrees(angle_deg))

def parse_arguments():
    """Parses system arguments for the targeted trial profile."""
    if len(sys.argv) < 4:
        print("\n[ERROR] Missing arguments!")
        print("Usage: python deliver_cube.py [robot_id] [cube_loc] [zone_loc] [optional_device_id]")
        print("Example: python deliver_cube.py near near near\n")
        sys.exit(1)
    robot_id = sys.argv[1].lower()
    cube_loc = sys.argv[2].lower()
    zone_loc = sys.argv[3].lower()
    device_id = sanitize_device_id(sys.argv[4]) if len(sys.argv) >= 5 else None
    return robot_id, cube_loc, zone_loc, device_id


def build_android_connector(device_id):
    """Builds an AndroidConnector across Cozmo SDK variants."""
    try:
        import cozmo.run as cozmo_run
        connector_cls = getattr(cozmo_run, "AndroidConnector", None)
    except Exception:
        connector_cls = None

    if connector_cls is None:
        raise RuntimeError("AndroidConnector is not available in this Cozmo SDK build.")

    candidate_kwargs = (
        {"device_id": device_id},
        {"serial": device_id},
        {"adb_device": device_id},
        {"adb_serial": device_id},
        {"android_device_id": device_id},
    )

    for kwargs in candidate_kwargs:
        try:
            return connector_cls(**kwargs)
        except TypeError:
            continue

    try:
        return connector_cls(device_id)
    except TypeError:
        raise RuntimeError("Could not construct AndroidConnector with this SDK version.")


def clear_adb_forwards(device_id):
    """Best-effort cleanup so parallel robot runs don't inherit stale forwards."""
    subprocess.call(["adb", "-s", device_id, "forward", "--remove-all"])

# Parse trial arguments
robot_id, cube_loc, zone_loc, cli_device_id = parse_arguments()

DEVICE_1_ID = sanitize_device_id(os.getenv("DEVICE_1_ID"))
DEVICE_2_ID = sanitize_device_id(os.getenv("DEVICE_2_ID"))

# Map the starting position keys based on the robot ID passed by the bash script
if robot_id == "near":
    start_x, start_y = get_coordinate_mm("COZ1_START_POS")
    default_device_id = DEVICE_1_ID
else:
    start_x, start_y = get_coordinate_mm("COZ2_START_POS")
    default_device_id = DEVICE_2_ID

selected_device_id = sanitize_device_id(cli_device_id or default_device_id)

# Construct and fetch absolute target markers
cube_x, cube_y = get_coordinate_mm("CUBE_{}_POS".format(cube_loc.upper()))
zone_x, zone_y = get_coordinate_mm("ZONE_{}_POS".format(zone_loc.upper()))

# Navigation and spacing adjustments (in millimeters)
PRE_DOCK_STANDOFF_MM = 70  
DRIVE_SPEED = 60           # Slower speed drastically reduces track slippage

def cozmo_program(robot):
    print("\n=============================================")
    print("🤖 TARGET ACTIVE: {} COZMO".format(robot_id.upper()))
    print("📦 COORD TARGETS: Cube ({:.1f}mm), Zone ({:.1f}mm)".format(cube_x, zone_x))
    print("=============================================\n")
    
    robot.set_robot_volume(0.0) # Suppress generic animations/audio bias
    
    # Some Cozmo SDK builds do not implement world.set_custom_origin.
    # Use it when available, otherwise continue with the default world frame.
    if hasattr(robot.world, "set_custom_origin"):
        robot.world.set_custom_origin(Pose(0, 0, 0, angle_z=degrees(0)))
    else:
        print("[INFO] SDK has no set_custom_origin(); using default origin.")
    start_pose = Pose(0, 0, 0, angle_z=degrees(0))

    # --- Phase 1: Navigate blindly to Pre-Dock ---
    pre_dock_pose = calculate_relative_pose(start_x, start_y, cube_x - PRE_DOCK_STANDOFF_MM, cube_y)
    
    print("[NAV] Driving blindly to pre-dock position...")
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()
    robot.go_to_pose(pre_dock_pose).wait_for_completed()

    # --- Phase 2: Visual Relocalization Handshake ---
    print("[VISION] Lowering head to lock onto cube and snap map drift...")
    robot.set_head_angle(degrees(-15)).wait_for_completed()
    time.sleep(0.5) # Wait for camera shutter tracking adjustment
    
    try:
        # Snap map coordinates back into true physical alignment using the LightCube marker
        observed_cube = robot.world.wait_for_observed_light_cube(timeout=3.0)
        print("[VISION] Success! Relocalized using Cube ID: {}".format(observed_cube.cube_id))
        
        pickup_action = robot.pickup_object(observed_cube, num_retries=2)
        pickup_action.wait_for_completed()
    except Exception:
        # Fallback to absolute blind pickup if lighting changes or a frame drops
        print("[WARNING] Cube vision handshake timed out. Falling back to deterministic drive...")
        robot.drive_straight(distance_mm(PRE_DOCK_STANDOFF_MM + 15), speed_mmps(DRIVE_SPEED)).wait_for_completed()
        robot.set_lift_height(0.7, max_speed=3.0).wait_for_completed()

    # --- Phase 3: Deliver to Zone ---
    delivery_pose = calculate_relative_pose(start_x, start_y, zone_x - 30, zone_y)
    print("[NAV] Navigating to delivery zone...")
    robot.go_to_pose(delivery_pose).wait_for_completed()

    # --- Phase 4: Drop Off & Retract ---
    print("[DELIVERY] Depositing package...")
    robot.set_lift_height(0.0, max_speed=3.0).wait_for_completed()
    robot.drive_straight(distance_mm(-80), speed_mmps(DRIVE_SPEED)).wait_for_completed()

    # --- Phase 5: Safe Return Home ---
    print("[NAV] Returning to initial start pose...")
    robot.go_to_pose(start_pose).wait_for_completed()
    print("🏁 Run completed successfully.\n")

if __name__ == '__main__':
    if selected_device_id:
        print("[INIT] Binding {} robot to Android serial {}".format(robot_id.upper(), selected_device_id))
        clear_adb_forwards(selected_device_id)
        connector = build_android_connector(selected_device_id)
        cozmo.run_program(cozmo_program, connector=connector, use_3d_viewer=False, use_viewer=False)
    else:
        print("[WARNING] No device ID configured. Falling back to ANDROID_SERIAL/default connector behavior.")
        cozmo.run_program(cozmo_program)