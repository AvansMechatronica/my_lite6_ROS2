#!/usr/bin/env python3
"""
Launch file for TeachBot Follower System

This launch file starts:
1. TeachBot follower action client node
2. TeachBot enable GUI for on/off control
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for teachbot follower system."""
    
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
    
    update_rate_arg = DeclareLaunchArgument(
        'update_rate',
        default_value='0.5',
        description='Update rate in seconds between commands'
    )
    
    position_tolerance_arg = DeclareLaunchArgument(
        'position_tolerance',
        default_value='0.01',
        description='Position tolerance in radians to trigger new commands'
    )
    
    trajectory_duration_arg = DeclareLaunchArgument(
        'trajectory_duration',
        default_value='2.0',
        description='Trajectory execution duration in seconds'
    )
    
    use_gui_arg = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Whether to launch the enable GUI'
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
            'update_rate': LaunchConfiguration('update_rate'),
            'position_tolerance': LaunchConfiguration('position_tolerance'),
            'trajectory_duration': LaunchConfiguration('trajectory_duration'),
        }]
    )
    
    # TeachBot Enable GUI Node
    teachbot_enable_gui_node = Node(
        package='my_uf_teachbot',
        executable='teachbot_enable_gui',
        name='teachbot_enable_gui',
        output='screen',
        parameters=[{
            'enable_topic': LaunchConfiguration('enable_topic'),
        }],
        condition=IfCondition(LaunchConfiguration('use_gui'))
    )
    
    return LaunchDescription([
        # Launch arguments
        teachbot_topic_arg,
        enable_topic_arg,
        controller_name_arg,
        update_rate_arg,
        position_tolerance_arg,
        trajectory_duration_arg,
        use_gui_arg,
        
        # Nodes
        teachbot_follower_node,
        teachbot_enable_gui_node,
    ])
