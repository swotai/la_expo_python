# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 21:39:11 2014

@author: Dennis

*** Line 11-17 (Performance Function Definition)
*** Line 88 (Simulate some link having fixed performance/our local road)
*** line 167-168 (Flow across highway network not stable)
"""
import numpy as np

def traveltime(x):
    tc = (x/1)**1
    return tc

def travelcost(flow, dist):
    tc = (flow/1)**1
    return tc

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


def MainProgram(load, flow):
    '''
    Program carry out the convex combination method to calculate flow in 5 steps:
    \n\t 1, calculate cost base on load input
    \n\t 2, calculate initial flow (x)
    \n\t 3, update cost,
    \n\t 4, calculate new flow (y)
    \n\t 5, find alpha that minimize the total travel cost
    
    Input
    -----
    load:   array
            vector of load
    Output
    ------
    x2:    array
           vector of resulting load (x+alfa*(y-x))
    a:     scalar
           alpha (for determining stopping)
    '''
#    Reset Cost
    g.es['cost'] = 0
    x = load.copy()
#    1, Calcualte initial cost
    g.es['cost'] = travelcost(load,g.es['dist'])
#    g.es[1]['cost']=10
#    print g.es['cost']
    t=g.es['cost']
    
#    4, Reallocate flow base on new cost
    g.es['load'] = 0    
    i=0
    while i < 4:
        j=0
        while j < 4:
            if flow[i,j] > 0:
                path = g.get_shortest_paths(i, j, weights='cost', output="epath")[0]
                for edge in path:
                    thisedge = g.es[edge]
                    thisedge['load']+=flow[i,j]
#                print "loaded", flow[i,j], "flows to edges", path
            j+=1
        i+=1


#    print "Flow2:", g.es['load']
    y = np.array(g.es['load'])


#    5, Seek alpha
    alfa = bisection(0,1,0.00001,objfn,x,y)
#    print "objfn at alpha = 0:", objfn(x,y,0), "; at alpha = 1:", objfn(x,y,1)
#    print "alpha:", alfa
#    print "new x:", x+alfa*(y-x)
#    print "new t:", traveltime(x+alfa*(y-x))
    
#    Return the new load for next iteration
    return x,y,t,x+alfa*(y-x), alfa




if __name__ == '__main__':
    import igraph
    from random import random
    g = igraph.Graph()
    g.add_vertices(4)
    g.vs['label']=["A","B","C","D"]
    g.add_edges([(0,2),(0,3),(2,3),(2,1),(3,1)])
    g.es['load'] = 0
    g.es['dist'] = 1
    g.es['cost'] = 0
    graph_style={}
    graph_style["vertex_size"] = 30
    graph_style["vertex_label"] = g.vs["label"]
    graph_style["vertex_label_size"] = 20
    graph_style["edge_label"] = [1,2,3,4,5] #g.es["load"]
    graph_style["edge_label_size"] = 20
#    Source and Destination Flows:
#    Recall four vertices ["A","B","C","D"]
#    Flow is represented by 4x4 matrix.  Row = O, col = D
#    e.g. Flow AB = 10 --> flow[0,1] = 10
    flow=np.zeros([4,4])
#    Flow AB = 10, flow CB = 5
    flow[0,1] = 10
    flow[2,1] = 5
    flow[3,1] = 7

    from prettytable import PrettyTable
    col = "Iter t1 t2 t3 t4 t5 y1 y2 y3 y4 y5 alpha x1 x2 x3 x4 x5 seed"
    col = col.split()
    table = PrettyTable(col)
    table.float_format = 4.2
    table.float_format['Iter'] = 2.0
    table.float_format['alpha'] = 1.4
    table.float_format['seed'] = 1.5
    
#    Initialize
    x1,y1,t,x,a = MainProgram(np.array(g.es['cost']), flow)
    table.add_row(np.concatenate(([0]*12, x,[0]), axis=1))
#    table.add_row(np.concatenate((t,y1,[a],x), axis=1))
    
    count = 0
    while a > 0.01 and count < 50:
        randomseed = 1+random()*.0
        x1,y1,t1,x,a = MainProgram(x, flow*(randomseed))
        table.add_row(np.concatenate(([count+1], t1, y1, [a], x,[randomseed]), axis=1))    
        count +=1

    print table
 


#    igraph.plot(g, layout="fr", **graph_style)



'''
#    Update the cost
#    for edge in g.es:
#        edge['cost'] = travelcost(edge['load'], edge['dist'])
#    graph_style["edge_label"] = g.es["cost"]
#    costg = igraph.plot(g, layout= "fr", **graph_style)
'''