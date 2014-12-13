# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 21:29:21 2014

@author: Dennis
"""

import numpy as np
print "hello world"

inSpace = "C:/Users/Dennis/Desktop/DATA/"
inFlow = inSpace + "inFlow.csv"

fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
		
print "importing various matrices"
#Read TAZ-TAZ flow
ff = np.genfromtxt(inFlow, 
                   dtype = fdtype,
                   delimiter = ",",
                   skip_header = 0)