import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True

def NAtoCSV(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile):
    '''
    Core code that calls arcpy to run the solver.
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
        print "Make OD in:", inGdb
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
        print "Begin Solving for", outFile[:-4]
        arcpy.na.Solve(outNALayer)
        print "Done Solving for", outFile[:-4]
        
        
        # Extract lines layer, export to CSV
        # SOMEHOW THIS WORKS, SO LETS KEEP IT THAT WAY
#        fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
        for lyr in arcpy.mapping.ListLayers(outNALayer):
            if lyr.name == linesLayerName:
                print "found linelayer.  Exporting to", inSpace+"CSV/"+outFile
                arcpy.TableToTable_conversion(lyr, inSpace+"CSV/", outFile)
#                with open(outFile, 'w') as f:
#                    #f.write(','.join(fields)+'\n') # csv headers
#                    with arcpy.da.SearchCursor(lyr, fields) as cursor:
#                        print "Successfully created lines searchCursor.  Exporting to " + outFile
#                        for row in cursor:
#                            f.write(','.join([str(r) for r in row])+'\n')
        
        print "output completed:", inSpace+"CSV/"+outFile
        # Deleteing using del outNALayer is not enough.  Need to delete within arcpy to release
#        arcpy.Delete_management(outNALayer)

        return 1
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModRealSolveExp line %i" % tb.tb_lineno
        print str(e)        


    finally:
        #Check the network analyst extension license back in, regardless of errors.
        arcpy.CheckInExtension("Network")

if __name__ == '__main__':
    
    temp = "LA-scratch-P.gdb"
    #inSpace = "C:/Users/Dennis/Desktop/DATA1/"
    inSpace = "E:/DATA_testMP/"
    inGdb = temp
    inNetworkDataset = "Trans/DriveOnly_ND"
    impedanceAttribute = "Cost"
    accumulateAttributeName = "#"
    #accumulateAttributeName = ['Length', 'dps']
    fcTAZ = "TAZ_LA_TESTSAMPLE"
    fcDet = "hd_ML_snap"

    #TT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = "Trans/"+fcTAZ
    inDestinations = "Trans/"+fcTAZ
    outFile = inSpace+"CSV/TT.csv"

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
        fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
        for lyr in arcpy.mapping.ListLayers(outNALayer):
            if lyr.name == linesLayerName:
                arcpy.TableToTable_conversion(lyr, inSpace+"FIGS/", "test.dbf")
#                with open(outFile, 'w') as f:
#                    #f.write(','.join(fields)+'\n') # csv headers
#                    with arcpy.da.SearchCursor(lyr, fields) as cursor:
#                        print "Successfully created lines searchCursor.  Exporting to " + outFile
#                        for row in cursor:
#                            f.write(','.join([str(r) for r in row])+'\n')
        
        # Deleteing using del outNALayer is not enough.  Need to delete within arcpy to release
        arcpy.Delete_management(outNALayer)
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import traceback, sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModRealSolve line %i" % tb.tb_lineno
        print str(e)        