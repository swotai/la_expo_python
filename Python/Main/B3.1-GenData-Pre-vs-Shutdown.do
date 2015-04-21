clear all
tempfile temp

* Load pre driving TT and total flow matrices
local DrivingPrePath = "C:/Users/Dennis/Desktop/Pre"
local TransitPrePath = "C:/Users/Dennis/Desktop/CalcTransit/Pre"
local TransitPostPath = "C:/Users/Dennis/Desktop/CalcTransit/CF-nometro"
local outDataset = "C:/Users/Dennis/Desktop/Results/1028/Transit-pre-shutdown.dta"
local vmtData = "C:/Users/Dennis/Desktop/Results/1028/TT_vmt"

insheet using `DrivingPrePath'/CSV/TT.csv, clear
gen oID = substr(v3, 1, 8)
gen dID = substr(v3, 12,20)
destring *ID, replace
drop v1-v3
ren v4 predrvcost
ren v5 predrvlen
ren v6 predrvdps
save `temp', replace

insheet using `DrivingPrePath'/CSV/TotalTTflow1.csv, clear
ren v1 oID
ren v2 dID
ren v3 totalflow
merge 1:1 oID dID using `temp'
drop _m
save `temp', replace


* Import transit pre, calculate precost using $15 VOT
use `TransitPrePath'/TransitMatrix.dta, clear
ren oid oID
ren did dID

gen fare = prebusl > 0 | premetrol > 0
replace fare = fare * 1.25
replace precost = predps * 15 + fare
ren fare farepre
keep oID dID predps fare precost prebusl premetrol prewalkl prelength

merge 1:1 oID dID using `temp'
drop _m
save `temp', replace


* Import transit pre with metro shutdown, calculate precost using $15 VOT
use `TransitPostPath'/TransitMatrix.dta, clear
ren oid oID
ren did dID

gen fare_norail = postbusl > 0
replace fare_norail = fare_norail * 1.25
replace postcost = postdps * 15 + fare_norail
ren fare_norail farepost

keep oID dID postdps fare postcost postbusl postmetrol postwalkl postlength
compress
merge 1:1 oID dID using `temp'
drop _m
save `temp', replace



save `outDataset', replace

beep
