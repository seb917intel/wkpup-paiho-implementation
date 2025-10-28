#!/bin/sh

# sh move.sh $testbench

testbench=$1
if [ -f $testbench.postl/$testbench.log ]; then
	rm -r $testbench.postl
fi

rm -f $testbench*.pd0
rm -f $testbench.fp.log*
#rm -f $testbench.log*
rm -f $testbench*.pdmi*
rm -f $testbench.pa*
rm -f $testbench*.ic*
rm -f $testbench.st*
rm -f $testbench.lis
rm -f $testbench.elog
rm -f ##*

if [ -f "$testbench.mt0" ]; then
	mv $testbench*.mt* result
fi

if [ -f "$testbench""_a0.mt0" ]; then
	mv $testbench*.mt* result
fi

if [ -f "$testbench.tr0" ]; then
	mv $testbench*.tr* result
fi

if [ -f "$testbench""_a0.tr0" ]; then
	mv $testbench*.tr* result
fi

if [ -f "$testbench.fsdb" ]; then
	mv $testbench*.fsdb* result
fi

if [ -f "$testbench""_a0.fsdb" ]; then
	mv $testbench*.fsdb* result
fi

if [ -f "$testbench.ac0" ]; then
	mv $testbench*.ac0 result
fi

if [ -f "$testbench""_a0.ac0" ]; then
	mv $testbench*.ac0 result
fi

if [ -f "$testbench.ma0" ]; then
	mv $testbench*.ma0 result
fi

if [ -f "$testbench""_a0.ma0" ]; then
	mv $testbench*.ma0 result
fi

if [ -f "$testbench.sw0" ]; then
	mv $testbench*.sw0 result
fi

if [ -f "$testbench""_a0.sw0" ]; then
	mv $testbench*.sw0 result
fi

if [ -f "$testbench.md0" ]; then
	mv $testbench*.md0 result
fi

if [ -f "$testbench""_a0.md0" ]; then
	mv $testbench*.md0 result
fi
