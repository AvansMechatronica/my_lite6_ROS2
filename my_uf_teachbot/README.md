# UR TeachBot Follower

This package contains ROS2 nodes that allow a UR robot to follow joint positions published by a teachbot device.

## Overview

The teachbot device publishes joint states on `/teachbot/joint_states`, and these nodes command the UR robot to move to match those positions.

## Quick Start

### Launch with GUI Control (Recommended)
```bash
ros2 launch my_uf_teachbot teachbot_follower.launch.py
```

This starts:
- TeachBot follower action client
- Enable/Disable GUI for easy control

### Launch without GUI
```bash
ros2 launch my_uf_teachbot teachbot_follower_simple.launch.py
```

Then manually enable via command line:
```bash
ros2 topic pub /teachbot/enable std_msgs/msg/Bool "data: true"
```

## Available Nodes

### 1. `teachbot_follower_action` ✅ **RECOMMENDED - Action Client**

This node uses action client to send trajectory goals. Robust with feedback and result handling.

**Usage:**
```bash
ros2 run my_uf_teachbot teachbot_follower_action
```

**Parameters:**
- `teachbot_topic` (default: `/teachbot/joint_states`) - Topic to subscribe to for teachbot commands
- `enable_topic` (default: `/teachbot/enable`) - Topic for enable/disable control
- `controller_name` (default: `scaled_joint_trajectory_controller`) - Name of the joint trajectory controller
- `update_rate` (default: `0.5`) - Seconds between updates
- `position_tolerance` (default: `0.01`) - Minimum position change (radians) to trigger movement
- `trajectory_duration` (default: `2.0`) - Duration for each trajectory segment

### 2. `teachbot_follower_moveit_commander` 📝 **Alternative - Direct Commands**

This node directly publishes trajectory commands to the robot controller.

**Usage:**
```bash
ros2 run my_uf_teachbot teachbot_follower_moveit_commander
```

**Parameters:**
- `teachbot_topic` (default: `/teachbot/joint_states`)
- `enable_topic` (default: `/teachbot/enable`)
- `controller_name` (default: `scaled_joint_trajectory_controller`)
- `update_rate` (default: `0.5`)
- `position_tolerance` (default: `0.01`)
- `trajectory_duration` (default: `0.5`)

### 3. `teachbot_enable_gui` 🎛️ **Enable/Disable GUI**

Provides a simple GUI with ON/OFF button to enable/disable teachbot following.

**Usage:**
```bash
ros2 run my_uf_teachbot teachbot_enable_gui
```

**Parameters:**
- `enable_topic` (default: `/teachbot/enable`) - Topic to publish enable state
- `publish_rate` (default: `10.0`) - Publishing rate in Hz

### 3. `ur_teachbot_follower` ⚠️ **MoveIt Python API - Advanced**

This node uses the MoveIt Python API for motion planning. Requires MoveIt to be properly configured.

**Usage:**
```bash
ros2 run my_uf_teachbot ur_teachbot_follower
```

**Parameters:**
- `teachbot_topic` (default: `/teachbot/joint_states`)
- `move_group_name` (default: `arm`)
- `update_rate` (default: `0.5`)
- `position_tolerance` (default: `0.01`)

### 4. `ur_teachbot_simple` ⚠️ **MoveGroup Interface - Experimental**

This node uses MoveIt's MoveGroup interface. May have compatibility issues.

**Usage:**
```bash
ros2 run my_uf_teachbot ur_teachbot_simple
```

**Parameters:**
- `teachbot_topic` (default: `/teachbot/joint_states`)
- `move_group_name` (default: `ur_manipulator`)
- `update_rate` (default: `1.0`)
- `position_tolerance` (default: `0.01`)
- `velocity_scaling` (default: `0.3`) - Maximum velocity scaling factor
- `acceleration_scaling` (default: `0.3`) - Maximum acceleration scaling factor

## Complete Workflow

1. **Build the package:**
   ```bash
   cd ~/ur_ws
   colcon build --packages-select my_uf_teachbot
   source install/setup.bash
   ```

2. **Launch your UR robot with MoveIt:**
   ```bash
   # For simulation:
   ros2 launch my_uf_bringup ur5e_bringup_sim.launch.py
   
   # Or for real robot:
   ros2 launch my_uf_bringup ur5e_bringup.launch.py robot_ip:=<ROBOT_IP>
   ```

3. **Start your teachbot device** (ensure it publishes to `/teachbot/joint_states`)

4. **Run the follower node:**
   ```bash
   ros2 run my_uf_teachbot ur_teachbot_commander
   ```

## Joint Names

Make sure the joint names in the teachbot message match the UR robot joint names:
- `shoulder_pan_joint`
- `shoulder_lift_joint`
- `elbow_joint`
- `wrist_1_joint`
- `wrist_2_joint`
- `wrist_3_joint`

## Troubleshooting

### Robot doesn't move
- Check that `/teachbot/joint_states` is being published: `ros2 topic echo /teachbot/joint_states`
- Verify MoveIt is running: `ros2 node list | grep move_group`
- Check for errors: `ros2 topic echo /rosout`

### Movement is too slow/fast
- Adjust `update_rate` parameter (lower = faster updates)
- For `ur_teachbot_simple`, adjust `velocity_scaling` and `acceleration_scaling`
- For `ur_teachbot_commander`, adjust `trajectory_duration`

### Joint names don't match
- Check your teachbot joint names: `ros2 topic echo /teachbot/joint_states --once`
- Verify UR joint names: `ros2 topic echo /joint_states --once`

## Safety Notes

⚠️ **Warning**: This node will command the robot to follow the teachbot positions. Ensure:
- The workspace is clear of obstacles
- Emergency stop is accessible
- The robot is in a safe starting configuration
- You start with slow update rates and small movements to test

## License

TODO: Add license information
