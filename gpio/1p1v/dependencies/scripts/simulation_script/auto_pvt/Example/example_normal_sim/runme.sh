#!/bin/bash
polo_sim=0
testname="sim hvls hs vcn"

source /nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/alias_param_source/script_param


timestamp=$(date +"%Y%m%d%H%M")
start_time=$(date +%s)

echo "sim regress for : $testname start at $timestamp"

sh $sim_pvt config.cfg gen
sleep 10

echo "submit job & running"



if [ "$polo_sim" -eq 1 ]; then
{
## polo tttt extration run

sh $sim_pvt config.cfg run tttt

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done

echo ""
echo "check un-complete job & rerun"
sh $sim_pvt config.cfg chk tttt
sleep 10
if [ -f rerun.sh ]; then
{
echo "re-run un-complete job"
sh rerun.sh > job_log.txt

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done
echo "re-run done"
rm rerun.sh
}
else
echo "No -un-complete job"
fi

rm *.txt
rm job_stat.log 


## polo prcs3 extration run

sh $sim_pvt config.cfg run prcs3

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done

echo ""
echo "check un-complete job & rerun"
sh $sim_pvt config.cfg chk prcs3
sleep 10
if [ -f rerun.sh ]; then
{
echo "re-run un-complete job"
sh rerun.sh > job_log.txt

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt


qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done
echo "re-run done"
rm rerun.sh
}
else
echo "No -un-complete job"
fi

rm *.txt
rm job_stat.log 


## polo prcf3 extration run

sh $sim_pvt config.cfg run prcf3

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done

echo ""
echo "check un-complete job & rerun"
sh $sim_pvt config.cfg chk prcf3
sleep 10
if [ -f rerun.sh ]; then
{
echo "re-run un-complete job"
sh rerun.sh > job_log.txt

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done
echo "re-run done"
rm rerun.sh
}
else
echo "No -un-complete job"
fi

}

else
{
#prelay sim
sh $sim_pvt config.cfg run

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done

echo ""
echo "check un-complete job & rerun"
sh $sim_pvt config.cfg chk
sleep 10
if [ -f rerun.sh ]; then
{
echo "re-run un-complete job"
sh rerun.sh > job_log.txt

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target altera_png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 30
done
echo "re-run done"
rm rerun.sh
}
else
echo "No -un-complete job"
fi

}
fi

echo "all job completed & data compilation start"

sh $sim_pvt config.cfg ext
sleep 20

sh $sim_pvt config.cfg srt
sleep 20

sh $sim_pvt config.cfg bkp

rm *.txt
rm job_stat.log 


end_time=$(date +%s) 
delta=$((end_time - start_time)) 
hours=$(echo "scale=2; $delta / 3600" | bc)

echo "Regression done, time: $hours HRs"
echo "Regression done, time: $hours HRs" > run_$timestamp.log
