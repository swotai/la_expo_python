import pandas as pd
import numpy as np
import time

print "Stata starts: ", time.strftime("%d/%m/%Y - %H:%M:%S")


inSpace = 'C:/Users/Dennis/Desktop/Test/'

# Paths
fTT = inSpace+'TT.csv'
fTotalTTflow = inSpace+'TotalTTflow1.csv'
fTransitPre = 'C:/Users/Dennis/Desktop/TransitPre/CSV/'+'TT.csv'
fTransitPost= 'C:/Users/Dennis/Desktop/TransitPost/CSV/'+'TT.csv'

# TT cost matrix column names
TransTTlabel = ['v1', 'v2', 'v3', 'cost', 'length', 'dps', 'metrol', 'busl', 'walkl', 'lblue', 'lred', 'lgreen', 'lgold', 'lexpo']

# VOT
vot = 15



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

# Read TransitPre TT cost matrix
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
colname = ['pre'+name for name in colname]   # Rename variables
colname[0:2] = ['oid','did']
TransitPre.columns = colname

# Read TransitPost TT cost matrix
TransitPost = pd.read_csv(fTransitPost, header=None)
TransitPost.columns = [TransTTlabel]   # Rename columns
odNames = pd.DataFrame(TransitPost['v3'].str.split(' - ').tolist(), columns=['oid','did'])   # substring the v3 into oid and did strs
odNames = odNames.convert_objects(convert_numeric=True)   # destring, replace
TransitPost['oid'] = odNames['oid']
TransitPost['did'] = odNames['did']
TransitPost['fare'] = 1.25*(TransitPost['busl']+TransitPost['metrol']>0)    # Generate fare
TransitPost['cost'] = TransitPost['dps']*vot + TransitPost['fare']          # Update cost
TransitPost = TransitPost[['oid','did','dps','fare','cost','busl','metrol','walkl','length']]   # keep relavent variables
colname = TransitPost.columns.values   
colname = ['post'+name for name in colname]   # Rename variables
colname[0:2] = ['oid','did']
TransitPost.columns = colname


# The Big Merge
Dataset=pd.merge(TT, TotalTTflow,      left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')
Dataset=pd.merge(Dataset, TransitPre,  left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')
Dataset=pd.merge(Dataset, TransitPost, left_on=['oid', 'did'], right_on=['oid', 'did'], how='inner')

# Generate new Sij
Dataset['costdiffpre'] = 5.45-5.05*(Dataset['precost']/Dataset['predrvcost'])
Dataset['costdiffpost'] = 5.45-5.05*(Dataset['postcost']/Dataset['predrvcost'])

Dataset['Sijpre']  = np.exp(Dataset['costdiffpre']) /(1 + np.exp(Dataset['costdiffpre']))
Dataset['Sijpost'] = np.exp(Dataset['costdiffpost'])/(1 + np.exp(Dataset['costdiffpost']))

Dataset['dflowpre']  = Dataset['totalflow'] * (1-Dataset['Sijpre'])
Dataset['dflowpost'] = Dataset['totalflow'] * (1-Dataset['Sijpost'])
Dataset['tflowpre']  = Dataset['totalflow'] * (Dataset['Sijpre'])
Dataset['tflowpost'] = Dataset['totalflow'] * (Dataset['Sijpost'])

tflowpre = Dataset[['oid','did','tflowpre']]
tflowpost= Dataset[['oid','did','tflowpost']]

tflowpre.to_csv(inSpace+'preflow.csv', header=None)
tflowpost.to_csv(inSpace+'postflow.csv', header=None)

# Write it out to see if it works
Dataset.to_stata(inSpace+'test.dta')

print "Stata finishes: ", time.strftime("%d/%m/%Y - %H:%M:%S")