* Script generating elasticity_data_V2 is in Results/1028/DO_FILES
* Script generates numbers for Table 4 and Table 5

use "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta", clear

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
label var dflowpost "Driving flow Shutdown"
label var tflowpre "Transit flow pre expo"
label var tflowpost "Transit flow Shutdown"

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
*gen tfmetroonlypost = tflowpost * metroonlypost // no metro
gen tfwalkonlypost = tflowpost * walkonlypost
gen tfwalkpost = tflowpost * walkpost
*gen tfmetropost = tflowmetropost // no metro

*Gen vmt by mode
gen tvbuspre = tvmtpre * buspre
gen tvbusonlypre = tvmtpre * busonlypre
gen tvmetroonlypre = tvmtpre * metroonlypre
gen tvwalkonlypre = tvmtpre * walkonlypre
gen tvwalkpre = tvmtpre * walkpre
gen tvmetropre = tvmtpre * metropre

gen tvbuspost = tvmtpost * buspost
gen tvbusonlypost = tvmtpost * busonlypost
*gen tvmetroonlypost = tvmtpost * metroonlypost // no metro
gen tvwalkonlypost = tvmtpost * walkonlypost
gen tvwalkpost = tvmtpost * walkpost
*gen tvmetropost = tvmtpost * metropost // no metro

gen busmiles0 = prebusl*tflowpre
gen metromiles0 = premetrol*tflowpre
gen busmiles1 = postbusl*tflowpost
*gen metromiles1 = postmetrol*tflowpost // no metro

}
drop if oID == dID

cls

* Table 4 (Hidden in  column K,L)
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
di "**Hetero delay(shutdown) =" `delay1'-`delay0'

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

qui {
	n: di "Panel A: Per added driving mile"
	n: di "**Hetero delay(shutdown) =" `delay1'-`delay0'
	n: di "**baseline number of veh mile per day am peak = " `dvmtpre'
	n: di "**Change in driving trips per day am peak = " `ddflow'
	n: di "**Change in driving miles per day am peak = " `diff_vmt_drv'
	n: di "Panel B: Per changed transit mile"
	n: di "**Hetero delay(shutdown) =" `delay1'-`delay0'
	n: di "**baseline number of veh mile per day am peak = " `dvmtpre'
	n: di "**Change in transit trips per day am peak = " `dtflow'
	n: di "**Change in transit miles per day am peak = " `diff_vmt_transit'
}

* Generate numbers for table 5
qui {
n: di "Table 5 panel A"
n: tabstat tflowpre dflowpre, stat(sum) col(stat) format(%14.2f)
n: tabstat tfwalkonlypre tfbusonlypre tfmetropre, stat(sum) col(stat) format(%14.2f)

n: di "Table 5 panel C"
n: tabstat tflowpost dflowpost, stat(sum) col(stat) format(%14.2f)
n: tabstat tfwalkonlypost tfbusonlypost, stat(sum) col(stat) format(%14.2f)

n: di "Table 5 panel A - VMT"
n: tabstat tvmtpre dvmtpre, stat(sum) col(stat) format(%14.2f)
n: tabstat tvwalkonlypre tvbusonlypre tvmetropre, stat(sum) col(stat) format(%14.2f)
n: tabstat *miles0 if walkonlypre == 1, stat(sum)
n: tabstat *miles0 if busonlypre == 1, stat(sum)
n: tabstat *miles0 if metropre == 1, stat(sum)
n: tabstat *miles0, stat(sum) col(stat)

n: di "Table 5 panel C - VMT"
n: tabstat tvmtpost dvmtpost, stat(sum) col(stat) format(%14.2f)
n: tabstat tvwalkonlypost tvbusonlypost, stat(sum) col(stat) format(%14.2f)
n: tabstat *miles1 if walkonlypost == 1, stat(sum)
n: tabstat *miles1 if busonlypost == 1, stat(sum)
*n: tabstat *miles1 if metropost == 1, stat(sum) // no metro
n: tabstat *miles1, stat(sum) col(stat)

sum dvmtpre, meanonly
local vmtpre = `r(sum)'
sum dvmtpost, meanonly
local vmtpost = `r(sum)'
n: di "Change in VMT: " (`vmtpost'/`vmtpre'-1)

}

x
gen ddelay = delay1-delay0
keep ddflow ddelay dflowpre dflowpost dps spd1



x


* At Means level table

qui {
tabstat dflowpre, stat(sum) format (%12.2f) save
matrix tab = r(StatTotal)
local dflowpre = tab[1,1]
n: di "**baseline number of car trips per day am peak = " `dflowpre'

sum predrvlen [iw=dflowpre], meanonly
local avgpredrvlen = `r(mean)'
n: di "**Average baseline driving length = " `avgpredrvlen'

tabstat ddflow, stat(sum) save
matrix tab = r(StatTotal)
local ddflow = tab[1,1]
n: di "**number trips added to driving or removed from transit = " `ddflow'

sum predrvlen [iw=ddflow], meanonly
local avgtranlength = `r(mean)'
n: di "**Average added driving length = " `avgtranlength'

sum prelength [iw=ddflow], meanonly
local avgtranlength = `r(mean)'
n: di "**Average added transit length = " `avgtranlength'
}


gen id_taz12a = dID
merge m:1 id_ using ../Setup/TAZpark
drop _m
replace park = park*10

* merge with distance to feature data
gen id_taz12a = oID
merge m:1 id_taz12a using TAZdisttofeatures
drop _m
ren near* o_near*

replace id_taz12a = dID
merge m:1 id_taz12a using TAZdisttofeatures
drop _m
ren near* d_near*

drop id_taz12a

* Table 4b: # of vmt in annual calculation
tabstat dvmtpre, stat(sum) format(%9.2f)

* Table 4a (overall)
tabstat tflowpre tflowpost dflowpre dflowpost, stat(n sum) col(stat)

* Table 4a (all trips equal or less than 7 mile)
tabstat tflowpre tflowpost dflowpre dflowpost ///
if prelength <= 7, stat(n sum) col(stat)
sum prelength if prelength <= 7

tabstat tflowpre tflowpost dflowpre dflowpost ///
if prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if prelength > 6.5 & prelength < 7.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 0.5 & d_nearmetro < 0.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 0.5 & d_nearmetro < 0.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 0.5 & d_nearmetro < 0.5 & prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 0.5 & d_nearmetro < 0.5 & prelength > 6.5 & prelength < 7.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5

tabstat tvmtpre tvmtpost dvmtpre dvmtpost ///
if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5


x //>> Copy these to new file so can swap vmt and flow w/ replace
tabstat tflowpre tflowpost dflowpre dflowpost ///
if prelength <= 7, stat(n sum) col(stat) format(%9.2f)
sum prelength if prelength <= 7


tabstat tflowpre tflowpost dflowpre dflowpost ///
if prelength > 7, stat(n sum) col(stat) format(%9.2f)
sum prelength if prelength <= 7


* Table 4a (overall)
tabstat tflowpre tflowpost dflowpre dflowpost, stat(n sum) col(stat)

* Table 4a (all trips equal or less than 7 mile)
tabstat tflowpre tflowpost dflowpre dflowpost ///
if prelength <= 7, stat(n sum) col(stat)
sum prelength if prelength <= 7

tabstat tflowpre tflowpost dflowpre dflowpost ///
if prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if prelength > 6.5 & prelength < 7.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 0.5 & d_nearmetro < 0.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 0.5 & d_nearmetro < 0.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 0.5 & d_nearmetro < 0.5 & prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 0.5 & d_nearmetro < 0.5 & prelength > 6.5 & prelength < 7.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5

tabstat tflowpre tflowpost dflowpre dflowpost ///
if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5, stat(n sum) col(stat)
sum prelength if o_nearmetro < 5 & d_nearmetro < 5 & prelength > 6.5 & prelength < 7.5


* Generate passenger mile breakdown
gen vbuspre = tflowpre * prebusl
gen vmetropre = tflowpre * premetrol

gen vbuspost = tflowpost * postbusl
gen vmetropost = tflowpost * postmetrol

tabstat vbuspre vmetropre if walkonlypre == 1, stat(sum) col(stat) format(%10.2f)
tabstat vbuspre vmetropre if busonlypre == 1, stat(sum) col(stat) format(%10.2f)
tabstat vbuspre vmetropre if metroonlypre == 1, stat(sum) col(stat) format(%10.2f)
tabstat vbuspre vmetropre if metropre == 1, stat(sum) col(stat) format(%10.2f)

tabstat vbuspost vmetropost if walkonlypost == 1, stat(sum) col(stat) format(%10.2f)
tabstat vbuspost vmetropost if busonlypost == 1, stat(sum) col(stat) format(%10.2f)
tabstat vbuspost vmetropost if metroonlypost == 1, stat(sum) col(stat) format(%10.2f)
tabstat vbuspost vmetropost if metropost == 1, stat(sum) col(stat) format(%10.2f)
