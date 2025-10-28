#!/bin/bash
usr_script ()
{

## single run code:

ls -d 00bkp* > bkp.list
lastline=$(tail -n 1 bkp.list)
rm bkp.list
echo "read data from $lastline"

bkpfolder=$lastline

libpath="/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/calvsshleak_lib/"
mkdir -p $libpath

libfile="1p05v_ctt_calvsshleak.lib"
listfile="1p05v_ctt_calvsshleak_list.txt"

echo "*vsshi leak code lib*" 
echo "*vsshi leak code lib*" > $libpath/$libfile
echo "" >> $libpath/$libfile

echo "pvt	target	value	code" > $libpath/$listfile

## single run code:


core_func ()
{

## PVT loop code:

echo ".lib $i""_$j""_$k""_$l" >> $libpath/$libfile

echo "fail" > $current_path/comp_temp.txt
count="17"
rowx="2"
targ="0"



while [ $( cat $current_path/comp_temp.txt | grep -w fail ) ] && [ $count -gt 1 ]
do
line=`head -n $rowx $current_path/$bkpfolder/report/report_$i\_$j\_$k\_$l.txt | tail -1`
read aa bb xx yy zz val tt uu <<< $line
#val=$(echo "${line[$index]%e-*}*10^(-1*${line[$index]#*e-})" | bc -l)
perl $current_path/compare.pl $targ $val > $current_path/comp_temp.txt
(( count -- ))
(( rowx ++ ))
done

rm $current_path/comp_temp.txt

vall=`expr $rowx - 3`

bin=$(echo "obase=2;$vall" | bc | xargs printf "%04d\n")

echo "*target: $zz, value: $yy*" >> $libpath/$libfile


for char_num in $(seq 0 3)
do
	if [ $( echo ${bin:$char_num:1} | grep -w 0 ) ]; then
		echo ".param vsshleak$((3-$char_num)) = 0" >> $libpath/$libfile
	elif [ $( echo ${bin:$char_num:1} | grep -w 1 ) ]; then
		echo ".param vsshleak$((3-$char_num)) = 1" >> $libpath/$libfile
	fi
done

echo ".endl" >> $libpath/$libfile
echo "" >> $libpath/$libfile

echo "$i"_"$j"_"$k"_"$l	$zz	$yy	$vall" >> $libpath/$listfile

## PVT loop code:

}
}

