clear all

use "C:/Users/Dennis/Desktop/Results/1028/CF-fastall-set.dta", clear
cd "D:\Dropbox\Cornell\LA Expo Line Project\Data Files\Gravity Flow Prediction\Output"
drop in 1/1

ren *max *

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



