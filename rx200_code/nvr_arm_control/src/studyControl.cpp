//maybe come back to this if the project demands it
// #include <memory>
// #include <chrono>
// #include <rclcpp/rclcpp.hpp>
// #include <moveit/move_group_interface/move_group_interface.h>
// #include <geometry_msgs/msg/pose.hpp>
// #include <fstream>
// #include <thread>
#include <iostream>
// #include "armController.hpp"
// #include "json.hpp"
// #include "study_interfaces/action/study_run.hpp"
// #include "study_interfaces/srv/continue_ping.hpp"
// #include "study_interfaces/srv/send_command.hpp"

// #define INTERM_POSE "intermAlign"
// #define GRIPPER_OPEN "Released"
// #define GRIPPER_CLOSED "objGripped"
// typedef struct {
//         json object_pose;
//         json goal_pose;
// } order;

// using moveit::planning_interface::MoveGroupInterface;
// using ContinuePing = study_interfaces::srv::ContinuePing;
// using SendCommand = study_interfaces::srv::SendCommand;
// using StudyRun = study_interfaces::action::StudyRun;
// using GoalHandle = rclcpp_action::ServerGoalHandle<StudyRun>;


// class StudyControl : public rclcpp::Node
// {
//     public:
//         StudyControl() : Node("study_control")
//     {
//         // Setup the control object
//         arm_planning_interface = MoveGroupInterface(node, "interbotix_arm");
//         gripper_planning_interface = MoveGroupInterface(node, "interbotix_gripper");
//         arm = armController(INTERM_POSE, GRIPPER_OPEN, GRIPPER_CLOSED, arm_planning_interface, gripper_planning_interface);
//         // TO DO: figure out how to communicate with robot2
//         // Parse json for object set
//         std::ifstream poses_raw("/home/ws/src/nvr_arm_control/src/poses.json");
//         poses = json::parse(poses_raw);
//         action_server_ =
//         rclcpp_action::create_server<StudyRun>(
//             this,
//             "StudyRun",

//             std::bind(
//                 &StudyControl::handle_goal,
//                 this,
//                 std::placeholders::_1,
//                 std::placeholders::_2),

//             std::bind(
//                 &StudyControl::handle_cancel,
//                 this,
//                 std::placeholders::_1),

//             std::bind(
//                 &StudyControl::handle_accepted,
//                 this,
//                 std::placeholders::_1));
//         continue_ping_service_ =this->create_service<ContinuePing>(
//             "continue_ping",
//             std::bind(
//                 &StudyControl::continue_ping_callback,
//                 this,
//                 std::placeholders::_1,
//                 std::placeholders::_2));
//         send_command_service_=
//         this->create_service<sendCommand>(
//             "send_command",
//             std::bind(
//                 &StudyControl::send_command_callback,
//                 this,
//                 std::placeholders::_1,
//                 std::placeholders::_2));  
//     }

//     void execute(const std::shared_ptr<GoalHandle> goal_handle)
//     {
            

//     // Scope MoveIt interfaces so they are destroyed BEFORE ROS shutdown
    
//         // Start in a favorable position to avoid collisions
//         arm_planning_interface.setNamedTarget(INTERM_POSE);
//         arm_planning_interface.move();

//         // get into loop
//         /* grab command (repped as object 1, 2 or 3 then goal 1, 2, or 3. 
//         implicitly, the left arm is defined with the first two chars, the right with the last two
//         and the objects being numbered from left to right)
//         */
//         // // safely terminate if 'e' is given as input
//         // // so 6 chars, given as one string
//         // build structs to compile the commands
//         // execute in order given, reading the string from the left to right
//         // // struct 1 will be made with elms 0->1, while struct2 will be made wih elms 2->3
//         // wait for wizard to confirm reset, then re-use the structs to place the objects back
//         // // depending on how piloting goes, I may want to give the wizard the option on where things are returned to
//         //create containers to retain commands adn organize run order
//         order first_robot, second_robot;
//         // make the result to send out to ros later
//         auto result = std::make_shared<StudyRun::Result>();
//         auto feedback = std::make_shared<StudyRun::Feedback>();
        

//         while(true)
//         {
//             // TO DO: add more robust input and pose validation once the basic stuff is working
//             // wait for service call to give command after notifing who ever is listening
            
//             feedback->status = "WAITING_FOR_INPUT";

//             goal_handle->publish_feedback(feedback);

           
//             while (!cont)
//             {
//                 std::this_thread::sleep_for(
//                 std::chrono::milliseconds(1));
//             }
            
//             // turn off cont flag so we will pause befor execution
//             cont = false;
//             if(command == "e" || command.empty())
//             {
//                 break;
//             }
//             order first_robot = compile_order(command.substr(0, 2), poses);
//             // order second_robot = compile_order(command.substr(2, 2), poses);
//             // wait for confirm
           

//             deliver_package(arm, first_robot);
//             // TO DO: check for sucess here later
//             // un comment when 2nd robot is properly implemented
//               // feedback->status = "WAITING_FOR_CONFIRM_ARM2";

//             // goal_handle->publish_feedback(feedback);

//             //   while (!cont)
//             // {
//             //  std::this_thread::sleep_for(
//             //  std::chrono::milliseconds(1));
//             // }
//             // cont = false;
//             // deliver_package(arm, second_robot);

           
          


//             feedback->status = "WAITING_FOR_CONFIRM_ARM2";

//             goal_handle->publish_feedback(feedback);

//             while (!cont)
//             {
//              std::this_thread::sleep_for(
//              std::chrono::milliseconds(1));
//             }

//             cont = false;
//             reset(arm, first_robot);
//             // reset(arm, second_robot);
//         }
//         // Go back to rest
//         std::cout << "safely returning robots to sleep, please wait...\n";
//         arm_planning_interface.setNamedTarget("Sleep");
//         arm_planning_interface.move();
//         result -> message = "all done!";
//         result -> success = true;
//         goal_handle->succeed(result);
//         }
//     private:
//     rxlcpp::logeer logger = rclcpp::get_logger("study_control");
//     json poses;
//     armController arm;
//     std::atomic<bool> cont{false};
//     std::string command;
//     // ROS interfaces
//     rclcpp_action::Server<StudyRun>::SharedPtr action_server_;
//     rclcpp::Service<ContinuePing>::SharedPtr continue_ping_service_;
//     rclcpp::Service<SendCommand>::SharedPtr send_command_service_;
//     MoveGroupInterface arm_planning_interface;
//     MoveGroupInterface grippper_planning_interface;
//      // Action callbacks

//     // ROS uses this to decide wether an action should be run
//     rclcpp_action::GoalResponse handle_goal(
//            const rclcpp_action::GoalUUID & uuid,
//     std::shared_ptr<const StudyRun::Goal> goal)
//     {
//         RCLCPP_INFO(
//             logger,
//             "Received goal");

//         return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
//     }

//     // Handles the case for when the user wants to cancel the action
//     rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<GoalHandle> goal_handle)
//     {
//         RCLCPP_INFO(
//             logger,
//             "Received request to cancel goal");

//         return rclcpp_action::CancelResponse::ACCEPT;
//     }
    
    
//     // Action recieved, get into the robot logic, also run it in a separate thread so we can safely pause when needed 
// void handle_accepted(
//     const std::shared_ptr<GoalHandle> goal_handle)
// {
//     std::thread{
//         //placeholders allow ROS to feed it's neccecary arguments
//         std::bind(
//             &StudyControl::execute,
//             this,
//             std::placeholders::_1),
//         goal_handle
//     }.detach();
// }

//     // Service callbacks
//     void continue_ping_callback(const std::shared_ptr<ContinuePing::Request> request,
//     std::shared_ptr<ContinuePing::Response> response)
//     {
//         cont = true;
//         response -> status = true;
//         response -> message = "Continuing process";
//     }
//     void send_command_callback(const std::shared_ptr<SendCommand::Request> request,
//     std::shared_ptr<SendCommand::Response> response)
//     {
//         command = request->command;
//         cont = true;
//         response -> message = "Command recorded";
//         response -> status = true;
//     }

//     /* Takes in the info needed to re define the poses for the robot to target. 
// config is a 3 char string denoting the robot, object pose, and goal pose (L23, for example) */
//     // jhelpers for execuion
//     order compile_order(std::string configuration, json pose)
//     {
//         order new_order;
//         new_order.object_pose = pose["obj" + configuration[0]];
//         new_order.goal_pose = pose["goal" + configuration[1]];
//         return new_order;
//     }

//     bool deliver_package(armController arm, order poses)
//     {
//         // Pick and Place sequence
//         arm.pick(poses.object_pose);
//         arm.go_to_interm();
//         arm.go_to(poses.goal_pose);
//         arm.place(poses.goal_pose);
//         return true;
//     }

//     bool reset(armController arm, order poses)
//     {

//         // Reset by doing pick and place backwards
//         arm.pick(poses.goal_pose);
//         arm.go_to_interm();
//         arm.go_to(poses.object_pose);
//         arm.place(poses.object_pose);
//         return true;
//     }

// };
    







// int main(int argc, char * argv[])
// {
//     rclcpp::init(argc, argv);

//     auto node =
//         std::make_shared<StudyControl>();

//     rclcpp::spin(node);

//     rclcpp::shutdown();

//     return 0;
// }

int main()
{
    std::cout << "this node is under construction!\n";
}