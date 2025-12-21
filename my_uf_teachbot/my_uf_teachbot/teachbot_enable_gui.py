#!/usr/bin/env python3
"""
TeachBot Enable GUI

This node provides a simple GUI with an ON/OFF button to enable/disable
the teachbot follower by publishing to a boolean topic.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import tkinter as tk
from tkinter import ttk


class TeachBotEnableGUI(Node):
    """Node that provides a GUI to enable/disable teachbot following."""
    
    def __init__(self):
        super().__init__('teachbot_enable_gui')
        
        # Declare parameters
        self.declare_parameter('enable_topic', '/teachbot/enable')
        self.declare_parameter('publish_rate', 10.0)  # Hz
        
        # Get parameters
        enable_topic = self.get_parameter('enable_topic').value
        publish_rate = self.get_parameter('publish_rate').value
        
        # Create publisher
        self.enable_pub = self.create_publisher(Bool, enable_topic, 10)
        
        # Create timer to publish at regular intervals
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_enable_state)
        
        # State
        self.enabled = False
        
        # Create GUI
        self.create_gui()
        
        self.get_logger().info(f'Publishing enable state to {enable_topic}')
        self.get_logger().info('GUI ready. Use the button to enable/disable teachbot following.')
    
    def create_gui(self):
        """Create the GUI window with ON/OFF button."""
        self.root = tk.Tk()
        self.root.title("TeachBot Enable Control")
        self.root.geometry("300x150")
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 14))
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Label
        self.status_label = ttk.Label(
            main_frame, 
            text="TeachBot Following: DISABLED",
            font=('Arial', 12, 'bold')
        )
        self.status_label.grid(row=0, column=0, pady=10)
        
        # Toggle button
        self.toggle_button = tk.Button(
            main_frame,
            text="Enable",
            command=self.toggle_enable,
            font=('Arial', 16, 'bold'),
            width=12,
            height=2,
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049'
        )
        self.toggle_button.grid(row=1, column=0, pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def toggle_enable(self):
        """Toggle the enable state."""
        self.enabled = not self.enabled
        self.update_gui()
        self.get_logger().info(f'TeachBot following {"ENABLED" if self.enabled else "DISABLED"}')
    
    def update_gui(self):
        """Update the GUI to reflect current state."""
        if self.enabled:
            self.status_label.config(
                text="TeachBot Following: ENABLED",
                foreground='green'
            )
            self.toggle_button.config(
                text="Disable",
                bg='#f44336',
                activebackground='#da190b'
            )
        else:
            self.status_label.config(
                text="TeachBot Following: DISABLED",
                foreground='red'
            )
            self.toggle_button.config(
                text="Enable",
                bg='#4CAF50',
                activebackground='#45a049'
            )
    
    def publish_enable_state(self):
        """Publish the current enable state."""
        msg = Bool()
        msg.data = self.enabled
        self.enable_pub.publish(msg)
    
    def update_ros(self):
        """Update ROS while keeping GUI responsive."""
        rclpy.spin_once(self, timeout_sec=0.01)
        self.root.after(10, self.update_ros)
    
    def on_closing(self):
        """Handle window closing."""
        self.get_logger().info('Closing TeachBot Enable GUI')
        self.root.quit()
    
    def run(self):
        """Run the GUI event loop."""
        self.root.after(10, self.update_ros)
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = TeachBotEnableGUI()
        node.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
