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

# GIS Operation in one function for MP process.
import ModSetupWorker, ModJoinSpeed, ModBuild, ModSolveMP, ModAlloc, ModSpeedCalc_avg10, ModUpdateFlow
from ModSetupWorker import setup_3workers, del_3workers, dbf2CSV
import time
import multiprocessing as mp

def GISops(inSpace, inGdb, currentIter, fcTAZ, fcDet):
    try:
    #    print "Starting GIS process", mp.current_process().name, "on", time.strftime("%d/%m/%Y - %H:%M:%S")
        # SETUP JOBS
        period = "P"
        inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
        Gdb_P = Gdb
        j1_p = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
        j2_p = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
        j3_p = mp.Process(target=ModSolveMP.solve_2p, args=(inSpace, Gdb, fcTAZ, fcDet, period))
        
        period = "OP"
        inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
        Gdb_OP = Gdb
        j1_op = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
        j2_op = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
        j3_op = mp.Process(target=ModSolveMP.solve_2p, args=(inSpace, Gdb, fcTAZ, fcDet, period))
    
    
        # Run Jobs.  Try to keep jobs in sync    
        # HINT: Give some slack time between processes to make sure they won't try to access same files.
        # HINT: Run j1 together, wait for both job to finish with join, then run next job.
        # Job 1
        j1_p.start()
        time.sleep(10)
        j1_op.start()
        j1_p.join()
        j1_op.join()
        # Job 2
        j2_p.start()
        time.sleep(10)
        j2_op.start()
        j2_p.join()
        j2_op.join()
        # Job 3
        setup_3workers(inSpace, Gdb_P)
        setup_3workers(inSpace, Gdb_OP)
        j3_p.start()
        time.sleep(30)
        j3_op.start()
        j3_p.join()
        j3_op.join()
    
        del_3workers(inSpace, Gdb_P)
        del_3workers(inSpace, Gdb_OP)
        
        # Convert DBF to CSV
        dbf2CSV(inSpace+"/CSV/TTP.dbf")
        dbf2CSV(inSpace+"/CSV/TTOP.dbf")
        dbf2CSV(inSpace+"/CSV/TDP.dbf")
        dbf2CSV(inSpace+"/CSV/TDOP.dbf")
        dbf2CSV(inSpace+"/CSV/DTP.dbf")
        dbf2CSV(inSpace+"/CSV/DTOP.dbf")
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in GISops line %i" % tb.tb_lineno
        print str(e)

if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "E:/DATA_testMP/"
    inGdb = temp
    #inSpeed = "spdtest.csv"
#    SET whether use transit Pre or Post cost
#    Make sure csvs have correct format.
#    oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#    20211000,20211000,0,0
#    20211000,20212000,89.348434,19.777
#    20211000,20213000,135.59612,26.074003
    inTTp = inSpace+"TTpubPre.csv" 
    #inTTp = inSpace+"TTpubPost.csv"

    
    base = inSpace+base
    temp = inSpace+temp
    
    ##TAZs:
    ##    TAZ_LA_proj_centroid  >---< inFlow.csv
    ##    TAZ_LA_TESTSAMPLE (50)  >---< inFlow50.csv
    ##Detectors:
    ##    hd_ML_snap (1800)
    fcTAZ = "TAZ_LA_proj_centroid"
#    fcTAZ = "TAZ_LA_TESTSAMPLE"
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
    startIter = 5
    maxIter = 2
    
    # Off peak commuting penalty
    OPpenalty = 48.4575

    #ACTUAL COMPUTATION START HERE
    # Import necessary modules

    
    
    ssdPath = {}
    currentIter = startIter
    try:
        while currentIter < (maxIter + startIter):
            print "Iteration", currentIter, "starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
            print inTTp, ", at", inSpace
            # 0, create temp scratch
            print "Setting up scratch version"
            tempP = temp[:-4] + "-P" + temp[-4:]
            ModSetupWorker.clearOld(base,tempP)
            tempOP = temp[:-4] + "-OP" + temp[-4:]
            ModSetupWorker.clearOld(base,tempOP)
            print "Scratch version set up.  Proceding..."
            
            print "GIS operations begins."
            GISops(inSpace, inGdb, currentIter, fcTAZ, fcDet)
            print "GIS operations completed."
            
            print "Predicting flow from gravity equation"
            ModUpdateFlow.update_2p(inSpace, currentIter, inTTp, OPpenalty)
        
            print "Flow Allocation"
            inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-P.csv"
            flow_p = ModAlloc.alloc_2p(inSpace, currentIter, "P")
    
            inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-OP.csv"
            flow_op = ModAlloc.alloc_2p(inSpace, currentIter, "OP")        
            
            print "Update Speed"
            ModSpeedCalc_avg10.flow2speed_2p(inSpace, currentIter, FL, LIMIT)
            
            print "Iteration", currentIter, "done on ", time.strftime("%d/%m/%Y - %H:%M:%S")
            currentIter += 1
        
        print maxIter, "EVERYTHING COMPLETED on", time.strftime("%d/%m/%Y - %H:%M:%S")

    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in MAIN_2period_MP line %i" % tb.tb_lineno
        print str(e)

#        Save TT cost calculated from speed0
#        if currentIter == 1:
#            shutil.copyfile(inSpace+'CSV/TT.csv', inSpace+'CSV/TT0.csv')

if __name__ == '__backup__':
    jc1 = mp.Process(target=dbf2CSV, args=(inSpace+"/CSV/TTP.dbf",))
    jc2 = mp.Process(target=dbf2CSV, args=(inSpace+"/CSV/TTOP.dbf",))
    jc3 = mp.Process(target=dbf2CSV, args=(inSpace+"/CSV/TDP.dbf",))
    jc4 = mp.Process(target=dbf2CSV, args=(inSpace+"/CSV/TDOP.dbf",))
    jc5 = mp.Process(target=dbf2CSV, args=(inSpace+"/CSV/DTP.dbf",))
    jc6 = mp.Process(target=dbf2CSV, args=(inSpace+"/CSV/DTOP.dbf",))
    
#    jc1.start()
#    time.sleep(5)
#    jc2.start()
#    time.sleep(5)
#    jc3.start()
#    time.sleep(5)
#    jc4.start()
#    time.sleep(5)
#    jc5.start()
#    time.sleep(5)
#    jc6.start()
#    
#    jc1.join()
#    jc2.join()
#    jc3.join()
#    jc4.join()
#    jc5.join()
#    jc6.join()