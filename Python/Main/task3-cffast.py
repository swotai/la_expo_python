# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 14:56:46 2015

@author: Dennis

# Purpose: Run modules to do the following:
# 3, Calculate cost (TD + DT)
# 4, Compute station level flow

# For Equilibrium calculation
# and Allocating flow to Transit stations.
# Functions are defined in section 1, and actual main code in section 2.
"""


# Section 1: This section is for defining functions.

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

def solvetrans(inSpace, inNetwork, inGdb, fcTAZ, fcDet):
    '''
    Solves TD and DT, given fcTAZ and fcDet
    '''
    #Set local variables
    inNetworkDataset = "Trans/"+inNetwork
    impedanceAttribute = "Cost"
    # accumulateAttributedt = "#" << Use this if no need to accumulate
    accumulateAttributeTT = ['Length', 'Cost', 'DPS', 'lenmetro', 'lenbus', 'lenwalk', 'lblue', 'lred', 'lgreen', 'lgold', 'lexpo', 'lorange', 'lsilver']
    FieldsTT = ["OriginID", "DestinationID", "Name", "Total_Cost", 'Total_Length', 'Total_DPS', 'Total_lenmetro', 'Total_lenbus', 'Total_lenwalk', 'Total_lblue', 'Total_lred', 'Total_lgreen', 'Total_lgold', 'Total_lexpo']
    accumulateAttributeDT = "#"
    FieldsDT = ["OriginID", "DestinationID", "Name", "Total_Cost"]

    #TT COST CALCULATION STARTS HERE
    outNALayerName = "ODTT"
    inOrigins = "Trans/"+fcTAZ
    inDestinations = "Trans/"+fcTAZ
    outFile = inSpace+"CSV/TT.csv"
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeTT, inOrigins, inDestinations, outNALayerName, outFile, FieldsTT)
    print "TT Solved"

    #TD COST CALCULATION STARTs HERE
    outNALayerName = "ODTD"
    inOrigins = "Trans/"+fcTAZ
    inDestinations = "Trans/"+fcDet
    outFile = inSpace+"CSV/TD.csv"
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeDT, inOrigins, inDestinations, outNALayerName, outFile, FieldsDT)
    print "TD Solved"

    #DT COST CALCULATION STARTS HERE
    outNALayerName = "ODDT"
    inOrigins = "Trans/"+fcDet
    inDestinations = "Trans/"+fcTAZ
    outFile = inSpace+"CSV/DT.csv"
    NAtoCSV_trans(inSpace, inGdb, inNetworkDataset, impedanceAttribute, accumulateAttributeDT, inOrigins, inDestinations, outNALayerName, outFile, FieldsDT)
    print "DT Solved"
     

def alloc_trans(inSpace, inFlow, currentIter):
    '''
    Base on alloc(), but changed the hard coded items for transit matrices
    '''
    import numpy as np
    from ModIO import readcsv
    from math import sqrt

    inTT = inSpace+"CSV/TT.csv"
    inTD = inSpace+"CSV/TD.csv"
    inDT = inSpace+"CSV/DT.csv"
    outCSV = inSpace+'CSV/Transdetflow'+str(currentIter)+'.csv'

    #Test: 50 TAZs, 1813 DET
    #Full: 2241 TAZs, 1813 DETs
    nTAZ = 50
    nDET = 1813

    dttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
    tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8'),('length','f8'),('dps','f8'),('metro','f8'),('bus','f8'),('walk','f8'),('blue','f8'),('green','f8'),('red','f8'),('gold','f8'),('expo','f8')]
    fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
    
    print "importing various matrices"
    #Read TAZ-TAZ flow
    ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)

    #Read TD cost
    td = readcsv(inTD, dttype, incol = 4, sort = [1,0], header = None)

    #Read DT cost
    dt = readcsv(inDT, dttype, incol = 4, sort = [0,1], header = None)

    #Read TT cost
    tt = readcsv(inTT, tttype, incol = 14, sort = [0,1], header = None)

    nTAZ = int(sqrt(tt.size))
    if nTAZ != sqrt(tt.size):
        print "ERROR: TAZ SIZE NOT SQUARE!"
    if dt.size != td.size:
        print "ERROR: TD and DT SIZE NOT MATCH!"
    nDET = dt.size/nTAZ
    print "import completed, TAZ:", nTAZ, "DET:", nDET

    print "reshaping..."
    ctd = np.reshape(td['cost'],(nDET, nTAZ))
    cdt = np.reshape(dt['cost'],(nDET, nTAZ))
    ndt = np.reshape(dt['name'],(nDET, nTAZ))
    ctt = np.reshape(tt['cost'],(nTAZ, nTAZ))
    ftt = np.reshape(ff['postflow'],(nTAZ, nTAZ))

    # FLOW MATRIX
    print "begin flow allocation"
    x3 = np.matrix(ctt)
    i = 0
    count = 0
    detFlow = {999999: 0}
    while i < nDET:
        #Extract current detector id_stn
        det = ndt[i,1][0:6]

        # Extract cost vectors
        x1 = np.matrix(ctd[i])
        x1 = x1.T
        x2 = np.matrix(cdt[i])

        tddt=x1+x2

        #Precise matching
        isflow = x3 == tddt

        #Element multiply by flow
        flow = np.multiply(isflow, ftt)
        totalflow = np.nansum(flow)
        #print "Current iteration:", i
        if totalflow > 0:
            print "stn", i, "flow:", totalflow
            count +=1
        
        #Record flow in dictionary
        detFlow[det] = totalflow
        i+=1

    del detFlow[999999]
    print "Number of detectors with match:", count

    dtype = [('idstn','i8'),('flow','f8')]
    detFlow= np.array(detFlow.items(), dtype=dtype)

    np.savetxt(outCSV, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
    
    return detFlow



# Section 2: This section is actual code
if __name__ == '__main__':
    import ModSetupWorker, ModBuild
    import time
    currentIter = 1
    fcTAZ = "TAZ_LA_proj_centroid"
    fcDet = "AllStationsML"

    # VOT
    vot = 15

#   Specify two paths: 
#       1) path to driving TT cost and driving total TT flow    
#       2) path to transit network dataset
    drvpath = 'C:/Users/Dennis/Desktop/Pre/'
    transitpath = 'C:/Users/Dennis/Desktop/CalcTransit/CF-fast/'
    inSpace = transitpath
    
#   This adds a prefix to the variables output to the transit matrix.
#   e.g. predps, postdps  Should be 'post' unless it's 'pre'.
    varprefix = 'post'
    base = "LA_MetroPostBus-DPS.gdb"
    temp = "LA-scratch.gdb"
    inNetwork = "PostBusDPS_ND"

     
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

    # 2, rebuild network dataset
    print "Speed updated. Rebuild Dataset..."
    ModBuild.buildTrans(inSpace, inNetwork, inGdb)
    
    # 3, solve network
    print "Dataset rebuilt. Solve for TT, TD, DT"
    solvetrans(inSpace, inNetwork, inGdb, fcTAZ, fcDet)
    print "Transit cost matrix calculation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")
   
    
### Generate OD level transit flow
    import pandas as pd
    import numpy as np
    import time
    
    print "Flow-gen starts: ", time.strftime("%d/%m/%Y - %H:%M:%S")
    # Paths
    fTT = drvpath+'CSV/TT.csv'
    fTotalTTflow = drvpath+'CSV/TotalTTflow1.csv'
    fTransitPre = transitpath+'CSV/TT.csv'
    
    # TT cost matrix column names
    TransTTlabel = ['v1', 'v2', 'v3', 'cost', 'length', 'dps', 'metrol', 'busl', 'walkl', 'lblue', 'lred', 'lgreen', 'lgold', 'lexpo']
    
    # Read Driving TT cost matrix
    TT = pd.read_csv(fTT, header=None)
    TT.columns = ['v1','v2','v3','predrvcost','predrvlen','predrvdps']   # Rename columns
    odNames = pd.DataFrame(TT['v3'].str.split(' - ').tolist(), columns=['oid','did'])
    odNames = odNames.convert_objects(convert_numeric=True)
    TT['oid'] = odNames['oid']
    TT['did'] = odNames['did']
    del TT['v1'], TT['v2'], TT['v3']                       # delete v1, v2 columns
    
    # Read Total Flow Matrix
    TotalTTflow = pd.read_csv(fTotalTTflow, header=None)
    TotalTTflow.columns = ['oid', 'did', 'totalflow']   # Rename columns
    
    # Read Transit TT cost matrix
    TransitPre = pd.read_csv(fTransitPre, header=None)
    TransitPre.columns = [TransTTlabel]   # Rename columns
    odNames = pd.DataFrame(TransitPre['v3'].str.split(' - ').tolist(), columns=['oid','did'])   # substring the v3 into oid and did strs
    odNames = odNames.convert_objects(convert_numeric=True)   # destring, replace
    TransitPre['oid'] = odNames['oid']
    TransitPre['did'] = odNames['did']
    TransitPre['fare'] = 1.25*(TransitPre['busl']+TransitPre['metrol']>0)   # Generate fare
    TransitPre['cost'] = TransitPre['dps']*vot + TransitPre['fare']         # Update cost
    TransitPre = TransitPre[['oid','did','dps','fare','cost','busl','metrol','walkl','length']]   # keep relavent variables
    colname = TransitPre.columns.values   
    colname = [varprefix+name for name in colname]   # Rename variables
    colname[0:2] = ['oid','did']
    TransitPre.columns = colname
    
    # The Big Merge
    Dataset=pd.merge(TT, TotalTTflow,       left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')
    Dataset=pd.merge(Dataset, TransitPre,   left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')
    
    # Generate new Sij, flow
    Dataset['costdiff'] = 5.45-5.05*(Dataset[varprefix+'cost']/Dataset['predrvcost'])
    Dataset['Sij']  = np.exp(Dataset['costdiff']) /(1 + np.exp(Dataset['costdiff']))
    Dataset['dflow']  = Dataset['totalflow'] * (1-Dataset['Sij'])
    Dataset['tflow']  = Dataset['totalflow'] * (Dataset['Sij'])
    
    # Save the flow into TransTTflow1.csv in corresponding folder.
    tflowpre = Dataset[['oid','did','tflow']]
    tflowpre.to_csv(transitpath+'CSV/TransTTflow1.csv', header=None, index = None)
    
    # Write out the calculated matrix into DTA for table generation
    Dataset.to_stata(transitpath+'TransitMatrix.dta')
    print "Flow-gen finishes: ", time.strftime("%d/%m/%Y - %H:%M:%S")
    del Dataset, TransitPre

### Allocate flow
    # Pre allocation
    print "Transit flow ALLOCATION starts on", time.strftime("%d/%m/%Y - %H:%M:%S")
    print "Flow Allocation"
    inFlow = inSpace + "CSV/TransTTflow" + str(currentIter) + ".csv"
    flow = alloc_trans(inSpace, inFlow, currentIter)
    
    print "Transit flow allocation completes on", time.strftime("%d/%m/%Y - %H:%M:%S")
    
