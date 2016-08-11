# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 16:01:32 2015

@author: SWOT
"""

def NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeName, inOrigins, inDestinations, outNALayerName, outFile, outField):
    '''
    Same as NAtoCSV, but removed "oneway" since Transit network doesnot have this attribute
    Also changed the SNAP code to "ions" for all stations
    '''
    fields = outField
    import arcpy
    from arcpy import env
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
        oriField = "Name PlotID #"
        oriSort = "PlotID"
        destField = "Name PlotID #"
        destSort = "PlotID"
        searchTAZ   = "Rail NONE;WalkRoad SHAPE;RailStn NONE;Transit_ND_Junctions NONE"
        print "Origins: ", inOrigins, " Destinations: ", inDestinations
        arcpy.AddLocations_na(outNALayer, originsLayerName, inOrigins,
                              oriField, sort_field = oriSort, append = "CLEAR", search_criteria = searchTAZ)
        print "loaded stations onto network"

        arcpy.AddLocations_na(outNALayer, destinationsLayerName, inDestinations,
                              destField, sort_field = destSort, append = "CLEAR", search_criteria = searchTAZ)    
        print "loaded stations onto network"
        
        #Solve the OD cost matrix layer
        print "Begin Solving"
        arcpy.na.Solve(outNALayer)
        print "Done Solving"
        
        # Extract lines layer, export to CSV
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
        print "An error occurred in NAtoCSV_Trans line %i" % tb.tb_lineno
        print str(e)        

    finally:
        #Check the network analyst extension license back in, regardless of errors.
        arcpy.CheckInExtension("Network")
    

def solvetransTT(inSpace, inNetwork, inGdb, fcTAZ, outname):
    '''
    Solves TD and DT, given fcTAZ and fcDet
    '''
    #Set local variables
    inNetworkDataset = inNetwork
    impedanceAttribute = "Cost"
    # accumulateAttributedt = "#" << Use this if no need to accumulate
    accumulateAttributeTT = ['Length', 'Cost', 'dist_rail', 'dist_walk', 'time']
    FieldsTT = ["OriginID", "DestinationID", "Name", "Total_Cost", 'Total_Length', 'Total_dist_walk', 'Total_dist_rail', 'Total_time']
    
    #TT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = fcTAZ
    inDestinations = fcTAZ
    outFile = inSpace+outname
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeTT, inOrigins, inDestinations, outNALayerName, outFile, FieldsTT)
    print "TT Solved"
    
def solvedrvTT(inSpace, inNetwork, inGdb, fcTAZ, outname):
    '''
    Solves TD and DT, given fcTAZ and fcDet
    '''
    #Set local variables
    inNetworkDataset = inNetwork
    impedanceAttribute = "Cost"
    # accumulateAttributedt = "#" << Use this if no need to accumulate
    accumulateAttributeTT = ['Length', 'Cost', 'dist_hwy', 'dist_road', 'time']
    FieldsTT = ["OriginID", "DestinationID", "Name", "Total_Cost", 'Total_Length', 'Total_dist_hwy', 'Total_dist_road', 'Total_time']
    
    #TT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = fcTAZ
    inDestinations = fcTAZ
    outFile = inSpace+outname
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeTT, inOrigins, inDestinations, outNALayerName, outFile, FieldsTT)
    print "TT Solved"