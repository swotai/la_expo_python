# Name: ModAlloc
# Description: Read CSV output from GIS, calculate flow and alloc flow to detectors


# Steps:
# Read the TT, TD, DT costs, $$$FLOW$$$
# for each detector, calculate matching matrix: 2000x2000 matrix of 1 and 0 indicating
# which OD pair (cell) is this detector on route
    # TD+DT == TT cost
# For each detector, multiply the matching matrix (1,0) to the route level flow 2000x2000 using multiply
# *** CHECK DIMENSION OF THE TWO AGREES
# Calculate the sum of flow using numpy.matrix.sum
# Record the detector flow in detector dictionary
# Export detector flow to CSV.  Retain in memory/return as object so that can run the
# speed update in next module




def readcsv(infile, indtype, incol, sort, header):
    # incol must be the same number of item as "indtype"
    # sort specify as [0] or [0,1] where number is column number
    # Header either None or True
    import pandas as pd
    import numpy as np
    if header != None:
        header = 0
    outFTT = pd.read_csv(infile, header = header)
    outFTT.columns = [i for i,col in enumerate(outFTT.columns)]
    outFTT = outFTT.sort(columns=sort)
    outFTT = np.asarray(outFTT.iloc[:,0:incol].values)
    outFTT = np.core.records.fromarrays(outFTT.transpose(), dtype = indtype)
    outFTT = np.asarray(outFTT)
    return outFTT

def alloc_2p(inSpace, currentIter, period):
    import numpy as np
    import sys
    from math import sqrt
    try:
        inTT = inSpace+"CSV/TT-" + period + ".csv"
        inTD = inSpace+"CSV/TD-" + period + ".csv"
        inDT = inSpace+"CSV/DT-" + period + ".csv"
        inFlow = inSpace+"CSV/TTflow"+str(currentIter)+ "-" + period + '.csv'
        outCSV = inSpace+'CSV/detflow'+str(currentIter)+ "-" + period + '.csv'

        #Test: 50 TAZs, 1813 DET
        #Full: 2241 TAZs, 1813 DETs
        nTAZ = 50
        nDET = 1813

        #fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
        datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        #fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
        fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
        
        print "importing various matrices"
        #Read TAZ-TAZ flow
        ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)

        #Read TD cost
        td = readcsv(inTD, datatype, incol = 4, sort = [1,0], header = None)

        #Read DT cost
        dt = readcsv(inDT, datatype, incol = 4, sort = [0,1], header = None)

        #Read TT cost
        tt = readcsv(inTT, datatype, incol = 4, sort = [0,1], header = None)

        nTAZ = int(sqrt(tt.size))
        if nTAZ != sqrt(tt.size):
            print "ERROR: TAZ SIZE NOT SQUARE!"
        if dt.size != td.size:
            print "ERROR: TD and DT SIZE NOT MATCH!"
        nDET = dt.size/nTAZ
        print "import completed"

        print "reshaping..."
        ctd = np.reshape(td['cost'],(nDET, nTAZ))
        cdt = np.reshape(dt['cost'],(nDET, nTAZ))
        ndt = np.reshape(dt['name'],(nDET, nTAZ))
        ctt = np.reshape(tt['cost'],(nTAZ, nTAZ))
        ftt = np.reshape(ff['postflow'],(nTAZ, nTAZ))
        #ftt = ftt + ftt.T

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
            #Imprecise/Buffer matching, not needed hopefully
            #match = x3 - tddt
            #t=abs(match)<0.5

            #Precise matching
            isflow = x3 == tddt

            #Element multiply by flow
            flow = np.multiply(isflow, ftt)
            totalflow = flow.sum()
            #print "Current iteration:", i
            if totalflow > 0:
            #    print "flow:", totalflow
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
    
    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModAlloc"
        print "An error occurred in ModAlloc line %i" % tb.tb_lineno 
        print e.message
        
        
def alloc(inSpace, inFlow, currentIter):
    import numpy as np
    import sys
    from math import sqrt
    try:
        inTT = inSpace+"CSV/TT.csv"
        inTD = inSpace+"CSV/TD.csv"
        inDT = inSpace+"CSV/DT.csv"
        outCSV = inSpace+'CSV/detflow'+str(currentIter)+'.csv'

        #Test: 50 TAZs, 1813 DET
        #Full: 2241 TAZs, 1813 DETs
        nTAZ = 50
        nDET = 1813

        #fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
        datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        #fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
        fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
        
        print "importing various matrices"
        #Read TAZ-TAZ flow
#        ff = np.genfromtxt(inFlow,
#                    dtype = fdtype,
#                    delimiter = ",",
#                    skip_header = 0)
#        
#        ff = np.asarray(sorted(ff, key=itemgetter(0,1)),
#                    dtype = fdtype)
        ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)

        #Read TD cost
#        td = np.genfromtxt(inTD, 
#                    dtype = datatype,
#                    delimiter = ",", 
#                    skip_header = 0)
#
#        td = np.asarray(sorted(td, key=itemgetter(1,0)),
#                    dtype = datatype)
        td = readcsv(inTD, datatype, incol = 4, sort = [1,0], header = None)

        #Read DT cost
#        dt = np.genfromtxt(inDT, 
#                    dtype = datatype,
#                    delimiter = ",", 
#                    skip_header = 0)
#                    
#        dt = np.asarray(sorted(dt, key=itemgetter(0,1)),
#                    dtype = datatype)
        dt = readcsv(inDT, datatype, incol = 4, sort = [0,1], header = None)

        #Read TT cost
#        tt = np.genfromtxt(inTT, 
#                    dtype = datatype,
#                    delimiter = ",", 
#                    skip_header = 0)
#                
#        tt = np.asarray(sorted(tt, key=itemgetter(0,1)),
#                    dtype = datatype)
        tt = readcsv(inTT, datatype, incol = 4, sort = [0,1], header = None)

        nTAZ = int(sqrt(tt.size))
        if nTAZ != sqrt(tt.size):
            print "ERROR: TAZ SIZE NOT SQUARE!"
        if dt.size != td.size:
            print "ERROR: TD and DT SIZE NOT MATCH!"
        nDET = dt.size/nTAZ
        print "import completed"

        print "reshaping..."
        ctd = np.reshape(td['cost'],(nDET, nTAZ))
        cdt = np.reshape(dt['cost'],(nDET, nTAZ))
        ndt = np.reshape(dt['name'],(nDET, nTAZ))
        ctt = np.reshape(tt['cost'],(nTAZ, nTAZ))
        ftt = np.reshape(ff['postflow'],(nTAZ, nTAZ))
        #ftt = ftt + ftt.T

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
            #Imprecise/Buffer matching, not needed hopefully
            #match = x3 - tddt
            #t=abs(match)<0.5

            #Precise matching
            isflow = x3 == tddt

            #Element multiply by flow
            flow = np.multiply(isflow, ftt)
            totalflow = flow.sum()
            #print "Current iteration:", i
            if totalflow > 0:
            #    print "flow:", totalflow
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
    
    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModAlloc"
        print "An error occurred in ModAlloc line %i" % tb.tb_lineno 
        print e.message
        
def alloc_trans(inSpace, inFlow, currentIter):
    '''
    Base on alloc(), but changed the hard coded items for transit matrices
    '''
    import numpy as np
    import sys
    from math import sqrt
    try:
        inTT = inSpace+"CSV/TT.csv"
        inTD = inSpace+"CSV/TD.csv"
        inDT = inSpace+"CSV/DT.csv"
        outCSV = inSpace+'CSV/detflow'+str(currentIter)+'.csv'

        #Test: 50 TAZs, 1813 DET
        #Full: 2241 TAZs, 1813 DETs
        nTAZ = 50
        nDET = 1813

        #fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
        datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        #fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
        fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
        
        print "importing various matrices"
        #Read TAZ-TAZ flow
        ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)

        #Read TD cost
        td = readcsv(inTD, datatype, incol = 4, sort = [1,0], header = None)

        #Read DT cost
        dt = readcsv(inDT, datatype, incol = 4, sort = [0,1], header = None)

        #Read TT cost
        tt = readcsv(inTT, datatype, incol = 4, sort = [0,1], header = None)

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
        #ftt = ftt + ftt.T

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
            #Imprecise/Buffer matching, not needed hopefully
            #match = x3 - tddt
            #t=abs(match)<0.5

            #Precise matching
            isflow = x3 == tddt

            #Element multiply by flow
            flow = np.multiply(isflow, ftt)
            totalflow = flow.sum()
            #print "Current iteration:", i
            if totalflow > 0:
            #    print "flow:", totalflow
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
    
    except Exception as e:
        tb = sys.exc_info()[2]
        print "Exception in ModAlloc"
        print "An error occurred in ModAlloc line %i" % tb.tb_lineno 
        print e.message
        
if __name__ == "__main__":
    from math import sqrt
    import numpy as np
    inSpace = "C:\Users\Dennis\Desktop\TransitPre/"
    currentIter = 1
    inTT = inSpace+"CSV/TT.csv"
    inTD = inSpace+"CSV/TD.csv"
    inDT = inSpace+"CSV/DT.csv"
    inFlow = inSpace+"CSV/TTflow"+str(currentIter)+'.csv'
#    inFlow = inSpace+"CSV/TTflow"+str(2)+'.csv'
    outCSV = inSpace+'CSV/detflow'+str(currentIter)+'.csv'

    #Test: 50 TAZs, 1813 DET
    #Full: 2241 TAZs, 1813 DETs
    nTAZ = 50
    nDET = 1813

    #fields = ["OriginID", "DestinationID", "Name", "Total_Cost"]
    datatype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
    #fdtype = [('oid','i8'),('did','i8'),('preflow','f8'),('postflow','f8')]
    fdtype = [('oid','i8'),('did','i8'),('postflow','f8')]
    
    print "importing various matrices"
    #Read TAZ-TAZ flow
    ff = readcsv(inFlow, fdtype, incol = 3, sort = [0,1], header = None)
    print "TT done"
    #Read TD cost
    td = readcsv(inTD, datatype, incol = 4, sort = [1,0], header = None)
    print "TD done"
    #Read DT cost
    dt = readcsv(inDT, datatype, incol = 4, sort = [0,1], header = None)
    print "DT done"
    #Read TT cost
    tt = readcsv(inTT, datatype, incol = 4, sort = [0,1], header = True)
    print "TT cost done"
    
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
    #ftt = ftt + ftt.T

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
        #Imprecise/Buffer matching, not needed hopefully
        #match = x3 - tddt
        #t=abs(match)<0.5

        #Precise matching
        isflow = x3 == tddt

        #Element multiply by flow
        flow = np.multiply(isflow, ftt)
        totalflow = flow.sum()
        #print "Current iteration:", i
        if totalflow > 0:
        #    print "flow:", totalflow
            count +=1
        
        #Record flow in dictionary
        detFlow[det] = totalflow
        i+=1

    del detFlow[999999]
    print "Number of detectors with match:", count

    dtype = [('idstn','i8'),('flow','f8')]
    detFlow= np.array(detFlow.items(), dtype=dtype)

    np.savetxt(outCSV, detFlow, delimiter=',', fmt='%7.0f, %7.10f')
    
    
