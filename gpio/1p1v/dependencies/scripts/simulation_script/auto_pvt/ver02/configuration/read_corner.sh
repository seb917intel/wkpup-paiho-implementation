#!/bin/bash

read_corner()
{
csv_file="$script_path/configuration/table_corner_list.csv"

while IFS=',' read -r col1 col2 col3
do

if [ "$col1" == "nom_tt" ]; then
{
typ_ex=$col2
typ_corner=$col3
}

elif [ "$col1" == "full_tt" ]; then
{
typ_ex_cornerlist_tt=$col3
}

elif [ "$col1" == "full_tt_gsgf" ]; then
{
typ_ex_cornerlist_tt_gsgf=$col3
}


elif [ "$col1" == "cross_default" ]; then
{
cross_ex=$col2
cross_ex_cornerlist_default_nonegsgf=$col3
}

elif [ "$col1" == "cross_default_gsgf" ]; then
{
cross_ex=$col2
cross_ex_cornerlist_default_gsgf=$col3
}

elif [ "$col1" == "cross_full" ]; then
{
cross_ex_cornerlist_full_nonegsgf=$col3
}

elif [ "$col1" == "cross_full_gsgf" ]; then
{
cross_ex_cornerlist_full_gsgf=$col3
}

fi

done < "$script_path/configuration/table_corner_list.csv"



if [ "$gsgf_corner" == "No" ]; then
{
typ_ex_cornerlist=$typ_ex_cornerlist_tt
cross_ex_cornerlist_full=$cross_ex_cornerlist_full_nonegsgf
cross_ex_cornerlist_default=$cross_ex_cornerlist_default_nonegsgf
}

else
{
typ_ex_cornerlist=$typ_ex_cornerlist_tt_gsgf
cross_ex_cornerlist_full=$cross_ex_cornerlist_full_gsgf
cross_ex_cornerlist_default=$cross_ex_cornerlist_default_gsgf
}

fi


if [ "$postlay_cross_cornerlist" == "default" ]; then

{
cross_ex_cornerlist=$cross_ex_cornerlist_default
}
elif [ "$postlay_cross_cornerlist" == "full" ]; then

{
cross_ex_cornerlist=$cross_ex_cornerlist_full
}
elif [ "$postlay_cross_cornerlist" == "custom" ]; then

{
cross_ex_cornerlist=$custom_corner
}
else
{
cross_ex_cornerlist=$cross_ex_cornerlist_default
}
fi
}
