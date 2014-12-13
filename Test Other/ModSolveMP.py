# Name: ModSolve.py
# Description: Setup OD cost matrix, solve for TT, TD, DT costs
#              output cost matrices as CSCV
# Requirements: Network Analyst Extension 
# The following are hard coded:
#		- Name of output csv


from ModRealSolveMP import NAtoCSV
import multiprocessing as mp

def combfile(inPath, fileName):
	filenames = (fileName+'1.csv',fileName+'2.csv',fileName+'3.csv',fileName+'4.csv')
	
	with open(inPath+fileName+".CSV", 'w') as outfile:
		for fname in filenames:
			with open(inPath+fname) as infile:
				for line in infile:
					outfile.write(line)
					
					
def solve(inSpace, inGdb, fcTAZ, fcDet):
	try:
		
		#Set local variables
		inNetworkDataset = "Trans/DriveOnly_ND"
		impedanceAttribute = "Cost"
		accumulateAttributeName = "#"
		#accumulateAttributeName = ['Length', 'dps']
		
		#TT COST CALCULATION STARTS HERE
#		outNALayerName = "ODTT"
#		inDestinations = "Trans/"+fcTAZ
#		inOrigins = "Trans/"+fcTAZ
#		outFile = inSpace+"CSV/TT"
#		TTjobs = []
#		for i in range(4):
#			#inGdb[:(len(inGdb)-4)] + str(i+1) + ".gdb"
#			p = mp.Process(target=NAtoCSV, args = (inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins+str(i+1), inDestinations, outNALayerName+str(i+1), outFile+str(i+1)+".csv"))
#			TTjobs.append(p)
#			p.start()
#		for proc in TTjobs:
#			proc.join()
#		
#		#Combine output files
#		combfile(inSpace+"CSV/", "TT")
#		print "TT Solved"
#				
#		
#		#TD COST CALCULATION STARTs HERE
#		outNALayerName = "ODTD"
#		inOrigins = "Trans/"+fcTAZ
#		inDestinations = "Trans/"+fcDet
#		outFile = inSpace+"CSV/TD"
#		TDjobs = []
#		for i in range(4):
#			p = mp.Process(target=NAtoCSV, args = (inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins+str(i+1), inDestinations, outNALayerName+str(i+1), outFile+str(i+1)+".csv"))
#			TDjobs.append(p)
#			p.start()
#		for proc in TDjobs:
#			proc.join()
#
#		#Combine output files
#		combfile(inSpace+"CSV/", "TD")
#
#		print "TD Solved"
		

		#DT COST CALCULATION STARTS HERE
		outNALayerName = "ODDT"
		inOrigins = "Trans/"+fcDet
		inDestinations = "Trans/"+fcTAZ
		outFile = inSpace+"CSV/DT"
		DTjobs = []
		for i in range(4):
			p = mp.Process(target=NAtoCSV, args = (inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins+str(i+1), inDestinations, outNALayerName+str(i+1), outFile+str(i+1)+".csv"))
			DTjobs.append(p)
			p.start()
		for proc in DTjobs:
			proc.join()

		#Combine output files
		combfile(inSpace+"CSV/", "DT")
		
		print "DT Solved"
		
		#NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
		
	except Exception as e:
		# If an error occurred, print line number and error message
		import sys
		tb = sys.exc_info()[2]
		print "An error occurred in ModSolveMP line %i" % tb.tb_lineno
		print str(e)		


