* This script generates All counterfactual tables

clear all
local TransitPrePath = "C:/Users/Dennis/Desktop/CalcTransit/Pre/CSV"
local TransitPostPath = "C:/Users/Dennis/Desktop/CalcTransit/Post/CSV"
local TransitPostCFPath = "C:/Users/Dennis/Desktop/CalcTransit/CF-fast/CSV"
local TransitPostCF2Path = "C:/Users/Dennis/Desktop/CalcTransit/CF-fastall/CSV"
local outputFolder = "C:/Users/Dennis/Desktop/Results/1028"
insheet using `TransitPrePath'/Transdetflow1.csv
sort v1
ren v1 idstn
ren v2 preflow
label var preflow "Transit pre flow"
tempfile temp
save `temp'
insheet using `TransitPostPath'/Transdetflow1.csv, clear
sort v1
ren v1 idstn
ren v2 postflow
label var postflow "Transit post flow"
merge 1:1 idstn using `temp'
drop _m
save `temp', replace
insheet using `TransitPostCFPath'/Transdetflow1.csv, clear
sort v1
ren v1 idstn
ren v2 post1flow
label var post1flow "Transit post CF flow"
merge 1:1 idstn using `temp'
drop _m
save `temp', replace
insheet using `TransitPostCF2Path'/Transdetflow1.csv, clear
sort v1
ren v1 idstn
ren v2 post2flow
label var post2flow "Transit post CF flow fastall"
merge 1:1 idstn using `temp'
drop _m
save `temp', replace

gen dflowpct = (postflow/preflow)-1
gen dflow1pct = (post1flow/postflow)-1
gen dflow2pct = (post2flow/postflow)-1
sum
save `temp', replace

*Export csv for mapping

*save `outputFolder'/ChangeStn-Flow, replace
*export excel using `outputFolder'/stnflow-0327.xls, ///
*       sheet("stnflow-0327") firstrow(variables) replace


gen line = int(idstn/100)
label define LineName 801 "Blue" 802 "Red" 803 "Green" 804 "Gold" 806 "Expo" 910 "Silver" 901 "Orange"
label values line LineName

*Table 2
tabstat dflowpct, by(line) stat(mean min p50 max) nototal
tabstat dflow1pct, by(line) stat(mean min p50 max) nototal
tabstat dflow2pct, by(line) stat(mean min p50 max) nototal

*Table 1

collapse (max)  maxpreflow=preflow maxpostflow=postflow maxpost1flow=post1flow maxpost2flow=post2flow ///
(mean) avgpreflow=preflow avgpostflow=postflow avgpost1flow=post1flow avgpost2flow=post2flow ///
, by(line)


di "Browse data and copy/paste to excel"

x

/*
Ballpark Ridership
801  blue   90000
802  red    160000
803  green  43000
804  gold   43000
806  expo   27000

Gravity Flow output

+-----------------------------------------+
|  line    preflow   postflow      ldflow |
|-----------------------------------------|
|  Blue   360119.9   368347.7    .0225905 |
|   Red   397425.4   399157.9    .0043498 |
| Green   124282.7   120939.7   -.0272666 |
|  Gold     112292   116031.9    .0327619 |
|  Expo      59391   125691.5     .749688 |
+-----------------------------------------+
