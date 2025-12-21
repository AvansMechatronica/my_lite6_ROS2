#include <cstdio>
#include <iostream>
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

static const rclcpp::Logger LOGGER = rclcpp::get_logger("my_demo_cpp");

int main(int argc, char ** argv)
{
    (void) argc;
    (void) argv;

    printf("My Demo CPP\n");
 
    rclcpp::init(argc, argv);
    //rclcpp::NodeOptions node_options;
    //node_options.automatically_declare_parameters_from_overrides(true);
    auto move_group_node = rclcpp::Node::make_shared("my_node", rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));
 

    // We spin up a SingleThreadedExecutor for the current state monitor to get information
    // about the robot's state.
    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(move_group_node);
    std::thread([&executor]() { executor.spin(); }).detach();
 
 
    // MoveIt operates on sets of joints called "planning groups" and stores them in an object called
    // the ``JointModelGroup``. Throughout MoveIt, the terms "planning group" and "joint model group"
    // are used interchangeably.
    static const std::string PLANNING_GROUP = "arm";

 
    // The
    // :moveit_codedir:`MoveGroupInterface<moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h>`
    // class can be easily set up using just the name of the planning group you would like to control and plan for.
    moveit::planning_interface::MoveGroupInterface move_group(move_group_node, PLANNING_GROUP);



    string group_states[] = {"home", "left", "right", "home", "resting"};
    for(const string &group_state : group_states){
        move_group.setJointValueTarget(move_group.getNamedTargetValues(group_state));

    #if 0
        // We will use the
        // :moveit_codedir:`PlanningSceneInterface<moveit_ros/planning_interface/planning_scene_interface/include/moveit/planning_scene_interface/planning_scene_interface.h>`
        // class to add and rem    std::cout << "1" << std::endl;ove collision objects in our "virtual world" scene
        //  moveit::planning_interface::PlanningSceneInterface planning_scene_interface;

        moveit_msgs::msg::Constraints constraints;
        std::map<std::string, double>::iterator it = target.begin();
        while(it != target.end())
        {
            moveit_msgs::msg::JointConstraint joint_constraint;

            std::cout<<it->first<<" = "<<it->second<<std::endl;
            // Constrain the position of a joint to be within a certain bound
            joint_constraint.joint_name = it->first;

            // the bound to be achieved is [position - tolerance_below, position + tolerance_above]
            joint_constraint.position = it->second;
            joint_constraint.tolerance_above = 0.1;
            joint_constraint.tolerance_below = 0.1;

            // A weighting factor for this constraint (denotes relative importance to other constraints. Closer to zero means less important)
            joint_constraint.weight = 1.0;

            constraints.joint_constraints.push_back(joint_constraint);

            it++;
        }


        move_group.setJointValueTarget(target);
        move_group.setPlanningTime(10.0);

        move_group.setPathConstraints(constraints);
    #endif

        moveit::planning_interface::MoveGroupInterface::Plan my_plan_arm;

        bool success = (move_group.plan(my_plan_arm) == moveit::core::MoveItErrorCode::SUCCESS);
        if (success)
        {
            printf("Execute plan\n");
            move_group.move();
        }
        else{
            printf("Faild to create plan\n");
        }
    }
    printf("Ready\n");
    rclcpp::shutdown();
    return 0;
}

