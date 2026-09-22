#include "armController.hpp"

armController :: armController( std::string intermPose, std::string gripperRelease, std::string gripperClench, 
            moveit::planning_interface::MoveGroupInterface &armPlanner, moveit::planning_interface::MoveGroupInterface &gripperPlanner):
            intermPose(intermPose), gripperRelease(gripperRelease), gripperClench(gripperClench), armPlanner(armPlanner), gripperPlanner(gripperPlanner)
            {}
/* Each object will have an approah pose and an align pose that is assosiated, these are already defined
in the robot's set of poses, so only the names of said poses are required.

also to note: the object poses are representitive of their respective locationsat the start of the study, so they
will not update after the arm moves one.*/
void armController::pick(json object) {
    armPlanner.setNamedTarget(object["align"]);
    armPlanner.move();
    gripperPlanner.setNamedTarget(gripperRelease);
    gripperPlanner.move();
    armPlanner.setNamedTarget(object["approach"]);
    armPlanner.move();
    gripperPlanner.setNamedTarget(gripperClench);
    gripperPlanner.move();
    armPlanner.setNamedTarget(object["align"]);
    armPlanner.move();
}

// IMPORTANT! The arm should already have picked before calling this!
void armController::place(json goal)
{
    gripperPlanner.setNamedTarget(gripperRelease);
    gripperPlanner.move();
    armPlanner.setNamedTarget(goal["align"]);
    armPlanner.move();
}

void armController::go_to(json object)
{
    armPlanner.setNamedTarget(object["align"]);
    armPlanner.move();
    armPlanner.setNamedTarget(object["approach"]);
    armPlanner.move();
}

void armController::leave(json object)
{
    armPlanner.setNamedTarget(object["align"]);
    armPlanner.move();
    armPlanner.setNamedTarget(intermPose);
    armPlanner.move();
}

void armController::go_to_interm()
{
    armPlanner.setNamedTarget(intermPose);
    armPlanner.move();
}         

void armController::go_to_sleep()
{
    armPlanner.setNamedTarget("Sleep");
    armPlanner.move();
}         


