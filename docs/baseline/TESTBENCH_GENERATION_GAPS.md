# Testbench Generation Analysis: wkpup2 Baseline Reference

## Document Purpose

This document provides the **authoritative baseline** for testbench generation in Pai Ho's wkpup2 implementation. It serves as the reference for identifying gaps and inconsistencies when comparing against the wkpup automation system.

**Status**: ✅ BASELINE REFERENCE (wkpup2)  
**Source**: COMPREHENSIVE_ANALYSIS.md and actual wkpup2 implementation  
**Location**: `gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/gen_tb.pl`

---

## Executive Summary

### Critical Facts About gen_tb.pl

- **Lines of Code**: 571 lines
- **Language**: Perl (optimized for pattern-based text processing)
- **Input Arguments**: 44 total
- **Pattern Matching Rules**: 10 distinct rules
- **Input File**: `template/sim_tx.sp` (111 lines)
- **Output**: Fully substituted SPICE netlist (111 lines, modified)
- **Critical Behavior**: Line 52 is preserved verbatim (does NOT match any pattern)

---

## 1. Complete Argument List (44 Arguments)

### Arguments 1-10: Core PVT Parameters

```perl
$infile        # Arg 1:  template/sim_tx.sp (template file path)
$si_corner     # Arg 2:  TT, FFG, SSG, FSG, SFG, FFAG, SSAG (silicon corner)
$ex_corner     # Arg 3:  typical, cworst_CCworst_T, cbest_CCbest_T (extraction corner)
$temperature   # Arg 4:  m40, 85, 100, 125 (temperature in string format)
$vtrend_v1     # Arg 5:  min, nom, max (1st supply voltage trend)
$vtrend_v2     # Arg 6:  min, nom, max (2nd supply voltage trend)
$vtrend_v3     # Arg 7:  min, nom, max (3rd supply voltage trend)
$supply1       # Arg 8:  vcc, vccana, vccn (1st supply rail name)
$supply2       # Arg 9:  vcctx, vccana, vccn, NA (2nd supply rail name)
$supply3       # Arg 10: vccn, vccn_vcctx, NA (3rd supply rail name)
```

### Arguments 11-22: Voltage Values

```perl
# VCC voltage values (Args 11-13)
$vccmin        # Arg 11: VCC minimum voltage
$vccnom        # Arg 12: VCC nominal voltage
$vccmax        # Arg 13: VCC maximum voltage

# VCCN voltage values (Args 14-16)
$vcnmin        # Arg 14: VCCN minimum voltage
$vcnnom        # Arg 15: VCCN nominal voltage
$vcnmax        # Arg 16: VCCN maximum voltage

# VCCANA voltage values (Args 17-19)
$vccanamin     # Arg 17: VCCANA minimum voltage
$vccananom     # Arg 18: VCCANA nominal voltage
$vccanamax     # Arg 19: VCCANA maximum voltage

# VCCTX voltage values (Args 20-22)
$vctxmin       # Arg 20: VCCTX minimum voltage
$vctxnom       # Arg 21: VCCTX nominal voltage
$vctxmax       # Arg 22: VCCTX maximum voltage
```

### Argument 23: VID Flag

```perl
$vcc_vid       # Arg 23: "Yes" or "No" (Voltage ID support enabled/disabled)
```

### Arguments 24-44: VID Voltage Tables (21 Values)

**TT Corner VID Voltages** (Args 24-29):
```perl
$vccmin_tt_h   # Arg 24: TT corner, hot temperature, minimum VCC
$vccnom_tt_h   # Arg 25: TT corner, hot temperature, nominal VCC
$vccmax_tt_h   # Arg 26: TT corner, hot temperature, maximum VCC
$vccmin_tt_c   # Arg 27: TT corner, cold temperature, minimum VCC
$vccnom_tt_c   # Arg 28: TT corner, cold temperature, nominal VCC
$vccmax_tt_c   # Arg 29: TT corner, cold temperature, maximum VCC
```

**FF Corner VID Voltages** (Args 30-35):
```perl
$vccmin_ff_h   # Arg 30: FF corner, hot temperature, minimum VCC
$vccnom_ff_h   # Arg 31: FF corner, hot temperature, nominal VCC
$vccmax_ff_h   # Arg 32: FF corner, hot temperature, maximum VCC
$vccmin_ff_c   # Arg 33: FF corner, cold temperature, minimum VCC
$vccnom_ff_c   # Arg 34: FF corner, cold temperature, nominal VCC
$vccmax_ff_c   # Arg 35: FF corner, cold temperature, maximum VCC
```

**SS Corner VID Voltages** (Args 36-44):
```perl
$vccmin_ss_h   # Arg 36: SS corner, hot temperature, minimum VCC
$vccnom_ss_h   # Arg 37: SS corner, hot temperature, nominal VCC
$vccmax_ss_h   # Arg 38: SS corner, hot temperature, maximum VCC
$vccmin_ss_c   # Arg 39: SS corner, cold temperature, minimum VCC
$vccnom_ss_c   # Arg 40: SS corner, cold temperature, nominal VCC
$vccmax_ss_c   # Arg 41: SS corner, cold temperature, maximum VCC
```

**Note**: Arguments 42-44 exist in the parameter list but are not used in current ver03 implementation.

---

## 2. Pattern Matching Rules (10 Rules)

### Rule 1: Temperature Substitution

**Pattern**: `.temp <value>`

**Perl Code** (Lines 85-88):
```perl
if ($line =~ m/.temp /)
{
    print ".temp $temp_num\n";  # -40, 85, 100, or 125
}
```

**Transformation Examples**:
- Template: `.temp 100`
- Output (m40): `.temp -40`
- Output (85): `.temp 85`
- Output (100): `.temp 100`
- Output (125): `.temp 125`

**Temperature String to Number Mapping**:
```perl
# Lines 66-71
if ($temperature eq "m40") { $temp_num = "-40"; }
elsif ($temperature eq "85") { $temp_num = "85"; }
elsif ($temperature eq "100") { $temp_num = "100"; }
elsif ($temperature eq "125") { $temp_num = "125"; }
```

---

### Rule 2: HSPICE Model Corner Substitution

**Pattern**: `(.+)DP_HSPICE_MODEL(.+)`

**Perl Code** (Lines 90-93):
```perl
elsif ($line =~ m/(.+)DP_HSPICE_MODEL(.+)/)
{
    print "$1\DP_HSPICE_MODEL\" $si_corner\n";
}
```

**Transformation Examples**:
- Template: `.lib "$DP_HSPICE_MODEL" TT`
- Output (TT): `.lib "$DP_HSPICE_MODEL" TT`
- Output (FFG): `.lib "$DP_HSPICE_MODEL" FFG`
- Output (SSG): `.lib "$DP_HSPICE_MODEL" SSG`

---

### Rule 3: Extraction Parasitic Files

**Pattern A**: `(.+)\_tparam_typical.spf(.+)`  
**Pattern B**: `(.+)\_tparam_typical.red.spf(.+)`

**Perl Code** (Lines 96-103):
```perl
elsif ($line =~ m/(.+)\_tparam_typical.spf(.+)/)
{
    print "$1\_tparam_$ex_corner.spf\"\n";
}
elsif ($line =~ m/(.+)\_tparam_typical.red.spf(.+)/)
{
    print "$1\_tparam_$ex_corner.red.spf\"\n";
}
```

**Transformation Examples**:
- Template: `.inc "layout_tparam_typical.spf"`
- Output (typical): `.inc "layout_tparam_typical.spf"`
- Output (cworst_CCworst_T): `.inc "layout_tparam_cworst_CCworst_T.spf"`
- Output (cbest_CCbest_T): `.inc "layout_tparam_cbest_CCbest_T.spf"`

**Purpose**: Swaps parasitic extraction corner files for post-layout simulations

---

### Rule 4: Library Corner Parameters (**CRITICAL - Line 52 Exception**)

**Pattern**: `(.+)\_lib.lib(.+)` (files ending with `_lib.lib`)

**Perl Code** (Lines 144-161):
```perl
elsif ($line =~ m/(.+)\_lib.lib(.+)/)
{
    if ($supply3 eq "vccn") {
        # 3 supply configuration
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\_v3$vtrend_v3\n";
    }
    elsif ($supply2 eq "NA") {
        # 1 supply configuration
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\n";
    }
    else {
        # 2 supply configuration
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\n";
    }
}
```

**Pattern Matching Logic**:
```
Files that MATCH:
✓ custom_rs_lib.lib       (has _lib.lib)
✓ custom_rt_lib.lib       (has _lib.lib)
✓ anything_lib.lib        (has _lib.lib)

Files that DO NOT MATCH:
✗ weakpullup.lib          (no underscore before lib.lib)
✗ standard.lib            (no _lib pattern)
✗ models.lib              (no _lib pattern)
```

**Transformation Examples**:
```spice
# Template
.lib "custom_rs_lib.lib" default

# Output (1 supply: vcc, TT, typical, 85°C, nom)
.lib "custom_rs_lib.lib" TT_typical_85_v1nom

# Output (2 supplies: vcc + vcctx, FFG, typical, 125°C, max + min)
.lib "custom_rs_lib.lib" FFG_typical_125_v1max_v2min

# Output (3 supplies: vcc + vcctx + vccn, SSG, cworst_CCworst_T, -40°C, min + nom + max)
.lib "custom_rs_lib.lib" SSG_cworst_CCworst_T_m40_v1min_v2nom_v3max
```

**WHY LINE 52 IS PRESERVED**:
```spice
# Line 52 in template
.lib "weakpullup.lib" enable

# Pattern check: Does "weakpullup.lib" match (.+)_lib.lib(.+)?
# Answer: NO - there is no underscore before "lib.lib"
# Result: Falls through to Rule 10 (pass-through) - COPIED VERBATIM
```

**This is the CRITICAL MECHANISM that preserves the enable/enable_i3c differentiation!**

---

### Rule 5: VCCN Parameter Substitution

**Pattern**: `.param vcn=(.+)`

**Perl Code** (Lines 166-231):
```perl
elsif ($line =~ m/.param vcn=(.+)/)
{
    if ($supply1 eq "vccn") {
        if ($vtrend_v1 eq "max") { print ".param vcn=$vcnmax\n"; }
        elsif ($vtrend_v1 eq "nom") { print ".param vcn=$vcnnom\n"; }
        elsif ($vtrend_v1 eq "min") { print ".param vcn=$vcnmin\n"; }
    }
    elsif ($supply2 eq "vccn") {
        if ($vtrend_v2 eq "max") { print ".param vcn=$vcnmax\n"; }
        elsif ($vtrend_v2 eq "nom") { print ".param vcn=$vcnnom\n"; }
        elsif ($vtrend_v2 eq "min") { print ".param vcn=$vcnmin\n"; }
    }
    elsif ($supply3 eq "vccn" || $supply3 eq "vccn_vcctx") {
        if ($vtrend_v3 eq "max") { print ".param vcn=$vcnmax\n"; }
        elsif ($vtrend_v3 eq "nom") { print ".param vcn=$vcnnom\n"; }
        elsif ($vtrend_v3 eq "min") { print ".param vcn=$vcnmin\n"; }
    }
}
```

**Transformation Examples**:
- Template: `.param vcn=1.1`
- Output (vccn supply, max): `.param vcn=1.188`
- Output (vccn supply, nom): `.param vcn=1.1`
- Output (vccn supply, min): `.param vcn=1.012`

---

### Rule 6: VSSH Parameter (VCCN-Derived)

**Pattern**: `.param vsh=(.+)`

**Perl Code** (Lines 238-306):
```perl
elsif ($line =~ m/.param vsh=(.+)/)
{
    # Complex formula based on supply configuration and voltage trend
    if ($supply1 eq "vccn") {
        if ($vtrend_v1 eq "max") {
            print ".param vsh=\"(($vcnnom-0.8)*vcn/$vcnnom)+0.05\"\n";
        }
        elsif ($vtrend_v1 eq "nom") {
            print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)\"\n";
        }
        elsif ($vtrend_v1 eq "min") {
            print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)-0.05\"\n";
        }
    }
    # Similar logic for supply2 and supply3...
}
```

**VSSH Formula Examples**:
```spice
# Maximum voltage trend
.param vsh="((1.1-0.8)*vcn/1.1)+0.05"

# Nominal voltage trend
.param vsh="((1.1-0.85)*vcn/1.1)"

# Minimum voltage trend
.param vsh="((1.1-0.85)*vcn/1.1)-0.05"
```

**Purpose**: VSSH (substrate voltage) is calculated as a function of VCCN with offset adjustments for voltage corners

---

### Rule 7: VCC Parameter with VID Support (**MOST COMPLEX RULE**)

**Pattern**: `.param vc=(.+)`

**Perl Code** (Lines 310-484):
```perl
elsif ($line =~ m/.param vc=(.+)/)
{
    if ($supply1 eq "vcc") {
        if ($vtrend_v1 eq "max") {
            if ($vcc_vid eq "Yes") {
                # VID ENABLED: Use corner-specific and temperature-specific tables
                if ($vcc_vid_corner eq "tt") {
                    if ($temperature eq "m40") { print ".param vc=$vccmax_tt_c\n"; }
                    elsif ($temperature eq "125") { print ".param vc=$vccmax_tt_h\n"; }
                    else { print ".param vc=$vccmax\n"; }
                }
                elsif ($vcc_vid_corner eq "ff") {
                    if ($temperature eq "m40") { print ".param vc=$vccmax_ff_c\n"; }
                    elsif ($temperature eq "125") { print ".param vc=$vccmax_ff_h\n"; }
                    else { print ".param vc=$vccmax\n"; }
                }
                elsif ($vcc_vid_corner eq "ss") {
                    if ($temperature eq "m40") { print ".param vc=$vccmax_ss_c\n"; }
                    elsif ($temperature eq "125") { print ".param vc=$vccmax_ss_h\n"; }
                    else { print ".param vc=$vccmax\n"; }
                }
            }
            else {
                # VID DISABLED: Use standard max voltage
                print ".param vc=$vccmax\n";
            }
        }
        elsif ($vtrend_v1 eq "nom") { /* similar logic for nom */ }
        elsif ($vtrend_v1 eq "min") { /* similar logic for min */ }
    }
    # Similar logic for supply2 and supply3...
}
```

**VCC Corner Mapping** (Lines 47-63):
```perl
# Map silicon corners to VID corner categories
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

**VID Logic Decision Tree**:
```
VCC Parameter Substitution:
├─ Is supply1 = "vcc"? (or supply2/supply3)
│  ├─ YES:
│  │  ├─ Is vcc_vid = "Yes"?
│  │  │  ├─ YES (VID ENABLED):
│  │  │  │  ├─ Map si_corner → vcc_vid_corner (tt/ff/ss)
│  │  │  │  ├─ Check temperature (m40=cold, 125=hot, other=typical)
│  │  │  │  └─ Select from 18 VID table values
│  │  │  └─ NO (VID DISABLED):
│  │  │     └─ Use standard vccmin/vccnom/vccmax
│  │  └─ Check voltage trend (min/nom/max)
│  └─ NO: Use nominal value
```

**VID Voltage Table Structure** (18 values total):
```
TT Corner:  vccmin_tt_h, vccnom_tt_h, vccmax_tt_h (hot)
            vccmin_tt_c, vccnom_tt_c, vccmax_tt_c (cold)

FF Corner:  vccmin_ff_h, vccnom_ff_h, vccmax_ff_h (hot)
            vccmin_ff_c, vccnom_ff_c, vccmax_ff_c (cold)

SS Corner:  vccmin_ss_h, vccnom_ss_h, vccmax_ss_h (hot)
            vccmin_ss_c, vccnom_ss_c, vccmax_ss_c (cold)
```

**Transformation Examples**:
```spice
# Template
.param vc=0.75

# Output (vcc supply, max trend, VID disabled)
.param vc=0.855

# Output (vcc supply, max trend, VID enabled, TT corner, -40°C)
.param vc=0.862  # vccmax_tt_c

# Output (vcc supply, max trend, VID enabled, FF corner, 125°C)
.param vc=0.870  # vccmax_ff_h
```

---

### Rule 8: VCCTX Parameter Substitution

**Pattern**: `.param vctx=(.+)`

**Perl Code** (Lines 487-524):
```perl
elsif ($line =~ m/.param vctx=(.+)/)
{
    if ($supply2 eq "vcctx") {
        if ($vtrend_v2 eq "max") { print ".param vctx=$vctxmax\n"; }
        elsif ($vtrend_v2 eq "nom") { print ".param vctx=$vctxnom\n"; }
        elsif ($vtrend_v2 eq "min") { print ".param vctx=$vctxmin\n"; }
    }
    elsif ($supply3 eq "vccn_vcctx") {
        if ($vtrend_v3 eq "max") { print ".param vctx=$vctxmax\n"; }
        elsif ($vtrend_v3 eq "nom") { print ".param vctx=$vctxnom\n"; }
        elsif ($vtrend_v3 eq "min") { print ".param vctx=$vctxmin\n"; }
    }
    else {
        print ".param vctx=$vctxnom\n";  # Default to nominal
    }
}
```

**Transformation Examples**:
- Template: `.param vctx=1.8`
- Output (vcctx supply, max): `.param vctx=1.944`
- Output (vcctx supply, nom): `.param vctx=1.8`
- Output (vcctx supply, min): `.param vctx=1.656`

---

### Rule 9: VCCANA Parameter Substitution

**Pattern**: `.param vccana=(.+)`

**Perl Code** (Lines 527-563):
```perl
elsif ($line =~ m/.param vccana=(.+)/)
{
    if ($supply1 eq "vccana") {
        if ($vtrend_v1 eq "max") { print ".param vccana=$vccanamax\n"; }
        elsif ($vtrend_v1 eq "nom") { print ".param vccana=$vccananom\n"; }
        elsif ($vtrend_v1 eq "min") { print ".param vccana=$vccanamin\n"; }
    }
    elsif ($supply2 eq "vccana") {
        if ($vtrend_v2 eq "max") { print ".param vccana=$vccanamax\n"; }
        elsif ($vtrend_v2 eq "nom") { print ".param vccana=$vccananom\n"; }
        elsif ($vtrend_v2 eq "min") { print ".param vccana=$vccanamin\n"; }
    }
    else {
        print ".param vccana=$vccananom\n";  # Default to nominal
    }
}
```

**Transformation Examples**:
- Template: `.param vccana=3.3`
- Output (vccana supply, max): `.param vccana=3.564`
- Output (vccana supply, nom): `.param vccana=3.3`
- Output (vccana supply, min): `.param vccana=3.036`

---

### Rule 10: Pass-Through (Default Rule)

**Pattern**: All lines that don't match Rules 1-9

**Perl Code** (Lines 566-569):
```perl
else
{
    print "$line\n";  # Copy line verbatim if no pattern matches
}
```

**Critical Lines Preserved by This Rule**:
```spice
# Line 52 - THE PROTOCOL DIFFERENTIATOR
.lib "weakpullup.lib" enable           # GPIO
.lib "weakpullup.lib" enable_i3c       # I3C

# All comment lines
* Circuit simulation for GPIO weak pull-up

# Standard SPICE commands not requiring substitution
.option post=2
.option accurate
.ic v(pad)=0
```

**This is HOW the enable/enable_i3c parameter is preserved unchanged through all 84 generated netlists!**

---

## 3. Complete Call Chain to gen_tb.pl

### Execution Path

```
runme.sh (user entry point)
  ↓
sim_pvt.sh config.cfg gen
  ↓ sources shell libraries:
  ├── tb_gen/pvt_loop.sh        (defines gen_pvt_loop_seq, gen_pvt_loop_par)
  ├── configuration/read_cfg.sh  (parses config.cfg → 15 parameters)
  ├── configuration/read_supply.sh (reads CSV → voltage values)
  └── configuration/read_corner.sh (reads CSV → corner lists)
  ↓ executes:
  gen_pvt_loop_seq() or gen_pvt_loop_par()
    ↓ nested loops create:
    for corner in [TT, FFG, SSG, FSG, SFG, FFAG, SSAG]
      for extraction in [typical, cworst_CCworst_T, cbest_CCbest_T]
        for temp in [m40, 85, 100, 125]
          for voltage in [v1min, v1nom, v1max]
            ↓ calls core_func():
            perl gen_tb.pl template/sim_tx.sp \
              $si_corner $ex_corner $temperature \
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
              > $output_path/sim_tx.sp
```

### Example gen_tb.pl Invocation

```bash
perl gen_tb.pl template/sim_tx.sp \
  TT typical 85 \
  nom nom nom \
  vcc NA NA \
  0.675 0.75 0.825 \
  0.99 1.1 1.21 \
  2.97 3.3 3.63 \
  1.62 1.8 1.98 \
  No \
  0.0 0.0 0.0 0.0 0.0 0.0 \
  0.0 0.0 0.0 0.0 0.0 0.0 \
  0.0 0.0 0.0 0.0 0.0 0.0 \
  > TT/typical/typical_85/v1nom/sim_tx.sp
```

---

## 4. Files Accessed by gen_tb.pl

### Input Files

**Template File** (`$infile` - Argument 1):
- **Path**: `template/sim_tx.sp`
- **Size**: 111 lines
- **Format**: SPICE netlist with variable placeholders
- **Critical Line**: Line 52 `.lib "weakpullup.lib" enable` (GPIO) or `.lib "weakpullup.lib" enable_i3c` (I3C)

### Output Files

**Generated Netlist** (stdout redirected):
- **Path**: `$corner/$extraction/${extraction}_${temp}/$voltage_combo/sim_tx.sp`
- **Example**: `TT/typical/typical_85/v1nom/sim_tx.sp`
- **Size**: 111 lines (same as template)
- **Format**: Fully substituted SPICE netlist
- **Critical Preservation**: Line 52 copied verbatim from template

### No External Dependencies

**gen_tb.pl does NOT read**:
- ✗ CSV configuration files
- ✗ config.cfg
- ✗ Library files
- ✗ Any other external inputs

**All data comes from**:
- ✓ Template file (argument 1)
- ✓ 43 command-line arguments (arguments 2-44)

**Processing model**: Pure stream processor (stdin → pattern matching → stdout)

---

## 5. Output Directory Structure

### PVT Matrix Organization

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
│   │   │   ├── v1min/sim_tx.sp
│   │   │   ├── v1nom/sim_tx.sp
│   │   │   └── v1max/sim_tx.sp
│   │   └── typical_125/
│   │       ├── v1min/sim_tx.sp
│   │       ├── v1nom/sim_tx.sp
│   │       └── v1max/sim_tx.sp
│   ├── cworst_CCworst_T/
│   │   └── [same temp/voltage structure]
│   └── cbest_CCbest_T/
│       └── [same temp/voltage structure]
├── FFG/
│   └── [same extraction/temp/voltage structure]
├── SSG/
│   └── [same extraction/temp/voltage structure]
├── FSG/
│   └── [same extraction/temp/voltage structure]
├── SFG/
│   └── [same extraction/temp/voltage structure]
├── FFAG/
│   └── [same extraction/temp/voltage structure]
└── SSAG/
    └── [same extraction/temp/voltage structure]
```

### Total Netlists Generated

**Calculation**:
- 7 corners (TT, FFG, SSG, FSG, SFG, FFAG, SSAG)
- × 3 extractions (typical only for pre-layout; typical + cworst + cbest for post-layout)
- × 4 temperatures (m40, 85, 100, 125)
- × 3 voltages (v1min, v1nom, v1max)

**Pre-layout** (mode=prelay): 7 × 1 × 4 × 3 = **84 netlists**  
**Post-layout** (mode=postlay): 7 × 3 × 4 × 3 = **252 netlists**

---

## 6. Verification Checklist for wkpup Comparison

When comparing wkpup automation against this wkpup2 baseline, verify:

### File Integrity
- [ ] gen_tb.pl is exactly 571 lines
- [ ] All 10 pattern matching rules are present and identical
- [ ] Rule order is preserved (critical for precedence)
- [ ] Line 52 preservation mechanism works (Rule 4 must NOT match "weakpullup.lib")

### Argument Handling
- [ ] All 44 arguments are passed in correct order
- [ ] Argument names match exactly (case-sensitive)
- [ ] VID table has 18 values (6 per corner: tt, ff, ss)
- [ ] Temperature string-to-number conversion is correct (m40 → -40)

### Pattern Matching Logic
- [ ] Rule 1: `.temp` substitution works
- [ ] Rule 2: `$DP_HSPICE_MODEL` substitution works
- [ ] Rule 3: `_tparam_typical.spf` extraction file substitution works
- [ ] Rule 4: `_lib.lib` pattern matching works BUT excludes "weakpullup.lib"
- [ ] Rule 5: `.param vcn=` VCCN substitution works
- [ ] Rule 6: `.param vsh=` VSSH formula calculation works
- [ ] Rule 7: `.param vc=` VCC substitution with VID support works
- [ ] Rule 8: `.param vctx=` VCCTX substitution works
- [ ] Rule 9: `.param vccana=` VCCANA substitution works
- [ ] Rule 10: Pass-through for unmatched lines works

### Critical Behavior
- [ ] Line 52 is preserved verbatim in ALL generated netlists
- [ ] "enable" parameter stays "enable" for GPIO
- [ ] "enable_i3c" parameter stays "enable_i3c" for I3C
- [ ] No other line is modified to become a library include statement

### Output Validation
- [ ] Correct number of netlists generated (84 for pre-layout, 252 for post-layout)
- [ ] Directory structure matches: `corner/extraction/extraction_temp/voltage/sim_tx.sp`
- [ ] All generated netlists are exactly 111 lines
- [ ] File permissions and ownership are correct

### Bit-Identical Test
- [ ] **CRITICAL**: For identical inputs, gen_tb.pl output must be bit-identical between wkpup and wkpup2
- [ ] Use `diff -q` to compare generated netlists
- [ ] Any difference indicates a regression or bug

---

## 7. Known Issues and Edge Cases

### Edge Case 1: Temperature Boundary Values
- **Issue**: Temperature string "m40" must map to numeric "-40"
- **Test**: Verify `.temp -40` appears in output, not `.temp m40`
- **Impact**: Simulator won't recognize "m40" as valid temperature

### Edge Case 2: VID Disabled with VID Tables
- **Issue**: If `vcc_vid="No"`, VID tables (args 24-44) are passed but ignored
- **Test**: Verify output uses standard vccmin/vccnom/vccmax, not VID values
- **Impact**: Incorrect voltage application if VID logic is broken

### Edge Case 3: Supply Configuration = "NA"
- **Issue**: supply2 or supply3 can be "NA" (not applicable)
- **Test**: Verify parameter substitution skips NA supplies correctly
- **Impact**: Parameters may be set incorrectly if NA handling is wrong

### Edge Case 4: Corner Name Case Sensitivity
- **Issue**: Corner names are case-sensitive (TT, FFG, SSG, not tt, ffg, ssg)
- **Test**: Verify corner names in output match input exactly
- **Impact**: Library lookups will fail if case is wrong

### Edge Case 5: Line 52 Pattern Collision
- **Issue**: If a file like "custom_weakpullup_lib.lib" existed, it WOULD match Rule 4
- **Test**: Verify template uses "weakpullup.lib" (no underscore before lib)
- **Impact**: Line 52 would be modified, breaking GPIO/I3C differentiation

---

## 8. Test Cases for Validation

### Test Case 1: Single Netlist Generation (Basic)

**Input**:
```bash
perl gen_tb.pl template/sim_tx.sp \
  TT typical 85 \
  nom nom nom \
  vcc NA NA \
  0.675 0.75 0.825 \
  0.99 1.1 1.21 \
  2.97 3.3 3.63 \
  1.62 1.8 1.98 \
  No \
  0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
```

**Expected Output Line 52**:
```spice
.lib "weakpullup.lib" enable   # (GPIO) or enable_i3c (I3C)
```

**Verification**:
```bash
# Generate netlist
perl gen_tb.pl ... > test_output.sp

# Check line 52
sed -n '52p' test_output.sp | grep -q 'weakpullup.lib.*enable'
echo $?  # Should be 0 (success)

# Verify it's unchanged from template
diff <(sed -n '52p' template/sim_tx.sp) <(sed -n '52p' test_output.sp)
echo $?  # Should be 0 (identical)
```

---

### Test Case 2: Temperature Conversion

**Input Temperatures**: m40, 85, 100, 125

**Expected Outputs**:
- m40 → `.temp -40`
- 85 → `.temp 85`
- 100 → `.temp 100`
- 125 → `.temp 125`

**Verification**:
```bash
# Test m40 conversion
perl gen_tb.pl template/sim_tx.sp TT typical m40 ... | grep "\.temp" 
# Should output: .temp -40
```

---

### Test Case 3: VID Support Enabled

**Input**:
```bash
perl gen_tb.pl template/sim_tx.sp \
  FFG typical 125 \
  max nom nom \
  vcc NA NA \
  0.675 0.75 0.825 \
  0.99 1.1 1.21 \
  2.97 3.3 3.63 \
  1.62 1.8 1.98 \
  Yes \
  0.725 0.765 0.805 \
  0.715 0.755 0.795 \
  0.735 0.775 0.815 \
  0.725 0.765 0.805 \
  0.705 0.745 0.785 \
  0.695 0.735 0.775
```

**Expected Output**:
```spice
.param vc=0.815   # vccmax_ff_h (FFG=ff, 125=hot, max, arg 32)
```

**Verification**:
```bash
perl gen_tb.pl ... | grep "\.param vc="
# Should output: .param vc=0.815
```

---

### Test Case 4: Library Corner Parameter Substitution

**Input**: 2-supply configuration (vcc + vcctx), TT corner, typical extraction, 85°C, v1nom + v2max

**Template Line**:
```spice
.lib "custom_rs_lib.lib" default
```

**Expected Output**:
```spice
.lib "custom_rs_lib.lib" TT_typical_85_v1nom_v2max
```

**Verification**:
```bash
perl gen_tb.pl ... | grep "custom_rs_lib.lib"
# Should output: .lib "custom_rs_lib.lib" TT_typical_85_v1nom_v2max
```

---

### Test Case 5: Full PVT Matrix Generation

**Input**: Run complete PVT loop (84 iterations)

**Expected**:
- 84 netlists created
- All in correct directory structure
- All Line 52 instances preserved

**Verification**:
```bash
# Count generated netlists
find . -name "sim_tx.sp" | wc -l
# Should output: 84 (for pre-layout mode)

# Check all Line 52 instances
find . -name "sim_tx.sp" -exec sed -n '52p' {} \; | sort | uniq
# Should output: exactly 1 unique line (either enable or enable_i3c)
```

---

## 9. Critical Success Criteria

For wkpup automation to be considered **equivalent** to wkpup2:

1. ✅ **gen_tb.pl must be bit-identical** to wkpup2 version (571 lines)
2. ✅ **All 44 arguments must be passed correctly** in the exact order
3. ✅ **All 10 pattern matching rules must be identical** in logic and order
4. ✅ **Line 52 must be preserved verbatim** in 100% of generated netlists
5. ✅ **Temperature conversion must work** (m40 → -40)
6. ✅ **VID support must function correctly** (18 voltage values)
7. ✅ **Library corner parameters must generate correctly** (Rule 4)
8. ✅ **Output directory structure must match** exactly
9. ✅ **Total netlist count must be correct** (84 pre-layout, 252 post-layout)
10. ✅ **Generated netlists must be bit-identical** for same inputs

**ANY deviation from these criteria indicates a critical bug that MUST be fixed.**

---

## 10. References

### Source Documents
- **COMPREHENSIVE_ANALYSIS.md**: Lines 589-1050 (gen_tb.pl deep dive)
- **TIER2_TESTBENCH_ANALYSIS.md**: archive/source_documents/ (template analysis)
- **Actual Script**: `gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/gen_tb.pl`

### Related Analysis Documents
- **SIMULATION_FLOW_GAPS.md**: How gen_tb.pl fits into overall workflow
- **CORNER_MATRIX_GAPS.md**: PVT matrix structure and coverage
- **CONFIGURATION_GAPS.md**: How arguments are sourced from config files

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: ✅ BASELINE REFERENCE COMPLETE  
**Next Step**: Compare wkpup automation gen_tb.pl against this baseline  
**Critical Finding**: Line 52 preservation mechanism (Rule 4 exception) is THE key to protocol differentiation
