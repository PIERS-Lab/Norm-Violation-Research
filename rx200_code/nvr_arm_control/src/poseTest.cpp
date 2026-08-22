#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose.hpp>
#include <fstream>
#include <thread>
#include <iostream>
#include "armController.hpp"
#include "json.hpp"

#define INTERM_POSE "intermAlign"
#define GRIPPER_OPEN "Released"
#define GRIPPER_CLOSED "objGripped"

int main(int argc, char * argv[])
{   
  // Initialize ROS
  rclcpp::init(argc, argv);

  // Create the Node
  auto const node = std::make_shared<rclcpp::Node>("poseTest");
  auto const logger = rclcpp::get_logger("hello_moveit");

  // FIX 1: Use a MultiThreadedExecutor so MoveIt callbacks aren't blocked by the main thread
  auto executor = std::make_shared<rclcpp::executors::MultiThreadedExecutor>();
  executor->add_node(node);
  
  // Spin the multi-threaded executor in a background thread
  std::thread spinner([executor]() { executor->spin(); });  

  // Scope MoveIt interfaces so they are destroyed BEFORE ROS shutdown
  {
    using moveit::planning_interface::MoveGroupInterface;

    auto arm_planning_interface = MoveGroupInterface(node, "interbotix_arm");
    auto gripper_planning_interface = MoveGroupInterface(node, "interbotix_gripper");

    std::cout << "Testing commands by the following sequence: pick object 1 -> move to interm -> place object 1 at goal 1 -> move to interm -> pick object 1 from goal 1 -> move to interm -> place object 1 at it's orig spot -> rest\n";

    // Setup the control object
    auto arm = armController(INTERM_POSE, GRIPPER_OPEN, GRIPPER_CLOSED, arm_planning_interface, gripper_planning_interface);

    // Parse json for object set
    std::ifstream poses_raw("/home/ws/src/nvr_arm_control/src/poses.json");
    json poses = json::parse(poses_raw);

    // Start in a favorable position to avoid collisions
    arm_planning_interface.setNamedTarget(INTERM_POSE);
    arm_planning_interface.move();

    // Pick and Place sequence
    arm.pick(poses["obj1"]);
    arm_planning_interface.setNamedTarget(INTERM_POSE);
    arm_planning_interface.move();
    arm.go_to(poses["goal1"]);
    arm.place(poses["goal1"]);

    // Test accuracy by doing the same in reverse
    arm.pick(poses["goal1"]);
    arm_planning_interface.setNamedTarget(INTERM_POSE); // Added intermediate step for safety
    arm_planning_interface.move();
    arm.go_to(poses["obj1"]);
    arm.place(poses["obj1"]);

    // Go back to rest
    arm_planning_interface.setNamedTarget("Sleep");
    arm_planning_interface.move();
  }

  
  executor->cancel();
  if (spinner.joinable())
  {
    spinner.join();
  }

  // Shutdown ROS safely
  rclcpp::shutdown();
  return 0;
}
