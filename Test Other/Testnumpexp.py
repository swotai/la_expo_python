# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 11:28:54 2014

@author: Dennis
"""

def docalc(exp):
	import numexpr as ne
	ne.evaluate(exp)

def docalc1(exp):
	eval(exp)


import numpy as np
import timeit

a=np.arange(1e8)
b=np.arange(1e8)
c=np.arange(4000*4000)




print "ne times:", timeit.Timer("docalc('a**2 + b**2 + 2*a*b')", "from __main__ import docalc").timeit(number=1)
print "reg times:", timeit.Timer("docalc1('a**2 + b**2 + 2*a*b')", "from __main__ import docalc1").timeit(number=1)
