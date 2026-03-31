# this test set will test the custom functionality made for the norm violation project
# edit the function being called at the bottom to use differant tests!
import concurrent.futures
from cozCube import coz
import cozmo
from cozmo import *
import concurrent
import asyncio
import threading
import math
import time

TurnAdjust = 10

async def test_find_cube(connection):
    print("testing cube recognition")
    print ("Please input cube ID to assign the cozmo to: ")
    testiee = coz(await connection.wait_for_robot(), input())
    print ("please input the cube Id that cozmo should grab: ")
    result = await testiee.findCube(input())
    if (result):
        testiee._robot.say_text("Cube Found!", play_excited_animation=True,use_cozmo_voice=True).wait_for_completed()
    # print("i'm out!\n")
    return 

async def test_move(connection):
    print("Testing cube relocation")
    print ("Please input cube ID to assign the cozmo to: ")
    ID = input()
    testiee = coz(await connection.wait_for_robot(), ID)
    await testiee.moveCube(ID)

async def test_find_goal(connection):
    print("Testing Goal Identification with goal 1")
    threadPool = concurrent.futures.ThreadPoolExecutor(3)
    testiee = await coz.create(await connection.wait_for_robot(), 1, threadPool)
    threadPool.submit(threading.main_thread())

    
    result = await testiee.find_goal(0)
    if (result != False):
        await testiee._robot.say_text("Goal Found!", play_excited_animation=True, use_cozmo_voice=True).wait_for_completed()
        return
    return

async def test_goal_approach(connection):
    print("Testing goal approach with goal 1")
    threadPool = concurrent.futures.ThreadPoolExecutor(3)
    testiee = await coz.create(await connection.wait_for_robot(), 1, threadPool)
    threadPool.submit(threading.main_thread())

    goalPose = await testiee.find_goal(0)
    print(goalPose)
    dist = math.sqrt((goalPose._x * goalPose._x) + (goalPose._y * goalPose._y))
    ang = math.atan2(goalPose._x, goalPose._y)
    if(ang <= 0):
        TA = TurnAdjust * -1
    else:
        TA = TurnAdjust
    print("ang: ", math.degrees(ang))
    print ("adjusted ang", (math.degrees(ang)-TA))
    # note that the custom co-ords use right as the positive dir for both translation and rotation, so CLKwise is pos here
    print("Path Vector Magnitude: ", dist, " Angle ", math.degrees(ang))
    #drive.turn(robot, ang, 27, 1)
    await testiee._robot.turn_in_place(cozmo.util.degrees((-(math.degrees(ang)-TA)))).wait_for_completed()
    # await robot.drive_straight(cozmo.util.distance_mm(dist), cozmo.util.speed_mmps(100)).wait_for_completed()
    # await asyncio.sleep(0.05)
    testiee._robot.drive_wheel_motors(100, 100, 0, 0)
    # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
    # add 37.5 to the distance to make the refremce point from cozmo's center, thus staying consitant for the differential drive math.
    await asyncio.sleep(((dist * 1000)-40)/100)
    testiee._robot.stop_all_motors()
    await testiee._robot.set_lift_height(0).wait_for_completed()
    await asyncio.sleep(1)
    # robot.drive_wheel_motors(100, 100, 0, 0)
    #   # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
    #   # add 37.5 to the distance to make the refremce point from cozmo's center, thus staying consitant for the differential drive math.
    # time.sleep(((dist) + 37.5)/100)
    testiee._robot.stop_all_motors() 

async def test_deliver(connection):
    print("Testing Goal Identification with goal 1")
    testiee = await coz.create(await connection.wait_for_robot(), 1)
    print(testiee._goals)
    print("finding cube")
    cube = await testiee.findCube(1)
    if(cube == False):
        print("couldn't find cube!")
        return
    print ("finding goal")
    goalPose = await testiee.find_goal(0)
    if(goalPose == False):
        print ("could not find goal")
        return
    print("grabbing cube")
    await testiee.lift_cube(cube)
    print("delivering cube to goal")
    print(goalPose)
    await testiee.deliver(goalPose)
    return

async def test_return(connection):
    print("Testing Goal Identification with goal 1")
    testiee = await coz.create(await connection.wait_for_robot(), 1)
    print(testiee._goals)
    print("finding cube")
    cube = await testiee.findCube(1)
    if(cube == False):
        print("couldn't find cube!")
        return
    print ("finding goal")
    goalPose = await testiee.find_goal(0)
    if(goalPose == False):
        print ("could not find goal")
        return
    print("grabbing cube")
    await testiee.lift_cube(cube)
    print("delivering cube to goal")
    print(goalPose)
    await testiee.deliver(goalPose)
    await testiee.reset_position()
    return

cozmo.connect(test_goal_approach)