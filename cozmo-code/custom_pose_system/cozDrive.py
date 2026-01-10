# The lifter issue only exists with go to pose, but if finer control is required, these functions can be re-introduced
import cozmo
import time
import math



# + 37.5 cam -> middle of robot
# - 20.7 mm cam-> extended lifter
# note: the following functions will be implemented into the coz class proper if the methods prove effective

''' Some manual movement functions (cozmo does have these at higher levels, 
but having finer grain control with low level motor functions will be nice, plus this solves the lifter problem)'''
# takes in a distance in mm and travel time in sec, then travels the specified distance in the specified time
def drive_forward(robot, dist_mm, time_sec):
        # Note, research wise, manipulating time may be more impactful than speed, cosnider adding a way to just use distance and time
        # using classic no accel physics here D/T = V
        # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
        # add 37.5 to the distance to make the refrence point from cozmo's center, thus staying consistant for the differential drive math
        speed_mm = (dist_mm)/time_sec
        print ("Calculated:", speed_mm)
        robot.drive_wheel_motors(speed_mm, speed_mm, 0, 0)
        time.sleep(time_sec)
        robot.stop_all_motors()
        # wait to make sure the robot has wrapped up it's action before another command is recieved
        time.sleep(1)
        # takes in a change in angle and a time to complete the turn in, this is used for turning in place with precision
        

''' takes an angle to rotate by (this is an offset, NOT a destination), distance from either drive wheel to the center of the robot, and the time to do it in
    the robot will then turn in place by the specified degrees, CW is positive here, this is to make the programming logic easier '''
# this function currently does not work properly, needs tweaking if it is to be re-introduced
def turn(robot, angle_deg, rw, time_sec):
        print ("Params: Angle", angle_deg, "rw", rw, "turn time", time_sec)
        #convert angle to rads to properly apply equations
        angle_rad = float(angle_deg*(math.pi/180.0))
        print(angle_rad)

        speed_mm  = ((angle_rad/time_sec)*rw) * 1.74
        print("Calculated", speed_mm)
        robot.drive_wheel_motors(speed_mm, -speed_mm, 0, 0)
        time.sleep(time_sec)
        robot.stop_all_motors()
        # wait to make sure the robot has wrapped up it's action before another command is recieved
        time.sleep(1)  

# simple test if needed
async def test_move_functs(connection):
    robot = await connection.wait_for_robot()
    drive_forward(robot, 100, 2)
    turn(robot, 180, 27, 1)
    drive_forward(robot, 100, 2)
    turn(robot, -180, 27, 1)
cozmo.connect(test_move_functs)    