# PVT Corner Matrix Analysis: wkpup2 Baseline Reference

## Document Purpose

This document provides the **authoritative baseline** for Process-Voltage-Temperature (PVT) corner matrix generation in Pai Ho's wkpup2 implementation. It serves as the reference for identifying matrix coverage gaps and inconsistencies when comparing against the wkpup automation system.

**Status**: ✅ BASELINE REFERENCE (wkpup2)  
**Source**: COMPREHENSIVE_ANALYSIS.md and actual wkpup2 configuration files  
**Key Files**: `table_corner_list.csv`, `table_supply_list.csv`, `pvt_loop.sh`

---

## Executive Summary

### PVT Matrix Dimensions

**wkpup2 generates a comprehensive PVT matrix with these dimensions**:

```
Process Corners (P): 7-9 corners (depending on configuration)
Voltage Levels (V):  3 levels per supply rail (min, nom, max)
Temperature Points (T): 4 temperatures (-40°C, 85°C, 100°C, 125°C)
Extraction Corners (E): 1-3 (typical only for pre-layout, +cworst/cbest for post-layout)
```

**Total Simulations**:
- **Pre-layout** (mode=prelay): 7 corners × 1 extraction × 4 temps × 3 voltages = **84 netlists**
- **Post-layout** (mode=postlay): 7 corners × 3 extractions × 4 temps × 3 voltages = **252 netlists**
- **Post-layout with GS/GF**: 9 corners × 3 extractions × 4 temps × 3 voltages = **324 netlists**

---

## 1. Process Corners (P Dimension)

### Silicon Corner Definitions

**Source**: `table_corner_list.csv`

#### Standard 7-Corner Set

```
TT    - Typical NMOS, Typical PMOS (nominal)
FFG   - Fast NMOS, Fast PMOS, Fast Global
SSG   - Slow NMOS, Slow PMOS, Slow Global
FSG   - Fast NMOS, Slow PMOS, Slow Global
SFG   - Slow NMOS, Fast PMOS, Fast Global
FFAG  - Fast NMOS, Fast PMOS, Fast Global (alternative)
SSAG  - Slow NMOS, Slow PMOS, Slow Global (alternative)
```

#### Extended 9-Corner Set (with GS/GF Support)

When `gs_corner=Yes` or `gf_corner=Yes` in `config.cfg`:

```
TT       - Typical NMOS, Typical PMOS, Typical Global
FFG      - Fast NMOS, Fast PMOS, Fast Global
SSG      - Slow NMOS, Slow PMOS, Slow Global
FSG      - Fast NMOS, Slow PMOS, Slow Global
SFG      - Slow NMOS, Fast PMOS, Fast Global
FFAG     - Fast NMOS, Fast PMOS, Fast Global (alternative)
SSAG     - Slow NMOS, Slow PMOS, Slow Global (alternative)
FFG_SSG  - Fast Si, Slow Global (spatial variation)
SSG_FFG  - Slow Si, Fast Global (spatial variation)
```

### Corner Selection Logic

**Configuration Parameter**: `gs_corner` and `gf_corner` in `config.cfg`

```bash
# config.cfg
gs_corner:Yes        # Include GS corners (FFG_SSG, SSG_FFG)
gf_corner:No         # Exclude GF corners
```

**read_corner.sh Logic**:
```bash
if [ "$gsgf_corner" == "No" ]; then
    typ_ex_cornerlist="TT FSG SFG FFG FFAG SSG SSAG"           # 7 corners
else
    typ_ex_cornerlist="TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG"  # 9 corners
fi
```

### table_corner_list.csv Structure

**File Location**: `dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/table_corner_list.csv`

**Complete Content**:
```csv
type,extraction,corner list
nom_tt,typical,TT
full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG
full_tt_gsgf,typical,TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG
cross_default,cworst_CCworst_T cbest_CCbest_T,FSG SFG SSG FFG
cross_default_gsgf,cworst_CCworst_T cbest_CCbest_T,FSG SFG SSG FFG FFG_SSG SSG_FFG
cross_full,cworst_CCworst_T cbest_CCbest_T,TT FSG SFG FFG FFAG SSG SSAG
cross_full_gsgf,cworst_CCworst_T cbest_CCbest_T,TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG
```

**Row Type Definitions**:
- `nom_tt`: Nominal corner only (TT)
- `full_tt`: All 7 standard corners
- `full_tt_gsgf`: All 9 corners (with GS/GF)
- `cross_default`: Reduced corner set for post-layout cross-extraction (4 corners)
- `cross_default_gsgf`: Reduced corner set with GS/GF (6 corners)
- `cross_full`: Full corner set for post-layout cross-extraction (7 corners)
- `cross_full_gsgf`: Full corner set with GS/GF (9 corners)

### Corner Usage by Mode

**Pre-Layout (mode=prelay)**:
- Uses `typ_ex_cornerlist` (7 or 9 corners)
- Extraction: `typical` only
- Total: 7 corners × 1 extraction = 7 corner groups

**Post-Layout (mode=postlay)**:
- Typical extraction: Uses `typ_ex_cornerlist` (7 or 9 corners)
- Cross extraction: Uses `cross_ex_cornerlist` (4, 6, 7, or 9 corners based on `postlay_cross_cornerlist`)

**Example Configuration**:
```bash
# config.cfg
mode:postlay
gs_corner:Yes
postlay_cross_cornerlist:default

# Result:
typ_ex_cornerlist = "TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG"  # 9 corners
cross_ex_cornerlist = "FSG SFG SSG FFG FFG_SSG SSG_FFG"              # 6 corners
```

---

## 2. Extraction Corners (E Dimension)

### Extraction Corner Definitions

**Extraction corners represent parasitic RC extraction variations**:

```
typical          - Nominal extraction (capacitance and resistance)
cworst_CCworst_T - Worst-case capacitance, worst-case temperature
cbest_CCbest_T   - Best-case capacitance, best-case temperature
```

### Extraction Corner Usage

**Pre-Layout Simulations** (mode=prelay):
- **Extraction**: `typical` only
- **Reason**: No parasitic extraction files exist pre-layout
- **Template References**: No `.spf` files

**Post-Layout Simulations** (mode=postlay):
- **Extraction**: `typical`, `cworst_CCworst_T`, `cbest_CCbest_T`
- **Reason**: Parasitic extraction creates multiple corner files
- **Template References**: 
  - `.inc "layout_tparam_typical.spf"`
  - `.inc "layout_tparam_cworst_CCworst_T.spf"`
  - `.inc "layout_tparam_cbest_CCbest_T.spf"`

### gen_tb.pl Pattern Matching (Rule 3)

```perl
elsif ($line =~ m/(.+)\_tparam_typical.spf(.+)/)
{
    print "$1\_tparam_$ex_corner.spf\"\n";
}
```

**Transforms**:
- Template: `.inc "layout_tparam_typical.spf"`
- Output (typical): `.inc "layout_tparam_typical.spf"`
- Output (cworst): `.inc "layout_tparam_cworst_CCworst_T.spf"`
- Output (cbest): `.inc "layout_tparam_cbest_CCbest_T.spf"`

---

## 3. Temperature Points (T Dimension)

### Temperature Definitions

**Standard Temperature Points**:

```
m40  - -40°C (Cold extreme)
85   -  85°C (Typical operation)
100  - 100°C (Warm operation)
125  - 125°C (Hot extreme)
```

### Temperature String to Number Conversion

**gen_tb.pl Logic** (Lines 66-71):
```perl
if ($temperature eq "m40") { $temp_num = "-40"; }
elsif ($temperature eq "85") { $temp_num = "85"; }
elsif ($temperature eq "100") { $temp_num = "100"; }
elsif ($temperature eq "125") { $temp_num = "125"; }
```

### Temperature Application in Netlist

**Template**:
```spice
.temp 100
```

**Generated Output**:
```spice
.temp -40   # For m40 corner
.temp 85    # For 85 corner
.temp 100   # For 100 corner
.temp 125   # For 125 corner
```

### VID Temperature Categories

**For Voltage ID (VID) support**, temperatures are categorized:

```
Cold (c): m40 (-40°C)
Hot (h):  125 (125°C)
Typical:  85, 100 (uses standard voltage)
```

**VID Corner Mapping** (gen_tb.pl Lines 47-63):
```perl
if ($si_corner eq "TT" || $si_corner eq "FSG" || $si_corner eq "SFG") {
    $vcc_vid_corner = "tt";
}
elsif ($si_corner eq "FFG" || $si_corner eq "FFG_SSG" || $si_corner eq "FFAG") {
    $vcc_vid_corner = "ff";
}
elsif ($si_corner eq "SSG" || $si_corner eq "SSG_FFG" || $si_corner eq "SSAG") {
    $vcc_vid_corner = "ss";
}
```

**VID Voltage Selection Example**:
- Corner: FFG (maps to `ff`)
- Temperature: 125 (maps to `hot`)
- Trend: max
- Result: Uses `$vccmax_ff_h` from VID table

---

## 4. Voltage Levels (V Dimension)

### Voltage Trend Definitions

**For each supply rail, three voltage levels are simulated**:

```
min - Minimum voltage (worst case low)
nom - Nominal voltage (typical)
max - Maximum voltage (worst case high)
```

### Supply Rail Configuration

**Single Supply Example** (vcc only):
```
v1min - VCC at minimum
v1nom - VCC at nominal
v1max - VCC at maximum
```

**Two Supply Example** (vcc + vcctx):
```
v1min_v2min - VCC min, VCCTX min
v1min_v2nom - VCC min, VCCTX nom
v1min_v2max - VCC min, VCCTX max
v1nom_v2min - VCC nom, VCCTX min
v1nom_v2nom - VCC nom, VCCTX nom
v1nom_v2max - VCC nom, VCCTX max
v1max_v2min - VCC max, VCCTX min
v1max_v2nom - VCC max, VCCTX nom
v1max_v2max - VCC max, VCCTX max
```
**Total**: 3 × 3 = 9 voltage combinations

**Three Supply Example** (vcc + vcctx + vccn):
```
v1min_v2min_v3min through v1max_v2max_v3max
```
**Total**: 3 × 3 × 3 = 27 voltage combinations

### Voltage Value Sources

**Source**: `table_supply_list.csv` or `table_supply_list_ac.csv` / `table_supply_list_dc.csv`

**Selection Logic** (read_supply.sh):
```bash
if [ "$sim_mode" == "ac" ]; then
    csv_file="configuration/table_supply_list_ac.csv"
elif [ "$sim_mode" == "dc" ]; then
    csv_file="configuration/table_supply_list_dc.csv"
else
    csv_file="configuration/table_supply_list.csv"
fi
```

### table_supply_list.csv Structure

**File Location**: `dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/table_supply_list_ac.csv`

**Format**:
```csv
rail,func_min,perf_min,nom,perf_max,func_max,htol,hvqk
vcc,0.68,0.69,0.78,0.88,0.89,0.945,1.6
vcc_vid_tt_h,0.665,0.675,0.75,0.935,0.945,0.945,1.6
vcc_vid_tt_c,0.68,0.69,0.78,0.935,0.945,0.945,1.6
vcc_vid_ff_h,0.665,0.675,0.75,0.88,0.89,0.945,1.6
vcc_vid_ff_c,0.665,0.675,0.75,0.88,0.89,0.945,1.6
vcc_vid_ss_h,0.68,0.69,0.75,0.935,0.945,0.945,1.6
vcc_vid_ss_c,0.68,0.69,0.78,0.935,0.945,0.945,1.6
vccana,0.705,0.715,0.75,0.785,0.795,0.945,1.6
1p1v,0.98,0.99,1.1,1.188,1.2,1.246,1.65
vcctx_600,0.565,0.575,0.6,0.625,0.635,0.623,0.825
vcctx_800,0.755,0.765,0.8,0.835,0.845,0.831,1.1
vcctx_1200,1.13,1.15,1.2,1.25,1.27,1.247,1.65
vcctx_1500,1.42,1.44,1.5,1.56,1.58,1.559,2.06
vcctx_1800,1.7,1.73,1.8,1.87,1.9,1.87,2.475
```

**Column Definitions**:
- **func_min**: Functional minimum voltage
- **perf_min**: Performance minimum voltage  
- **nom**: Nominal voltage
- **perf_max**: Performance maximum voltage
- **func_max**: Functional maximum voltage
- **htol**: High-temperature operating life maximum
- **hvqk**: High-voltage qualification maximum

### Voltage Selection by Condition

**Configuration Parameter**: `condition` in `config.cfg`

```bash
# config.cfg
condition:func   # or perf, htol, hvqk
```

**read_supply.sh Logic**:
```bash
if [ "$condition" == "func" ]; then
    vccmin=$col2  # func_min
    vccnom=$col4  # nom
    vccmax=$col6  # func_max
elif [ "$condition" == "perf" ]; then
    vccmin=$col3  # perf_min
    vccnom=$col4  # nom
    vccmax=$col5  # perf_max
elif [ "$condition" == "htol" ]; then
    vccmin=$col2  # func_min
    vccnom=$col4  # nom
    vccmax=$col7  # htol
elif [ "$condition" == "hvqk" ]; then
    vccmin=$col2  # func_min
    vccnom=$col4  # nom
    vccmax=$col8  # hvqk
fi
```

**Example (vcc, functional condition)**:
```
vccmin = 0.68
vccnom = 0.78
vccmax = 0.89
```

### VID Voltage Support

**VID (Voltage ID)** provides corner-specific and temperature-specific voltage values.

**Configuration**: `vcc_vid:Yes` in `config.cfg`

**VID Voltage Table** (18 values):
```
TT Corner:
  vccmin_tt_h = 0.665  (TT, hot, min)
  vccnom_tt_h = 0.675  (TT, hot, nom)
  vccmax_tt_h = 0.75   (TT, hot, max)
  vccmin_tt_c = 0.68   (TT, cold, min)
  vccnom_tt_c = 0.69   (TT, cold, nom)
  vccmax_tt_c = 0.78   (TT, cold, max)

FF Corner:
  vccmin_ff_h = 0.665
  vccnom_ff_h = 0.675
  vccmax_ff_h = 0.75
  vccmin_ff_c = 0.665
  vccnom_ff_c = 0.675
  vccmax_ff_c = 0.75

SS Corner:
  vccmin_ss_h = 0.68
  vccnom_ss_h = 0.69
  vccmax_ss_h = 0.75
  vccmin_ss_c = 0.68
  vccnom_ss_c = 0.69
  vccmax_ss_c = 0.78
```

**VID Application Example**:
```
Corner: FFG → maps to FF corner category
Temperature: 125°C → hot
Voltage Trend: max
Result: .param vc=0.75  (uses vccmax_ff_h)
```

---

## 5. Complete PVT Matrix Generation

### pvt_loop.sh: Matrix Loop Generator

**Function**: `gen_pvt_loop_seq()` (Sequential) or `gen_pvt_loop_par()` (Parallel)

**Nested Loop Structure**:
```bash
for si_corner in $si_corner_list; do           # P: 7-9 iterations
    for ex_corner in $ex_corner_list; do       # E: 1-3 iterations
        for temp in $temp_list; do             # T: 4 iterations
            for voltage in $voltage_list; do   # V: 3 iterations (1 supply)
                # Generate netlist
                core_func $si_corner $ex_corner $temp $voltage
            done
        done
    done
done
```

### Variable Definitions

```bash
# From read_corner.sh
si_corner_list="TT FSG SFG FFG FFAG SSG SSAG"                    # 7 corners
ex_corner_list="typical"                                         # 1 extraction (pre-lay)
# OR
ex_corner_list="typical cworst_CCworst_T cbest_CCbest_T"        # 3 extractions (post-lay)

# Hardcoded in pvt_loop.sh
temp_list="m40 85 100 125"                                       # 4 temperatures

# From voltage sweep configuration (1 supply example)
voltage_list="v1min v1nom v1max"                                 # 3 voltages
```

### Total Matrix Calculations

**Pre-Layout (7 corners, 1 extraction, 4 temps, 3 voltages)**:
```
Total = 7 × 1 × 4 × 3 = 84 netlists
```

**Post-Layout Default (7 corners, 3 extractions, 4 temps, 3 voltages)**:
```
Typical extraction:  7 corners × 1 × 4 × 3 = 84
Cross extraction:    4 corners × 2 × 4 × 3 = 96  (cworst + cbest)
Total = 84 + 96 = 180 netlists
```

**Post-Layout Full (7 corners, 3 extractions, 4 temps, 3 voltages)**:
```
Total = 7 × 3 × 4 × 3 = 252 netlists
```

**Post-Layout with GS/GF (9 corners, 3 extractions, 4 temps, 3 voltages)**:
```
Total = 9 × 3 × 4 × 3 = 324 netlists
```

### Directory Structure Generated

```
gpio/1p1v/  (or i3c/1p1v/)
├── TT/
│   ├── typical/
│   │   ├── typical_m40/
│   │   │   ├── v1min/sim_tx.sp
│   │   │   ├── v1nom/sim_tx.sp
│   │   │   └── v1max/sim_tx.sp
│   │   ├── typical_85/
│   │   │   ├── v1min/sim_tx.sp
│   │   │   ├── v1nom/sim_tx.sp
│   │   │   └── v1max/sim_tx.sp
│   │   ├── typical_100/
│   │   │   └── [3 voltage files]
│   │   └── typical_125/
│   │       └── [3 voltage files]
│   ├── cworst_CCworst_T/
│   │   └── [4 temp × 3 voltage = 12 files]
│   └── cbest_CCbest_T/
│       └── [12 files]
├── FFG/
│   └── [same structure: 3 extractions × 4 temps × 3 voltages]
├── SSG/
├── FSG/
├── SFG/
├── FFAG/
├── SSAG/
├── FFG_SSG/  (if GS/GF enabled)
└── SSG_FFG/  (if GS/GF enabled)
```

---

## 6. Configuration Impact on PVT Matrix

### Key Configuration Parameters

```bash
# config.cfg parameters that affect PVT matrix

mode:prelay                          # prelay or postlay
gs_corner:No                         # Include GS/GF corners (Yes/No)
gf_corner:No                         # (same as gs_corner)
postlay_cross_cornerlist:default     # default, full, or custom
condition:func                       # func, perf, htol, hvqk
sim_mode:ac                          # ac, dc, or default
vcc_vid:No                           # Yes or No
1st_supply_swp:vcc                   # First supply rail name
2nd_supply_swp:NA                    # Second supply (NA if not used)
3rd_supply_swp:NA                    # Third supply (NA if not used)
```

### Configuration Scenarios

#### Scenario 1: Minimal Pre-Layout

```bash
mode:prelay
gs_corner:No
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA

Result:
- 7 corners (TT, FFG, SSG, FSG, SFG, FFAG, SSAG)
- 1 extraction (typical)
- 4 temperatures
- 3 voltages (1 supply)
Total: 7 × 1 × 4 × 3 = 84 netlists
```

#### Scenario 2: Full Post-Layout with GS/GF

```bash
mode:postlay
gs_corner:Yes
postlay_cross_cornerlist:full
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA

Result:
- 9 corners (includes FFG_SSG, SSG_FFG)
- 3 extractions (typical, cworst, cbest)
- 4 temperatures
- 3 voltages (1 supply)
Total: 9 × 3 × 4 × 3 = 324 netlists
```

#### Scenario 3: Two-Supply Configuration

```bash
mode:prelay
gs_corner:No
1st_supply_swp:vcc
2nd_supply_swp:vcctx
3rd_supply_swp:NA

Result:
- 7 corners
- 1 extraction
- 4 temperatures
- 9 voltages (3×3 for 2 supplies)
Total: 7 × 1 × 4 × 9 = 252 netlists
```

---

## 7. Verification Checklist for wkpup Comparison

When comparing wkpup automation against this wkpup2 baseline, verify:

### Corner Definitions
- [ ] table_corner_list.csv exists and has identical structure
- [ ] All 7 standard corners defined: TT, FFG, SSG, FSG, SFG, FFAG, SSAG
- [ ] GS/GF corners defined if supported: FFG_SSG, SSG_FFG
- [ ] Corner lists match for each row type (nom_tt, full_tt, cross_default, etc.)

### Extraction Corners
- [ ] Pre-layout uses "typical" only
- [ ] Post-layout uses "typical cworst_CCworst_T cbest_CCbest_T"
- [ ] Extraction corner selection logic matches (default/full/custom)

### Temperature Points
- [ ] Temperature list is "m40 85 100 125"
- [ ] String-to-number conversion works (m40 → -40)
- [ ] VID temperature categorization correct (m40=cold, 125=hot)

### Voltage Configuration
- [ ] table_supply_list.csv exists with all required rails
- [ ] Voltage selection by condition works (func/perf/htol/hvqk)
- [ ] VID voltage table has 18 values (6 per corner: tt, ff, ss)
- [ ] Multi-supply voltage combinations calculated correctly

### PVT Loop Generation
- [ ] pvt_loop.sh generates correct nested loops
- [ ] Sequential and parallel modes both work
- [ ] Total netlist count matches expected value
- [ ] Directory structure matches: corner/extraction/extraction_temp/voltage/

### Configuration Parameters
- [ ] mode parameter affects extraction corner count
- [ ] gs_corner/gf_corner affects corner count
- [ ] postlay_cross_cornerlist affects cross-extraction corners
- [ ] Supply sweep parameters affect voltage combinations
- [ ] vcc_vid parameter enables/disables VID support

---

## 8. Critical Success Criteria

For wkpup automation to be considered **equivalent** to wkpup2:

1. ✅ **Corner definitions must be identical** (table_corner_list.csv)
2. ✅ **Voltage tables must be identical** (table_supply_list*.csv)
3. ✅ **Temperature list must be identical** (m40, 85, 100, 125)
4. ✅ **PVT matrix dimensions must match** for same configuration
5. ✅ **Total netlist count must be correct** (84, 180, 252, or 324)
6. ✅ **Directory structure must match** exactly
7. ✅ **Corner selection logic must be identical** (read_corner.sh)
8. ✅ **Voltage selection logic must be identical** (read_supply.sh)
9. ✅ **VID support must function identically** (18-value table)
10. ✅ **Configuration parameters must affect matrix identically**

**ANY deviation from these criteria indicates incomplete or incorrect PVT coverage.**

---

## 9. Test Cases for Validation

### Test Case 1: Pre-Layout 7-Corner Matrix

**Configuration**:
```bash
mode:prelay
gs_corner:No
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA
```

**Expected Result**:
```
Netlists: 84
Directory count: 7 corners × 1 extraction × 4 temps × 3 voltages
Directory example: TT/typical/typical_85/v1nom/sim_tx.sp
```

**Verification**:
```bash
find . -name "sim_tx.sp" | wc -l  # Should be 84
find . -type d -name "TT" | wc -l  # Should be 1
find . -type d -name "FFG_SSG" | wc -l  # Should be 0 (GS/GF disabled)
```

---

### Test Case 2: Post-Layout with GS/GF

**Configuration**:
```bash
mode:postlay
gs_corner:Yes
postlay_cross_cornerlist:full
```

**Expected Result**:
```
Netlists: 324
Corners: 9 (includes FFG_SSG, SSG_FFG)
Extractions: 3 (typical, cworst_CCworst_T, cbest_CCbest_T)
```

**Verification**:
```bash
find . -name "sim_tx.sp" | wc -l  # Should be 324
find . -type d -name "FFG_SSG" | wc -l  # Should be 1
find . -type d -path "*/cworst_CCworst_T/*" | head -1  # Should exist
```

---

### Test Case 3: VID Voltage Application

**Configuration**:
```bash
vcc_vid:Yes
condition:perf
```

**Input Corner**: FFG, 125°C, max voltage

**Expected Result**:
```spice
.param vc=0.89  # Uses vccmax_ff_h from VID table
```

**Verification**:
```bash
corner_dir="FFG/typical/typical_125/v1max"
grep "\.param vc=" $corner_dir/sim_tx.sp
# Should show VID value, not standard vccmax
```

---

### Test Case 4: Two-Supply Voltage Combinations

**Configuration**:
```bash
1st_supply_swp:vcc
2nd_supply_swp:vcctx
3rd_supply_swp:NA
```

**Expected Voltage Directories**:
```
v1min_v2min, v1min_v2nom, v1min_v2max
v1nom_v2min, v1nom_v2nom, v1nom_v2max
v1max_v2min, v1max_v2nom, v1max_v2max
```

**Verification**:
```bash
find TT/typical/typical_85 -type d -name "v1*_v2*" | wc -l
# Should be 9 (3×3 combinations)
```

---

## 10. References

### Source Documents
- **COMPREHENSIVE_ANALYSIS.md**: Lines 3070-3250 (configuration system)
- **table_corner_list.csv**: Corner definitions
- **table_supply_list_ac.csv**: AC voltage values
- **pvt_loop.sh**: PVT matrix generation loops

### Related Analysis Documents
- **TESTBENCH_GENERATION_GAPS.md**: How gen_tb.pl uses PVT parameters
- **SIMULATION_FLOW_GAPS.md**: How PVT matrix flows through stages
- **CONFIGURATION_GAPS.md**: config.cfg parameter definitions

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: ✅ BASELINE REFERENCE COMPLETE  
**Next Step**: Compare wkpup automation PVT matrix against this baseline  
**Critical Finding**: PVT matrix is fully configurable with 84-324 simulation range
