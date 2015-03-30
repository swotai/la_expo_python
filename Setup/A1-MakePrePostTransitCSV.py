# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 14:30:02 2015

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
    import sys
    import pandas as pd
    import numpy as np
    if header != None:
        header = 0
    outFTT = pd.read_csv(infile, header = header)
    outFTT1 = outFTT.copy()
    outFTT.columns = [i for i,col in enumerate(outFTT.columns)]
    outFTT = outFTT.sort(columns=sort)
    outFTT = np.asarray(outFTT.iloc[:,0:incol].values)
    outFTT = np.core.records.fromarrays(outFTT.transpose(), dtype = indtype)
    outFTT = np.asarray(outFTT)
    sys.stdout.flush()
    return outFTT, outFTT1
    

import pandas as pd
import numpy as np
inSpace = "C:/Users/Dennis/Desktop/"

accutype = [('v1','i8'),('v2','i8'),('name','S20'),('cost','f8'),('v5','f8'),('v6','f8'),('v7','f8'),('v8','f8')]
preTT, preTT1 = readcsv(inSpace+"TransitPre/TransitPre_Accu1.csv", accutype, incol=8, sort=[0], header=None)
