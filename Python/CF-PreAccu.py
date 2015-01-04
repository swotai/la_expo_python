'''
Name: CF-PreAccu
Purpose: Calculate Accumulated miles for TT
'''


def solve(inSpace, inGdb, fcTAZ, fcDet):
    '''
    Solves TT, TD and DT, given fcTAZ and fcDet
    '''

    #Set local variables
    inNetworkDataset = "Trans/DriveOnly_ND"
    impedanceAttribute = "Cost"
    accumulateAttributeName = "#"
    accumulateAttributeName = ['Length']

    #TT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = "Trans/"+fcTAZ
    inDestinations = "Trans/"+fcTAZ
    outFile = inSpace+"CSV/TT.csv"
    NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile)
    print "TT Solved"

def NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile):
    import arcpy
    from arcpy import env
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
                                                "ALLOW_UTURNS","Oneway","NO_HIERARCHY","#","NO_LINES","#")

    
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
    #Exploit the fact that the detector feature is named hd_ML_snap,
    #change the field mapping of Name to id_stn
    oriField = "Name ID_TAZ12A #"
    oriSort = "ID_TAZ12A"
    destField = "Name ID_TAZ12A #"
    destSort = "ID_TAZ12A"
    if inOrigins[-4:] == "snap":
        oriField = "Name id_stn #"
        oriSort = "id_stn"
    
    if inDestinations[-4:] == "snap":
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
    fields = ["OriginID", "DestinationID", "Name", "Total_Cost", "Total_Length"]
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
    
    

if __name__ == '__main__':
    # Parameter settings (mostly paths):
    # NOTE: MAKE SURE inSpace folder HAS ending slash "/"
    base = "DriveOnly_LA.gdb"
    temp = "LA-scratch.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "C:\Users\Dennis\Desktop\Preaccu/"
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
    period = "pre"
    
    base = inSpace+base
    temp = inSpace+temp
    
    ##TAZs:
    ##    TAZ_LA_proj_centroid  >---< inFlow.csv
    ##    TAZ_LA_TESTSAMPLE (50)  >---< inFlow50.csv
    ##Detectors:
    ##    hd_ML_snap (1800)
    fcTAZ = "TAZ_LA_proj_centroid"
    fcDet = "hd_ML_snap"
    #inFLOW = PREDICTED FLOW FROM GRAVITY (STATIC), not to confused with AF (Actual Flow)
    #inFLOW.csv at inSpace is used for Pre flow as starting point for iteration.
    inFlow = inSpace + "inFlow.csv"
    
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
    startIter = 1
    maxIter = 1


    #ACTUAL COMPUTATION START HERE
    # Import necessary modules
    import ModSetupWorker, ModJoinSpeed, ModBuild
    import time
    
    ssdPath = {}
    currentIter = startIter
    print "Iteration", currentIter, "starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
    print inTTp, ", without Transpose, at", inSpace
    # 0, create temp scratch
    print "Setting up scratch version"
    ModSetupWorker.clearOld(base,temp)
    print "Scratch version set up.  Proceding..."

    # 1, update speed, recalculate cost 
    print "Update Speed..."
    inSpeed = "detspd" + str(currentIter - 1) + ".csv"
    ModJoinSpeed.joinSpeed(inSpace, inGdb, inSpeed)

    # 2, rebuild network dataset
    print "Speed updated. Rebuild Dataset..."
    ModBuild.build(inSpace, inGdb)
    
    solve(inSpace, inGdb, fcTAZ, fcDet)
    
    print maxIter, "EVERYTHING COMPLETED on", time.strftime("%d/%m/%Y - %H:%M:%S")



