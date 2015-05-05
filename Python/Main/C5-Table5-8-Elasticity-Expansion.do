* Run A3.1-GenData-Pre-vs-Post before this script
* Script generates numbers for Table 4, 5, and 6

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

qui {
gen metropre = premetrol>0
gen metropost= postmetrol>0
gen buspre = prebusl>0
gen buspost= postbusl>0
gen walkpre = prewalkl>0
gen walkpost= postwalkl>0
gen busonlypre = prebusl>0  & premetrol==0
gen busonlypost= postbusl>0 & postmetrol==0
gen metroonlypre = prebusl==0  & premetrol>0
gen metroonlypost= postbusl==0 & postmetrol>0
gen walkonlypre = prebusl==0  & premetrol==0
gen walkonlypost= postbusl==0 & postmetrol==0

gen dvmtpre = predrvlen*dflowpre
gen dvmtpost = predrvlen*dflowpost
gen tvmtpre = prelength*tflowpre
gen tvmtpost = prelength*tflowpost
gen tflowmetropre = tflowpre * metropre
gen tflowmetropost = tflowpost * metropost
gen dtflowpct = tflowpost/tflowpre -1
gen dtflowmetro = tflowmetropost/tflowmetropre -1
sum dtflowpct dtflowmetro

*Gen flow by mode
gen tfbuspre = tflowpre * buspre
gen tfbusonlypre = tflowpre * busonlypre
gen tfmetroonlypre = tflowpre * metroonlypre
gen tfwalkonlypre = tflowpre * walkonlypre
gen tfwalkpre = tflowpre * walkpre
gen tfmetropre = tflowpre * metropre

gen tfbuspost = tflowpost * buspost
gen tfbusonlypost = tflowpost * busonlypost
gen tfmetroonlypost = tflowpost * metroonlypost
gen tfwalkonlypost = tflowpost * walkonlypost
gen tfwalkpost = tflowpost * walkpost
gen tfmetropost = tflowmetropost

*Gen vmt by mode
gen tvbuspre = tvmtpre * buspre
gen tvbusonlypre = tvmtpre * busonlypre
gen tvmetroonlypre = tvmtpre * metroonlypre
gen tvwalkonlypre = tvmtpre * walkonlypre
gen tvwalkpre = tvmtpre * walkpre
gen tvmetropre = tvmtpre * metropre

gen tvbuspost = tvmtpost * buspost
gen tvbusonlypost = tvmtpost * busonlypost
gen tvmetroonlypost = tvmtpost * metroonlypost
gen tvwalkonlypost = tvmtpost * walkonlypost
gen tvwalkpost = tvmtpost * walkpost
gen tvmetropost = tvmtpost * metropost

gen busmiles0 = prebusl*tflowpre
gen metromiles0 = premetrol*tflowpre
gen busmiles1 = postbusl*tflowpost
gen metromiles1 = postmetrol*tflowpost

}
drop if oID == dID

cls

* Table 4 (Hidden in  column K,L), for table 8
qui {
gen dpsspd = predrvlen / predrvdps
drop if dps > 65

gen delay0 = 65/dps-1
gen flow0 = 500+log(dpsspd/65)/(-.000191)
gen pctddflow = dflowpost/dflowpre
gen flow1 = flow0*pctdd
gen spd1 = 65*exp(-.000191*(flow1-500))
gen delay1 = 65/spd1 -1
sum delay0 [iw=dflowpre], meanonly
local delay0 = `r(mean)'
sum delay1 [iw=dflowpre], meanonly
local delay1 = `r(mean)'
di "**Hetero delay(expand) =" `delay1'-`delay0'

}

* OD Level Table
qui{
gen ddflow = dflowpost-dflowpre
gen dtflow = tflowpost-tflowpre
gen diff_vmt_drv = ddflow * predrvlen
gen diff_vmt_transit = dtflow * prelength
}

qui {
tabstat dflowpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dflowpre = tab[1,1]
di "**baseline number of car trips per day am peak = " `dflowpre'

tabstat dvmtpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dvmtpre = tab[1,1]
di "**baseline number of veh mile per day am peak = " `dvmtpre'
di "**baseline annual vehicle mile annual = " %14.2f 2*260*`dvmtpre'

tabstat ddflow, stat(sum) save
matrix tab = r(StatTotal)
local ddflow = tab[1,1]
tabstat dtflow, stat(sum) save
matrix tab = r(StatTotal)
local dtflow = tab[1,1]
di "**number trips change to driving = " `ddflow'
di "**number trips change to transit = " `dtflow'

tabstat diff_vmt_transit, stat(sum) save
matrix tab = r(StatTotal)
local diff_vmt_transit = tab[1,1]
di "**removed transit miles per day am peak = " `diff_vmt_transit'
di "**removed transit miles annual = " %14.2f 2*260*`diff_vmt_transit'

tabstat diff_vmt_drv, stat(sum) save
matrix tab = r(StatTotal)
local diff_vmt_drv = tab[1,1]
di "**removed driving miles per day am peak = " `diff_vmt_drv'
di "**removed driving miles annual = " %14.2f 2*260*`diff_vmt_drv'
}

* Generate numbers for table 5
qui {
n: di "Table 5 panel A"
n: tabstat tflowpre dflowpre, stat(sum) col(stat) format(%14.2f)
n: tabstat tfwalkonlypre tfbusonlypre tfmetropre, stat(sum) col(stat) format(%14.2f)

n: di "Table 5 panel B"
n: tabstat tflowpost dflowpost, stat(sum) col(stat) format(%14.2f)
n: tabstat tfwalkonlypost tfbusonlypost tfmetropost, stat(sum) col(stat) format(%14.2f)

n: di "Table 5 panel A - VMT"
n: tabstat tvmtpre dvmtpre, stat(sum) col(stat) format(%14.2f)
n: tabstat tvwalkonlypre tvbusonlypre tvmetropre, stat(sum) col(stat) format(%14.2f)
n: tabstat *miles0 if walkonlypre == 1, stat(sum)
n: tabstat *miles0 if busonlypre == 1, stat(sum)
n: tabstat *miles0 if metropre == 1, stat(sum)
n: tabstat *miles0, stat(sum) col(stat)

n: di "Table 5 panel B - VMT"
n: tabstat tvmtpost dvmtpost, stat(sum) col(stat) format(%14.2f)
n: tabstat tvwalkonlypost tvbusonlypost tvmetropost, stat(sum) col(stat) format(%14.2f)
n: tabstat *miles1 if walkonlypost == 1, stat(sum)
n: tabstat *miles1 if busonlypost == 1, stat(sum)
n: tabstat *miles1 if metropost == 1, stat(sum)
n: tabstat *miles1, stat(sum) col(stat)

sum dvmtpre, meanonly
local vmtpre = `r(sum)'
sum dvmtpost, meanonly
local vmtpost = `r(sum)'
di "Change in VMT: " (`vmtpost'/`vmtpre'-1)

}

qui{
n: di "Table 6"
n: tabstat tflowpre tfmetropre tflowpost tfmetropost, stat(sum) col(stat) format(%14.2f)
}


qui {
	n: di "Table 8"
	n: di "**Hetero delay(Expansion) =" `delay1'-`delay0'
	n: di "**baseline number of veh mile per day am peak = " `dvmtpre'
	n: di "**Change in driving trips per day am peak = " `ddflow'
	n: di "**Change in driving miles per day am peak = " `diff_vmt_drv'
	n: di "**Change in transit trips per day am peak = " `dtflow'
	n: di "**Change in driving miles per day am peak = " `diff_vmt_transit'
}

x


/*
* Table 7: # trips of transit vs cars
gen distcat=17
replace distcat=16 if prelength <40
replace distcat=15 if prelength <37
replace distcat=14 if prelength <35
replace distcat=13 if prelength <33
replace distcat=12 if prelength <30
replace distcat=11 if prelength <27
replace distcat=10 if prelength <25
replace distcat=9 if prelength <23
replace distcat=8 if prelength <20
replace distcat=7 if prelength <17
replace distcat=6 if prelength <15
replace distcat=5 if prelength <13
replace distcat=4 if prelength <10
replace distcat=3 if prelength <7
replace distcat=2 if prelength <5
replace distcat=1 if prelength <3

gen drvdistcat=17
replace drvdistcat=16 if predrvlen <40
replace drvdistcat=15 if predrvlen <37
replace drvdistcat=14 if predrvlen <35
replace drvdistcat=13 if predrvlen <33
replace drvdistcat=12 if predrvlen <30
replace drvdistcat=11 if predrvlen <27
replace drvdistcat=10 if predrvlen <25
replace drvdistcat=9 if predrvlen <23
replace drvdistcat=8 if predrvlen <20
replace drvdistcat=7 if predrvlen <17
replace drvdistcat=6 if predrvlen <15
replace drvdistcat=5 if predrvlen <13
replace drvdistcat=4 if predrvlen <10
replace drvdistcat=3 if predrvlen <7
replace drvdistcat=2 if predrvlen <5
replace drvdistcat=1 if predrvlen <3


label define DistCat ///
1 "0-3" 2 "3-5" 3 "5-7" 4 "7-10" 5 "10-13" ///
6 "13-15" 7 "15-17" 8 "17-20" 9 "20-23" ///
10 "23-25" 11 "25-27" 12 "27-30" 13 "30-33" ///
14 "33-35" 15 "35-37" 16 "37-40" 17 "40+"
label values distcat DistCat
label values drvdistcat DistCat


tabstat tflowpre dflowpre, stat(sum) by(distcat)
tabstat tflowpre dflowpre, stat(sum) by(drvdistcat)
tabstat prelength, stat(mean)  by(drvdistcat)


*/
