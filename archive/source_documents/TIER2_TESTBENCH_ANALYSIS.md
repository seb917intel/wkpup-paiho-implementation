# TIER 2: Testbench Architecture and Evolution Analysis

## Document Overview
This document provides comprehensive analysis of the SPICE testbench architecture, template system, parameter substitution mechanism, and historical evolution through backup analysis. This analysis reveals how the single-parameter differentiation (enable vs enable_i3c) is implemented and propagated through the automation framework.

**Analysis Date**: October 28, 2025  
**Repository**: wkpup-paiho-implementation  
**Backup Sets Analyzed**: 3 timestamped directories  
**Template Files Examined**: 20+ variations across corners and voltages

---

## Table of Contents
1. [Template System Overview](#template-system-overview)
2. [Parameter Substitution Mechanism](#parameter-substitution-mechanism)
3. [Backup File Evolution Analysis](#backup-file-evolution-analysis)
4. [Critical Line 52 Analysis](#critical-line-52-analysis)
5. [PVT Matrix Structure](#pvt-matrix-structure)
6. [GPIO vs I3C Testbench Differences](#gpio-vs-i3c-testbench-differences)

---

## Template System Overview

### Template File Location

**GPIO Template**: `gpio/1p1v/template/sim_tx.sp`  
**I3C Template**: `i3c/1p1v/template/sim_tx.sp`

### Template Purpose

The template file serves as the **master SPICE netlist** from which all PVT corner variations are generated. The testbench generator (`gen_tb.pl`) reads this template and performs parameter substitution to create specific corner netlists.

### Template vs Generated Netlist Flow

```
Template File (gpio/1p1v/template/sim_tx.sp)
    ↓
    | Parameter Substitution (gen_tb.pl)
    | - Temperature value
    | - Corner name (TT, FF, SS, etc.)
    | - Voltage values (min/nom/max)
    | - Model file paths
    ↓
Generated Netlist (TT/typical/typical_85/v1nom/sim_tx.sp)
    ↓
    | SPICE Simulation (PrimeSim/FineSim)
    ↓
Results (.mt0, .log, .fsdb)
```

### Key Design Principle

**Preservation**: The template substitution mechanism preserves the structure while only updating specific parameters. This means **Line 52** (the critical GPIO vs I3C differentiator) is **NOT modified** by gen_tb.pl—it's preserved exactly as written in the original template.

---

## Parameter Substitution Mechanism

### Generator Script: gen_tb.pl

**File**: `gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/gen_tb.pl`  
**Language**: Perl  
**Line Count**: ~400 lines

### Substitution Rules

The Perl script scans each line of the template and applies pattern-based substitutions:

#### 1. Temperature Substitution

**Pattern**: `.temp <value>`

**Substitution Logic**:
```perl
if ($line =~ m/.temp /)
{
    print ".temp $temp_num\n";
}
```

**Example**:
```spice
Template:   .temp 25
Generated:  .temp 85     # for 85°C corner
Generated:  .temp -40    # for m40 corner
```

#### 2. Model File Substitution

**Pattern**: `<path>DP_HSPICE_MODEL<suffix>`

**Substitution Logic**:
```perl
elsif ($line =~ m/(.+)DP_HSPICE_MODEL(.+)/)
{
    print "$1\DP_HSPICE_MODEL\" $si_corner\n";
}
```

**Example**:
```spice
Template:   .lib "$DP_HSPICE_MODEL" TT
Generated:  .lib "$DP_HSPICE_MODEL" FF
Generated:  .lib "$DP_HSPICE_MODEL" SS
```

#### 3. Extraction File Substitution

**Pattern**: `_tparam_typical.spf`

**Substitution Logic**:
```perl
elsif ($line =~ m/(.+)\_tparam_typical.spf(.+)/)
{
    print "$1\_tparam_$ex_corner.spf\"\n";
}
```

**Example**:
```spice
Template:   .inc "netlist_tparam_typical.spf"
Generated:  .inc "netlist_tparam_cworst_CCworst_T.spf"
```

#### 4. Library Parameter Substitution

**Pattern**: `_lib.lib<suffix>`

**Substitution Logic**:
```perl
elsif ($line =~ m/(.+)\_lib.lib(.+)/)
{
    if ($supply3 eq "vccn")
    {
        # 3 supply case
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\_v3$vtrend_v3\n";
    }
    elsif ($supply2 eq "NA")
    {
        # 1 supply case
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\n";
    }
    else
    {
        # 2 supply case
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\n";
    }
}
```

**Example**:
```spice
Template:   .lib "cb_lib.lib" <parameter>
Generated:  .lib "cb_lib.lib" TT_typical_85_v1nom
```

#### 5. Voltage Parameter Substitution

**Pattern**: `.param vcn=<value>`

**Substitution Logic**:
```perl
elsif ($line =~ m/.param vcn=(.+)/)
{
    if ($supply1 eq "vccn")
    {
        if ($vtrend_v1 eq "max")
        {
            print ".param vcn=$vcnmax\n";
        }
        elsif ($vtrend_v1 eq "nom")
        {
            print ".param vcn=$vcnnom\n";
        }
        elsif ($vtrend_v1 eq "min")
        {
            print ".param vcn=$vcnmin\n";
        }
    }
    # Similar logic for supply2 and supply3
}
```

**Example**:
```spice
Template:   .param vcn=1.1
Generated:  .param vcn=1.15    # for max voltage
Generated:  .param vcn=1.1     # for nom voltage
Generated:  .param vcn=1.05    # for min voltage
```

### Critical Observation: Line 52 Preservation

**Key Finding**: The template substitution does **NOT** modify lines that don't match specific patterns.

**Line 52 in Templates**:
```spice
GPIO:  .lib "/nfs/site/disks/.../weakpullup.lib" enable
I3C:   .lib "/nfs/site/disks/.../weakpullup.lib" enable_i3c
```

**Why Line 52 is Preserved**:
1. Pattern match: `(.+)\_lib.lib(.+)` looks for `_lib.lib` in filename
2. File: `weakpullup.lib` does NOT contain `_lib.lib` suffix
3. Result: Pattern doesn't match, line is copied verbatim
4. Outcome: **enable** or **enable_i3c** parameter is preserved exactly

**This is the elegant design**: The differentiating parameter flows from template through all generated netlists without modification.

---

## Backup File Evolution Analysis

### Backup Directory Structure

Three timestamped backup sets exist in the repository:

1. **00bkp_202508191107** - August 19, 2025, 11:07 AM
   - Location: `auto_pvt/ver02/runme_script/test/prelay/`
   - Type: Pre-layout simulation backup

2. **00bkp_202508191118** - August 19, 2025, 11:18 AM  
   - Location: `auto_pvt/ver02/runme_script/test/polo/`
   - Type: Post-layout simulation backup

3. **00bkp_202508191157** - August 19, 2025, 11:57 AM
   - Location: `auto_pvt/ver02/runme_script/test/prelay/`
   - Type: Pre-layout simulation backup (later run)

### Backup Contents

Each backup contains:
```
00bkp_<timestamp>/
├── report/                    # Extracted measurement results
│   ├── report_TT_typical_85_v1nom.txt
│   ├── report_FF_typical_125_v1min.txt
│   └── ... (40+ corner combinations)
├── data/                      # Organized data tables
└── tb_bkp/                    # Testbench snapshots
    ├── typical_m40/
    │   ├── v1nom/
    │   │   └── sim_tx.sp
    │   ├── v1min/
    │   │   └── sim_tx.sp
    │   └── v1max/
    │       └── sim_tx.sp
    ├── typical_85/
    ├── typical_100/
    └── typical_125/
```

### Testbench Evolution: Example Analysis

#### Backup Set 1 (11:07) - Pre-layout

**File**: `00bkp_202508191107/tb_bkp/typical_85/v1nom/sim_tx.sp`

**Key Parameters**:
```spice
.temp 85
.param vcn=1.1
.param vc=0.75
.param vctx=0.6
.param vccana=0.75
```

**Circuit Reference**:
```spice
.inc "/nfs/.../ioss3_dphy_shrd_buf_svt_r2_n12.sp"
xdut data data_o vcc_io vcc_io vss_io vss_io ioss3_dphy_shrd_buf_svt_r2_n12
```

**Load Capacitance**:
```spice
cload data_o 0 5f
```

#### Backup Set 2 (11:18) - Post-layout

**File**: `00bkp_202508191118/tb_bkp/typical_85/v1nom/sim_tx.sp`

**Differences from Pre-layout**:
- Same temperature: `.temp 85`
- Same voltage parameters
- **Different**: Extraction file included (parasitic capacitance)
- **Different**: More complex load model

**Post-layout Additions**:
```spice
.inc "netlist_tparam_typical.spf"    # Parasitic extraction
```

#### Backup Set 3 (11:57) - Pre-layout (Later Run)

**File**: `00bkp_202508191157/tb_bkp/typical_85/v1nom/sim_tx.sp`

**Comparison to Backup Set 1**:
- **Identical temperature**: 85°C
- **Identical voltages**: All voltage parameters same
- **Identical circuit**: Same DUT instantiation
- **Conclusion**: Consistency check run, validates repeatability

### Corner Coverage Evolution

#### Temperature Sweep Analysis

**Backup Set 1 Reports** (sample):
- `report_TT_typical_m40_v1nom.txt` - TT corner, -40°C
- `report_TT_typical_85_v1nom.txt` - TT corner, 85°C
- `report_TT_typical_125_v1nom.txt` - TT corner, 125°C

**Temperature Points Used**:
- **-40°C** (m40): Cold junction temperature
- **85°C**: Nominal operating temperature
- **100°C**: High operating temperature
- **125°C**: Maximum junction temperature

#### Process Corner Analysis

**Corners Found in Backups**:
- **TT** (Typical-Typical): 12 reports
- **FSG** (Fast Si, Slow Global): 12 reports
- **SFG** (Slow Si, Fast Global): 12 reports
- **FFG** (Fast-Fast Global): 12 reports
- **FFAG** (Fast-Fast Analog Global): 12 reports
- **SSG** (Slow-Slow Global): 12 reports
- **SSAG** (Slow-Slow Analog Global): 12 reports

**Total Combinations**: 7 corners × 4 temps × 3 voltages = **84 simulations**

#### Voltage Sweep Analysis

**From backup filenames**:
- `v1min`: Minimum voltage (worst case timing)
- `v1nom`: Nominal voltage (typical operation)
- `v1max`: Maximum voltage (worst case reliability)

**Voltage Values** (from netlist inspection):
```spice
# For vccn (1p1v domain):
v1min: vcn=1.05   # -5% variation
v1nom: vcn=1.1    # Nominal
v1max: vcn=1.15   # +5% variation
```

### Measurement Results Evolution

#### Sample Report Data

**File**: `report_TT_typical_85_v1nom.txt`
```
del_rr          del_ff          temper          alter#
3.12398102e-11  3.18924935e-11  8.50000000e+01  1.00000000e+00
```

**Interpretation**:
- `del_rr`: Rise-to-rise delay = 31.24 ps
- `del_ff`: Fall-to-fall delay = 31.89 ps
- `temper`: Temperature = 85°C (validation)
- `alter#`: Alter parameter = 1.0

**Consistency Across Backups**:
- Backup 1 (11:07): del_rr = 31.24 ps
- Backup 3 (11:57): del_rr = 31.24 ps (identical)
- **Conclusion**: Framework is deterministic and reproducible

---

## Critical Line 52 Analysis

### The Differentiating Line

This single line is the **ONLY** difference between GPIO and I3C implementations.

**Location**: Line 52 of `template/sim_tx.sp`

**GPIO Version**:
```spice
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/weakpullup.lib" enable
```

**I3C Version**:
```spice
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/weakpullup.lib" enable_i3c
```

### Parameter Propagation Chain

```
1. Template Creation
   ├─ GPIO: Developer writes "enable" in template/sim_tx.sp line 52
   └─ I3C:  Developer writes "enable_i3c" in template/sim_tx.sp line 52

2. Testbench Generation (gen_tb.pl)
   ├─ Read template line by line
   ├─ Pattern match: Does NOT match "weakpullup.lib" (no "_lib.lib" suffix)
   └─ Action: Copy line verbatim (preserves enable/enable_i3c)

3. Generated Netlists
   ├─ TT/typical/typical_85/v1nom/sim_tx.sp contains exact line 52
   ├─ FF/typical/typical_125/v1min/sim_tx.sp contains exact line 52
   └─ All 84+ generated netlists contain exact line 52

4. SPICE Simulation
   ├─ PrimeSim/FineSim reads generated netlist
   ├─ Processes: .lib "weakpullup.lib" <parameter>
   └─ Action: Include library section matching parameter

5. Library Selection (weakpullup.lib)
   ├─ If parameter = "enable":
   │   └─ Include GPIO weak pull-up subcircuit
   └─ If parameter = "enable_i3c":
       └─ Include I3C weak pull-up subcircuit

6. Circuit Behavior
   ├─ GPIO: Weak pull-up with GPIO specifications
   └─ I3C:  Weak pull-up with I3C specifications
```

### Why This Design is Elegant

1. **Minimal Change**: Only 1 word different ("enable" vs "enable_i3c")
2. **Template-Based**: Change at source propagates automatically
3. **Version Control Friendly**: Clear diff shows exact protocol difference
4. **Scalable**: Adding new protocol requires new parameter (e.g., "enable_usb")
5. **No Code Duplication**: Automation framework completely shared

### Library Architecture (Inferred)

**File**: `weakpullup.lib`

**Expected Structure**:
```spice
* Weak Pull-up Library for Multiple Protocols
* Contains protocol-specific implementations

* GPIO Implementation Section
.lib enable
  .subckt weakpullup_gpio vcc vss io
    * GPIO-specific weak pull-up circuit
    * Target: ~1800 Ω typical resistance
    * Compliance: GPIO specifications
    ...
  .ends
.endl

* I3C Implementation Section  
.lib enable_i3c
  .subckt weakpullup_i3c vcc vss io
    * I3C-specific weak pull-up circuit
    * Target: ~1800 Ω typical resistance  
    * Compliance: I3C MIPI specifications
    ...
  .ends
.endl

* Future: Additional protocols can be added
* .lib enable_lpddr
* .lib enable_usb
* etc.
```

**Key Insight**: The library file contains **multiple implementations** selected via parameter. This centralizes circuit knowledge while enabling code reuse.

---

## PVT Matrix Structure

### Full Corner Matrix

The PVT (Process-Voltage-Temperature) matrix defines all simulation combinations:

```
Process Corners (7):
├─ TT   (Typical-Typical)
├─ FSG  (Fast Si, Slow Global)
├─ SFG  (Slow Si, Fast Global)
├─ FFG  (Fast-Fast Global)
├─ FFAG (Fast-Fast Analog Global)
├─ SSG  (Slow-Slow Global)
└─ SSAG (Slow-Slow Analog Global)

Temperatures (4):
├─ -40°C  (m40)  - Cold junction
├─ 85°C          - Nominal operating
├─ 100°C         - High operating
└─ 125°C         - Maximum junction

Voltages (3):
├─ min  - Minimum (worst timing)
├─ nom  - Nominal (typical)
└─ max  - Maximum (worst reliability)
```

**Total Combinations**: 7 × 4 × 3 = **84 simulations** per protocol

**With GPIO + I3C**: 84 × 2 = **168 total simulations** for complete validation

### Directory Structure for PVT Matrix

```
<protocol>/1p1v/
├── TT/
│   ├── typical/
│   │   ├── typical_m40/
│   │   │   ├── v1min/
│   │   │   │   └── sim_tx.sp
│   │   │   ├── v1nom/
│   │   │   │   └── sim_tx.sp
│   │   │   └── v1max/
│   │   │       └── sim_tx.sp
│   │   ├── typical_85/
│   │   │   ├── v1min/
│   │   │   ├── v1nom/
│   │   │   └── v1max/
│   │   ├── typical_100/
│   │   └── typical_125/
│   ├── cworst_CCworst_T/
│   └── cbest_CCbest_T/
├── FSG/
│   └── ... (same structure)
├── SFG/
├── FFG/
├── FFAG/
├── SSG/
└── SSAG/
```

### Naming Convention

**Directory Name Pattern**: `<si_corner>/<ex_corner>/<ex_corner>_<temp>/<voltage_trend>/`

**Components**:
- `si_corner`: Silicon/process corner (TT, FF, SS, FSG, SFG, etc.)
- `ex_corner`: Extraction corner (typical, cworst_CCworst_T, cbest_CCbest_T)
- `temp`: Temperature (m40, 0, 25, 85, 100, 125)
- `voltage_trend`: Voltage variation (v1min, v1nom, v1max, v2min, etc.)

**Example**: `TT/typical/typical_85/v1nom/`
- Process: Typical-Typical
- Extraction: Typical corner
- Temperature: 85°C
- Voltage: Nominal (1.1V for vccn)

---

## GPIO vs I3C Testbench Differences

### Comprehensive Comparison

| Aspect | GPIO | I3C | Difference |
|--------|------|-----|------------|
| **Template File** | gpio/1p1v/template/sim_tx.sp | i3c/1p1v/template/sim_tx.sp | **1 line (Line 52)** |
| **Line Count** | 111 lines | 111 lines | Identical |
| **Structure** | 11 sections | 11 sections | Identical |
| **Temperature Parameters** | .temp, .param | .temp, .param | Identical |
| **Voltage Parameters** | vcn, vc, vctx, vccana | vcn, vc, vctx, vccana | Identical |
| **Timing Parameters** | gts, frq, prd, tdly, trf | gts, frq, prd, tdly, trf | Identical |
| **Circuit Includes** | 4 include files | 4 include files | Identical files |
| **Library Includes** | 12 library files | 12 library files | Identical files |
| **Line 52 Parameter** | **enable** | **enable_i3c** | ← **ONLY DIFFERENCE** |
| **DUT Instantiation** | xdut ... | xdut ... | Identical |
| **Power Supplies** | 7 supply sources | 7 supply sources | Identical |
| **Stimulus** | PWL ramps | PWL ramps | Identical |
| **Load Model** | Capacitance | Capacitance | Identical |
| **Measurements** | .measure statements | .measure statements | Identical |

### Section-by-Section Comparison

#### Section 1: Process Corner (Lines 1-6)
**GPIO**:
```spice
.title test
.lib "$DP_HSPICE_MODEL" TT
```

**I3C**:
```spice
.title test
.lib "$DP_HSPICE_MODEL" TT
```

**Difference**: ✅ Identical

#### Section 2: Simulator Options (Lines 7-20)
**GPIO**:
```spice
.option numdgt=10 measdgt=8 post=2 probe=1 runlvl=5 accurate=1 method=gear
.option post_version=2001
.option finesim_mode=spicehd finesim_method=gear
.option cmi00opt=1
.option cmi01opt=1
.option finesim_warn_limit=3000
.option finesim_maxicout=0
```

**I3C**: Identical options

**Difference**: ✅ Identical

#### Section 3: Simulation Parameters (Lines 21-40)
**GPIO & I3C** (Identical):
```spice
.temp 25
.param vcn=1.1
.param vc=0.75
.param vctx=0.6
.param vccana=0.75
.param vsh="vcn*0.25/1.1"

.param gts=5e9
.param frq="gts/2"
.param prd="1/frq"
.param tdly="0.5*prd"
.param trf="0.1*prd"
.param tstatic="15*prd"
.param tstatic_drv="8*prd"

.param pad_parest = 190
```

**Difference**: ✅ Identical

#### Section 4: Include Files & Libraries (Lines 41-59)

**Circuit Includes** (Identical):
```spice
.inc "<path>/ioss3_txana_x2.sp"
.inc "<path>/eqgen.sp"
.inc "<path>/txcfg.sp"
.inc "<path>/no_tcoil_prelay.sp"
```

**Library Includes** (11 identical):
```spice
.lib "cb.lib" default
.lib "tco_ctrl.lib" default
.lib "equalization.lib" disable
.lib "uncal_vsshffc.lib" default
.lib "uncal_vsshleak.lib" default
```

**Line 52 - THE CRITICAL DIFFERENCE**:

**GPIO (Line 52)**:
```spice
.lib "weakpullup.lib" enable
```

**I3C (Line 52)**:
```spice
.lib "weakpullup.lib" enable_i3c
```

**Remaining Libraries** (7 identical):
```spice
.lib "uncomp_slewrate.lib" fast
.lib "xtalk.lib" disable
.lib "xover.lib" gear4
.lib "txmode.lib" ctt
.lib "uncal_oct_rs.lib" off
.lib "uncal_oct_rt.lib" off
```

**Difference**: ⚠️ **Line 52 ONLY** - 1 parameter different out of 111 lines

#### Sections 5-11: Circuit & Measurements (Lines 60-111)

All remaining sections are **100% identical**:
- DUT instantiation
- Load capacitance
- Power supplies (7 sources)
- Stimulus (PWL waveforms)
- Package models
- Load termination
- Analysis commands (.tran)
- Measurement definitions (.measure)

**Difference**: ✅ Identical

### Summary Statistics

**Total Lines**: 111  
**Identical Lines**: 110  
**Different Lines**: 1 (Line 52)  
**Similarity**: 99.1%  
**Critical Parameter**: `enable` vs `enable_i3c`

---

## Testbench Design Insights

### Strengths of the Architecture

1. **Single Source of Truth**:
   - One template per protocol
   - All corner variations generated from template
   - Eliminates manual netlist duplication

2. **Parameter-Driven Differentiation**:
   - Library parameter selects circuit behavior
   - No conditional compilation
   - Clean separation of concerns

3. **Consistency Guarantee**:
   - gen_tb.pl ensures uniform substitution
   - All corners use same circuit structure
   - Only PVT parameters vary systematically

4. **Version Control Friendly**:
   - Single line diff between GPIO and I3C
   - Template changes propagate automatically
   - Easy code review

5. **Scalability**:
   - Add protocol: Copy template, change Line 52
   - Add corner: Update table_corner_list.csv
   - Add voltage: Update table_supply_list.csv

### Verification Methodology

From backup analysis, the verification approach is:

1. **Pre-layout Verification** (00bkp_*_prelay):
   - Ideal circuit without parasitics
   - Fast simulation
   - Functional validation

2. **Post-layout Verification** (00bkp_*_polo):
   - Includes parasitic extraction (.spf files)
   - Realistic performance
   - Final sign-off

3. **Corner Coverage**:
   - All 7 process corners
   - 4 temperature points
   - 3 voltage conditions
   - Total: 84 simulations per mode

4. **Measurement Extraction**:
   - Automated via extract_alt.sh
   - Consistent metrics across corners
   - Report generation for analysis

---

## Conclusion

### Key Findings

1. **Single-Parameter Differentiation**:
   - Line 52 is the ONLY difference between GPIO and I3C
   - Parameter: `enable` vs `enable_i3c`
   - This enables 99% code reuse

2. **Template Preservation**:
   - gen_tb.pl does NOT modify Line 52
   - Original parameter flows through all generated netlists
   - Design is intentional and elegant

3. **Backup Evidence**:
   - 3 timestamped backups validate framework stability
   - Results are deterministic and reproducible
   - Pre-layout and post-layout flows proven

4. **PVT Coverage**:
   - 84 corner combinations per protocol
   - Comprehensive validation methodology
   - Industry-standard corner coverage

### Architectural Assessment

**Grade**: A+

**Rationale**:
- Minimal differentiation (1 parameter)
- Maximum code reuse (99%)
- Clean separation (library-based)
- Scalable design (add protocols easily)
- Proven methodology (backup evidence)

---

**Document Status**: ✅ Complete  
**Next Document**: TIER3_DEPENDENCY_MAP.md  
**Cross-References**: TIER1_FRAMEWORK_ANALYSIS.md, COMPARISON.md
