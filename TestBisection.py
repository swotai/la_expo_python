# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 20:01:18 2014

@author: Dennis
"""


import numpy as np
fl = 500
limit = 65

# XXX Begin sub function block
def readcsv(infile, indtype, incol, sort, header):
    '''
    Reads CSV using pandas that's super fast
    
    inputs
    ------
    incol    : number
               must be the same number of item as "indtype"
    sort     : list
               specify as [0] or [0,1] where number is column number
    Header   : Required
               either None or True
    '''
    
    import pandas as pd
    import numpy as np
    if header != None:
        header = 0
    outFTT = pd.read_csv(infile, header = header)
    outFTT.columns = [i for i,col in enumerate(outFTT.columns)]
    outFTT = outFTT.sort(columns=sort)
    outFTT = np.asarray(outFTT.iloc[:,0:incol].values)
    outFTT = np.core.records.fromarrays(outFTT.transpose(), dtype = indtype)
    outFTT = np.asarray(outFTT)
    return outFTT
    
def bisection(a, b, tol, x, y, vd):
    '''
    Bisection method to find root.
    hardcoded in objective function as flowGradient,
    and value function as travelcost.
    
    Input
    -----
    a    : value
           min search value
    b    : value
           max search value
    tol  : value
           tolerance
    x,y  : vector
           flow vectors (prev, predicted)
    vd   : vector
           distance vector from AF
    
    Return
    ------
    Alpha of root.               
    '''
    def f(alpha):
        return flowGradient(x, y, alpha, vd)
        
    c = (a+b)/2.0
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
def flowGradient(x, y, alpha, vdist):
    '''
    Calculate the gradient value based on value function and various inputs
    (y1-x1)*t(x1+a*(y1-x1))
    
    Contains a short, no-output version of flow2spd, and travelcost calculation
    
    Input
    -----
    x          : vector
                 Prev flow
    y          : vector
                 Expected flow
    alpha      : value
                 Alpha value for move.  See Sheffi p. 119.  Supplied from bisection
    vdist      : vector
                 vector of distance from AF reading

    Output
    ------
    Grad(Z)    : Value
                 Value of the gradient, for use in bisection method
    '''
    def flow2spd(x, FL, LIMIT):
        # given x as PER LANE flow, FL, LIMIT, returns the resulting speed.
        from math import exp
        if x > FL:
            return LIMIT * exp(-0.000191*(x-FL))
        else:
            return LIMIT

    def travelcost(x, dist):
        # segment length to be implimented
        vflow2spd = np.vectorize(flow2spd, otypes=[np.float])
#        travelcost = (11.5375 *dist / vflow2spd(x, fl, limit)) + 0.469 * dist
        travelcost = (11.5375 * dist / vflow2spd(x, fl, limit))**4
        travelcost = 65-vflow2spd(x, fl, limit)
        travelcost = 65**.2 - vflow2spd(x, fl, limit)**.2
        return travelcost
        
    grad = (y-x)*travelcost(x+alpha*(y-x), vdist)
    return grad.sum()
# XXX end sub function block

if __name__ == '__main__':
    inSpace = "E:/TestingLab/"
    x1path = "CSV/xdetflow.csv"
    y1path = "CSV/ydetflow.csv"
    
    ratio_x = 10.0550935465
    ratio_y = 10.7308926556
    # Find Alpha
    fdtype = [('idstn','i8'),('flow','f8')]
    x1 = readcsv(inSpace+x1path, fdtype, incol = 2, sort = [0], header = None)
    y1 = readcsv(inSpace+y1path, fdtype, incol = 2, sort = [0], header = None)
    
    inAF = inSpace+"AF.csv"
    fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8'),('dist','f8')]
    af = readcsv(inAF, fdtype, incol = 5, sort=0, header = True)
 
    checksum = x1['idstn'] != y1['idstn']
    print 'number of detectors out of order:', checksum.sum()
    if checksum.sum() > 0:
        print 'OH NOES!!, XY not match'
    checksum = x1['idstn'] != af['idstn']
    print 'number of detectors out of order:', checksum.sum()
    if checksum.sum() > 0:
        print 'OH NOES!!, AF not match'
    vx1 = ratio_x * .06 * x1['flow'] / af['lane']
    vy1 = ratio_y * .06 * y1['flow'] / af['lane']
    vd  = af['dist']
    alfa = bisection(0, 1, 0.0001, vx1, vy1, vd)
    
    print "Gradient at 0:", flowGradient(vx1, vy1, 0, vd)
    print "Gradient at 1:", flowGradient(vx1, vy1, 1, vd)
    print "alpha:", alfa
    
    
    
    
    
    
    
    
    
    