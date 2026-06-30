import time
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose

def cozmo_program(robot):
    # type: (cozmo.robot.Robot) -> None
    
    # Phase 1: Initialize and look for the cube
    print("[DEBUG] Initializing: Lowering lift and setting head angle...")
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()

    print("[DEBUG] Searching for a LightCube...")
    cube = None
    try:
        cube = robot.world.wait_for_observed_light_cube(timeout=5.0)
        print("[DEBUG] Confirmation: Found cube! ID: {}".format(cube.cube_id))
    except Exception as e:
        print("[DEBUG] ERROR: No cube observed within 5 seconds.")
        return

    # Phase 2: Autonomous Navigation to "Pre-Dock" position
    print("[DEBUG] Action: Calculating autonomous route to the cube...")
    
    # Define an offset exactly 20mm directly in front of the cube's face.
    # We use define_pose_relative_this to transform this into global coordinates.
    pre_dock_pose = Pose(-20, 0, 0, angle_z=degrees(0))
    target_pose = cube.pose.define_pose_relative_this(pre_dock_pose)

    print("[DEBUG] Action: Planning path and navigating autonomously...")
    navigate_action = robot.go_to_pose(target_pose)
    navigate_action.wait_for_completed()
    print("[DEBUG] Navigation finished. Status: {}".format(navigate_action.state))

    if not navigate_action.has_succeeded:
        print("[DEBUG] ERROR: Path planning failed or was blocked.")
        return

    print("[DEBUG] Arrived at pre-dock position successfully. Switching to hard-coded sequence.")

    # Phase 3: Hard-Coded Approach (Drive forward into the cube slots)
    print("[DEBUG] Action [MANUAL]: Driving forward into the cube...")
    drive_forward = robot.drive_straight(distance_mm(55), speed_mmps(40))
    drive_forward.wait_for_completed()

    # Phase 4: Hard-Coded Lift
    print("[DEBUG] Action [MANUAL]: Lifting the lift...")
    lift_up = robot.set_lift_height(1.0)
    lift_up.wait_for_completed()

    print("[DEBUG] Action [MANUAL]: Holding cube briefly...")
    time.sleep(1.5)

    # Phase 5: Hard-Coded Lower
    print("[DEBUG] Action [MANUAL]: Lowering the lift...")
    lift_down = robot.set_lift_height(0.0)
    lift_down.wait_for_completed()

    # Phase 6: Hard-Coded Retreat
    print("[DEBUG] Action [MANUAL]: Driving backwards away from the cube...")
    drive_backward = robot.drive_straight(distance_mm(-60), speed_mmps(40))
    drive_backward.wait_for_completed()

    print("[DEBUG] SUCCESS: Hybrid sequence complete!")

# Run the program
cozmo.run_program(cozmo_program)