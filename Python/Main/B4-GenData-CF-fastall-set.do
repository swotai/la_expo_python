* Script generates statistics for CF set
clear all
cd "C:/Users/Dennis/Desktop/CalcTransit/CF-fastall-set/"

tempfile dflowpre
tempname memhold
local outfile = "C:/Users/Dennis/Desktop/Results/1028/CF-fastall-set.dta"
postfile `memhold' speed timesave tflow avgtspd ///
	bluemax redmax greenmax goldmax expomax orangemax silvermax ///
	using `outfile', replace
local defdelay = 0

* No Metro case
qui {
	use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta", clear
	drop if oID == dID
	gen costdiffpost = 5.45-5.05*(postcost/predrvcost)
	gen Sijpost = exp(costdiffpost)/(1+exp(costdiffpost))
	gen dflowpost = totalflow * (1-Sijpost)
	gen tflowpost = totalflow * (Sijpost)
	gen ttpost = postdps*tflowpost
	sum ttpost, meanonly
	local traveltimepost = 0
	sum tflowpost, meanonly
	local tflownometro = r(sum)
	sum postdps [iw=tflowpost], meanonly
	local nometrospd = r(mean)
	ren oID oid
	ren dID did
	drop pre*
	ren dflowpost dflowpre
	ren tflowpost tflowpre
	ren postdps predps
	keep oid did dflowpre tflowpre predps
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
	post `memhold' (-1) (`traveltimepost') (`tflownometro') (`nometrospd') ///
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
	merge 1:1 oid did using `dflowpre'
	
	gen switchT = tflowpost-tflowpre
	gen timediff = postdps - predps
	gen timesave = switchT*timediff
	
	sum timesave, meanonly
	local timesaved = r(sum)
	sum tflowpost, meanonly
	local tflownow = r(sum)
	sum postdps [iw=tflowpost], meanonly
	local tspdnow = r(mean)
	
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
	post `memhold' (`currentSpeed') (`timesaved') (`tflownow') (`tspdnow') ///
		(`l1p100') (`l2p100') (`l3p100') (`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: speed = " `currentSpeed'
}
}

postclose `memhold'

use `outfile', clear

