# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 19:47:08 2014

@author: Dennis
"""
import multiprocessing as mp
import ModJoinSpeed, ModBuild, ModSolveMP, time
from ModSetupWorker import setup_3workers, del_3workers, dbf2CSV
import sys

      
        
def GISops_2p(inSpace, inGdb, currentIter, fcTAZ, fcDet):
    '''
    Carry out GIS operations, 2 periods hard coded

    Inputs
    -----
    inSpace     : str
                  working directory
    inGdb       : str
                  Name of geodatabase
    currentIter : int
                  Current iteration
    fcTAZ       : str
                  Name of TAZ featureclass
    fcDet       : str
                  Name of detector featureclass
    
    Outputs
    -------
    Cost matrices: TT, TD, DT
    '''
    try:
    #    print "Starting GIS process", mp.current_process().name, "on", time.strftime("%d/%m/%Y - %H:%M:%S")
        # SETUP JOBS
        period = "P"
        inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
        Gdb_P = Gdb
        j1_p = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
        j2_p = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
        j3_p = mp.Process(target=ModSolveMP.solve, args=(inSpace, Gdb, fcTAZ, fcDet, period))

        period = "OP"
        inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
        Gdb_OP = Gdb
        j1_op = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
        j2_op = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
        j3_op = mp.Process(target=ModSolveMP.solve, args=(inSpace, Gdb, fcTAZ, fcDet, period))
    
    
        # Run Jobs.  Try to keep jobs in sync    
        # HINT: Give some slack time between processes to make sure they won't try to access same files.
        # HINT: Run j1 together, wait for both job to finish with join, then run next job.
        # Job 1
        j1_p.start()
        time.sleep(10)
        j1_op.start()
        j1_p.join()
        j1_op.join()
        # Job 2
        j2_p.start()
        time.sleep(10)
        j2_op.start()
        j2_p.join()
        j2_op.join()
        # Job 3
#        setup_3workers(inSpace, Gdb_P)
#        setup_3workers(inSpace, Gdb_OP)
        j3_p.start()
        time.sleep(30)
        j3_op.start()
        j3_p.join()
        j3_op.join()
    
        del_3workers(inSpace, Gdb_P)
        del_3workers(inSpace, Gdb_OP)
        
        # Convert DBF to CSV
        dbf2CSV(inSpace+"CSV/TTP.dbf")
        dbf2CSV(inSpace+"CSV/TDP.dbf")
        dbf2CSV(inSpace+"CSV/DTP.dbf")
        dbf2CSV(inSpace+"CSV/TTOP.dbf")
        dbf2CSV(inSpace+"CSV/TDOP.dbf")
        dbf2CSV(inSpace+"CSV/DTOP.dbf")
        sys.stdout.flush()

        return 1
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModGIS.GISops_2p line %i" % tb.tb_lineno
        print str(e)
        
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      

def GISops_dta(inSpace, inGdb, fcTAZ, fcDet, inSpeed):
    '''
    Carry out GIS operations, particularly for DTA operation

    Inputs
    -----
    inSpace     : str
                  working directory
    inGdb       : str
                  Name of geodatabase
    fcTAZ       : str
                  Name of TAZ featureclass
    fcDet       : str
                  Name of detector featureclass
    inSpeed     : str
                  Name of detector speed vector.  Used in DTA loop, input temp speed name
                  inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
    
    Outputs
    -------
    Cost matrices: TT, TD, DT
    '''
    try:
    #    print "Starting GIS process", mp.current_process().name, "on", time.strftime("%d/%m/%Y - %H:%M:%S")
        # SETUP JOBS
        period = "P"
        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
        Gdb_P = Gdb
        j1_p = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
        j2_p = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
#        j3_p = mp.Process(target=ModSolveMP.solve_2p, args=(inSpace, Gdb, fcTAZ, fcDet, period))
        
    
    
        # Run Jobs.  Try to keep jobs in sync    
        # HINT: Give some slack time between processes to make sure they won't try to access same files.
        # HINT: Run j1 together, wait for both job to finish with join, then run next job.
        # Job 1
        j1_p.start()
#        time.sleep(10)
#        j1_op.start()
        j1_p.join()
#        j1_op.join()
        # Job 2
        j2_p.start()
#        time.sleep(10)
#        j2_op.start()
        j2_p.join()
#        j2_op.join()
        # Job 3
        setup_3workers(inSpace, Gdb_P)
#        setup_3workers(inSpace, Gdb_OP)
#        j3_p.start()
#        time.sleep(30)
#        j3_op.start()
#        j3_p.join()
#        j3_op.join()
        ModSolveMP.solve_2p(inSpace, Gdb, fcTAZ, fcDet, period)
#        del_3workers(inSpace, Gdb_P)
#        del_3workers(inSpace, Gdb_OP)
        
        # Convert DBF to CSV
        dbf2CSV(inSpace+"CSV/TTP.dbf")
        dbf2CSV(inSpace+"CSV/TDP.dbf")
        dbf2CSV(inSpace+"CSV/DTP.dbf")
#        dbf2CSV(inSpace+"CSV/TTOP.dbf")
#        dbf2CSV(inSpace+"CSV/TDOP.dbf")
#        dbf2CSV(inSpace+"CSV/DTOP.dbf")
        sys.stdout.flush()

        return 1
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModGIS.GISops_dta line %i" % tb.tb_lineno
        print str(e)
















def GISops_1p(inSpace, inGdb, currentIter, fcTAZ, fcDet):
    '''
    Carry out GIS operations

    Inputs
    -----
    inSpace     : str
                  working directory
    inGdb       : str
                  Name of geodatabase
    currentIter : int
                  Current iteration, reads CurrentIteration-1 speed
    fcTAZ       : str
                  Name of TAZ featureclass
    fcDet       : str
                  Name of detector featureclass
    
    Outputs
    -------
    Cost matrices: TT, TD, DT
    '''
    try:
    #    print "Starting GIS process", mp.current_process().name, "on", time.strftime("%d/%m/%Y - %H:%M:%S")
        # SETUP JOBS
        period = "P"
        inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
        Gdb_P = Gdb
        ModJoinSpeed.joinSpeed(inSpace, Gdb, inSpeed)
        ModBuild.build(inSpace, Gdb)
#        j1_p = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
#        j2_p = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
#        j3_p = mp.Process(target=ModSolveMP.solve_2p, args=(inSpace, Gdb, fcTAZ, fcDet, period))
        
#        period = "OP"
#        inSpeed = "detspd" + str(currentIter - 1) + "-"+period+".csv"
#        Gdb = inGdb[:-4] + "-" + period + inGdb[-4:]
#        Gdb_OP = Gdb
#        j1_op = mp.Process(target=ModJoinSpeed.joinSpeed, args=(inSpace, Gdb, inSpeed))
#        j2_op = mp.Process(target=ModBuild.build, args=(inSpace, Gdb))
#        j3_op = mp.Process(target=ModSolveMP.solve_2p, args=(inSpace, Gdb, fcTAZ, fcDet, period))
    
    
        # Run Jobs.  Try to keep jobs in sync    
        # HINT: Give some slack time between processes to make sure they won't try to access same files.
        # HINT: Run j1 together, wait for both job to finish with join, then run next job.
        # Job 1
#        j1_p.start()
#        time.sleep(10)
#        j1_op.start()
#        j1_p.join()
#        j1_op.join()
        # Job 2
#        j2_p.start()
#        time.sleep(10)
#        j2_op.start()
#        j2_p.join()
#        j2_op.join()
        # Job 3
        setup_3workers(inSpace, Gdb_P)
#        setup_3workers(inSpace, Gdb_OP)
#        j3_p.start()
#        time.sleep(30)
#        j3_op.start()
#        j3_p.join()
#        j3_op.join()
        ModSolveMP.solve_2p(inSpace, Gdb, fcTAZ, fcDet, period)

#        del_3workers(inSpace, Gdb_P)
#        del_3workers(inSpace, Gdb_OP)
        
        # Convert DBF to CSV
        dbf2CSV(inSpace+"CSV/TTP.dbf")
        dbf2CSV(inSpace+"CSV/TDP.dbf")
        dbf2CSV(inSpace+"CSV/DTP.dbf")
#        dbf2CSV(inSpace+"CSV/TTOP.dbf")
#        dbf2CSV(inSpace+"CSV/TDOP.dbf")
#        dbf2CSV(inSpace+"CSV/DTOP.dbf")
        sys.stdout.flush()

        return 1
    except Exception as e:
        # If an error occurred, print line number and error message
        import sys
        tb = sys.exc_info()[2]
        print "An error occurred in ModGIS.GISops_1p line %i" % tb.tb_lineno
        print str(e)