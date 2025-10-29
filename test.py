import anki_vector
import anki_vector.connection
import anki_vector.util


def main():
    args = anki_vector.util.parse_command_args()

    with anki_vector.Robot(args.serial, behavior_control_level=anki_vector.connection.ControlPriorityLevel.DEFAULT_PRIORITY) as robot:
        robot.behavior.set_lift_height(1.0)
        print("calling drive straight")
        robot.behavior.drive_straight(anki_vector.util.distance_mm(100), anki_vector.util.speed_mmps(100))
        print("Calling go_to_pose")
        robot.behavior.go_to_pose(anki_vector.util.Pose(0, 0, 0, angle_z=anki_vector.util.Angle(0)))

if __name__ == '__main__':
    main()
