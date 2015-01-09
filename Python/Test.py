# -*- coding: utf-8 -*-
"""
Created on Thu Jan 08 17:43:48 2015

@author: Dennis
"""
currentIter = 1
inSpace = "C:/Users/Dennis/Desktop/Pre/"
inTTp = inSpace+"TTpubPre.csv" 
inSpeed = "detspd" + str(currentIter - 1) + ".csv"
base = "DriveOnly_LA.gdb"
temp = "LA-scratch.gdb"
base = inSpace+base
temp = inSpace+temp


'''
Output both TT flow for driving and transit
'''
from math import exp, sqrt, pi
import numpy as np
from ModIO import readcsv


#print "Code starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
#Parameters
c1 = 5.45
c2 = -5.05
G = exp(-3.289)
beta1 = 0.535
beta2 = 0.589
tau = -2.077


#import various matrices
fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
petype = [('oid','i8'),('emp','f8'),('pop','f8')]
areatype = [('oid','i8'),('area','f8')]

#import from inFlow
#This is used as OUTPUT TEMPLATE
outFTT = inSpace + "inFlow.csv"
outFTT = readcsv(outFTT, fdtype, incol = 3, sort = [0,1], header = None)

#TT Cost (pub)
#Post/PRE as SEPARATE CSV FILE
print "importing TTcost for Transit"
ttp = readcsv(inTTp, tttype, incol = 4, sort = [0,1], header = True)

print "importing TTcost for driving (current)"
#TT Cost (driving, CURRENT)
inTTd = inSpace+"CSV/TT.csv"
#inTTd = inSpace+"TTdrv.csv"
ttd = readcsv(inTTd, tttype, incol = 4, sort = [0,1], header = None)

#print "check sorting"
#make sure both TT costs are sorted correctly:
#if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
#if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
#    raise Exception('Driving and Transit TT not match!')
#print "sorting is fine"

print "importing census"
#Population & employment
inPE = inSpace+"census.csv"        
pe = readcsv(inPE, petype, incol = 3, sort = [0], header = True)

print "importing TAZ area"
inArea = inSpace+"TAZarea.csv"        
area = readcsv(inArea, areatype, incol=2, sort=[0], header = True)
area = area['area']

print "testing squareness"
#Test square of TTcost and TTcostpub, test same size of pop/emp
ttsize = sqrt(np.size(ttd))
if ttsize != int(ttsize):
    raise Exception('Driving TT cost not square!!!')
ttsize = sqrt(np.size(ttp))
if ttsize != int(ttsize):
    raise Exception('Transit TT cost not square!!!')
pesize = np.size(pe)
if pesize != int(ttsize):
    raise Exception('Population/Employment vector not same size as TAZ!!!')
nTAZ = ttsize
print "square is fine, import completed"


print "creating internal cost"
#Internal cost: cost of ppl going to work within own TAZ
#        replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
#                    +3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
#                    replace with 1 if lower than 1        
dist = (2./3) * (area/pi)**0.5
intci = 11.5375 * dist / 15 + 0.469 * dist
intcp = 11.5375 * dist / 3

#make diagonal (Origin = destination)
I = np.identity(nTAZ)
intci = intci*I
intcp = intcp*I

print "reshaping..."
ttcosti = np.reshape(ttd['cost'],(nTAZ, nTAZ)) + intci
ttcostp = np.reshape(ttp['cost'],(nTAZ, nTAZ)) + intcp


print "calculate Sij"
#New transit share
deltaC = ttcostp/ttcosti
exx = np.exp(c1+c2*deltaC)
sij = exx/(1+exx)
outSij = sij.reshape(nTAZ**2,1)
outCSVsij = inSpace+'CSV/Sij'+str(currentIter)+'.csv'
print "Writing transit share to", outCSVsij

with open(outCSVsij, 'wb') as f:
    np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')



print "population and employment"
#Gravity prediction
pop = pe['pop'] ** beta1
pop = np.matrix(pop)
emp = pe['emp'] ** beta2
emp = np.matrix(emp)

print "final matrix calculation"
FTT = G * np.array(pop.T * emp) * (sij*ttcostp + (1-sij)*ttcosti)**tau
pFTT= FTT * (1-sij)
pFTT= pFTT.reshape(1,nTAZ**2)
tFTT= FTT * (sij)
tFTT= tFTT.reshape(1,nTAZ**2)
FTTback = FTT.copy()
FTT = np.reshape(FTT,(1,nTAZ**2))

outFTT['flow'] = pFTT
outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'.csv'
print "Writing output to", outCSV
#    with open(outCSV, 'wb') as f:
#        np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')

outFTT['flow'] = tFTT
outCSV = inSpace+'CSV/TransTTflow'+str(currentIter)+'.csv'
print "Writing output to", outCSV
#    with open(outCSV, 'wb') as f:
#        np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')
    
outFTT['flow'] = FTT
outCSV = inSpace+'CSV/TotalTTflow'+str(currentIter)+'.csv'
print "Writing output to", outCSV
with open(outCSV, 'wb') as f:
    np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')

FTTchk = readcsv(outCSV, fdtype, incol=3, sort=[0,1], header=None)
FTT1 = FTTchk['flow']
FTT1 = np.reshape(FTT1, (nTAZ, nTAZ))
chk = FTT1 == FTTback
print "Does it work?", chk.min()