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
from matplotlib import pyplot as plt
from cozmo_pose import cozPose
import time
import sys
import numpy
from custom_pose_system.cozmoPose import cozPose
# test the functionality for Cozmo to see an April tag, and locate it
async def test_tag(connection):
    robot = await connection.wait_for_robot()
    # robot = cozmo.robot.Robot
    # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
    detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True))

    while (True):
        
        # feed cozmo's camera data into april tag, then print data
        image = await robot.wait_for(cozmo.camera.EvtNewRawCameraImage, None)
        # Cozmo gives it's images as a PIL.Image.Image object, It needs to be transformed into a GS numpy array

        # convert the raw image into greyscale
        GSImage = image.image.convert("L")
        upscaled = GSImage.resize((640, 480), resample=PIL.Image.NEAREST)

        #convert greyscale Image into a numpy array
        GSImage = numpy.array(GSImage, dtype=numpy.uint8)
        #used the transformed image to detect april tags

        # note if more than one april tag is present, then an array is returned
        detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))
        print(type(detections), detections)
        #print(sys.getsizeof(len(detections)))
        
async def test_tag_pose(connection):
    robot = await connection.wait_for_robot()
    # robot = cozmo.robot.Robot
    # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
    detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True))
    # focal_x, focal_y, centerx, centery
    cozmo.camera.CameraConfig.focal_length
    camera_data = {288.87, 288.36 ,155.11, 111.40}
    while (True):
        
        # feed cozmo's camera data into april tag, then print data
        image = await robot.wait_for(cozmo.camera.EvtNewRawCameraImage, None)
        # Cozmo gives it's images as a PIL.Image.Image object, It needs to be transformed into a GS numpy array

        # convert the raw image into greyscale
        GSImage = image.image.convert("L")
        upscaled = GSImage.resize((640, 480), resample=PIL.Image.NEAREST)

        #convert greyscale Image into a numpy array
        GSImage = numpy.array(GSImage, dtype=numpy.uint8)
        #used the transformed image to detect april tags

        # note if more than one april tag is present, then an array is returned
        detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))
        #rint(type(detections), detections)
        #tag size in meters
        #figure out camera params next\
        #camera params are read in a list (fx, fy, cx cy)
        #The pose situation should loop through detections and store poses in a
        #list or array
        #print(type(detections), detections)
        if(detections):
          Poses = detector.detection_pose(detections[0], camera_data, 0.05, +1)
          
          #Poses use a homegeneous transformation matrix, so
          '''
          [ U_X_x, U_Y_x, U_Z_x, p_x ] 
          [U_X_y, U_Y_y, U_Z_y, p_y  ]
          [U_X_z, U_Y_z, U_Z_z, p_z  ]
          [0,     0,     0,     1    ]
          '''
          #the top left 3x3 represents rotation as 3 unit vectors
          #the final column represents positional data
          #bottom row is there just to make math easier
          print(Poses[0])
          # Note: these arrays are column major
          print("Pose:\n", "x: ", Poses[0][0][3], "\n", "y: ", Poses[0][1][3], "\n" "z: ", Poses[0][2][3], "\n")

async def test_pose_usage(connection):
    # place the tag in froont of cozmo's view, given the collected pose data, cozmo will ddrive up to the tags z position
    robot = await connection.wait_for_robot()
    # robot = cozmo.robot.Robot
    # create an apriltag detector class, which takes the cozmo image and recognizes the included tag
    detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True))
    # focal_x, focal_y, centerx, centery
    camera_data = {288.87, 288.36 ,155.11, 111.40}
    while (True):
        
        # feed cozmo's camera data into april tag, then print data
        image = await robot.wait_for(cozmo.camera.EvtNewRawCameraImage, None)
        # Cozmo gives it's images as a PIL.Image.Image object, It needs to be transformed into a GS numpy array

        # convert the raw image into greyscale
        GSImage = image.image.convert("L")
        upscaled = GSImage.resize((640, 480), resample=PIL.Image.NEAREST)

        #convert greyscale Image into a numpy array
        GSImage = numpy.array(GSImage, dtype=numpy.uint8)
        #used the transformed image to detect april tags

        # note if more than one april tag is present, then an array is returned
        detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))
        #rint(type(detections), detections)
        #tag size in meters
        #figure out camera params next\
        #camera params are read in a list (fx, fy, cx cy)
        #The pose situation should loop through detections and store poses in a
        #list or array
        #print(type(detections), detections)
        if(detections):
          Poses = detector.detection_pose(detections[0], camera_data, 0.05, +1)
          
          #Poses use a homegeneous transformation matrix, so
          '''
          [ U_X_x, U_Y_x, U_Z_x, p_x ] 
          [U_X_y, U_Y_y, U_Z_y, p_y  ]
          [U_X_z, U_Y_z, U_Z_z, p_z  ]
          [0,     0,     0,     1    ]
          '''
          #the top left 3x3 represents rotation as 3 unit vectors
          #the final column represents positional data
          #bottom row is there just to make math easier
          print(Poses[0])
          # Note: these arrays are column major
          print("Pose:\n", "x: ", Poses[0][0][3], "\n", "y: ", Poses[0][1][3], "\n" "z: ", Poses[0][2][3], "\n")
          #cozmo.robot.Robot.drive_wheel_motors(self, 100, 100, 0, 0)
          print("The tag is ", Poses[0][2][3] * 1000, "mm ahead of me!")
          #cozmo.robot.Robot.drive_wheel_motors(self, 100, 100, 0, 0)
          await robot.set_lift_height(1.0).wait_for_completed()
          robot.drive_wheel_motors(100, 100, 0, 0)
          # there appears to be a consitant error in the pose accuracy, but this just so happens to work out as a natural goal offset, so yay?
          # add 37.5 to the distance to make the refremce point from cozmo's center, thus staying consitant for the differential drive math.
          time.sleep(((Poses[0][2][3] * 1000) + 37.5)/100)
          robot.stop_all_motors()
          await robot.set_lift_height(0).wait_for_completed()
          time.sleep(1)
          return

async def demo_path_planning(connection):
    
    cozGrid = plt.subplot(1, 1, 1)
    goalPose = cozPose()
    robot = await connection.wait_for_robot()
    # robot = cozmo.robot.Robot
    # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
    detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True))
    # focal_x, focal_y, centerx, centery
    cozmo.camera.CameraConfig.focal_length
    camera_data = {288.87, 288.36 ,155.11, 111.40}
    while (True):
        
        # feed cozmo's camera data into april tag, then print data
        image = await robot.wait_for(cozmo.camera.EvtNewRawCameraImage, None)
        # Cozmo gives it's images as a PIL.Image.Image object, It needs to be transformed into a GS numpy array

        # convert the raw image into greyscale
        GSImage = image.image.convert("L")
        upscaled = GSImage.resize((640, 480), resample=PIL.Image.NEAREST)

        #convert greyscale Image into a numpy array
        GSImage = numpy.array(GSImage, dtype=numpy.uint8)
        #used the transformed image to detect april tags

        # note if more than one april tag is present, then an array is returned
        detections = detector.detect(numpy.array(upscaled, dtype=numpy.uint8))
        if(detections):
          Poses = detector.detection_pose(detections[0], camera_data, 0.05, +1)
          
          #Poses use a homegeneous transformation matrix, so
          '''
          [ U_X_x, U_Y_x, U_Z_x, p_x ] 
          [U_X_y, U_Y_y, U_Z_y, p_y  ]
          [U_X_z, U_Y_z, U_Z_z, p_z  ]
          [0,     0,     0,     1    ]
          '''
          #the top left 3x3 represents rotation as 3 unit vectors
          #the final column represents positional data
          #bottom row is there just to make math easier
          print(Poses[0])
          # Note: these arrays are column major
          print("Final pose:\n", "x: ", Poses[0][0][3], "\n", "y: ", Poses[0][1][3], "\n" "z: ", Poses[0][2][3], "\n")
          # update pose, use pose to print in graph
          # work on path planning 
          # graph state

cozmo.connect_with_tkviewer(test_pose_usage)