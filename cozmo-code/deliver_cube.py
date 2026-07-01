import time
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose

def cozmo_program(robot):
    # type: (cozmo.robot.Robot) -> None
    
    # --- Phase 0: Initialize ---

    print("[DEBUG] Initializing: Lowering lift and setting head angle...")
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()
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

    # --- Phase 4: Return to starting position ---
    print("[DEBUG] Action [AUTO]: Returning to initial start pose...")
    return_action = robot.go_to_pose(start_pose)
    return_action.wait_for_completed()
    if not return_action.has_succeeded:
        print("[DEBUG] WARNING: Return to start pose failed. Dropping cube at current pose.")

    # --- Phase 5: Drop-off ---
    print("[DEBUG] Action [MANUAL]: Lowering the lift to drop cube...")
    robot.set_lift_height(0.0).wait_for_completed()

    print("[DEBUG] SUCCESS: Pickup, return, and drop-off sequence complete!")

# Run the program
cozmo.run_program(cozmo_program)