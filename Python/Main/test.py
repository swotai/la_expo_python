# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 15:33:32 2015

@author: Dennis
"""

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "ExpoLine_split"
import arcpy

arcpy.CalculateField_management("ExpoLine_split","avgspd",20,"PYTHON","#")