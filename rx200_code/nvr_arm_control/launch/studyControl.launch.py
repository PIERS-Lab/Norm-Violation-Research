import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    
    # 1. Define your specific Interbotix robot model 
    # (e.g., 'wx200', 'px150', 'rx200', 'vx300', etc.)
    robot_model = 'rx200' 

    # 2. Safely find package directories using standard lazy substitutions
    interbotix_descriptions_share = FindPackageShare('interbotix_xsarm_descriptions')
    interbotix_moveit_share = FindPackageShare('interbotix_xsarm_moveit')

    # 3. Create lazy path mappings
    xacro_path = PathJoinSubstitution([interbotix_descriptions_share, 'urdf', f'{robot_model}.urdf.xacro'])
    srdf_path = PathJoinSubstitution([
    interbotix_moveit_share, 
    'config', 
    'srdf',                   # <-- Added missing 'srdf' folder level
    f'{robot_model}.srdf.xacro' # <-- Added missing .xacro extension
])
    kinematics_yaml_path = PathJoinSubstitution([interbotix_moveit_share, 'config', 'kinematics.yaml'])

    # 4. Use ParameterValue to cleanly evaluate text commands inside the parameter tree
    robot_description_content = ParameterValue(
        Command(['xacro ', xacro_path, ' use_world_frame:=true']),
        value_type=str
    )

    robot_description_semantic_content = ParameterValue(
    Command(['xacro ', srdf_path]),
    value_type=str
)
    # 5. Build your custom test node and inject the clean data streams
    study_control_node = Node(
        package='nvr_arm_control',               # Your custom package name
        executable='studyControl',                   # Your compiled executable target binary
        output='screen',                         
        parameters=[
            {'robot_description': robot_description_content},
            {'robot_description_semantic': robot_description_semantic_content},
            kinematics_yaml_path
        ]
    )

    return LaunchDescription([
        study_control_node
    ])
