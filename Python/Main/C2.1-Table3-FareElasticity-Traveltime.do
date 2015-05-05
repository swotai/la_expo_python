* Run A3.1-GenData-Pre-vs-Shutdown before this script
* Generate Table 3-alt, which calculates the travel time elasticity:
* what happen to mode choice when travel time of transit increase by 1%

local featuresData = "C:/Users/Dennis/Desktop/Results/1028/TAZdisttofeatures.dta"


use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta", clear
drop post*
drop *post

* Fare Simulate travel increase by 1%
gen precost90 = (1.01*predps)*15 + fare
gen prelength90 = prelength

* Generate new Sij
gen costdiff = 5.45-5.05*(precost/predrvcost)
gen costdiff90 = 5.45-5.05*(precost90/predrvcost)
gen Sij = exp(costdiff)/(1+exp(costdiff))
gen Sij90 = exp(costdiff90)/(1+exp(costdiff90))
gen dflow = totalflow * (1-Sij)
gen tflow = totalflow * (Sij)
gen dflow90 = totalflow * (1-Sij90)
gen tflow90 = totalflow * (Sij90)
label var dflow "Driving flow"
label var dflow90 "Driving flow @ transit travel time = 101%"
label var tflow "Transit flow"
label var tflow90 "Transit flow @ transit travel time = 101%"

gen vmt = predrvlen*dflow
gen vmt90 = predrvlen*dflow90
gen tvmt = prelength*tflow
gen tvmt90 = prelength90*tflow90


* Merge with distance to feature data
gen id_taz12a = oID
merge m:1 id_taz12a using `featuresData'
drop _m
ren near* o_near*
replace id_taz12a = dID
merge m:1 id_taz12a using `featuresData'
drop _m
ren near* d_near*
drop id_taz12a


* Calculate percentage changes
gen pct_change_tr_OD = tflow90/tflow - 1
gen pct_change_tr_vmt = tvmt90/tvmt - 1
gen pct_change_dr_OD = dflow90/dflow - 1
gen pct_change_dr_vmt = vmt90/vmt -1

gen dcost = precost90/precost
sum dcost
sum dcost if o_nearmetro < 1.5 & d_nearmetro < 1.5

qui{
gen nearmeas = .
local crit = "o_nearmetro < 1 & d_nearmetro < 1 & premetrol > 0"
replace nearmeas = 1 if `crit'
local crit = "o_nearmetro > 1 & d_nearmetro > 1 & o_nearmetro < 3 & d_nearmetro < 3 & premetrol > 0"
replace nearmeas = 2 if `crit'
local crit = "o_nearmetro > 3 & d_nearmetro > 3 & o_nearmetro < 5 & d_nearmetro < 5 & premetrol > 0"
replace nearmeas = 3 if `crit'
local crit = "o_nearmetro > 5 & d_nearmetro > 5 & premetrol > 0"
replace nearmeas = 4 if `crit'
gen all = 0
}

table all, contents(mean pct_change_tr_OD mean pct_change_tr_vmt mean pct_change_dr_OD mean pct_change_dr_vmt)
table nearmeas, contents(mean pct_change_tr_OD mean pct_change_tr_vmt mean pct_change_dr_OD mean pct_change_dr_vmt)


beep
x



use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta", clear
drop post*
drop *post

* Fare Simulate travel increase by 1%
gen prelength90 = prelength
gen parking = (predrvdps*15+.469*predrvlen-predrvcost)<-5
replace parking = parking * 10
gen predrvcost101 = 1.01*predrvdps*15+.469*predrvlen+parking
replace predrvcost = predrvdps*15+.469*predrvlen+parking

* Generate new Sij
gen costdiff = 5.45-5.05*(precost/predrvcost)
gen costdiff90 = 5.45-5.05*(precost/predrvcost101)
gen Sij = exp(costdiff)/(1+exp(costdiff))
gen Sij90 = exp(costdiff90)/(1+exp(costdiff90))
gen dflow = totalflow * (1-Sij)
gen tflow = totalflow * (Sij)
gen dflow90 = totalflow * (1-Sij90)
gen tflow90 = totalflow * (Sij90)
label var dflow "Driving flow"
label var dflow90 "Driving flow @ transit travel time = 101%"
label var tflow "Transit flow"
label var tflow90 "Transit flow @ transit travel time = 101%"

gen vmt = predrvlen*dflow
gen vmt90 = predrvlen*dflow90
gen tvmt = prelength*tflow
gen tvmt90 = prelength90*tflow90


* Merge with distance to feature data
gen id_taz12a = oID
merge m:1 id_taz12a using `featuresData'
drop _m
ren near* o_near*
replace id_taz12a = dID
merge m:1 id_taz12a using `featuresData'
drop _m
ren near* d_near*
drop id_taz12a

* Calculate percentage changes
gen pct_change_tr_OD = tflow90/tflow - 1
gen pct_change_tr_vmt = tvmt90/tvmt - 1
gen pct_change_dr_OD = dflow90/dflow - 1
gen pct_change_dr_vmt = vmt90/vmt -1

/*gen dcost = precost90/precost
sum dcost
sum dcost if o_nearmetro < 1.5 & d_nearmetro < 1.5*/

qui{
gen nearmeas = .
local crit = "o_nearmetro < 1 & d_nearmetro < 1 & premetrol > 0"
replace nearmeas = 1 if `crit'
local crit = "o_nearmetro > 1 & d_nearmetro > 1 & o_nearmetro < 3 & d_nearmetro < 3 & premetrol > 0"
replace nearmeas = 2 if `crit'
local crit = "o_nearmetro > 3 & d_nearmetro > 3 & o_nearmetro < 5 & d_nearmetro < 5 & premetrol > 0"
replace nearmeas = 3 if `crit'
local crit = "o_nearmetro > 5 & d_nearmetro > 5 & premetrol > 0"
replace nearmeas = 4 if `crit'
gen all = 0
}

table all, contents(mean pct_change_tr_OD mean pct_change_tr_vmt mean pct_change_dr_OD mean pct_change_dr_vmt)
table nearmeas, contents(mean pct_change_tr_OD mean pct_change_tr_vmt mean pct_change_dr_OD mean pct_change_dr_vmt)

x
beep
