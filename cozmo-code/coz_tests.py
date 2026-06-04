# this test set will test the custom functionality made for the norm violation project
# edit the function being called at the bottom to use differant tests!
import concurrent.futures
from cozCube import coz
import cozmo
from cozmo.util import distance_mm, degrees, speed_mmps 
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

    
    result = await testiee.find_goal(1)
    if (result != False):
        await testiee._robot.say_text("Goal Found!", play_excited_animation=True, use_cozmo_voice=True).wait_for_completed()
        return
    return

async def test_goal_approach(connection):
    print("Testing goal approach with goal 1")
    threadPool = concurrent.futures.ThreadPoolExecutor(3)
    testiee = await coz.create(await connection.wait_for_robot(), 1, threadPool)
    threadPool.submit(threading.main_thread())

    goalPose = await testiee.find_goal(1)
    print(goalPose)
    await testiee.deliver(goalPose)
    testiee._robot.stop_all_motors() 

async def test_deliver(connection):
    print ("delivering cube 1 to goal 1")
    threadPool = concurrent.futures.ThreadPoolExecutor(3)
    testiee = await coz.create(await connection.wait_for_robot(), 1, threadPool)
    threadPool.submit(threading.main_thread())
    print(testiee._goals)
    print("finding cube")
    cube = await testiee.findCube(1)
    if(cube == False):
        print("couldn't find cube!")
        return
    print ("finding goal")
    
    print("grabbing cube")
    await testiee.lift_cube(cube)
    goalPose = await testiee.find_goal(1)
    if(goalPose == False):
        print ("could not find goal")
        return
    print("delivering cube to goal")
    print(goalPose)
    await testiee.deliver(goalPose)
    return

async def test_game_deliver(connection):
    print ("delivering cube 1 to goal 1")
    targetCube = 2
    threadPool = concurrent.futures.ThreadPoolExecutor(3)
    testiee = await coz.create(await connection.wait_for_robot(), targetCube, threadPool)
    threadPool.submit(threading.main_thread())
    await testiee._robot.drive_straight(distance_mm(200), speed_mmps(100)).wait_for_completed()
    print("finding cube")
    cube = await testiee.findCube(targetCube)
    if(cube == False):
        print("couldn't find cube!")
        return
    print ("finding goal")
    
    print("grabbing cube")
    await testiee.lift_cube(cube)
    await testiee._robot.drive_straight(distance_mm(-200), speed_mmps(100)).wait_for_completed()
    goalPose = await testiee.find_goal(2)
    if(goalPose == False):
        print ("could not find goal")
        return
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
    goalPose = await testiee.find_goal(2)
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

# comzo may be missing goal due to cube vision?
cozmo.connect(test_game_deliver)