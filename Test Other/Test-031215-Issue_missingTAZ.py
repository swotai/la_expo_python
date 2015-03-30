# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 17:00:32 2015

@author: Dennis
"""

'''
Same as NAtoCSV, but removed "oneway" since Transit network doesnot have this attribute
Also changed the SNAP code to "ions" for all stations
'''

inSpace = "C:/Users/Dennis/Desktop/TransitPre/"

# Specify the transit gdb
base = "LA_MetroPreBus-DPS.gdb"
temp = "LA-scratch.gdb"
inGdb = temp
base = inSpace+base
temp = inSpace+temp
inNetwork = "PreBusDPS_ND"
    
##TAZs:
##    TAZ_LA_proj_centroid  >---< inFlow.csv
##    TAZ_LA_TESTSAMPLE (50)  >---< inFlow50.csv
##Detectors:
##    hd_ML_snap (1800)
##Stations:
##    ??? (20?)
fcTAZ = "TAZ_LA_proj_centroid"
fcDet = "AllStationsML1"





inNetworkDataset = "Trans/"+inNetwork
impedanceAttribute = "Cost"
#    accumulateAttributedt = "#"
accumulateAttributeTT = ['Length', 'Cost', 'DPS', 'lenmetro', 'lenbus', 'lenwalk', 'lblue', 'lred', 'lgreen', 'lgold', 'lexpo', 'lorange', 'lsilver']
FieldsTT = ["OriginID", "DestinationID", "Name", "Total_Cost", 'Total_Length', 'Total_DPS', 'Total_lenmetro', 'Total_lenbus', 'Total_lenwalk', 'Total_lblue', 'Total_lred', 'Total_lgreen', 'Total_lgold', 'Total_lexpo']
accumulateAttributeDT = "#"
FieldsDT = ["OriginID", "DestinationID", "Name", "Total_Cost"]
outNALayerName = "ODDT"
inOrigins = "Trans/"+fcDet
inDestinations = "Trans/"+fcTAZ
outFile = inSpace+"CSV/DT.csv"


print "Starting Test"

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
                                            accumulateAttributeTT,
                                            "ALLOW_UTURNS","#","NO_HIERARCHY","#","NO_LINES","#")
print "created OD cost matrix layer"

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
searchMetro = "BlueLine_Split SHAPE;GoldLine_split SHAPE;GreenLine_split SHAPE;LABus_prj NONE;LABus_prj_conn NONE;Metro_Tiger_Conn SHAPE;Orange_Conn SHAPE;OrangeLine_split SHAPE;RedLine_split SHAPE;Silver_Conn SHAPE;SilverLine_split SHAPE;TAZ_Tiger_Conn NONE;tl_2012_LAC_prj NONE;BusStopsWLines_prj NONE;Metro_Tiger_Conn_pt SHAPE;Orange_Conn_pt SHAPE;Silver_Conn_pt SHAPE;PreBusDPS_ND_Junctions NONE"
searchTAZ   = "BlueLine_Split NONE;GoldLine_split NONE;GreenLine_split NONE;LABus_prj NONE;LABus_prj_conn NONE;Metro_Tiger_Conn NONE;Orange_Conn NONE;OrangeLine_split NONE;RedLine_split NONE;Silver_Conn NONE;SilverLine_split NONE;TAZ_Tiger_Conn SHAPE;tl_2012_LAC_prj NONE;BusStopsWLines_prj NONE;Metro_Tiger_Conn_pt NONE;Orange_Conn_pt NONE;Silver_Conn_pt NONE;PreBusDPS_ND_Junctions NONE"
print "Origins: ", inOrigins, " Destinations: ", inDestinations
if "Station" in inOrigins:
    oriField = "Name id_stn #"
    oriSort = "id_stn"
    arcpy.AddLocations_na(outNALayer, originsLayerName, inOrigins,
                          oriField, sort_field = oriSort, append = "CLEAR", search_criteria = searchMetro)
    print "loaded stations onto transit network (search_criteria)"
else:
    arcpy.AddLocations_na(outNALayer, originsLayerName, inOrigins,
                          oriField, sort_field = oriSort, append = "CLEAR", search_criteria = searchTAZ)
    print "loaded stations onto network"

if "Station" in inDestinations:
    destField = "Name id_stn #"
    destSort = "id_stn"
    arcpy.AddLocations_na(outNALayer, destinationsLayerName, inDestinations,
                          destField, sort_field = destSort, append = "CLEAR", search_criteria = searchMetro)
    print "loaded stations onto transit network (search_criteria)"
else:
    arcpy.AddLocations_na(outNALayer, destinationsLayerName, inDestinations,
                          destField, sort_field = destSort, append = "CLEAR", search_criteria = searchTAZ)    
    print "loaded stations onto network"

fields = ["Name"]
fieldcount = 0
for lyr in arcpy.mapping.ListLayers(outNALayer):
    if lyr.name == originsLayerName:
        with open(outFile, 'w') as f:
            #f.write(','.join(fields)+'\n') # csv headers
            with arcpy.da.SearchCursor(lyr, fields) as cursor:
                print "Successfully created lines searchCursor.  Counting..."
                for row in cursor:
                    fieldcount+=1
print "Origins loaded: ", fieldcount

fieldcount = 0
for lyr in arcpy.mapping.ListLayers(outNALayer):
    if lyr.name == destinationsLayerName:
        with open(outFile, 'w') as f:
            #f.write(','.join(fields)+'\n') # csv headers
            with arcpy.da.SearchCursor(lyr, fields) as cursor:
                print "Successfully created lines searchCursor.  Counting..."
                for row in cursor:
                    fieldcount+=1
print "Destinations loaded: ", fieldcount


# Let's solve it.  Then see whether everything is solved.
print "Begin Solving"
arcpy.na.Solve(outNALayer, "HALT")
print "Done Solving"

fieldcount = 0
for lyr in arcpy.mapping.ListLayers(outNALayer):
    if lyr.name == linesLayerName:
        with open(outFile, 'w') as f:
            #f.write(','.join(fields)+'\n') # csv headers
            with arcpy.da.SearchCursor(lyr, fields) as cursor:
                print "Successfully created lines searchCursor.  Counting..."
                for row in cursor:
                    fieldcount+=1
print "Lines calculated: ", fieldcount