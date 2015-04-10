* Run A3.1-GenData-Pre-vs-Post before this script
* Script generates numbers for Table 4, 5, and 6

use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-cffastall.dta", clear

* Generate new Sij
* NOTE Driving cost does not change in this case.
gen costdiffpre = 5.45-5.05*(precost/predrvcost)
gen costdiffpost = 5.45-5.05*(postcost/predrvcost)
gen costdiffpost1 = 5.45-5.05*(post1cost/predrvcost)
gen Sijpre = exp(costdiffpre)/(1+exp(costdiffpre))
gen Sijpost = exp(costdiffpost)/(1+exp(costdiffpost))
gen Sijpost1 = exp(costdiffpost1)/(1+exp(costdiffpost1))
gen dflowpre = totalflow * (1-Sijpre)
gen dflowpost = totalflow * (1-Sijpost)
gen dflowpost1 = totalflow * (1-Sijpost1)
gen tflowpre = totalflow * (Sijpre)
gen tflowpost = totalflow * (Sijpost)
gen tflowpost1 = totalflow * (Sijpost1)
label var dflowpre "Driving flow pre expo"
label var dflowpost "Driving flow post expo"
label var dflowpost1 "Driving flow FAST expo"
label var tflowpre "Transit flow pre expo"
label var tflowpost "Transit flow post expo"
label var tflowpost1 "Transit flow FAST expo"

gen dvmtpre = drvlength*dflowpre

drop if oID == dID

cls

* Table 3 part 1: original
qui {
gen dpsspd = drvlength / predrvdps
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
di "**Hetero delay(expand) =" `delay1'-`delay0'

}

* OD Level Table
qui{
gen ddflow = dflowpost-dflowpre
gen dtflow = tflowpost-tflowpre
gen diff_vmt_drv = ddflow * drvlength
gen diff_vmt_transit = dtflow * prelength
}

qui {
tabstat dflowpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dflowpre = tab[1,1]
di "**baseline number of car trips per day am peak = " `dflowpre'

tabstat dvmtpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dvmtpre = tab[1,1]
di "**baseline number of veh mile per day am peak = " `dvmtpre'
di "**baseline annual vehicle mile annual = " %14.2f 2*260*`dvmtpre'

tabstat ddflow, stat(sum) save
matrix tab = r(StatTotal)
local ddflow = tab[1,1]
tabstat dtflow, stat(sum) save
matrix tab = r(StatTotal)
local dtflow = tab[1,1]
di "**number trips change to driving = " `ddflow'
di "**number trips change to transit = " `dtflow'

tabstat diff_vmt_drv, stat(sum) save
matrix tab = r(StatTotal)
local diff_vmt_drv = tab[1,1]
di "**removed driving miles per day am peak = " `diff_vmt_drv'
di "**removed driving miles annual = " %14.2f 2*260*`diff_vmt_drv'

tabstat diff_vmt_transit, stat(sum) save
matrix tab = r(StatTotal)
local diff_vmt_transit = tab[1,1]
di "**removed transit miles per day am peak = " `diff_vmt_transit'
di "**removed transit miles annual = " %14.2f 2*260*`diff_vmt_transit'
gen switchT = tflowpost-tflowpre
gen timediff = postdps - predps
gen timesave = switchT*timediff
}

qui {
	n: di "Table 8"
	n: di "**Hetero delay(Expansion) =" `delay1'-`delay0'
	n: di "**baseline number of veh mile per day am peak = " `dvmtpre'
	n: di "**Change in driving trips per day am peak = " `ddflow'
	n: di "**Change in driving miles per day am peak = " `diff_vmt_drv'
	n: di "**Change in transit trips per day am peak = " `dtflow'
	n: di "**Change in transit miles per day am peak = " `diff_vmt_transit'
	n: di "Travel Time Saving:"
	n: tabstat timesave, stat(sum)
}


* Table 3 part 2: Faster Expo
qui {
sum delay0 delay1 flow0 flow1 pctddflow spd1
drop delay0 delay1 flow0 flow1 pctddflow spd1

gen delay0 = 65/dps-1
gen flow0 = 500+log(dpsspd/65)/(-.000191)
gen pctddflow = dflowpost1/dflowpre
gen flow1 = flow0*pctddflow
gen spd1 = 65*exp(-.000191*(flow1-500))
gen delay1 = 65/spd1 -1
sum delay0 [iw=dflowpre], meanonly
local delay0 = `r(mean)'
sum delay1 [iw=dflowpre], meanonly
local delay1 = `r(mean)'
di "**Hetero delay(expand) =" `delay1'-`delay0'
sum delay0 delay1 flow0 flow1 pctddflow spd1
}

* OD Level Table
qui{
gen ddflow1 = dflowpost1-dflowpre
gen dtflow1 = tflowpost1-tflowpre
gen diff_vmt_drv1 = ddflow1 * drvlength
gen diff_vmt_transit1 = dtflow1 * prelength
}

qui {
tabstat dflowpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dflowpre = tab[1,1]
di "**baseline number of car trips per day am peak = " `dflowpre'

tabstat dvmtpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dvmtpre = tab[1,1]
di "**baseline number of veh mile per day am peak = " `dvmtpre'
di "**baseline annual vehicle mile annual = " %14.2f 2*260*`dvmtpre'

tabstat ddflow1, stat(sum) save
matrix tab = r(StatTotal)
local ddflow = tab[1,1]
tabstat dtflow1, stat(sum) save
matrix tab = r(StatTotal)
local dtflow = tab[1,1]
di "**number trips change to driving = " `ddflow'
di "**number trips change to transit = " `dtflow'

tabstat diff_vmt_drv1, stat(sum) save
matrix tab = r(StatTotal)
local diff_vmt_drv = tab[1,1]
di "**removed driving miles per day am peak = " `diff_vmt_drv'
di "**removed driving miles annual = " %14.2f 2*260*`diff_vmt_drv'

tabstat diff_vmt_transit1, stat(sum) save
matrix tab = r(StatTotal)
local diff_vmt_transit = tab[1,1]
di "**removed transit miles per day am peak = " `diff_vmt_transit'
di "**removed transit miles annual = " %14.2f 2*260*`diff_vmt_transit'
gen switchT1 = tflowpost1-tflowpre
gen timediff1 = post1dps - predps
gen timesave1 = switchT1*timediff1
}


qui {
	n: di "Table 8"
	n: di "**Hetero delay(Expansion) =" `delay1'-`delay0'
	n: di "**baseline number of veh mile per day am peak = " `dvmtpre'
	n: di "**Change in driving trips per day am peak = " `ddflow'
	n: di "**Change in driving miles per day am peak = " `diff_vmt_drv'
	n: di "**Change in transit trips per day am peak = " `dtflow'
	n: di "**Change in transit miles per day am peak = " `diff_vmt_transit'
	n: di "Travel Time Saving:"
	n: tabstat timesave1, stat(sum)
}
