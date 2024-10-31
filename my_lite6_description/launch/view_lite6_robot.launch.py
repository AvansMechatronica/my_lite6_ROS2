from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Define the path to the URDF file within the package
    urdf_file_path = os.path.join(
        get_package_share_directory('my_lite6_description'),
        'urdf',
        'lite6_robot.urdf.xacro'
    )

    # Define the path to the RViz configuration file within the package
    rviz_config_path = os.path.join(
        get_package_share_directory('my_lite6_description'),
        'cfg',
        'view_robot.rviz'
    )

    # Define the robot description using xacro command
    robot_description = Command(['xacro ', urdf_file_path])

    return LaunchDescription([
        # Declare URDF file argument
        DeclareLaunchArgument(
            'urdf_file',
            default_value=urdf_file_path,
            description='Full path to the URDF file to load'
        ),
        
        # Set robot description parameter
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),
        
        # Joint State Publisher GUI Node
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            parameters=[{'use_gui': True}]
        ),
        
        # RViz Node
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz',
            output='screen',
            arguments=['-d', rviz_config_path]
        )
    ])
