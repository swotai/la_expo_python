# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 21:38:08 2014

@author: Dennis
# Purpose: Run modules to do the following:
# 0, Create a temp scratch version of the network dataset for operation
# 1, Update speed, recalculate cost
# 2, rebuild network dataset
# 3, Calculate cost (TT = TD + DT)
# 4, Compute detector level flow
# 5, Compute detector level updated speed using supply side equation

# For Equilibrium calculation

"""

# Name: GIS_Iteration


if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "E:/DATA_Post_fix1028/"
    inGdb = temp
    #inSpeed = "spdtest.csv"
#    SET whether use transit Pre or Post cost
#    Make sure csvs have correct format.
#    oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#    20211000,20211000,0,0
#    20211000,20212000,89.348434,19.777
    inTTp = inSpace+"TTpubPre.csv" 
    inTTp = inSpace+"TTpubPost.csv"

    
    base = inSpace+base
    temp = inSpace+temp
    
    ##TAZs:
    ##    TAZ_LA_proj_centroid  >---< inFlow.csv
    ##    TAZ_LA_TESTSAMPLE (50)  >---< inFlow50.csv
    ##Detectors:
    ##    hd_ML_snap (1800)
    fcTAZ = "TAZ_LA_proj_centroid"
    fcDet = "hd_ML_snap"
    #inFLOW = PREDICTED FLOW FROM GRAVITY (STATIC, OBSELETE), not to confused with AF (Actual Flow)
    #inFLOW.csv at inSpace is used for Pre flow as starting point for iteration.
#    inFlow = inSpace + "inFlow.csv"
    
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
    

    #ACTUAL COMPUTATION START HERE
    # Import necessary modules
    import ModSetupWorker, ModJoinSpeed, ModBuild, ModSolve, ModAlloc, ModSpeedCalc_avg10, ModUpdateFlow
    import time
    
    currentIter = 1
    
    # Pre equilibrium calculation
    print "Pre expo equilibrium calculation starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
    inSpace = "C:/Users/Dennis/Desktop/Pre/"
    inTTp = inSpace+"TTpubPre.csv" 
    inSpeed = "pre_eqm_speed-2130.csv"
    print inTTp, ", at", inSpace, "using speed vector", inSpeed

    # 0, create temp scratch
    print "Setting up scratch version"
    ModSetupWorker.clearOld(base,temp)
    print "Scratch version set up.  Proceding..."

    # 1, update speed, recalculate cost 
    print "Update Speed..."
    ModJoinSpeed.joinSpeed(inSpace, inGdb, inSpeed)

    # 2, rebuild network dataset
    print "Speed updated. Rebuild Dataset..."
    ModBuild.build(inSpace, inGdb)
    
    # 3, solve network
    print "Dataset rebuilt. Solve for TT, TD, DT"
    ModSolve.solve(inSpace, inGdb, fcTAZ, fcDet)

    print "Predicting flow from gravity equation"
    ModUpdateFlow.update(inSpace, currentIter, inTTp)

    print "Flow Allocation"
    inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
    flow = ModAlloc.alloc(inSpace, inFlow, currentIter)

    print "Update Speed"
    ssds = ModSpeedCalc_avg10.flow2speed(inSpace, flow, currentIter, FL, LIMIT)
    
    print "Pre expo equilibrium calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")




    # Post equilibrium calculation
    print "Post expo equilibrium calculation starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
    inSpace = "C:/Users/Dennis/Desktop/Post/"
    inTTp = inSpace+"TTpubPost.csv"
    inSpeed = "pre_eqm_speed-2130.csv"
    print inTTp, ", at", inSpace, "using speed vector", inSpeed

    # 0, create temp scratch
    print "Setting up scratch version"
    ModSetupWorker.clearOld(base,temp)
    print "Scratch version set up.  Proceding..."

    # 1, update speed, recalculate cost 
    print "Update Speed..."
    ModJoinSpeed.joinSpeed(inSpace, inGdb, inSpeed)

    # 2, rebuild network dataset
    print "Speed updated. Rebuild Dataset..."
    ModBuild.build(inSpace, inGdb)
    
    # 3, solve network
    print "Dataset rebuilt. Solve for TT, TD, DT"
    ModSolve.solve(inSpace, inGdb, fcTAZ, fcDet)

    print "Predicting flow from gravity equation"
    ModUpdateFlow.update(inSpace, currentIter, inTTp)

    print "Flow Allocation"
    inFlow = inSpace + "CSV/TTflow" + str(currentIter) + ".csv"
    flow = ModAlloc.alloc(inSpace, inFlow, currentIter)

    print "Update Speed"
    ssds = ModSpeedCalc_avg10.flow2speed(inSpace, flow, currentIter, FL, LIMIT)

    print "Post expo equilibrium calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")

