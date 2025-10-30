#!/bin/bash
# Mock sim_pvt.sh for testing
# Simulates Pai Ho's script behavior

config_file=$1
stage=$2

echo "Mock sim_pvt.sh: config=$config_file stage=$stage"

case $stage in
    gen)
        echo "Generating testbenches..."
        mkdir -p TT/typical/typical_85/v1nom
        echo "netlist" > TT/typical/typical_85/v1nom/sim_tx.sp
        exit 0
        ;;
    run)
        echo "Running simulations..."
        sleep 1
        echo "simulation complete" > TT/typical/typical_85/v1nom/sim_tx.mt0
        exit 0
        ;;
    ext)
        echo "Extracting results..."
        exit 0
        ;;
    srt)
        echo "Sorting results..."
        mkdir -p report
        echo "consolidated report" > report/creport.txt
        exit 0
        ;;
    bkp)
        echo "Backing up results..."
        mkdir -p 00bkp_test
        exit 0
        ;;
    usr)
        echo "Running user script..."
        exit 0
        ;;
    *)
        echo "Unknown stage: $stage"
        exit 1
        ;;
esac
