# Name: GIS_Iteration
# Purpose: Run modules to do the following:
# 0, Create a temp scratch version of the network dataset for operation
# 1, Update speed, recalculate cost
# 2, rebuild network dataset
# 3, Calculate cost (TT = TD + DT)
# 4, Compute detector level flow
# 5, Compute detector level updated speed using supply side equation
# 6, Reiterate


if __name__ == '__main__':
	# Parameter settings (mostly paths):
	# NOTE: MAKE SURE inSpace folder HAS ending slash "/"
	base = "DriveOnly_LA.gdb"
	temp = "LA-scratch.gdb"
	#inSpace = "C:/Users/Dennis/Desktop/DATA1/"
	inSpace = "E:/CF-PRE/"
	inGdb = temp
	#inSpeed = "spdtest.csv"
#	SET whether use transit Pre or Post cost
#	Make sure csvs have correct format.
#	oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#	20211000,20211000,0,0
#	20211000,20212000,89.348434,19.777
#	20211000,20213000,135.59612,26.074003
	inTTp = inSpace+"TTpubPre.csv" 
	#inTTp = inSpace+"TTpubPost.csv"
	period = "pre"
	
	base = inSpace+base
	temp = inSpace+temp
	
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
	
	#Specify output file path for excel of relative gap 
	outRelGap = inSpace + "FIGS/relgap.csv"
	
		
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
	startIter = 1
	maxIter = 1


	#ACTUAL COMPUTATION START HERE
	# Import necessary modules
	import ModSetupWorker, ModJoinSpeed, ModBuild, ModSolve, ModAlloc, ModSpeedCalc, ModUpdateFlow, ModRelgap
	import time, shutil
	
	ssdPath = {}
	currentIter = startIter
	while currentIter < (maxIter + startIter):
		print "Iteration", currentIter, "starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
		print inTTp, ", without Transpose, at", inSpace
		# 0, create temp scratch
		print "Setting up scratch version"
		ModSetupWorker.clearOld(base,temp)
		print "Scratch version set up.  Proceding..."
	
		# 1, update speed, recalculate cost 
		print "Update Speed..."
		inSpeed = "detspd" + str(currentIter - 1) + ".csv"
		ModJoinSpeed.joinSpeed(inSpace, inGdb, inSpeed)
	
		# 2, rebuild network dataset
		print "Speed updated. Rebuild Dataset..."
		ModBuild.build(inSpace, inGdb)
		
		print "Dataset rebuilt. Solve for TT, TD, DT"
		ModSolve.solve(inSpace, inGdb, fcTAZ, fcDet)
		
		print "Predicting flow from gravity equation"
		ModUpdateFlow.update(inSpace, currentIter, inTTp)
	
		print "Flow Allocation"
		inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
		flow = ModAlloc.alloc(inSpace, inFlow, currentIter)
	
		#Save TT cost calculated from speed0
		if currentIter == 1:
			shutil.copyfile(inSpace+'CSV/TT.csv', inSpace+'CSV/TT0.csv')
			fd = open(outRelGap,"wb")
			fd.write("Iteration, Relative Gap")
			fd.close()
		#Calculate relative gap
#		relgap = ModRelgap.calc(inSpace, currentIter)
#		relgap = str(currentIter) + ', ' + str(relgap) + ' \n'
#		fd = open(outRelGap,"a")
#		fd.write(relgap)
#		fd.close()
		
		print "Update Speed"
		ssds = ModSpeedCalc.flow2speed(inSpace, flow, currentIter, FL, LIMIT)
		print "SSD from demand:", ssds[0]
		#(ssdsum, ssdmean, ssdsd, ssdmin, ssdmax)
		ssdPath[currentIter] = ssds
		if ssds[0] < threshDS:
			print "Demand met supply"
			break
		
		print "Iteration", currentIter, "done on ", time.strftime("%d/%m/%Y - %H:%M:%S")
		currentIter += 1
	
	#Moving files to results and renaming them.
	import shutil
	#Expected speed
	shutil.copy(inSpace+"detspd0.csv", inSpace+"Results/pre_exp_speed.csv")
	#Predicted flow from expected speed
	shutil.copy(inSpace+"CSV/detflow1.csv", inSpace+"Results/"+period+"_flow.csv")
	shutil.copy(inSpace+"CSV/detflow_adj1.csv", inSpace+"Results/"+period+"_flow_adj.csv")
	#Realized speed
	shutil.copy(inSpace+"detspdSY0.csv", inSpace+"Results/"+period+"_realized_speed.csv")
	
	
	print maxIter, "EVERYTHING COMPLETED on", time.strftime("%d/%m/%Y - %H:%M:%S")
