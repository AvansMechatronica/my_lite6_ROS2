#include <cstdio>
#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>
using namespace std;
//#include <pluginlib/class_loader.hpp>

// MoveIt
#include <moveit/robot_model_loader/robot_model_loader.h>
#include <moveit/planning_interface/planning_interface.h>
#include <moveit/planning_scene/planning_scene.h>
#include <moveit/kinematic_constraints/utils.h>
#include <moveit_msgs/msg/display_trajectory.hpp>
#include <moveit_msgs/msg/planning_scene.h>
//#include <moveit_visual_tools/moveit_visual_tools.h>
#include <moveit/move_group_interface/move_group_interface.h>
#include <ament_index_cpp/get_package_share_directory.hpp>

static const rclcpp::Logger LOGGER = rclcpp::get_logger("my_uf_demo_cpp");

int main(int argc, char ** argv)
{
    (void) argc;
    (void) argv;

    printf("My uFactory xarm5 demo CPP\n");
 
    rclcpp::init(argc, argv);
    
    auto move_group_node = rclcpp::Node::make_shared("move_group", rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));
    
    // Load robot description from file if not provided as parameter
    if (!move_group_node->has_parameter("robot_description_semantic")) {
        RCLCPP_WARN(LOGGER, "Could not read robot_description_semantic parameter");   
    }
 
    // We spin up a SingleThreadedExecutor for the current state monitor to get information
    // about the robot's state.
    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(move_group_node);
    std::thread([&executor]() { executor.spin(); }).detach();
 
    // Give move_group time to initialize
    std::this_thread::sleep_for(std::chrono::seconds(2));
 
    // MoveIt operates on sets of joints called "planning groups" and stores them in an object called
    // the ``JointModelGroup``. Throughout MoveIt, the terms "planning group" and "joint model group"
    // are used interchangeably.
    static const std::string PLANNING_GROUP = "xarm5";

 
    // The
    // :moveit_codedir:`MoveGroupInterface<moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h>`
    // class can be easily set up using just the name of the planning group you would like to control and plan for.
    moveit::planning_interface::MoveGroupInterface move_group(move_group_node, PLANNING_GROUP);

    return 0;
}

