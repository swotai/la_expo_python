# Name: ModSolve.py
# Description: Setup OD cost matrix, solve for TT, TD, DT costs
#              output cost matrices as CSCV
# Requirements: Network Analyst Extension 
# The following are hard coded:
#        - Name of output csv


from ModRealSolveExp import NAtoCSV
import time

def solve(inSpace, inGdb, fcTAZ, fcDet):
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
        outFile = inSpace+"CSV/TT.csv"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "TT Solved"
                
        
        #TD COST CALCULATION STARTs HERE
        outNALayerName = "ODTD"
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcDet
        outFile = inSpace+"CSV/TD.csv"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "TD Solved"
        

        #DT COST CALCULATION STARTS HERE
        outNALayerName = "ODDT"
        inOrigins = "Trans/"+fcDet
        inDestinations = "Trans/"+fcTAZ
        outFile = inSpace+"CSV/DT.csv"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "DT Solved"
        
        print "\n\n Solve: CHECK GDB LOCK NOW!!!"
        
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModSolve line %i" % tb.tb_lineno
        print str(e)        


def solve_2p(inSpace, inGdb, fcTAZ, fcDet, period):
    try:
        
        #Set local variables
        inNetworkDataset = "Trans/DriveOnly_ND"
        impedanceAttribute = "Cost"
        accumulateAttributeName = "#"
        #accumulateAttributeName = ['Length', 'dps']
        
        #TT COST CALCULATION STARTS HERE
        outNALayerName = "ODTT"+period
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcTAZ
        outFile = inSpace+"CSV/TT-" + period + ".csv"
        outFile = "TT-" + period + ".dbf"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "TT Solved"
                
        
        #TD COST CALCULATION STARTs HERE
        outNALayerName = "ODTD"+period
        inOrigins = "Trans/"+fcTAZ
        inDestinations = "Trans/"+fcDet
        outFile = inSpace+"CSV/TD-" + period + ".csv"
        outFile = "TD-" + period + ".dbf"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "TD Solved"
        

        #DT COST CALCULATION STARTS HERE
        outNALayerName = "ODDT"+period
        inOrigins = "Trans/"+fcDet
        inDestinations = "Trans/"+fcTAZ
        outFile = inSpace+"CSV/DT-" + period + ".csv"
        outFile = "DT-" + period + ".dbf"
        NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
        print "DT Solved"
        
        print "\n\n Solve: CHECK GDB LOCK NOW!!!"
        
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModSolve line %i" % tb.tb_lineno
        print str(e)        
