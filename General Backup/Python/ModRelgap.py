# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 13:20:21 2014

@author: Dennis
"""

def calc(inSpace, currentIter):
    import sys
    import numpy as np
    from operator import itemgetter
    
    try:
        datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
        
        print "Reading matrices for relative gap calculation"
        #Read TT cost
        inTT = inSpace+"CSV/TT.csv"
        ttc1 = np.genfromtxt(inTT,
        dtype = datatype,
        delimiter = ",", 
        skip_header = 0)
        ttc1 = np.asarray(sorted(ttc1, key=itemgetter(0,1)), dtype = datatype)
        
        inTT = inSpace+"CSV/TTflow"+str(currentIter)+".csv"
        ttf1 = np.genfromtxt(inTT,
        dtype = fdtype,
        delimiter = ",", 
        skip_header = 0)
        ttf1 = np.asarray(sorted(ttf1, key=itemgetter(0,1)), dtype = fdtype)
        
        
        inTT0 = inSpace+"CSV/TT0.csv"
        ttc0 = np.genfromtxt(inTT0, 
        dtype = datatype,
        delimiter = ",", 
        skip_header = 0)
        ttc0 = np.asarray(sorted(ttc0, key=itemgetter(0,1)), dtype = datatype)
        
        inTT0 = inSpace+"CSV/TTflow1.csv"
        ttf0 = np.genfromtxt(inTT,
        dtype = fdtype,
        delimiter = ",", 
        skip_header = 0)
        ttf0 = np.asarray(sorted(ttf0, key=itemgetter(0,1)), dtype = fdtype)
        
        tt0 = ttc0['cost']*ttf0['flow']
        tt1 = ttc1['cost']*ttf1['flow']
        
        relgap = (tt1.sum()-tt0.sum())/tt0.sum()
        
        return relgap

    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModRelgap"
        print "An error occurred in ModRelgap line %i" % tb.tb_lineno 
        print e.message




import numpy as np
from operator import itemgetter


if __name__ == '__main__':
    inSpace = 'C:/Users/Dennis/Desktop/DATA/'
    datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
    fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
    currentIter = 20
    
    print "Reading matrices for relative gap calculation"
    #Read TT cost
    inTT = inSpace+"CSV/TT.csv"
    ttc1 = np.genfromtxt(inTT,
    dtype = datatype,
    delimiter = ",", 
    skip_header = 0)
    ttc1 = np.asarray(sorted(ttc1, key=itemgetter(0,1)), dtype = datatype)
    
    inTT = inSpace+"CSV/TTflow"+str(currentIter)+".csv"
    ttf1 = np.genfromtxt(inTT,
    dtype = fdtype,
    delimiter = ",", 
    skip_header = 0)
    ttf1 = np.asarray(sorted(ttf1, key=itemgetter(0,1)), dtype = fdtype)
    
    
    inTT0 = inSpace+"CSV/TT0.csv"
    ttc0 = np.genfromtxt(inTT0, 
    dtype = datatype,
    delimiter = ",", 
    skip_header = 0)
    ttc0 = np.asarray(sorted(ttc0, key=itemgetter(0,1)), dtype = datatype)
    
    inTT0 = inSpace+"CSV/TTflow1.csv"
    ttf0 = np.genfromtxt(inTT,
    dtype = fdtype,
    delimiter = ",", 
    skip_header = 0)
    ttf0 = np.asarray(sorted(ttf0, key=itemgetter(0,1)), dtype = fdtype)
    
    tt0 = ttc0['cost']*ttf0['flow']
    tt1 = ttc1['cost']*ttf1['flow']
    
    relgap = (tt1.sum()-tt0.sum())/tt0.sum()

