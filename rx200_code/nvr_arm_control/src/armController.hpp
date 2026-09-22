#pragma once
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose.hpp>
#include "json.hpp"
using json = nlohmann::json;
// this class sserves to organize the poses needed to pick and place and associate them with their respective object
class armController {
    public:
        armController( std::string intermPose, std::string gripperRelease, std::string gripperClench, 
            moveit::planning_interface::MoveGroupInterface &armPlanner, moveit::planning_interface::MoveGroupInterface &gripperPlanner);
        void pick(json object);
        void place(json object);
        void go_to(json object);
        void leave(json object);
        void go_to_interm();
        void go_to_sleep(); 


    private:
        std::string intermPose;
        std::string gripperRelease;
        std::string gripperClench;
        moveit::planning_interface::MoveGroupInterface &armPlanner; 
        moveit::planning_interface::MoveGroupInterface &gripperPlanner;
};
