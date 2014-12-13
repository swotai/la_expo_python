# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 15:18:31 2014

@author: Dennis
"""

import multiprocessing  
import csv  
import arcpy  
  
def CalculateOD(stuffPassed):  
    '''Calculate the OD matrix and write the results to a CSV'''  
      
    ## Generate the input layer. You can read in a saved layer template  
    ## add add the appropriate origins and destinations for this chunk  
      
    ## Solve the layer  
      
    ## Call the external Save-to-CSV code or write your own code  
      
    ## Return the path to the CSV  
      
  
# ---- Main code ----  
def main():  
  
    ## Do whatever you need to prepare your analysis  
    ODChunks = []  
    ## Fill your list of OD chunks somehow  
  
    # Pass this info as inputs to the multiprocessing function.  
    stuffToPass = []  
    for chunk in ODChunks:  
        if chunk:  
            idx = ODChunks.index(chunk)  
            # I'm passing the chunk index because you can use that to name the output file  
            stuffToPass.append([chunk, idx, OTHERVARIABLES])  
  
    # Do the multiprocessing. It could return the paths to the output csvs if you want.  
    pool = multiprocessing.Pool()  
    OutCSVs = pool.map(CalculateOD, stuffToPass)  
    pool.close()  
    pool.join()  
      
   
    # Combine the output csvs  
    for CSVFile in OutCSVs:  
        ## Open each CSV using python's csv module  
        ## The first line is probably the field headers, so discard that after the first time  
        ## Dump the rows out into one giant table.  
      
      
if __name__ == '__main__':  
    main()  