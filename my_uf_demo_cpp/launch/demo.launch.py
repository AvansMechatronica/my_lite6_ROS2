#!/usr/bin/env python3
import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from uf_ros_lib.moveit_configs_builder import MoveItConfigsBuilder


def generate_launch_description():
    pkg_path = os.path.join(get_package_share_directory('my_uf_moveit_config'))
    urdf_file = os.path.join(pkg_path, 'config', 'lite6_robot.urdf.xacro')
    srdf_file = os.path.join(pkg_path, 'config', 'lite6_robot.srdf')
    kinematics_file = os.path.join(pkg_path, 'config', 'kinematics.yaml')
    joint_limits_file = os.path.join(pkg_path, 'config', 'joint_limits.yaml')

    moveit_config = (
        MoveItConfigsBuilder(
            context=None,
            dof=6,
            robot_type='lite',
            prefix='',
            limited=True,
        )
        .robot_description(file_path=urdf_file)
        .robot_description_semantic(file_path=srdf_file)
        .robot_description_kinematics(file_path=kinematics_file)
        .joint_limits(file_path=joint_limits_file)
        .to_moveit_configs()
    )

    # Move group node with parameters
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict()],
    )

    # Demo node - delayed to allow MoveIt2 to start
    demo_node = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='my_uf_demo_cpp',
                executable='demo',
                name='my_uf_demo_cpp',
                output='screen',
                parameters=[moveit_config.to_dict()],
            )
        ]
    )

    return LaunchDescription([
        move_group_node,
        demo_node,
    ])
