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
import ModSetupWorker, ModGIS, ModAlloc, ModSpeedCalc_avg10, ModUpdateFlow, time


def dta_1p(inSpace, currentIter, ratio, FL, limit):
    from ModBisec import readcsv, bisection, flowGradient
    
    # Read AF
    inAF = inSpace+"AF.csv"
    fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8')]
    af = readcsv(inAF, fdtype, incol = 4, sort=0, header = True)

    # Read initial flow vector
    cff_init = inSpace+"CSV/detflow"+str(currentIter)+"-P.csv"
    fdtype = [('idstn','i8'),('flow','f8')]
    cff_init = readcsv(cff_init, fdtype, incol = 2, sort = [0], header = None)

    aft = af['center']*af['flow']
    aft = aft.sum()
    cft = af['center']*cff_init['flow']
    cft = cft.sum()
    ratio = aft/(cft)
    print "AF/GF Ratio:", ratio

#    Procedure for new flow
    alpha = 1
    
    while alpha > 0.001:
        1, Update (Recalculate speed)
        2, Direction (Predict Flow)
        3, Determine step (find out alpha)
        4, Move (Change flow)
    cff_op = inSpace+"detflow_adj"+str(currentIter)+".csv"
    fdtype = [('idstn','i8'),('flow','f8')]
    x1 = readcsv(cff_op, fdtype, incol = 2, sort = [0], header = None)
    
    cff_op = inSpace+"detflow_adj"+str(currentIter+1)+".csv"
    fdtype = [('idstn','i8'),('flow','f8')]
    y1 = readcsv(cff_op, fdtype, incol = 2, sort = [0], header = None)

    
    # Make sure the idstn align
    checksum = x1['idstn'] != y1['idstn']
    print 'number of detectors out of order:', checksum.sum()
    if checksum.sum() > 0:
        print 'OH SHIT'

    # Extract Flow
    x1 = x1['flow']
    y1 = y1['flow']
    
    # Convert to per lane flow for speed equation
    # cff_p['flow'] = ratio*0.12*(cff_p['flow'])/af['lane']
    x1 = ratio * .06 * x1 / af['lane']
    y1 = ratio * .06 * y1 / af['lane']
    
    alpha = bisection(0,1,0.0001, flowGradient, x1, y1, FL, LIMIT)
    print "solved alpha:", alpha
    
    print "new flow"
    x2 = x1+alpha*(y1-x1)

    return NEWFLOW



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
    startIter = 1
    maxIter = 1
    
    # Off peak commuting penalty
    OPpenalty = 48.4575


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
#            tempOP = temp[:-4] + "-OP" + temp[-4:]
#            ModSetupWorker.clearOld(base,tempOP)
            print "Scratch version set up.  Proceding..."
            
            print "GIS operations begins."
            ModGIS.GISops_1p(inSpace, inGdb, currentIter, fcTAZ, fcDet)
            print "GIS operations completed."
            
            print "Predicting flow from gravity equation"
#            ModUpdateFlow.update_2p(inSpace, currentIter, inTTp, OPpenalty)
            ModUpdateFlow.update(inSpace, currentIter, inTTp)
            # GIVES TTFLOW-ITER.csv
            print "Flow Allocation"
            inFlow = inSpace+"CSV/TTflow"+str(currentIter)+".csv"
            flow_p = ModAlloc.alloc_2p(inSpace, currentIter, "")

            inFlow = inSpace+"CSV/TTflow"+str(currentIter)+"-OP.csv"
            flow_op = ModAlloc.alloc_2p(inSpace, currentIter, "OP")        

            # TODO: Do mix flow loop here
            # Each iteration of currentIter run couple iteration of DTA
            dta_1p

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

