'''This class serves both as an easy way to run multiple robots, and
as the vehichle to implement the game, all needed functions and behaviors will be defined here'''
# next development steps 
# 1: implement movement commands as member functions  Y
# 2: integrate camera/tag mechanics with threads (have detector running in the back round and a fucntion to grab latest detections) X
# 3: integrate "turn in place" so that the detector can still run during a cozmo loop X

# use a member var to store goal path, reset this on every search to effectively clear previous goal search data during runtime



#Curr Err lies with angle conversion somewhere
import asyncio 
import time
import cozmo 
from cozmo import *
from cozmo.util import degrees
from cozmo.objects import CustomObjectMarkers
import math
from custom_pose_system.cozmoPose import cozPose
import concurrent.futures.thread
import apriltag
import PIL
from matplotlib import pyplot as plt
from custom_pose_system.cozmoPose import cozPose
from custom_pose_system import cozDrive as drive
import time
import numpy
import math
class coz:
    # focal x, focal y, center x, center y
    cameraParams = {288.87, 288.36, 155.11, 111.40}
    # in meters
    tagSize = 0.05
    # in mm
    centerOff = 37.5

    drivespeedmmps = 100.0

    turnspeedstrtmmps = 100.0
    # cozmo's camera readings were consistantly off to the right by ~140 mm, adding this offset in re-adjusts to what's expected
    # CONSIDERATION: re calibration is a more desireable fix,if there are more problems down the road come try that 
    cameraxoff = -0.14
    # made to adjust calculated angle away from error (degrees).
    turnAdjust = 10
    def __init__ (self, robot, cube_Num, pose = cozPose()):
        # robot is a cozmo.conn.cozmoConnection.robot.Robot object
        self._robot = robot
        self._cubeID = cube_Num
        # from the person's position, goal 0 is far left, goal 1 is middle, goal 2 is far right
        self._goals = None
        self._pose = pose
        self._alignDistmm = 200
        # start the camera stream seperate from the viewing window (this is reduntant if run_with_tkviwewr is used)
        self._robot.camera.image_stream_enabled = True
        self._detect_pipe = tag_pipe()
        # intilaze and launch detector thread
        self._threads = concurrent.futures.ThreadPoolExecutor(4)
        # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
        self._threads.submit(self._apriltag_finder, apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True)), self._detect_pipe)

    async def create(robot, cube_num):
        self = coz(robot, cube_num)
        self._goals = [await self._robot.world.define_custom_wall(cozmo.objects.CustomObjectTypes.CustomType01,
                                              CustomObjectMarkers.Triangles5,
                                              100, 120,
                                              40, 40, True), 
                                              await self._robot.world.define_custom_wall(cozmo.objects.CustomObjectTypes.CustomType02,
                                              CustomObjectMarkers.Circles5,
                                              100, 120,
                                              40, 40, True), await self._robot.world.define_custom_wall(cozmo.objects.CustomObjectTypes.CustomType03,
                                              CustomObjectMarkers.Hexagons5,
                                              100, 120,
                                              40, 40, True)]
        # set up goal markers Goals are x by x by x (still wip) at their base, a wall is used due to other options being not suitable
        return self
    
    def __del__ (self):
        # signal detector thread to terminate
        self._detect_pipe.active = False
        # give threads time to terminate
        time.sleep(0.5)

    async def failmsg(self, detail = "."):
        await self._robot.say_text("I can't do that! " + detail).wait_for_completed()

    # It needs to take input as apart of analyzing the task
    # returns the found lightcube object
    async def findCube(self, cbID):
        await self._robot.set_head_angle(degrees(0)).wait_for_completed()
        if (cbID != self._cubeID):
            await self.failmsg(detail = "as I don't own this cube")
            return
        # look for cube
        ''' To-Do: make this more robust, 
        have cozmo search a little harder (maybe have him move around to account for the poor range of his vision)'''
        currBehavior = self._robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try: 
            found = await self._robot.world.wait_for_observed_light_cube(timeout = 40)
            while (int(found.cube_id) != int(cbID)):
                found = await self._robot.world.wait_for_observed_light_cube(timeout = 40, include_existing=False)
                # if we can't find the right cube, fail
        except asyncio.TimeoutError:
            cozmo.behavior.Behavior.stop(currBehavior)
            await self._robot.say_text("I couldn't find my cube", use_cozmo_voice=True).wait_for_completed()
            return False
        cozmo.behavior.Behavior.stop(currBehavior)
        
        
        return found
    async def lift_cube(self, target):
        await self._robot.dock_with_cube(target, num_retries=3, approach_angle=cozmo.util.degrees(0)).wait_for_completed()
        await self._robot.set_lift_height(1.0).wait_for_completed()

    async def drop_cube(self):
        await self._robot.set_lift_height(0).wait_for_completed()
        # back away from cube to avoid messing with it accidentally
        await self._robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()
    # if cozmo fails for any reason, false is returned, other wise the pose of the desired object (cozmoPose) is returned instead
    async def find_goal(self, goalNum):
        await self._robot.set_head_angle(degrees(0)).wait_for_completed()
        if goalNum < 0 or goalNum > 2:
            self.failmsg("as that goal is not real!")
            return False 
        # look for goal
        # To-Do: make this more robust, 
        # have cozmo search a little harder (maybe have him move around to account for the poor range of his vision
        # check if we found the correct goals
        # prepare flags properly
        self._detect_pipe.searching = True
        self._detect_pipe.found = False
        self._detect_pipe.detect = None
        ''' 
        look _around should take control of the main thread until it is done, so
        it can be assumed that the detect pipe will have relevant info. once the fucntion finishes up.
        ''' 
        self.look_around(self._detect_pipe)
        
        #note: Implement multi-tag sorting later
        print("goal found!") 
        goalPose = cozPose()
        goalPose._x = self._detect_pipe.detect [0][0][3] - 0.13
        goalPose._y = self._detect_pipe.detect [0][2][3]
        return        
        # except asyncio.TimeoutError:
        #     cozmo.behavior.Behavior.stop(currBehavior)
        #     await self._robot.say_text("I couldn't find the goal", use_cozmo_voice=True).wait_for_completed()
        #     return False 
        
    
    async def deliver(self, goal):
        goalPose = self.find_goal(goal)
        print (goalPose)
        ''' Note that due to the restrictions of the SDK, cozmo will be seeing
        the goals as a wall, so an offset must be applied so cozmo arrives at the correct location
        Also: this current offset will not be finalized until a goal design is complete '''
        # this must be done like this, the API does not like existing poses being edited for some reason
        #goal stuff
        # #calculate the x and y offsets using pythagoreans theorem
        # xAlignOff = self._alignDistmm * math.cos(goal.pose._rotation.angle_z.radians)
        # yAlignOff = self._alignDistmm * math.sin(goal.pose._rotation.angle_z.radians)
        # destSetup = cozmo.util.Pose(goal.pose.position.x - xAlignOff, goal.pose.position.y - yAlignOff, goal.pose.position.z, 
        #                        angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # # dest = cozmo.util.Pose(xdelivOff, ydelivOff, goal.pose.position.z, 
        # #                        angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # # align Cozmo with the goal entrance
        # await self._robot.go_to_pose(destSetup).wait_for_completed()
        # #await self._robot.go_to_pose(dest).wait_for_completed()
        # #enter goal and deliver
        # await self._robot.drive_straight(cozmo.util.distance_mm(100), cozmo.util.speed_mmps(100)).wait_for_completed()
        # await self.drop_cube()
        

          # plan a straight path from cozmo to the goal pose
          # use simple trig, dist = sqrt(x^2+y^2) for dist, theta = tan^-1(delta x/delta y)
        dist = math.sqrt((goalPose._x * goalPose._x) + (goalPose._y * goalPose._y))
        ang = math.atan2(goalPose._x, goalPose._y)
        if(ang <= 0):
            TurnAdjust *= -1
        print("ang: ", math.degrees(ang))#calculate the x and y offsets using pythagoreans theorem
        # xAlignOff = self._alignDistmm * math.cos(goal.pose._rotation.angle_z.radians)
        # yAlignOff = self._alignDistmm * math.sin(goal.pose._rotation.angle_z.radians)
        # destSetup = cozmo.util.Pose(goal.pose.position.x - xAlignOff, goal.pose.position.y - yAlignOff, goal.pose.position.z, 
        #                        angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # # dest = cozmo.util.Pose(xdelivOff, ydelivOff, goal.pose.position.z, 
        # #                        angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # # align Cozmo with the goal entrance
        # await self._robot.go_to_pose(destSetup).wait_for_completed()
        # #await self._robot.go_to_pose(dest).wait_for_completed()
        # #enter goal and deliver
        # await self._robot.drive_straight(cozmo.util.distance_mm(100), cozmo.util.speed_mmps(100)).wait_for_completed()
        # await self.drop_cube()

        print ("adjusted ang", (math.degrees(ang)-TurnAdjust))
          # note that the custom co-ords use right as the positive dir for both translation and rotation, so CLKwise is pos here
        print("Path Vector Magnitude: ", dist, " Angle ", math.degrees(ang))
        #drive.turn(robot, ang, 27, 1)
        await self._robot.turn_in_place(cozmo.util.degrees((-(math.degrees(ang)-TurnAdjust)))).wait_for_completed()
        # await robot.drive_straight(cozmo.util.distance_mm(dist), cozmo.util.speed_mmps(100)).wait_for_completed()
        # await asyncio.sleep(0.05)
        
        self.cust_drive_forward(dist, 1)
        await self._robot.set_lift_height(0).wait_for_completed
        self.cust_drive_forward(-100, 1)
        return
    # end point is a cozmo pose
    '''  if return _to_start is set to true cozmo will Ignore the end point argument 
    and just return to his starting position if not given one '''
    async def moveCube(self, cbID, endpoint = cozmo.util.Pose(0,0, 0, angle_z=cozmo.util.degrees(0))):
        temp = await self.findCube(cbID)
        if (temp == False):
            return False
        await self.lift_cube(temp)
        await self._robot.go_to_pose(endpoint).wait_for_completed()
        await self.drop_cube()

    async def set_cube_ownership(self, cubeID):
        self._cubeID = cubeID


    async def reset_position(self):
         await self._robot.set_head_angle(degrees(0)).wait_for_completed()
         await self._robot.set_lift_height(0).wait_for_completed() 
         await self._robot.go_to_pose(cozmo.util.Pose(0,0, 0, angle_z=cozmo.util.degrees(0))).wait_for_completed()
        
        # + 37.5 cam -> middle of robot
    # - 20.7 mm cam-> extended lifter
    # note: the following functions will be implemented into the coz class proper if the methods prove effective

    ''' Some manual movement functions (cozmo does have these at higher levels, 
    but having finer grain control with low level motor functions will be nice, plus this solves the lifter problem)'''
    # takes in a distance in mm and travel time in sec, then travels the specified distance in the specified time
    def cust_drive_forward(self, dist_mm, time_sec):
            # Note, research wise, manipulating time w be more impactful than speed, cosnider adding a way to just use distance and time
            # using classic no accel physics here D/T = V
            # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
            # add 37.5 to the distance to make the refrence point from cozmo's center, thus staying consistant for the differential drive math
          # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
          # add 37.5 to the distance to make the refremce point from cozmo's center, thus staying consitant for the differential drive math.
            speed_mm = (dist_mm)/time_sec
            print ("Calculated:", speed_mm)
            self._robot.drive_wheel_motors(speed_mm, speed_mm, 0, 0)
            time.sleep(time_sec)
            self._robot.stop_all_motors()
            # wait to make sure the robot has wrapped up it's action before another command is recieved
            time.sleep(0.5)
            # takes in a change in angle and a time to complete the turn in, this is used for turning in place with precision
            

    ''' takes an angle to rotate by (this is an offset, NOT a destination), distance from either drive wheel to the center of the robot, and the time to do it in
        the robot will then turn in place by the specified degrees, CW is positive here, this is to make the programming logic easier '''
    # this function currently does not work properly, needs tweaking if it is to be re-introduced
    def cust_turn(self, angle_deg, rw, time_sec):
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

    def _apriltag_finder(self, detector, detectionPipe):
        while (detectionPipe.active):
            image = self._robot.wait_for(cozmo.camera.EvtNewRawCameraImage, None)
            print("image found")
                # Cozmo gives it's images as a PIL.Image.Image object, It needs to be transformed into a GS numpy array

                # convert the raw image into greyscale
            GSImage = image.image.convert("L")
            upscaled = GSImage.resize((640, 480), resample=PIL.Image.NEAREST)

                #convert greyscale Image into a numpy array
            GSImage = numpy.array(GSImage, dtype=numpy.uint8)
                #used the transformed image to detect april tags

                # note if more than one april tag is present, then an array is returned
            detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))

            if(detections and detectionPipe.searching and not detectionPipe.found):
                # stop searching, store data, and relay to the turn behavior that it's thread can terminate
                self._robot.stop_all_motors()
                detectionPipe = detector.detection_pose(detections[0], self.cameraParams, 0.05, +1)
                detectionPipe.searching = False
                detectionPipe.found = True
        return
    #need to check before every movement, motors will be stopped by detector
    def look_around(self, detectionPipe):
        while (detectionPipe.found == False):
            self._robot.turn_in_place(cozmo.util.rotation_z_angle(cozmo.util.degrees(50)), cozmo.util.speed_mmps(10))
            time.sleep(1)
            if (detectionPipe.found == False):
                self._robot.turn_in_place(cozmo.util.rotation_z_angle(cozmo.util.degrees(50)), cozmo.util.speed_mmps(10))
                time.sleep(1)
            if (detectionPipe.found == False):    
                self._robot.turn_in_place(cozmo.util.rotation_z_angle(cozmo.util.degrees(-30)), cozmo.util.speed_mmps(10))
                time.sleep(1)
        return detectionPipe.dectect
    

#flag/info 'pipe' to collect positional goal data from tag thread

class tag_pipe:
    def __init__ (self):
        # Used to let tag node know if it neeeds to clear data to avoid error.
        searching = False
        # Used to tell turn behavior to stop after locating the goal.
        found = False
        # Used to get positional data back to the main.
        detect = None
        # Used to signify to the searching thread that it needs to terminate 
        active = True