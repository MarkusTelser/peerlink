from threading import Lock, Thread
from random import random
from time import sleep
from queue import Queue
    
class Test:
    def __init__(self) -> None:
        self.i = 0
        self.lock = Lock()
    
    def test(self, sleep_time, i, queue, start_queue):
        print(i, "started sleeping")
        sleep(sleep_time)
        #self.lock.acquire()
        self.i = sleep_time + 1
        #self.lock.release()
        start_queue.get()
        queue.put(self)
        print(i, "finished sleeping")

class Testing:
    def __init__(self) -> None:
        self.max_trackers = Queue(maxsize=5) # start only amount of at the same time
        self.finished_tracker = Queue()
        self.count = 10
        self.tests = list()
        for i in range(self.count):
            self.tests.append(Test())

    def announce_tracker(self):
        # create and start threads
        for i, t in enumerate(self.tests):
            sleep_time = i
            t1 = Thread(target=t.test, args=(sleep_time, i, self.finished_tracker, self.max_trackers))
            self.max_trackers.put(t1)
            t1.start()

    def connect_peer(self):
        # check until finished, then start peer
        finished = 0
        while finished != self.count:
            item = self.finished_tracker.get()
            finished += 1
            print(item, "finished")
            
        for t in self.tests:
            print(t.i)

    
tt = Testing()
t1 = Thread(target=tt.announce_tracker)
t1.start()
t2 = Thread(target=tt.connect_peer)
t2.start()


t1.join()
t2.join()
for t in tt.tests:
    print(t.i)

"""
first announce -> return Tracker() Object back

list = list(Tracker())

announce_over_tracker = 
"""