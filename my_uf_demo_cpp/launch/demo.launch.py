import os
import yaml

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory



def generate_launch_description():

    demo_node = Node(
            package='my_uf_demo_cpp',
            executable='demo',
            name='demo_node',
            output='screen'
        )


    return LaunchDescription([
        demo_node,
    ])
