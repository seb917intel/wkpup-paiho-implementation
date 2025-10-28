 
timestamp=$(date +"%Y%m%d%H%M")


echo "run log $timestamp" >> run_log.txt
sleep 2
timestamp=$(date +"%Y%m%d%H%M%S")
echo "testA start $timestamp" >> run_log.txt

sleep 5
timestamp=$(date +"%Y%m%d%H%M%S")
echo "testB start $timestamp" >> run_log.txt
