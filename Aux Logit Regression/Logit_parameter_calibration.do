/* 
Sij: 
i = peak/off peak, peak = 0, op = 1
j = transit/drive, drive = 0, transit = 1
*/

cd 

* Import census CTPP data, calculate transit share

* Import cost data (driving)

* Import transit data (Pre expo)

* Generate target share for regression for four periods


* Multinomial logits

program define mylogit
    args lnf Xb
    replace `lnf' = -ln(1+exp(-`Xb')) if $ML_y1==1
    replace `lnf' = -`Xb' - ln(1+exp(-`Xb')) if $ML_y1==0
end

ml model lf mylogit (foreign = mp weight)
ml maximize
