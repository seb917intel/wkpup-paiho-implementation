# Simulation Flow Analysis: wkpup2 Baseline Reference

## Document Purpose

This document provides the **authoritative baseline** for the complete simulation workflow in Pai Ho's wkpup2 implementation. It serves as the reference for identifying execution flow gaps and inconsistencies when comparing against the wkpup automation system.

**Status**: ✅ BASELINE REFERENCE (wkpup2)  
**Source**: COMPREHENSIVE_ANALYSIS.md and actual wkpup2 implementation  
**Main Orchestrator**: `sim_pvt.sh`

---

## Executive Summary

### 6-Stage Workflow Overview

The wkpup2 simulation framework follows a **deterministic 6-stage pipeline**:

```
Stage 1: Generation (gen)  → Creates 84 PVT netlists from template
Stage 2: Simulation (run)  → Executes SPICE on all corners
Stage 3: Extraction (ext)  → Parses .mt0 measurement files
Stage 4: Sorting (srt)     → Aggregates results into reports
Stage 5: Backup (bkp)      → Creates timestamped archive
Stage 6: User Script (usr) → Optional post-processing
```

### Entry Point

**User Command**:
```bash
./runme.sh
```

**Actual Execution**:
```bash
sh $sim_pvt config.cfg gen run ext srt bkp
```

**Critical Files**:
- `runme.sh` - User entry point (sources environment, calls sim_pvt.sh)
- `sim_pvt.sh` - Main orchestration script (coordinates all stages)
- `config.cfg` - Configuration parameters (15 settings)

---

## 1. runme.sh - User Entry Point

### File Location
```
gpio/1p1v/runme.sh
i3c/1p1v/runme.sh
```

### Complete runme.sh Content

```bash
#!/bin/bash

# Source simulation environment
source /nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/env_setup.sh

# Define paths
sim_pvt="dependencies/scripts/simulation_script/auto_pvt/ver03/sim_pvt.sh"
cfg="config.cfg"

# Execute simulation workflow
sh $sim_pvt $cfg gen run ext srt bkp

# Optional: Run user-defined post-processing script
# sh $sim_pvt $cfg usr
```

### Key Responsibilities

1. **Environment Setup**: Sources common environment variables
   - Simulator paths (PrimeSim/FineSim)
   - Library paths
   - Tool licenses
   - Job submission configuration

2. **Path Configuration**:
   - Defines `sim_pvt` → location of orchestration script
   - Defines `cfg` → location of configuration file

3. **Workflow Execution**:
   - Calls `sim_pvt.sh` with stages: `gen run ext srt bkp`
   - Optionally calls `usr` stage for custom post-processing

### Validation Points

When comparing wkpup automation:
- [ ] Does wkpup use equivalent entry point script?
- [ ] Is environment setup identical?
- [ ] Are stage sequences the same (gen run ext srt bkp)?
- [ ] Is config file passed correctly?

---

## 2. sim_pvt.sh - Main Orchestration Script

### File Location
```
dependencies/scripts/simulation_script/auto_pvt/ver03/sim_pvt.sh
```

### Script Structure

**Size**: ~800 lines of bash script

**Main Sections**:
1. **Library Sourcing** (Lines 1-50)
2. **Configuration Parsing** (Lines 51-150)
3. **Stage Functions** (Lines 151-600)
4. **Main Execution Logic** (Lines 601-800)

### Library Dependencies

**sim_pvt.sh sources these libraries**:

```bash
# Line 10-20: Source configuration readers
source configuration/read_cfg.sh      # Parses config.cfg → 15 parameters
source configuration/read_supply.sh   # Reads CSV → voltage values
source configuration/read_corner.sh   # Reads CSV → corner definitions

# Line 30-40: Source stage functions
source tb_gen/pvt_loop.sh            # Defines PVT matrix loops
source data_extraction/extract_alt.sh # Defines extraction functions
source data_extraction/move.sh       # Defines file organization
source runme_script/runme_func.sh    # Defines simulation execution
```

### Configuration Parsing

**After sourcing libraries, sim_pvt.sh**:

```bash
# Read config.cfg (15 parameters)
read_cfg $config_file

# Outputs these global variables:
# - mode (prelay/postlay)
# - vccn (voltage domain)
# - vcctx (TX voltage)
# - supply_swp_1st, supply_swp_2nd, supply_swp_3rd
# - condition (perf/func/htol)
# - CPU, MEM
# - alter_extraction, alter_string
# - sim_mode (ac/dc)
# - gs_corner, gf_corner
# - vcc_vid (Yes/No)
# - simulator (primesim/finesim)
# - postlay_cross_cornerlist

# Read voltage CSV tables
read_supply $vccn $vcctx $sim_mode

# Outputs voltage arrays:
# - vccmin, vccnom, vccmax
# - vcnmin, vcnnom, vcnmax
# - vccanamin, vccananom, vccanamax
# - vctxmin, vctxnom, vctxmax

# Read corner CSV tables
read_corner $gs_corner $gf_corner

# Outputs corner arrays:
# - si_corner_list (TT, FFG, SSG, FSG, SFG, FFAG, SSAG)
# - ex_corner_list (typical, cworst_CCworst_T, cbest_CCbest_T)
```

---

## 3. Stage 1: Generation (gen)

### Function: gen_stage()

**Location**: sim_pvt.sh, Lines ~200-280

**Purpose**: Generate PVT matrix of testbench netlists

### Execution Flow

```bash
gen_stage() {
    echo "==================================="
    echo "STAGE 1: TESTBENCH GENERATION (gen)"
    echo "==================================="
    
    # Clean previous generation
    rm -rf TT FFG SSG FSG SFG FFAG SSAG 2>/dev/null
    
    # Determine parallel or sequential execution
    if [ "$CPU" -gt 1 ]; then
        echo "Parallel generation enabled (CPU=$CPU)"
        gen_pvt_loop_par  # Parallel generation
    else
        echo "Sequential generation (CPU=1)"
        gen_pvt_loop_seq  # Sequential generation
    fi
    
    # Verify generation completed
    check_generation_complete
    
    echo "Generation complete: $(count_netlists) netlists created"
}
```

### PVT Loop Functions (pvt_loop.sh)

#### Sequential Generation: gen_pvt_loop_seq()

```bash
gen_pvt_loop_seq() {
    for si_corner in $si_corner_list; do
        for ex_corner in $ex_corner_list; do
            for temp in $temp_list; do
                for voltage_combo in $voltage_list; do
                    # Create directory
                    mkdir -p $si_corner/$ex_corner/${ex_corner}_${temp}/$voltage_combo
                    
                    # Generate netlist
                    core_func $si_corner $ex_corner $temp $voltage_combo
                done
            done
        done
    done
}
```

#### Parallel Generation: gen_pvt_loop_par()

```bash
gen_pvt_loop_par() {
    # Build job array
    jobs=()
    for si_corner in $si_corner_list; do
        for ex_corner in $ex_corner_list; do
            for temp in $temp_list; do
                for voltage_combo in $voltage_list; do
                    jobs+=("$si_corner $ex_corner $temp $voltage_combo")
                done
            done
        done
    done
    
    # Execute jobs in parallel (max $CPU processes)
    printf '%s\n' "${jobs[@]}" | xargs -P $CPU -I {} bash -c 'core_func {}'
}
```

### Core Generation Function: core_func()

```bash
core_func() {
    local si_corner=$1
    local ex_corner=$2
    local temp=$3
    local voltage_combo=$4
    
    # Parse voltage combo (e.g., v1nom_v2max)
    parse_voltage_combo $voltage_combo  # Sets vtrend_v1, vtrend_v2, vtrend_v3
    
    # Determine supply configuration
    determine_supply_config  # Sets supply1, supply2, supply3
    
    # Get voltage values
    get_voltage_values $vtrend_v1 $vtrend_v2 $vtrend_v3
    
    # Call gen_tb.pl
    perl tb_gen/gen_tb.pl \
        template/sim_tx.sp \
        $si_corner $ex_corner $temp \
        $vtrend_v1 $vtrend_v2 $vtrend_v3 \
        $supply1 $supply2 $supply3 \
        $vccmin $vccnom $vccmax \
        $vcnmin $vcnnom $vcnmax \
        $vccanamin $vccananom $vccanamax \
        $vctxmin $vctxnom $vctxmax \
        $vcc_vid \
        $vccmin_tt_h $vccnom_tt_h $vccmax_tt_h \
        $vccmin_tt_c $vccnom_tt_c $vccmax_tt_c \
        $vccmin_ff_h $vccnom_ff_h $vccmax_ff_h \
        $vccmin_ff_c $vccnom_ff_c $vccmax_ff_c \
        $vccmin_ss_h $vccnom_ss_h $vccmax_ss_h \
        $vccmin_ss_c $vccnom_ss_c $vccmax_ss_c \
        > $si_corner/$ex_corner/${ex_corner}_${temp}/$voltage_combo/sim_tx.sp
}
```

### Generation Validation

```bash
check_generation_complete() {
    # Expected count based on mode
    if [ "$mode" = "prelay" ]; then
        expected=84  # 7 corners × 1 extraction × 4 temps × 3 voltages
    else
        expected=252 # 7 corners × 3 extractions × 4 temps × 3 voltages
    fi
    
    # Actual count
    actual=$(find . -name "sim_tx.sp" | wc -l)
    
    if [ $actual -ne $expected ]; then
        echo "ERROR: Expected $expected netlists, found $actual"
        exit 1
    fi
}
```

### Output Structure

```
TT/typical/typical_85/v1nom/sim_tx.sp
TT/typical/typical_85/v1min/sim_tx.sp
TT/typical/typical_85/v1max/sim_tx.sp
TT/typical/typical_m40/v1nom/sim_tx.sp
... (84 total for pre-layout)
```

---

## 4. Stage 2: Simulation (run)

### Function: run_stage()

**Location**: sim_pvt.sh, Lines ~300-400

**Purpose**: Execute SPICE simulations on all generated netlists

### Execution Flow

```bash
run_stage() {
    echo "==================================="
    echo "STAGE 2: SIMULATION EXECUTION (run)"
    echo "==================================="
    
    # Run simulations for each extraction corner
    for ex_corner in $ex_corner_list; do
        echo "Running extraction corner: $ex_corner"
        run_sim $ex_corner
    done
    
    # Wait for all jobs to complete
    wait_for_jobs
    
    # Verify simulation completed
    check_simulation_complete
    
    echo "Simulation complete"
}
```

### Simulation Function: run_sim()

**Source**: runme_script/runme_func.sh

```bash
run_sim() {
    local ex_corner=$1
    
    # Find all netlists for this extraction corner
    netlist_dirs=$(find . -type d -path "*/$ex_corner/${ex_corner}_*")
    
    for dir in $netlist_dirs; do
        # Navigate to netlist directory
        cd $dir
        
        # Determine simulator command
        if [ "$simulator" = "primesim" ]; then
            sim_cmd="primesim -np $CPU -spice sim_tx.sp -o sim_tx"
        elif [ "$simulator" = "finesim" ]; then
            sim_cmd="finesim -spice sim_tx.sp -o sim_tx"
        fi
        
        # Submit job to cluster
        nbjob run \
            --target altera_png_normal \
            --qslot /psg/km/phe/ckt/gen \
            --class "SLES15&&${MEM}G&&${CPU}C" \
            --name "sim_${si_corner}_${temp}_${voltage}" \
            $sim_cmd
        
        # Return to top directory
        cd - >/dev/null
    done
}
```

### nbjob Command Structure

**Critical Components**:
```bash
nbjob run \
    --target altera_png_normal       # Cluster target
    --qslot /psg/km/phe/ckt/gen     # Resource queue
    --class 'SLES15&&4G&&8C'         # OS + Memory + CPU requirements
    --name sim_TT_85_v1nom           # Job name (for tracking)
    primesim -np 8 -spice sim_tx.sp -o sim_tx  # Simulator command
```

### Job Management

```bash
wait_for_jobs() {
    echo "Waiting for simulation jobs to complete..."
    
    while true; do
        # Check job status
        running=$(nbjob list | grep -c "RUNNING\|PENDING")
        
        if [ $running -eq 0 ]; then
            echo "All jobs completed"
            break
        fi
        
        echo "Jobs remaining: $running"
        sleep 60  # Check every minute
    done
}
```

### Simulation Validation

```bash
check_simulation_complete() {
    # Expected .mt0 files
    expected=$(find . -name "sim_tx.sp" | wc -l)
    
    # Actual .mt0 files
    actual=$(find . -name "sim_tx.mt0" | wc -l)
    
    if [ $actual -ne $expected ]; then
        echo "WARNING: Expected $expected .mt0 files, found $actual"
        
        # Find failed simulations
        find . -name "sim_tx.sp" | while read netlist; do
            dir=$(dirname $netlist)
            if [ ! -f "$dir/sim_tx.mt0" ]; then
                echo "FAILED: $dir"
            fi
        done
    fi
}
```

### Output Files (per corner/temp/voltage)

```
sim_tx.mt0   - Measurement results (CRITICAL)
sim_tx.log   - Simulation log
sim_tx.fsdb  - Waveform data (if enabled)
sim_tx.tr0   - Transient results
```

---

## 5. Stage 3: Extraction (ext)

### Function: ext_stage()

**Location**: sim_pvt.sh, Lines ~420-480

**Purpose**: Parse .mt0 files and extract measurement data

### Execution Flow

```bash
ext_stage() {
    echo "==================================="
    echo "STAGE 3: DATA EXTRACTION (ext)"
    echo "==================================="
    
    # Call extraction script
    extract_alt
    
    # Verify extraction completed
    check_extraction_complete
    
    echo "Extraction complete"
}
```

### Extraction Function: extract_alt()

**Source**: data_extraction/extract_alt.sh

```bash
extract_alt() {
    # Create extraction output directory
    mkdir -p report/raw_data
    
    # Find all .mt0 files
    mt0_files=$(find . -name "sim_tx.mt0")
    
    for mt0_file in $mt0_files; do
        # Parse corner/temp/voltage from path
        parse_path $mt0_file  # Sets si_corner, temp, voltage
        
        # Extract measurements
        extract_measurements $mt0_file
        
        # Write to output file
        echo "$si_corner,$temp,$voltage,$measurements" >> report/raw_data/extracted.csv
    done
}
```

### Measurement Extraction Logic

```bash
extract_measurements() {
    local mt0_file=$1
    
    # Typical measurements extracted:
    # - trise: Rising edge delay
    # - tfall: Falling edge delay
    # - ipeak: Peak current
    # - rpullup: Pull-up resistance
    # - voh: Output high voltage
    # - vol: Output low voltage
    
    trise=$(grep "trise=" $mt0_file | awk '{print $2}')
    tfall=$(grep "tfall=" $mt0_file | awk '{print $2}')
    ipeak=$(grep "ipeak=" $mt0_file | awk '{print $2}')
    rpullup=$(grep "rpullup=" $mt0_file | awk '{print $2}')
    voh=$(grep "voh=" $mt0_file | awk '{print $2}')
    vol=$(grep "vol=" $mt0_file | awk '{print $2}')
    
    # Return comma-separated values
    measurements="$trise,$tfall,$ipeak,$rpullup,$voh,$vol"
}
```

### Extraction Output

```
report/raw_data/extracted.csv

Format:
corner,temp,voltage,trise,tfall,ipeak,rpullup,voh,vol
TT,85,v1nom,2.5e-9,2.8e-9,150e-6,7.3e3,1.08,0.02
TT,85,v1max,2.2e-9,2.5e-9,165e-6,6.8e3,1.15,0.01
...
```

---

## 6. Stage 4: Sorting (srt)

### Function: srt_stage()

**Location**: sim_pvt.sh, Lines ~500-560

**Purpose**: Aggregate extracted data into consolidated reports

### Execution Flow

```bash
srt_stage() {
    echo "==================================="
    echo "STAGE 4: REPORT GENERATION (srt)"
    echo "==================================="
    
    # Create report directory
    mkdir -p report
    
    # Generate consolidated report
    generate_creport
    
    # Generate summary statistics
    generate_summary
    
    echo "Report generation complete"
}
```

### Consolidated Report: creport.txt

```bash
generate_creport() {
    # Header
    cat > report/creport.txt <<EOF
================================================================================
WKPUP Simulation Results - Consolidated Report
Generated: $(date)
Mode: $mode
Voltage Domain: $vccn
Condition: $condition
================================================================================

EOF
    
    # Sort by corner, then temp, then voltage
    sort -t, -k1,1 -k2,2n -k3,3 report/raw_data/extracted.csv | \
    while IFS=, read corner temp voltage measurements; do
        printf "%-8s %-6s %-8s %s\n" \
            "$corner" "$temp" "$voltage" "$measurements" \
            >> report/creport.txt
    done
    
    # Footer
    cat >> report/creport.txt <<EOF

================================================================================
Total simulations: $(wc -l < report/raw_data/extracted.csv)
================================================================================
EOF
}
```

### Summary Statistics

```bash
generate_summary() {
    cat > report/summary.txt <<EOF
Summary Statistics
==================

Worst-case trise: $(awk -F, '{print $4}' report/raw_data/extracted.csv | sort -n | tail -1)
Best-case trise:  $(awk -F, '{print $4}' report/raw_data/extracted.csv | sort -n | head -1)

Worst-case tfall: $(awk -F, '{print $5}' report/raw_data/extracted.csv | sort -n | tail -1)
Best-case tfall:  $(awk -F, '{print $5}' report/raw_data/extracted.csv | sort -n | head -1)

Max ipeak: $(awk -F, '{print $6}' report/raw_data/extracted.csv | sort -n | tail -1)
Min ipeak: $(awk -F, '{print $6}' report/raw_data/extracted.csv | sort -n | head -1)
EOF
}
```

---

## 7. Stage 5: Backup (bkp)

### Function: bkp_stage()

**Location**: sim_pvt.sh, Lines ~580-640

**Purpose**: Create timestamped archive of complete simulation run

### Execution Flow

```bash
bkp_stage() {
    echo "==================================="
    echo "STAGE 5: BACKUP CREATION (bkp)"
    echo "==================================="
    
    # Generate timestamp
    timestamp=$(date +%Y%m%d%H%M)
    
    # Create backup directory
    bkp_dir="00bkp_${timestamp}"
    mkdir -p $bkp_dir
    
    # Copy results
    copy_results $bkp_dir
    
    # Copy configuration
    copy_config $bkp_dir
    
    # Create archive manifest
    create_manifest $bkp_dir
    
    echo "Backup created: $bkp_dir"
}
```

### Backup Contents

```bash
copy_results() {
    local bkp_dir=$1
    
    # Copy report files
    cp -r report $bkp_dir/
    
    # Copy all .mt0 files (optional, large)
    # find . -name "sim_tx.mt0" -exec cp --parents {} $bkp_dir/ \;
    
    # Copy simulation logs (errors only)
    find . -name "sim_tx.log" | while read log; do
        if grep -q "ERROR\|FATAL" $log; then
            cp --parents $log $bkp_dir/
        fi
    done
}

copy_config() {
    local bkp_dir=$1
    
    # Copy configuration files
    cp config.cfg $bkp_dir/
    cp template/sim_tx.sp $bkp_dir/
    
    # Copy CSV tables
    cp configuration/table_*.csv $bkp_dir/
}
```

### Backup Manifest

```bash
create_manifest() {
    local bkp_dir=$1
    
    cat > $bkp_dir/MANIFEST.txt <<EOF
Backup Manifest
===============

Timestamp: $(date)
Mode: $mode
Voltage Domain: $vccn
Simulator: $simulator
CPU: $CPU
Memory: ${MEM}G

Stages Completed:
- Generation: Yes
- Simulation: Yes
- Extraction: Yes
- Sorting: Yes
- Backup: Yes

Total Simulations: $(wc -l < report/raw_data/extracted.csv)

Files Included:
$(find $bkp_dir -type f | sed 's|^|  - |')
EOF
}
```

### Backup Directory Structure

```
00bkp_202506161234/
├── MANIFEST.txt
├── config.cfg
├── sim_tx.sp
├── table_corner_list.csv
├── table_supply_list.csv
└── report/
    ├── creport.txt
    ├── summary.txt
    └── raw_data/
        └── extracted.csv
```

---

## 8. Stage 6: User Script (usr) - Optional

### Function: usr_stage()

**Location**: sim_pvt.sh, Lines ~660-680

**Purpose**: Run custom user-defined post-processing

### Execution Flow

```bash
usr_stage() {
    echo "==================================="
    echo "STAGE 6: USER SCRIPT (usr)"
    echo "==================================="
    
    # Check if user script exists
    if [ -f "user_script.sh" ]; then
        echo "Executing user_script.sh"
        bash user_script.sh
    else
        echo "No user script found (user_script.sh)"
    fi
}
```

**NOTE**: This stage is typically not used in standard workflow. User can create `user_script.sh` for custom analysis.

---

## 9. Main Execution Logic

### Stage Sequencing

**Location**: sim_pvt.sh, Lines 700-800

```bash
# Parse command-line arguments
config_file=$1
shift
stages=("$@")  # gen, run, ext, srt, bkp, usr

# Read configuration
read_cfg $config_file
read_supply
read_corner

# Execute requested stages
for stage in "${stages[@]}"; do
    case $stage in
        gen)
            gen_stage
            ;;
        run)
            run_stage
            ;;
        ext)
            ext_stage
            ;;
        srt)
            srt_stage
            ;;
        bkp)
            bkp_stage
            ;;
        usr)
            usr_stage
            ;;
        *)
            echo "Unknown stage: $stage"
            exit 1
            ;;
    esac
done

echo "========================================="
echo "ALL STAGES COMPLETED SUCCESSFULLY"
echo "========================================="
```

### Error Handling

```bash
# Enable strict error handling
set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Trap errors
trap 'handle_error $LINENO' ERR

handle_error() {
    local line=$1
    echo "ERROR at line $line"
    echo "Stage: $current_stage"
    echo "Check logs for details"
    exit 1
}
```

---

## 10. Verification Checklist for wkpup Comparison

When comparing wkpup automation against this wkpup2 baseline, verify:

### Entry Point
- [ ] wkpup has equivalent of `runme.sh`
- [ ] Environment setup is sourced correctly
- [ ] Configuration file is passed as argument
- [ ] Stages are specified in command line

### Stage Sequencing
- [ ] Stages execute in correct order: gen → run → ext → srt → bkp
- [ ] Each stage completes before next begins (unless parallel)
- [ ] Errors in one stage prevent subsequent stages

### Stage 1: Generation
- [ ] Uses identical PVT matrix (7 × 4 × 3 = 84 for pre-layout)
- [ ] Calls gen_tb.pl with correct arguments
- [ ] Creates correct directory structure
- [ ] Validates netlist count after generation

### Stage 2: Simulation
- [ ] Uses nbjob for cluster submission
- [ ] nbjob parameters match (target, qslot, class)
- [ ] CPU and memory allocation correct
- [ ] Waits for all jobs to complete
- [ ] Validates .mt0 file count

### Stage 3: Extraction
- [ ] Parses all .mt0 files
- [ ] Extracts correct measurements
- [ ] Creates raw data CSV
- [ ] Handles extraction errors gracefully

### Stage 4: Sorting
- [ ] Generates creport.txt
- [ ] Sorts by corner/temp/voltage
- [ ] Calculates summary statistics
- [ ] Format matches wkpup2 output

### Stage 5: Backup
- [ ] Creates timestamped directory (00bkp_YYYYMMDDHHMM)
- [ ] Copies report files
- [ ] Copies configuration files
- [ ] Creates manifest

### Error Handling
- [ ] Uses `set -e` for exit on error
- [ ] Has trap for error handling
- [ ] Provides meaningful error messages
- [ ] Cleans up on failure

---

## 11. Critical Success Criteria

For wkpup automation to be considered **equivalent** to wkpup2:

1. ✅ **Stage sequence must be identical**: gen → run → ext → srt → bkp
2. ✅ **runme.sh must call sim_pvt.sh** with correct arguments
3. ✅ **sim_pvt.sh must source identical libraries** (read_cfg, read_supply, read_corner, pvt_loop)
4. ✅ **PVT matrix generation must be identical** (same nested loops)
5. ✅ **nbjob submission must use same parameters** (target, qslot, class)
6. ✅ **Extraction must parse same measurements** from .mt0 files
7. ✅ **Report format must match** creport.txt structure
8. ✅ **Backup must create timestamped directory** with manifest
9. ✅ **Error handling must be robust** (set -e, traps)
10. ✅ **Validation checks must exist** at each stage

**ANY deviation from these criteria indicates a workflow inconsistency that may affect reliability.**

---

## 12. References

### Source Documents
- **COMPREHENSIVE_ANALYSIS.md**: Lines 153-450 (complete workflow)
- **TIER1_FRAMEWORK_ANALYSIS.md**: archive/source_documents/ (automation framework)
- **Actual Scripts**:
  - `runme.sh`
  - `dependencies/scripts/simulation_script/auto_pvt/ver03/sim_pvt.sh`
  - `dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/pvt_loop.sh`

### Related Analysis Documents
- **TESTBENCH_GENERATION_GAPS.md**: gen_tb.pl details
- **CORNER_MATRIX_GAPS.md**: PVT matrix structure
- **CONFIGURATION_GAPS.md**: config.cfg parsing

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: ✅ BASELINE REFERENCE COMPLETE  
**Next Step**: Compare wkpup automation workflow against this baseline  
**Critical Finding**: 6-stage deterministic pipeline is key to reproducibility
