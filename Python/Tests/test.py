import numpy as np
from operator import itemgetter
from math import sqrt
import sys
# TESTING CODE TO RUN STANDALONE
import ModAlloc
if __name__ == "__main__":
	currentIter = 1 	

	inSpace = "C:/Users/Dennis/Desktop/DATAe/"
	inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
	flow = ModAlloc.alloc(inSpace, inFlow, currentIter)

	inSpace = "C:/Users/Dennis/Desktop/DATAe1/"
	inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
	flow = ModAlloc.alloc(inSpace, inFlow, currentIter)


if __name__ == "__in__":
	try:
		inSpace = "C:/Users/Dennis/Desktop/DATAe/"
		inSpacepre = "C:/Users/Dennis/Desktop/DATAe1/"
		currentIter = 1
		inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
		inFlowpre = inSpacepre + "CSV/TTflow" + str(currentIter) + ".csv"
		inTT = inSpace+"CSV/TT.csv"
		inTD = inSpace+"CSV/TD.csv"
		inDT = inSpace+"CSV/DT.csv"
		inTT1 = inSpacepre+"CSV/TT.csv"
		inTD1 = inSpacepre+"CSV/TD.csv"
		inDT1 = inSpacepre+"CSV/DT.csv"
		outCSV = inSpace+"CSV/detflowpost.csv"
		outCSV1 = inSpace+"CSV/detflowpre.csv"

		#Test: 50 TAZs, 1813 DET
		#Full: 2241 TAZs, 1813 DETs
		nTAZ = 50
		nDET = 1813

		#fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
		datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
		#fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
		fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
		
		print "importing various matrices"
		#Read TAZ-TAZ flow (POST)
		ff = np.genfromtxt(inFlow,
					dtype = fdtype,
					delimiter = ",",
					skip_header = 0)
		
		ff = np.asarray(sorted(ff, key=itemgetter(0,1)),
					dtype = fdtype)


		#Read TD cost
		td = np.genfromtxt(inTD, 
					dtype = datatype,
					delimiter = ",", 
					skip_header = 0)

		td = np.asarray(sorted(td, key=itemgetter(1,0)),
					dtype = datatype)
		#print td
		#Read DT cost
		dt = np.genfromtxt(inDT, 
					dtype = datatype,
					delimiter = ",", 
					skip_header = 0)
					
		dt = np.asarray(sorted(dt, key=itemgetter(0,1)),
					dtype = datatype)
		#print dt
		#Read TT cost
		tt = np.genfromtxt(inTT, 
					dtype = datatype,
					delimiter = ",", 
					skip_header = 0)
				
		tt = np.asarray(sorted(tt, key=itemgetter(0,1)),
					dtype = datatype)
		#print tt


		#PRE PRE PRE PRE PRE PRE

		#Read TAZ-TAZ flow (PRE)
		ffpre = np.genfromtxt(inFlowpre,
					dtype = fdtype,
					delimiter = ",",
					skip_header = 0)
		
		ffpre = np.asarray(sorted(ffpre, key=itemgetter(0,1)),
					dtype = fdtype)

		#Read TD cost
		tdpre = np.genfromtxt(inTD1, 
					dtype = datatype,
					delimiter = ",", 
					skip_header = 0)

		tdpre = np.asarray(sorted(tdpre, key=itemgetter(1,0)),
					dtype = datatype)
		#print td
		#Read DT cost
		dtpre = np.genfromtxt(inDT1, 
					dtype = datatype,
					delimiter = ",", 
					skip_header = 0)
					
		dtpre = np.asarray(sorted(dtpre, key=itemgetter(0,1)),
					dtype = datatype)
		#print dt
		#Read TT cost
		ttpre = np.genfromtxt(inTT1, 
					dtype = datatype,
					delimiter = ",", 
					skip_header = 0)
				
		ttpre = np.asarray(sorted(ttpre, key=itemgetter(0,1)),
					dtype = datatype)



		nTAZ = int(sqrt(tt.size))
		if nTAZ != sqrt(tt.size):
			print "ERROR: TAZ SIZE NOT SQUARE!"
		print "import completed"

		print "reshaping..."
		ctd = np.reshape(td['cost'],(nDET, nTAZ))
		cdt = np.reshape(dt['cost'],(nDET, nTAZ))
		ndt = np.reshape(dt['name'],(nDET, nTAZ))
		ctt = np.reshape(tt['cost'],(nTAZ, nTAZ))
		ftt = np.reshape(ff['postflow'],(nTAZ, nTAZ))
		
		ctd1 = np.reshape(tdpre['cost'],(nDET, nTAZ))
		cdt1 = np.reshape(dtpre['cost'],(nDET, nTAZ))
		ndt1 = np.reshape(dtpre['name'],(nDET, nTAZ))
		ctt1 = np.reshape(ttpre['cost'],(nTAZ, nTAZ))
		ftt1 = np.reshape(ffpre['postflow'],(nTAZ, nTAZ))
		
		# Generate a matrix representing TT flow actually changed
		deltaTT = ftt-ftt1
		#deltaTT = deltaTT!=0

		# FLOW MATRIX
		print "begin flow allocation"
		x3 = np.matrix(ctt)
		i = 0
		count = 0
		count1 = 0
		detFlow = {999999: 0}
		detFlow1 = {999999: 0}
		detTest = {999999: 0}
		while i < nDET:
			#Extract current detector id_stn
			det = ndt[i,1][0:6]

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

			#Element multiply by flow
			flow = np.multiply(isflow, ftt)
			totalflow = flow.sum()
			test = np.multiply(isflow, deltaTT)
			detChanged = test.sum()
			#print "Current iteration:", i
			if totalflow > 0:
			#	print "flow:", totalflow
				count +=1
			
			#Record flow in dictionary
			detFlow[det] = totalflow
			detTest[det] = detChanged
			
			
			
			
			
			
			
			det = ndt1[i,1][0:6]

			# Extract cost vectors
			x1 = np.matrix(ctd1[i])
			x1 = x1.T
			x2 = np.matrix(cdt1[i])

			tddt=x1+x2
			#Imprecise/Buffer matching, not needed hopefully
			#match = x3 - tddt
			#t=abs(match)<0.5

			#Precise matching
			isflow = x3 == tddt

			#Element multiply by flow
			flow = np.multiply(isflow, ftt1)
			totalflow = flow.sum()
			#print "Current iteration:", i
			if totalflow > 0:
			#	print "flow:", totalflow
				count1 +=1
			
			#Record flow in dictionary
			detFlow1[det] = totalflow
			
			
			i+=1

		del detFlow[999999]
		del detFlow1[999999]
		print "Number of detectors with match (post):", count
		print "Number of detectors with match (pre):", count1

		dtype = [('idstn','i8'),('flow','f8')]
		detFlow= np.array(detFlow.items(), dtype=dtype)
		detFlow1= np.array(detFlow1.items(), dtype=dtype)

		
		np.savetxt(outCSV, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
		np.savetxt(outCSV1, detFlow1, delimiter=',', fmt='%7.0f, %7.10f')

	except Exception as e:
		tb = sys.exc_info()[2]
		print "Exception in ModAlloc"
		print "An error occurred in ModAlloc line %i" % tb.tb_lineno 
		print e.message
	finally:
		import winsound
		winsound.Beep(500,1000)