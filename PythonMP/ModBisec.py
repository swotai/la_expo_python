# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 15:10:04 2014

@author: SWOT
"""

from ModIO import readcsv


def bisection(a, b, tol, objfn, valuefn, x, y, fl, limit):
    '''
    Bisection method to find root.
    
    Input
    -----
    a    : value
           min search value
    b    : value
           max search value
    tol  : value
           tolerance
    objfn : function
           objective function, that has a root at zero
    valuefn : function
           value function that the objective function evaluates
    x,y  : vector
           flow vectors (prev, predicted)
    etc  : values
           other parameters (Flow/Lane FL, speed limit LIMIT)
           
    '''
    def f(alpha):
        return objfn(x, y, alpha, valuefn, fl, limit)
        
    c = (a+b)/2.0
    print "c", c
    while (b-a)/2.0 > tol:
        if f(c) == 0:
            print 'fc=0'
            return c
        elif f(a)*f(c) < 0:
            b = c
        else :
            a = c
        c = (a+b)/2.0
         
    return c


def flowGradient(x, y, alpha, valuefn, fl, limit):
    '''
    Calculate the gradient value based on value function and various inputs
    (y1-x1)*t(x1+a*(y1-x1))
    
    Input
    -----
    x          : vector
                 Prev flow
    y          : vector
                 Expected flow
    alpha      : value
                 Alpha value for move.  See Sheffi p. 119.  Supplied from bisection
    valuefn    : function
                 Value function, e.g. Travel time/cost
    Output
    ------
    Grad(Z)    : Value
                 Value of the gradient, for use in bisection method
    '''
    grad = (y-x)*valuefn(x+alpha*(y-x), fl, limit)
    return grad.sum()
    
    
def flow2spd(x, FL, LIMIT):
    '''
    given x as per lane flow, FL as per lane flow cutoff (500), LIMIT as speed limit, returns the resulting speed.
    '''
    from math import exp
    if x > FL:
        return LIMIT * exp(-0.000191*(x-FL))
    else:
        return LIMIT

def traveltime(x, fl, limit):
    # segment length to be implimented
    from numpy import vectorize
    vflow2speed = vectorize(flow2spd, otypes=[np.float])

    return 1./vflow2speed(x, fl, limit)


    

if __name__ == '__main__':
    # Want Link objective, not just detectors.  
    # i.e. minimize the aggregate cost travelling on the highway network's links
    # Need : link distance, cost = (11.5375 * dist / inSpd + 0.469 * dist)

    inSpace = "/Users/SWOT/Desktop/TestBisection/"
    currentIter = 10
    ratio = 10
    FL = 500
    LIMIT = 65
    import numpy as np
    
    cff_op = inSpace+"detflow_adj"+str(currentIter)+".csv"
    fdtype = [('idstn','i8'),('flow','f8')]
    x1 = readcsv(cff_op, fdtype, incol = 2, sort = [0], header = None)
    
    cff_op = inSpace+"detflow_adj"+str(currentIter+1)+".csv"
    fdtype = [('idstn','i8'),('flow','f8')]
    y1 = readcsv(cff_op, fdtype, incol = 2, sort = [0], header = None)

    inAF = inSpace+"AF.csv"
    fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8')]
    af = readcsv(inAF, fdtype, incol = 4, sort=0, header = True)

    
    # Make sure the idstn align
    checksum = x1['idstn'] != y1['idstn']
    print 'number of detectors out of order:', checksum.sum()
    if checksum.sum() > 0:
        print 'OH SHIT'

    # Extract Flow
    x1 = x1['flow']
    y1 = y1['flow']
    
    # Convert to per lane flow for speed equation
    # cff_p['flow'] = ratio*0.12*(cff_p['flow'])/af['lane']
    x1 = ratio * .06 * x1 / af['lane']
    y1 = ratio * .06 * y1 / af['lane']
    
    alpha = bisection(0,1,0.0001, flowGradient, traveltime, x1, y1, FL, LIMIT)
    print "solved alpha:", alpha
    
    print "new flow"
    x2 = x1+alpha*(y1-x1)
    
    















