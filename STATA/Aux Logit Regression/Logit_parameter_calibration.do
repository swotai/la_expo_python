/* 
Sij: 
i = transit/drive, transit = 0, drive = 1
j = peak/off peak, peak = 0, op = 1
*/

clear all
cd "C:\Users\Dennis\Desktop\Results\SETUP"


* temp file for generating shares.
set obs 1
generate var1 = 1 in 1
set obs 2
replace var1 = 2 in 2
set obs 3
replace var1 = 3 in 3
set obs 4
replace var1 = 4 in 4
gen v2 = .
tempfile temp
label define var1 1 "00 transit peak" 2 "01 transit offpeak" 3 "10 driving peak" 4 "11 driving offpeak"
label values var1 var1
save `temp', replace




* Import census CTPP data, calculate transit share
use Census1
gen drive = pdrive+ pcarpool2+ pcarpool3+ pcarpool4+ pcarpool6+ pcarpool7
gen trans = pbus+ pstreetcar+ psubway+ prailroad
gen Si = (100*trans)/(trans+drive)
sum
order ID Si
keep ID Si
tempfile Share
ren ID oID_TAZ12A
save `Share', replace

* Import transit data (Pre expo)
use pre4, clear

* Import cost data (driving)
merge 1:1 oID dID using drive4
drop if precost == . | drvcost == .
drop _merge

merge m:1 oID using `Share'
drop _merge

x
* Generate target share for regression for four periods
gen s00 = Si * .95
gen s01 = Si * .05
gen s10 = (1-Si) * .95
gen s11 = (1-Si) * .05
gen v2 = .
joinby v2 using `temp'

tab var1, gen(g)
drop v2
local scale = 1000
replace g1 = g1*s00*`scale'
replace g2 = g2*s01*`scale'
replace g3 = g3*s10*`scale'
replace g4 = g4*s11*`scale'

expand g1
expand g2
expand g3
expand g4


* Multinomial logits
/*
program define mylogit
    args lnf Xb
    replace `lnf' = -ln(1+exp(-`Xb')) if $ML_y1==1
    replace `lnf' = -`Xb' - ln(1+exp(-`Xb')) if $ML_y1==0
end

ml model lf mylogit (foreign = mp weight)
ml maximize
*/
