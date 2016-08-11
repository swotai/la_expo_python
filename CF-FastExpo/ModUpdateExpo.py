# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 15:05:18 2015

@author: Dennis

Updates Metro speed by supplying inSpeed as integer
Base on AddFieldFromJoin.py
Description: Change the "Speed" field, recaucluates DPS field, 
VOT = 21.46  !!! Don't change VOT HERE!!! VOT is updated/calculated afterwards in Stata
"""

def joinSpeed(inSpace, inGdb, inSpeed):
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
        inBlue = inGdb + "/Trans/BlueLine_Split"
        inExpo = inGdb + "/Trans/ExpoLine_Split"
        inGold = inGdb + "/Trans/GoldLine_Split"
        inGreen= inGdb + "/Trans/GreenLine_Split"
        inRed  = inGdb + "/Trans/RedLine_Split"

        layerBlue = "BlueL"
        layerExpo = "ExpoL"
        layerGold = "GoldL"
        layerGreen= "GreenL"
        layerRed  = "RedL"

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
        arcpy.MakeFeatureLayer_management (inBlue, layerBlue)
        arcpy.MakeFeatureLayer_management (inExpo, layerExpo)
        arcpy.MakeFeatureLayer_management (inGold, layerGold)
        arcpy.MakeFeatureLayer_management (inGreen, layerGreen)
        arcpy.MakeFeatureLayer_management (inRed, layerRed)
        
        # Update speed with new speed
        print "Update Metro speed to", inSpeed, "mph"
        #arcpy.CalculateField_management (inBlue, "avgspd", inSpeed, "PYTHON")
        arcpy.CalculateField_management (inExpo, "avgspd", inSpeed, "PYTHON")
        #arcpy.CalculateField_management (inGold, "avgspd", inSpeed, "PYTHON")
        #arcpy.CalculateField_management (inGreen, "avgspd", inSpeed, "PYTHON")
        #arcpy.CalculateField_management (inRed, "avgspd", inSpeed, "PYTHON")
        
        # Calculate new travel time        
        print "Update travel time (DPS)"
        arcpy.CalculateField_management (inBlue, "DPS", "!TotalLengt! / !avgspd!", "PYTHON")
        arcpy.CalculateField_management (inExpo, "DPS", "!TotalLengt! / !avgspd!", "PYTHON")
        arcpy.CalculateField_management (inGold, "DPS", "!TotalLengt! / !avgspd!", "PYTHON")
        arcpy.CalculateField_management (inGreen, "DPS", "!TotalLengt! / !avgspd!", "PYTHON")
        arcpy.CalculateField_management (inRed, "DPS", "!TotalLengt! / !avgspd!", "PYTHON")

        # Calculate new cost base on expression
        print "Update trip cost"
        arcpy.CalculateField_management (inBlue, "Cost", "!DPS!*15", "PYTHON")
        arcpy.CalculateField_management (inExpo, "Cost", "!DPS!*15", "PYTHON")
        arcpy.CalculateField_management (inGold, "Cost", "!DPS!*15", "PYTHON")
        arcpy.CalculateField_management (inGreen, "Cost", "!DPS!*15", "PYTHON")
        arcpy.CalculateField_management (inRed, "Cost", "!DPS!*15", "PYTHON")
        
        # Stop the edit operation.
        edit.stopOperation()
        
        # Stop the edit session and save the changes
        edit.stopEditing(True)
                
        # THIS IS WHAT LOCKS THE GDB UP!!!!~~~~ YAY FOR FINDING THIS!!~!
        arcpy.Delete_management(layerBlue)
        arcpy.Delete_management(layerExpo)
        arcpy.Delete_management(layerGold)
        arcpy.Delete_management(layerGreen)
        arcpy.Delete_management(layerRed)
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