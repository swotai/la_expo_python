# Name: ModSpeedCalc.py
# Description:	Recalculate network speed based on updated flow.
#				Export CSV for next iteration
 

from ModIO import readcsv



def flow2speed_2p(inSpace, currentIter, FL, LIMIT):
	import sys
	import numpy as np
	from math import exp

	try:
		# READ FLOW (PEAK)
		cff_p = inSpace+"CSV/detflow"+str(currentIter)+"-P.csv"
		fdtype = [('idstn','i8'),('flow','f8')]
		cff_p = readcsv(cff_p, fdtype, incol = 2, sort = [0], header = None)
		# READ FLOW (Off PEAK)
		cff_op = inSpace+"CSV/detflow"+str(currentIter)+"-OP.csv"
		fdtype = [('idstn','i8'),('flow','f8')]
		cff_op = readcsv(cff_op, fdtype, incol = 2, sort = [0], header = None)

		numBack = 9    # How many iteration back to include in the exp. +1 = total number for exp
	
		# Simple weight for now
		avgwt = 1./(np.arange(currentIter)+1)
		
		# Truncate the weight to at most 10	
		avgwt = avgwt[0:numBack]
		avgwt = avgwt[::-1]
		
		print avgwt
		
		prior = np.arange(currentIter)
		prior = prior[-numBack:]
		
		# Read Previous Speeds (PEAK)
		print "prior:", prior
		a = np.zeros([numBack,1813])    # TODO: HARDCODED 1813 here.  NEED FIX WHEN UPDATE TO FULL LA AREA
		j = 0
		for i in prior:
			inPspd = inSpace+"detspd"+str(i)+"-P.csv"
			fdtype = [('idstn','i8'),('speed','f8')]
			ps1 = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
			print "a[",j,"]", "=", inPspd
			a[j] = ps1['speed']
			j+=1
		b = np.average(a[:j], axis=0, weights=avgwt)
		ps1['speed'] = np.copy(b)
		ps_p = np.copy(ps1)
		del a, b, ps1
		

		# Read Previous Speeds (offPEAK)
		print "prior:", prior
		a = np.zeros([numBack,1813])    # TODO: HARDCODED 1813 here.  NEED FIX WHEN UPDATE TO FULL LA AREA
		j = 0
		for i in prior:
			inPspd = inSpace+"detspd"+str(i)+"-OP.csv"
			ps1 = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
			print "a[",j,"]", "=", inPspd
			a[j] = ps1['speed']
			j+=1
		b = np.average(a[:j], axis=0, weights=avgwt)
		ps1['speed'] = np.copy(b)
		ps_op = np.copy(ps1)
		del a, b, ps1

		

		#AF = Actual Daily TOTAL FLOW (average pre expo)
		inAF = inSpace+"AF.csv"
		fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8')]
#		af = np.genfromtxt(inAF,
#							dtype = fdtype,
#							delimiter = ",",
#							skip_header = 1)
#		af = np.asarray(sorted(af, key=itemgetter(0)),
#						dtype = fdtype)
		af = readcsv(inAF, fdtype, incol = 4, sort=0, header = True)

		#Convert from GF to the peak time flow F (F = GF x 2 x 6%)
		#cff['flow'] = cff['flow']*0.12
		
		#CHECK TO MAKE SURE THE ARRAYS MATCHES
		x1 = af['idstn']
		x2 = cff_p['idstn']
		xeq = x1==x2
		if xeq[xeq!=True].size != 0:
			raise Exception("AF and Current detector flow idstn DOES NOT MATCH!")
		#Calculate AF/GF ratio for center detectors
		np.seterr(divide = 'ignore')
#		THIS RATIO IS NOT GOOD: Average take into consider non-central areas
#		ratio = af['center']*af['flow']/(cff['flow']+0.000001)
#		Remove inf and nan, calculate mean
#		ratio = ratio[~np.isnan(ratio)]
#		ratio = ratio[~np.isinf(ratio)]
#		ratio = ratio.mean()
		aft = af['center']*af['flow']
		aft = aft.sum()
		cft_p = af['center']*cff_p['flow']
		cft_p = cft_p.sum()
		cft_op = af['center']*cff_op['flow']
		cft_op = cft_op.sum()
		ratio = aft/(cft_p + cft_op)
		print "AF/GF Ratio:", ratio

		#SAVE DETFLOW WITH ADJUSTMENT
		#PEAK
		detFlow= np.copy(cff_p)
		detFlow['flow'] = detFlow['flow']*ratio
		outCSVcff = inSpace+'CSV/detflow_adj'+str(currentIter)+'-P.csv'
		np.savetxt(outCSVcff, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
		#OffPEAK
		detFlow= np.copy(cff_op)
		detFlow['flow'] = detFlow['flow']*ratio
		outCSVcff = inSpace+'CSV/detflow_adj'+str(currentIter)+'-OP.csv'
		np.savetxt(outCSVcff, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
		
		#Convert from GF to the peak time flow F = AF/GF*6%*GF
#		cff['flow'] = ratio*0.06*(cff['flow'])/af['lane']
		# TODO:	Ratio of 6% still ok??? 
		cff_p['flow'] = ratio*0.6*(cff_p['flow'])/af['lane']
		cff_op['flow'] = ratio*0.6*(cff_op['flow'])/af['lane']
		
		#Update supply side speed using supply side equation
		#PEAK
		for x in np.nditer(cff_p['flow'], op_flags = ['readwrite']):
			if x > FL:
				x[...] = LIMIT * exp(-0.000191*(x-FL))
			else:
				x[...] = LIMIT
		#OffPEAK
		for x in np.nditer(cff_op['flow'], op_flags = ['readwrite']):
			if x > FL:
				x[...] = LIMIT * exp(-0.000191*(x-FL))
			else:
				x[...] = LIMIT

		cff_p.dtype = ([('idstn', '<i8'), ('speed', '<f8')])
		cff_op.dtype = ([('idstn', '<i8'), ('speed', '<f8')])

		#SAVE THE SUPPLY SIDE SPEED
		outCSV = inSpace+'detspdSY'+str(currentIter-1)+'-P.csv'
		print "speed updated.  Writing to", outCSV
		with open(outCSV, 'wb') as f:
			f.write(b'id_stn,speed\n')
			np.savetxt(f, cff_p, delimiter=',', fmt='%7.0f, %7.10f')
		outCSV = inSpace+'detspdSY'+str(currentIter-1)+'-OP.csv'
		print "speed updated.  Writing to", outCSV
		with open(outCSV, 'wb') as f:
			f.write(b'id_stn,speed\n')
			np.savetxt(f, cff_op, delimiter=',', fmt='%7.0f, %7.10f')
	
		
		#Set new supply side speed as linear combination of prev and current
		#supply side speed.  Weight wt is set in the beginning.
		#OLD WEIGHTING METHOD		
		#cff['speed'] = weight*cff['speed'] + (1-weight)*ps['speed']
		#Construct weight vector

		#HINT: PEAK
		weight = cff_p['speed'] - ps_p['speed']
		weight = abs(weight)
		#FULL CONTROL: weight is 10% of absolute speed difference
		#Top code at 7.5mph
		#Old equation actually works without modification
		for x in np.nditer(weight, op_flags = ['readwrite']):
			if x > 25:
				x[...] = 0.5
			elif x > 0.25:
				x[...] = x**0.5/10
			else:
				x[...] = 0
		cff_p['speed'] = weight*cff_p['speed'] + (1-weight)*ps_p['speed']

		outCSV = inSpace+'detspd'+str(currentIter)+'-P.csv'
		print "speed updated.  Writing to", outCSV
		with open(outCSV, 'wb') as f:
			f.write(b'id_stn,speed\n')
			np.savetxt(f, cff_p, delimiter=',', fmt='%7.0f, %7.10f')


		#HINT: OffPEAK
		weight = cff_op['speed'] - ps_op['speed']
		weight = abs(weight)
		#FULL CONTROL: weight is 10% of absolute speed difference
		#Top code at 7.5mph
		#Old equation actually works without modification
		for x in np.nditer(weight, op_flags = ['readwrite']):
			if x > 25:
				x[...] = 0.5
			elif x > 0.25:
				x[...] = x**0.5/10
			else:
				x[...] = 0
		cff_op['speed'] = weight*cff_op['speed'] + (1-weight)*ps_op['speed']

		outCSV = inSpace+'detspd'+str(currentIter)+'-OP.csv'
		print "speed updated.  Writing to", outCSV
		with open(outCSV, 'wb') as f:
			f.write(b'id_stn,speed\n')
			np.savetxt(f, cff_op, delimiter=',', fmt='%7.0f, %7.10f')

		#Loop End Condition
		#  2, Number of iteration reach X
		#  3, Supply side Speed - Demand side < threshold
		#Function returns the ssd(1) and ssd for SY-DD(3)

#		ssd = cff['speed'] - ps['speed']
#		ssdmean = ssd.mean()
#		ssdsd = ssd.std()
#		ssdmin = ssd.min()
#		ssdmax = ssd.max()
#		
#		ssdsum = ssd*ssd
#		ssdsum = ssdsum.sum()
#		return (ssdsum, ssdmean, ssdsd, ssdmin, ssdmax)
				
	except Exception as e:
		tb = sys.exc_info()[2]
		print "Exception in ModSpeedCalc"
		print "An error occurred in ModSpeedCalc line %i" % tb.tb_lineno 
		print e.message
		

#def flow2speed(inSpace, inFlow, currentIter, FL, LIMIT):
#	import sys
#	import numpy as np
#	from math import exp
#	from operator import itemgetter
#	try:
#		
#		cff = inFlow
#		fdtype = [('idstn','i8'),('flow','f8')]
#		cff = np.asarray(sorted(cff, key=itemgetter(0)),
#						  dtype = fdtype)
#
#		#Previous speed
#		inPspd = inSpace+"detspd"+str(currentIter-1)+".csv"
#		fdtype = [('idstn','i8'),('speed','f8')]
##		ps = np.genfromtxt(inPspd,
##							dtype = fdtype,
##							delimiter = ",",
##							skip_header = 1)
##		ps = np.asarray(sorted(ps, key=itemgetter(0)),
##						dtype = fdtype)
##		ps = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
#		numBack = 9    # How many iteration back to include in the exp. +1 = total number for exp
#		a = np.zeros([numBack,1813])
#	
#		# Simple weight for now
#		avgwt = 1./(np.arange(currentIter)+1)
#		
#		# Truncate the weight to at most 10	
#		avgwt = avgwt[0:numBack]
#		avgwt = avgwt[::-1]
#		
#		print avgwt
#		
#		prior = np.arange(currentIter)
#		prior = prior[-numBack:]
#		print "prior:", prior
#		j = 0
#		for i in prior:
#			inPspd = inSpace+"detspd"+str(i)+".csv"
#			ps = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
#			print "a[",j,"]", "=", inPspd
#			a[j] = ps['speed']
#			j+=1
#		b = np.average(a[:j], axis=0, weights=avgwt)
#		ps['speed'] = np.copy(b)
#		del a, b
#
#		#AF = Actual Daily TOTAL FLOW (average pre expo)
#		inAF = inSpace+"AF.csv"
#		fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8')]
##		af = np.genfromtxt(inAF,
##							dtype = fdtype,
##							delimiter = ",",
##							skip_header = 1)
##		af = np.asarray(sorted(af, key=itemgetter(0)),
##						dtype = fdtype)
#		af = readcsv(inAF, fdtype, incol = 4, sort=0, header = True)
#
#		#Convert from GF to the peak time flow F (F = GF x 2 x 6%)
#		#cff['flow'] = cff['flow']*0.12
#		
#		#CHECK TO MAKE SURE THE ARRAYS MATCHES
#		x1 = af['idstn']
#		x2 = cff['idstn']
#		xeq = x1==x2
#		if xeq[xeq!=True].size != 0:
#			raise Exception("AF and Current detector flow idstn DOES NOT MATCH!")
#		#Calculate AF/GF ratio for center detectors
#		np.seterr(divide = 'ignore')
##		THIS RATIO IS NOT GOOD: Average take into consider non-central areas
##		ratio = af['center']*af['flow']/(cff['flow']+0.000001)
##		Remove inf and nan, calculate mean
##		ratio = ratio[~np.isnan(ratio)]
##		ratio = ratio[~np.isinf(ratio)]
##		ratio = ratio.mean()
#		aft = af['center']*af['flow']
#		aft = aft.sum()
#		cft = af['center']*cff['flow']
#		cft = cft.sum()
#		ratio = aft/cft
#		print "AF/GF Ratio:", ratio
#
#		#SAVE DETFLOW WITH ADJUSTMENT
#		detFlow= np.copy(cff)
#		detFlow['flow'] = detFlow['flow']*ratio
#		outCSVcff = inSpace+'CSV/detflow_adj'+str(currentIter)+'.csv'
#		np.savetxt(outCSVcff, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
#		
#		#Convert from GF to the peak time flow F = AF/GF*6%*GF
#		cff['flow'] = ratio*0.06*(cff['flow'])/af['lane']
#		
#		#Update supply side speed using supply side equation
#		for x in np.nditer(cff['flow'], op_flags = ['readwrite']):
#			if x > FL:
#				x[...] = LIMIT * exp(-0.000191*(x-FL))
#			else:
#				x[...] = LIMIT
#
#		cff.dtype = ([('idstn', '<i8'), ('speed', '<f8')])
#
#		#SAVE THE SUPPLY SIDE SPEED
#		outCSV = inSpace+'detspdSY'+str(currentIter-1)+'.csv'
#		print "speed updated.  Writing to", outCSV
#		with open(outCSV, 'wb') as f:
#			f.write(b'id_stn,speed\n')
#			np.savetxt(f, cff, delimiter=',', fmt='%7.0f, %7.10f')
#	
#		
#		#Set new supply side speed as linear combination of prev and current
#		#supply side speed.  Weight wt is set in the beginning.
#		#OLD WEIGHTING METHOD		
#		#cff['speed'] = weight*cff['speed'] + (1-weight)*ps['speed']
#		#Construct weight vector
#		weight = cff['speed'] - ps['speed']
#		weight = abs(weight)
#		#FULL CONTROL: weight is 10% of absolute speed difference
#		#Top code at 7.5mph
#		#Old equation actually works without modification
#		for x in np.nditer(weight, op_flags = ['readwrite']):
#			if x > 25:
#				x[...] = 0.5
#			elif x > 0.25:
#				x[...] = x**0.5/10
#			else:
#				x[...] = 0
#		cff['speed'] = weight*cff['speed'] + (1-weight)*ps['speed']
#
#		outCSV = inSpace+'detspd'+str(currentIter)+'.csv'
#		print "speed updated.  Writing to", outCSV
#		with open(outCSV, 'wb') as f:
#			f.write(b'id_stn,speed\n')
#			np.savetxt(f, cff, delimiter=',', fmt='%7.0f, %7.10f')
#
#		#Loop End Condition
#		#  2, Number of iteration reach X
#		#  3, Supply side Speed - Demand side < threshold
#		#Function returns the ssd(1) and ssd for SY-DD(3)
#
#		ssd = cff['speed'] - ps['speed']
#		ssdmean = ssd.mean()
#		ssdsd = ssd.std()
#		ssdmin = ssd.min()
#		ssdmax = ssd.max()
#		
#		ssdsum = ssd*ssd
#		ssdsum = ssdsum.sum()
#		return (ssdsum, ssdmean, ssdsd, ssdmin, ssdmax)
#				
#	except Exception as e:
#		tb = sys.exc_info()[2]
#		print "Exception in ModSpeedCalc"
#		print "An error occurred in ModSpeedCalc line %i" % tb.tb_lineno 
#		print e.message
#		
#if __name__ == '__man__':
##	import os, sys, traceback
##	import numpy as np
##	from math import exp
##	from operator import itemgetter
#	inSpace = "C:/Users/Dennis/Desktop/Results/Gen_PreTT_RightSpeed/"
#	flow = "C:\Users\Dennis\Desktop\Results\Gen_PreTT_RightSpeed\pre_eqm_detflow1.csv"
#	currentIter = 1
#	FL=500
#	LIMIT = 65
#	fdtype = [('idstn','i8'),('flow','f8')]
#	inFlow = np.genfromtxt(flow, dtype=fdtype, delimiter=",", skip_header = 0)
#	flow2speed(inSpace, inFlow, currentIter, FL, LIMIT)
#
#if __name__ == '__main__':
##	import os, sys, traceback
##	import numpy as np
##	from math import exp
##	from operator import itemgetter
##	Function should be receiving the flow vector from input.
##	For dev purpose, import from CSV
#	import numpy as np
#	currentIter = 18
#	inSpace = "C:/Users/Dennis/Desktop/DATA/"
#	LIMIT = 65
#	weight = 0.5
#	FL = 500
#	#inPspd = inSpace+"detspd"+str(currentIter-1)+".csv"
#	fdtype = [('idstn','i8'),('speed','f8')]
#	#ps = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
#	a = np.zeros([9,1813])
#
#	# Simple weight for now
#	avgwt = 1./(np.arange(currentIter)+1)
#	
#	# Truncate the weight to at most 10	
#	avgwt = avgwt[0:9]
#	avgwt = avgwt[::-1]
#	
#	print avgwt
#	
#	prior = np.arange(currentIter)
#	prior = prior[-9:]
#	print "prior:", prior
#	j = 0
#	for i in prior:
#		inPspd = inSpace+"detspd"+str(i)+".csv"
#		ps = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
#		print "a[",j,"]", "=", inPspd
#		a[j] = ps['speed']
#		j+=1
#	b = np.average(a[:j], axis=0, weights=avgwt)
#	ps['speed'] = np.copy(b)







#	READ SPEED FROM DETECTOR, SHOULDN'T NEED 
	#Current flow
#	inFlow = inSpace+"CSV/detflow"+str(currentIter)+".csv"
#	fdtype = [('idstn','i8'),('flow','f8')]
#	cff = np.genfromtxt(inFlow,
#					 dtype = fdtype,
#					 delimiter = ",",
#					 skip_header = 0)
#	cff = np.asarray(sorted(cff, key=itemgetter(0)),
#					dtype = fdtype)
#
#	inPspd = inSpace+"detspd"+str(currentIter-1)+".csv"
#	ps = np.genfromtxt(inPspd,
#						dtype = fdtype,
#						delimiter = ",",
#						skip_header = 1)
#	ps = np.asarray(sorted(ps, key=itemgetter(0)),
#					dtype = fdtype)
#	ps1 = readcsv(inPspd, fdtype, incol = 2, sort = [0], header = True)
#
#	inAF = inSpace+"AF.csv"
#	fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8')]
#	af = np.genfromtxt(inAF,
#						dtype = fdtype,
#						delimiter = ",",
#						skip_header = 1)
#	af = np.asarray(sorted(af, key=itemgetter(0)),
#					dtype = fdtype)
#	af1 = readcsv(inAF, fdtype, incol = 4, sort=0, header = True)

#	x1 = af['idstn']
#	x2 = cff['idstn']
#	xeq = x1==x2
#	if xeq[xeq!=True].size !=0:
#		print("AF and Current detector flow idstn DOES NOT MATCH")
#
#	centerflow = af['center']*af['flow']
#	centerflow.sum()
#	centerflow.mean()
#	centercff = af['center']*cff['flow']
#	centercff.sum()
#	print "centerflow sum ratio:",centerflow.sum()/centercff.sum()
#	
#	b = centerflow/centercff
#	b = b[~np.isnan(b)]
#	print "mean ratio:", b.mean()
#	aft = af['center']*af['flow']
#	aft = aft.sum()
#	cft = af['center']*cff['flow']
#	cft = cft.sum()
#	ratio = aft/cft
#	print "AF/GF Ratio:", ratio
#	
#	print "current method ratio:", ratio
#	detFlow=cff
#	detFlow['flow'] = detFlow['flow']*ratio
#	dtype = [('idstn','i8'),('flow','f8')]
#	outCSVcff = inSpace+'CSV/detflow_adj'+str(currentIter-1)+'.csv'
#	np.savetxt(outCSVcff, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
#	orig=np.copy(cff)
#	
#	#Convert from GF to the peak time flow F = AF/GF*6%*GF
#	cff['flow'] = ratio*0.06*(cff['flow'])
#	
#	
#	#Update supply side speed using supply side equation
#	for x in np.nditer(cff['flow'], op_flags = ['readwrite']):
#		if x > FL:
#			x[...] = LIMIT * exp(-0.000191*(x-FL))
#		else:
#			x[...] = LIMIT
#
#	cff.dtype = ([('idstn', '<i8'), ('speed', '<f8')])
#	a=np.copy(cff)
#	
#	cff = np.copy(orig)	
#	cff['flow'] = ratio*0.06*(cff['flow'])/af['lane']
#	#Update supply side speed using supply side equation
#	for x in np.nditer(cff['flow'], op_flags = ['readwrite']):
#		if x > FL:
#			x[...] = LIMIT * exp(-0.000191*(x-FL))
#		else:
#			x[...] = LIMIT
#
#	cff.dtype = ([('idstn', '<i8'), ('speed', '<f8')])
#	b=np.copy(cff)