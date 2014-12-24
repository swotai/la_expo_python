# Name: ModUpdateFlow.py
# Description: This script updates the TAZ to TAZ flow using 
#              updated speed, completing the iteration circle
# Input: updated TT cost (driving), TT cost (transit), 
#        gravity parameters, population (O), employment (D)
# Output: TAZ-TAZ transit share, TAZ-TAZ flow
# Note: This script REQUIRES 64 bit python and numpy to function
#
# Steps:
# 1, Compute updated transit share S (2000x2000)
#    Share equation S_ij = [exp(c1+c2*delta C_ij)]/[1+exp(c1+c2*delta C_ij)]
#    delta C_ij = C(pub)_ij / C(drv)_ij
# 2, Compute total transport flows according to gravity equation:
#    TTF_ij =     G 
#                * P_i^beta1
#                * E_j^beta2
#                * [S_ij * C(pub)_ij + (1-S_ij) * C(drv)_ij]^tau
# 3, Compute updated private transport flows PTTF
#    PTTF_ij = (1-S_ij) * TTF_ij

#import numpy as np
#from math import exp
## Input: updated TT cost (driving), TT cost (transit), 
##        gravity parameters, population (O), employment (D)
#
##Parameters
#c1 = 5.45
#c2 = -5.05
#G = exp(-3.289)
#beta1 = 0.535
#beta2 = 0.589
#tau = -2.077
#
#ttcost = np.arange(9, dtype = 'float32')+1
#ttcost = ttcost.reshape(3,3)
#
#ttcosti = ttcost
#ttcostp = ttcost + 4
#
#pop = np.array((1.0, 3.0, 6.0)) ** beta1
#pop = np.matrix(pop)
#emp = np.array((8.0, 1.1, 0.9)) ** beta2
#emp = np.matrix(emp)
#
## Sij (OK)
#deltaC = ttcosti/ttcostp
#exx = np.exp(c1+c2*deltaC)
#sij = exx / (1+exx)
#
## Gravity prediction
#a = G * np.array(pop.T * emp) * (sij*ttcostp + (1-sij)*ttcosti)**tau
#print a



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


def update_2p(inSpace, currentIter, inTTp, penalty):
    try:
        from math import exp, sqrt, pi
        import numpy as np
        import sys
        
        #print "Code starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
        #Parameters
        c1 = 5.45
        c2 = -5.05
        G = exp(-3.289)
        beta1 = 0.535
        beta2 = 0.589
        tau = -2.077
        
    
        #import various matrices
        fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
        tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        petype = [('oid','i8'),('emp','f8'),('pop','f8')]
        areatype = [('oid','i8'),('area','f8')]
        
        #import from inFlow
        #This is used as OUTPUT TEMPLATE
        outFTT = inSpace + "inFlow.csv"
        outFTT = readcsv(outFTT, fdtype, incol = 3, sort = [0,1], header = None)
        
        #TT Cost (pub)
        #Post/PRE as SEPARATE CSV FILE
        print "importing TTcost for Transit"
        ttp = readcsv(inTTp, tttype, incol = 4, sort = [0,1], header = True)
        
        print "importing TTcost for driving (peak)"
        #TT Cost (driving, CURRENT)
        inTTdp = inSpace+"CSV/TTP.csv"
        ttdp = readcsv(inTTdp, tttype, incol = 4, sort = [0,1], header = None)
        inTTdop = inSpace+"CSV/TTOP.csv"
        ttdop = readcsv(inTTdop, tttype, incol = 4, sort = [0,1], header = None)
        
        
        #print "check sorting"
        #make sure both TT costs are sorted correctly:
        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
        #    raise Exception('Driving and Transit TT not match!')
        #print "sorting is fine"
        
        print "importing census"
        #Population & employment
        inPE = inSpace+"census.csv"        
        pe = readcsv(inPE, petype, incol = 3, sort = [0], header = True)
        
        print "importing TAZ area"
        inArea = inSpace+"TAZarea.csv"        
        area = readcsv(inArea, areatype, incol=2, sort=[0], header = True)
        area = area['area']
        
        print "testing squareness"
        #Test square of TTcost and TTcostpub, test same size of pop/emp
        ttsize = sqrt(np.size(ttdp))
        if ttsize != int(ttsize):
            raise Exception('Driving TT cost at peak not square!!!')
        ttsize = sqrt(np.size(ttdop))
        if ttsize != int(ttsize):
            raise Exception('Driving TT cost offpeak not square!!!')
        ttsize = sqrt(np.size(ttp))
        if ttsize != int(ttsize):
            raise Exception('Transit TT cost not square!!!')
        pesize = np.size(pe)
        if pesize != int(ttsize):
            raise Exception('Population/Employment vector not same size as TAZ!!!')
        nTAZ = ttsize
        print "square is fine, import completed"
        
        
        print "creating internal cost"
        #Internal cost: cost of ppl going to work within own TAZ
#        replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
#                    +3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
#                    replace with 1 if lower than 1        
        dist = (2./3) * (area/pi)**0.5
        intci = 11.5375 * dist / 15 + 0.469 * dist
        intcp = 11.5375 * dist / 3
        
        #make diagonal (Origin = destination)
        I = np.identity(nTAZ)
        intci = intci*I
        intcp = intcp*I
        
        print "reshaping..."
        ttcosti = np.reshape(ttd['cost'],(nTAZ, nTAZ)) + intci
        ttcostp = np.reshape(ttp['cost'],(nTAZ, nTAZ)) + intcp
        
        
        print "calculate Sij"
        #New transit share
        deltaC = ttcostp/ttcosti
        exx = np.exp(c1+c2*deltaC)
        sij = exx/(1+exx)
        outSij = sij.reshape(nTAZ**2,1)
        outCSVsij = inSpace+'CSV/Sij'+str(currentIter)+'.csv'
        print "Writing transit share to", outCSVsij
        
        with open(outCSVsij, 'wb') as f:
            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')

        
        print "population and employment"
        #Gravity prediction
        pop = pe['pop'] ** beta1
        pop = np.matrix(pop)
        emp = pe['emp'] ** beta2
        emp = np.matrix(emp)

        print "final matrix calculation"
        FTT = G * np.array(pop.T * emp) * (sij*ttcostp + (1-sij)*ttcosti)**tau
        pFTT= FTT * (1-sij)
        pFTT= pFTT.reshape(1,nTAZ**2)

        # 2 period model treatment (temporary)
        # Without proper time disaggregated data we won't be able to properly
        # estimate the Sij across time periods (survey from SCAG might help)
        # So currently hard code using literature 4.2% (Small 1982)
        outFTT['flow'] = pFTT*.958    
        outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'-P.csv'
        print "Writing output to", outCSV
        with open(outCSV, 'wb') as f:
            np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')

        outFTT['flow'] = pFTT*.042
        outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'-OP.csv'
        print "Writing output to", outCSV
        with open(outCSV, 'wb') as f:
            np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')


    except Exception as e:
        tb = sys.exc_info()[2]
        print "Error occurred in ModUpdateFlow %i" % tb.tb_lineno 
        print e
    
    #finally:
        #print "Code ends on ", time.strftime("%d/%m/%Y - %H:%M:%S")


#def update_2p_backup(inSpace, currentIter, inTTp, penalty):
#    try:
#        from math import exp, sqrt, pi
#        import numpy as np
#        import sys
#        
#        #print "Code starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
#        #Parameters
#        c1 = 5.45
#        c2 = -5.05
#        G = exp(-3.289)
#        beta1 = 0.535
#        beta2 = 0.589
#        tau = -2.077
#        
#    
#        #import various matrices
#        fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
#        tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
#        petype = [('oid','i8'),('emp','f8'),('pop','f8')]
#        areatype = [('oid','i8'),('area','f8')]
#        
#        #import from inFlow
#        #This is used as OUTPUT TEMPLATE
#        outFTT = inSpace + "inFlow.csv"
#        outFTT = readcsv(outFTT, fdtype, incol = 3, sort = [0,1], header = None)
#        
#        #TT Cost (pub)
#        #Post/PRE as SEPARATE CSV FILE
#        print "importing TTcost for Transit"
#        ttp = readcsv(inTTp, tttype, incol = 4, sort = [0,1], header = True)
#        
#        print "importing TTcost for driving (peak)"
#        #TT Cost (driving, CURRENT)
#        inTTdp = inSpace+"CSV/TTP.csv"
#        ttdp = readcsv(inTTdp, tttype, incol = 4, sort = [0,1], header = None)
#        inTTdop = inSpace+"CSV/TTOP.csv"
#        ttdop = readcsv(inTTdop, tttype, incol = 4, sort = [0,1], header = None)
#        
#        
#        #print "check sorting"
#        #make sure both TT costs are sorted correctly:
#        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
#        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
#        #    raise Exception('Driving and Transit TT not match!')
#        #print "sorting is fine"
#        
#        print "importing census"
#        #Population & employment
#        inPE = inSpace+"census.csv"        
#        pe = readcsv(inPE, petype, incol = 3, sort = [0], header = True)
#        
#        print "importing TAZ area"
#        inArea = inSpace+"TAZarea.csv"        
#        area = readcsv(inArea, areatype, incol=2, sort=[0], header = True)
#        area = area['area']
#        
#        print "testing squareness"
#        #Test square of TTcost and TTcostpub, test same size of pop/emp
#        ttsize = sqrt(np.size(ttdp))
#        if ttsize != int(ttsize):
#            raise Exception('Driving TT cost at peak not square!!!')
#        ttsize = sqrt(np.size(ttdop))
#        if ttsize != int(ttsize):
#            raise Exception('Driving TT cost offpeak not square!!!')
#        ttsize = sqrt(np.size(ttp))
#        if ttsize != int(ttsize):
#            raise Exception('Transit TT cost not square!!!')
#        pesize = np.size(pe)
#        if pesize != int(ttsize):
#            raise Exception('Population/Employment vector not same size as TAZ!!!')
#        nTAZ = ttsize
#        print "square is fine, import completed"
#        
#        
#        print "creating internal cost"
#        #Internal cost: cost of ppl going to work within own TAZ
##        replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
##                    +3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
##                    replace with 1 if lower than 1        
#        dist = (2./3) * (area/pi)**0.5
#        intci = 11.5375 * dist / 15 + 0.469 * dist
#        intcp = 11.5375 * dist / 3
#        
#        #make diagonal (Origin = destination)
#        I = np.identity(nTAZ)
#        intci = intci*I
#        intcp = intcp*I
#        
#        print "reshaping..."
#        ttcosti_p = np.reshape(ttdp['cost'],(nTAZ, nTAZ)) + intci
#        ttcosti_op = np.reshape(ttdop['cost'],(nTAZ, nTAZ)) + intci + penalty
#        ttcostp_p = np.reshape(ttp['cost'],(nTAZ, nTAZ)) + intcp
#        ttcostp_op = np.reshape(ttp['cost'],(nTAZ, nTAZ)) + intcp + penalty
#        
#        
#        print "calculate Sij"
#        # New transit share
#        # V is the value function, as opposed to in the two period model where 
#        # we have this c1+c2*deltaC
#        # Vi is value for ind transport, Vp is value for pub transit
##        eVi_p = np.exp(c1+c2*(ttcostp_p/ttcosti_p))
##        eVp_p = np.exp(c1+c2*(ttcosti_p/ttcostp_p))
##        eVi_op = np.exp(c1+c2*(ttcostp_op/ttcosti_op))
##        eVp_op = np.exp(c1+c2*(ttcosti_op/ttcostp_op))
#        c1 = 0
#        c2 = 1
#        eVi_p = np.exp(c1+c2*(1./ttcosti_p))
#        eVp_p = np.exp(c1+c2*(1./ttcostp_p))
#        eVi_op = np.exp(c1+c2*(1./ttcosti_op))
#        eVp_op = np.exp(c1+c2*(1./ttcostp_op))
#        sumeV = eVi_p + eVp_p + eVi_op + eVp_op
#
#        # STILL NEED TO OUTPUT ALL SHARES
#        siji_p = eVi_p/sumeV
#        siji_op = eVi_op/sumeV
#        sijp_p = eVp_p/sumeV
#        sijp_op = eVp_op/sumeV
#
#        # We don't care about saving the transit shares
#        outSij = siji_p.reshape(nTAZ**2,1)
#        outCSVsij = inSpace+'CSV/Siji_p'+str(currentIter)+'.csv'
#        print "Writing transit share to", outCSVsij
#        
#        with open(outCSVsij, 'wb') as f:
#            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')
#
#        outSij = siji_op.reshape(nTAZ**2,1)
#        outCSVsij = inSpace+'CSV/Siji_op'+str(currentIter)+'.csv'
#        print "Writing transit share to", outCSVsij
#        
#        with open(outCSVsij, 'wb') as f:
#            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')
#
#        outSij = sijp_p.reshape(nTAZ**2,1)
#        outCSVsij = inSpace+'CSV/Sijp_p'+str(currentIter)+'.csv'
#        print "Writing transit share to", outCSVsij
#        
#        with open(outCSVsij, 'wb') as f:
#            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')
#
#        outSij = sijp_op.reshape(nTAZ**2,1)
#        outCSVsij = inSpace+'CSV/Sijp_op'+str(currentIter)+'.csv'
#        print "Writing transit share to", outCSVsij
#        
#        with open(outCSVsij, 'wb') as f:
#            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')
#
#
#        
#        print "population and employment"
#        #Gravity prediction
#        pop = pe['pop'] ** beta1
#        pop = np.matrix(pop)
#        emp = pe['emp'] ** beta2
#        emp = np.matrix(emp)
#        
#        print "final matrix calculation"
#        # Flow = G P^beta1 E^beta2 [Sijp_p x Cpub + Siji_p x Cind + Sijp_op x Cpub + Siji_op x Cind]^tau
#        # PEAK FIRST
#        FTT = G * np.array(pop.T * emp) * (sijp_p*ttcostp_p + siji_p*ttcosti_p + sijp_op*ttcostp_op + siji_p*ttcosti_op)**tau
#        pFTT= FTT * siji_p
#        pFTT= pFTT.reshape(1,nTAZ**2)
#        outFTT['flow'] = pFTT
#        
#        outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'-P.csv'
#        print "Writing output to", outCSV
#        
#        with open(outCSV, 'wb') as f:
#            np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')
#
#        del pFTT
#
#        pFTT= FTT * siji_op
#        pFTT= pFTT.reshape(1,nTAZ**2)
#        outFTT['flow'] = pFTT
#        
#        outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'-OP.csv'
#        print "Writing output to", outCSV
#        
#        with open(outCSV, 'wb') as f:
#            np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')
#
#
#    except Exception as e:
#        tb = sys.exc_info()[2]
#        print "Error occurred in ModUpdateFlow %i" % tb.tb_lineno 
#        print e
#    
#    #finally:
#        #print "Code ends on ", time.strftime("%d/%m/%Y - %H:%M:%S")


def update(inSpace, currentIter, inTTp):
    try:
        from math import exp, sqrt, pi
        import numpy as np
        import sys
        
        #print "Code starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
        #Parameters
        c1 = 5.45
        c2 = -5.05
        G = exp(-3.289)
        beta1 = 0.535
        beta2 = 0.589
        tau = -2.077
        
    
        #import various matrices
        fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
        tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        petype = [('oid','i8'),('emp','f8'),('pop','f8')]
        areatype = [('oid','i8'),('area','f8')]
        
        #import from inFlow
        #This is used as OUTPUT TEMPLATE
        outFTT = inSpace + "inFlow.csv"
        outFTT = readcsv(outFTT, fdtype, incol = 3, sort = [0,1], header = None)
        
        #TT Cost (pub)
        #Post/PRE as SEPARATE CSV FILE
        print "importing TTcost for Transit"
        ttp = readcsv(inTTp, tttype, incol = 4, sort = [0,1], header = True)
        
        print "importing TTcost for driving (current)"
        #TT Cost (driving, CURRENT)
        inTTd = inSpace+"CSV/TT.csv"
        #inTTd = inSpace+"TTdrv.csv"
        ttd = readcsv(inTTd, tttype, incol = 4, sort = [0,1], header = None)
        
        #print "check sorting"
        #make sure both TT costs are sorted correctly:
        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
        #    raise Exception('Driving and Transit TT not match!')
        #print "sorting is fine"
        
        print "importing census"
        #Population & employment
        inPE = inSpace+"census.csv"        
        pe = readcsv(inPE, petype, incol = 3, sort = [0], header = True)
        
        print "importing TAZ area"
        inArea = inSpace+"TAZarea.csv"        
        area = readcsv(inArea, areatype, incol=2, sort=[0], header = True)
        area = area['area']
        
        print "testing squareness"
        #Test square of TTcost and TTcostpub, test same size of pop/emp
        ttsize = sqrt(np.size(ttd))
        if ttsize != int(ttsize):
            raise Exception('Driving TT cost not square!!!')
        ttsize = sqrt(np.size(ttp))
        if ttsize != int(ttsize):
            raise Exception('Transit TT cost not square!!!')
        pesize = np.size(pe)
        if pesize != int(ttsize):
            raise Exception('Population/Employment vector not same size as TAZ!!!')
        nTAZ = ttsize
        print "square is fine, import completed"
        
        
        print "creating internal cost"
        #Internal cost: cost of ppl going to work within own TAZ
#        replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
#                    +3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
#                    replace with 1 if lower than 1        
        dist = (2./3) * (area/pi)**0.5
        intci = 11.5375 * dist / 15 + 0.469 * dist
        intcp = 11.5375 * dist / 3
        
        #make diagonal (Origin = destination)
        I = np.identity(nTAZ)
        intci = intci*I
        intcp = intcp*I
        
        print "reshaping..."
        ttcosti = np.reshape(ttd['cost'],(nTAZ, nTAZ)) + intci
        ttcostp = np.reshape(ttp['cost'],(nTAZ, nTAZ)) + intcp
        
        
        print "calculate Sij"
        #New transit share
        deltaC = ttcostp/ttcosti
        exx = np.exp(c1+c2*deltaC)
        sij = exx/(1+exx)
        outSij = sij.reshape(nTAZ**2,1)
        outCSVsij = inSpace+'CSV/Sij'+str(currentIter)+'.csv'
        print "Writing transit share to", outCSVsij
        
        with open(outCSVsij, 'wb') as f:
            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')


        
        print "population and employment"
        #Gravity prediction
        pop = pe['pop'] ** beta1
        pop = np.matrix(pop)
        emp = pe['emp'] ** beta2
        emp = np.matrix(emp)
        
        print "final matrix calculation"
        FTT = G * np.array(pop.T * emp) * (sij*ttcostp + (1-sij)*ttcosti)**tau
        pFTT= FTT * (1-sij)
        pFTT= pFTT.reshape(1,nTAZ**2)
        outFTT['flow'] = pFTT
        
        outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'.csv'
        print "Writing output to", outCSV
        
        with open(outCSV, 'wb') as f:
            np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')


    except Exception as e:
        tb = sys.exc_info()[2]
        print "Error occurred in ModUpdateFlow %i" % tb.tb_lineno 
        print e
    
    #finally:
        #print "Code ends on ", time.strftime("%d/%m/%Y - %H:%M:%S")


if __name__ == "__mai__":
    inSpace = "E:/DATA2/"
    currentIter = 1
    inTTp = inSpace + "TTpubPost.csv"
    try:
        from math import exp, sqrt, pi
        from operator import itemgetter
        import numpy as np
        import numexpr as ne
        import sys
        
        #print "Code starts on ", time.strftime("%d/%m/%Y - %H:%M:%S")
        #Parameters
        c1 = 5.45
        c2 = -5.05
        G = exp(-3.289)
        beta1 = 0.535
        beta2 = 0.589
        tau = -2.077
        
    
        #import various matrices
        fdtype = [('oid','i8'),('did','i8'),('flow','f8')]
        tttype = [('oid','i8'),('did','i8'),('name','S20'),('cost','f8')]
        petype = [('oid','i8'),('emp','f8'),('pop','f8')]
        areatype = [('oid','i8'),('area','f8')]
        
        #import from inFlow
        #This is used as OUTPUT TEMPLATE
        outFTT = inSpace + "inFlow.csv"
        outFTT = readcsv(outFTT, fdtype, incol = 3, sort = [0,1], header = None)
        
        #TT Cost (pub)
        #Post/PRE as SEPARATE CSV FILE
        print "importing TTcost for Transit"
        ttp = readcsv(inTTp, tttype, incol = 4, sort = [0,1], header = True)
        
        print "importing TTcost for driving (current)"
        #TT Cost (driving, CURRENT)
        inTTd = inSpace+"CSV/TT.csv"
        #inTTd = inSpace+"TTdrv.csv"
        ttd = readcsv(inTTd, tttype, incol = 4, sort = [0,1], header = None)
        
        #print "check sorting"
        #make sure both TT costs are sorted correctly:
        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
        #if any(ttp['oid'] != ttd['oid']) or any(ttp['did'] != ttd['did']):
        #    raise Exception('Driving and Transit TT not match!')
        #print "sorting is fine"
        
        print "importing census"
        #Population & employment
        inPE = inSpace+"census.csv"        
        pe = readcsv(inPE, petype, incol = 3, sort = [0], header = True)
        
        print "importing TAZ area"
        inArea = inSpace+"TAZarea.csv"        
        area = readcsv(inArea, areatype, incol=2, sort=[0], header = True)
        area = area['area']
        
        print "testing squareness"
        #Test square of TTcost and TTcostpub, test same size of pop/emp
        ttsize = sqrt(np.size(ttd))
        if ttsize != int(ttsize):
            raise Exception('Driving TT cost not square!!!')
        ttsize = sqrt(np.size(ttp))
        if ttsize != int(ttsize):
            raise Exception('Transit TT cost not square!!!')
        pesize = np.size(pe)
        if pesize != int(ttsize):
            raise Exception('Population/Employment vector not same size as TAZ!!!')
        nTAZ = ttsize
        print "square is fine, import completed"
        
        
        print "creating internal cost"
        #Internal cost: cost of ppl going to work within own TAZ
#        replace drvcost = 21.46*[(2/3)*(area_dest/_pi)^0.5]/15
#                    +3.752*[(2/3)*(area_dest/_pi)^0.5]/20 if oID_TAZ12A== dID_TAZ12A
#                    replace with 1 if lower than 1        
        dist = (2./3) * (area/pi)**0.5
        intci = 11.5375 * dist / 15 + 0.469 * dist
        intcp = 11.5375 * dist / 3
        
        #make diagonal (Origin = destination)
        I = np.identity(nTAZ)
        intci = intci*I
        intcp = intcp*I
        
        print "reshaping..."
        ttcosti = np.reshape(ttd['cost'],(nTAZ, nTAZ)) + intci
        ttcostp = np.reshape(ttp['cost'],(nTAZ, nTAZ)) + intcp
        
        
        print "calculate Sij"
        #New transit share
        deltaC = ttcostp/ttcosti
        exx = np.exp(c1+c2*deltaC)
        sij = exx/(1+exx)
#        outSij = sij.reshape(nTAZ**2,1)
#        outCSVsij = inSpace+'CSV/Sij'+str(currentIter)+'.csv'
#        print "Writing transit share to", outCSVsij
#        
#        with open(outCSVsij, 'wb') as f:
#            np.savetxt(f, outSij, delimiter=',', fmt='%7.10f')
        sij1 = ne.evaluate("(exp(c1+c2*(ttcostp/ttcosti)))/(1+exp(c1+c2*(ttcostp/ttcosti)))")

        
        print "population and employment"
        #Gravity prediction
        pop = pe['pop'] ** beta1
        pop = np.matrix(pop)
        emp = pe['emp'] ** beta2
        emp = np.matrix(emp)
        popemp = np.array(pop.T*emp)
        print "final matrix calculation"
        FTT = G * np.array(pop.T * emp) * (sij*ttcostp + (1-sij)*ttcosti)**tau
        FTT1 = ne.evaluate("G * popemp * (sij1*ttcostp + (1-sij1)*ttcosti)**tau")
        pFTT= FTT * (1-sij)
        pFTT= pFTT.reshape(1,nTAZ**2)
        outFTT['flow'] = pFTT
        
        outCSV = inSpace+'CSV/TTflow'+str(currentIter)+'.csv'
        print "Writing output to", outCSV
        
#        with open(outCSV, 'wb') as f:
#            np.savetxt(f, outFTT, delimiter=',', fmt='%7.0f, %7.0f, %7.10f')


    except Exception as e:
        tb = sys.exc_info()[2]
        print "Error occurred in ModUpdateFlow %i" % tb.tb_lineno 
        print e
    
#    finally:
#        print "Code ends on ", time.strftime("%d/%m/%Y - %H:%M:%S")