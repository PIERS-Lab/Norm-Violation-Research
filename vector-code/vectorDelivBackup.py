'''This class serves both as an easy way to run multiple robots, and
as the vehichle to implement the game, all needed functions and behaviors will be defined here'''
import asyncio
from asyncio import wrap_future
import time
import threading
import anki_vector
import anki_vector.events
from anki_vector.objects import CustomObjectTypes, CustomObjectMarkers 
import anki_vector.objects
from anki_vector.util import degrees, speed_mmps, distance_mm
import anki_vector.world 
from vectorEventWatcher import vectorObjectWatcher
import math
class vecDeliv:
    def __init__ (self, serialNum, cube_Num):
        # To prep vector to program, only the serial num is needed (note this can also auto parse cmd line args for this)
        self._robot = anki_vector.AsyncRobot(serialNum, show_viewer=True)
        self._robot.connect()
        self._cubeID = cube_Num
        # from the person's position, goal 0 is far left, goal 1 is middle, goal 2 is far right
        self._goals = None
        self._alignDistmm = 200
        # most recently observed object
        self.latestSeen = vectorObjectWatcher(self._robot, anki_vector.events.Events.object_appeared)
    async def create(serialNum, cube_num):
        self = vecDeliv(serialNum, cube_num)
        self._goals = [await wrap_future (self._robot.world.define_custom_wall(CustomObjectTypes.CustomType01,
                                              100, 120,
                                              40, 40, True), 
                                              await wrap_future(self._robot.world.define_custom_wall(CustomObjectTypes.CustomType02,
                                              CustomObjectMarkers.Circles5,
                                              100, 120,
                                              40, 40, True)), await wrap_future(self._robot.world.define_custom_wall(CustomObjectTypes.CustomType03,
                                              CustomObjectMarkers.Hexagons5,
                                              100, 120,
                                              40, 40, True)))]
        # set up goal markers Goals are 10 mm by 15 mm by 12 mm, a wall is used due to other options being not suitable
        return self
    async def failmsg(self, detail = "."):
        await wrap_future(self._robot.behavior.say_text("I can't do that! " + detail))
    # It needs to take input as apart of analyzing the task
    # returns the found lightcube object
    async def findCube(self, cbID):
        print("Start")
        await wrap_future(self._robot.behavior.set_head_angle(degrees(0)))
        if (cbID != self._cubeID):
            await self.failmsg(detail = "as I don't own this cube")
            return
        # look for cube
        ''' To-Do: make this more robust, 
        have Vector search a little harder (maybe have him move around to account for the poor range of his vision)'''
        secs = 0
        sTime = time.clock_gettime(1)
        try: 
            ''' FINISH AND TEST'''
            while(True):
                currBehavior = await wrap_future(self._robot.behavior.look_around_in_place())
                print (self.latestSeen.obj)
                if (self.latestSeen.obj == anki_vector.objects.LightCube):
                    return self.latestSeen.obj 
                # setup timeout so vector doesn't get stuck searching
                if (sTime - time.clock_gettime(1) >= 20.0):
                    raise asyncio.TimeoutError
            # Vector only has one cube, so this will require a different implementation
            # while (int(found.cube_id) != int(cbID)):
            #     found = await wrap_future self._robot.world.wait_for_observed_light_cube(timeout = 40, include_existing=False)
            #     # if we can't find the right cube, fail
        except asyncio.TimeoutError:
            await wrap_future (self._robot.behavior.say_text("I couldn't find my cube"))
            return False
        
    async def lift_cube(self, target):
        await wrap_future(self._robot.behavior.dock_with_cube(target, num_retries=3, approach_angle=anki_vector.util.degrees(0)))
        await wrap_future(self._robot.behavior.set_lift_height(1.0))

    async def drop_cube(self):
        await wrap_future(self._robot.behavior.set_lift_height(0))
        # back away from cube to avoid messing with it accidentally
        await wrap_future(self._robot.behavior.drive_straight(distance_mm(-100), anki_vector.util.speed_mmps(100)))
    # if anki_vector fails for any reason, false is returned, other wise the pose of the desired object is returned instead
    async def find_goal(self, goalNum):
        await wrap_future(self._robot.behavior.set_head_angle(degrees(0)))
        if goalNum < 0 or goalNum > 2:
            self.failmsg("as that goal is not real!")
            return False 
        
        # look for goal * math.
        # To-Do: make this more robust, 
        # have anki_vector search a little harder (maybe have him move around to account for the poor range of his vision)
        try:
            # check if we found the correct goals
            currBehavior = self._robot.start_behavior(anki_vector.behavior.BehaviorTypes.LookAroundInPlace)
            found = await wrap_future(self._robot.wait_for(anki_vector.objects.EvtObjectObserved,  timeout = 40))
            while (isinstance(found.obj, anki_vector.objects.LightCube) or isinstance(found.obj, anki_vector.objects.Charger) or 
                   self._goals[goalNum].object_type != found.obj.object_type):
                found = await wrap_future(self._robot.wait_for(anki_vector.objects.EvtObjectObserved,  timeout = 40))
                
        except asyncio.TimeoutError:
            anki_vector.behavior.Behavior.stop(currBehavior)
            await wrap_future(self._robot.behavior.say_text("I couldn't find the goal", use_cozmo_voice=True))
            return False 
        print("goal found!") 
        anki_vector.behavior.Behavior.stop(currBehavior)
        print (found.obj.pose)
        return found.obj
    
    async def deliver(self, goal):
        ''' Note that due to the restrictions of the SDK, Vectpr will be seeing
        the goals as a wall, so an offset must be applied so anki_vector arrives at the correct location'''
        # this must be done like this, the API does not like existing poses being edited for some reason

        #calculate the x and y offsets using pythagoreans theorem
        xAlignOff = self._alignDistmm * math.cos(goal.pose._rotation.angle_z.radians)
        yAlignOff = self._alignDistmm * math.sin(goal.pose._rotation.angle_z.radians)
        destSetup = anki_vector.util.Pose(goal.pose.position.x - xAlignOff, goal.pose.position.y - yAlignOff, goal.pose.position.z, 
                               angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # dest = anki_vector.util.Pose(xdelivOff, ydelivOff, goal.pose.position.z, 
        #                        angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # align Cozmo with the goal entrance
        await wrap_future(self._robot.go_to_pose(destSetup))
        #await wrap_future self._robot.go_to_pose(dest)
        #enter goal and deliver
        await wrap_future(self._robot.drive_straight(anki_vector.util.distance_mm(100), anki_vector.util.speed_mmps(100)))
        await wrap_future(self.drop_cube())

    # end point is a anki_vector pose
    '''  if return _to_start is set to true anki_vector will Ignore the end point argument 
    and just return to his starting position if not given one '''
    async def moveCube(self, cbID, endpoint = anki_vector.util.Pose(0,0, 0, angle_z=anki_vector.util.degrees(0))):
        temp = await wrap_future(self.findCube(cbID))
        if (temp == False):
            return False
        await wrap_future(self.lift_cube(temp))
        await wrap_future(self._robot.go_to_pose(endpoint))
        await wrap_future(self.drop_cube())

    async def set_cube_ownership(self, cubeID):
        self._cubeID = cubeID


    async def reset_position(self):
         await wrap_future(self._robot.set_head_angle(degrees(0)))
         await wrap_future(self._robot.set_lift_height(0)) 
         await wrap_future(self._robot.go_to_pose(anki_vector.util.Pose(0,0, 0, angle_z=anki_vector.util.degrees(0))))