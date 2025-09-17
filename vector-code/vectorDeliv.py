'''This class serves both as an easy way to run multiple robots, and
as the vehichle to implement the game, all needed functions and behaviors will be defined here'''
import asyncio 
import time
import anki_vector
from anki_vector.objects import CustomObjectTypes, CustomObjectMarkers 
from anki_vector.util import degrees, speed_mmps 
import math
class vecDeliv:

    def __init__ (self, robot, cube_Num):
        # robot is a anki_vector.conn.cozmoConnection.robot.Robot object
        self._robot = robot
        self._cubeID = cube_Num
        # from the person's position, goal 0 is far left, goal 1 is middle, goal 2 is far right
        self._goals = None
        self._alignDistmm = 200
    async def create(robot, cube_num):
        self = vecDeliv(robot, cube_num)
        self._goals = [await self._robot.world.define_custom_wall(CustomObjectTypes.CustomType01,
                                              100, 120,
                                              40, 40, True), 
                                              await self._robot.world.define_custom_wall(CustomObjectTypes.CustomType02,
                                              CustomObjectMarkers.Circles5,
                                              100, 120,
                                              40, 40, True), await self._robot.world.define_custom_wall(anki_vector.objects.CustomObjectTypes.CustomType03,
                                              CustomObjectMarkers.Hexagons5,
                                              100, 120,
                                              40, 40, True)]
        # set up goal markers Goals are x by x by x (still wip) at their base, a wall is used due to other options being not suitable
        return self
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
        have anki_vector search a little harder (maybe have him move around to account for the poor range of his vision)'''
        currBehavior = self._robot.start_behavior(anki_vector.behavior.BehaviorTypes.LookAroundInPlace)
        try: 
            found = await self._robot.world.wait_for_observed_light_cube(timeout = 40)
            while (int(found.cube_id) != int(cbID)):
                found = await self._robot.world.wait_for_observed_light_cube(timeout = 40, include_existing=False)
                # if we can't find the right cube, fail
        except asyncio.TimeoutError:
            anki_vector.behavior.Behavior.stop(currBehavior)
            await self._robot.say_text("I couldn't find my cube", use_cozmo_voice=True).wait_for_completed()
            return False
        anki_vector.behavior.Behavior.stop(currBehavior)
        
        
        return found
    async def lift_cube(self, target):
        await self._robot.dock_with_cube(target, num_retries=3, approach_angle=anki_vector.util.degrees(0)).wait_for_completed()
        await self._robot.set_lift_height(1.0).wait_for_completed()

    async def drop_cube(self):
        await self._robot.set_lift_height(0).wait_for_completed()
        # back away from cube to avoid messing with it accidentally
        await self._robot.drive_straight(anki_vector.util.distance_mm(-100), anki_vector.util.speed_mmps(100)).wait_for_completed()
    # if anki_vector fails for any reason, false is returned, other wise the pose of the desired object is returned instead
    async def find_goal(self, goalNum):
        await self._robot.set_head_angle(degrees(0)).wait_for_completed()
        if goalNum < 0 or goalNum > 2:
            self.failmsg("as that goal is not real!")
            return False 
        
        # look for goal
        # To-Do: make this more robust, 
        # have anki_vector search a little harder (maybe have him move around to account for the poor range of his vision)
        try:
            # check if we found the correct goals
            currBehavior = self._robot.start_behavior(anki_vector.behavior.BehaviorTypes.LookAroundInPlace)
            found = await self._robot.wait_for(anki_vector.objects.EvtObjectObserved,  timeout = 40)
            while (isinstance(found.obj, anki_vector.objects.LightCube) or isinstance(found.obj, anki_vector.objects.Charger) or 
                   self._goals[goalNum].object_type != found.obj.object_type):
                found = await self._robot.wait_for(anki_vector.objects.EvtObjectObserved,  timeout = 40)
                
        except asyncio.TimeoutError:
            anki_vector.behavior.Behavior.stop(currBehavior)
            await self._robot.say_text("I couldn't find the goal", use_cozmo_voice=True).wait_for_completed()
            return False 
        print("goal found!") 
        anki_vector.behavior.Behavior.stop(currBehavior)
        print (found.obj.pose)
        return found.obj
    
    async def deliver(self, goal):
        ''' Note that due to the restrictions of the SDK, anki_vector will be seeing
        the goals as a wall, so an offset must be applied so anki_vector arrives at the correct location
        Also: this current offset will not be finalized until a goal design is complete '''
        # this must be done like this, the API does not like existing poses being edited for some reason

        #calculate the x and y offsets using pythagoreans theorem
        xAlignOff = self._alignDistmm * math.cos(goal.pose._rotation.angle_z.radians)
        yAlignOff = self._alignDistmm * math.sin(goal.pose._rotation.angle_z.radians)
        destSetup = anki_vector.util.Pose(goal.pose.position.x - xAlignOff, goal.pose.position.y - yAlignOff, goal.pose.position.z, 
                               angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # dest = anki_vector.util.Pose(xdelivOff, ydelivOff, goal.pose.position.z, 
        #                        angle_z=goal.pose._rotation.angle_z, origin_id=goal.pose._origin_id )
        # align Cozmo with the goal entrance
        await self._robot.go_to_pose(destSetup).wait_for_completed()
        #await self._robot.go_to_pose(dest).wait_for_completed()
        #enter goal and deliver
        await self._robot.drive_straight(anki_vector.util.distance_mm(100), anki_vector.util.speed_mmps(100)).wait_for_completed()
        await self.drop_cube()

    # end point is a anki_vector pose
    '''  if return _to_start is set to true anki_vector will Ignore the end point argument 
    and just return to his starting position if not given one '''
    async def moveCube(self, cbID, endpoint = anki_vector.util.Pose(0,0, 0, angle_z=anki_vector.util.degrees(0))):
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
         await self._robot.go_to_pose(anki_vector.util.Pose(0,0, 0, angle_z=anki_vector.util.degrees(0))).wait_for_completed()