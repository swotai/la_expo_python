# -*- coding: utf-8 -*-
"""
Created on Sat Jan 03 09:31:32 2015

@author: Dennis
"""

def dbf2CSV(dbf_path): 
    '''
    Read a dbf file as a pandas.DataFrame
    Based on dbf2df code by: "Dani Arribas-Bel <darribas@asu.edu>"
    
    Arguments
    ---------
    dbf_path    : str
                  Path to the DBF file to be read

    Usage
    -----
    outFile = inSpace+"CSV/TD.dbf"\n
    dbf2CSV(outFile)\n
    outputs file as inSpace+"CSV/TD.csv"
    '''
#    (dbf_path, index=None, cols=False, incl_index=False, inSpace, outFile)
#    table = dbf2df(inSpace+"TDP.dbf", cols = ['OriginID', 'Destinatio', 'Name', 'Total_Cost'])
#    table.to_csv(inSpace+"testout.csv", columns = ['OriginID', 'Destinatio', 'Name', 'Total_Cost'], index=False)
    # Fix cols to read the four vars
    import pysal as ps
    import pandas as pd
    cols = ['OriginID', 'Destinatio', 'Name', 'Total_Cost']
    db = ps.open(dbf_path)
    if cols:
        vars_to_read = cols
    else:
        vars_to_read = db.header
    data = dict([(var, db.by_col(var)) for var in vars_to_read])
    db.close()
    table = pd.DataFrame(data)
    #export to csv using Pandas to_csv function
    outFile = dbf_path[:-4]+".csv"
    table.to_csv(outFile, columns = cols, index = False, header=False)

if __name__ == "__main__":
    '''
	Table output from GIS accumulating from the following code:
		ObjectID
		*Shape
		Name
		OriginID
		DestinationID
		DestinationRank
		Total_Cost
		Total_DPS
		Total_Length
		Total_lenmetro
		Total_lenbus
		Total_lenwalk
	Shape is only visible for GIS.
	
	This code is to extract the data from dbf.
	'''
    import pysal as ps
    import pandas as pd
    
    inSpace = "C:\Users\Dennis\Desktop\TransitPost/"
    dbf_path = inSpace+"TransitPost_Accu.dbf"
    cols = ['OriginID', 'Destinatio', 'Name', 'Total_Cost', 'Total_lenm', 'Total_lenb', 'Total_lenw', 'Total_Leng']
    db = ps.open(dbf_path)
    vars_to_read = cols
    data = dict([(var, db.by_col(var)) for var in vars_to_read])
    db.close()
    table = pd.DataFrame(data)
    #export to csv using Pandas to_csv function
    outFile = dbf_path[:-4]+".csv"
    table.to_csv(outFile, columns = cols, index = False, header=False)
