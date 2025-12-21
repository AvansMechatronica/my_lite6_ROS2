#!/usr/bin/env python3
"""
UR Robot TeachBot Follower Node (Action Client)

This node subscribes to joint states from a teachbot device and commands
the UR robot to follow those positions using action client for trajectory execution.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import threading


class URTeachBotFollowerAction(Node):
    """Node that follows teachbot joint commands using action client."""
    
    def __init__(self):
        super().__init__('teachbot_follower_action')
        
        # Declare parameters
        self.declare_parameter('teachbot_topic', '/teachbot/joint_states')
        self.declare_parameter('enable_topic', '/teachbot/enable')
        self.declare_parameter('controller_name', 'scaled_joint_trajectory_controller')
        self.declare_parameter('update_rate', 0.5)  # seconds between updates
        self.declare_parameter('position_tolerance', 0.01)  # radians
        self.declare_parameter('trajectory_duration', 2.0)  # seconds - increased to avoid path tolerance violations
        
        # Get parameters
        teachbot_topic = self.get_parameter('teachbot_topic').value
        enable_topic = self.get_parameter('enable_topic').value
        controller_name = self.get_parameter('controller_name').value
        self.update_rate = self.get_parameter('update_rate').value
        self.position_tolerance = self.get_parameter('position_tolerance').value
        self.trajectory_duration = self.get_parameter('trajectory_duration').value
        
        # Storage for latest joint states
        self.latest_joint_states = None
        self.current_robot_state = None  # Current robot joint positions
        self.last_commanded_positions = None
        self.enabled = False  # Enable/disable flag
        self.lock = threading.Lock()
        self.is_executing = False
        
        # Create action client
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            f'/{controller_name}/follow_joint_trajectory'
        )
        
        # Subscribe to teachbot joint states
        self.subscription = self.create_subscription(
            JointState,
            teachbot_topic,
            self.joint_state_callback,
            10
        )
        
        # Subscribe to robot joint states to get current position
        self.robot_state_subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.robot_state_callback,
            10
        )
        
        # Subscribe to enable topic
        self.enable_subscription = self.create_subscription(
            Bool,
            enable_topic,
            self.enable_callback,
            10
        )
        
        # Create a timer to periodically send commands
        self.timer = self.create_timer(self.update_rate, self.update_robot_position)
        
        self.get_logger().info(f'Subscribed to {teachbot_topic}')
        self.get_logger().info(f'Subscribed to {enable_topic}')
        self.get_logger().info(f'Action client: /{controller_name}/follow_joint_trajectory')
        self.get_logger().info(f'Update rate: {self.update_rate} seconds')
        self.get_logger().info('Waiting for action server...')
        
        # Wait for action server
        self._action_client.wait_for_server()
        self.get_logger().info('Action server connected. Ready to follow teachbot commands')
    
    def joint_state_callback(self, msg):
        """Store the latest joint state message."""
        with self.lock:
            self.latest_joint_states = msg
    
    def robot_state_callback(self, msg):
        """Store the current robot joint state."""
        with self.lock:
            self.current_robot_state = msg
    
    def enable_callback(self, msg):
        """Handle enable/disable messages."""
        was_enabled = self.enabled
        self.enabled = msg.data
        
        if self.enabled and not was_enabled:
            self.get_logger().info('TeachBot following ENABLED')
        elif not self.enabled and was_enabled:
            self.get_logger().info('TeachBot following DISABLED')
    
    def update_robot_position(self):
        """Periodically update the robot position based on teachbot input."""
        # Check if enabled
        if not self.enabled:
            return
        
        # Don't send new commands while executing
        if self.is_executing:
            return
            
        with self.lock:
            if self.latest_joint_states is None:
                return
            
            joint_states = self.latest_joint_states
        
        try:
            # Check if we need to update (positions changed significantly)
            if self.should_update_position(joint_states):
                self.send_goal(joint_states)
        except Exception as e:
            self.get_logger().error(f'Error updating robot position: {str(e)}')
    
    def should_update_position(self, joint_states):
        """Check if the position has changed enough to warrant a new command."""
        if self.last_commanded_positions is None:
            return True
        
        # Check if any joint has moved beyond the tolerance
        for i, pos in enumerate(joint_states.position):
            if i < len(self.last_commanded_positions):
                if abs(pos - self.last_commanded_positions[i]) > self.position_tolerance:
                    return True
        
        return False
    
    def send_goal(self, joint_states):
        """Send a trajectory goal via action client."""
        self.is_executing = True
        
        # Strip tf_prefix from joint names (e.g., 'teachbot/shoulder_pan_joint' -> 'shoulder_pan_joint')
        joint_names = [name.split('/')[-1] for name in joint_states.name]
        
        # Log joint name mapping for debugging
        if any('/' in name for name in joint_states.name):
            self.get_logger().debug(
                f'Stripped tf_prefix: {list(joint_states.name)} -> {joint_names}'
            )
        
        # Get current robot positions for these joints
        current_positions = None
        with self.lock:
            if self.current_robot_state is not None:
                # Map joint names to positions
                robot_joint_map = {name: pos for name, pos in zip(
                    self.current_robot_state.name, 
                    self.current_robot_state.position
                )}
                # Get positions in the same order as target
                current_positions = [robot_joint_map.get(name, 0.0) for name in joint_names]
        
        # Create trajectory message
        trajectory = JointTrajectory()
        trajectory.joint_names = joint_names
        
        # If we have current position, create a 2-point trajectory (smooth motion)
        if current_positions is not None:
            # Point 0: Current position (very short time)
            point0 = JointTrajectoryPoint()
            point0.positions = current_positions
            point0.velocities = [0.0] * len(joint_names)
            point0.time_from_start = Duration(sec=0, nanosec=100000000)  # 0.1 seconds
            trajectory.points.append(point0)
            
            # Point 1: Target position
            point1 = JointTrajectoryPoint()
            point1.positions = list(joint_states.position)
            point1.velocities = [0.0] * len(joint_names)
            point1.time_from_start = Duration(
                sec=int(self.trajectory_duration),
                nanosec=int((self.trajectory_duration % 1) * 1e9)
            )
            trajectory.points.append(point1)
        else:
            # Fallback: Single point trajectory
            point = JointTrajectoryPoint()
            point.positions = list(joint_states.position)
            point.velocities = [0.0] * len(joint_names)
            point.time_from_start = Duration(
                sec=int(self.trajectory_duration),
                nanosec=int((self.trajectory_duration % 1) * 1e9)
            )
            trajectory.points = [point]
        
        # Create goal with relaxed tolerances to avoid PATH_TOLERANCE_VIOLATED
        from control_msgs.msg import JointTolerance
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory
        
        # Set path tolerances (relaxed to avoid violations during motion)
        for joint_name in trajectory.joint_names:
            tol = JointTolerance()
            tol.name = joint_name
            tol.position = 0.5  # radians - relaxed tolerance
            tol.velocity = 0.5  # rad/s
            tol.acceleration = 1.0  # rad/s^2
            goal_msg.path_tolerance.append(tol)
        
        # Set goal tolerances (tighter at the end)
        for joint_name in trajectory.joint_names:
            tol = JointTolerance()
            tol.name = joint_name
            tol.position = 0.05  # radians
            tol.velocity = 0.1  # rad/s
            tol.acceleration = 0.0  # Don't check acceleration at goal
            goal_msg.goal_tolerance.append(tol)
        
        # Set goal time tolerance
        goal_msg.goal_time_tolerance = Duration(sec=2, nanosec=0)
        
        self.get_logger().info(
            f'Sending goal: {[f"{p:.3f}" for p in joint_states.position]}'
        )
        
        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)
        
        # Update last commanded positions
        self.last_commanded_positions = list(joint_states.position)
    
    def goal_response_callback(self, future):
        """Handle goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            self.is_executing = False
            return
        
        self.get_logger().info('Goal accepted')
        
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    def get_result_callback(self, future):
        """Handle result."""
        from control_msgs.action import FollowJointTrajectory as FJT
        result = future.result().result
        
        # Map error codes to messages
        error_messages = {
            FJT.Result.SUCCESSFUL: 'SUCCESSFUL',
            FJT.Result.INVALID_GOAL: 'INVALID_GOAL',
            FJT.Result.INVALID_JOINTS: 'INVALID_JOINTS',
            FJT.Result.OLD_HEADER_TIMESTAMP: 'OLD_HEADER_TIMESTAMP',
            FJT.Result.PATH_TOLERANCE_VIOLATED: 'PATH_TOLERANCE_VIOLATED',
            FJT.Result.GOAL_TOLERANCE_VIOLATED: 'GOAL_TOLERANCE_VIOLATED'
        }
        
        error_msg = error_messages.get(result.error_code, f'UNKNOWN({result.error_code})')
        
        if result.error_code == FJT.Result.SUCCESSFUL:
            self.get_logger().info(f'Result: {error_msg}')
        else:
            self.get_logger().warn(f'Result: {error_msg} (code: {result.error_code})')
        
        self.is_executing = False
    
    def feedback_callback(self, feedback_msg):
        """Handle feedback (optional)."""
        pass


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = URTeachBotFollowerAction()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
