# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 21:59:01 2014

@author: Dennis
"""
from scipy.integrate import quad
def integrand(x, a, b):
    return a * x + b
a = 2
b = 1
I = quad(integrand, 0, 2, args=(a,b))
print I

'''
A Python function or method to integrate. 
If func takes many arguments, it is integrated 
along the axis corresponding to the first argument.
'''

from numbapro import vectorize

@vectorize(['float32, float32'], target='cpu')
def sum(a, b):
    return a + b


sum(1.,2.)