# this driver will test the custom functionality made for the norm violation project
# edit the function being called at the bottom to use differant tests!
import anki_vector.animation
import anki_vector.behavior
import anki_vector.world
from vectorDeliv import vecDeliv
import anki_vector
import asyncio
async def test_find_cube(vectorSerial):
    print("testing cube recognition")
    print ("Please input cube ID to assign the vector to: ")
    testiee = vecDeliv(vectorSerial, input())
    result = await testiee.findCube(input())
    '''TEST NEXT TIME'''
    if (result):
        print("Cube identified!")
        print(testiee.latestSeen.obj)
        testiee._robot.behavior.say_text("Cube Found!")
    #print("i'm out!\n")
    return 

async def test_move(vectorSerial):
    print("Testing cube relocation")
    print ("Please input cube ID to assign the cozmo to: ")
    ID = input()
    
    testiee = vecDeliv(vectorSerial, ID)
    await testiee.moveCube(ID)

# async def test_find_goal(connection):
#     print("Testing Goal Identification with goal 1")
#     testiee = await coz.create(await connection.wait_for_robot(), 1)
#     result = await testiee.find_goal(0)
#     if (result != False):
#         await testiee._robot.say_text("Goal Found!", play_excited_animation=True, use_cozmo_voice=True).wait_for_completed()
#         return
#     return


# async def test_deliver(connection):
#     print("Testing Goal Identification with goal 1")
#     testiee = await coz.create(await connection.wait_for_robot(), 1)
#     print(testiee._goals)
#     print("finding cube")
#     cube = await testiee.findCube(1)
#     if(cube == False):
#         print("couldn't find cube!")
#         return
#     print ("finding goal")
#     goalPose = await testiee.find_goal(0)
#     if(goalPose == False):
#         print ("could not find goal")
#         return
#     print("grabbing cube")
#     await testiee.lift_cube(cube)
#     print("delivering cube to goal")
#     print(goalPose)
#     await testiee.deliver(goalPose)
#     return

# async def test_return(connection):
#     print("Testing Goal Identification with goal 1")
#     testiee = await coz.create(await connection.wait_for_robot(), 1)
#     print(testiee._goals)
#     print("finding cube")
#     cube = await testiee.findCube(1)
#     if(cube == False):
#         print("couldn't find cube!")
#         return
#     print ("finding goal")
#     goalPose = await testiee.find_goal(0)
#     if(goalPose == False):
#         print ("could not find goal")
#         return
#     print("grabbing cube")
#     await testiee.lift_cube(cube)
#     print("delivering cube to goal")
#     print(goalPose)
#     await testiee.deliver(goalPose)
#     await testiee.reset_position()
#     return
# cozmo.connect_with_3dviewer(test_deliver, enable_camera_view=True)

async def main(Serial):
    #await test_find_cube(Serial)
    await test_move(Serial)

# use asyncio to properly run tests that need awaits 
asyncio.run(main("00a137df"))