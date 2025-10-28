#!/bin/bash

# sh extract.sh $testbench $swpl $simulator (finesim/primesim)

current_path=`pwd`
testbench=$1
swpl=$2
simulator=$3

mkdir -p result


if [ -f $testbench.postl/$testbench.log ]; then
	rm -r $testbench.postl
fi

rm -f $testbench*.pd0
rm -f $testbench.fp.log*
rm -f $testbench.log*
rm -f $testbench*.pdmi*
rm -f $testbench.pa*
rm -f $testbench*.ic*
rm -f $testbench.st*
rm -f $testbench.lis
rm -f $testbench.elog
rm - *.grp
rm -f ##*


directory="$current_path/result"

if [ "$simulator" == "finesim" ]; then
{

if [ -f "$testbench.mt0" ]; then
	mv $testbench*.mt* result
fi

if [ -f "$testbench.tr0" ]; then
	mv $testbench*.tr* result
fi

if [ -f "$testbench.fsdb" ]; then
	mv $testbench*.fsdb* result
fi

if [ -f "$testbench.ac0" ]; then
	mv $testbench*.ac0 result
fi

if [ -f "$testbench.ma0" ]; then
	mv $testbench*.ma0 result
fi

if [ -f "$testbench.sw0" ]; then
	mv $testbench*.sw0 result
fi

if [ -f "$testbench.md0" ]; then
	mv $testbench*.md0 result
fi

if [ -f "$current_path/result/$testbench.mt0" ]; then
	meas="mt0"
fi

if [ -f "$current_path/result/$testbench.ma0" ]; then
	meas="ma0"
fi

if [ -f "$current_path/result/$testbench.md0" ]; then
	meas="md0"
fi

result_files=`ls  $directory | grep -e $meas`
count=0

cd $directory

for j in $result_files
do
if [ $count -gt 0 ]; then
mv $testbench#$count.$meas $testbench.$meas$count
else
mv $testbench.$meas $testbench.$meas$count
fi
count=`expr $count + 1`
done

cd $current_path
}

elif [ "$simulator" == "primesim" ]; then 
{
if [ -f "$testbench"_a0".mt0" ]; then
	mv $testbench*.mt* result
fi

if [ -f "$testbench"_a0".tr0" ]; then
	mv $testbench*.tr* result
fi

if [ -f "$testbench"_a0".fsdb" ]; then
	mv $testbench*.fsdb* result
fi

if [ -f "$testbench"_a0".ac0" ]; then
	mv $testbench*.ac0 result
fi

if [ -f "$testbench"_a0".ma0" ]; then
	mv $testbench*.ma0 result
fi

if [ -f "$testbench"_a0".sw0" ]; then
	mv $testbench*.sw0 result
fi

if [ -f "$testbench"_a0".md0" ]; then
	mv $testbench*.md0 result
fi

if [ -f "$current_path/result/$testbench""_a0.mt0" ]; then
	meas="mt0"
fi

if [ -f "$current_path/result/$testbench""_a0.ma0" ]; then
	meas="ma0"
fi

if [ -f "$current_path/result/$testbench""_a0.md0" ]; then
	meas="md0"
fi

result_files=`ls  $directory | grep -e $meas`
count=0

cd $directory

for j in $result_files
do
mv $testbench"_a"$count.$meas $testbench.$meas$count
count=`expr $count + 1`
done

cd $current_path
}

#spectre

fi



count=0
result_files=`ls -r -t $directory | grep -e $meas`

#create header limit param 100
line1=`head -n 3 $directory/$testbench.$meas$count | tail -1`
read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 var101 var102 <<< $line1
echo "swp	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100	$var101	$var102" > report.txt

#read data
for i in $result_files
do

line0=`head -n 2 $directory/$testbench.$meas$count | tail -1`
read var0 var1 <<< $line0

var1=`echo $var1 | tr -d "[='=]"`
var1=${var1:0:$swpl}
varswp=`echo $var1 | tr -d '\n'`

line1=`head -n 4 $directory/$testbench.$meas$count | tail -1`
read var1 var2 var3 var4 var5 var6 var7 var8 var9 var10 var11 var12 var13 var14 var15 var16 var17 var18 var19 var20 var21 var22 var23 var24 var25 var26 var27 var28 var29 var30 var31 var32 var33 var34 var35 var36 var37 var38 var39 var40 var41 var42 var43 var44 var45 var46 var47 var48 var49 var50 var51 var52 var53 var54 var55 var56 var57 var58 var59 var60 var61 var62 var63 var64 var65 var66 var67 var68 var69 var70 var71 var72 var73 var74 var75 var76 var77 var78 var79 var80 var81 var82 var83 var84 var85 var86 var87 var88 var89 var90 var91 var92 var93 var94 var95 var96 var97 var98 var99 var100 var101 var102 <<< $line1
echo "$varswp	$var1	$var2	$var3	$var4	$var5	$var6	$var7	$var8	$var9	$var10	$var11	$var12	$var13	$var14	$var15	$var16	$var17	$var18	$var19	$var20	$var21	$var22	$var23	$var24	$var25	$var26	$var27	$var28	$var29	$var30	$var31	$var32	$var33	$var34	$var35	$var36	$var37	$var38	$var39	$var40	$var41	$var42	$var43	$var44	$var45	$var46	$var47	$var48	$var49	$var50	$var51	$var52	$var53	$var54	$var55	$var56	$var57	$var58	$var59	$var60	$var61	$var62	$var63	$var64	$var65	$var66	$var67	$var68	$var69	$var70	$var71	$var72	$var73	$var74	$var75	$var76	$var77	$var78	$var79	$var80	$var81	$var82	$var83	$var84	$var85	$var86	$var87	$var88	$var89	$var90	$var91	$var92	$var93	$var94	$var95	$var96	$var97	$var98	$var99	$var100	$var101	$var102" >> report.txt

count=`expr $count + 1`

done

exit 0


