# Name: ModSetupWorker.py
# Description: Copy the base gdb to a new temp worker gdb
#              in order to ensure network build successful
# Requirements: shutil (high level file operation)



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

def clearOld(pathBase, pathTemp):
    import shutil, sys, os

    try:
        if os.path.exists(pathTemp):
            shutil.rmtree(pathTemp)
            print "Scratch file removed."
        else:
            print "No scratch file existed.  It's fine."

    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModSetupWorker"
        print "Line %i" % tb.tb_lineno 
        print "If code break here, likely there's a lock on " 
        print pathTemp
        print "Make sure arcGIS or arcCatalog is closed"
        print e.message
    
    finally:
        shutil.copytree(pathBase, pathTemp, symlinks=False, ignore=None)
        print "Copied new temp"


def setup_3workers(inSpace, inGdb):
    import shutil, os, sys
    '''
    Check if GDB workers (x3) folder exist, if so, remove, then create new workers.
    
    Arguments
    ---------
    inSpace :     Path to working directory
    
    scratchName : Name of scratch file, 
                  e.g. LA-scratch-OP.gdb

    '''
    try:
        path = inGdb[:-4] + "1" + inGdb[-4:]
        path = inSpace + path
        if os.path.exists(path):
            print "remove", path
            shutil.rmtree(path)
        path = inGdb[:-4] + "2" + inGdb[-4:]
        path = inSpace + path
        if os.path.exists(path):
            print "remove", path
            shutil.rmtree(path)
        path = inGdb[:-4] + "3" + inGdb[-4:]
        path = inSpace + path
        if os.path.exists(path):
            print "remove", path
            shutil.rmtree(path)

        print "making copies of GDB for running.", inGdb
        Gdb = inGdb[:-4] + "1" + inGdb[-4:]
        shutil.copytree(inSpace+inGdb, inSpace+Gdb, symlinks=False, ignore=None)
        Gdb = inGdb[:-4] + "2" + inGdb[-4:]
        shutil.copytree(inSpace+inGdb, inSpace+Gdb, symlinks=False, ignore=None)
        Gdb = inGdb[:-4] + "3" + inGdb[-4:]
        shutil.copytree(inSpace+inGdb, inSpace+Gdb, symlinks=False, ignore=None)
    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModSetupWorker.Setup_3worker"
        print "Line %i" % tb.tb_lineno 
        print e.message
    
#E:/DATA_testMP/LA-scratch-P.gdb > E:/DATA_testMP/LA-scratch-P1.gdb
def del_3workers(inSpace, inGdb):
    import shutil, os, sys
    '''
    Remove GDB workers (x3) folders.
    
    Arguments
    ---------
    inSpace :     Path to working directory
    
    scratchName : Name of scratch file, 
                  e.g. LA-scratch-OP.gdb

    '''
    try:
        path = inGdb[:-4] + "1" + inGdb[-4:]
        path = inSpace + path
        if os.path.exists(path):
            shutil.rmtree(path)
        path = inGdb[:-4] + "2" + inGdb[-4:]
        path = inSpace + path
        if os.path.exists(path):
            shutil.rmtree(path)
        path = inGdb[:-4] + "3" + inGdb[-4:]
        path = inSpace + path
        if os.path.exists(path):
            shutil.rmtree(path)

    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModSetupWorker"
        print "Setup_3worker Line %i" % tb.tb_lineno 
        print e.message