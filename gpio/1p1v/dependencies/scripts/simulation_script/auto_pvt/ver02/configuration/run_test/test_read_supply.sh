cfg_file=$1


# path & source:
current_path=`pwd`
script_path="/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver02"

source /$script_path/tb_gen/pvt_loop.sh
source /$script_path/configuration/read_cfg.sh
source /$script_path/configuration/read_supply.sh
source /$script_path/configuration/read_corner.sh

read_cfg
read_supply
read_corner 

echo "vccmin_tt_c=$vccmin_tt_c"
echo "vccnom_tt_c=$vccnom_tt_c"
echo "vccmax_tt_c=$vccmax_tt_c"
echo "vccmin_ff_c=$vccmin_ff_c"
echo "vccnom_ff_c=$vccnom_ff_c"
echo "vccmax_ff_c=$vccmax_ff_c"
echo "vccmin_tt_h=$vccmin_tt_h"
echo "vccnom_tt_h=$vccnom_tt_h"
echo "vccmax_tt_h=$vccmax_tt_h"
echo "vccmin_ff_h=$vccmin_ff_h"
echo "vccnom_ff_h=$vccnom_ff_h"
echo "vccmax_ff_h=$vccmax_ff_h"
echo "vccmin_ss_c=$vccmin_ss_c"
echo "vccnom_ss_c=$vccnom_ss_c"
echo "vccmax_ss_c=$vccmax_ss_c"
echo "vccmin_ss_h=$vccmin_ss_h"
echo "vccnom_ss_h=$vccnom_ss_h"
echo "vccmax_ss_h=$vccmax_ss_h"
echo "vcnmin=$vcnmin"
echo "vcnnom=$vcnnom"
echo "vcnmax=$vcnmax"
echo "vctxmin=$vctxmin"
echo "vctxnom=$vctxnom"
echo "vctxmax=$vctxmax"
