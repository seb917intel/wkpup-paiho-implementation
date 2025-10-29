# Inconsistency Analysis Framework

## Document Purpose

This document provides a **framework and template** for conducting systematic comparison between the wkpup automation system and the wkpup2 baseline. It consolidates findings from the detailed baseline reference documents and provides a structured approach for gap analysis.

**Status**: 📋 ANALYSIS FRAMEWORK  
**Prerequisites**: Read all *_GAPS.md baseline reference documents first  
**Output**: Detailed inconsistency report when wkpup automation becomes available

---

## Executive Summary

### Comparison Strategy

The wkpup2 baseline has been thoroughly documented across four critical areas:

1. **Testbench Generation** (TESTBENCH_GENERATION_GAPS.md)
2. **Simulation Workflow** (SIMULATION_FLOW_GAPS.md)
3. **PVT Corner Matrix** (CORNER_MATRIX_GAPS.md)
4. **Configuration System** (CONFIGURATION_GAPS.md)

**Next Step**: When wkpup automation system files become available, perform systematic comparison in each area and document ALL deviations.

---

## 1. Testbench Generation Comparison

### Critical Files to Compare

**wkpup2 Baseline**:
```
gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/gen_tb.pl
```

**wkpup Automation** (to be located):
```
[Path TBD - search for gen_tb.pl in wkpup automation]
```

### Comparison Checklist

- [ ] **File Size**: Verify gen_tb.pl is exactly 571 lines in both
- [ ] **Pattern Matching Rules**: Verify all 10 rules are present and identical
- [ ] **Rule Order**: Verify rules execute in same sequence (critical for precedence)
- [ ] **Argument Count**: Verify 44 arguments are passed in correct order
- [ ] **Line 52 Preservation**: Verify "weakpullup.lib" does NOT match Rule 4 pattern
- [ ] **Temperature Conversion**: Verify m40 → -40 conversion works
- [ ] **VID Support Logic**: Verify 18-value VID table implementation
- [ ] **Library Corner Parameters**: Verify Rule 4 pattern `(.+)_lib.lib(.+)`
- [ ] **VSSH Formula**: Verify Rule 6 formula for substrate voltage
- [ ] **Supply Configuration Logic**: Verify 1/2/3 supply handling

### Deviation Template

For each deviation found, document using this template:

```markdown
### Deviation #: [Short Name]

**Component**: gen_tb.pl
**Location**: Line [X] in wkpup vs Line [Y] in wkpup2
**Severity**: [Critical / High / Medium / Low]

**wkpup2 Baseline (CORRECT)**:
```
[Code or behavior from wkpup2]
```

**wkpup Automation (INCORRECT)**:
```
[Code or behavior from wkpup]
```

**Impact**:
- [ ] Breaks Line 52 preservation
- [ ] Incorrect parameter substitution
- [ ] Wrong corner definitions
- [ ] Other: [describe]

**Root Cause**: [Why the deviation exists]

**Fix Required**: [Specific changes needed]

**Validation Test**: [How to verify the fix]
```

---

## 2. Simulation Workflow Comparison

### Critical Files to Compare

**wkpup2 Baseline**:
```
gpio/1p1v/runme.sh
gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/sim_pvt.sh
gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/pvt_loop.sh
```

**wkpup Automation** (to be located):
```
[Search for equivalent orchestration scripts]
```

### Comparison Checklist

- [ ] **Entry Point**: Verify equivalent of runme.sh exists
- [ ] **Stage Sequence**: Verify stages execute as gen → run → ext → srt → bkp
- [ ] **Library Sourcing**: Verify all required libraries are sourced
- [ ] **PVT Loop Structure**: Verify nested loop order: corner → extraction → temp → voltage
- [ ] **nbjob Commands**: Verify job submission parameters match
- [ ] **Error Handling**: Verify `set -e`, trap handlers exist
- [ ] **Validation Checks**: Verify netlist count validation exists
- [ ] **Parallel Execution**: Verify CPU>1 triggers parallel generation
- [ ] **Extraction Scripts**: Verify extract_alt.sh vs extract.sh selection
- [ ] **Report Generation**: Verify creport.txt generation logic

---

## 3. PVT Corner Matrix Comparison

### Critical Files to Compare

**wkpup2 Baseline**:
```
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/table_corner_list.csv
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/table_supply_list_ac.csv
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/read_corner.sh
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/read_supply.sh
```

**wkpup Automation** (to be located):
```
[Search for corner and voltage configuration files]
```

### Comparison Checklist

- [ ] **Corner Definitions**: Verify table_corner_list.csv has all 9 corners
- [ ] **Corner Selection Logic**: Verify read_corner.sh logic matches
- [ ] **Voltage Tables**: Verify all voltage rails defined in CSV
- [ ] **Voltage Selection**: Verify condition (func/perf/htol/hvqk) logic
- [ ] **VID Table**: Verify 18 VID voltage values exist
- [ ] **Temperature List**: Verify m40, 85, 100, 125 are used
- [ ] **Extraction Corners**: Verify typical/cworst/cbest defined
- [ ] **Matrix Calculation**: Verify total netlist count is correct
- [ ] **Directory Structure**: Verify corner/extraction/temp/voltage hierarchy

---

## 4. Configuration System Comparison

### Critical Files to Compare

**wkpup2 Baseline**:
```
gpio/1p1v/config.cfg
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/read_cfg.sh
```

**wkpup Automation** (to be located):
```
[Search for configuration files]
```

### Comparison Checklist

- [ ] **Parameter Count**: Verify all 15 parameters are supported
- [ ] **Parameter Names**: Verify names match exactly (case-sensitive)
- [ ] **Parsing Logic**: Verify colon-separated format is used
- [ ] **Variable Export**: Verify all variables are exported globally
- [ ] **Default Handling**: Verify defaults for missing parameters
- [ ] **Column 3 Support**: Verify custom corner list support

---

## 5. Integration Points Comparison

### Critical Integration to Verify

#### Integration 1: config.cfg → read_cfg.sh → gen_tb.pl

**Data Flow**:
```
config.cfg parameters
  ↓
read_cfg.sh (parse)
  ↓
read_supply.sh (load voltages)
  ↓
read_corner.sh (load corners)
  ↓
pvt_loop.sh (generate matrix)
  ↓
gen_tb.pl (create netlists with 44 arguments)
```

**Verification**:
- [ ] All 15 config parameters reach gen_tb.pl correctly
- [ ] Voltage values from CSV match gen_tb.pl arguments
- [ ] Corner lists affect PVT loop correctly
- [ ] VID flag controls VID table usage

#### Integration 2: gen_tb.pl → Simulation → Extraction

**Data Flow**:
```
gen_tb.pl output (sim_tx.sp)
  ↓
nbjob submission (primesim/finesim)
  ↓
sim_tx.mt0 (measurement file)
  ↓
extract_alt.sh (parse measurements)
  ↓
report.txt (extracted data)
```

**Verification**:
- [ ] Generated netlists are valid SPICE
- [ ] Line 52 preserved correctly
- [ ] Simulator processes netlist successfully
- [ ] Measurements extracted correctly

---

## 6. Feature Preservation Assessment

### wkpup Automation Advanced Features

When comparing, also assess how wkpup automation's advanced features integrate:

#### Feature 1: Web UI (main_tornado.py)

**Questions**:
- Does Web UI call the same backend scripts as wkpup2?
- Are there any UI-driven parameter overrides?
- Does UI selection mechanism use identical gen_tb.pl?

**Validation**:
- [ ] UI-triggered simulations use wkpup2-equivalent scripts
- [ ] No shortcuts or parameter modifications in UI layer
- [ ] Selected jobs produce identical output to full runs

#### Feature 2: Database Tracking

**Questions**:
- Does database store accurate workflow metadata?
- Are there any database-driven parameter changes?
- Does database enforce workflow correctness?

**Validation**:
- [ ] Database records wkpup2-compliant workflows
- [ ] No database logic that bypasses proper workflow
- [ ] Data integrity maintained with correct backend

#### Feature 3: Selective Job Execution

**Questions**:
- How does job selection mechanism work?
- Does it skip any generation steps?
- Are selected jobs bit-identical to full-run equivalents?

**Validation**:
- [ ] Selection works within wkpup2 PVT matrix framework
- [ ] Selected jobs use identical gen_tb.pl logic
- [ ] No corner-specific shortcuts

---

## 7. Bit-Identical Output Validation

### Final Validation Test

**Objective**: Prove wkpup automation produces identical results to wkpup2

**Test Procedure**:
1. Create identical config.cfg for both systems
2. Run both systems with same inputs
3. Compare all generated files

**Expected Results**:
```bash
# Compare generated netlists
diff -r wkpup2/TT/typical/typical_85/v1nom/sim_tx.sp \
        wkpup/TT/typical/typical_85/v1nom/sim_tx.sp
# Should output: (empty - files are identical)

# Compare all netlists
find wkpup2 -name "sim_tx.sp" | while read f; do
    f2=${f/wkpup2/wkpup}
    diff "$f" "$f2" || echo "DIFF: $f"
done
# Should output: (nothing - all files identical)
```

**Success Criteria**:
- ✅ All generated netlists are bit-identical
- ✅ Line 52 preserved in 100% of netlists
- ✅ Directory structure matches exactly
- ✅ Netlist count matches exactly

---

## 8. Deviation Severity Classification

### Critical (Must Fix Immediately)

**Definition**: Deviation causes incorrect simulation results

**Examples**:
- gen_tb.pl pattern matching differs
- Line 52 not preserved
- Wrong PVT matrix generated
- Missing or extra corners
- Incorrect voltage values

**Impact**: **Simulation results are scientifically invalid**

---

### High (Fix Before Production)

**Definition**: Deviation affects workflow reliability or completeness

**Examples**:
- Stage sequence differs
- Missing validation checks
- Incorrect error handling
- Wrong nbjob parameters
- Incomplete backup creation

**Impact**: **Simulations may fail or results may be unreliable**

---

### Medium (Fix for Consistency)

**Definition**: Deviation doesn't affect correctness but causes confusion

**Examples**:
- Different directory naming
- Different file organization
- Different logging format
- Non-critical parameter names differ

**Impact**: **Operational confusion, but results are correct**

---

### Low (Document Only)

**Definition**: Benign differences that don't affect operation

**Examples**:
- Comment differences
- Whitespace changes
- Variable naming (if logic identical)
- Debug output format

**Impact**: **No impact on functionality**

---

## 9. Report Template

When wkpup automation files become available, use this template:

```markdown
# WKPUP Automation Inconsistency Analysis Report

## Date: [Date]
## Analyzer: [Name]
## wkpup2 Version: [commit hash]
## wkpup Automation Version: [commit hash or path]

---

## Executive Summary

**Total Deviations Found**: [X]
- Critical: [X]
- High: [X]
- Medium: [X]
- Low: [X]

**Recommendation**: [PASS / FAIL / CONDITIONAL PASS]

---

## Component 1: Testbench Generation

### Files Compared
- wkpup2: [path]
- wkpup: [path]

### Deviations Found: [X]

[Use deviation template for each finding]

---

## Component 2: Simulation Workflow

[Repeat structure]

---

## Component 3: PVT Corner Matrix

[Repeat structure]

---

## Component 4: Configuration System

[Repeat structure]

---

## Validation Test Results

[Document bit-identical output test results]

---

## Recommendations

1. [Priority 1 fixes]
2. [Priority 2 fixes]
3. [Documentation updates]
```

---

## 10. References

### Baseline Reference Documents (Read These First)
- **TESTBENCH_GENERATION_GAPS.md**: gen_tb.pl complete analysis
- **SIMULATION_FLOW_GAPS.md**: 6-stage workflow details
- **CORNER_MATRIX_GAPS.md**: PVT matrix structure
- **CONFIGURATION_GAPS.md**: 15-parameter system

### Next Steps Documents
- **VALIDATION_METHODOLOGY.md**: Test strategy
- **FIX_ROADMAP.md**: Implementation sequence
- **CUSTOM_PVT_FEASIBILITY.md**: Extensibility analysis

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: 📋 FRAMEWORK READY  
**Next Step**: Apply this framework when wkpup automation files become available  
**Expected Output**: Detailed inconsistency report with all deviations classified and documented
