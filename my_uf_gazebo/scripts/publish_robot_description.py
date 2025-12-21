#!/usr/bin/env python3
"""
Simple node to publish robot_description on a topic for controller_manager.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from std_msgs.msg import String


class RobotDescriptionPublisher(Node):
    def __init__(self):
        super().__init__('robot_description_publisher')
        
        # Declare and get the robot_description parameter
        self.declare_parameter('robot_description', '')
        robot_description = self.get_parameter('robot_description').value
        
        if not robot_description:
            self.get_logger().error('robot_description parameter is empty!')
            return
            
        # Create QoS profile with transient_local durability (required by controller_manager)
        qos_profile = QoSProfile(depth=1)
        qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL
        
        # Create publisher with proper QoS
        self.publisher = self.create_publisher(String, 'robot_description', qos_profile)
        
        # Publish immediately and then periodically
        self.robot_description_msg = String()
        self.robot_description_msg.data = robot_description
        
        # Publish once immediately
        self.publisher.publish(self.robot_description_msg)
        
        # Keep publishing at 1 Hz to ensure it's always available
        self.timer = self.create_timer(1.0, self.timer_callback)
        
        self.get_logger().info('Publishing robot_description topic with transient_local QoS')
    
    def timer_callback(self):
        self.publisher.publish(self.robot_description_msg)


def main(args=None):
    rclpy.init(args=args)
    node = RobotDescriptionPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
