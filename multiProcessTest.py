
import threading
import time
import concurrent.futures.thread
import multiprocessing
from multiprocessing import Process, Pipe
'''This tests continuous running until a signal shows up using multi-processing'''  
def count(p):
    start = 0
    Pipe()[0].recv
    stop = p.recv()
    print("Child started")
    while(not stop):
        print("Child: " + str(start))
        start += 1
        time.sleep(1)
        if (p.poll()):
            stop = p.recv()

    print ("done!")
    return

print("hello")
stop = False
pipe=Pipe()
counter = Process(target = count, args = (pipe[1], ))
sigStop = pipe[0]
# send false to start loop
sigStop.send(False)
counter.start()

print("Main: thread started")
time.sleep(10)
print("Main: stopping")
sigStop.send(True)
counter.join()
print("Exiting")

