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
import cozmo.camera
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
import threading
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
    # upon intitializaton, a new thread pool executor is created if none is given,
    # a ll robots should be in the same thread pool
    def __init__ (self, robot, cube_Num, threadManager, pose = cozPose()):
        # robot is a cozmo.conn.cozmoConnection.robot.Robot object
        self._robot = robot
        self._cubeID = cube_Num
        # from the person's position, goal 0 is far left, goal 1 is middle, goal 2 is far right
        self._goals = None
        self._pose = pose
        self._alignDistmm = 200
        # start the camera stream seperate from the viewing window (this is reduntant if run_with_tkviwewr is used)
        self._robot.camera.image_stream_enabled = True
        self._robot.add_event_handler(cozmo.camera.EvtNewRawCameraImage, self.grabImg)
        print("Starting thread management")
        self._detect_pipe = tag_pipe()
        # intilaze and launch detector thread
        self._threads = threadManager
        # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
        time.sleep(0.5)
        finder = threading.Thread(target = self._apriltag_finder, args = (apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True)), self._detect_pipe))
        finder.daemon=True
        finder.start()
        #self._threads.submit(self._apriltag_finder, apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True)), self._detect_pipe)
    async def create(robot, cube_num, threadManager):
        self = coz(robot, cube_num, threadManager)
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
        #convert goal number to proper index
        goalNum = goalNum - 1
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

        # let the robot find the goal before processing a pose
        goalIndex = None
        scanner = 0
        while (goalIndex is None):
            await self.look_around_for_goal(self._detect_pipe)
            # search detections for the target
            for det in self._detect_pipe.detect:
                if (det.tag_id == goalNum):
                    goalIndex = scanner
                    break
                scanner += 1
                    
        print("goal found!") 
        goalPose = cozPose()
        goalPose._x = self._detect_pipe.detect [0][0][3] - 0.13
        goalPose._y = self._detect_pipe.detect [0][2][3]
        
        return goalPose 
        # except asyncio.TimeoutError:
        #     cozmo.behavior.Behavior.stop(currBehavior)
        #     await self._robot.say_text("I couldn't find the goal", use_cozmo_voice=True).wait_for_completed()
        #     return False 
        
    # This is effectively a go_to_Pose for apriltag points and can be used as such
    async def deliver(self, goalPose):
        print(goalPose)
        # mult dist by 100 so dist is in mm
        dist = (math.sqrt((goalPose._x * goalPose._x) + (goalPose._y * goalPose._y))) * 1000
        ang = math.atan2(goalPose._x, goalPose._y)
        if(ang <= 0):
            TA = self.turnAdjust * -1
        else:
            TA = self.turnAdjust
        # Replacdrivign commands with a cust_drive_forward call
        print("ang: ", math.degrees(ang))
        print ("adjusted ang", (math.degrees(ang)-TA))
        # note that the custom co-ords use right as the positive dir for both translation and rotation, so CLKwise is pos here
        print("Path Vector Magnitude: ", dist, " Angle ", math.degrees(ang))
        #drive.turn(robot, ang, 27, 1)
        await self._robot.turn_in_place(cozmo.util.degrees((-(math.degrees(ang)-TA)))).wait_for_completed()
        # await robot.drive_straight(cozmo.util.distance_mm(dist), cozmo.util.speed_mmps(100)).wait_for_completed()
        # await asyncio.sleep(0.05)

        # # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
        # # add 37.5 to the distance to make the refrence point from cozmo's center, thus staying consitant for the differential drive math.
        self.cust_drive_forward(dist - 37.5, 100)
        # self._robot.drive_wheel_motors(100, 100, 0, 0)
        
        # await asyncio.sleep(((dist * 1000)-40)/100)
        # self._robot.stop_all_motors()
        # await self._robot.set_lift_height(0).wait_for_completed()
        # await asyncio.sleep(1)
        # # robot.drive_wheel_motors(100, 100, 0, 0)
        # #   # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
        # #   # add 37.5 to the distance to make the refremce point from cozmo's center, thus staying consitant for the differential drive math.
        # # time.sleep(((dist) + 37.5)/100)
        # self._robot.stop_all_motors()
        await self._robot.set_lift_height(0).wait_for_completed()
        self.cust_drive_forward(-50, 100)
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
    def cust_drive_forward(self, dist_mm, speed_mm):
            # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
            # add 37.5 to the distance to make the refrence point from cozmo's center, thus staying consistant for the differential drive math
            time_sec = abs(dist_mm)/speed_mm
            # use a negative velocity if dist is < 1
            heading = dist_mm/abs(dist_mm)
            print ("Calculated:", time_sec)
            self._robot.drive_wheel_motors(speed_mm * heading, speed_mm * heading, 0, 0)
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
            self._robot.drive_wheel_motors(speed_mm, -speed_mm, 0, 0)
            time.sleep(time_sec)
            self._robot.stop_all_motors()
            # wait to make sure the robot has wrapped up it's action before another command is recieved
            time.sleep(1)  

    def _apriltag_finder(self, detector, detect_pipe):
        print(detect_pipe)
        print("finder: active", detect_pipe.active)
        print("fidner: search", detect_pipe.searching)
        print("fidner: found", detect_pipe.found)
        while (detect_pipe.active):
            time.sleep(0.2) 
            # print("fidner: search", detect_pipe.searching)
            # print("fidner: found", detect_pipe.found
            #print("detection pipe search status", detect_pipe.found)
            #print("fidner: search", detect_pipe.searching)
            # wait for the image stream to be fully active
            while(not self._robot.world.latest_image):
                print("inactive...")
                time.sleep(0.1)

            # wait for image
            with(self._detect_pipe.cond):
                self._detect_pipe.cond.wait()          
                # Cozmo gives it's images as a PIL.Image.Image object, It needs to be transformed into a GS numpy array
                # print(self._detect_pipe.image)
                # convert the raw image into greyscale
                GSImage = self._detect_pipe.image.convert("L")
                # upscale the image to improve detection
                upscaled = GSImage.resize((640, 480), resample=PIL.Image.NEAREST)
                #use the transformed image to detect april tags
                # note if more than one april tag is present, then an array is returned
                detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))
                #print(detections)
                if(detections and self._detect_pipe.searching and not self._detect_pipe.found):
                    print("goal found")
                    # stop searching, store data, and relay to the turn behavior that it's thread can terminate
                    self._robot.stop_all_motors()
                    detect_pipe.detect = detector.detection_pose(detections[0], self.cameraParams, 0.05, +1)
                    detect_pipe.found = True
        print("finishing up")
        return
    #Specific behavior to allow cozmo to search for the goals using apriltag, normal cozmo behaviors should be used for other behaviors
    # this particular function being async allows an easy way to wait for the detection without complicating the info pipe.
    async def look_around_for_goal(self, detect_pipe):
        print(detect_pipe)
        detect_pipe.searching = True
        #print("lookthread: searching = ", detect_pipe.searching)
        while (detect_pipe.found == False):
            #print("detection pipe found status", detect_pipe.found)
            self._robot.turn_in_place(cozmo.util.degrees(30), cozmo.util.speed_mmps(10))
            await asyncio.sleep(0.6)
            if (detect_pipe.found == False):
                self._robot.turn_in_place(cozmo.util.degrees(30), cozmo.util.speed_mmps(10))
            await asyncio.sleep(0.6)
            if (detect_pipe.found == False):    
               self._robot.turn_in_place(cozmo.util.degrees(-10), cozmo.util.speed_mmps(10))
            await asyncio.sleep(0.6)
        self._robot.stop_all_motors()
        detect_pipe.searching = False
        return detect_pipe.detect
    #call back for Cozmo image collection
    # Kw allows for any extra keyword args to be passed without crashing
    def grabImg(self, evt, **kwargs):
        #print("got one!")
        with self._detect_pipe.cond:
            self._detect_pipe.image = evt.image
            self._detect_pipe.imageNew = True
            # let the apriltag detector know that a new frame has come in
            self._detect_pipe.cond.notify()

    
    

#flag/info 'pipe' to collect positional goal data from tag thread

class tag_pipe:
    def __init__ (self):
        # Used to let tag node know if it neeeds to clear data to avoid error.
        self.searching = False
        # Used to tell turn behavior to stop after locating the goal.
        self.found = False
        # Used to get positional data back to the main.
        self.detect = None
        # Used to signify to the searching thread that it needs to terminate 
        self.active = True
        #stores the most recent cozmo image 
        self.image = None

        self.imgNew = False

        #used to make sure that the image stream isn't getting blocked
        self.cond = threading.Condition()
    
async def hello_world():
    print("hello world!")


