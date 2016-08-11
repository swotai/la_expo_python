/*
Updated 1/26 to use new VOT value of $15 to generate 
new TTpubcost for pre and post
*/
clear all

cd C:/Users/Dennis/Desktop/

insheet using TransitPre/TransitPre_Accu2.csv, clear

gen oID_TAZ12A = substr(name, 1, 8)
gen dID_TAZ12A = substr(name, 12,8)
destring *ID_*, replace

gen fare = total_lenbus > 0 | total_lenmetro > 0
replace fare = fare * 1.25

gen precost = total_dps * 15 + fare
ren total_dps pre_triptime

keep oID dID pre_triptime precost
order oID dID pre_triptime precost

export delimited using TTpubPre.csv, delimiter(",") replace

insheet using TransitPost/TransitPost_Accu2.csv, clear

gen oID_TAZ12A = substr(name, 1, 8)
gen dID_TAZ12A = substr(name, 12,8)
destring *ID_*, replace

gen fare = total_lenbus > 0 | total_lenmetro > 0
replace fare = fare * 1.25

gen postcost = total_dps * 15 + fare
ren total_dps post_triptime

keep oID dID post_triptime postcost
order oID dID post_triptime postcost

export delimited using TTpubPost.csv, delimiter(",") replace

