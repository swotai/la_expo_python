# Name: ModBuild.py
# Description: Build network dataset.
# Requirements: Network Analyst Extension 

#Import system modules
import os, shutil, arcpy
from arcpy import env

def build(inSpace, inGdb):
    '''
    Build network dataset < Trans/DriveOnly_ND > at inSpace + inGdb
    '''
    try:
        if arcpy.CheckExtension("Network") == "Available":
            arcpy.CheckOutExtension("Network")
            print "Network checked out"
        else:
            # Raise a custom exception
            print "Network license unavailable, make sure you have network analyst extension installed."
        
        #Set environment settings
        env.workspace = inSpace + inGdb

        #Set local variables
        inNetworkDataset = "Trans/DriveOnly_ND"

        #Build the network dataset
        print "Building"
        arcpy.na.BuildNetwork(inNetworkDataset)
        print "completed"

        #If there are any build errors, they are recorded in a BuildErrors.txt file
        #present in the system temp directory. So copy this file to the directory
        #containing this script

        #First get the path to the system temp directory
        tempDir = os.environ.get("TEMP")
        if tempDir:
            shutil.copy2(os.path.join(tempDir,"BuildErrors.txt"),inSpace+"BuildErrors.txt")

        print "Script completed successfully."
        print "Error log is BuildErrors.txt if there's any error."
        
        
    except:
        print arcpy.GetMessages(2)
        
    finally:
        #Check the network analyst extension license back in, regardless of errors.
        arcpy.CheckInExtension("Network")
  
def buildTrans(inSpace, inNetwork, inGdb):
    '''
    Build network dataset < Trans/inNetwork > at inSpace + inGdb
    '''
    try:
        if arcpy.CheckExtension("Network") == "Available":
            arcpy.CheckOutExtension("Network")
            print "Network checked out"
        else:
            # Raise a custom exception
            print "Network license unavailable, make sure you have network analyst extension installed."
        
        #Set environment settings
        env.workspace = inSpace + inGdb

        #Set local variables
        inNetworkDataset = inNetwork

        #Build the network dataset
        print "Building"
        arcpy.na.BuildNetwork(inNetworkDataset)
        print "completed"

        #If there are any build errors, they are recorded in a BuildErrors.txt file
        #present in the system temp directory. So copy this file to the directory
        #containing this script

        #First get the path to the system temp directory
        tempDir = os.environ.get("TEMP")
        if tempDir:
            shutil.copy2(os.path.join(tempDir,"BuildErrors.txt"),inSpace+"BuildErrors.txt")

        print "Script completed successfully."
        print "Error log is BuildErrors.txt if there's any error."
        
        
    except:
        print arcpy.GetMessages(2)
        
    finally:
        #Check the network analyst extension license back in, regardless of errors.
        arcpy.CheckInExtension("Network")