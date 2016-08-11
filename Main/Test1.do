clear all

use "C:/Users/Dennis/Desktop/Results/1028/CF-fastall-set.dta", clear
cd "D:\Dropbox\Cornell\LA Expo Line Project\Data Files\Gravity Flow Prediction\Output"

drop bluemax - silver

* Calculate Congestion relief, Pollution relief
* Pollution relief
gen vmtdiff = dvmt - dvmt[1]
gen bPollute = vmtdiff*(1.102*10^(-6))*(439.4*21 + .07*15000 + .09*4100)

* Congestion relief
* 0.25 = 15$ VOT per hour convert to per min
* Following the excel file we use the "no metro" driving vmt.

gen bCongest = dvmt[1]*0.25*delay

* Travel time savings
gen timesaved = timesave - timesave[1]
gen bTraveltime = timesaved * 15

order b*, last

* Total benefit (Convert to annual)
replace bPollute = -1*bPollute*2*260
replace bCongest = -1*bCongest*2*260
replace bTraveltime = -1*bTraveltime*2*260
gen bTotal = bPollute + bCongest + bTraveltime

*/
