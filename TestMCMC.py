# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 11:28:54 2014

@author: Dennis
"""

if __name__ == '__main__':
	try:
		import numpy
		
		def filter2d(image, filt):
		    M, N = image.shape
		    Mf, Nf = filt.shape
		    Mf2 = Mf // 2
		    Nf2 = Nf // 2
		    result = numpy.zeros_like(image)
		    for i in range(Mf2, M - Mf2):
		        for j in range(Nf2, N - Nf2):
		            num = 0.0
		            for ii in range(Mf):
		                for jj in range(Nf):
		                    num += (filt[Mf-1-ii, Nf-1-jj] * image[i-Mf2+ii, j-Nf2+jj])
		            result[i, j] = num
		    return result
		
		# This kind of quadruply-nested for-loop is going to be quite slow.
		# Using Numba we can compile this code to LLVM which then gets
		# compiled to machine code:
		
		from numba import double, jit
		
		fastfilter_2d = jit(double[:,:](double[:,:], double[:,:]))(filter2d)
		
		# Now fastfilter_2d runs at speeds as if you had first translated
		# it to C, compiled the code and wrapped it with Python
		image = numpy.random.random((100, 100))
		filt = numpy.random.random((10, 10))
		print image
		print filt
		print "Slow filter"
		res = filter2d(image, filt)
		print res
		print "Fast filter"
		res1 = fastfilter_2d(image, filt)
		print res
		
	except Exception as e:
		import sys		
		tb = sys.exc_info()[2]
		print "An error occurred in line %i" % tb.tb_lineno 
		print e.message
