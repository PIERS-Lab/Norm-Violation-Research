# this driver will test the custom functionality made for the norm violation project
# edit the function being called at the bottom to use differant tests!
import PIL.Image
import cozmo.camera
from cozCube import coz
import cozmo
from cozmo import *
import asyncio
import apriltag
import PIL
import numpy
from cozmo_pose import cozPose
# test the functionality for Cozmo to see an April tag, and locate it
async def test_tag(connection):
    robot = await connection.wait_for_robot()
    #robot = cozmo.robot.Robot
    # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
    detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11"))

    while (True):
        # feed cozmo's camera data into april tag, then print data
        image = await robot.wait_for(cozmo.camera.EvtNewRawCameraImage, None)
        # Cozmo gives it's images as a PIL.Image.Image object, this is NOT compatable with apriltag functions
        # The Image needs to be converted into a numpy format
        GSImage = numpy.asfarray(image.image)
        output = detector.detect(GSImage)
        print(output)
    # The following happens as a result of just using numpy
    ''' /home/cozwizard/.pyenv/versions/3.5.10/envs/cozmoEnv/bin/python /home/cozwizard/Norm-Violation-Research/cozmo-code/coz_tag_driver.py
Task exception was never retrieved
future: <Task finished coro=<_connect_viewer.<locals>.view_connector() done, defined at /home/cozwizard/.pyenv/versions/3.5.10/envs/cozmoEnv/lib/python3.5/site-packages/cozmo/run.py:613> exception=AssertionError()>
Traceback (most recent call last):
  File "/home/cozwizard/.pyenv/versions/3.5.10/lib/python3.5/asyncio/tasks.py", line 240, in _step
    result = coro.send(None)
  File "/home/cozwizard/.pyenv/versions/3.5.10/envs/cozmoEnv/lib/python3.5/site-packages/cozmo/run.py", line 618, in view_connector
    await f(coz_conn)
  File "/home/cozwizard/Norm-Violation-Research/cozmo-code/coz_tag_driver.py", line 24, in test_tag
    output = detector.detect(GSImage)
  File "/home/cozwizard/.pyenv/versions/3.5.10/envs/cozmoEnv/lib/python3.5/site-packages/apriltag.py", line 352, in detect
    assert len(img.shape) == 2
AssertionError '''



cozmo.connect_with_tkviewer(test_tag)







  # code to append next
    #     # robot = cozmo.robot.Robot
    # robot = connection.wait_for_robot()
    # # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
    # detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11"))
    # #define cozmo's origin
    # currPose = cozmoPose(0, 0, 0, 0)
    # while (True):
    #     # feed cozmo's camera data into april tag, then print data
    #     image = robot.wait_for(robot, cozmo.camera.EvtNewRawCameraImage, None)
    #     output = detector.detect(image)
    #     print(output)