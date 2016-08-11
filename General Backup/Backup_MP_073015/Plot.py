# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 13:09:17 2014

@author: Dennis
"""

# Name: Plot.py
# Description:	Plot stats for interpretation.
 
import numpy as np
from operator import itemgetter


maxiter = 13


#Convert from GF to the peak time flow F (F = GF x 2 x 6%)

inSpace = "C:/Users/Dennis/Desktop/Results/Pre_1028/"
#inSpace = "E:/DATA_Pre_fix1028/"
inSpace = "C:/Users/Dennis/Desktop/DATA3/"


ssdPath = list()
plotssd = list()
plotssddd = list()
plotffd = list()

period = "P"
i = 1
while i < maxiter:
	fdtype = ([('idstn', '<i8'), ('speed', '<f8')])
	#Read Supply SPEED
	inPS = inSpace + "detspdSY" + str(i) +"-" + period + ".csv"
	inPS = inSpace + "detspd" + str(i-1) +"-" + period + ".csv"

#	inPS = inSpace + "detspdSY" + str(i) +".csv"
#	inPS = inSpace + "detspd" + str(i-1) +".csv"
	ps = np.genfromtxt(inPS, dtype = fdtype, delimiter = ",", skip_header = 1)
	ps = np.asarray(sorted(ps, key=itemgetter(0)), dtype = fdtype)
	
	#Read demand speed
	inCS = inSpace + "detspd" + str(i) +"-" + period + ".csv"
#	inCS = inSpace + "detspd" + str(i) +".csv"
	cs = np.genfromtxt(inCS, dtype = fdtype, delimiter = ",", skip_header = 1)
	cs = np.asarray(sorted(cs, key=itemgetter(0)), dtype = fdtype)
	
#	#Read prev demand speed
#	inCSn = inSpace + "detspd" + str(i+1) +".csv"
#	cs = np.genfromtxt(inCS, dtype = fdtype, delimiter = ",", skip_header = 1)
#	cs = np.asarray(sorted(cs, key=itemgetter(0)), dtype = fdtype)
	
	#Demand side speed
	inDspd = inSpace+"DDspd.csv"
	ds = np.genfromtxt(inDspd, dtype = fdtype, delimiter = ",", skip_header = 0)
	ds = np.asarray(sorted(ds, key=itemgetter(0)), dtype = fdtype)
	
	#Actual flow
	inAF = inSpace+"AF.csv"
	fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8')]
	af = np.genfromtxt(inAF, dtype = fdtype, delimiter = ",", skip_header = 1)
	af = np.asarray(sorted(af, key=itemgetter(0)), dtype = fdtype)
	
	#Current flow
	inFlow = inSpace+"CSV/detflow"+str(i+1)+"-" + period + ".csv"
#	inFlow = inSpace+"CSV/detflow"+str(i+1)+".csv"
	fdtype = [('idstn','i8'),('flow','f8')]
	cff = np.genfromtxt(inFlow, dtype = fdtype, delimiter = ",", skip_header = 0)
	cff = np.asarray(sorted(cff, key=itemgetter(0)), dtype = fdtype)

	ssd = cs['speed'] - ps['speed']
	ffd = (cff['flow']*3.3 - af['flow'])*af['center']
	ffd = ffd[ffd!=0]
	ssdmean = ssd.mean()
	ssdsd = ssd.std()
	ssdmin = ssd.min()
	ssdmax = ssd.max()
	ssdsum = np.multiply(ssd,ssd)
	ssdsum = ssdsum.sum()
	changecount = np.count_nonzero(ssd[abs(ssd)>0.25])

	plotssd.append(ssd)
	plotffd.append(ffd)
	ssdPath.append((i, ssdsum, ssdmean, ssdsd, ssdmin, ssdmax, changecount))

	i+=1

dtype = [('iter','i8'),('sum','f8'),('mean','f8'),('sd','f8'),('min','f8'),('max','f8'),('detchange','i8')]
ssdPath = np.array(ssdPath, dtype=dtype)
outCSV = inSpace+'FIGS/ssdPath.csv'
print "Writing SSD path to", outCSV
with open(outCSV, 'wb') as f:
	f.write(b'iter,SSDsum, Dmean, Dsd, Dmin, Dmax, detChange>0.25, (speed is Dd - Sy)\n')
	np.savetxt(f, ssdPath, delimiter=',', fmt='%7.0f, %7.10f, %7.10f, %7.10f, %7.10f, %7.10f, %7.0f')


from pylab import *
#Box Graph
figure()
title('Evolution path of Dd speed differences between iterations')
xlabel('Iterations')
ylabel('Difference (mph)')
notes = "Note: Box represent interquartile range, red line represent median," + \
		"\nand small crosses represent outlyers."
plt.annotate(notes, (0,0), (0, -40), xycoords='axes fraction', textcoords='offset points', va='top',size='small')
boxplot(plotssd)
#show()
savefig(inSpace+'FIGS/dPath.pdf', bbox_inches='tight')


#Box Graph Zoomed in
figure()
title('Evolution path of speed diff\n(Last five iterations)')
xlabel('Iterations')
ylabel('Difference (mph)')
notes = "Note: Box represent interquartile range, red line represent median," + \
		"\nand small crosses represent outlyers."

plt.annotate(notes, (0,0), (0, -40), xycoords='axes fraction', textcoords='offset points', va='top',size='small')
boxplot(plotssd[-5:])
savefig(inSpace+'FIGS/dPath-last5.pdf', bbox_inches='tight')



# Two subplots, unpack the axes array immediately
f, (ax1, ax2) = plt.subplots(1, 2)
suptitle('Sum Squared Error path\nDifference between iterations',size='large')
ax1.plot(ssdPath['sum'])
ax2.plot(ssdPath['sum'][-20:])
xlabel('Iterations')
#ax2.set_xticks(np.arange(3+1,maxiter,1))
notes = "Note: x axis represent iterations, left graph plots overall SSD evolution path, "+\
		"\nright graph skips the first three iterations to zoom in on the tail to show scale."
ax1.annotate(notes, (0,0), (0, -40), xycoords='axes fraction', textcoords='offset points', va='top',size='small')
savefig(inSpace+'FIGS/ssdPath.pdf', bbox_inches='tight')


#Number of detectors changing
figure()
title('Number of detectors with >0.25 mph speed change')
xlabel('Iterations')
ylabel('# detectors')
plot(ssdPath['detchange'])
show()

#Number of detectors changing (zoom)
figure()
title('Number of detectors with >0.25 mph speed change\n(last 5 iterations)')
xlabel('Iterations')
ylabel('# detectors')
plot(ssdPath['detchange'][-5:])
savefig(inSpace+'FIGS/detChange.pdf', bbox_inches='tight')


#FLOW DIFFERENCE (STILL VERY BAD)
#figure()
#title('Evolution path of predicted\nand actual flow difference')
#xlabel('Iterations')
#ylabel('Difference (# cars)')
#notes = "Note: Box represent interquartile range, red line represent median," + \
#		"\nand small crosses represent outlyers."
#plt.annotate(notes, (0,0), (0, -40), xycoords='axes fraction', textcoords='offset points', va='top',size='small')
#boxplot(plotffd)
#show()






