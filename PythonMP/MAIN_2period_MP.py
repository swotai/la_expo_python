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

import ModSetupWorker, ModGIS, ModAlloc, ModUpdateFlow, ModSpeedCalc_avg10
import time

if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    inSpace = "C:/Users/Dennis/Desktop/DATA3/"
#    inSpace = "E:/DATA_testMP/"
    inGdb = temp
    #inSpeed = "spdtest.csv"
#    SET whether use transit Pre or Post cost
#    Make sure csvs have correct format.
#    oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#    20211000,20211000,0,0
#    20211000,20212000,89.348434,19.777
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
    startIter = 1
    maxIter = 20
    
    # Off peak commuting penalty
    OPpenalty = 48.4575

    #ACTUAL COMPUTATION START HERE
    # Import necessary modules

    
    
    ssdPath = {}
    currentIter = startIter
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
        ModGIS.GISops_2p(inSpace, inGdb, currentIter, fcTAZ, fcDet)
        print "GIS operations completed."
        
        print "Predicting flow from gravity equation"
        ModUpdateFlow.update_2p(inSpace, currentIter, inTTp, OPpenalty)
    
        print "Flow Allocation"
        inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-P.csv"
        flow_p = ModAlloc.alloc_2p(inSpace, currentIter, "P")

        inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-OP.csv"
        flow_op = ModAlloc.alloc_2p(inSpace, currentIter, "OP")        
        
        print "Update Speed"
        ModSpeedCalc_avg10.flow2speed_2p_old(inSpace, currentIter, FL, LIMIT)
        
        print "Iteration", currentIter, "done on ", time.strftime("%d/%m/%Y - %H:%M:%S")
        currentIter += 1
    
    print maxIter, "EVERYTHING COMPLETED on", time.strftime("%d/%m/%Y - %H:%M:%S")

#        Save TT cost calculated from speed0
#        if currentIter == 1:
#            shutil.copyfile(inSpace+'CSV/TT.csv', inSpace+'CSV/TT0.csv')
