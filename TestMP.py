# -*- coding: utf-8 -*-
"""
Created on Wed Nov 05 20:01:44 2014

@author: Dennis
"""


import multiprocessing as mp
import time
import sys
import ModJoinSpeed

def daemon1(towait):
    print 'Starting:', multiprocessing.current_process().name
    print "wait seconds:", towait
    time.sleep(towait)
    
    print 'Exiting :', multiprocessing.current_process().name

def non_daemon(toprint):
    print 'Starting:', multiprocessing.current_process().name
    print toprint
    print 'Exiting :', multiprocessing.current_process().name

if __name__ == '__mai__':
    d = multiprocessing.Process(name='process 1: wait 3, daemon', target=daemon1, args=(3,))
#    d.daemon = True

    n = multiprocessing.Process(name='process 2: wait 5', target=daemon1, args=(10,))
#    n.daemon = False

    d.start()
    time.sleep(1)
    n.start()

    d.join()
    print 'd._is_alive()', d.is_alive()
    n.join()
    print "whatever follows"
				
def testjoinspeed(inSpace, inGdb, inSpeed):
	Gdb = inGdb[:-4] + "" + inGdb[-4:]
	j01 = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace,Gdb,inSpeed))
	Gdb = inGdb[:-4] + "1" + inGdb[-4:]
	j02 = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace,Gdb,inSpeed))
	j01.start()
	time.sleep(5)
	j02.start()
	j01.join()
	j02.join()
if __name__ == '__main__':
	# Parameter settings (mostly paths):
	# NOTE: MAKE SURE inSpace folder HAS ending slash "/"
	base = "DriveOnly_LA.gdb"
	temp = "LA-scratch.gdb"
	temp_op = "LA-scratch-op.gdb"
	#inSpace = "C:/Users/Dennis/Desktop/DATA1/"
	inSpace = "E:/DATA_testMP/"
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
	startIter = 1
	maxIter = 2
	
	# Off peak commuting penalty
	OPpenalty = 10


	print "Baseline: time for running 1 time.  Starting time",time.strftime("%d/%m/%Y - %H:%M:%S")
#	time0 = time.time()
#	inSpeed = "detspd" + str(0) + "-P.csv"
#	ModJoinSpeed.joinSpeed(inSpace, inGdb, inSpeed)
#	time1 = time.time()
#	print "takes:", (time1-time0)/60, "minutes, ending",time.strftime("%d/%m/%Y - %H:%M:%S")
	print "Baseline takes 0.5 minutes roughly."

	currentIter = startIter
		
	while currentIter < (maxIter + startIter):
		print "iteration", currentIter, "starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
		inSpeed = "detspd" + str(currentIter - 1) + "-P.csv"
		j1 = mp.Process(target=testjoinspeed, args=(inSpace, inGdb, inSpeed))
		inSpeed = "detspd" + str(currentIter - 1) + "-OP.csv"
		j2 = mp.Process(target=testjoinspeed, args=(inSpace, inGdb_op, inSpeed))
		
		time0 = time.time()
		j1.start()
		time.sleep(5)
		j2.start()
		j1.join()
		j2.join()
		time1 = time.time()
		print "takes:", (time1-time0)/60, "minutes, ending",time.strftime("%d/%m/%Y - %H:%M:%S")
		currentIter +=1
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	