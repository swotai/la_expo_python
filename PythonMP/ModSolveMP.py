# Name: ModSolve.py
# Description: Setup OD cost matrix, solve for TT, TD, DT costs
#              output cost matrices as CSCV
# Requirements: Network Analyst Extension 
# The following are hard coded:
#        - Name of output csv


from ModRealSolveExp import NAtoCSV
import multiprocessing as mp

def solve(inSpace, inGdb, fcTAZ, fcDet, period):
    '''
    GIS solving single threaded.
    
    Inputs
    -----
    inSpace     : str
                  working directory
    inGdb       : str
                  Name of geodatabase
    fcTAZ       : str
                  Name of TAZ featureclass
    fcDet       : str
                  Name of detector featureclass
    period      : str
                  Period. (either P or OP, caps)
    
    Outputs
    -------
    Cost matrices: TT, TD, DT in DBF format.
    '''
    try:
        #Set local variables
        inNetworkDataset = "Trans/DriveOnly_ND"
        impedanceAttribute = "Cost"
        accumulateAttributeName = "#"
        #accumulateAttributeName = ['Length', 'dps']
        
        #TT COST CALCULATION STARTS HERE
        outNALayerName = "ODTT"
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcTAZ
#        outFile = inSpace+"CSV/TT.csv"
#        outFile = inSpace+"CSV/TT-" + period + ".csv"
        outFile = "TT" + period + ".dbf"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "TT Solved"
                
        
        #TD COST CALCULATION STARTs HERE
        outNALayerName = "ODTD"
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcDet
#        outFile = inSpace+"CSV/TD.csv"
#        outFile = inSpace+"CSV/TD-" + period + ".csv"
        outFile = "TD" + period + ".dbf"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "TD Solved"
        

        #DT COST CALCULATION STARTS HERE
        outNALayerName = "ODTT"
        inOrigins = "Trans/"+fcDet
        inDestinations = "Trans/"+fcTAZ
#        outFile = inSpace+"CSV/DT.csv"
#        outFile = inSpace+"CSV/DT-" + period + ".csv"
        outFile = "DT" + period + ".dbf"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "DT Solved"
        
        print "\n\n Solve: CHECK GDB LOCK NOW!!!"
        
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModSolveMP.solve line %i" % tb.tb_lineno
        print str(e)        


def solve_2p(inSpace, inGdb, fcTAZ, fcDet, period):
    import time 
    queue=mp.Queue()
    try:
        import os
        for dbffile in ["TT"+period+".dbf", "TD"+period+".dbf", "DT"+period+".dbf",
                        "TT"+period+".dbf.XML", "TD"+period+".dbf.XML", "DT"+period+".dbf.XML"]:
            if os.path.exists(inSpace+"CSV/"+dbffile):
                print "removing old", dbffile
                os.remove(inSpace+"CSV/"+dbffile)
        #Set local variables
        inNetworkDataset = "Trans/DriveOnly_ND"
        impedanceAttribute = "Cost"
        accumulateAttributeName = "#"
        #accumulateAttributeName = ['Length', 'dps']
        
        #TT COST CALCULATION STARTS HERE
        outNALayerName = "ODTT"+period
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcTAZ
#        outFile = inSpace+"CSV/TT-" + period + ".csv"
        outFile = "TT" + period + ".dbf"
        Gdb = inGdb[:-4] + "1" + inGdb[-4:]
        j_solve_01 = mp.Process(target=NAtoCSV, args = (inSpace, Gdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile,queue))
#        j_solve_01.daemon = True
        ttpath = inSpace+"CSV/"+outFile
        
        #TD COST CALCULATION STARTs HERE
        outNALayerName = "ODTD"+period
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcDet
#        outFile = inSpace+"CSV/TD-" + period + ".csv"
        outFile = "TD" + period + ".dbf"
        Gdb = inGdb[:-4] + "2" + inGdb[-4:]
        j_solve_02 = mp.Process(target=NAtoCSV, args = (inSpace, Gdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile,queue))
#        j_solve_02.daemon = True
        tdpath = inSpace+"CSV/"+outFile

        #DT COST CALCULATION STARTS HERE
        outNALayerName = "ODDT"+period
        inOrigins = "Trans/"+fcDet
        inDestinations = "Trans/"+fcTAZ
#        outFile = inSpace+"CSV/DT-" + period + ".csv"
        outFile = "DT" + period + ".dbf"
        Gdb = inGdb[:-4] + "3" + inGdb[-4:]
        j_solve_03 = mp.Process(target=NAtoCSV, args = (inSpace, Gdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile,queue))
#        j_solve_03.daemon = True
        dtpath = inSpace+"CSV/"+outFile
        
        j_solve_01.start()
        time.sleep(10)
        j_solve_02.start()
        time.sleep(10)
        j_solve_03.start()
        time.sleep(10)
        oj = queue.get()
        j_solve_01.join()
        j_solve_02.join()
        j_solve_03.join()
        
        for j in [j_solve_01, j_solve_02, j_solve_03]:
            print '%s.exitcode = %s' % (j.name, j.exitcode)
        print "oj",oj
        # Check filesize.  If any file fail to output after join, recompute.
        # Typical file size at least 600Mb, TT ~ 800Mb
        # if fail to output usually dbf has zero byte.
        import os
        allclear = 0
        while allclear < 3:
            allclear = 3
            if (not os.path.exists(ttpath)) or os.path.getsize(ttpath) < 600e6:
                #kill prev job
                print ttpath, "size:", os.path.getsize(ttpath)
                print "TT matrix error: recompute"
                j_solve_01.terminate()
                del j_solve_01
                outNALayerName = "ODTT"+period
                inOrigins = "Trans/"+fcTAZ
                inDestinations = "Trans/"+fcTAZ
                outFile = "TT" + period + ".dbf"
                Gdb = inGdb[:-4] + "1" + inGdb[-4:]
                j_solve_01 = mp.Process(target=NAtoCSV, args = (inSpace, Gdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile,queue))
                j_solve_01.start()
                allclear -=1
            if (not os.path.exists(tdpath)) or os.path.getsize(tdpath) < 600e6:
                #kill prev job
                print tdpath, "size:", os.path.getsize(tdpath)
                print "TD matrix error: recompute"
                j_solve_02.terminate()
                del j_solve_02
                outNALayerName = "ODTD"+period
                inOrigins = "Trans/"+fcTAZ
                inDestinations = "Trans/"+fcDet
                outFile = "TD" + period + ".dbf"
                Gdb = inGdb[:-4] + "2" + inGdb[-4:]
                j_solve_02 = mp.Process(target=NAtoCSV, args = (inSpace, Gdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile,queue))
                j_solve_02.start()
                allclear -=1
            if (not os.path.exists(dtpath)) or os.path.getsize(dtpath) < 600e6:
                #kill prev job
                print "DT matrix error: recompute"
                j_solve_03.terminate()
                del j_solve_03
                outNALayerName = "ODDT"+period
                inOrigins = "Trans/"+fcDet
                inDestinations = "Trans/"+fcTAZ
                outFile = "DT" + period + ".dbf"
                Gdb = inGdb[:-4] + "3" + inGdb[-4:]
                j_solve_03 = mp.Process(target=NAtoCSV, args = (inSpace, Gdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile,queue))
                j_solve_03.start()
                allclear -=1
            oj = queue.get()
            j_solve_01.join()
            j_solve_02.join()
            j_solve_03.join()
            
        
        
        
        
        print "\n Solve completed for period", period
        return 1
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModSolveMP.solve_2p line %i" % tb.tb_lineno
        print str(e)
        pass
    

        