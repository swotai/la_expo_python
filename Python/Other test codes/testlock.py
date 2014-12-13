# Join speed field, update cost.
# Base on AddFieldFromJoin.py
# Description: Adds a field to a table, and calculates its values based
#              on the values in a field from a joined table

import arcpy, os

from arcpy import env

arcpy.env.overwriteOutput = True

def joinSpeed(inSpace, inGdb, inSpeed):
	try:
		# set the environments
		#env.workspace = "C:/data"
		#env.qualifiedFieldNames = "UNQUALIFIED"
		env.workspace = inSpace
		env.qualifiedFieldNames = "UNQUALIFIED"
		
		# Define script parameters    
		inFeatures = "Habitat_Analysis.gdb/vegtype"
		layerName = "veg_layer"
		newField = "description"
		joinTable = "vegtable.dbf"
		joinField = "HOLLAND95"
		calcExpression = "!vegtable.VEG_TYPE!"
		outFeature = "Habitat_Analysis.gdb/vegjoin335"
		
		inFeatures = inGdb + "/Trans/Tiger_2012_LA_FINAL1"
		layerName = "Tiger_layer"
		newSpd = "speed1"
		newCost = "cost"
		joinTable = inSpeed
		joinField = "id_stn"
		outFeature = inGdb + "/Trans/Tiger_2012_LA_FINAL2"
		# Speed expression
		spdExpression = "!" + inSpeed + ".speed!"
		# Cost expression
		costExpression = "calc(!speed1!,!cost!,!distance!)"
		codeblock = """def calc(inSpd,oldCost,dist):
		if inSpd is None:
			return oldCost
		else:
			newCost = (11.5375 * dist / inSpd + 0.469 * dist)
			return newCost"""

		fc = inSpace + "/" + inGdb
		workspace = os.path.dirname(fc)
		
		# Edit session is required to edit source in a network dataset, so that 
		# arcGIS can compute properly the dirty region for rebuilding.
		# Start an edit session. Must provide the worksapce.
		edit = arcpy.da.Editor(workspace)

		# Edit session is started without an undo/redo stack for versioned data
		#  (for second argument, use False for unversioned data)
		edit.startEditing(False, True)

		# Start an edit operation
		edit.startOperation()

		# Add the new field
		#arcpy.AddField_management (inFeatures, newSpd, "DOUBLE")
		
		# Create a feature layer from the vegtype featureclass
		#arcpy.MakeFeatureLayer_management (inFeatures,  layerName)
		
		# Join the feature layer to a table
		#arcpy.AddJoin_management (layerName, joinField, joinTable, joinField, "KEEP_ALL")
		
		print "Copy speed into join"
		# Populate the newly created field with values from the joined table
		#arcpy.CalculateField_management (layerName, newSpd, spdExpression, "PYTHON")
		
		# Remove the join
		#arcpy.RemoveJoin_management (layerName, inSpeed)
		
		print "Calc new cost"
		# Calculate new cost base on expression
		#arcpy.CalculateField_management (layerName, newCost, costExpression, "PYTHON", codeblock)
		print "Finished calc new cost"
		
		# Stop the edit operation.
		edit.stopOperation()
		
		# Stop the edit session and save the changes
		edit.stopEditing(True)
		
		
	except Exception, e:
		
		print "Exception"
		import traceback, sys
		tb = sys.exc_info()[2]
		print "Line %i" % tb.tb_lineno
		print e.message
		