# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 14:21:35 2015

This code uses the Expo line modules to compute TT costs for transit scenarios
in the prototype city.  

"""

# Section 1: Calls function and loop
if __name__ == '__main__':
    import ModSetupWorker, ModBuild, ModUpdateTransit, ModSolve
    import time
    currentIter = 1
    fcTAZ = "CityBase/CityZoneCentroid"


    # VOT
    vot = 15
    
    # Speeds
    initspd = 10
    topspd = 30

##################################
# EDIT THIS SECTION TO SET PATHS #
##################################
#   Specify two paths: 
#       1) path to driving TT cost and driving total TT flow    
#       2) path to transit network dataset
    drvpath = 'C:/Users/Dennis/Desktop/Pre/'
    transitpath = 'D:/Mapping/Prototype/'
    inSpace = transitpath
    
#   This adds a prefix to the variables output to the transit matrix.
#   e.g. predps, postdps  Should be 'post' unless it's 'pre'.
    varprefix = 'post'
    base = "PrototypeCity.gdb"
    temp = "Proto-scratch.gdb"
    inNetwork = "RoadBase/Drive_ND"
##################################
#   END OF SECTION TO SET PATHS  #
##################################

     
### Cost matrix calculation
    print "Transit cost matrix calculation starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
    print "Using transit dataset at:", transitpath
    # Specify the transit gdb
    inGdb = temp
    base = inSpace+base
    temp = inSpace+temp
    
    # 0, create temp scratch
    print "Setting up scratch version"
    ModSetupWorker.clearOld(base,temp)
    print "Scratch version set up.  Proceding..."
    
    # 3, rebuild network dataset
    print "Speed updated. Rebuild Dataset..."
    ModBuild.buildTrans(inSpace, inNetwork, inGdb)
    
    # 4, solve network
    print "Dataset rebuilt. Solve for TT"
    outname = "CSV/Proto-ODDist-Drv.txt"
    ModSolve.solvedrvTT(inSpace, inNetwork, inGdb, fcTAZ, outname)
    print "Transit cost matrix calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")
    
        