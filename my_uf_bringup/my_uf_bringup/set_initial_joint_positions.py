#!/usr/bin/env python3
"""
Set initial joint positions after robot spawns in Gazebo.
"""
import os
import yaml
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math


class InitialJointPositionSetter(Node):
    def __init__(self):
        super().__init__('initial_joint_position_setter')
        self.declare_parameter('prefix', '')
        self.declare_parameter('ros_namespace', '')
        self.declare_parameter('controller_name', 'uf_traj_controller')
        self.declare_parameter('initial_positions_file', '')
        self.declare_parameter('goal_time_sec', 2)
        self.declare_parameter('max_retries', 3)

        prefix = self.get_parameter('prefix').get_parameter_value().string_value
        ros_namespace = self.get_parameter('ros_namespace').get_parameter_value().string_value
        controller_name = self.get_parameter('controller_name').get_parameter_value().string_value
        initial_positions_file = self.get_parameter('initial_positions_file').get_parameter_value().string_value
        goal_time_sec = self.get_parameter('goal_time_sec').get_parameter_value().integer_value
        max_retries = self.get_parameter('max_retries').get_parameter_value().integer_value

        self.base_joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']
        self.default_target_positions = {
            'joint1': 0.0,
            'joint2': 0.0,
            'joint3': -0.25 * math.pi,
            'joint4': 0.0,
            'joint5': 0.25 * math.pi,
        }
        loaded_positions = self._load_initial_positions(initial_positions_file)
        self.target_positions = [
            self._as_float(loaded_positions.get(name, self.default_target_positions[name]), name)
            for name in self.base_joint_names
        ]
        self.joint_names = [f'{prefix}{name}' if prefix else name for name in self.base_joint_names]
        self.goal_time_sec = int(goal_time_sec) if goal_time_sec > 0 else 2
        self.max_retries = int(max_retries) if max_retries > 0 else 1
        self.current_try = 0
        self.retry_timer = None

        action_name = self._build_action_name(ros_namespace, controller_name)

        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            action_name
        )
        self.get_logger().info(f'Waiting for action server: {action_name}')
        if not self._action_client.wait_for_server(timeout_sec=30.0):
            self.get_logger().error(f'Action server not available: {action_name}')
            rclpy.shutdown()
            return

        self.get_logger().info('Sending initial joint positions...')
        self.send_goal()

    def _build_action_name(self, ros_namespace, controller_name):
        ns = ros_namespace.strip('/') if ros_namespace else ''
        controller = controller_name.strip('/') if controller_name else 'uf_traj_controller'
        if ns:
            return f'/{ns}/{controller}/follow_joint_trajectory'
        return f'/{controller}/follow_joint_trajectory'

    def _load_initial_positions(self, initial_positions_file):
        if not initial_positions_file:
            return self.default_target_positions
        if not os.path.isfile(initial_positions_file):
            self.get_logger().warning(
                f'Initial positions file not found: {initial_positions_file}, using defaults.'
            )
            return self.default_target_positions

        try:
            with open(initial_positions_file, 'r', encoding='utf-8') as handle:
                data = yaml.safe_load(handle) or {}
            positions = data.get('initial_positions', {})
            if not isinstance(positions, dict):
                self.get_logger().warning('Invalid initial_positions format, using defaults.')
                return self.default_target_positions
            return positions
        except Exception as exc:
            self.get_logger().warning(
                f'Failed to parse initial positions file ({initial_positions_file}): {exc}. Using defaults.'
            )
            return self.default_target_positions

    def _as_float(self, value, joint_name):
        try:
            return float(value)
        except (TypeError, ValueError):
            default_value = self.default_target_positions[joint_name]
            self.get_logger().warning(
                f'Invalid value for {joint_name}: {value}, using default {default_value}'
            )
            return default_value
        
    def send_goal(self):
        self.current_try += 1
        goal_msg = FollowJointTrajectory.Goal()
        
        # Create trajectory
        trajectory = JointTrajectory()
        trajectory.joint_names = self.joint_names
        
        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = self.target_positions
        point.time_from_start = Duration(sec=self.goal_time_sec, nanosec=0)
        
        trajectory.points = [point]
        goal_msg.trajectory = trajectory
        
        self.get_logger().info(
            f'Sending goal attempt {self.current_try}/{self.max_retries} with positions: {self.target_positions}'
        )
        
        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            self._retry_or_shutdown()
            return
        
        self.get_logger().info('Goal accepted')
        
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    def get_result_callback(self, future):
        result = future.result().result
        success_code = FollowJointTrajectory.Result.SUCCESSFUL
        self.get_logger().info(f'Result: {result.error_code}')
        if result.error_code == success_code:
            self.get_logger().info('Initial positions set successfully!')
            rclpy.shutdown()
            return

        self.get_logger().warning(
            f'Initial position action returned non-success code: {result.error_code}'
        )
        self._retry_or_shutdown()

    def _retry_or_shutdown(self):
        if self.current_try < self.max_retries:
            self.get_logger().warning('Retrying initial position command...')
            if self.retry_timer is not None:
                self.retry_timer.cancel()
            self.retry_timer = self.create_timer(1.0, self._retry_once)
            return
        self.get_logger().error('Failed to set initial positions after maximum retries.')
        rclpy.shutdown()

    def _retry_once(self):
        if self.retry_timer is not None:
            self.retry_timer.cancel()
            self.retry_timer = None
        self.send_goal()


def main(args=None):
    rclpy.init(args=args)
    node = InitialJointPositionSetter()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()
