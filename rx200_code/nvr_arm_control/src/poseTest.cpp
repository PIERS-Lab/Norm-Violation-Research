#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose.hpp>

int main(int argc, char * argv[])
{
  // Initialize ROS and create the Node
  rclcpp::init(argc, argv);

  // enable automatic parameter downloading

  auto const node = std::make_shared<rclcpp::Node>(
    "poseTest",
    rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true)
  );

  // Create a ROS logger
    auto const logger = rclcpp::get_logger("hello_moveit");
  //create a spinner to let ros move
    auto spinner = std::thread([node]() { rclcpp::spin(node); });  

// Create the MoveIt MoveGroup Interface
using moveit::planning_interface::MoveGroupInterface;
auto move_group_interface = MoveGroupInterface(node, "interbotix_arm");

// Set a target Pose
auto const target_pose = []{
  geometry_msgs::msg::Pose msg;
  
  msg.orientation.w = -0.506;
  msg.orientation.x = 0.525;
  msg.orientation.y = 0.475;
  msg.orientation.z = 0.493;
  msg.position.x = 0.0;
  msg.position.y = 0.20;
  msg.position.z = 0.10;
  return msg;
}();
move_group_interface.setEndEffectorLink("rx200/ee_gripper_link");
move_group_interface.setPoseTarget(target_pose);

// Create a plan to that target pose
auto const [success, plan] = [&move_group_interface]{
  moveit::planning_interface::MoveGroupInterface::Plan msg;
  auto const ok = static_cast<bool>(move_group_interface.plan(msg));
  return std::make_pair(ok, msg);
}();

// Execute the plan
if(success) {
  move_group_interface.execute(plan);
} else {
  RCLCPP_ERROR(logger, "Planning failed!");
}
  // Shutdown ROS
  rclcpp::shutdown();
  if (spinner.joinable())
  {
    spinner.join();
  }
  return 0;
}