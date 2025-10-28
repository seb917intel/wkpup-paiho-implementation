#!/bin/bash

testname="sim vssh leak comp"

source /nfs/png/disks/km6_io_7/users/paihobon/simulation/simulation_script/alias_param_source/script_param

timestamp=$(date +"%Y%m%d%H%M")
start_time=$(date +%s)

echo "sim regress for : $testname start at $timestamp"

sh $sim_pvt config.cfg gen
sleep 10

echo "submit job & running"

sh $sim_pvt config.cfg run > job_log.txt
sleep 60

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt
sleep 60

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 60
done


echo "check un-complete job & rerun"
sh $sim_pvt config.cfg chk 
sleep 10
if [ -s rerun.sh ]; then
{
echo "re-run un-complete job"
sh rerun.sh > job_log.txt
sleep 60

grep -o 'JobID [0-9]*' job_log.txt | cut -d ' ' -f2 > job_id.txt
sleep 60

qjob=10
while [[ $qjob -gt 0 ]]
do
nbstatus jobs --target png_normal > job_chk.txt
tail -n +7 job_chk.txt | awk '{print $2}' | grep -o '[0-9]*' > job_q_id.txt
qjob=`grep -Fwf job_q_id.txt job_id.txt | wc -l`
printf "\r%s" "running Jobs: $qjob   "
sleep 60
done
echo "re-run done"
}
else
echo "No -un-complete job"
fi

echo "all job completed & data compilation start"

sh $sim_pvt config.cfg ext
sleep 240

sh $sim_pvt config.cfg srt
sleep 20

sh $sim_pvt config.cfg bkp
sleep 60

sh $sim_pvt config.cfg usr_script

rm *.txt
rm job_stat.log 
rm rerun.sh

end_time=$(date +%s) 
delta=$((end_time - start_time)) 
hours=$(echo "scale=2; $delta / 3600" | bc)

echo "Regression done, time: $hours HRs"
echo "Regression done, time: $hours HRs" > run_$timestamp.log
