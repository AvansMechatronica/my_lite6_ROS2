#!/usr/bin/env python3
"""
Simple launch file for TeachBot Follower (no GUI)

This launch file starts only the teachbot follower action client node.
Use this if you want to control enable/disable via command line or another method.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for teachbot follower (no GUI)."""
    
    # Declare launch arguments
    teachbot_topic_arg = DeclareLaunchArgument(
        'teachbot_topic',
        default_value='/teachbot/joint_states',
        description='Topic to subscribe to for teachbot joint states'
    )
    
    enable_topic_arg = DeclareLaunchArgument(
        'enable_topic',
        default_value='/teachbot/enable',
        description='Topic for enable/disable control'
    )
    
    controller_name_arg = DeclareLaunchArgument(
        'controller_name',
        default_value='scaled_joint_trajectory_controller',
        description='Name of the joint trajectory controller'
    )
    
    # TeachBot Follower Action Node
    teachbot_follower_node = Node(
        package='my_uf_teachbot',
        executable='teachbot_follower_action',
        name='teachbot_follower_action',
        output='screen',
        parameters=[{
            'teachbot_topic': LaunchConfiguration('teachbot_topic'),
            'enable_topic': LaunchConfiguration('enable_topic'),
            'controller_name': LaunchConfiguration('controller_name'),
            'update_rate': 0.5,
            'position_tolerance': 0.01,
            'trajectory_duration': 2.0,
        }]
    )
    
    return LaunchDescription([
        # Launch arguments
        teachbot_topic_arg,
        enable_topic_arg,
        controller_name_arg,
        
        # Node
        teachbot_follower_node,
    ])
