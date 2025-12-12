# this driver will test the custom functionality made for the norm violation project
# edit the function being called at the bottom to use different tests!
import sys
print(sys.path)
import PIL.Image
import cozmo.camera
from cozCube import coz
import cozmo
from cozmo import *
import asyncio
import apriltag
import PIL
from matplotlib import pyplot as plt
from custom_pose_system.cozmoPose import cozPose
import time
import numpy
import math

# note: the following functions will be implemented into the coz class proper if the methods 

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
    # turn on interactive mode, so that the graph does not hold up the robot.
    plt.ion()    
    cozGrid = plt.subplot(1, 1, 1)
    goalPose = cozPose()
    robot = await connection.wait_for_robot()
    # robot = cozmo.robot.Robot
    # create an apriltag detector class, which takes the cozmo image and reconizes the included tag
    detector = apriltag.Detector(apriltag.DetectorOptions("tag36h11",border=1,quad_decimate=0, refine_edges=True))
    # focal_x, focal_y, centerx, centery
    cozmo.camera.CameraConfig.focal_length
    camera_data = {288.87, 288.36,155.11, 111.40}
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
          goalPose._x = Poses[0][1][3] 
          goalPose._y = Poses[0][2][3]
          # plan a straight path from cozmo to the goal pose
          # use simple trig, dist = sqrt(x^2+y^2) for dist, theta = tan^-1(delta x/delta y)
          dist = math.sqrt((goalPose._x * goalPose._x) + (goalPose._y * goalPose._y))
          ang = math.atan2(goalPose._x, goalPose._y)
          print("Path Vector Magnitude: ", dist, " Angle ", math.degrees(ang))
          cozDraw(cozGrid, goals = (goalPose, ), pathLine=(dist, ang))
         

          # graph state
        else:
            cozDraw(cozGrid)
# is specifically designed to draw points + path vector, pathLine should be a tuple with mag, dir
def cozDraw(cozGrid, cozmoPosition = cozPose(), goals = (), pathLine = None):
    #cozGrid = plt.subplot(1, 1, 1)
    cozGrid.clear()
    cozGrid.set_title("Cozmo path planning (in respect to cozmo's facing)")
    cozGrid.set_xlim(-500, 500)
    cozGrid.set_ylim(-200, 500)
    cozGrid.set_xlabel("Perpendicular Position(mm)")
    cozGrid.set_ylabel("Prallel Position(mm)")
    # Note: implement cozmo curr facing after integrating to class
    cozGrid.grid(True, color = "grey", linewidth = "1.4", linestyle = "-.")

    cozGrid.plot(cozmoPosition._x, cozmoPosition._y, 'red', marker = ".", label = "Cozmo")
    cozGrid.text((cozmoPosition._x * 1000) + 10, (cozmoPosition._y * 1000) + 10, "goal")

    cozGrid.grid(True, color = "grey", linewidth = "1.4", linestyle = "-.")
    # goals will be printed in order 
    goalCount = 1
    ''' Note, this shows potential paths to each goal, at the moment, it does not account for 
    not just cozmo's current target'''
    if (goals):
        for i in goals:
            print(i)
            cozGrid.plot(i._x * 1000, i._y * 1000, 'green', marker = ".", label = "goal")
            cozGrid.text((i._x * 1000) + 10, (i._y * 1000) + 10, ("goal" + str(goalCount)))
            goalCount += 1              

    if (pathLine):
        # draw pathline 
        # each value is converted to mm for easy viewing
        # use these variables so that the same calculation does not need top be done repreatedly
        destposx=cozmoPosition._x + pathLine[0] * math.sin(pathLine[1])
        destposy=cozmoPosition._y + pathLine[0] * math.cos(pathLine[1])
        cozGrid.plot([cozmoPosition._x * 1000,  destposx * 1000], 
                     [cozmoPosition._y * 1000,  destposy * 1000], 
                     'b-')
        # print magnitue in the middle of the line
        cozGrid.text((destposx-cozmoPosition._x)*1000/2 + 10, (destposy-cozmoPosition._y)*1000/2 + 10, str(pathLine[0] * 1000))
    plt.pause(0.1)
    plt.show()

cozmo.connect_with_tkviewer(demo_path_planning)   