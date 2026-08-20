#include "armController.hpp"


armController :: armController( std::string intermPose, std::string gripperRelease, std::string gripperClench. 
            moveit::planning_interface::MoveGroupInterface &armPlanner, moveit::planning_interface::MoveGroupInterface &gripperPlanner):
            intermPose(intermPose), gripperRelease(gripperRelease), gripperClench(gripperClench), gripperPlanner(*gripperPlanner), armPlanner(*armPlanner)
            {}
/* Each object will have an approah pose and an align pose that is assosiated, these are already defined
in the robot's set of poses, so only the names of said poses are required.

also to note: the object poses are representitive of their respective locationsat the start of the study, so they
will not update after the arm moves one.*/
void armController::pick(json object) {
    armPlanner.move(object["align"]);
    armPlanner.move(object["approach"]);
    gripperPlanner.move(gripperClench);
}
// IMPORTANT! The arm should already have picked before running this
void armController::place(json goal)
{
    gripperPlanner.move(gripperRelease);
    armPlanner.move(goal["align"]);
}
void armController::go_to(json object)
{
    armPlanner.move(object["align"]);
    armPlanner.move(object["approach"]);
}
void armController::leave(json object)
{
    armPlanner.move(object["align"]);
}         


