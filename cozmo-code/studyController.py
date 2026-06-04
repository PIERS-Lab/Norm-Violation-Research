import cozmo
import concurrent
import asyncio
from cozmo.util import distance_mm, degrees, speed_mmps
from statemachine import StateMachine, State 
from cozCube import coz
# This program allows the wizard to make robot commands manually instead of using preset functions (primarily used for testing)
'''TODO: 
allow the user to input cubes and the goals of said cubes
add an option to autonomously reset robot positions
POTENTIAL:
Robot Speech
integration with behaviors to allow the wizard to inject behaviors/speech
'''

class studyController (StateMachine):
   
    # get the robot connections established and objects instantiated
    entry = State("entry", initial=True)
    assignment = State("assignment")
    orderDecide = State("orderDecide")
    autoReset = State("autoreset")
    # robot 1 then robot 2
    execute12 = State("execute12")
    # robot 2 then robot 1
    execute21 = State("execute21")

    # State trasitions
    start = entry.to(assignment)
    assignDone = assignment.to(orderDecide)
    start1 = orderDecide.to(execute12)
    start2 = orderDecide.to(execute21)
    resetDone = autoReset.to(assignment)

    # Resets
    resetOrders = orderDecide.to(assignment)
    reset12 = execute12.to(assignment)
    reset21 = execute21.to(assignment)
    autoResetDone = autoReset.to(assignment) 

    # Reset with automatic driving
    autoResetOrders = orderDecide.to(autoReset)
    autoReset12 = execute12.to(autoReset)
    autoReset21 = execute21.to(autoReset)


    async def on_enter_assignment(self):
        # use input to define internal robot instances
        # there is no input validation here, so the wizard should be careful
        print("State: assign params(CGCG)")
        params = input()
        await self.robot1.set_cube_ownership(params[0])
        self.robot1goal = params[1]
        await self.robot2.set_cube_ownership(params[2])
        self.robot2goal = params[3]
        await self.assignDone()
    async def on_enter_autoReset (self):
          # robots drive to origin, then reset
        await self.robot1._robot.go_to_pose(cozmo.util.Pose(0, 0, 0))
        await self.robot2._robot.go_to_pose(cozmo.util.Pose(0, 0, 0))
        await self.resetDone()
    
        
    async def on_enter_orderDecide (self):
         # use input to decide wether or not robot 1 or 2 should go first, wizard can reset here
        print("State: assign execution order (1, 2, ar)")
        order = input()
        if (order == "ar"):
            await self.autoResetOrders()
        elif (order == "1"):
            await self.start1()
        elif (order == "2"):
            await self.start2()
        else:
            await self.resetOrders()        

    async def on_enter_execute12 (self):
            # Could improve later by making some sort of injection object used to place code in the pauses
        print("State: executing with order 1->2 ([r] or [ar] at pause to reset use any other input to continue)")
        # robot 1
        await self.robot1._robot.drive_straight(distance_mm(200), speed_mmps(100)).wait_for_completed()
        cube = await self.robot1.findCube(self.robot1._cubeID)
        await self.robot1.lift_cube(cube)
        await self.robot1._robot.drive_straight(distance_mm(-200), speed_mmps(100)).wait_for_completed()
        goal = await self.robot1.find_goal(self.robot1goal)
        reset = input()
        if reset == "r":
            await self.reset12()
        elif reset == "ar":
            await self.autoReset12()
        goal = await self.robot1.find_goal(self.robot1goal)    
        await self.robot1.deliver(goal)
        reset = input()
        if reset == "r":
            await self.reset12()
        elif reset == "ar":
            await self.autoReset12()
        # robot 2 
        cube = await self.robot2.findCube(self.robot2._cubeID)
        await self.robot2.lift_cube(cube)
        goal = await self.robot2.find_goal(self.robot2goal)
        reset = input()
        if reset == "r":
            await self.reset12()
        elif reset == "ar":
            await self.autoReset12()
        goal = await self.robot2.find_goal(self.robot2goal)
        await self.robot2.deliver(goal)
        reset = input()
        if reset == "ar":
            await self.autoReset12()
        else:
            await self.reset12()

       
    async def do_on_enter_execute21 (self):
         # Could improve later by making some sort of injection object used to place code in the pauses
        print("State: executing with order 2->1 ([r] or [ar] at pause to reset use any other input to continue)")
        # robot 1
        cube = await self.robot1.findCube(self.robot2._cubeID)
        await self.robot1.lift_cube(cube)
        goal = await self.robot1.find_goal(self.robot2goal)
        reset = input()
        if reset == "r":
            self.autoReset21()
        elif reset == "ar":
            self.autoReset21()
        await self.robot1.deliver(goal)
        reset = input()
        if reset == "r":
            self.reset21()
        elif reset == "ar":
            self.autoReset21()
        # robot 2 
        cube = await self.robot1.findCube(self.robot1._cubeID)
        await self.robot1.lift_cube(cube)
        goal = await self.robot1.find_goal(self.robot1goal)
        reset = input()
        if reset == "r":
            await self.reset21()
        elif reset == "ar":
            await self.autoReset21()
        await self.robot2.deliver(goal)
        reset = input()
        if reset == "ar":
            await self.autoReset21()

        else:
            await self.reset21()

       

    async def create(cozmo1, cozmo2, loop):
         #   get both robots, connect, then instansiate
        self = studyController(cozmo1, cozmo2, loop)
        threadPool1 = concurrent.futures.ThreadPoolExecutor(3)
        threadPool2 = concurrent.futures.ThreadPoolExecutor(3)
        self.robot1 = await self.robot1.wait_for_robot()
        self.robot2 = await self.robot2.wait_for_robot()
        self.robot1 = await coz.create(self.robot1, 1, threadPool1)
        self.robot2 = await coz.create(self.robot2, 2, threadPool2)
        return self



    def __init__(self, cozmo1, cozmo2, loop):
        self.robot1 = cozmo1
        self.robot2 = cozmo2
        self.loop = loop
        super().__init__()
    
    async def activate(self):
        await self.start()
        

async def run(cozmo1, cozmo2, loop):
    control = await studyController.create(cozmo1, cozmo2, loop)
    await control.activate()
    print(control.current_state)
    while True:
        await asyncio.sleep(0.01)
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(cozmo.connect_on_loop(loop), cozmo.connect_on_loop(loop), loop))
    
#Just use the SM curr state w a switch statement, because apparently nothing wants to work with asyncad