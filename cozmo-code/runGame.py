# this is where real runs of the game will be run from, the particular variation will be determined via command line args
# Coz will be the robot starting on the left, while Moe will be ther robot starting on the right

''' The base run of the game, 
Coz will take his turn, moving cube 1 to goal 3, then the person will move cube 2 to goal 2, and finally moe will move cube 3 to goal 1
 '''

''' startup code that every run will need
connect the robots and set them up
The robots will Identify themselves so 
physical adjustments can be made if needed'''
import sys
from cozCube import coz
import cozmo
import asyncio
async def start(conn1, conn2, loop):
    # Newly definded functions must be added here 
    # note: the connections are gathered in the order that each robot's device was plugged in
    functions = {
        "base":base,
        "steal":test_norm_violation
    }
    Coz = (await coz.create(await conn1.wait_for_robot(), 3))
    Moe = (await coz.create(await conn2.wait_for_robot(), 1))
    await Coz._robot.say_text("Hey! I'm Coz!").wait_for_completed()
    await Moe._robot.say_text("Greetings! I'm Moe!").wait_for_completed()
    while (True):
        print("Enter the name of the function that you want to run.\n" 
        "Enter nothing to end the program")
        print("Functions: \n", functions)
        # run functions until the user gives invalid input
        call = input()
        if (call == "end" or call == "\n"):
            return
        await functions[call](Coz, Moe)
        print("Function Completed")
        
# base case: nothing crazy happens, just deliver    
async def base(Coz, Moe):
    await Coz._robot.say_text("I'll go first!").wait_for_completed()
    print("coz is finding his cube")
    cube = await Coz.findCube(3)
    print("coz is finding his goal")
    goalPose = await Coz.find_goal(0)
    await Coz._robot.say_text("Got It!", play_excited_animation = True).wait_for_completed()
    await Coz.lift_cube(cube)
    await Coz.deliver(goalPose)
    await Coz._robot.say_text("Your Turn!").wait_for_completed()
    # Person's turn: Wizard needs to prompt a move here by entering anything
    input()
    await Moe._robot.say_text("Here I go!").wait_for_completed()
    print("Moe is finding his cube")
    cube = await Moe.findCube(1)
    print("Moe is finding his goal")
    goalPose = await Moe.find_goal(2)
    await Moe.lift_cube(cube)
    await Moe._robot.say_text("Easy!").wait_for_completed()
    await Moe.deliver(goalPose)

# robot steals from person norm violation!:
async def test_norm_violation(connection1, connection2):
    print("Initializing first robot with cube 3")
    # cozmo1 = await coz.create(await connection1.wait_for_robot(), 3)
    print("Initializing second robot with cube 1")
    # cozmo2 = await coz.create(await connection2.wait_for_robot(), 1)
    print("Robot 1 finding cube 3")
    cube1 = await connection1.findCube(3)
    if cube1 == False:
        print("Robot 1 couldn't find cube 3!")
        return
    print("Robot 1 locating goal 1")
    goal1 = await connection1.find_goal(0)
    if goal1 == False:
        print("Robot 1 couldn't find goal 1!")
        return
    print("Robot 1 grabbing cube 3")
    await connection1.lift_cube(cube1)
    print("Robot 1 delivering cube 3 to goal 1")
    print(goal1)
    await connection1.deliver(goal1)
    print("Robot 2 finding cube 1")
    cube2 = await connection2.findCube(1)
    if cube2 == False:
        print("Robot 2 couldn't find cube 1!")
        return
    print("Robot 2 locating goal 2")
    goal2 = await connection2.find_goal(1)
    if goal2 == False:
        print("Robot 2 couldn't find goal 2!")
        return
    print("Robot 2 grabbing cube 1")
    await connection2.lift_cube(cube2)
    print("Robot 2 delivering cube 1 to goal 2")
    print(goal2)
    await connection2.deliver(goal2)
    return

# Code above
loop = asyncio.get_event_loop()
loop.run_until_complete(start(cozmo.connect_on_loop(loop), cozmo.connect_on_loop(loop), loop))
