# Name: ModUpdateFlow.py
# Description: This script updates the TAZ to TAZ flow using 
#              updated speed, completing the iteration circle
# Input: updated TT cost (driving), TT cost (transit), 
#        gravity parameters, population (O), employment (D)
# Output: TAZ-TAZ transit share, TAZ-TAZ flow
# Note: This script REQUIRES 64 bit python and numpy to function
#
# Steps:
# 1, Compute updated transit share S (2000x2000)
#    Share equation S_ij = [exp(c1+c2*delta C_ij)]/[1+exp(c1+c2*delta C_ij)]
#    delta C_ij = C(pub)_ij / C(drv)_ij
# 2, Compute total transport flows according to gravity equation:
#    TTF_ij = 	G 
#				* P_i^beta1
#				* E_j^beta2
#				* [S_ij * C(pub)_ij + (1-S_ij) * C(drv)_ij]^tau
# 3, Compute updated private transport flows PTTF
#    PTTF_ij = (1-S_ij) * TTF_ij

#import numpy as np
#from math import exp
## Input: updated TT cost (driving), TT cost (transit), 
##        gravity parameters, population (O), employment (D)
#
##Parameters
#c1 = 5.45
#c2 = -5.05
#G = exp(-3.289)
#beta1 = 0.535
#beta2 = 0.589
#tau = -2.077
#
#ttcost = np.arange(9, dtype = 'float32')+1
#ttcost = ttcost.reshape(3,3)
#
#ttcosti = ttcost
#ttcostp = ttcost + 4
#
#pop = np.array((1.0, 3.0, 6.0)) ** beta1
#pop = np.matrix(pop)
#emp = np.array((8.0, 1.1, 0.9)) ** beta2
#emp = np.matrix(emp)
#
## Sij (OK)
#deltaC = ttcosti/ttcostp
#exx = np.exp(c1+c2*deltaC)
#sij = exx / (1+exx)
#
## Gravity prediction
#a = G * np.array(pop.T * emp) * (sij*ttcostp + (1-sij)*ttcosti)**tau
#print a

#def readcsv(infile, indtype, sort):
#	outFTT = pd.read_csv(infile, header =None)
#	outFTT = outFTT.sort(columns=sort)
#	outFTT = np.asarray(outFTT.iloc[:,0:3].values)
#	outFTT = np.core.records.fromarrays(outFTT.transpose(), dtype = indtype)
#	outFTT = np.asarray(outFTT)
#	return outFTT

def readcsv(infile, indtype, incol, sort, header):
	import pandas as pd
	if header != None:
		header = 0
	outFTT = pd.read_csv(infile, header = header)
	outFTT.columns = [i for i,col in enumerate(outFTT.columns)]
	outFTT = outFTT.sort(columns=sort)
	outFTT = np.asarray(outFTT.iloc[:,0:incol].values)
	outFTT = np.core.records.fromarrays(outFTT.transpose(), dtype = indtype)
	outFTT = np.asarray(outFTT)
	return outFTT

def update(inSpace, currentIter, inTTp):
	try:
		from math import exp, sqrt, pi
		from operator import itemgetter
		import numpy as np
		import sys
		
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
		#	raise Exception('Driving and Transit TT not match!')
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
#		replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
#					+3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
#					replace with 1 if lower than 1		
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
		outFTT['flow'] = pFTT
		
		outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'.csv'
		print "Writing output to", outCSV
		
		with open(outCSV, 'wb') as f:
			np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')


	except Exception as e:
		tb = sys.exc_info()[2]
		print "Error occurred in ModUpdateFlow %i" % tb.tb_lineno 
		print e
	
	#finally:
		#print "Code ends on ", time.strftime("%d/%m/%Y - %H:%M:%S")




if __name__ == "__main__":
	import numpy as np
	inSpace = "E:/DATA2/"
	currentIter = 1
	inTTp = inSpace + "TTpubPost.csv"
	fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
	tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
	petype = [('oid','i8'),('emp','f8'),('pop','f8')]
	areatype = [('oid','i8'),('area','f8')]
	from operator import itemgetter

	outFTT = inSpace + "inFlow.csv"
	outFTT = readcsv(outFTT, fdtype, incol = 3, sort = [0,1], header = None)

	print "importing TTcost for Transit"
	ttp = np.genfromtxt(inTTp, 
				dtype = tttype,
				delimiter = ",", 
				skip_header = 1)
			
	ttp = np.asarray(sorted(ttp, key=itemgetter(0,1)),
				dtype = tttype)
	ttp1 = readcsv(inTTp, tttype, incol = 4, sort = [0,1], header = True)
	
	print "importing TTcost for driving (current)"
#	#TT Cost (driving, CURRENT)
	inTTd = inSpace+"CSV/TT.csv"
	#inTTd = inSpace+"TTdrv.csv"
	ttd = np.genfromtxt(inTTd, 
				dtype = tttype,
				delimiter = ",", 
				skip_header = 0)#header = 0 in actual
			
	ttd = np.asarray(sorted(ttd, key=itemgetter(0,1)),
				dtype = tttype)
	ttd1 = readcsv(inTTd, tttype, incol = 4, sort = [0,1], header = None)
	print ttd[ttd!=ttd1]
	print ttd1[ttd!=ttd1]	
	
	#print "check sorting"
	#make sure both TT costs are sorted correctly:
	#if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
	#if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
	#	raise Exception('Driving and Transit TT not match!')
	#print "sorting is fine"
	
	print "importing census"
	#Population & employment
	inPE = inSpace+"census.csv"		
	pe = np.genfromtxt(inPE,
				dtype = petype,
				delimiter = ",",
				skip_header = 1)
	
	pe = np.asarray(sorted(pe, key=itemgetter(0)),
				dtype = petype)
	pe1 = readcsv(inPE, petype, incol = 3, sort = [0], header = True)
	print pe[pe!=pe1]
	print pe1[pe!=pe1]
	
	print "importing TAZ area"
	inArea = inSpace+"TAZarea.csv"		
	area = np.genfromtxt(inArea,
				dtype = areatype,
				delimiter = ",",
				skip_header = 1)
	
	area = np.asarray(sorted(area, key=itemgetter(0)),
				dtype = areatype)
	area1 = readcsv(inArea, areatype, incol=2, sort=[0], header = True)
	area = area['area']
	area1 = area1['area']
	print area[area!=area1]
	print area1[area!=area1]

if __name__ == "__man__":
	inSpace = "E:/DATA2/"
	currentIter = 1
	inTTp = inSpace + "TTpubPost.csv"
	try:
		from math import exp, sqrt, pi
		from operator import itemgetter
		import numpy as np
		import numexpr as ne
		import sys
		
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
		outFTT = np.genfromtxt(outFTT,
					dtype = fdtype,
					delimiter = ",",
					skip_header = 0)		
		#TT Cost (pub)
		#Post/PRE as SEPARATE CSV FILE
		print "importing TTcost for Transit"
		ttp = np.genfromtxt(inTTp, 
					dtype = tttype,
					delimiter = ",", 
					skip_header = 1)
				
		ttp = np.asarray(sorted(ttp, key=itemgetter(0,1)),
					dtype = tttype)
		
		print "importing TTcost for driving (current)"
		#TT Cost (driving, CURRENT)
		inTTd = inSpace+"CSV/TT.csv"
		#inTTd = inSpace+"TTdrv.csv"
		ttd = np.genfromtxt(inTTd, 
					dtype = tttype,
					delimiter = ",", 
					skip_header = 0)#header = 0 in actual
				
		ttd = np.asarray(sorted(ttd, key=itemgetter(0,1)),
					dtype = tttype)
		
		#print "check sorting"
		#make sure both TT costs are sorted correctly:
		#if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
		#if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
		#	raise Exception('Driving and Transit TT not match!')
		#print "sorting is fine"
		
		print "importing census"
		#Population & employment
		inPE = inSpace+"census.csv"		
		pe = np.genfromtxt(inPE,
					dtype = petype,
					delimiter = ",",
					skip_header = 1)
		
		pe = np.asarray(sorted(pe, key=itemgetter(0)),
					dtype = petype)
		
		print "importing TAZ area"
		inArea = inSpace+"TAZarea.csv"		
		area = np.genfromtxt(inArea,
					dtype = areatype,
					delimiter = ",",
					skip_header = 1)
		
		area = np.asarray(sorted(pe, key=itemgetter(0)),
					dtype = areatype)
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
#		replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
#					+3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
#					replace with 1 if lower than 1		
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
#		outSij = sij.reshape(nTAZ**2,1)
#		outCSVsij = inSpace+'CSV/Sij'+str(currentIter)+'.csv'
#		print "Writing transit share to", outCSVsij
#		
#		with open(outCSVsij, 'wb') as f:
#			np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')
		sij1 = ne.evaluate("(exp(c1+c2*(ttcostp/ttcosti)))/(1+exp(c1+c2*(ttcostp/ttcosti)))")

		
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
		outFTT['flow'] = pFTT
		
		outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'.csv'
		print "Writing output to", outCSV
		
#		with open(outCSV, 'wb') as f:
#			np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')


	except Exception as e:
		tb = sys.exc_info()[2]
		print "Error occurred in ModUpdateFlow %i" % tb.tb_lineno 
		print e
	
#	finally:
#		print "Code ends on ", time.strftime("%d/%m/%Y - %H:%M:%S")