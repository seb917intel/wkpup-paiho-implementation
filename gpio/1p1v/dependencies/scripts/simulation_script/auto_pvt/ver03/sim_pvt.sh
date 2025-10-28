# sh sim_pvt config_file {stage}
# stage = gen; run; ext; srt; bkp
# stage need to execute in sequence

# read variable
cfg_file=$1
stage=$2
run_ex_corner=$3

# path & source:
current_path=`pwd`
script_path="/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03"

source /$script_path/tb_gen/pvt_loop.sh
source /$script_path/configuration/read_cfg.sh
source /$script_path/configuration/read_supply.sh
source /$script_path/configuration/read_corner.sh

read_cfg
read_supply
read_corner

#set variable
swpl=$alt_ext_n
mem=$nmem
cpu=$ncpu

#check integer
val=$cpu
val=`echo "$cpu"|grep "^[0-9]*$"`
val="$?"

mval=$mem
mval=`echo "$mem"|grep "^[0-9]*$"`
mval="$?"


#search template sp file
tb_file=`ls  $current_path/template | grep -e '.sp'| grep -v '~'`
testbench=`echo ${tb_file[0]} | sed 's/.sp//g'`

if [ -z "$stage" ]; then
{
echo "sim_pvt cofig_file {stage}"
echo "stage = gen  --> generate testbench & directory"
echo "stage = run  --> submit sim to farm, please specified #cpu according to your simulation size"
echo "stage = ext  --> to extract data after sim completed, alter data, swpl = alter title length"
echo "stage = srt  --> to sort data after extraction completed"
echo "stage = bkp  --> backup data to 00bkp_{time} folder"
echo "stage execution by stages: gen -> run -> ext* -> srt*"
}

elif [ $( echo $stage | grep -w gen ) ]; then
{

echo "gen testbench & directory"
echo "vccn $vcn_lvl"
echo "vcctx $vctx_lvl"
echo "sweep supply: $supply1, $supply2, $supply3"
echo "$mode $condition"

echo "vcc_vid: $vcc_vid"
if [ "$vcc_vid" == "Yes" ]; then
{
echo "vcc_ff_hot_temp : $vccmin_ff_h $vccnom_ff_h $vccmax_ff_h"
echo "vcc_ff_cold_temp: $vccmin_ff_c $vccnom_ff_c $vccmax_ff_c"
echo "vcc_tt_hot_temp : $vccmin_tt_h $vccnom_tt_h $vccmax_tt_h"
echo "vcc_tt_cold_temp: $vccmin_tt_c $vccnom_tt_c $vccmax_tt_c"
echo "vcc_ss_hot_temp : $vccmin_ss_h $vccnom_ss_h $vccmax_ss_h"
echo "vcc_ss_cold_temp : $vccmin_ss_c $vccnom_ss_c $vccmax_ss_c"
}
else
{
echo "vcc none VID : $vccmin $vccnom $vccmax"
}
fi

if [ "$mode" == "prelay" ]; then
{
echo "prelay simulation"
}
else
{
echo "polo simulation"
echo "corners run with typical extraction: $typ_ex_cornerlist"
echo "corners run with cworst_CCworst_T, cbest_CCbest_T extraction: $cross_ex_cornerlist"
}
fi


core_func ()
{
mkdir -p $i/$j/$j\_$k/$l
perl /$script_path/tb_gen/gen_tb.pl template/$testbench.sp $i $j $k $lv1 $lv2 $lv3 $supply1 $supply2 $supply3 $vccmin $vccnom $vccmax $vcnmin $vcnnom $vcnmax $vccanamin $vccananom $vccanamax $vctxmin $vctxnom $vctxmax $vcc_vid $vccmin_tt_h $vccnom_tt_h $vccmax_tt_h $vccmin_tt_c $vccnom_tt_c $vccmax_tt_c $vccmin_ff_h $vccnom_ff_h $vccmax_ff_h $vccmin_ff_c $vccnom_ff_c $vccmax_ff_c $vccmin_ss_h $vccnom_ss_h $vccmax_ss_h $vccmin_ss_c $vccnom_ss_c $vccmax_ss_c > $i/$j/$j\_$k/$l/$testbench.sp
}
# execute pvt loop
gen_pvt_loop_par
}

elif [ $( echo $stage | grep -w run ) ]; then
{
if [ -z $cpu ]; then
echo "#cpu not specifid, please specified #cpu 2,4,6,8,10,12,14,16"
elif [ $val != 0 ]; then
echo "#cpu not a number, please specified #cpu 2,4,6,8,10,12,14,16"
elif [ -z $mem ]; then
echo "#Mem not specified"
elif [ $mval != 0 ]; then
echo "#Mem not a number"
else

core_func ()
{
cd $i/$j/$j\_$k/$l

if [ "$simulator" == "finesim" ]; then 
{
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' finesim -np $cpu $testbench.sp -o $testbench >> $current_path/job_log.txt
}
elif [ "$simulator" == "primesim" ]; then 
{
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' primesim -np $cpu -spice $testbench.sp -o $testbench >> $current_path/job_log.txt
}
#to add spectre
else
{
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' finesim -np $cpu $testbench.sp -o $testbench >> $current_path/job_log.txt
}
fi
}

if [ "$mode" == "prelay" ]; then
{
echo "Submit simulation job & running prelay"
echo "NB job submit log" > $current_path/job_log.txt
# execute pvt loop
gen_pvt_loop_seq
}
else
{

if [ -z $run_ex_corner ]; then
echo "#run_ex_corner not specifid, please specified: typical/cworst_CCworst_T/cbest_CCbest_T"
else
# execute pvt loop for polo
echo "Submit simulation job & running for polo extraction: $run_ex_corner"
echo "NB job submit log" > $current_path/job_log.txt
run_pvt_loop_polo
fi
}
fi

fi
}

elif [ $( echo $stage | grep -w ext ) ]; then
{
mkdir -p report
mkdir -p compiled_waveform

echo "start data extraction"

if [ "$alt_ext_mode" == "No" ]; then

core_func ()
{
cp /$script_path/data_extraction/extract.sh $i/$j/$j\_$k/$l
cp /$script_path/data_extraction/move.sh $i/$j/$j\_$k/$l
	
cd $i/$j/$j\_$k/$l

mkdir -p result

sh move.sh $testbench
sh extract.sh $testbench

mv report.txt $current_path/report/report_$i\_$j\_$k\_$l.txt

rm extract.sh
rm move.sh

cd result


if [ -f "$testbench.tr0" ]; then
	mv $testbench.tr0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.tr0
fi

if [ -f "$testbench.fsdb" ]; then
	mv $testbench.fsdb $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.fsdb
fi

if [ -f "$testbench.ac0" ]; then
	mv $testbench.ac0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.ac0
fi

if [ -f "$testbench.sw0" ]; then
	mv $testbench.sw0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.sw0
fi

cd ..
rm -r result

cd $current_path
}

else

core_func ()
{

cp $script_path/data_extraction/extract_alt.sh $i/$j/$j\_$k/$l
cp $script_path/data_extraction/move.sh $i/$j/$j\_$k/$l
	
cd $i/$j/$j\_$k/$l

mkdir -p result

sh move.sh $testbench
sh extract_alt.sh $testbench $swpl $simulator

rm extract_alt.sh
rm move.sh

mv report.txt $current_path/report/report_$i\_$j\_$k\_$l.txt



cd result
result_path=`pwd`
rm *.grp

if [ "$simulator" == "finesim" ]; then
{
if [ -f "$testbench.fsdb" ]; then

wave_file=`ls $result_path | grep -e "fsdb"`
count=0
for m in $wave_file
do 
if [ $count -gt 0 ]; then
	mv $testbench#$count.fsdb $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l#$count.fsdb
else
	mv $testbench.fsdb $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.fsdb
fi
count=`expr $count + 1`
done

elif [ -f "$testbench.ac0" ]; then
wave_file=`ls $result_path | grep -e "ac0"`
count=0
for m in $wave_file
do 
if [ $count -gt 0 ]; then
	mv $testbench#$count.ac0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l#$count.ac0
else
	mv $testbench.ac0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.ac0
fi
count=`expr $count + 1`
done

elif [ -f "$testbench.sw0" ]; then
wave_file=`ls $result_path | grep -e "sw0"`
count=0
for m in $wave_file
do 
if [ $count -gt 0 ]; then
	mv $testbench#$count.sw0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l#$count.sw0
else
	mv $testbench.sw0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l.sw0
fi
count=`expr $count + 1`
done

fi
}
elif [ "$simulator" == "primesim" ]; then
{
if [ -f "$testbench"_a0".fsdb" ]; then
wave_file=`ls $result_path | grep -e "fsdb"`
count=0
for m in $wave_file
do 
	mv $testbench"_a"$count.fsdb $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l"_a"$count.fsdb
count=`expr $count + 1`
done

elif [ -f "$testbench"_a0".ac0" ]; then
wave_file=`ls $result_path | grep -e "ac0"`
count=0
for m in $wave_file
do 
	mv $testbench"_a"$count.ac0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l"_a"$count.ac0
count=`expr $count + 1`
done

elif [ -f "$testbench"_a0".sw0" ]; then
wave_file=`ls $result_path | grep -e "sw0"`
count=0
for m in $wave_file
do 
	mv $testbench"_a"$count.sw0 $current_path/compiled_waveform/$testbench\_$i\_$j\_$k\_$l"_a"$count.sw0
count=`expr $count + 1`
done

fi
}

#spectre

fi
cd ..
rm -r result

cd $current_path
}

fi

# execute pvt loop
#### need to check if change to seq, how long is the ext time, if ok, then runme.sh no need add long wait time.
#gen_pvt_loop_par
gen_pvt_loop_seq
}


elif [ $( echo $stage | grep -w srt ) ]; then
{
#
echo "start data sorting"

echo "supply condition" > report/creport.txt
echo "v1: $supply1" >> report/creport.txt
echo "v2: $supply2" >> report/creport.txt
echo "v3: $supply3" >> report/creport.txt

if [ "$vcc_vid" == "Yes" ]; then
{
echo "vcc_vid: vcc_ff_h#$vccmin_ff_h,$vccnom_ff_h,$vccmax_ff_h; vcc_ff_c#$vccmin_ff_c,$vccnom_ff_c,$vccmax_ff_c; vcc_tt_h#$vccmin_tt_h,$vccnom_tt_h,$vccmax_tt_h; vcc_tt_c#$vccmin_tt_c,$vccnom_tt_c,$vccmax_tt_c; vcc_ss_h#$vccmin_ss_h,$vccnom_ss_h,$vccmax_ss_h; vcc_ss_c#$vccmin_ss_c,$vccnom_ss_c,$vccmax_ss_c" >> report/creport.txt
}
else
{
echo "vcc none vid: $vccmin,$vccnom,$vccmax" >> report/creport.txt
}
fi

echo "vccana: $vccanamin,$vccananom,$vccanamax" >> report/creport.txt
echo "vccn: $vcnmin,$vcnnom,$vcnmax" >> report/creport.txt
echo "vcctx: $vctxmin,$vctxnom,$vctxmax" >> report/creport.txt
echo "" >> report/creport.txt

#creport Header
if [ "$supply3" == "vccn" ]; then
{
line=`head -n 1 report/report_$typ_corner\_$typ_ex\_85_v1nom_v2nom_v3nom.txt | tail -1`
read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
echo "process	extract	temp	v1	v2	v3	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt
}
elif [ "$supply3" == "vccn_vcctx" ]; then
{
line=`head -n 1 report/report_$typ_corner\_$typ_ex\_85_v1nom_v2nom_v3nom.txt | tail -1`
read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
echo "process	extract	temp	v1	v2	v3	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt
}
elif [ "$supply2" == "NA" ]; then
{
line=`head -n 1 report/report_$typ_corner\_$typ_ex\_85_v1nom.txt | tail -1`
read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
echo "process	extract	temp	v1	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt
}
else
{
line=`head -n 1 report/report_$typ_corner\_$typ_ex\_85_v1nom_v2nom.txt | tail -1`
read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
echo "process	extract	temp	v1	v2	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt
}
fi




core_func ()
{
count=1
	
while [ $count -lt $(wc -l < report/report_$i\_$j\_$k\_$l.txt) ]
do
	count=`expr $count + 1`

if [ "$supply3" == "vccn" ]; then
{
	line=`head -n $count report/report_$i\_$j\_$k\_$l.txt | tail -1`
	read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
	echo "$i	$j	$tmp	$lv1	$lv2	$lv3	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt

}
elif [ "$supply3" == "vccn_vcctx" ]; then
{
	line=`head -n $count report/report_$i\_$j\_$k\_$l.txt | tail -1`
	read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
	echo "$i	$j	$tmp	$lv1	$lv2	$lv3	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt

}
elif [ "$supply2" == "NA" ]; then
{
	line=`head -n $count report/report_$i\_$j\_$k\_$l.txt | tail -1`
	read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
	echo "$i	$j	$tmp	$lv1	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt

}
else
{
	line=`head -n $count report/report_$i\_$j\_$k\_$l.txt | tail -1`
	read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 <<< $line
	echo "$i	$j	$tmp	$lv1	$lv2	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100" >> report/creport.txt

}
fi

done
}
# execute pvt loop
gen_pvt_loop_seq
}

elif [ $( echo $stage | grep -w bkp ) ]; then
{
echo "start data backup"
timestamp=$(date +"%Y%m%d%H%M")

mkdir -p 00bkp_$timestamp
mv report 00bkp_$timestamp/
mv compiled_waveform 00bkp_$timestamp/

if [ "$supply3" == "vccn" ]; then
{
cp $current_path/$typ_corner/$typ_ex/$typ_ex\_85/v1nom_v2nom_v3nom/$testbench.log $current_path/00bkp_$timestamp/simulation.log
}
elif [ "$supply3" == "vccn_vcctx" ]; then
{
cp $current_path/$typ_corner/$typ_ex/$typ_ex\_85/v1nom_v2nom_v3nom/$testbench.log $current_path/00bkp_$timestamp/simulation.log
}
elif [ "$supply2" == "NA" ]; then
{
cp $current_path/$typ_corner/$typ_ex/$typ_ex\_85/v1nom/$testbench.log $current_path/00bkp_$timestamp/simulation.log
}
else
{
cp $current_path/$typ_corner/$typ_ex/$typ_ex\_85/v1nom_v2nom/$testbench.log $current_path/00bkp_$timestamp/simulation.log
}
fi

## to add copy TT folder as bkp for checking
#cp -r $current_path/$typ_corner/$typ_ex/ $current_path/00bkp_$timestamp/tb_bkp
rsync -a --include='*.sp' --include='*/' --exclude='*' $current_path/$typ_corner/$typ_ex/ $current_path/00bkp_$timestamp/tb_bkp

core_func ()
{
rm -f -r $i
}
# execute pvt loop
gen_pvt_loop_seq

}

elif [ $( echo $stage | grep -w chk ) ]; then
{
#nbstatus jobs --target png_normal

echo "corners   status" > $current_path/job_stat.log
> $current_path/rerun.sh

core_func ()
{
cd $i/$j/$j\_$k/$l

if [ -f $testbench.log ]; then

found=0

if [ "$simulator" == "finesim" ]; then

if grep -q "FineSim Successfully Completed" $testbench.log; then
found=1
fi
elif [ "$simulator" == "primesim" ]; then
if grep -q "PrimeSim Successfully Completed" $testbench.log; then
found=1
fi
#spectre
fi

if [ "$found" -eq 1 ]; then
echo "$i $j $k $l    Done" >> $current_path/job_stat.log
else
echo "$i $j $k $l    not-complete, check if error" >> $current_path/job_stat.log
echo "cd $current_path/$i/$j/$j""_$k/$l" >> $current_path/rerun.sh
echo "rerun" > $current_path/rerun
if [ "$simulator" == "finesim" ]; then
{
echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' finesim -np $cpu $testbench.sp -o $testbench" >> $current_path/rerun.sh
}
elif [ "$simulator" == "primesim" ]; then
{
echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' primesim -np $cpu -spice $testbench.sp -o $testbench" >> $current_path/rerun.sh
}
#to add spectre
else
{
echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' finesim -np $cpu $testbench.sp -o $testbench" >> $current_path/rerun.sh
}
fi
fi

else
echo "$i $j $k $l    not-start" >> $current_path/job_stat.log
echo "cd $current_path/$i/$j/$j""_$k/$l" >> $current_path/rerun.sh
echo "rerun" > $current_path/rerun
if [ "$simulator" == "finesim" ]; then
{
echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' finesim -np $cpu $testbench.sp -o $testbench" >> $current_path/rerun.sh
}
elif [ "$simulator" == "primesim" ]; then
{
echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' primesim -np $cpu -spice $testbench.sp -o $testbench" >> $current_path/rerun.sh
}
#to add spectre
else
{
echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$cpu'C' finesim -np $cpu $testbench.sp -o $testbench" >> $current_path/rerun.sh
}
fi
#echo "cd $current_path" >> $current_path/rerun.sh
fi
}

if [ "$mode" == "prelay" ]; then
{
# execute pvt loop
gen_pvt_loop_seq
echo "cd $current_path" >> $current_path/rerun.sh
}
else
{

if [ -z $run_ex_corner ]; then
echo "#run_ex_corner not specifid, please specified: typical/cworst_CCworst_T/cbest_CCbest_T"
else
# execute pvt loop for polo
run_pvt_loop_polo
echo "cd $current_path" >> $current_path/rerun.sh
fi

}
fi

if [ -f rerun ]; then
{
echo "rerun.sh script generated for un-completed job"
rm rerun
}
else
{
rm rerun.sh
}
fi

}
elif [ $( echo $stage | grep -w usr_script ) ]; then
{
source usr_script.sh
usr_script
# execute pvt loop
gen_pvt_loop_seq
}

else

echo "invalid stage, please specified as:"
echo "sim_pvt cofig_file {stage}"
echo "stage = gen  --> generate testbench & directory"
echo "stage = run  --> submit sim to farm, please specified #cpu according to your simulation size"
echo "stage = ext  --> to extract data after sim completed, alter data, swpl = alter title length"
echo "stage = srt  --> to sort data after extraction completed"
echo "stage = bkp  --> backup data to 00bkp_{time} folder"
echo "stage execution by stages: gen -> run -> ext* -> srt*"


fi
