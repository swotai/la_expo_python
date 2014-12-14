# -*- coding: utf-8 -*-
"""
Created on Sun Dec 14 09:28:42 2014

@author: Dennis
"""
import numpy as np
movingavg = np.array([100])
i = 0
while i < 50:
    movingavg = np.append(movingavg, 10*(i%2))
    print "Average is", movingavg[-10:].mean()
    i+=1