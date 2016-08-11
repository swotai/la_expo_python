# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 20:41:04 2014

@author: Dennis
"""
import numpy as np
fl = 500
limit = 65


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
    Alpha where function is zero.
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

def flow2spd(x, FL, LIMIT):
    # given x as PER LANE flow, FL, LIMIT, returns the resulting speed.
    from math import exp
    if x > FL:
        return LIMIT * exp(-0.000191*(x-FL))
    else:
        return LIMIT

def travelcost(x, dist):
    # given x as vector per lane flow vector, dist as distance vector,
    # output travelcost vector
    vflow2spd = np.vectorize(flow2spd, otypes=[np.float])
    travelcost = (11.5375 *dist / vflow2spd(x, fl, limit)) + 0.469 * dist
#    travelcost = (1/vflow2spd(x, fl, limit))**4
    travelcost = (65**.2 - vflow2spd(x, fl, limit)**.2)
    return travelcost


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
        
    grad = (y-x)*travelcost(x+alpha*(y-x), vdist)
    return grad.sum()

def fg(a):
    return flowGradient(vx1, vy1, a, vd)


def inttotalcost(x,d):
    # Calculate the integral of travel cost. (the function behind gradient)
    from scipy.integrate import quad
    result = quad(travelcost,0,x,args=(d))
    return result[0]

def inttc(x,y,alpha,vdist):
    # vectorize the scalar inttotalcost() function
    import numpy as np
    vtc = np.vectorize(inttotalcost, otypes=[np.float])
    tc = vtc(x+alpha*(y-x), vdist)
    return tc.sum()

def tc(a):
    # convert function as a function of a
    return inttc(vx1, vy1, a, vd)

if __name__ == '__main__':
    import ModSpeedCalc
    from ModIO import readcsv
    import os
    maxa = 1.
    inSpace = "C:\Users\Dennis\Desktop\Results\DTA_Logit_test\Post/"
    # Change inSpace to where the current py file is located.
    # Should also have AF and xdetflow, ydetflow files.
#    inSpace = str(os.path.dirname(__file__)+'/')
    
    x1path = "xdetflow0.186218261719.csv"
    y1path = "ydetflow0.186218261719.csv"
    fdtype = [('idstn','i8'),('flow','f8')]
    x1 = readcsv(inSpace+x1path, fdtype, incol = 2, sort = [0], header = None)
    y1 = readcsv(inSpace+y1path, fdtype, incol = 2, sort = [0], header = None)
    
    inAF = inSpace+"AF.csv"
    fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8'),('dist','f8')]
    af = readcsv(inAF, fdtype, incol = 5, sort=0, header = True)

    ratio_x = ModSpeedCalc.flow2speed(inSpace, x1path, fl, limit, outCSV="", dta=True) #detspd-temp.csv
    ratio_y = ModSpeedCalc.flow2speed(inSpace, y1path, fl, limit, outCSV="", dta=True)
    
    
    vd  = af['dist']
    vx1 = ratio_x * .06 * x1['flow'] / af['lane']
    vy1 = ratio_y * .06 * y1['flow'] / af['lane']

    
    alfa = bisection(0, 1, 0.0001, vx1, vy1, vd)
    print alfa
    

    a = np.arange(0.,maxa,.005)
    vfg = np.vectorize(fg, otypes=[np.float])
    gradients = vfg(a)

#    Tried calculating the "travelcost" (i.e. the function to be minimized)
#    but crashes every time, perhaps the nested loop + integral kills the pc?
#    vtc = np.vectorize(tc, otypes=[np.float])
#    tcs = vtc(a)
    
    import matplotlib.pyplot as plt
    plt.plot(a, gradients)
    plt.hlines(0,0,maxa)
    plt.title('Gradient graph')
    plt.show()
    
