* This script generates Table 1, Table 2

clear all
local TransitPrePath = "C:/Users/Dennis/Desktop/CalcTransit/Pre/CSV"
local TransitPostPath = "C:/Users/Dennis/Desktop/CalcTransit/Post/CSV"
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

gen dflowpct = (postflow/preflow)-1
sum
save `temp', replace

*Export csv for mapping

save `outputFolder'/ChangeStn-Flow, replace
export excel using `outputFolder'/stnflow-0327.xls, ///
       sheet("stnflow-0327") firstrow(variables) replace


gen line = int(idstn/100)
label define LineName 801 "Blue" 802 "Red" 803 "Green" 804 "Gold" 806 "Expo" 910 "Silver" 901 "Orange"
label values line LineName

*Table 2
tabstat dflow, by(line) stat(mean min p50 max) nototal

*Table 1

collapse (sum) preflow postflow ///
(min)  minpreflow=preflow minpostflow=postflow ///
(max)  maxpreflow=preflow maxpostflow=postflow ///
(mean) avgpreflow=preflow avgpostflow=postflow ///
(p50)  midpreflow=preflow midpostflow=postflow ///
, by(line)

gen linepctdflow = postflow/preflow-1

list

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

*replace preflow = 0 in 84
*replace preflow = 0 in 85
collapse (sum) preflow postflow ///
(min)  minpreflow=preflow minpostflow=postflow ///
(max)  maxpreflow=preflow maxpostflow=postflow ///
(mean) avgpreflow=preflow avgpostflow=postflow ///
(p50)  midpreflow=preflow midpostflow=postflow ///
, by(line)

gen linepctdflow = postflow/preflow-1

*/

