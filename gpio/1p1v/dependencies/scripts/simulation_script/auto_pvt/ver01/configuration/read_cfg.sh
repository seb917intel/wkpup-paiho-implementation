#!/bin/bash

read_cfg()
{
csv_file="$current_path/$cfg_file"

#default
mode="prelay"
vcn_lvl="1p1v"
vctx_lvl="vcctx_600"
vca_lvl="vccana"
supply1="vcc"
supply2="NA"
supply3="NA"
condition="perf"
ncpu="4"
nmem="4"
alt_ext_mode="No"
alt_ext_n="0"
sim_mode="ac"
gsgf_corner="No"
vcc_vid="No"
simulator="finesim"
postlay_cross_cornerlist="default"

while IFS=':' read -r col1 col2 col3
do

if [ "$col1" == "mode" ]; then
{
mode=$col2
}

elif [ "$col1" == "vccn" ]; then
{
vcn_lvl=$col2
}

elif [ "$col1" == "vcctx" ]; then
{
vctx_lvl=$col2
}

elif [ "$col1" == "vccana" ]; then
{
vca_lvl=$col2
}


elif [ "$col1" == "1st_supply_swp" ]; then
{
supply1=$col2
}

elif [ "$col1" == "2nd_supply_swp" ]; then
{
supply2=$col2
}

elif [ "$col1" == "3rd_supply_swp" ]; then
{
supply3=$col2
}

elif [ "$col1" == "condition" ]; then
{
condition=$col2
}

elif [ "$col1" == "CPU #" ]; then
{
ncpu=$col2
}

elif [ "$col1" == "MEM [G]" ]; then
{
nmem=$col2
}

elif [ "$col1" == "alter_extraction" ]; then
{
alt_ext_mode=$col2
}

elif [ "$col1" == "alter_string#" ]; then
{
alt_ext_n=$col2
}

elif [ "$col1" == "sim_mode" ]; then
{
sim_mode=$col2
}

elif [ "$col1" == "gs/gf_corner" ]; then
{
gsgf_corner=$col2
}

elif [ "$col1" == "vcc_vid" ]; then
{
vcc_vid=$col2
}

elif [ "$col1" == "simulator" ]; then
{
simulator=$col2
}


elif [ "$col1" == "postlay_cross_cornerlist" ]; then
{
postlay_cross_cornerlist=$col2
custom_corner=$col3
}

else

echo "ERROR reading config file"

fi

done < "$current_path/$cfg_file"
 
}
