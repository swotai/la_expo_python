# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 21:38:08 2014

@author: Dennis
# Purpose: Run modules to do the following:
# 3, Calculate cost (TD + DT)
# 4, Compute station level flow

# For Equilibrium calculation
"""

def NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile):
    import arcpy
    from arcpy import env
    '''
    Same as NAtoCSV, but removed "oneway" since Transit network doesnot have this attribute
    Also changed the SNAP code to "ions" for all stations
    '''
    try:
        #Check out the Network Analyst extension license
        if arcpy.CheckExtension("Network") == "Available":
            arcpy.CheckOutExtension("Network")
        else:
            # Raise a custom exception
            print "Network license unavailable, make sure you have network analyst extension installed."


        #Check out the Network Analyst extension license
        arcpy.CheckOutExtension("Network")

        #Set environment settings
        env.workspace = inSpace + inGdb
        env.overwriteOutput = True

        #Create a new OD Cost matrix layer.
        outNALayer = arcpy.na.MakeODCostMatrixLayer(inNetworkDataset, outNALayerName,
                                                    impedanceAttribute, "#", "#",
                                                    accumulateAttributeName,
                                                    "ALLOW_UTURNS","#","NO_HIERARCHY","#","NO_LINES","#")

        
        #Get the layer object from the result object. The OD cost matrix layer can 
        #now be referenced using the layer object.
        outNALayer = outNALayer.getOutput(0)
        
        #Get the names of all the sublayers within the OD cost matrix layer.
        subLayerNames = arcpy.na.GetNAClassNames(outNALayer)

        #Stores the layer names that we will use later
        originsLayerName = subLayerNames["Origins"]
        destinationsLayerName = subLayerNames["Destinations"]
        linesLayerName = subLayerNames["ODLines"]
        
        #Adjust field names
        #Exploit the fact that the detector feature is named hd_ML_snap, (or AllStationsML)
        #change the field mapping of Name to id_stn
        oriField = "Name ID_TAZ12A #"
        oriSort = "ID_TAZ12A"
        destField = "Name ID_TAZ12A #"
        destSort = "ID_TAZ12A"
        if inOrigins[-4:] == "nsML":
            oriField = "Name id_stn #"
            oriSort = "id_stn"
        
        if inDestinations[-4:] == "nsML":
            destField = "Name id_stn #"
            destSort = "id_stn"

        #Add locations
        arcpy.AddLocations_na(outNALayer, originsLayerName, inOrigins,
                              oriField, sort_field = oriSort, append = "CLEAR")
        arcpy.AddLocations_na(outNALayer, destinationsLayerName, inDestinations,
                              destField, sort_field = destSort, append = "CLEAR")    
        
        #Solve the OD cost matrix layer
        print "Begin Solving"
        arcpy.na.Solve(outNALayer)
        print "Done Solving"
        
        
        # Extract lines layer, export to CSV
        # SOMEHOW THIS WORKS, SO LETS KEEP IT THAT WAY
        fields = ["OriginID", "DestinationID", "Name", "Total_Cost", 'Total_Length', 'Total_lenmetro', 'Total_lenbus', 'Total_lenwalk', 'Total_lblue', 'Total_lred', 'Total_lgreen', 'Total_lgold', 'Total_lexpo']
        for lyr in arcpy.mapping.ListLayers(outNALayer):
            if lyr.name == linesLayerName:
                with open(outFile, 'w') as f:
                    #f.write(','.join(fields)+'\n') # csv headers
                    with arcpy.da.SearchCursor(lyr, fields) as cursor:
                        print "Successfully created lines searchCursor.  Exporting to " + outFile
                        for row in cursor:
                            f.write(','.join([str(r) for r in row])+'\n')
        
        # Deleteing using del outNALayer is not enough.  Need to delete within arcpy to release
        arcpy.Delete_management(outNALayer)
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModRealSolve line %i" % tb.tb_lineno
        print str(e)        


    finally:
        #Check the network analyst extension license back in, regardless of errors.
        arcpy.CheckInExtension("Network")

def solvetrans(inSpace, inNetwork, inGdb, fcTAZ, fcDet):

    '''
    Solves TD and DT, given fcTAZ and fcDet
    '''
    #Set local variables
    inNetworkDataset = "Trans/"+inNetwork
    impedanceAttribute = "Cost"
    accumulateAttributeName = "#"
    accumulateAttributeName = ['Length', 'lenmetro', 'lenbus', 'lenwalk', 'lblue', 'lred', 'lgreen', 'lgold', 'lexpo']

    #TT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = "Trans/"+fcTAZ
    inDestinations = "Trans/"+fcTAZ
    outFile = inSpace+"CSV/TT.csv"
#    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
    print "TT Solved"

    #TD COST CALCULATION STARTs HERE
    outNALayerName = "ODTD"
    inOrigins = "Trans/"+fcTAZ
    inDestinations = "Trans/"+fcDet
    outFile = inSpace+"CSV/TD.csv"
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
    print "TD Solved"


    #DT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = "Trans/"+fcDet
    inDestinations = "Trans/"+fcTAZ
    outFile = inSpace+"CSV/DT.csv"
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
    print "DT Solved"

    print "\n\n Solve: CHECK GDB LOCK NOW!!!"
        
# Name: GIS_Iteration


if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "D:/DATA_Post_fix1028/"
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
    fcDet = "AllStationsML"
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
    import ModSetupWorker, ModBuild
    import time
    
    currentIter = 1
    
    # Pre equilibrium calculation
#    print "Pre transit calculation starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
#    inSpace = "C:/Users/Dennis/Desktop/TransitPre/"
#
#    # Specify the transit gdb
#    base = "LA_MetroPreBus-DPS.gdb"
#    temp = "LA-scratch.gdb"
#    inGdb = temp
#    base = inSpace+base
#    temp = inSpace+temp
#    inNetwork = "PreBusDPS_ND"
#
#
#    # 0, create temp scratch
#    print "Setting up scratch version"
#    ModSetupWorker.clearOld(base,temp)
#    print "Scratch version set up.  Proceding..."
#
#    # 2, rebuild network dataset
#    print "Speed updated. Rebuild Dataset..."
#    ModBuild.buildTrans(inSpace, inNetwork, inGdb)
#    
#    # 3, solve network
#    print "Dataset rebuilt. Solve for TT, TD, DT"
#    solvetrans(inSpace, inNetwork, inGdb, fcTAZ, fcDet)
#
#    print "Flow Allocation"
#    inFlow = inSpace + "CSV/TransTTflow" + str(currentIter) + ".csv"
##    flow = ModAlloc.alloc_trans(inSpace, inFlow, currentIter)
#
#    print "Pre transit calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")




#    # Post equilibrium calculation
    print "Post transit calculation starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
    inSpace = "C:/Users/Dennis/Desktop/TransitPost/"

    # Specify the transit gdb
    base = "LA_MetroPostBus-DPS.gdb"
    temp = "LA-scratch.gdb"
    inGdb = temp
    base = inSpace+base
    temp = inSpace+temp
    inNetwork = "PostBusDPS_ND"
    
    # 0, create temp scratch
    print "Setting up scratch version"
    ModSetupWorker.clearOld(base,temp)
    print "Scratch version set up.  Proceding..."

    # 2, rebuild network dataset
    print "Speed updated. Rebuild Dataset..."
    ModBuild.buildTrans(inSpace, inNetwork, inGdb)
    
    # 3, solve network
    print "Dataset rebuilt. Solve for TT, TD, DT"
    solvetrans(inSpace, inNetwork, inGdb, fcTAZ, fcDet)

    print "Flow Allocation"
    inFlow = inSpace + "CSV/TransTTflow" + str(currentIter) + ".csv"
#    flow = ModAlloc.alloc_trans(inSpace, inFlow, currentIter)

    print "Post transit calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")

