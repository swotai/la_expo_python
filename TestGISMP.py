# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 00:12:28 2014

@author: Dennis
"""
import ModSetupWorker, ModGIS, time
if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "E:/TestingLab/"
    inGdb = temp

#    SET whether use transit Pre or Post cost
#    Make sure csvs have correct format.
#    oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#    20211000,20211000,0,0
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
    fcTAZ = "TAZ_LA_TESTSAMPLE"
    fcDet = "hd_ML_snap"
    #inFLOW = PREDICTED FLOW FROM GRAVITY (STATIC), not to confused with AF (Actual Flow)
    #probably used as placeholder
    #TODO: See if still needed.
#    inFlow = inSpace + "inFlow.csv"
    

    #For Allocation
    LIMIT = 65
    FL = 500
    
    # The way this is coded, if an iteraction is completed
    # i.e. with the speed outputed, the code can start from there.
    # Change the currentIter to the max number of detspd +1
    startIter = 1
    maxIter = 1
    
    # Off peak commuting penalty
    OPpenalty = 48.4575

    # start with current iteration
    currentIter = startIter
    
    try:
        # Begin looping
        while currentIter < 2:
            print "Iteration", currentIter, "starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
            print inTTp, ", at", inSpace
    
            # 0, create temp scratch
            print "Setting up scratch version"
            tempP = temp[:-4] + "-P" + temp[-4:]
            ModSetupWorker.clearOld(base,tempP)
            print "Scratch version set up.  Proceding..."
    
            print "GIS operations begins."
            ModGIS.GISops_MP(inSpace, inGdb, currentIter, fcTAZ, fcDet)
            print "GIS operations completed."
            currentIter +=1
            
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in TestDTA line %i" % tb.tb_lineno
        print str(e)