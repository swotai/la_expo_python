* Script generates statistics for CF set
clear all
cd "C:/Users/Dennis/Desktop/CalcTransit/CF-fastall-set/"

tempfile dflowpre
tempname memhold
local outfile = "C:/Users/Dennis/Desktop/Results/1028/CF-fastall-set.dta"
postfile `memhold' speed traveltimesave ///
	bluemax redmax greenmax goldmax expomax orangemax silvermax ///
	using `outfile', replace
local defdelay = 0

qui {/*
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
	sum ttpre, meanonly
	local traveltimepre = r(sum)
	sum ttpost, meanonly
	local traveltimepost = r(sum)
	ren oID oid
	ren dID did
	keep oid did dflowpre
	save `dflowpre'
}

qui {
	* Pre
	* read station flow, get median and max flow
	insheet using "C:/Users/Dennis/Desktop/CalcTransit/Pre/CSV/Transdetflow1.csv", clear
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
	post `memhold' (0) (`traveltimepre') (`defdelay') (`l1p100') (`l2p100') (`l3p100') ///
		(`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: pre"
}

qui {
	* Post
	* read station flow, get median and max flow
	insheet using "C:/Users/Dennis/Desktop/CalcTransit/Post/CSV/Transdetflow1.csv", clear
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
	post `memhold' (1) (`traveltimepost') (`defdelay') (`l1p100') (`l2p100') (`l3p100') ///
		(`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: post"*/
}

* add No Metro case
qui {
	use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta", clear
	drop if oID == dID
	gen costdiffpost = 5.45-5.05*(postcost/predrvcost)
	gen Sijpost = exp(costdiffpost)/(1+exp(costdiffpost))
	gen dflowpost = totalflow * (1-Sijpost)
	gen tflowpost = totalflow * (Sijpost)
	gen ttpost = postdps*tflowpost
	sum ttpost, meanonly
	local traveltimenometro = r(sum)
	
	ren oID oid
	ren dID did
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
	post `memhold' (-1) (`traveltimepost') (`defdelay') (`l1p100') (`l2p100') (`l3p100') ///
		(`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: nometro"
}


*Start looping through the CF set
qui {
forvalues currentSpeed = 15/34 {
	use aTransitMatrix`currentSpeed', clear
	drop if oid == did
	gen tt = postdps * tflow
	sum tt, meanonly
	local traveltime = r(sum)
	merge 1:1 oid did using `dflowpre'
	
	gen dpsspd = predrvlen / predrvdps
	drop if dps > 65
	gen delay0 = 65/dps-1
	gen flow0 = 500+log(dpsspd/65)/(-.000191)
	gen pctddflow = dflow/dflowpre
	gen flow1 = flow0*pctddflow
	gen spd1 = 65*exp(-.000191*(flow1-500))
	gen delay1 = 65/spd1 -1
	sum delay0 [iw=dflowpre], meanonly
	local delay0 = `r(mean)'
	sum delay1 [iw=dflowpre], meanonly
	local delay1 = `r(mean)'
	local delay = `delay1'-`delay0'


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
	post `memhold' (`currentSpeed') (`traveltime') (`delay') ///
		(`l1p100') (`l2p100') (`l3p100') (`l4p100') (`l5p100') (`l6p100') (`l7p100')
	n: di "Completed: speed = " `currentSpeed'
}
}

postclose `memhold'

use `outfile', clear
x

qui {
gen switchT = tflowpost-tflowpre
gen timediff = postdps - predps
gen timesave = switchT*timediff
}

