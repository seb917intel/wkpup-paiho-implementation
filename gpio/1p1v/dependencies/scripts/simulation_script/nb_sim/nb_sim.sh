#!/bin/sh

# sh lsfsim.sh testbench.sp hspice/finesim ncpu memory

testbench=$1
simulator=$2
ncpu=$3
mem=$4

outfile=`echo $testbench | sed 's/.sp//g'`

if [ -z "$testbench" ]; then

echo "sim [testbench.sp] [hspice/finesim/spectre] [ncpu] [memory]G"

elif [ -z "$simulator" ]; then

echo "simulator not specified"
echo "sim [testbench.sp] [hspice/finesim/spectre] [ncpu] [memory]G"

elif [ -z "$ncpu" ]; then

echo "ncpu not specified"
echo "sim [testbench.sp] [hspice/finesim/spectre] [ncpu] [memory]G"

elif [ -z "$mem" ]; then

echo "memory not specified"
echo "sim [testbench.sp] [hspice/finesim/spectre] [ncpu] [memory]G"

elif [ $simulator = "hspice" ]; then

echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' hspice -mt $ncpu -i $testbench -o $outfile >& /dev/null"
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' hspice -mt $ncpu -i $testbench -o $outfile >& /dev/null

elif [ $simulator = "finesim" ]; then

echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' finesim -np $ncpu $testbench -o $outfile >& /dev/null"
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' finesim -np $ncpu $testbench -o $outfile >& /dev/null

elif [ $simulator = "primesim" ]; then

echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' primesim -np $ncpu -spice $testbench -o $outfile >& /dev/null"
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' primesim -np $ncpu -spice $testbench -o $outfile >& /dev/null

elif [ $simulator = "spectre" ]; then

echo "nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' spectre +aps=liberal +mt=$ncpu $testbench -o $outfile >& /dev/null"
nbjob run --target altera_png_normal --qslot /psg/km/phe/ckt/gen --class 'SLES15&&'$mem'G&&'$ncpu'C' spectre +aps=liberal +mt=$ncpu $testbench -o $outfile >& /dev/null

else

echo "incorrect simulator"
echo "hspice/finesim"

fi


