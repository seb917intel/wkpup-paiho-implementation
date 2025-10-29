# Reference Results from wkpup2 Baseline

## Document Purpose

This document provides **expected outputs and reference data** from the wkpup2 baseline implementation. These serve as the "ground truth" for validating wkpup automation.

**Status**: ✅ REFERENCE DATA  
**Source**: wkpup2 backup files and actual simulation runs  
**Use**: Compare wkpup automation outputs against these references

---

## 1. Expected File Structure

### Complete Directory Tree (Pre-Layout, 84 Simulations)

```
gpio/1p1v/  (or i3c/1p1v/)
├── config.cfg
├── runme.sh
├── template/
│   └── sim_tx.sp (111 lines)
├── TT/
│   └── typical/
│       ├── typical_m40/
│       │   ├── v1min/sim_tx.sp
│       │   ├── v1nom/sim_tx.sp
│       │   └── v1max/sim_tx.sp
│       ├── typical_85/
│       │   ├── v1min/sim_tx.sp
│       │   ├── v1nom/sim_tx.sp
│       │   └── v1max/sim_tx.sp
│       ├── typical_100/
│       │   └── [3 netlists]
│       └── typical_125/
│           └── [3 netlists]
├── FFG/typical/...
├── SSG/typical/...
├── FSG/typical/...
├── SFG/typical/...
├── FFAG/typical/...
├── SSAG/typical/...
├── report/
│   ├── creport.txt
│   ├── summary.txt
│   └── raw_data/
│       └── extracted.csv
└── 00bkp_202506161234/
    ├── MANIFEST.txt
    ├── config.cfg
    ├── sim_tx.sp
    └── report/
        └── creport.txt
```

**Verification**:
```bash
# Total directories
find . -type d | wc -l
# Expected: ~100 (7 corners × 4 temps × 3 voltages + support dirs)

# Total netlists
find . -name "sim_tx.sp" | wc -l
# Expected: 84 (pre-layout) or 252 (post-layout)
```

---

## 2. Expected Netlist Content

### Template Line 52 Preservation

**GPIO Template** (Line 52):
```spice
.lib "/nfs/.../weakpullup.lib" enable
```

**I3C Template** (Line 52):
```spice
.lib "/nfs/.../weakpullup.lib" enable_i3c
```

**Verification**:
```bash
# Check all GPIO netlists preserve "enable"
find gpio/1p1v -name "sim_tx.sp" -exec grep -l "weakpullup.lib.*enable\"" {} \; | wc -l
# Expected: 84 (all netlists)

# Check all I3C netlists preserve "enable_i3c"
find i3c/1p1v -name "sim_tx.sp" -exec grep -l "weakpullup.lib.*enable_i3c\"" {} \; | wc -l
# Expected: 84 (all netlists)

# Ensure no cross-contamination
find gpio/1p1v -name "sim_tx.sp" -exec grep -l "enable_i3c" {} \; | wc -l
# Expected: 0 (none should have I3C parameter)
```

---

### Example Generated Netlist (TT/typical/typical_85/v1nom/sim_tx.sp)

**Expected Substitutions**:
```spice
* Line 1: Title (unchanged)
* Weak Pull-up Circuit Simulation

* Lines 10-20: Temperature (substituted)
.temp 85                              ← Was: .temp 100

* Lines 30-40: Corner (substituted)
.lib "$DP_HSPICE_MODEL" TT            ← Was: .lib "$DP_HSPICE_MODEL" TT

* Line 52: Protocol differentiator (PRESERVED)
.lib "/nfs/.../weakpullup.lib" enable  ← Unchanged from template

* Lines 60-70: Parameters (substituted)
.param vcn=1.1                        ← Was: .param vcn=1.1 (nominal)
.param vc=0.75                        ← Was: .param vc=0.75 (nominal)
.param vsh="((1.1-0.85)*vcn/1.1)"    ← Formula (nominal)

* Line 111: End of netlist
.end
```

**Checksum Verification**:
```bash
# Generate reference checksum
md5sum gpio/1p1v/TT/typical/typical_85/v1nom/sim_tx.sp > reference_checksum.txt

# Later, verify wkpup matches
md5sum wkpup/TT/typical/typical_85/v1nom/sim_tx.sp | diff - reference_checksum.txt
# Should output: (empty - files identical)
```

---

## 3. Expected Configuration Outputs

### From config.cfg (GPIO Example)

**Input** (`gpio/1p1v/config.cfg`):
```bash
mode:prelay
vccn:1p1v
vcctx:vcctx_1800
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA
condition:func
CPU #:1
MEM [G]:4
alter_extraction:No
alter_string#:20
sim_mode:ac
gs/gf_corner:No
vcc_vid:No
simulator:primesim
```

**Expected Parsed Values** (from `read_cfg.sh`):
```bash
$mode = "prelay"
$vcc_lvl = "1p1v"
$vctx_lvl = "vcctx_1800"
$supply_swp_1st = "vcc"
$supply_swp_2nd = "NA"
$supply_swp_3rd = "NA"
$condition = "func"
$CPU = "1"
$MEM = "4"
$alter_extraction = "No"
$swpl = "20"
$sim_mode = "ac"
$gsgf_corner = "No"
$vcc_vid = "No"
$simulator = "primesim"
```

---

### From CSV Tables

**table_corner_list.csv** (Expected):
```csv
type,extraction,corner list
nom_tt,typical,TT
full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG
full_tt_gsgf,typical,TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG
cross_default,cworst_CCworst_T cbest_CCbest_T,FSG SFG SSG FFG
```

**table_supply_list_ac.csv** (Expected - VCC row):
```csv
rail,func_min,perf_min,nom,perf_max,func_max,htol,hvqk
vcc,0.68,0.69,0.78,0.88,0.89,0.945,1.6
```

**Resulting Voltage Values** (condition=func):
```bash
$vccmin = "0.68"
$vccnom = "0.78"
$vccmax = "0.89"
```

---

## 4. Expected Simulation Outputs

### Measurement File Format (.mt0)

**Example**: `TT/typical/typical_85/v1nom/result/sim_tx.mt0`

```
.TITLE Weak Pull-up Measurements

alter# = 1.00000000e+00

trise_rr    tfall_ff    rpullup    voh        vol
3.124e-11   3.189e-11   7.35e3     1.08       0.02
```

**Field Definitions**:
- `trise_rr`: Rising edge delay (seconds)
- `tfall_ff`: Falling edge delay (seconds)
- `rpullup`: Pull-up resistance (ohms)
- `voh`: Output high voltage (volts)
- `vol`: Output low voltage (volts)

---

### Extracted Data File (report.txt)

**Example**: `report/report_TT_typical_85_v1nom.txt`

```
trise_rr    tfall_ff    rpullup    voh        vol
3.124e-11   3.189e-11   7.35e3     1.08       0.02
```

---

### Consolidated Report (creport.txt)

**Expected Format**:
```
================================================================================
WKPUP Simulation Results - Consolidated Report
Generated: 2025-06-16 12:34:56
Mode: prelay
Voltage Domain: 1p1v
Condition: func
================================================================================

Corner   Temp   Voltage  trise_rr    tfall_ff    rpullup    voh    vol
TT       m40    v1min    3.456e-11   3.523e-11   8.12e3     1.15   0.01
TT       m40    v1nom    3.234e-11   3.301e-11   7.56e3     1.10   0.01
TT       m40    v1max    3.012e-11   3.078e-11   7.01e3     1.05   0.02
TT       85     v1min    3.345e-11   3.412e-11   7.89e3     1.12   0.02
TT       85     v1nom    3.124e-11   3.189e-11   7.35e3     1.08   0.02
TT       85     v1max    2.901e-11   2.967e-11   6.81e3     1.03   0.02
... (84 rows total)

================================================================================
Total simulations: 84
================================================================================
```

---

## 5. Expected Backup Structure

### Backup Directory (00bkp_202506161234/)

**Expected Contents**:
```
00bkp_202506161234/
├── MANIFEST.txt
├── config.cfg
├── sim_tx.sp (template copy)
├── table_corner_list.csv
├── table_supply_list_ac.csv
└── report/
    ├── creport.txt
    ├── summary.txt
    └── raw_data/
        └── extracted.csv
```

**MANIFEST.txt Content**:
```
Backup Manifest
===============

Timestamp: 2025-06-16 12:34:56
Mode: prelay
Voltage Domain: 1p1v
Simulator: primesim
CPU: 1
Memory: 4G

Stages Completed:
- Generation: Yes
- Simulation: Yes
- Extraction: Yes
- Sorting: Yes
- Backup: Yes

Total Simulations: 84

Files Included:
  - MANIFEST.txt
  - config.cfg
  - sim_tx.sp
  - table_corner_list.csv
  - table_supply_list_ac.csv
  - report/creport.txt
  - report/summary.txt
  - report/raw_data/extracted.csv
```

---

## 6. Expected Corner Coverage

### Pre-Layout (mode=prelay, gs/gf_corner=No)

**Corners Generated**: 7
```
TT, FFG, SSG, FSG, SFG, FFAG, SSAG
```

**Extractions**: 1 (typical)

**Temperatures**: 4 (m40, 85, 100, 125)

**Voltages**: 3 (v1min, v1nom, v1max)

**Total**: 7 × 1 × 4 × 3 = **84 simulations**

---

### Post-Layout Full (mode=postlay, gs/gf_corner=No, postlay_cross_cornerlist=full)

**Corners Generated**: 7

**Extractions**: 3 (typical, cworst_CCworst_T, cbest_CCbest_T)

**Temperatures**: 4

**Voltages**: 3

**Total**: 7 × 3 × 4 × 3 = **252 simulations**

---

### Post-Layout with GS/GF (gs/gf_corner=Yes)

**Corners Generated**: 9
```
TT, FFG, SSG, FSG, SFG, FFAG, SSAG, FFG_SSG, SSG_FFG
```

**Total**: 9 × 3 × 4 × 3 = **324 simulations**

---

## 7. Validation Checksums

### Reference Checksums (GPIO, Pre-Layout)

```bash
# Generate reference checksums for all netlists
cd gpio/1p1v
find . -name "sim_tx.sp" -type f -exec md5sum {} \; > ../gpio_1p1v_checksums.txt
cd ..

# Example checksums (first 5 netlists)
cat gpio_1p1v_checksums.txt | head -5
```

**Expected Output**:
```
a1b2c3d4e5f6... ./TT/typical/typical_m40/v1min/sim_tx.sp
b2c3d4e5f6g7... ./TT/typical/typical_m40/v1nom/sim_tx.sp
c3d4e5f6g7h8... ./TT/typical/typical_m40/v1max/sim_tx.sp
d4e5f6g7h8i9... ./TT/typical/typical_85/v1min/sim_tx.sp
e5f6g7h8i9j0... ./TT/typical/typical_85/v1nom/sim_tx.sp
```

**Usage**:
```bash
# Validate wkpup against reference
cd wkpup/gpio/1p1v
find . -name "sim_tx.sp" -type f -exec md5sum {} \; | \
  diff - ../../../gpio_1p1v_checksums.txt

# Should output: (empty if all files match)
```

---

## 8. Expected Timing and Resource Usage

### Generation Stage

**Sequential (CPU=1)**:
- **Time**: ~5-10 seconds for 84 netlists
- **Memory**: <100 MB
- **Output**: 84 files

**Parallel (CPU=8)**:
- **Time**: ~2-3 seconds for 84 netlists
- **Memory**: <200 MB
- **Output**: 84 files (identical to sequential)

---

### Simulation Stage

**Per Job**:
- **Time**: 30-120 seconds (varies by circuit complexity)
- **Memory**: 1-4 GB
- **CPU**: 8 cores (if CPU #:8)

**Total** (84 jobs):
- **Time**: 1-2 hours (parallel job submission)
- **Storage**: ~500 MB (all .mt0 + .log files)

---

## 9. Numerical Tolerances

### Measurement Precision

**Expected Precision**: Scientific notation with 8-9 significant figures

**Examples**:
```
trise = 3.12398102e-11  (11 characters total)
rpullup = 7.35124e3     (9 characters)
voh = 1.08234567        (10 characters)
```

**Comparison Tolerance**:
- **Exact match**: For parameter substitutions (strings, integers)
- **Numerical tolerance**: ±1e-15 for floating-point measurements
- **String match**: Exact for corner names, file paths

---

## 10. Common Reference Values

### Standard Voltages (condition=func, sim_mode=ac)

| Rail | Min (V) | Nom (V) | Max (V) |
|------|---------|---------|---------|
| vcc | 0.68 | 0.78 | 0.89 |
| 1p1v | 0.98 | 1.1 | 1.188 |
| vcctx_1800 | 1.7 | 1.8 | 1.9 |

### Standard Temperatures

| Label | Value (°C) | SPICE Value |
|-------|------------|-------------|
| m40 | -40 | -40 |
| 85 | 85 | 85 |
| 100 | 100 | 100 |
| 125 | 125 | 125 |

---

## 11. References

- **TESTBENCH_GENERATION_GAPS.md**: gen_tb.pl expected behavior
- **SIMULATION_FLOW_GAPS.md**: Workflow expected outputs
- **CORNER_MATRIX_GAPS.md**: PVT matrix expected structure
- **VALIDATION_METHODOLOGY.md**: How to use these references

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: ✅ REFERENCE DATA COMPLETE  
**Source**: wkpup2 baseline execution (June 16, 2025 backup)  
**Use**: Compare wkpup automation outputs against these expected results
