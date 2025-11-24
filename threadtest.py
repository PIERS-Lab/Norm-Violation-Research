import threading
import time
import concurrent.futures.thread
'''figure out concurrency'''

class flag:
    def __init__ (self, start):
        self.status = start
    def set (self):
        self.status = True
    def unset (self):
        self.status = False

cool = threading.Event()
cool.clear()

def main(stop):
    print("Main: thread started")
    time.sleep(5)
    print("Main: stopping")
    stop.set()

    
def count(stop):
    start = 0
    while(not stop.isSet()):
        print("Thread: " + str(start))
        time.sleep(1)
        start += 1
    print ("done!")
    return

print("hello")
behavior = concurrent.futures.ThreadPoolExecutor(4)
stop = threading.Event()

behavior.submit(count, stop)
behavior.submit(threading.main_thread())
print("Main: thread started")
time.sleep(5)
print("Main: stopping")
stop.set()
time.sleep(10)
print(stop)
stop.set()

