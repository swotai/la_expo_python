# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 22:23:00 2015

@author: SWOT

This code generates the OD distance matrix for a M x N grid.

Input:
------
m:       integer
n:       integer

Output:
-------
Array of (mxn) x (mxn)
"""

import numpy as np

m = 11
n = 11

# initiate array
OD = np.zeros((m*n,m*n))
OD = np.asmatrix(OD)

for rownum in range(0,m):
    for colnum in range(0,n):
        