from cozCube import coz
import cozmo
from cozmo import * 
import asyncio


#this tests 2 cozmos at once, making sure that they can run concurrently
async def multiTest(cozmo1, cozmo2, loop):

    print ("Please input cube ID to assign the first cozmo to: ")
    c1 = coz(await cozmo1.wait_for_robot(), input())
    print ("Please input cube ID to assign the second cozmo to: ")
    c2 = coz( await cozmo2.wait_for_robot(), input())
    print ("Please input cube ID for 1st Cozmo to find: ")
    ID1 = input()
    print ("Please input cube ID for 2nd Cozmo to find: ")
    ID2 = input()
    task1 = loop.create_task(c1.findCube(ID1))
    task2 = loop.create_task(c2.findCube(ID2))
    await asyncio.gather(task1, task2)

#this tests moves with 2 cozmos at the same time
async def test_move(connection):
    print("Testing cube relocation")
    print ("Please input cube IDs for the first and secodn cozmos\nCozmo 1: ")
    ID1 = input()
    print ("Cozmo 2: ")
    ID2 = input()
    c1 = coz(await connection.wait_for_robot(), ID1)
    c2 = coz(await connection.wait_for_robot(), ID2)
    task1 = loop.create_task(c1.moveCube(ID1))
    task2 = loop.create_task(c2.moveCube(ID2))
    await asyncio.gather(task1, task2)
    

loop = asyncio.get_event_loop()
loop.run_until_complete(multiTest(cozmo.connect_on_loop(loop), cozmo.connect_on_loop(loop), loop))






