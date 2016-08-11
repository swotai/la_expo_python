* Script generates statistics for CF set
clear all
cd "C:/Users/Dennis/Desktop/CalcTransit/CF-fastall-set/"

tempfile dflowpre
tempname memhold
local outfile = "C:/Users/Dennis/Desktop/Results/1028/CF-fastall-set.dta"
postfile `memhold' speed timesave tflow dvmt avgtspd delay ///
	bluemax redmax greenmax goldmax expomax orangemax silvermax ///
	using `outfile', replace
local defdelay = 0

	use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-post.dta", clear
	drop if oID == dID
	gen costdiffpre = 5.45-5.05*(precost/predrvcost)
	gen costdiffpost = 5.45-5.05*(postcost/predrvcost)
	gen Sijpre = exp(costdiffpre)/(1+exp(costdiffpre))
	gen Sijpost = exp(costdiffpost)/(1+exp(costdiffpost))
	gen dflowpre = totalflow * (1-Sijpre)
	gen dflowpost = totalflow * (1-Sijpost)
	gen tflowpre = totalflow * (Sijpre)
	gen tflowpost = totalflow * (Sijpost)
	gen ttpre = predps*tflowpre
	gen ttpost = postdps*tflowpost
	gen dvmtpre = dflowpre * predrvlen
	gen dvmtpost = dflowpost * predrvlen
	sum ttpre, meanonly
	local traveltimepre = r(sum)
	sum ttpost, meanonly
	local traveltimepost = r(sum)
	sum tflowpre, meanonly
	local tflowpre = r(sum)
	sum tflowpost, meanonly
	local tflowpost = r(sum)
	sum dvmtpre, meanonly
	local dvmtpre = r(sum)
	sum dvmtpost, meanonly
	local dvmtpost = r(sum)
	sum predps [iw=tflowpre], meanonly
	local prespd = r(mean)
	sum postdps [iw=tflowpost], meanonly
	local postspd = r(mean)
	
	gen dpsspd = predrvlen / predrvdps
	drop if dps > 65
	gen delay0 = 65/dps-1
	gen flow0 = 500+log(dpsspd/65)/(-.000191)
	gen pctddflow = dflowpost/dflowpre
	gen flow1 = flow0*pctddflow
	gen spd1 = 65*exp(-.000191*(flow1-500))
	gen delay1 = 65/spd1 -1
	sum delay0 [iw=dflowpre], meanonly
	local delay0 = `r(mean)'
	sum delay1 [iw=dflowpre], meanonly
	local delay1 = `r(mean)'
	local delaynow = `delay1'-`delay0'
	
	gen switchT = tflowpost-tflowpre
	gen timediff = postdps - predps
	gen timesave = switchT*timediff
	sum timesave, meanonly
	local timesaved = r(sum)
	
	post `memhold' (11) (0) (`tflowpre') (`dvmtpre') (`prespd') (`defdelay') ///
		(0) (0) (0) (0) (0) (0) (0)
	post `memhold' (12) (`timesaved') (`tflowpost') (`dvmtpost') (`postspd') (`delaynow') ///
		(0) (0) (0) (0) (0) (0) (0)

postclose `memhold'

use `outfile', clear
x
* No Metro case
qui {
	use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta", clear
	drop if oID == dID
	gen costdiffpost = 5.45-5.05*(postcost/predrvcost)
	gen Sijpost = exp(costdiffpost)/(1+exp(costdiffpost))
	gen dflowpost = totalflow * (1-Sijpost)
	gen tflowpost = totalflow * (Sijpost)
	gen ttpost = postdps*tflowpost
	gen dvmtpost = dflowpost * predrvlen
	sum ttpost, meanonly
	local traveltimepost = 0
	sum tflowpost, meanonly
	local tflownometro = r(sum)
	sum dvmtpost, meanonly
	local dvmtnometro = r(sum)
	sum postdps [iw=tflowpost], meanonly
	local nometrospd = r(mean)
	ren oID oid
	ren dID did
	drop predps
	ren dflowpost dflowpre
	ren tflowpost tflowpre
	ren postdps predps
	keep oid did dflowpre tflowpre predps predrvlen predrvdps
	save `dflowpre'

	insheet using "C:/Users/Dennis/Desktop/CalcTransit/CF-nometro/CSV/Transdetflow1.csv", clear
	sort v1
	ren v1 idstn
	ren v2 flow
	gen line = int(idstn/100)
	drop if idstn == 80633 | idstn == 80634
	tabstat flow, by(line) stat(median max) save
	forvalues l = 1/7 {
		matrix def out`l' = r(Stat`l')
		local l`l'p100 = out`l'[2,1]
	}
	local delaybase = 0
	post `memhold' (-1) (`traveltimepost') (`tflownometro') (`dvmtnometro') (`nometrospd') (`delaybase') ///
		(`l1p100') (`l2p100') (`l3p100') (`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: nometro"
}


*Start looping through the CF set
qui {
forvalues currentSpeed = 15/34 {
	use aTransitMatrix`currentSpeed', clear
	drop if oid == did
	gen tt = postdps * tflow
	sum tt, meanonly
	ren tflow tflowpost
	ren dflow dflowpost
	merge 1:1 oid did using `dflowpre'
	
	gen switchT = tflowpost-tflowpre
	gen timediff = postdps - predps
	gen timesave = switchT*timediff
	gen dvmtpost = dflowpost * predrvlen
	
	sum timesave, meanonly
	local timesaved = r(sum)
	sum tflowpost, meanonly
	local tflownow = r(sum)
	sum dvmtpost, meanonly
	local dvmtnow = r(sum)
	sum postdps [iw=tflowpost], meanonly
	local tspdnow = r(mean)

	gen dpsspd = predrvlen / predrvdps
	drop if dps > 65
	gen delay0 = 65/dps-1
	gen flow0 = 500+log(dpsspd/65)/(-.000191)
	gen pctddflow = dflowpost/dflowpre
	gen flow1 = flow0*pctddflow
	gen spd1 = 65*exp(-.000191*(flow1-500))
	gen delay1 = 65/spd1 -1
	sum delay0 [iw=dflowpre], meanonly
	local delay0 = `r(mean)'
	sum delay1 [iw=dflowpre], meanonly
	local delay1 = `r(mean)'
	local delaynow = `delay1'-`delay0'
	
	insheet using "C:/Users/Dennis/Desktop/CalcTransit/CF-fastall-set/CSV/Transdetflow`currentSpeed'.csv", clear
	sort v1
	ren v1 idstn
	ren v2 flow
	gen line = int(idstn/100)
	drop if idstn == 80633 | idstn == 80634
	tabstat flow, by(line) stat(median max) save
	forvalues l = 1/7 {
		matrix def out`l' = r(Stat`l')
		local l`l'p100 = out`l'[2,1]
	}
	
	post `memhold' (`currentSpeed') (`timesaved') (`tflownow') (`dvmtnow') (`tspdnow') (`delaynow') ///
		(`l1p100') (`l2p100') (`l3p100') (`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: speed = " `currentSpeed'
}
}

postclose `memhold'

use `outfile', clear


beep

