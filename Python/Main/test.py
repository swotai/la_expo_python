# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 21:06:58 2015

@author: Dennis
"""

# Section 2: This section is actual code
if __name__ == '__main__':
    import time
    currentIter = 1
    fcTAZ = "TAZ_LA_proj_centroid"
    fcDet = "AllStationsML"

    # VOT
    vot = 15

##################################
# EDIT THIS SECTION TO SET PATHS #
##################################
#   Specify two paths: 
#       1) path to driving TT cost and driving total TT flow    
#       2) path to transit network dataset
    drvpath = 'C:/Users/Dennis/Desktop/Pre/'
    transitpath = 'C:/Users/Dennis/Desktop/CalcTransit/CF-fastall-set/'
    inSpace = transitpath
    
#   This adds a prefix to the variables output to the transit matrix.
#   e.g. predps, postdps  Should be 'post' unless it's 'pre'.
    varprefix = 'post'
    base = "LA_MetroPostBus-DPS.gdb"
    temp = "LA-scratch.gdb"
    inNetwork = "PostBusDPS_ND"
    startspeed = 15
    maxspeed = 35
##################################
#   END OF SECTION TO SET PATHS  #
##################################
    currentIter = startspeed
    inGdb = temp
    base = inSpace+base
    temp = inSpace+temp
    # Paths
    fTT = drvpath+'CSV/TT.csv'
    fTotalTTflow = drvpath+'CSV/TotalTTflow1.csv'
    fTransitTT = transitpath+'CSV/TT.csv'
    while currentIter < (maxspeed + 1): 
        speed = currentIter
        fTransitTT = transitpath+'TransitMatrix'+str(speed)+'.dta'
        ### Cost matrix calculation
        print "Starting iteration", currentIter
        
        ### Generate OD level transit flow
        import pandas as pd
        import numpy as np
        
        print "Flow-gen starts: ", time.strftime("%d/%m/%Y - %H:%M:%S")

        # TT cost matrix column names
        TransTTlabel = ['v1', 'v2', 'v3', 'cost', 'length', 'dps', 'metrol', 'busl']
        
        # Read Driving TT cost matrix
        TT = pd.read_csv(fTT, header=None)
        TT.columns = ['v1','v2','v3','predrvcost','predrvlen','predrvdps']   # Rename columns
        odNames = pd.DataFrame(TT['v3'].str.split(' - ').tolist(), columns=['oid','did'])
        odNames = odNames.convert_objects(convert_numeric=True)
        TT['oid'] = odNames['oid']
        TT['did'] = odNames['did']
        del TT['v1'], TT['v2'], TT['v3']                       # delete v1, v2 columns
        
       
        # Read Transit TT cost matrix
        TransitPre = pd.read_stata(fTransitTT)
        
        # The Big Merge
#        Dataset=pd.merge(TT, TotalTTflow,       left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')
        Dataset=pd.merge(TT, TransitPre,   left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')
        
        # Generate new Sij, flow
        Dataset['costdiff'] = 5.45-5.05*(Dataset[varprefix+'cost']/Dataset['predrvcost'])
        Dataset['Sij']  = np.exp(Dataset['costdiff']) /(1 + np.exp(Dataset['costdiff']))
        Dataset['dflow']  = Dataset['totalflow'] * (1-Dataset['Sij'])
        Dataset['tflow']  = Dataset['totalflow'] * (Dataset['Sij'])
        
        
        # Write out the calculated matrix into DTA for table generation
        Dataset.to_stata(transitpath+'aTransitMatrix' + str(currentIter) + '.dta', write_index=False)
        print "Flow-gen finishes: ", time.strftime("%d/%m/%Y - %H:%M:%S")
        del Dataset, TransitPre
    
        
        currentIter+=1
