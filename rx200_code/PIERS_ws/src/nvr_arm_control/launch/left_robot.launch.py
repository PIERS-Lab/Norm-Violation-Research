from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory
import os

arm_pkg_share = get_package_share_directory(
    "interbotix_xsarm_descriptions"
)

moveit_pkg_share = get_package_share_directory
(
    "interbotix_xsarm_moveit"
)

pkg_share = get_package_share_directory(
    "nvr_arm_control"
    )

urdf_path = os.path.join(
    arm_pkg_share,
    "urdf",
    "rx200.urdf.xacro"
)

srdf_path = os.path.join(
    moveit_pkg_share,
    "srdf",
    "rx200.srdf.xacro"
)

moveit_control_path = os.path.join(
    pkg_share, "config", "rx200_l_controllers.yaml"
)


def generate_launch_description():
    # 1. Define your custom namespace
    my_namespace = 'robot_1'

    # 2. Build MoveIt configurations 
    # Make sure your package name matches your moveit_config package
    moveit_config = (
        MoveItConfigsBuilder("rx200", package_name="interbotix_xsarm_moveit")
        .robot_description(file_path=urdf_path)
        .robot_description_semantic(file_path=srdf_path)
        .trajectory_execution(file_path=moveit_control_path)
        .to_moveit_configs()
    )

    # 3. Wrap MoveIt nodes inside a namespaced GroupAction
    namespaced_moveit_nodes = GroupAction(
        actions=[
            # Push the namespace for all nodes inside this group
            PushRosNamespace(my_namespace),

            # The main move_group node
            Node(
                package="moveit_ros_move_group",
                executable="move_group",
                output="screen",
                # Pass parameters directly (MoveIt internally handles namespacing for some parameters)
                parameters=[
                    moveit_config.to_dict(),
                    {"use_sim_time": True}
                ],
            ),

            # Launch rviz to observe the movements of each individual arm
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                parameters=[
                    moveit_config.robot_description,
                    moveit_config.robot_description_semantic,
                    moveit_config.robot_description_kinematics,
                    moveit_config.planning_pipelines,
                ],
            ),
        ]
    )

    return LaunchDescription([
        namespaced_moveit_nodes
    ])
