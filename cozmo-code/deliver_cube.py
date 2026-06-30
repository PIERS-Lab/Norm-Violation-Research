import time
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose

def handle_cliff_detected(evt, **kw):
    robot = evt.obj
    print("[DEBUG] WARNING: Table edge detected! Aborting current movement for safety.")
    # Forcefully abort whatever driving action Cozmo is currently doing
    robot.abort_all_actions()


def cozmo_program(robot):
    # type: (cozmo.robot.Robot) -> None
    
    # --- Phase 0: Initialize ---

    print("[DEBUG] Initializing safety cliff sensors...")
    robot.add_event_handler(cozmo.robot.EvtCliffDetected, handle_cliff_detected)

    print("[DEBUG] Initializing: Lowering lift and setting head angle...")
    robot.set_lift_height(0.0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()

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
                cube = robot.world.wait_for_observed_light_cube(timeout=1.0)
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
                relocate_action = robot.drive_straight(distance_mm(150), speed_mmps(50))
                relocate_action.wait_for_completed()
                
                # Safety check: Did we hit a cliff while trying to relocate?
                if relocate_action.is_cancelled or relocate_action.is_failure:
                    print("[DEBUG] ERROR: Relocation aborted safely by cliff detection. Exiting program.")
                    return
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
        print("[DEBUG] ERROR: Path planning failed, was blocked, or aborted by cliff detection.")
        return

    # Find cube again to correct odometry errors
    print("[DEBUG] Framing the cube in vision to correct coordinate drift...")
    robot.set_head_angle(degrees(-15)).wait_for_completed()
    
    # Pause to let the camera sensor read the markers and snap his internal map to the cube
    time.sleep(0.5)
    
    print("[DEBUG] Arrived at pre-dock position successfully. Switching to hard-coded sequence.")

    # --- Phase 3: Hard-Coded Approach (Drive forward into the cube slots) ---
    robot.set_lift_height(0.15).wait_for_completed()

    print("[DEBUG] Action [MANUAL]: Driving forward into the cube...")
    drive_forward = robot.drive_straight(distance_mm(105), speed_mmps(25))
    drive_forward.wait_for_completed()

    if drive_forward.is_cancelled or drive_forward.is_failure:
        print("[DEBUG] ERROR: Hard-coded approach aborted by cliff detection.")
        return

    # --- Phase 4: Hard-Coded Lift ---
    print("[DEBUG] Action [MANUAL]: Lifting the lift...")
    lift_up = robot.set_lift_height(1.0)
    lift_up.wait_for_completed()

    print("[DEBUG] Action [MANUAL]: Holding cube briefly...")
    time.sleep(1.5)

    # --- Phase 5: Hard-Coded Lower ---
    print("[DEBUG] Action [MANUAL]: Lowering the lift...")
    lift_down = robot.set_lift_height(0.0)
    lift_down.wait_for_completed()

    # --- Phase 6: Hard-Coded Retreat ---
    print("[DEBUG] Action [MANUAL]: Driving backwards away from the cube...")
    drive_backward = robot.drive_straight(distance_mm(-110), speed_mmps(40))
    drive_backward.wait_for_completed()

    print("[DEBUG] SUCCESS: Hybrid sequence complete!")

# Run the program
cozmo.run_program(cozmo_program)