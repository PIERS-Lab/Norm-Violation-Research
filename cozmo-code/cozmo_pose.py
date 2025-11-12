import cozmo
'''A class to just keep track of cozmo's pose in a custom frame Z, while not needed, is included to interface better with the cozmo API
measurements are specifically milimeters for position and degrees for rotation.'''
class cozPose:
    def __init__ (self, x=0, y=0, z=0, rotation=0):
        self._x = x
        self._y = y
        self._z = z
        self._rot = rotation

    def __sub__ (self, op2):
        return cozPose(self._x - op2._x, self._y - op2._y, self._z - op2._z)
    
    def __add__(self, op2):
        return cozPose(self._x + op2._x, self._y + op2._y, self._z + op2._z)
    


# will represent cozmo's 2D pose world, just have to figure it out
# class cozGrid:
