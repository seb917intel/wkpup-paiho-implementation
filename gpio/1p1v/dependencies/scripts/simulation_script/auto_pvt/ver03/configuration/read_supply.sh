#!/bin/bash

read_supply()
{

if [ "$sim_mode" == "ac" ]; then
{
csv_file="$script_path/configuration/table_supply_list_ac.csv"
}
elif [ "$sim_mode" == "dc" ]; then
{
csv_file="$script_path/configuration/table_supply_list_dc.csv"
}
else
{
csv_file="$script_path/configuration/table_supply_list.csv"
}
fi

vccmin_tt_c=0
vccnom_tt_c=0
vccmax_tt_c=0
vccmin_ff_c=0
vccnom_ff_c=0
vccmax_ff_c=0
vccmin_tt_h=0
vccnom_tt_h=0
vccmax_tt_h=0
vccmin_ff_h=0
vccnom_ff_h=0
vccmax_ff_h=0
vccmin_ss_c=0
vccnom_ss_c=0
vccmax_ss_c=0
vccmin_ss_h=0
vccnom_ss_h=0
vccmax_ss_h=0


while IFS=',' read -r col1 col2 col3 col4 col5 col6 col7 col8
do

if [ "$col1" == "$vcc_lvl" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin=$col2
vccnom=$col4
vccmax=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin=$col3
vccnom=$col4
vccmax=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin=$col2
vccnom=$col4
vccmax=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin=$col2
vccnom=$col4
vccmax=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "vcc_vid_tt_h" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin_tt_h=$col2
vccnom_tt_h=$col4
vccmax_tt_h=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin_tt_h=$col3
vccnom_tt_h=$col4
vccmax_tt_h=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin_tt_h=$col2
vccnom_tt_h=$col4
vccmax_tt_h=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin_tt_h=$col2
vccnom_tt_h=$col4
vccmax_tt_h=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "vcc_vid_tt_c" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin_tt_c=$col2
vccnom_tt_c=$col4
vccmax_tt_c=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin_tt_c=$col3
vccnom_tt_c=$col4
vccmax_tt_c=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin_tt_c=$col2
vccnom_tt_c=$col4
vccmax_tt_c=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin_tt_c=$col2
vccnom_tt_c=$col4
vccmax_tt_c=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "vcc_vid_ff_h" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin_ff_h=$col2
vccnom_ff_h=$col4
vccmax_ff_h=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin_ff_h=$col3
vccnom_ff_h=$col4
vccmax_ff_h=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin_ff_h=$col2
vccnom_ff_h=$col4
vccmax_ff_h=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin_ff_h=$col2
vccnom_ff_h=$col4
vccmax_ff_h=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "vcc_vid_ff_c" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin_ff_c=$col2
vccnom_ff_c=$col4
vccmax_ff_c=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin_ff_c=$col3
vccnom_ff_c=$col4
vccmax_ff_c=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin_ff_c=$col2
vccnom_ff_c=$col4
vccmax_ff_c=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin_ff_c=$col2
vccnom_ff_c=$col4
vccmax_ff_c=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "vcc_vid_ss_h" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin_ss_h=$col2
vccnom_ss_h=$col4
vccmax_ss_h=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin_ss_h=$col3
vccnom_ss_h=$col4
vccmax_ss_h=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin_ss_h=$col2
vccnom_ss_h=$col4
vccmax_ss_h=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin_ss_h=$col2
vccnom_ss_h=$col4
vccmax_ss_h=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "vcc_vid_ss_c" ]; then
{
if [ "$condition" == "func" ]; then
{
vccmin_ss_c=$col2
vccnom_ss_c=$col4
vccmax_ss_c=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccmin_ss_c=$col3
vccnom_ss_c=$col4
vccmax_ss_c=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccmin_ss_c=$col2
vccnom_ss_c=$col4
vccmax_ss_c=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccmin_ss_c=$col2
vccnom_ss_c=$col4
vccmax_ss_c=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "$vcn_lvl" ]; then
{
if [ "$condition" == "func" ]; then
{
vcnmin=$col2
vcnnom=$col4
vcnmax=$col6
}
elif [ "$condition" == "perf" ]; then
{
vcnmin=$col3
vcnnom=$col4
vcnmax=$col5
}
elif [ "$condition" == "htol" ]; then
{
vcnmin=$col2
vcnnom=$col4
vcnmax=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vcnmin=$col2
vcnnom=$col4
vcnmax=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "$vca_lvl" ]; then
{
if [ "$condition" == "func" ]; then
{
vccanamin=$col2
vccananom=$col4
vccanamax=$col6
}
elif [ "$condition" == "perf" ]; then
{
vccanamin=$col3
vccananom=$col4
vccanamax=$col5
}
elif [ "$condition" == "htol" ]; then
{
vccanamin=$col2
vccananom=$col4
vccanamax=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vccanamin=$col2
vccananom=$col4
vccanamax=$col8
}
else
echo "ERROR reading condition"
fi
}

elif [ "$col1" == "$vctx_lvl" ]; then
{
if [ "$condition" == "func" ]; then
{
vctxmin=$col2
vctxnom=$col4
vctxmax=$col6
}
elif [ "$condition" == "perf" ]; then
{
vctxmin=$col3
vctxnom=$col4
vctxmax=$col5
}
elif [ "$condition" == "htol" ]; then
{
vctxmin=$col2
vctxnom=$col4
vctxmax=$col7
}
elif [ "$condition" == "hvqk" ]; then
{
vctxmin=$col2
vctxnom=$col4
vctxmax=$col8
}
else
echo "ERROR reading condition"
fi
}

fi

done < "$csv_file"

}
