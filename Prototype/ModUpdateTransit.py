# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 15:05:18 2015

@author: Dennis

Updates Metro speed by supplying inSpeed as integer
Base on AddFieldFromJoin.py
Description: Change the "Speed" field, recaucluates DPS field, 
VOT = 15.  
"""

def joinSpeed(inSpace, inGdb, inSpeed, VOT):
    '''
    Upates the speed of five metro lines (Blue, Expo, Gold, Green, Red) 
    to the desired speed (inSpeed) at the specified GDB location.
    '''
    try:
        import arcpy, os
        from arcpy import env
        arcpy.env.overwriteOutput = True

        # set the environments
        env.workspace = inSpace
        env.qualifiedFieldNames = "UNQUALIFIED"
        
        # Define script parameters
        inRail = inGdb + "/Transitbase/Rail"

        layerRail = "ProtoRail"

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

        # Create a feature layer from the vegtype featureclass
        arcpy.MakeFeatureLayer_management (inRail, layerRail)
        
        # Update speed with new speed
        print "Update Metro speed to", inSpeed, "mph"
        arcpy.CalculateField_management (inRail, "speed", inSpeed, "PYTHON")
        
        # Calculate new cost base on expression
        print "Update trip cost"
        costvalue = "!dist_mile!/!speed!*" + str(VOT)
        arcpy.CalculateField_management (inRail, "cost", costvalue, "PYTHON")
        print "Update trip time"
        timevalue = "!dist_mile!/!speed!"
        arcpy.CalculateField_management (inRail, "time", timevalue, "PYTHON")
        
        # Stop the edit operation.
        edit.stopOperation()
        
        # Stop the edit session and save the changes
        edit.stopEditing(True)
                
        # THIS IS WHAT LOCKS THE GDB UP!!!!~~~~ YAY FOR FINDING THIS!!~!
        arcpy.Delete_management(layerRail)
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
    inSpace = "C:/Users/Dennis/Desktop/Test/"
    inGdb = "LA-scratch.gdb"
    inSpeed = 41
    
    joinSpeed(inSpace,inGdb,inSpeed)