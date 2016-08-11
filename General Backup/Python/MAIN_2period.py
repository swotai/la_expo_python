# Name: GIS_Iteration
# Purpose: Run modules to do the following:
# 0, Create a temp scratch version of the network dataset for operation
# 1, Update speed, recalculate cost
# 2, rebuild network dataset
# 3, Calculate cost (TT = TD + DT)
# 3.1, Calculate cost for Off Peak
# 4, Compute detector level flow
# 5, Compute detector level updated speed using supply side equation
# 6, Reiterate


if __name__ == '__main__':
	# Parameter settings (mostly paths):
	# NOTE: MAKE SURE inSpace folder HAS ending slash "/"
	base = "DriveOnly_LA.gdb"
	temp = "LA-scratch.gdb"
	temp_op = "LA-scratch-op.gdb"
	#inSpace = "C:/Users/Dennis/Desktop/DATA1/"
	inSpace = "E:/DATA_test2p_1105/"
	inGdb = temp
	inGdb_op = temp_op
	#inSpeed = "spdtest.csv"
#	SET whether use transit Pre or Post cost
#	Make sure csvs have correct format.
#	oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#	20211000,20211000,0,0
#	20211000,20212000,89.348434,19.777
#	20211000,20213000,135.59612,26.074003
	inTTp = inSpace+"TTpubPre.csv" 
	#inTTp = inSpace+"TTpubPost.csv"

	
	base = inSpace+base
	temp = inSpace+temp
	temp_op = inSpace+temp_op
	
	##TAZs:
	##	TAZ_LA_proj_centroid  >---< inFlow.csv
	##	TAZ_LA_TESTSAMPLE (50)  >---< inFlow50.csv
	##Detectors:
	##	hd_ML_snap (1800)
	fcTAZ = "TAZ_LA_proj_centroid"
	fcDet = "hd_ML_snap"
	#inFLOW = PREDICTED FLOW FROM GRAVITY (STATIC), not to confused with AF (Actual Flow)
	#inFLOW.csv at inSpace is used for Pre flow as starting point for iteration.
	inFlow = inSpace + "inFlow.csv"
	

	#For Allocation
	#weight is how much weight to put into new speed
	#FL should be 500, however because small TAZ number
	#in test sample, threshold changed to 1 to test equation.
	LIMIT = 65
	weight = 0.5
	FL = 500
	
	# Iteration ending thresholds:
	threshIT = 0.00001
	threshDS = 1
	
	# The way this is coded, if an iteraction is completed
	# i.e. with the speed outputed, the code can start from there.
	# Change the currentIter to the max number of detspd +1
	startIter = 2
	maxIter = 1
	
	# Off peak commuting penalty
	OPpenalty = 10

	#ACTUAL COMPUTATION START HERE
	# Import necessary modules
	import ModSetupWorker, ModJoinSpeed, ModBuild, ModSolve, ModAlloc, ModSpeedCalc_avg10, ModUpdateFlow
	import time, shutil
	
	ssdPath = {}
	currentIter = startIter
	while currentIter < (maxIter + startIter):
		print "Iteration", currentIter, "starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
		print inTTp, ", at", inSpace
		# 0, create temp scratch
		print "Setting up scratch version"
		ModSetupWorker.clearOld(base,temp)
		ModSetupWorker.clearOld(base,temp_op)
		print "Scratch version set up.  Proceding..."
	
		# 1, update speed, recalculate cost 
		print "Update Speed..."
		inSpeed = "detspd" + str(currentIter - 1) + "-P.csv"
		ModJoinSpeed.joinSpeed(inSpace, inGdb, inSpeed)
		inSpeed_op = "detspd" + str(currentIter - 1) + "-OP.csv"
		ModJoinSpeed.joinSpeed(inSpace, inGdb_op, inSpeed_op)
	
		# 2, rebuild network dataset
		print "Speed updated. Rebuild Dataset..."
		ModBuild.build(inSpace, inGdb)
		ModBuild.build(inSpace, inGdb_op)
		
		print "Dataset rebuilt. Solve for TT, TD, DT"
		ModSolve.solve_2p(inSpace, inGdb, fcTAZ, fcDet, "P")
		ModSolve.solve_2p(inSpace, inGdb_op, fcTAZ, fcDet, "OP")
		
		print "Predicting flow from gravity equation"
		ModUpdateFlow.update_2p(inSpace, currentIter, inTTp, OPpenalty)
	
		print "Flow Allocation"
#		inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-P.csv"
		flow_p = ModAlloc.alloc_2p(inSpace, currentIter, "P")

#		inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-OP.csv"
		flow_op = ModAlloc.alloc_2p(inSpace, currentIter, "OP")
	

		
		print "Update Speed"
		ModSpeedCalc_avg10.flow2speed_2p(inSpace, currentIter, FL, LIMIT)
#		print "SSD from demand:", ssds[0]
#		#(ssdsum, ssdmean, ssdsd, ssdmin, ssdmax)
#		ssdPath[currentIter] = ssds
#		if ssds[0] < threshDS:
#			print "Demand met supply"
#			break
		
		print "Iteration", currentIter, "done on ", time.strftime("%d/%m/%Y - %H:%M:%S")
		currentIter += 1
	
	print maxIter, "EVERYTHING COMPLETED on", time.strftime("%d/%m/%Y - %H:%M:%S")
	print "SSD Evolution Path"
	print ssdPath


#		Save TT cost calculated from speed0
#		if currentIter == 1:
#			shutil.copyfile(inSpace+'CSV/TT.csv', inSpace+'CSV/TT0.csv')
