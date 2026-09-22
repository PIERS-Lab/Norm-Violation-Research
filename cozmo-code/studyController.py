import cozmo
import concurrent
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
    async def create(self, cozmo1, cozmo2, loop):
         #   get both robots, connect, then instansiate
        self = studyController(cozmo1, cozmo2, loop)
        threadPool1 = concurrent.futures.ThreadPoolExecutor(3)
        threadPool2 = concurrent.futures.ThreadPoolExecutor(3)
        self.robot1 = await coz.create(self.robot1, 1, threadPool1)
        self.robot2 = await coz.create(self.robot2, 2, threadPool2)



    def __init__(self, cozmo1, cozmo2, loop):
        self.robot1 = cozmo1
        self.robot2 = cozmo2
        self.loop = loop
    # get the robot connections established and objects instantiated
    setup = State()
    assignemnt = State()
    orderDecide = State()
    autoReset = State()
    # robot 1 then robot 2
    execute12 = State()
    # robot 2 then robot 1
    execute21 = State()

    # State trasitions
    setupDone = setup.to(assignemnt)
    assignDone = assignemnt.to(orderDecide)
    start1 = orderDecide.to(execute12)
    start2 = orderDecide.to(execute21)
    resetDone = autoReset.to(assignemnt)

    # Resets
    resetOrders = orderDecide.to(assignemnt)
    reset12 = execute12.to(assignemnt)
    reset21 = execute21.to(assignemnt)
    autoResetDone = autoReset.to(assignemnt) 

    # Reset with automatic driving
    autoResetOrders = orderDecide.to(autoReset)
    autoReset12 = execute12.to(autoReset)
    autoReset21 = execute21.to(autoReset)


    async def on_assignemnt(self):
        # use input to define internal robot instances
        # there is no input validation here, so the wizard should be careful
        print("State: assign params(CGCG)")
        params = input()
        self.robot1.set_cube_ownership(params[0])
        self.robot1goal = params[1]
        self.robot2.set_cube_ownership(params[2])
        self.robot2goal = params[3]
        self.assignDone()
        
        
        
    async def on_orderDecide (self):
        # use input to decide wether or not robot 1 or 2 should go first, wizard can reset here
        print("State: assign execution order (1, 2, ar)")
        order = input()
        if (order == "ar"):
            self.autoResetOrders()
        elif (order == "1"):
            self.start1()
        elif (order == "2"):
            self.start2()
        else:
            self.resetOrders()        

        pass
    async def on_autoReset (self):
        # robots drive to origin, then reset
        await self.robot1._robot.go_to_pose(cozmo.util.Pose(0, 0, 0))
        await self.robot2._robot.go_to_pose(cozmo.util.Pose(0, 0, 0))
        self.resetDone()

    # robot 1 then robot 2
    async def on_execute12 (self):
        # Could improve later by making some sort of injection object used to place code in the pauses
        print("State: executing with order 1->2 ([r] or [ar] at pause to reset use any other input to continue)")
        # robot 1
        cube = await self.robot1.findCube(self.robot1._cubeID)
        await self.robot1.lift_cube(cube)
        goal = await self.robot1.find_goal(self.robot1goal)
        reset = input()
        if reset == "r":
            self.reset12()
        elif reset == "ar":
            self.autoReset12()
        await self.robot1.deliver(goal)
        reset = input()
        if reset == "r":
            self.reset12()
        elif reset == "ar":
            self.autoReset12()
        # robot 2 
        cube = await self.robot2.findCube(self.robot2._cubeID)
        await self.robot2.lift_cube(cube)
        goal = await self.robot2.find_goal(self.robot2goal)
        reset = input()
        if reset == "r":
            self.reset12()
        elif reset == "ar":
            self.autoReset12()
        await self.robot2.deliver(goal)
        reset = input()
        if reset == "ar":
            self.autoReset12()

        else:
            self.reset12()

    async def on_execute21 (self):
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
            self.reset21()
        elif reset == "ar":
            self.autoReset21()
        await self.robot2.deliver(goal)
        reset = input()
        if reset == "ar":
            self.autoReset21()

        else:
            self.reset21()


        

    
