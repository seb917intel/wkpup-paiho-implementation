## General runme template ##

############################
## setup sript parameters ##
############################
################################################################################################################################################
source /nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/alias_param_source/script_param

#Edit for manual pointer
#script_path="/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver02"
#sim_pvt="$script_path/sim_pvt.sh"
current_path=`pwd`
cfg_file="config.cfg"
source /$script_path/configuration/read_cfg.sh
source /$script_path/runme_script/runme_func.sh
read_cfg

################################################################################################################################################


########################
## User customization ##
########################
################################################################################################################################################
#Please edit accorgingly to your needs
# script_opt: Gen_run_compile_all, Gen_only, run_only_all, run_only_typical, run_only_cworst_CCworst_T, run_only_cbest_CCbest_T, compile_only
script_opt="Gen_run_compile_all"
#usr_script: Yes, No
usr_script="No"

################################################################################################################################################


########################
## Main run script    ##
########################
################################################################################################################################################

timestamp=$(date +"%Y%m%d%H%M")
start_time=$(date +%s)

echo "Auto_pvt script start at : $timestamp"
echo "Auto_pvt script start at : $timestamp" >> script_logging.log
echo "Sim dir : $current_path"
echo ""

###########################################################################
if [ "$script_opt" = "Gen_run_compile_all" ] || [ "$script_opt" = "Gen_only" ] ; then
{
logging "Gen PVT testbench & directory"
sh $sim_pvt config.cfg gen
sleep 10
}
fi
###########################################################################
if [ "$script_opt" = "Gen_run_compile_all" ] || [ "$script_opt" = "run_only_all" ] ; then
{
if [  "$mode" = "prelay" ] ; then
{
logging "Submit simulation job & running prelay"
run_sim
}
else
{
logging "Submit simulation job & running for polo extraction: typical"
run_sim "typical"

logging "Submit simulation job & running for polo extraction: cworst_CCworst_T"
run_sim "cworst_CCworst_T"

logging "Submit simulation job & running for polo extraction: cbest_CCbest_T"
run_sim "cbest_CCbest_T"
}
fi
}
fi
###########################################################################
if [ "$script_opt" = "run_only_cworst_CCworst_T" ] ; then
{
logging "Submit simulation job & running for polo extraction: cworst_CCworst_T"
run_sim "cworst_CCworst_T"
}
fi
###########################################################################
if [ "$script_opt" = "run_only_cbest_CCbest_T" ] ; then
{
logging "Submit simulation job & running for polo extraction: cbest_CCbest_T"
run_sim "cbest_CCbest_T"
}
fi
###########################################################################
if [ "$script_opt" = "Gen_run_compile_all" ] || [ "$script_opt" = "compile_only" ] ; then
{

logging "Data extraction"
sh $sim_pvt config.cfg ext
sleep 10

logging "Data sorting"
sh $sim_pvt config.cfg srt
sleep 10

logging "Data backup"
sh $sim_pvt config.cfg bkp
sleep 10

if [ "$usr_script" = "Yes" ] ; then
{
sh $sim_pvt config.cfg usr_script
}
fi
}
fi

###########################################################################
end_time=$(date +%s) 
delta=$((end_time - start_time)) 
hours=$(echo "scale=2; $delta / 3600" | bc)

echo "Auto_pvt script completed, time: $hours HRs"
echo "Auto_pvt script completed, time: $hours HRs" >> script_logging.log
################################################################################################################################################
