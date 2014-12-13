# Name: ModSpeedCalc.py
# Description:    Recalculate network speed based on updated flow.
#                Export CSV for next iteration
 


from ModIO import readcsv

def cong_fdbk(x, FL, LIMIT):
    from math import exp
    if x > FL:
        return LIMIT * exp(-0.000191*(x-FL))
    else:
        return LIMIT


def flow2speed(inSpace, inFlow, FL, LIMIT, outCSV, dta):
    '''
    Given flow vector, calculate speed vector.  Returns ratio at the end.
    
    input:
    ------
    inSpace     : str
                  Working path
    inFlow      : str
                  Name of DETECTOR flow vector, ending in CSV.  Reads inFlow = inSpace+inFlow
    FL          : value
                  Flow / lane cutoff
    LIMIT       : value
                  Freeflow speed / speed limit (65)
    outCSV      : str
                  outCSV = inSpace+outCSV
                  outCSV = inSpace+'detspd-temp.csv'
                  outCSV = inSpace+'detspd'+str(currentIter)+'.csv'
                  , IF EMPTY, return ratio
    dta         : bool
                  if False, output detflow_adj in CSV folder

    output:
    -------
    detspd-temp.csv if dta; if not dta detspdi.csv, detflow_adji.csv
    '''
    import sys
    import numpy as np
    try:
        # read AF for ratio calculation
        inAF = inSpace+"AF.csv"
        fdtype = [('idstn','i8'),('center','i8'),('lane','i8'),('flow','f8'),('dist','f8')]
        af = readcsv(inAF, fdtype, incol = 5, sort=0, header = True)
        
        # read flow
        inFlow = inSpace+inFlow
        fdtype = [('idstn','i8'),('flow','f8')]
        cflow = readcsv(inFlow, fdtype, incol = 2, sort=0, header = None)

        # CHECK TO MAKE SURE THE ARRAYS MATCHES
        x1 = af['idstn']
        x2 = cflow['idstn']
        xeq = x1!=x2
        if xeq.sum() > 0:
            raise Exception("AF and Current detector flow idstn DOES NOT MATCH!")

        # Calculate AF/GF ratio for center detectors
        aft = af['center']*af['flow']
        cft = af['center']*cflow['flow']
        ratio = aft.sum()/cft.sum()
        print "AF/GF Ratio:", ratio
        
        if outCSV == "":
            return ratio            
        
        if not dta:
            #SAVE DETFLOW WITH ADJUSTMENT if not a DTA round
            detFlow= np.copy(cflow)
            detFlow['flow'] = detFlow['flow']*ratio
            outCSVcff = inSpace+'CSV/detflow_adj'+outCSV[6]+'.csv'
            np.savetxt(outCSVcff, detFlow, delimiter=',', fmt='%7.0f, %7.10f')

        #Convert from GF to the peak time flow F = AF/GF*6%*GF
        thisflow = ratio*.06*cflow['flow']/af['lane']
        vfeedback = np.vectorize(cong_fdbk, otypes=[np.float])
        yflow = vfeedback(thisflow, FL, LIMIT)
        cflow1 = np.copy(cflow)        
        cflow1['flow'] = yflow
        cflow1.dtype = ([('idstn', '<i8'), ('speed', '<f8')])
        
        # Save temp speed if DTA round, save regular speed if not
        outCSV = inSpace+outCSV
        print "speed updated.  Writing to", outCSV
        with open(outCSV, 'wb') as f:
            f.write(b'id_stn,speed\n')
            np.savetxt(f, cflow1, delimiter=',', fmt='%7.0f, %7.10f')

        return ratio
    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModSpeedCalc"
        print "An error occurred in ModSpeedCalc.flow2speed line %i" % tb.tb_lineno 
        print e.message        
 
if __name__ == '__main__':
    import os
    inSpace = "D:\Dropbox\Cornell\LA Expo Line Project\Mapping\Dynamic Traffic Assignment\Outputs\DTA_flow_firstLogit/"
    for file in os.listdir(inSpace):
        if file[4:8] == "flow":
            outfile = file[0] + "detspd"+ file[8:]
            flow2speed(inSpace, file, 500, 65, outfile, dta=True)