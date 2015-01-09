# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 21:38:08 2014

@author: Dennis
# Purpose: Run modules to do the following:
# 3, Calculate cost (TD + DT)
# 4, Compute station level flow

# For Equilibrium calculation

"""
from ModIO import readcsv

def alloc_trans(inSpace, inFlow, currentIter):
    '''
    Base on alloc(), but changed the hard coded items for transit matrices
    '''
    import numpy as np
    from math import sqrt

    inTT = inSpace+"CSV/TT.csv"
    inTD = inSpace+"CSV/TD.csv"
    inDT = inSpace+"CSV/DT.csv"
    outCSV = inSpace+'CSV/Transdetflow'+str(currentIter)+'.csv'

    #Test: 50 TAZs, 1813 DET
    #Full: 2241 TAZs, 1813 DETs
    nTAZ = 50
    nDET = 1813

    #fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
    #fields = ["OriginID", "DestinationID", "Name", "Total_Cost", 'Total_Length', 'Total_lenmetro', 'Total_lenbus', 'Total_lenwalk', 'Total_lblue', 'Total_lred', 'Total_lgreen', 'Total_lgold', 'Total_lexpo']
    datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8'),('length','f8'),('metro','f8'),('bus','f8'),('walk','f8'),('blue','f8'),('green','f8'),('red','f8'),('gold','f8'),('expo','f8')]
    #fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
    fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
    
    print "importing various matrices"
    #Read TAZ-TAZ flow
    ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)

    #Read TD cost
    td = readcsv(inTD, datatype, incol = 13, sort = [1,0], header = None)

    #Read DT cost
    dt = readcsv(inDT, datatype, incol = 13, sort = [0,1], header = None)

    #Read TT cost
    tt = readcsv(inTT, datatype, incol = 13, sort = [0,1], header = None)

    nTAZ = int(sqrt(tt.size))
    if nTAZ != sqrt(tt.size):
        print "ERROR: TAZ SIZE NOT SQUARE!"
    if dt.size != td.size:
        print "ERROR: TD and DT SIZE NOT MATCH!"
    nDET = dt.size/nTAZ
    print "import completed, TAZ:", nTAZ, "DET:", nDET

    print "reshaping..."
    ctd = np.reshape(td['cost'],(nDET, nTAZ))
    cdt = np.reshape(dt['cost'],(nDET, nTAZ))
    ndt = np.reshape(dt['name'],(nDET, nTAZ))
    ctt = np.reshape(tt['cost'],(nTAZ, nTAZ))
    ftt = np.reshape(ff['postflow'],(nTAZ, nTAZ))
    #ftt = ftt + ftt.T

    # FLOW MATRIX
    print "begin flow allocation"
    x3 = np.matrix(ctt)
    i = 0
    count = 0
    detFlow = {999999: 0}
    while i < nDET:
        #Extract current detector id_stn
        det = ndt[i,1][0:6]

        # Extract cost vectors
        x1 = np.matrix(ctd[i])
        x1 = x1.T
        x2 = np.matrix(cdt[i])

        tddt=x1+x2

        #Precise matching
        isflow = x3 == tddt

        #Imprecise/Buffer matching, not needed hopefully
#        match = x3 - tddt
#        if int(det) > 90000:
#            isflow = abs(match) < 0.001


        #Element multiply by flow
        flow = np.multiply(isflow, ftt)
        totalflow = flow.sum()
        #print "Current iteration:", i
        if totalflow > 0:
            print "flow:", totalflow
            count +=1
        
        #Record flow in dictionary
        detFlow[det] = totalflow
        i+=1

    del detFlow[999999]
    print "Number of detectors with match:", count

    dtype = [('idstn','i8'),('flow','f8')]
    detFlow= np.array(detFlow.items(), dtype=dtype)

    np.savetxt(outCSV, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
    
    return detFlow





if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "D:/SOMEFOLDER/"
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
    ##Stations:
    ##    ??? (20?)
    fcTAZ = "TAZ_LA_proj_centroid"
    fcDet = "AllStations"
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
    import time
    
    currentIter = 1
    
    # Pre equilibrium calculation
    print "Pre transit calculation starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
    inSpace = "C:/Users/Dennis/Desktop/TransitPre/"
    # Specify the transit gdb
    base = "LA_MetroPreBus-DPS.gdb"
    temp = "LA-scratch.gdb"
    inGdb = temp
    base = inSpace+base
    temp = inSpace+temp
    inNetwork = "PreBusDPS_ND"

	

    print "Flow Allocation"
    inFlow = inSpace + "CSV/TransTTflow" + str(currentIter) + ".csv"
    flow = alloc_trans(inSpace, inFlow, currentIter)

    print "Pre transit calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")
	




