import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    robot_model = 'rx200' 
    
    # 1. Target the correct macro and configuration paths
    study_xacro = '/home/ws/src/nvr_arm_control/config/studyarms.srdf.xacro'
    
    # Pre-render the custom SRDF xacro macro into memory text right now
    compiled_srdf = xacro.process_file(study_xacro)
    
    # Write to a stable location for logging/MoveIt tracking references
    temp_static_srdf = '/tmp/generatedSRDF.srdf'
    with open(temp_static_srdf, 'w') as f:
        f.write(compiled_srdf.toxml())

    # 2. Resolve package share names cleanly (Fixes the share-name crash)
    interbotix_descriptions_share = FindPackageShare('interbotix_xsarm_descriptions')
    interbotix_dual_share = FindPackageShare('interbotix_xsarm_dual')
    
    kinematics_yaml_path = PathJoinSubstitution([interbotix_dual_share, 'config', 'kinematics.yaml'])
    base_urdf_xacro = PathJoinSubstitution([interbotix_descriptions_share, 'urdf', f'{robot_model}.urdf.xacro'])

    # 3. Use ParameterValue to map data structures cleanly into the runtime trees
    robot_description_content = ParameterValue(
        Command(['xacro ', base_urdf_xacro, ' use_world_frame:=true']),
        value_type=str
    )

    # Inject the pre-processed dual-arm XML targets string directly into the parameter
    robot_description_semantic_content = ParameterValue(
        compiled_srdf.toxml(),
        value_type=str
    )
    
    # 4. Declare your custom task orchestration argument flags (Fixes duplicates)
    deliv_config_arg = DeclareLaunchArgument(
        "config", 
        default_value="ld11", 
        description="Delivery behavior sequence config parameter (e.g. d11, r22)"
    )
    deliv_config_value = LaunchConfiguration('config')
    
    # 5. Build your custom test execution node with pristine configuration arrays
    deliver_node = Node(
        package='nvr_arm_control',               
        executable='deliver',                   
        output='screen',                         
        parameters=[
            {'robot_description': robot_description_content},
            {'robot_description_semantic': robot_description_semantic_content},
            kinematics_yaml_path,
            {'deliv_config_arg': deliv_config_value} # Pass the parameter seamlessly to your C++ logic
        ]
    )

    return LaunchDescription([
        deliv_config_arg,
        deliver_node
    ])
