#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from threading import Thread

from tf2_ros import Buffer, TransformListener, TransformException

from my_moveit_python import srdfGroupStates, MovegroupHelper


class Lite6Demo(Node):
    def __init__(self):
        super().__init__("lite6_demo")

        # Robot parameters
        prefix = ""
        self.joint_names = [
            prefix + "joint1",
            prefix + "joint2",
            prefix + "joint3",
            prefix + "joint4",
            prefix + "joint5",
            prefix + "joint6",
        ]
        self.base_link_name = "link_base"
        self.end_effector_name = "link6"
        self.group_name = "lite6"
        self.package_name = "my_lite6_moveit_config"
        self.srdf_file_name = "config/lite6_robot.srdf"

        # TF setup
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # MoveIt helpers
        self.group_states = srdfGroupStates(
            self.package_name, self.srdf_file_name, self.group_name
        )
        self.move_group = MovegroupHelper(
            self, self.joint_names, self.base_link_name, self.end_effector_name, self.group_name
        )

        # --- Create subscribers, publishers, clients, timers here ---

        self.get_logger().info("Lite6 demo node has been initialized.")

    # --- Create callback functions here ---

    # --- Motion primitives ------------------------------------------------
    def move_to_state(self, state_name: str):
        result, joint_values = self.group_states.get_joint_values(state_name)
        if not result:
            self.get_logger().error(f"Failed to get joint values for state '{state_name}'.")
            return
        self.get_logger().info(f"Moving to state '{state_name}'.")
        self.move_group.move_to_configuration(joint_values)

    def move_to_pose(self, translation, rotation):
        self.get_logger().info(f"Moving to pose: {translation}, {rotation}")
        self.move_group.move_to_pose(translation, rotation)

    def move_to_tf(self, from_frame: str, to_frame: str):
        try:
            t = self.tf_buffer.lookup_transform(
                to_frame, from_frame, rclpy.time.Time()
            )
            translation = [
                t.transform.translation.x,
                t.transform.translation.y,
                t.transform.translation.z,
            ]
            rotation = [
                t.transform.rotation.w,
                t.transform.rotation.x,
                t.transform.rotation.y,
                t.transform.rotation.z,
            ]
            self.get_logger().info(f"Moving to transform: {from_frame} → {to_frame}")
            self.move_to_pose(translation, rotation)
        except TransformException as ex:
            self.get_logger().warn(f"Could not transform {to_frame} to {from_frame}: {ex}")

    # --- App sequence ----------------------------------------------------

    def execute_app(self):
        for state in ["left", "right", "home"]:
            self.move_to_state(state)

        self.move_to_pose([0.5, 0.1, 0.25], [1.0, 0.0, 0.0, 0.0])
        self.move_to_tf("test_transfer_frame", "xarm_link")
        self.move_to_state("home")


# --------------------------------------------------------------------------

def main():
    rclpy.init()

    # Create an instance of your custom Node class (here called "Lite6Demo")
    # This must happen before creating the executor so that the node can be registered properly.
    node = Lite6Demo()  # Note: must be created before adding it to the executor

    # Create a multithreaded executor with 2 threads
    # This allows the node to handle multiple callbacks concurrently (e.g., subscriptions, timers)
    executor = MultiThreadedExecutor(num_threads=2)

    # Add the node to the executor so it can process its callbacks
    executor.add_node(node)

    # Start the executor in a separate background thread
    # This keeps the ROS event loop (callback processing) running
    # while your main thread can still execute custom logic (like execute_app)
    executor_thread = Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    # Create a 1 Hz rate object and sleep once to allow initialization
    # Equivalent to "rclpy.spin_once(node)" but gives time for system setup (e.g., MoveIt, TF)
    node.create_rate(1.0).sleep()

    # Run your custom main logic (defined inside the Assignment class)
    # This typically executes the robot’s motion, computation, or control behavior
    node.execute_app()

    # Shutdown ROS gracefully once the main logic finishes
    rclpy.shutdown()

    # Wait for the executor thread to exit cleanly before terminating the program
    executor_thread.join()


if __name__ == "__main__":
    main()
