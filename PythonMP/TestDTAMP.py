# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 20:15:52 2014

@author: Dennis
"""

import time, shutil, os, sys
import ModSetupWorker, ModSpeedCalc, ModGIS, ModUpdateFlow, ModAlloc
from ModIO import readcsv



def dta_1p(inSpace, inTTflow, fl, limit):
    '''
    This script runs the DTA loop.
    This script also contains the travelcost subfunction
    
    Inputs
    ------
    inSpace     : str
                  Path
    inTTflow    : str
                  Full path to TT flow of current iteration
    fl          : int
                  flow per lane
    limit       : int
                  speed limit
    '''
    import numpy as np

    # XXX Begin sub function block
    def bisection(a, b, tol, x, y, vd):
        '''
        Bisection method to find root.
        hardcoded in objective function as flowGradient,
        and value function as travelcost.
        
        Input
        -----
        a    : value
               min search value
        b    : value
               max search value
        tol  : value
               tolerance
        x,y  : vector
               flow vectors (prev, predicted)
        vd   : vector
               distance vector from AF
        
        Return
        ------
        Alpha of root.               
        '''
        def f(alpha):
            return flowGradient(x, y, alpha, vd)
            
        c = (a+b)/2.0
        while (b-a)/2.0 > tol:
            if f(c) == 0:
                print 'fc=0'
                return c
            elif f(a)*f(c) < 0:
                b = c
            else :
                a = c
            c = (a+b)/2.0
             
        return c
    def flowGradient(x, y, alpha, vdist):
        '''
        Calculate the gradient value based on value function and various inputs
        (y1-x1)*t(x1+a*(y1-x1))
        
        Contains a short, no-output version of flow2spd, and travelcost calculation
        
        Input
        -----
        x          : vector
                     Prev flow
        y          : vector
                     Expected flow
        alpha      : value
                     Alpha value for move.  See Sheffi p. 119.  Supplied from bisection
        vdist      : vector
                     vector of distance from AF reading

        Output
        ------
        Grad(Z)    : Value
                     Value of the gradient, for use in bisection method
        '''
        def flow2spd(x, FL, LIMIT):
            # given x as PER LANE flow, FL, LIMIT, returns the resulting speed.
            from math import exp
            if x > FL:
                return LIMIT * exp(-0.000191*(x-FL))
            else:
                return LIMIT

        def travelcost(x, dist):
            # segment length to be implimented
            vflow2spd = np.vectorize(flow2spd, otypes=[np.float])
#            travelcost = (11.5375 *dist / vflow2spd(x, fl, limit)) + 0.469 * dist
#            travelcost = (1/vflow2spd(x, fl, limit))**4
            travelcost = (65**.2 - vflow2spd(x, fl, limit)**.2)
            return travelcost
            
        grad = (y-x)*travelcost(x+alpha*(y-x), vdist)
        return grad.sum()
    # XXX end sub function block
    try:
        print "bisection starts on ", time.strftime("%H:%M:%S")
        # Create temp speed 
        x1path = "CSV/xdetflow.csv"
        outCSV = "detspd-temp.csv"
        x1spath = outCSV
        ratio_x = ModSpeedCalc.flow2speed(inSpace, x1path, fl, limit, outCSV, dta=True) #detspd-temp.csv
        
        # Perform all or nothing allocation
        print "DTA scratch version"
        ModSetupWorker.clearOld(base,tempP)
    
        print "GIS operation"
        inSpeed = "detspd-temp.csv"
        ModGIS.GISops_dta(inSpace, inGdb, fcTAZ, fcDet, inSpeed) # TT, DT, TD
        
        print "allocation"
        y1path = "CSV/ydetflow.csv"
        # inFlow is global
        
        ModAlloc.alloc(inSpace, inFlow, inSpace+y1path, period = "P") # Gives detflow y1
        outCSV = "ydetspd-temp.csv"
        y1spath = outCSV
        ratio_y = ModSpeedCalc.flow2speed(inSpace, y1path, fl, limit, outCSV=outCSV, dta=True)
        
#        ratio_x = 10.0550935465
#        ratio_y = 10.7308926556
        # Find Alpha
        fdtype = [('idstn','i8'),('flow','f8')]
        x1 = readcsv(inSpace+x1path, fdtype, incol = 2, sort = [0], header = None)
        y1 = readcsv(inSpace+y1path, fdtype, incol = 2, sort = [0], header = None)
        
        inAF = inSpace+"AF.csv"
        fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8'),('dist','f8')]
        af = readcsv(inAF, fdtype, incol = 5, sort=0, header = True)
     
        checksum = x1['idstn'] != y1['idstn']
        print 'number of detectors out of order:', checksum.sum()
        if checksum.sum() > 0:
            raise('OH NOES!!, XY not match')
        checksum = x1['idstn'] != af['idstn']
        print 'number of detectors out of order:', checksum.sum()
        if checksum.sum() > 0:
            print 'OH NOES!!, AF not match'
        vx1 = ratio_x * .06 * x1['flow'] / af['lane']
        vy1 = ratio_y * .06 * y1['flow'] / af['lane']
        vd  = af['dist']
        alfa = bisection(0, 1, 0.0001, vx1, vy1, vd)
        print "bisection result:", alfa       
    
        # Save both the speed and flow for DTA iteration
        x1back = x1path[:-4]+str(alfa)+x1path[-4:]
        y1back = y1path[:-4]+str(alfa)+y1path[-4:]
        shutil.copy(inSpace+x1path,inSpace+x1back)
        shutil.copy(inSpace+y1path,inSpace+y1back)
        x1sback = "CSV/xdetspd"+str(alfa)+".csv"
        y1sback = "CSV/ydetspd"+str(alfa)+".csv"
        shutil.copy(inSpace+x1spath,inSpace+x1sback)
        shutil.copy(inSpace+y1spath,inSpace+y1sback)
    
        # Create det flow x2
        x2flow = x1['flow']+alfa*(y1['flow']-x1['flow'])
        
        x2 = np.copy(x1)
        x2['flow'] = x2flow
        outX2 = inSpace+'CSV/xdetflow.csv'
        np.savetxt(outX2, x2, delimiter=',', fmt='%7.0f, %7.10f')
        
        print "bisection ends on ", time.strftime("%H:%M:%S"), "found alpha =", alfa
        return alfa
    
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in dta_1p line %i" % tb.tb_lineno
        print str(e)    





if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    inSpace = "C:/Users/Dennis/Desktop/DATA/"
#    inSpace = "E:/TestingLab/"
    inGdb = temp

#    SET whether use transit Pre or Post cost
#    Make sure csvs have correct format.
#    oID_TAZ12A,dID_TAZ12A,post_triptime,postcost
#    20211000,20211000,0,0
    inTTp = inSpace+"TTpubPre.csv" 
#    inTTp = inSpace+"TTpubPost.csv"

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
    maxIter = 10
    
    # Off peak commuting penalty
    OPpenalty = 48.4575

    # start with current iteration
    currentIter = startIter
    
    try:
        # Begin looping
        while currentIter < (maxIter + startIter):
            print "Iteration", currentIter, "starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
            print inTTp, ", at", inSpace

            # 0, create temp scratch
            print "Setting up scratch version"
            tempP = temp[:-4] + "-P" + temp[-4:]
            ModSetupWorker.clearOld(base,tempP)
            print "Scratch version set up.  Proceding..."

            print "GIS operations begins."
            ModGIS.GISops_1p(inSpace, inGdb, currentIter, fcTAZ, fcDet)
            print "GIS operations completed."

            print "Predicting flow from gravity equation"
#             Changed ModUpdateFlow line 300 to TTP for now
            ModUpdateFlow.update(inSpace, currentIter, inTTp)    # Gives TTflow1.csv from update (not 2p)

            print "Flow Allocation"
            inFlow = inSpace+"CSV/TTflow"+str(currentIter)+".csv"
            outCSV = inSpace+"CSV/xdetflow.csv"
            ModAlloc.alloc(inSpace, inFlow, outCSV, period="P") # Gives detflow
            
            alpha = 1
#            Loop through DTA:
            savepath = inSpace+"CSV/xdetflow-beforealpha-"+str(currentIter)+".csv"
            shutil.copy(outCSV, savepath)
            while alpha > 0.00999:
                alpha = dta_1p(inSpace, inFlow, FL, LIMIT)
                print "alpha:", alpha
                if alpha > 0.999:
                    shutil.copy(inSpace+"CSV/xdetflow"+str(alpha)+".csv", inSpace+"CSV/xdetflow.csv")
                    break
                
            # Save the proper detflow
            combCSV = inSpace+"CSV/xdetflow.csv"
            outCSV = inSpace+"CSV/detflow"+str(currentIter)+".csv"
            shutil.copy(combCSV, outCSV)
            
            detflow = "CSV/detflow"+str(currentIter)+".csv"
            outCSV = "detspd"+str(currentIter)+"-P.csv"
            fratio = ModSpeedCalc.flow2speed(inSpace, detflow, FL, LIMIT, outCSV, dta=False)
            print "final ratio after dta:", fratio
            currentIter +=1

            
    
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in TestDTA line %i" % tb.tb_lineno
        print str(e)





