# -*- coding: utf-8 -*-
"""
Created on Thu Nov 06 14:10:32 2014

@author: Dennis
"""


import pysal as ps
import pandas as pd



def dbf2df(dbf_path, index=None, cols=False, incl_index=False):
    '''
    Read a dbf file as a pandas.DataFrame, optionally selecting the index
    variable and which columns are to be loaded.
    __author__  = "Dani Arribas-Bel <darribas@asu.edu> "
    
    Arguments
    ---------
    dbf_path    : str
                  Path to the DBF file to be read
    index       : str
                  Name of the column to be used as the index of the DataFrame
    cols        : list
                  List with the names of the columns to be read into the
                  DataFrame. Defaults to False, which reads the whole dbf
    incl_index  : Boolean
                  If True index is included in the DataFrame as a
                  column too. Defaults to False
    Returns
    -------
    df          : DataFrame
                  pandas.DataFrame object created
    '''
    db = ps.open(dbf_path)
    if cols:
        if incl_index:
            cols.append(index)
        vars_to_read = cols
    else:
        vars_to_read = db.header
    data = dict([(var, db.by_col(var)) for var in vars_to_read])
    if index:
        index = db.by_col(index)
        db.close()
        return pd.DataFrame(data, index=index)
    else:
        db.close()
        return pd.DataFrame(data)


inSpace = "E:/DATA_testMP/FIGS/"

import time

timer = time.time()
table = dbf2df(inSpace+"TDP.dbf", cols = ['OriginID', 'Destinatio', 'Name', 'Total_Cost'])
table.to_csv(inSpace+"testout.csv", columns = ['OriginID', 'Destinatio', 'Name', 'Total_Cost'], index=False)
timer -= time.time()
print "read time:", -timer, "seconds"






#inSpace = "E:/DATA_test2p_1105/CSV/"


#testtable = dbf.Table(inSpace+'test.dbf')
#testtable.open()

#dbf.export(testtable, filename=inSpace+'test1.csv', header=True)

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "OD Cost Matrix\Lines"
#arcpy.TableToTable_conversion
#                ("OD Cost Matrix/Lines",
#                "C:/Users/Dennis/Desktop/DATA/Temp",
#                "test.dbf",
#                "#",
#                """Name "Name" true true true 128 Text 0 0 ,First,#,/ODLines,Name,-1,-1;OriginID "OriginID" true true true 4 Long 0 0 ,First,#,/ODLines,OriginID,-1,-1;Destinatio "Destinatio" true true true 4 Long 0 0 ,First,#,/ODLines,DestinationID,-1,-1;Total_Cost "Total_Cost" true true true 8 Double 0 0 ,First,#,/ODLines,Total_Cost,-1,-1""",
#                "#")
#count = 0
#for record in table:
#    print "oid:", record['originid'], "did:", record['destinatio'], "name:", record['name'], "cost:", record['total_cost']
#    count +=1
#    if count > 10:
#        break
#    