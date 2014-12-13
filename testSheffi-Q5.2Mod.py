# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 23:14:47 2014

@author: Dennis
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 21:39:11 2014

@author: Dennis
"""
import numpy as np

def traveltime(x):
    s = 65.*np.exp(-.000191*x)
    tc = 12/s + 0.5
    return tc

def speed(x):
    s = 65.*np.exp(-.000191*x)
    tc = 12/s + 0.5
    return s

def objfn(x,y,alpha):
    grad = (y-x)*traveltime(x+alpha*(y-x))
    return grad.sum()

def bisection(a, b, tol, objfn, x, y):
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
        return objfn(x, y, alpha)
        
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
    
if __name__ == '__main__':
#    import igraph
#    g = igraph.Graph()
#    g.add_vertices(4)
#    g.vs['label']=["A","B","C","D"]
#    g.add_edges([(0,2),(0,3),(2,3),(2,1),(3,1)])
#    layout = g.layout("kk")
#    igraph.plot(g, layout=layout)
    x = np.array([0,0,0,0,0])
    
    x = np.array([1000,2000,0,0,2000])
    y = np.array([3000,0,0,2000,0])
    x = np.array([1738.082886, 1261.917114, 0, 738.0828857, 1261.917114])
    y = np.array([1000,2000,0,0,2000])
   
    alfa = bisection(0,1,0.00001,objfn,x,y)
    
    print "alpha:", alfa
    print "new x:", x+alfa*(y-x)
    
    print "new t:", traveltime(x+alfa*(y-x))
    