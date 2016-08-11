# Join speed field, update cost.
# Base on AddFieldFromJoin.py
# Description: Adds a field to a table, and calculates its values based
#              on the values in a field from a joined table


def joinSpeed(inSpace, inGdb, inSpeed):
    try:
        import arcpy, os
        from arcpy import env
        arcpy.env.overwriteOutput = True

        # set the environments
        env.workspace = inSpace
        env.qualifiedFieldNames = "UNQUALIFIED"
        
        # Define script parameters
        inFeatures = inGdb + "/Trans/Tiger_2012_LA_FINAL1"
        layerName = "Tiger_layer"
        newSpd = "speed1"
        newCost = "cost"
        joinTable = inSpeed
        joinField = "id_stn"
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

        fc = inSpace + inGdb
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
        arcpy.AddField_management (inFeatures, newSpd, "DOUBLE")
        
        # Create a feature layer from the vegtype featureclass
        arcpy.MakeFeatureLayer_management (inFeatures,  layerName)
        
        # Join the feature layer to a table
        arcpy.AddJoin_management (layerName, joinField, joinTable, joinField, "KEEP_ALL")
        
        print "Copy speed into join"
        # Populate the newly created field with values from the joined table
        arcpy.CalculateField_management (layerName, newSpd, spdExpression, "PYTHON")
        
        # Remove the join
        arcpy.RemoveJoin_management (layerName, inSpeed)
        
        print "Complete join"
        # Calculate new cost base on expression
        arcpy.CalculateField_management (layerName, newCost, costExpression, "PYTHON", codeblock)
        print "Finished calc new cost"
        
        # Stop the edit operation.
        edit.stopOperation()
        
        # Stop the edit session and save the changes
        edit.stopEditing(True)
        
        
        # THIS IS WHAT LOCKS THE GDB UP!!!!~~~~ YAY FOR FINDING THIS!!~!
        arcpy.Delete_management(layerName)
        print "Completed."
        
    except Exception, e:
        print "Exception in ModJoinSpeed"
        print "ArcGIS errors:"
        print arcpy.GetMessages(2)
        print "Other errors:"
        import sys
        tb = sys.exc_info()[2]
        print "Line %i" % tb.tb_lineno
        print e.message
    
if __name__ == "__main__":
    inSpace = "C:/Users/Dennis/Desktop/DATA/"
    inGdb = "LA-scratch.gdb"
    inSpeed = "detspd0.csv"
    
    joinSpeed(inSpace,inGdb,inSpeed)