from collections import deque
from produce_number import main as produce_number
import pandas as pd
import time

import os
path = "C:\\Users\\puria\\source\\repos\\puria-radmard\\CambridgeCarbonMap\\python"
os.chdir(path)
cwd = os.getcwd()
print(cwd)
fileName = "image.jpg"

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
#produce_number("image.jpg")

while True:
    print(monitor.get_last_gradient())
    prevTime = os.path.getatime(fileName)

    # Watch for new image.jpg
    while os.path.getatime(fileName) == prevTime:
        pass

    # Classifying image
    new_absl = produce_number("image.jpg")

    # store_ref new value
    print(new_absl)
    monitor.store_value(new_absl)

    # get_last_gradient
    monitor.get_last_gradient()

    # change csv
    graphing = pd.DataFrame(index=times, data= init_val)
    graphing.to_csv("graphing.csv")

    pass