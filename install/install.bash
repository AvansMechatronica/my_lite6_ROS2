
sudo apt update
sudo apt -y install ros-$ROS_DISTRO-moveit
sudo apt -y install ros-$ROS_DISTRO-joint-state-publisher-gui
sudo apt -y install ros-$ROS_DISTRO-combined-robot-hw
sudo apt -y install ros-$ROS_DISTRO-moveit-servo
sudo apt -y install ros-$ROS_DISTRO-moveit-visual-tools
sudo apt -y install ros-$ROS_DISTRO-ros-controllers
sudo apt -y install ros-$ROS_DISTRO-controller-manager
sudo apt -y install ros-$ROS_DISTRO-controller-manager-msgs
sudo apt -y install ros-$ROS_DISTRO-tf-transformations

CURRENT_DIR=$(pwd)

if ros2 pkg list | grep -q "xarm_description"; then
    echo "xarm packages alredy installed"
else
    echo "cloning xarm packages"
    git clone https://github.com/xArm-Developer/xarm_ros2.git ../../xarm_ros -b $ROS_DISTRO --recursive 
    #git clone https://github.com/ros-planning/moveit_task_constructor.git ../../moveit_task_constructor -b $ROS_DISTRO

    cd ../../xarm_ros
    git pull
    git submodule sync
    git submodule update --init --remote
fi

cd "$CURRENT_DIR"
if ros2 pkg list | grep -q "pymoveit2"; then
    echo "pymoveit2 packages alredy installed"
else
    echo "cloning xarm pymoveit2"
    git clone https://github.com/AvansMechatronica/pymoveit2.git ../../pymoveit2 
fi

cd "$CURRENT_DIR"
if ros2 pkg list | grep -q "my_moveit_python"; then
    echo "my_moveit_python packages alredy installed"
else
    echo "cloning my_moveit_python"
    git clone https://github.com/AvansMechatronica/my_moveit_python.git ../../my_moveit_python 
fi

cd "$CURRENT_DIR"
cd ../../..
rosdep update
rosdep install --from-paths . --ignore-src --rosdistro $ROS_DISTRO -y