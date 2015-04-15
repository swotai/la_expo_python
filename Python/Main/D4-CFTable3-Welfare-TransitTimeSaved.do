* Run A3.1-GenData-Pre-vs-Post before this script
* Script generates Table 3 in CF excel file
clear all

use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-cffastall.dta", clear
ren post1* post2*
merge 1:1 oID dID using "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-cffast.dta"
drop _m
order oID dID totalflow drvlength fare* pre* post*

* Generate new Sij
* NOTE Driving cost does not change in this case.
qui {
drop if oID == dID
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

gen costdiff1post = 5.45-5.05*(post1cost/predrvcost)
gen Sij1post = exp(costdiff1post)/(1+exp(costdiff1post))
gen dflow1post = totalflow * (1-Sij1post)
gen tflow1post = totalflow * (Sij1post)

gen costdiff2post = 5.45-5.05*(post2cost/predrvcost)
gen Sij2post = exp(costdiff2post)/(1+exp(costdiff2post))
gen dflow2post = totalflow * (1-Sij2post)
gen tflow2post = totalflow * (Sij2post)


* Table 8 - Travel time saving
* In Counterfactual comparison, for the sake of comparison,
* let's look at the transit rider speed change.
* People who remain transit riders
gen tflow = min(tflowpre, tflowpost)
gen ttpre = predps*tflow
gen ttpost = postdps*tflow
gen ttdiff = ttpost-ttpre

gen ttpost1 = post1dps*tflow
gen ttdiff1 = ttpost1-ttpost

gen ttpost2 = post2dps*tflow
gen ttdiff2 = ttpost2-ttpost


}

qui {
n: di "Transit rider time saving:"
n: tabstat ttpre ttpost ttdiff ttdiff1 ttdiff2, stat(sum)
n: di "Transit rider time saving (average trip):"
n: tabstat ttpre ttpost ttdiff ttdiff1 ttdiff2 [aweight = tflow], stat(mean)
}


