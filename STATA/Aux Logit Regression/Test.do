clear
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


* Generate shares
use test
ren share Si
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

sort id g*
/*
keep if id == "a"

tab var1

drop g*
*/
