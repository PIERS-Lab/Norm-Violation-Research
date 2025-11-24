import numpy
import matplotlib as mplot
from matplotlib import pyplot as plt
import numpy as np
import math
import time
#just a testing space to mess around with grids in matplotlib
def main(): 
    plt.ion()
    print(plt.isinteractive())
    #creates an array of sub plots, 
    (grid) = plt.subplot(1, 1, 1)
    # dummy data
    print(grid, type(grid))
    x = [0, 100]
    y = [0, 150]
    grid.set_xlim(-500, 500)
    grid.set_ylim (-200, 500)
    grid.plot(0, 0, 'ro')
    grid.arrow(0, 0, 0, 20, width = 5)
    grid.plot(100, 150, 'ro')
    
    # set graph color
    grid.plot(x, y, 'green', ls = '-.', marker = '')
    # to set title
    grid.set_title("Test code")

    # draws gridlines of grey color using given
    # linewidth and linestyle

    grid.grid(True, color = "grey", linewidth = "1.4", linestyle = "-.")
    print("showing!")
    plt.pause(0.1)
    plt.show()
    #plt.draw()
    time.sleep(5)
    while(True):
        grid.plot(-100, 100, 'ro')
        grid.clear()
        grid.plot(0, 0, 'ro')
        grid.plot(100, 150, 'ro')
        plt.pause(0.01)

    
    # set graph color
    grid.plot(x, y, 'green', ls = '-.', marker = '')
    
    # while(True):
    #     plt.draw()
    

main()
print("Done!")