import time
import math
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose

try:
    import apriltag
    import PIL.Image
    import numpy
    HAS_APRILTAG_DEPS = True
except ImportError:
    HAS_APRILTAG_DEPS = False

# Delivery tuning for fixed lab setup where tag zone is straight ahead of start pose.
TAG_ZONE_FORWARD_MM = 300
DELIVERY_SPEED_MMPS = 60

# AprilTag delivery tuning.
APRILTAG_FAMILY = "tag36h11"
APRILTAG_SIZE_M = 0.05
# fx, fy, cx, cy for Cozmo camera (from prior calibration in this repo).
CAMERA_PARAMS = (288.87, 288.36, 155.11, 111.40)
TAG_SEARCH_STEPS = 12
TAG_SEARCH_TURN_DEG = 30
TAG_DROPOFF_STANDOFF_MM = 140
TAG_APPROACH_MAX_ITERS = 4
TAG_APPROACH_MAX_TURN_DEG = 25
TAG_APPROACH_MAX_STEP_MM = 120
TAG_ALIGN_TOLERANCE_DEG = 4


def find_apriltag_pose(robot):
    # Returns (x_m, z_m) in camera frame where x is lateral and z is forward depth.
    if not HAS_APRILTAG_DEPS:
        print("[DEBUG] AprilTag deps not installed; skipping tag-guided delivery.")
        return None

    detector = apriltag.Detector(
        apriltag.DetectorOptions(
            families=APRILTAG_FAMILY,
            border=1,
            quad_decimate=0,
            refine_edges=True,
        )
    )

    for step in range(TAG_SEARCH_STEPS):
        print("[DEBUG] AprilTag scan step {}/{}...".format(step + 1, TAG_SEARCH_STEPS))

        # Sample a few frames at each heading to reduce one-frame misses.
        for _ in range(3):
            try:
                image_evt = robot.wait_for(cozmo.camera.EvtNewRawCameraImage, timeout=1.0)
            except Exception:
                print("[DEBUG] Camera frame timeout during tag scan; retrying...")
                continue
            grayscale = image_evt.image.convert("L")
            upscaled = grayscale.resize((640, 480), resample=PIL.Image.NEAREST)
            detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))

            if detections:
                pose_matrix, _, _ = detector.detection_pose(
                    detections[0],
                    CAMERA_PARAMS,
                    APRILTAG_SIZE_M,
                    +1,
                )
                x_m = pose_matrix[0][3]
                z_m = pose_matrix[2][3]
                print("[DEBUG] AprilTag found. x={:.3f}m z={:.3f}m".format(x_m, z_m))
                return x_m, z_m

        if step < TAG_SEARCH_STEPS - 1:
            robot.turn_in_place(degrees(TAG_SEARCH_TURN_DEG)).wait_for_completed()

    return None


def drive_to_tag_zone(robot):
    # Iteratively re-localize and approach the tag to reduce one-shot pose error.
    for step in range(TAG_APPROACH_MAX_ITERS):
        tag_pose = find_apriltag_pose(robot)
        if tag_pose is None:
            print("[DEBUG] AprilTag not visible during approach step {}.".format(step + 1))
            return False

        tag_x_m, tag_z_m = tag_pose
        turn_deg = -math.degrees(math.atan2(tag_x_m, tag_z_m))
        turn_deg = max(-TAG_APPROACH_MAX_TURN_DEG, min(TAG_APPROACH_MAX_TURN_DEG, turn_deg))

        if abs(turn_deg) > TAG_ALIGN_TOLERANCE_DEG:
            print("[DEBUG] Step {}: turning {:.1f} deg toward tag...".format(step + 1, turn_deg))
            robot.turn_in_place(degrees(turn_deg)).wait_for_completed()

        forward_mm = (tag_z_m * 1000.0) - TAG_DROPOFF_STANDOFF_MM
        if forward_mm <= 20:
            print("[DEBUG] Step {}: already within drop stand-off distance.".format(step + 1))
            return True

        step_mm = min(TAG_APPROACH_MAX_STEP_MM, forward_mm)
        print("[DEBUG] Step {}: driving {:.1f} mm toward tag...".format(step + 1, step_mm))
        action = robot.drive_straight(distance_mm(step_mm), speed_mmps(DELIVERY_SPEED_MMPS))
        action.wait_for_completed()
        if not action.has_succeeded:
            print("[DEBUG] Step {}: drive action did not succeed.".format(step + 1))
            return False

    # Last iteration performed a movement; this is still acceptable for drop zone delivery.
    return True

def cozmo_program(robot):
    # type: (cozmo.robot.Robot) -> None
    
    # --- Phase 0: Initialize ---

    print("[DEBUG] Initializing: Lowering lift and setting head angle...")
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()
    # Raw camera events for AprilTag scanning require image streaming to be enabled.
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = False
    time.sleep(0.2)
    start_pose = Pose(
        robot.pose.position.x,
        robot.pose.position.y,
        robot.pose.position.z,
        angle_z=robot.pose.rotation.angle_z,
        origin_id=robot.pose._origin_id,
    )

    # Suppress robot sounds
    print("[DEBUG] Muting robot audio...")
    robot.set_robot_volume(0.0)
    
    # --- Phase 1: Search Loop Setup ---
    cube = None
    relocation_attempts = 3
    current_relocation = 0

    while cube is None and current_relocation < relocation_attempts:
        print("[DEBUG] --- Starting Search Area {}/{} ---".format(current_relocation + 1, relocation_attempts))
        
        # Reset head angle at the start of every new position search
        robot.set_head_angle(degrees(0)).wait_for_completed()
        
        # Perform 8 turns to get a thorough 360-degree view (8 * 45 = 360)
        for turn_num in range(1, 9):
            print("[DEBUG] Position {}, Scan {}/8: Looking for LightCube...".format(current_relocation + 1, turn_num))
            try:
                # Wait up to 1 second for a cube to appear in Cozmo's vision
                cube = robot.world.wait_for_observed_light_cube(timeout=2.0)
                print("[DEBUG] Success: Found cube! ID: {}".format(cube.cube_id))
                break # Break out of the 8-turn loop if cube is found
            except Exception as e:
                print("[DEBUG] Cube not seen in this field of view.")
                if turn_num < 8:
                    print("[DEBUG] Turning 45 degrees left...")
                    robot.turn_in_place(degrees(45)).wait_for_completed()

        # If the 360 sweep finishes and no cube was found, relocate
        if cube is None:
            current_relocation += 1
            if current_relocation < relocation_attempts:
                print("[DEBUG] Complete 360 scan failed. Relocating to a new position...")
                # Drive forward 150mm to change vantage point
                robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
            else:
                print("[DEBUG] ERROR: Failed to find cube after 3 full 360-degree area searches. Exiting program.")
                return

    # --- Phase 2: Autonomous Navigation to "Pre-Dock" position ---
    print("[DEBUG] Action: Calculating autonomous route to the cube...")
    pre_dock_pose = Pose(-70, 0, 0, angle_z=degrees(0))
    target_pose = cube.pose.define_pose_relative_this(pre_dock_pose)

    print("[DEBUG] Action: Planning path and navigating autonomously...")
    navigate_action = robot.go_to_pose(target_pose)
    navigate_action.wait_for_completed()
    print("[DEBUG] Navigation finished. Status: {}".format(navigate_action.state))

    if not navigate_action.has_succeeded:
        print("[DEBUG] ERROR: Path planning failed or was blocked.")
        return

    # Find cube again to correct odometry errors
    print("[DEBUG] Framing the cube in vision to correct coordinate drift...")
    robot.set_head_angle(degrees(-15)).wait_for_completed()
    time.sleep(0.5)

    print("[DEBUG] Arrived at pre-dock position successfully. Switching to SDK pickup sequence.")

    # --- Phase 3: Pickup with built-in retries and alignment ---
    print("[DEBUG] Action [SDK]: Picking up observed cube with retries...")
    pickup_action = robot.pickup_object(cube, num_retries=3)
    pickup_action.wait_for_completed()

    if not pickup_action.has_succeeded:
        print("[DEBUG] ERROR: pickup_object failed. Status: {}".format(pickup_action.state))
        return

    print("[DEBUG] Action [SDK]: Holding cube briefly...")
    time.sleep(1.0)

    # --- Phase 4: Drive to tag-zone drop-off using AprilTag pose ---
    print("[DEBUG] Action [VISION]: Approaching apriltag delivery zone...")
    if not drive_to_tag_zone(robot):
        print("[DEBUG] WARNING: Tag-guided approach failed. Falling back to fixed forward delivery {} mm.".format(TAG_ZONE_FORWARD_MM))
        deliver_action = robot.drive_straight(
            distance_mm(TAG_ZONE_FORWARD_MM),
            speed_mmps(DELIVERY_SPEED_MMPS)
        )
        deliver_action.wait_for_completed()

    # --- Phase 5: Drop-off ---
    print("[DEBUG] Action [MANUAL]: Lowering the lift to drop cube near tag zone...")
    robot.set_lift_height(0.0).wait_for_completed()

    # --- Phase 6: Return to starting position ---
    print("[DEBUG] Action [AUTO]: Returning to initial start pose...")
    return_action = robot.go_to_pose(start_pose)
    return_action.wait_for_completed()
    if not return_action.has_succeeded:
        print("[DEBUG] WARNING: Return to start pose failed.")

    print("[DEBUG] SUCCESS: Pickup, tag-zone delivery, drop-off, and return complete!")

# Run the program
cozmo.run_program(cozmo_program)