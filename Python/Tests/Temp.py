# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "Tiger_2012_LA_FINAL2"
arcpy.CalculateField_management("Tiger_2012_LA_FINAL2","test","calc( !cost!)","PYTHON_9.3","""def calc(fieldA):/n    if fieldA > 0:/n        return "True"/n    else:/n        return "False"/n""")



# Name: AttributeSelection.py
# Purpose: Join a table to a featureclass and select the desired attributes

# Import system modules
import arcpy
from arcpy import env

try:
    # Set environment settings
    env.workspace = "C:/data"
    env.qualifiedFieldNames = False
    
    # Set local variables    
    inFeatures = "Habitat_Analysis.gdb/vegtype"
    layerName = "veg_layer"
    joinTable = "vegtable.dbf"
    joinField = "HOLLAND95"
    expression = "vegtable.HABITAT = 1"
    outFeature = "Habitat_Analysis.gdb/vegjoin"
    
    # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management (inFeatures,  layerName)
    
    # Join the feature layer to a table
    arcpy.AddJoin_management(layerName, joinField, joinTable, joinField)
    
    # Select desired features from veg_layer
    arcpy.SelectLayerByAttribute_management(layerName, "NEW_SELECTION", expression)
    
    # Copy the layer to a new permanent feature class
    arcpy.CopyFeatures_management(layerName, outFeature)
    
except Exception, e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "Line %i" % tb.tb_lineno
    print e.message


	
	
	
	
	
	
# Name: BuildNetwork_ex02.py
# Description: Build a network dataset.
# Requirements: Network Analyst Extension 

#Import system modules
import sys
import os
import shutil
import arcpy
from arcpy import env

#Check out the Network Analyst extension license
arcpy.CheckOutExtension("Network")

#Set environment settings
env.workspace = "C:/data/SanFrancisco.gdb"

#Set local variables
inNetworkDataset = "Transportation/Streets_ND"

#Build the network dataset
arcpy.na.BuildNetwork(inNetworkDataset)

#If there are any build errors, they are recorded in a BuildErrors.txt file
#present in the system temp directory. So copy this file to the directory
#containing this script

#First get the path to the system temp directory
tempDir = os.environ.get("TEMP")
if tempDir:
    shutil.copy2(os.path.join(tempDir,"BuildErrors.txt"),sys.path[0])

print "Script completed successfully."




# AddFieldFromJoin.py
# Description: Adds a field to a table, and calculates its values based
#              on the values in a field from a joined table

# Import system modules
import arcpy
from arcpy import env

try:
    # set the environments
    env.workspace = "C:/data"
    env.qualifiedFieldNames = "UNQUALIFIED"
    
    # Define script parameters    
    inFeatures = "Habitat_Analysis.gdb/vegtype"
    layerName = "veg_layer"
    newField = "description"
    joinTable = "vegtable.dbf"
    joinField = "HOLLAND95"
    calcExpression = "!vegtable.VEG_TYPE!"
    outFeature = "Habitat_Analysis.gdb/vegjoin335"
    
    # Add the new field
    arcpy.AddField_management (inFeatures, newField, "TEXT")
    
    # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management (inFeatures,  layerName)
    
    # Join the feature layer to a table
    arcpy.AddJoin_management (layerName, joinField, joinTable, joinField)
    
    # Populate the newly created field with values from the joined table
    arcpy.CalculateField_management (layerName, newField, calcExpression, "PYTHON")
    
    # Remove the join
    arcpy.RemoveJoin_management (layerName, "vegtable")
    
    # Copy the layer to a new permanent feature class
    arcpy.CopyFeatures_management (layerName, outFeature)
    
except Exception, e:
    
    import traceback, sys
    tb = sys.exc_info()[2]
    print "Line %i" % tb.tb_lineno
    print e.message
	
	
	
	
	



# This script runs the Network Analyst module to calculate Total Cost.
# User supply TAZ features and specify the network dataset.
 
import arcpy, csv, time
arcpy.env.overwriteOutput = True
# Check out any necessary licenses
arcpy.CheckOutExtension("Network")
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)
# End hms_string
 
try:
    # Script arguments
    inND = arcpy.GetParameterAsText(0)
    inOD = arcpy.GetParameterAsText(1)
    fcTAZ = arcpy.GetParameterAsText(2)
    outFolder = arcpy.GetParameterAsText(3)
    inSpd1 = arcpy.GetParameterAsText(4)
    inSpd2 = arcpy.GetParameterAsText(5)
    inStep = arcpy.GetParameterAsText(6)

    # Convert inSpd into integer
    inSpd1 = int(inSpd1)
    inSpd2 = int(inSpd2) + 1    # add 1 so that in xrange the last number is also run through
    inStep = int(inStep)

    loopTime = 3  # Loop iteration delay
    timeZero = time.time()
    
    # Progress Bar Init.
    arcpy.SetProgressor("step",
                    "Starting OD cost calculation",
                    inSpd1, inSpd2, inStep)
    time.sleep(loopTime)

    for currentSpeed in xrange(inSpd1, inSpd2, inStep):
        timeStart = time.time()

        # Announcement
        arcpy.AddMessage(">> Begin OD Cost Calculation of speed %d" % (currentSpeed))
        arcpy.SetProgressorLabel("OD Cost Calculation of speed %d" % (currentSpeed))

        # Change Expo speed, recalculate fields
        arcpy.CalculateField_management("ExpoLine_split","avgspd","%d" % (currentSpeed),"PYTHON","#")
        arcpy.CalculateField_management("ExpoLine_split","Cost","[TotalLengt]*21.46/ [avgspd]","VB","#")
        arcpy.CalculateField_management("ExpoLine_split","DPS","[TotalLengt]/ [avgspd]","VB","#")
        arcpy.AddMessage("Expo speed changed to %d, cost and DPS recalculated.  Rebuilding ND." %(currentSpeed))
                
        # Rebuild Network
        arcpy.BuildNetwork_na(inND)
        arcpy.AddMessage("ND Rebuild completed")
        time.sleep(loopTime)
        
        # Add lcoations
        inOrigins = fcTAZ
        inDestinations = fcTAZ
##        arcpy.AddLocations_na(inOD, "Origins", inOrigins,
##                              "Name ID_TAZ12A #;SourceID SourceID #;SourceOID SourceOID #;PosAlong PosAlong #;SideOfEdge SideOfEdge #", append = "CLEAR")
##        arcpy.AddLocations_na(inOD, "Destinations", inDestinations,
##                              "Name ID_TAZ12A #;SourceID SourceID #;SourceOID SourceOID #;PosAlong PosAlong #;SideOfEdge SideOfEdge #", append = "CLEAR")
        #Add using geometries instead.  Should only add 2 min per iteration or 40 min overall
        arcpy.AddLocations_na(inOD, "Origins", inOrigins,
                              "Name ID_TAZ12A #", append = "CLEAR")
        arcpy.AddLocations_na(inOD, "Destinations", inDestinations,
                              "Name ID_TAZ12A #", append = "CLEAR")
        arcpy.AddMessage("Location Added, Proceed to solve.")
        
        # Solve    
        arcpy.Solve_na(inOD,"SKIP","CONTINUE","#")
        arcpy.AddMessage("Solve Completed")
        time.sleep(loopTime)

        # Export to CSV
        linesLayer = inOD + "\\Lines"
        outFile = outFolder + "\\pb%d.csv" % (currentSpeed)
        arcpy.AddMessage("Successfully created lines searchCursor.  Exporting to " + outFile)
        
        fields = [f.name for f in arcpy.ListFields(linesLayer) if f.type <> 'Geometry']
        
        # Remove columns that's not needed
        for i,f in enumerate(fields):
            if f=='ObjectID' or f=='OriginID' or f =='DestinationRank':
                del fields[i]
        # For some reason this has to be redone...
        for i,f in enumerate(fields):
            if f=='DestinationID':
                del fields[i]

        with open(outFile, 'w') as f:
            f.write(','.join(fields)+'\n') # csv headers
            with arcpy.da.SearchCursor(linesLayer, fields) as cursor:
                for row in cursor:
                    f.write(','.join([str(r) for r in row])+'\n')


        timeEnd = time.time()
       
        # Report a success message    
        arcpy.AddMessage("TD Cost completed, File writen to " + outFile)
        arcpy.AddMessage("Current iteration elapsed: {}".format(hms_string(timeEnd - timeStart)))
        arcpy.AddMessage("Total Time elapsed: {}".format(hms_string(timeEnd - timeZero)))
        # Update PBar
        arcpy.SetProgressorPosition(currentSpeed)
        time.sleep(loopTime)


except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    arcpy.AddMessage("An error occured on line %i" % tb.tb_lineno)
    arcpy.AddMessage(str(e))
    
    # Report an error messages
    arcpy.AddError("Could not complete!!!")
 
    # Report any error messages that the Buffer tool might have generated    
    arcpy.AddMessage(arcpy.GetMessages())



