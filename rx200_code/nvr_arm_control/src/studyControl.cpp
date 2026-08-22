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

typedef struct {
        json object_pose;
        json goal_pose;
} order;

/* Takes in the info needed to re define the poses for the robot to target. 
config is a 3 char string denoting the robot, object pose, and goal pose (L23, for example) */
order compile_order(std::string configuration, json pose);

bool deliver_package(armController arm, order poses);

bool reset(armController arm, order poses);

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

    

    // Setup the control object
    auto arm = armController(INTERM_POSE, GRIPPER_OPEN, GRIPPER_CLOSED, arm_planning_interface, gripper_planning_interface);

    //TO DO: figure out how to communicate with robot2
    // Parse json for object set
    std::ifstream poses_raw("/home/ws/src/nvr_arm_control/src/poses.json");
    const json poses = json::parse(poses_raw);

    // Start in a favorable position to avoid collisions
    arm_planning_interface.setNamedTarget(INTERM_POSE);
    arm_planning_interface.move();

    // get into loop
    /* grab command (repped as object 1, 2 or 3 then goal 1, 2, or 3. 
    implicitly, the left arm is defined with the first two chars, the right with the last two
    and the objects being numbered from left to right)
    */
    // // safely terminate if 'e' is given as input
    // // so 6 chars, given as one string
    // build structs to compile the commands
    // execute in order given, reading the string from the left to right
    // // struct 1 will be made with elms 0->1, while struct2 will be made wih elms 2->3
    // wait for wizard to confirm reset, then re-use the structs to place the objects back
    // // depending on how piloting goes, I may want to give the wizard the option on where things are returned to
    std::string command;
    //create containers to retain commands adn organize run order
    order first_robot, second_robot;
    
    while(true)
    {
        // TO DO: add more robust input and pose validation once the basic stuff is working
        std::cout << "Process start! input the configuration (e to finish up): \n";
        std::cin >> command;
        if(command == "e" || command.empty())
        {
            break;
        }
        order first_robot = compile_order(command.substr(0, 2), poses);
        // order second_robot = compile_order(command.substr(2, 2), poses);
        // wait for 
        std::cout << "Input anything to begin execution\n";
        std::cin.get();
        std::cout << "starting execution for robot1\n";
        deliver_package(arm, first_robot);
        // TO DO: check for sucess here later
        // un comment when 2nd robot is properly implemented
        // std::cout << "startiing execution for robot2\n";
        // deliver_package(arm, second_robot);
        std::cout << "Input anything to begin autonomus reset\n";
        std::cin.get();
        std::cout << "Beginning autonomous reset\n";
        reset(arm, first_robot);
        reset(arm, second_robot);
    }
    // Go back to rest
    std::cout << "safely returning robots to sleep, please wait...\n";
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



    

    
order compile_order(std::string configuration, json pose)
{
    order new_order;
    new_order.object_pose = pose["obj" + configuration[0]];
    new_order.goal_pose = pose["goal" + configuration[1]];
    return new_order;
}

bool deliver_package(armController arm, order poses)
{
    // Pick and Place sequence
    arm.pick(poses.object_pose);
    arm.go_to_interm();
    arm.go_to(poses.goal_pose);
    arm.place(poses.goal_pose);
    return true;
}

bool reset(armController arm, order poses)
{

    // Reset by doing pick and place backwards
    arm.pick(poses.goal_pose);
    arm.go_to_interm();
    arm.go_to(poses.object_pose);
    arm.place(poses.object_pose);
    return true;
}