#!/bin/bash



logging ()
{
timestamp=$(date +"%Y%m%d%H%M%S")
echo "$timestamp :: $1" >> script_logging.log
}

run_sim ()
{
sh $sim_pvt config.cfg run $1

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
echo "check un-complete job"
sh $sim_pvt config.cfg chk $1
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
echo "No un-complete job"
fi

rm *.txt
rm job_stat.log 
}
