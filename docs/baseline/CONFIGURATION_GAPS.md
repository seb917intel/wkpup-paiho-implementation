# Configuration System Analysis: wkpup2 Baseline Reference

## Document Purpose

This document provides the **authoritative baseline** for the configuration system in Pai Ho's wkpup2 implementation. It documents all 15 configuration parameters, CSV table structures, and parsing logic that control simulation behavior.

**Status**: ✅ BASELINE REFERENCE (wkpup2)  
**Source**: COMPREHENSIVE_ANALYSIS.md and wkpup2 configuration files  
**Key File**: `config.cfg`, `read_cfg.sh`, `read_supply.sh`, `read_corner.sh`

---

## Executive Summary

### Configuration System Architecture

The wkpup2 configuration system uses:
1. **config.cfg** - Main configuration file (15 parameters)
2. **read_cfg.sh** - Configuration parser (exports 15 shell variables)
3. **read_supply.sh** - Voltage table reader (parses CSV files)
4. **read_corner.sh** - Corner list reader (parses CSV files)

**All configuration is declarative** - changing config.cfg automatically adjusts:
- PVT matrix dimensions
- Voltage values
- Corner selections
- Simulation mode
- Resource allocation

---

## 1. config.cfg Structure

### Complete Parameter List (15 Parameters)

**File Format**: `parameter:value` (colon-separated)

```bash
mode:prelay                          # Parameter 1:  Simulation mode
vccn:1p1v                           # Parameter 2:  Voltage domain
vcctx:vcctx_1800                    # Parameter 3:  TX voltage rail
1st_supply_swp:vcc                  # Parameter 4:  First supply sweep
2nd_supply_swp:NA                   # Parameter 5:  Second supply sweep
3rd_supply_swp:NA                   # Parameter 6:  Third supply sweep
condition:func                       # Parameter 7:  Operating condition
CPU #:1                             # Parameter 8:  CPU count
MEM [G]:4                           # Parameter 9:  Memory allocation (GB)
alter_extraction:No                  # Parameter 10: Multi-sweep extraction
alter_string#:20                     # Parameter 11: Sweep string length
sim_mode:ac                          # Parameter 12: AC/DC simulation
gs/gf_corner:No                      # Parameter 13: GS/GF corner support
vcc_vid:No                           # Parameter 14: Voltage ID support
simulator:primesim                   # Parameter 15: Simulator choice
postlay_cross_cornerlist:default     # Parameter 16: Post-layout corners (optional)
```

### Parameter Definitions

#### Parameter 1: mode
**Purpose**: Determines simulation mode (pre-layout vs post-layout)

**Valid Values**:
- `prelay` - Pre-layout simulation (no parasitic extraction)
- `postlay` - Post-layout simulation (with parasitic extraction)

**Impact**:
- **prelay**: Uses 1 extraction corner (typical only), 84 simulations
- **postlay**: Uses 3 extraction corners (typical + cworst + cbest), 252 simulations

**Example**:
```bash
mode:prelay   # → 84 netlists
mode:postlay  # → 252 netlists
```

---

#### Parameter 2: vccn
**Purpose**: Specifies voltage domain/rail name

**Valid Values**: Any rail name from `table_supply_list.csv`
- `1p1v` - 1.1V domain
- `1p2v` - 1.2V domain
- `1p8v` - 1.8V domain
- `vcc` - Core voltage

**Impact**:
- Selects row from voltage table
- Determines min/nom/max voltage values

**Example**:
```bash
vccn:1p1v
# Reads row: 1p1v,0.98,0.99,1.1,1.188,1.2,1.246,1.65
# Sets: vcnmin=0.98, vcnnom=1.1, vcnmax=1.188 (for func condition)
```

---

#### Parameter 3: vcctx
**Purpose**: Specifies TX (transmit) voltage rail

**Valid Values**: TX rail names from `table_supply_list.csv`
- `vcctx_600` - 0.6V TX
- `vcctx_800` - 0.8V TX
- `vcctx_1200` - 1.2V TX
- `vcctx_1500` - 1.5V TX
- `vcctx_1800` - 1.8V TX

**Impact**:
- Sets VCCTX voltage values
- Used in .param vctx= substitution

**Example**:
```bash
vcctx:vcctx_1800
# Reads: vcctx_1800,1.7,1.73,1.8,1.87,1.9,1.87,2.475
# Sets: vctxmin=1.7, vctxnom=1.8, vctxmax=1.9 (for func condition)
```

---

#### Parameters 4-6: Supply Sweep Configuration

**Purpose**: Defines which supply rails to sweep

**Valid Values**:
- `vcc` - Core voltage
- `vccn` - VCCN voltage
- `vccana` - Analog voltage
- `vcctx` - TX voltage
- `NA` - Not applicable (no sweep)

**Impact**:
- **1 supply** (2nd=NA, 3rd=NA): 3 voltage combinations (v1min, v1nom, v1max)
- **2 supplies** (3rd=NA): 9 voltage combinations (v1*_v2*)
- **3 supplies**: 27 voltage combinations (v1*_v2*_v3*)

**Example**:
```bash
# Single supply
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA
# Result: v1min, v1nom, v1max (3 combos)

# Two supplies
1st_supply_swp:vcc
2nd_supply_swp:vcctx
3rd_supply_swp:NA
# Result: v1min_v2min, v1min_v2nom, ... v1max_v2max (9 combos)
```

---

#### Parameter 7: condition
**Purpose**: Selects operating condition (affects voltage selection)

**Valid Values**:
- `func` - Functional condition
- `perf` - Performance condition
- `htol` - High-temperature operating life
- `hvqk` - High-voltage qualification

**Impact**: Determines which columns from voltage table are used

**Voltage Selection Logic**:
```
func: min=func_min, nom=nom, max=func_max
perf: min=perf_min, nom=nom, max=perf_max
htol: min=func_min, nom=nom, max=htol
hvqk: min=func_min, nom=nom, max=hvqk
```

**Example**:
```bash
condition:func
# For vcc row: 0.68, 0.69, 0.78, 0.88, 0.89
# Uses: vccmin=0.68, vccnom=0.78, vccmax=0.89

condition:perf
# Uses: vccmin=0.69, vccnom=0.78, vccmax=0.88
```

---

#### Parameter 8: CPU #
**Purpose**: Number of CPUs for parallel job execution

**Valid Values**: 1-32 (integer)

**Impact**:
- **CPU=1**: Sequential generation (gen_pvt_loop_seq)
- **CPU>1**: Parallel generation (gen_pvt_loop_par)
- Passed to nbjob as `--class "SLES15&&${MEM}G&&${CPU}C"`

**Example**:
```bash
CPU #:8
# Result: Uses 8 CPUs per simulation job
# nbjob: --class "SLES15&&4G&&8C"
```

---

#### Parameter 9: MEM [G]
**Purpose**: Memory allocation per job (in gigabytes)

**Valid Values**: 1-64 (integer)

**Impact**:
- Passed to nbjob as resource requirement
- Ensures job has sufficient memory

**Example**:
```bash
MEM [G]:4
# Result: Request 4GB memory per job
# nbjob: --class "SLES15&&4G&&8C"
```

---

#### Parameter 10: alter_extraction
**Purpose**: Enable multi-sweep extraction

**Valid Values**:
- `Yes` - Use extract_alt.sh (supports .alter sweeps)
- `No` - Use extract.sh (single-point only)

**Impact**:
- Determines which extraction script is called
- extract_alt.sh handles multiple sweep points
- extract.sh is simpler/faster for single-point

**Example**:
```bash
alter_extraction:Yes
# Uses: extract_alt.sh $testbench $swpl $simulator
```

---

#### Parameter 11: alter_string#
**Purpose**: String length for sweep parameter extraction

**Valid Values**: 1-50 (integer, typically 20)

**Impact**:
- Controls truncation of sweep parameter value
- Used in extract_alt.sh: `var1=${var1:0:$swpl}`

**Example**:
```bash
alter_string#:20
# Truncates sweep value to first 20 characters
```

---

#### Parameter 12: sim_mode
**Purpose**: Simulation type (AC or DC analysis)

**Valid Values**:
- `ac` - AC analysis (uses table_supply_list_ac.csv)
- `dc` - DC analysis (uses table_supply_list_dc.csv)
- (blank) - Default (uses table_supply_list.csv)

**Impact**:
- Selects voltage table file
- Different voltage values for AC vs DC

**Example**:
```bash
sim_mode:ac
# Uses: configuration/table_supply_list_ac.csv
```

---

#### Parameter 13: gs/gf_corner
**Purpose**: Enable GS/GF (global/spatial variation) corners

**Valid Values**:
- `Yes` - Include FFG_SSG and SSG_FFG corners (9 total)
- `No` - Standard 7 corners only

**Impact**:
- Affects corner count: 7 → 9
- Changes total simulations: 84 → 108 (pre-layout)

**Example**:
```bash
gs/gf_corner:Yes
# Corner list: TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG
```

---

#### Parameter 14: vcc_vid
**Purpose**: Enable Voltage ID (VID) support

**Valid Values**:
- `Yes` - Use corner/temperature-specific voltages (18 values)
- `No` - Use standard min/nom/max voltages (3 values)

**Impact**:
- When enabled, VCC voltage varies by corner and temperature
- Provides more accurate voltage modeling

**Example**:
```bash
vcc_vid:Yes
# FFG corner, 125°C, max → uses vccmax_ff_h instead of vccmax
```

---

#### Parameter 15: simulator
**Purpose**: Select SPICE simulator

**Valid Values**:
- `primesim` - Synopsys PrimeSim
- `finesim` - Synopsys FineSim

**Impact**:
- Changes simulation command
- Affects measurement file naming (_a0 vs #0)

**Example**:
```bash
simulator:primesim
# Command: primesim -np 8 -spice sim_tx.sp -o sim_tx
```

---

#### Parameter 16: postlay_cross_cornerlist (Optional)
**Purpose**: Select post-layout cross-extraction corner set

**Valid Values**:
- `default` - Reduced corner set (4 corners: FSG SFG SSG FFG)
- `full` - Full corner set (7 or 9 corners)
- `custom` - Custom corner list (specified in column 3)

**Impact**:
- Only affects post-layout cross-extraction
- Does not affect typical extraction

**Example**:
```bash
postlay_cross_cornerlist:default
# Cross extraction uses: FSG SFG SSG FFG (4 corners)
# Typical extraction still uses all 7/9 corners
```

---

## 2. read_cfg.sh - Configuration Parser

### Script Location
```
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/read_cfg.sh
```

### Parsing Logic

```bash
read_cfg() {
    config_file=$1
    
    while IFS=':' read -r col1 col2 col3
    do
        # Remove leading/trailing whitespace
        col1=$(echo $col1 | xargs)
        col2=$(echo $col2 | xargs)
        col3=$(echo $col3 | xargs)
        
        # Parse each parameter
        if [ "$col1" == "mode" ]; then
            mode=$col2
        elif [ "$col1" == "vccn" ]; then
            vcc_lvl=$col2
        elif [ "$col1" == "vcctx" ]; then
            vctx_lvl=$col2
        elif [ "$col1" == "1st_supply_swp" ]; then
            supply_swp_1st=$col2
        elif [ "$col1" == "2nd_supply_swp" ]; then
            supply_swp_2nd=$col2
        elif [ "$col1" == "3rd_supply_swp" ]; then
            supply_swp_3rd=$col2
        elif [ "$col1" == "condition" ]; then
            condition=$col2
        elif [ "$col1" == "CPU #" ]; then
            CPU=$col2
        elif [ "$col1" == "MEM [G]" ]; then
            MEM=$col2
        elif [ "$col1" == "alter_extraction" ]; then
            alter_extraction=$col2
        elif [ "$col1" == "alter_string#" ]; then
            swpl=$col2
        elif [ "$col1" == "sim_mode" ]; then
            sim_mode=$col2
        elif [ "$col1" == "gs/gf_corner" ]; then
            gsgf_corner=$col2
        elif [ "$col1" == "vcc_vid" ]; then
            vcc_vid=$col2
        elif [ "$col1" == "simulator" ]; then
            simulator=$col2
        elif [ "$col1" == "postlay_cross_cornerlist" ]; then
            postlay_cross_cornerlist=$col2
            custom_corner=$col3  # Optional third column
        fi
    done < "$config_file"
    
    # Export variables for use by other scripts
    export mode vcc_lvl vctx_lvl supply_swp_1st supply_swp_2nd supply_swp_3rd
    export condition CPU MEM alter_extraction swpl sim_mode
    export gsgf_corner vcc_vid simulator postlay_cross_cornerlist custom_corner
}
```

### Variables Exported

After `read_cfg config.cfg`, these shell variables are available:

```bash
$mode                        # prelay or postlay
$vcc_lvl                     # Voltage domain name
$vctx_lvl                    # TX voltage rail name
$supply_swp_1st              # First supply name
$supply_swp_2nd              # Second supply name
$supply_swp_3rd              # Third supply name
$condition                   # func, perf, htol, hvqk
$CPU                         # CPU count
$MEM                         # Memory in GB
$alter_extraction            # Yes or No
$swpl                        # String length for sweep
$sim_mode                    # ac, dc, or blank
$gsgf_corner                 # Yes or No
$vcc_vid                     # Yes or No
$simulator                   # primesim or finesim
$postlay_cross_cornerlist    # default, full, or custom
$custom_corner               # Custom corner list (if applicable)
```

---

## 3. Validation Tests

### Test 1: Parse All 15 Parameters

**Input (config.cfg)**:
```bash
mode:prelay
vccn:1p1v
vcctx:vcctx_1800
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA
condition:func
CPU #:8
MEM [G]:4
alter_extraction:No
alter_string#:20
sim_mode:ac
gs/gf_corner:No
vcc_vid:No
simulator:primesim
```

**Verification**:
```bash
source read_cfg.sh
read_cfg config.cfg

echo $mode              # Should be: prelay
echo $vcc_lvl           # Should be: 1p1v
echo $CPU               # Should be: 8
echo $simulator         # Should be: primesim
```

---

### Test 2: Validate Default Values

**Missing Parameters**: If a parameter is not in config.cfg, what happens?

**Expected Behavior**:
- Variables should remain unset (empty string)
- Downstream logic should handle defaults

**Verification**:
```bash
# Config without postlay_cross_cornerlist
if [ -z "$postlay_cross_cornerlist" ]; then
    postlay_cross_cornerlist="default"  # Set default
fi
```

---

### Test 3: Column 3 Support (Custom Corners)

**Input**:
```bash
postlay_cross_cornerlist:custom:FSG SFG SSG
```

**Expected**:
```bash
$postlay_cross_cornerlist = "custom"
$custom_corner = "FSG SFG SSG"
```

---

## 4. Critical Success Criteria

For wkpup automation to be considered **equivalent** to wkpup2:

1. ✅ **config.cfg format must be identical** (colon-separated)
2. ✅ **All 15 parameters must be supported**
3. ✅ **read_cfg.sh parsing logic must be identical**
4. ✅ **Variable names must match exactly** (case-sensitive)
5. ✅ **Default value handling must be consistent**
6. ✅ **Column 3 support must work** (for custom corners)
7. ✅ **Exported variables must be available globally**
8. ✅ **Configuration must affect all downstream stages**

**ANY missing or incorrectly parsed parameter will cause simulation failures.**

---

## 5. References

### Source Documents
- **COMPREHENSIVE_ANALYSIS.md**: Lines 2950-3070 (config.cfg analysis)
- **Actual Files**:
  - `gpio/1p1v/config.cfg`
  - `dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/read_cfg.sh`

### Related Analysis Documents
- **CORNER_MATRIX_GAPS.md**: How config affects PVT matrix
- **TESTBENCH_GENERATION_GAPS.md**: How config values reach gen_tb.pl
- **SIMULATION_FLOW_GAPS.md**: Configuration flow through workflow

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: ✅ BASELINE REFERENCE COMPLETE  
**Next Step**: Compare wkpup automation configuration system against this baseline  
**Critical Finding**: 15-parameter configuration controls all simulation behavior
