from collections import deque
from produce_number import main as produce_number
import pandas as pd
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
path = "C:\\Users\\puria\\source\\repos\\puria-radmard\\CambridgeCarbonMap"
os.chdir(path)
cwd = os.getcwd()
print(cwd)

maxtime = 100

times = [0-n for n in range(maxtime)]
init_val = [0 for t in times]
graphing = pd.DataFrame(index=times, data= init_val)
graphing.to_csv("graphing.csv")

class Monitor(object):
    def __init__(self, dt):
        self.dt          = dt
        self.memory      = deque(maxlen = maxtime)
        self.memory_grad = deque(maxlen = maxtime)

    def push(self, result):
        self.memory.append(result)
        
    def push_grad(self, gradient):
        self.memory_grad.append(gradient)
    
    def get_gradient(self):
        if len(self.memory) < 2:
            return 0
        if len(self.memory) == 2:
            return (self.memory[-1] - self.memory[-2])/self.dt
        
        return (self.memory[-1] - self.memory[-3])/(2 * self.dt)
    
    def store_value(self, result):
        self.push(result)
        self.push_grad(self.get_gradient())
        
    def get_last_gradient(self):
        return self.memory_grad[-1]


monitor = Monitor(5)

for i in range(maxtime): monitor.memory_grad.append(0)

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')

while True:
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/data/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    pass