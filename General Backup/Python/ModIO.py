# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 22:56:21 2014

@author: Dennis
"""

def readcsv(infile, indtype, incol, sort, header):
    '''
    Reads CSV using pandas that's super fast
    
    inputs
    ------
    indtype  : array/list
               e.g. fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
    incol    : number
               must be the same number of item as "indtype"
    sort     : list
               specify as [0] or [0,1] where number is column number
    Header   : Required
               either None or True
    '''
#    import sys
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
#    sys.stdout.flush()
    return outFTT