# -*- coding: utf-8 -*-
"""
Created on Thu Jan 08 11:06:14 2015

@author: Dennis
"""
from ModIO import readcsv
import numpy as np
from math import sqrt

inSpace = "C:/Users/Dennis/Desktop/Pre/"
currentIter = 1

# CHECK: 763330 717035
detdesired = '717035'

inTT = inSpace+"CSV/TT.csv"
inTD = inSpace+"CSV/TD.csv"
inDT = inSpace+"CSV/DT.csv"
outCSV = inSpace+'ODthrough'+detdesired+'.csv'
inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"

#Test: 50 TAZs, 1813 DET
#Full: 2241 TAZs, 1813 DETs
nTAZ = 50
nDET = 1813

#fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
#fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]

print "importing various matrices"
#Read TAZ-TAZ flow
ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)

#Read TD cost
td = readcsv(inTD, datatype, incol = 4, sort = [1,0], header = None)

#Read DT cost
dt = readcsv(inDT, datatype, incol = 4, sort = [0,1], header = None)

#Read TT cost
tt = readcsv(inTT, datatype, incol = 4, sort = [0,1], header = None)

nTAZ = int(sqrt(tt.size))
if nTAZ != sqrt(tt.size):
    print "ERROR: TAZ SIZE NOT SQUARE!"
if dt.size != td.size:
    print "ERROR: TD and DT SIZE NOT MATCH!"
nDET = dt.size/nTAZ
print "import completed"

print "reshaping..."
ctd = np.reshape(td['cost'],(nDET, nTAZ))
cdt = np.reshape(dt['cost'],(nDET, nTAZ))
ndt = np.reshape(dt['name'],(nDET, nTAZ))
ctt = np.reshape(tt['cost'],(nTAZ, nTAZ))
ftt = np.reshape(ff['postflow'],(nTAZ, nTAZ))
namett = np.reshape(tt['name'],(nTAZ, nTAZ))
#ftt = ftt + ftt.T

# FLOW MATRIX
print "begin flow allocation"
x3 = np.matrix(ctt)
i = 0
count = 0
detFlow = {999999: 0}
while i<nDET :
    #Extract current detector id_stn
    det = ndt[i,1][0:6]
    if det == detdesired:
        # Extract cost vectors
        x1 = np.matrix(ctd[i])
        x1 = x1.T
        x2 = np.matrix(cdt[i])
    
        tddt=x1+x2
        #Imprecise/Buffer matching, not needed hopefully
        #match = x3 - tddt
        #t=abs(match)<0.5
    
        #Precise matching
        isflow = x3 == tddt
        break
 
    #Record flow in dictionary
#    detFlow[det] = totalflow
    i+=1

del detFlow[999999]

output = namett[isflow]
print "Saved OD pairs for detector", detdesired
np.savetxt(outCSV, output, delimiter=',', fmt='%s')

'''
WANT isflow matrix for a particular detector.
'''