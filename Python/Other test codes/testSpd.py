# TEST CODE FOR SPEEDCALC

import os, sys, traceback
import numpy as np
from math import exp
from operator import itemgetter
#Set parameters
#  -weight is how much weight to put into new speed
#  -FL should be 500, however because small TAZ number
#   in test sample, threshold changed to 1 to test equation.
LIMIT = 65
weight = 0.7
FL = 500
FL = 1

#Function should be receiving the flow vector from input.
#For dev purpose, import from CSV

currentIter = 1
inSpace = "C:/Users/Dennis/Desktop/DATA/"

#READ SPEED FROM DETECTOR, SHOULDN'T NEED 
#Current flow
inFlow = inSpace+"CSV/detflow"+str(currentIter)+".csv"
fdtype = [('idstn','i8'),('flow','f8')]
cff = np.genfromtxt(inFlow,
					dtype = fdtype,
					delimiter = ",",
					skip_header = 0)
#cff = inFlow
fdtype = [('idstn','i8'),('flow','f8')]
cff = np.asarray(sorted(cff, key=itemgetter(0)),
				  dtype = fdtype)

#Previous speed
inPspd = inSpace+"detspd"+str(currentIter-1)+".csv"
fdtype = [('idstn','i8'),('speed','f8')]
ps = np.genfromtxt(inPspd,
					dtype = fdtype,
					delimiter = ",",
					skip_header = 0)
ps = np.asarray(sorted(ps, key=itemgetter(0)),
				dtype = fdtype)

#Demand side speed
inDspd = inSpace+"DDspd.csv"
ds = np.genfromtxt(inDspd,
					dtype = fdtype,
					delimiter = ",",
					skip_header = 0)
ds = np.asarray(sorted(ds, key=itemgetter(0)),
				dtype = fdtype)


#Convert from GF to the peak time flow F (F = GF x 2 x 6%)
cff['flow'] = cff['flow']*0.12

#Update supply side speed using supply side equation
for x in np.nditer(cff['flow'], op_flags = ['readwrite']):
	if x > FL:
		x[...] = LIMIT * exp(-0.000191*(x-FL))
	else:
		x[...] = LIMIT

cff.dtype = ([('idstn', '<i8'), ('speed', '<f8')])
#Set new supply side speed as linear combination of prev and current
#supply side speed.  Weight wt is set in the beginning.
cff['speed'] = weight*cff['speed'] + (1-weight)*ps['speed']


outCSV = inSpace+'detspd'+str(currentIter)+'.csv'
print "speed updated.  Writing to", outCSV
with open(outCSV, 'wb') as f:
	f.write(b'id_stn,speed\n')
	np.savetxt(f, cff, delimiter=',', fmt='%7.0f, %7.10f')

#Loop End Condition
#  1, SSD < threshold
#  2, Number of iteration reach X
#  3, Supply side Speed = Demand side
#Function returns the ssd(1) and ssd for SY-DD(3)

ssd = cff['speed'] - ps['speed']
ssd = np.multiply(ssd,ssd)
ssd = ssd.sum()

ssdSD = cff['speed'] - ds['speed']
ssdSD = np.multiply(ssdSD,ssdSD)
ssdSD = ssdSD.sum()

print "SSD", ssd
print "SSDSD", ssdSD