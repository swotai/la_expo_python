clear all

use "C:/Users/Dennis/Desktop/Results/1028/CF-fastall-set.dta", clear
cd "D:\Dropbox\Cornell\LA Expo Line Project\Data Files\Gravity Flow Prediction\Output"

* Calculate Congestion relief, Pollution relief
* Pollution relief
gen vmtdiff = dvmt - dvmt[1]
gen bPollute = vmtdiff*(1.102*10^(-6))*(439.4*21 + .07*15000 + .09*4100)

* Congestion relief
* 0.25 = 15$ VOT per hour convert to per min
* Following the excel file we use the "no metro" driving vmt.
gen bCongest = dvmt[1]*0.25*delay

* Travel time savings
gen bTraveltime = timesave * 15 / 2

* Total benefit (Convert to annual)
replace bPollute = -1*bPollute*2*260
replace bCongest = -1*bCongest*2*260
replace bTraveltime = -1*bTraveltime*2*260
gen bTotal = bPollute + bCongest + bTraveltime
* Add adjustment
gen abPollute = bPollute * 2
gen abCongest = bCongest * 2
gen abTotal = abPollute + abCongest + bTraveltime

drop in 1/1
ren *max *
save CF-fastall-set.dta, replace

# delimit ;
twoway 
(line blue speed, lcolor(blue)) 
(line red speed, lcolor(red)) 
(line expo speed, lcolor(cyan)) 
(line green speed, lcolor(green)) 
(line gold speed, lcolor(gold)) 
(line orange speed, lcolor(orange)) 
(line silver speed, lcolor(gs12)),
title(Metro Max Station Flow)
subtitle(Line level performance at various metro speed)
ylabel(, labsize(vsmall))
ytitle(Flow)
xtitle(Metro speed mph)
note("Note: ""Orange and silver BRT lines remain their corresponding speeds");
graph export CF-Set-metroflow.png, replace;

replace timesave = -1*timesave;

twoway 
(line timesave speed) ,
title(Total time saved) 
subtitle(Compared to no-metro scenario) 
ytitle(Hours) 
xtitle(Metro speed mph) 
ylabel(, labsize(vsmall)) 
note("Note: "
"Time saved calculated as the number of people moved to transit system compared to the"
"no-metro scenario, multiply by the change in transit trip travel time, then aggregated") ;
graph export CF-Set-traveltimesaved.png, replace;

twoway 
(line tflow speed) ,
title(Total transit usage) 
subtitle(Compared to no-metro scenario) 
ytitle(Number of transit trips) 
xtitle(Metro speed mph) 
ylabel(, labsize(vsmall)) 
note("Note: "
"Time saved calculated as the number of people moved to transit system compared to the"
"no-metro scenario, multiply by the change in transit trip travel time, then aggregated") ;
graph export CF-Set-transitflow.png, replace;



graph bar (asis) bPollute bCongest bTraveltime, 
over(speed) stack ytitle(Dollar amount) ylabel(, labsize(vsmall) format(%16.0gc) angle(forty_five)) 
title(Total welfare effect of various Metro speeds) subtitle(Compared to no-Metro baseline scenario) 
note("Note:"
"Pollution reduction calculated by multiplying the driving vehicle miles removed with"
"the various emission parameters following Table 8, at each counterfactual speeds."
"Congestion relief calculated by calculating the reduction in delay per mile in highway"
"compared to the no-Metro case, multiply by the total driving trip miles."
"Graph reports annual figures.") 
legend(order(1 "Pollution reduction" 2 "Congestion relief" 3 "Travel time saving"));
graph export CF-Set-Welfarechange.png, replace;

graph bar (asis) abPollute abCongest bTraveltime, 
over(speed) stack ytitle(Dollar amount) ylabel(, labsize(vsmall) format(%16.0gc) angle(forty_five)) 
title(Total welfare effect of various Metro speeds-adjusted) subtitle(Compared to no-Metro baseline scenario) 
note("Note:"
"Pollution reduction calculated by multiplying the driving vehicle miles removed with"
"the various emission parameters following Table 8, at each counterfactual speeds."
"Congestion relief calculated by calculating the reduction in delay per mile in highway"
"compared to the no-Metro case, multiply by the total driving trip miles"
"Graph reports annual figures.  Annual vehicle miles adjusted following the welfare tables"
"in response to the underestimation of driving VMT in our model.") 
legend(order(1 "Pollution reduction" 2 "Congestion relief" 3 "Travel time saving"));
graph export CF-Set-Welfarechange_adjusted.png, replace;


x
twoway (line bCongest speed), ///
ylabel(, labsize(vsmall) format(%16.0gc) angle(forty_five))
