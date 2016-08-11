* Run A3.1-GenData-Pre-vs-Post before this script
* Script generates numbers for Table 9
clear all

use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-post.dta", clear

* Generate new Sij
* NOTE Driving cost does not change in this case.
gen costdiffpre = 5.45-5.05*(precost/predrvcost)
gen costdiffpost = 5.45-5.05*(postcost/predrvcost)
gen Sijpre = exp(costdiffpre)/(1+exp(costdiffpre))
gen Sijpost = exp(costdiffpost)/(1+exp(costdiffpost))
gen dflowpre = totalflow * (1-Sijpre)
gen dflowpost = totalflow * (1-Sijpost)
gen tflowpre = totalflow * (Sijpre)
gen tflowpost = totalflow * (Sijpost)
label var dflowpre "Driving flow pre expo"
label var dflowpost "Driving flow post expo"
label var tflowpre "Transit flow pre expo"
label var tflowpost "Transit flow post expo"
drop if oID == dID
cls




* Table 8 - Travel time saving
qui {
/* THESE ARE LOOKING AT THE DISTRIBUTIONAL EFFECT AND NOT TOTAL WELFARE
* People who remain transit riders
gen tflow = min(tflowpre, tflowpost)
gen ttpre = predps*tflow
gen ttpost = postdps*tflow
gen ttdiff = ttpost-ttpre

* People who switch to transit
gen switchT = tflowpost-tflowpre
gen dpsdiff = postdps - predrvdps
gen timesave = switchT * dpsdiff if switchT > 0
gen switchD = dflowpost-dflowpre
gen dpsdiffD = predrvdps - predps
replace timesave = switchD * dpsdiffD if switchD > 0
*/

* Total welfare effect = MB(TT) x \DeltaM(expansion)
** >> i.e. travel time saving in transit x number of people moved
* Calculate number of people moved
gen switchT = tflowpost-tflowpre
gen timediff = postdps - predps
gen timesave = switchT*timediff
}

qui {
n: di "Welfare from time saving:"
n: tabstat timesave, stat(sum)
}
beep
x
/* 
Travel time is given by the variable dps (distance/spd)
2 groups of people
group A: Transit riders that remain transit riders
    >> Time saving = # ppl X (pre time - post time)
group B: Drivers who switch to transit

*/

 binscatter predrvdps switcher if switcher > 0
