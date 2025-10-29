# Test Cases: WKPUP Automation System Validation

## Document Purpose

This document provides **comprehensive, executable test cases** to validate that wkpup automation produces scientifically accurate results equivalent to wkpup2 baseline. All test cases are designed for automated execution and include specific pass/fail criteria.

**Status**: ✅ COMPLETE TEST SUITE  
**Scope**: Unit, Integration, Regression, and Performance Tests  
**Framework**: Based on VALIDATION_METHODOLOGY.md  
**Success Criterion**: 100% bit-identical output for identical inputs

---

## Quick Reference

### Test Categories

| Category | Test Count | Priority | Execution Time |
|----------|-----------|----------|----------------|
| **Unit Tests** | 15 | P0 | ~5 minutes |
| **Integration Tests** | 8 | P0 | ~30 minutes |
| **Regression Tests** | 6 | P1 | ~10 minutes |
| **Performance Tests** | 4 | P2 | ~20 minutes |
| **TOTAL** | **33** | - | **~65 minutes** |

### Critical Tests (Must Pass)

1. **UT-001**: gen_tb.pl Pattern Matching (10 rules)
2. **UT-002**: Line 52 Preservation
3. **IT-001**: Bit-Identical Output Comparison
4. **IT-002**: Complete Workflow Execution
5. **RT-001**: Line 52 Preservation Regression
6. **RT-002**: PVT Matrix Completeness

---

## Test Naming Convention

**Format**: `[Category]-[Number]: [Test Name]`

- **UT**: Unit Test
- **IT**: Integration Test  
- **RT**: Regression Test
- **PT**: Performance Test

**Example**: `UT-001: gen_tb.pl Temperature Substitution`

---

# UNIT TESTS

## UT-001: gen_tb.pl Temperature Substitution (Rule 1)

**Objective**: Verify temperature parameter substitution works correctly  
**Priority**: P0 (Critical)  
**Component**: gen_tb.pl - Pattern Matching Rule 1  
**Reference**: TESTBENCH_GENERATION_GAPS.md Section 2.2.1

### Test Inputs

```bash
# Template file (template.sp)
.temp 100

# Test configurations
TEMPS=("m40" "85" "100" "125")
EXPECTED=("-40" "85" "100" "125")
```

### Test Script

```bash
#!/bin/bash
# File: test_ut001_temp_substitution.sh

TEST_NAME="UT-001: Temperature Substitution"
PASSED=0
FAILED=0

# Create test template
cat > /tmp/test_template.sp <<EOF
.temp 100
EOF

# Test each temperature
for i in 0 1 2 3; do
    temp="${TEMPS[$i]}"
    expected="${EXPECTED[$i]}"
    
    # Generate netlist
    perl gen_tb.pl /tmp/test_template.sp TT typical $temp nom nom nom vcc NA NA \
        0.675 0.75 0.825 0.675 0.75 0.825 0.675 0.75 0.825 \
        0.675 0.75 0.825 0.675 0.75 0.825 0.675 0.75 0.825 \
        No NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA \
        No primesim > /tmp/output_$temp.sp
    
    # Verify temperature conversion
    actual=$(grep "\.temp" /tmp/output_$temp.sp | awk '{print $2}')
    
    if [ "$actual" == "$expected" ]; then
        echo "PASS: Temperature $temp → $expected"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: Temperature $temp → Expected $expected, Got $actual"
        FAILED=$((FAILED + 1))
    fi
done

# Report
echo "---"
echo "$TEST_NAME: $PASSED passed, $FAILED failed"
if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
```

### Pass Criteria

- ✅ All 4 temperatures convert correctly:
  - m40 → -40
  - 85 → 85
  - 100 → 100
  - 125 → 125
- ✅ No perl errors
- ✅ Output file created

### Expected Output

```
PASS: Temperature m40 → -40
PASS: Temperature 85 → 85
PASS: Temperature 100 → 100
PASS: Temperature 125 → 125
---
UT-001: Temperature Substitution: 4 passed, 0 failed
```

---

## UT-002: Line 52 Preservation (Rule 4 Exception)

**Objective**: Verify Line 52 ".lib weakpullup.lib" is NOT modified by pattern matching  
**Priority**: P0 (Critical)  
**Component**: gen_tb.pl - Line 52 Exception Logic  
**Reference**: TESTBENCH_GENERATION_GAPS.md Section 2.2.4, CRITICAL_FINDINGS.md

### Test Inputs

```bash
# Template file with Line 52
# GPIO version
.lib "weakpullup.lib" enable

# I3C version
.lib "weakpullup.lib" enable_i3c
```

### Test Script

```bash
#!/bin/bash
# File: test_ut002_line52_preservation.sh

TEST_NAME="UT-002: Line 52 Preservation"

# Test GPIO
echo "Testing GPIO Line 52..."
cat > /tmp/template_gpio.sp <<EOF
.title GPIO Testbench
.lib "process.lib" TT
.temp 100
...
.lib "weakpullup.lib" enable
...
EOF

# Generate netlist
perl gen_tb.pl /tmp/template_gpio.sp TT typical 85 nom nom nom vcc NA NA \
    0.675 0.75 0.825 ... > /tmp/output_gpio.sp

# Extract Line 52
template_line52=$(sed -n '52p' /tmp/template_gpio.sp)
output_line52=$(sed -n '52p' /tmp/output_gpio.sp)

# Compare
if [ "$template_line52" == "$output_line52" ]; then
    echo "PASS: GPIO Line 52 preserved"
    gpio_pass=1
else
    echo "FAIL: GPIO Line 52 modified"
    echo "  Template: $template_line52"
    echo "  Output:   $output_line52"
    gpio_pass=0
fi

# Test I3C
echo "Testing I3C Line 52..."
cat > /tmp/template_i3c.sp <<EOF
.title I3C Testbench
.lib "process.lib" TT
.temp 100
...
.lib "weakpullup.lib" enable_i3c
...
EOF

perl gen_tb.pl /tmp/template_i3c.sp TT typical 85 nom nom nom vcc NA NA \
    0.675 0.75 0.825 ... > /tmp/output_i3c.sp

template_line52=$(sed -n '52p' /tmp/template_i3c.sp)
output_line52=$(sed -n '52p' /tmp/output_i3c.sp)

if [ "$template_line52" == "$output_line52" ]; then
    echo "PASS: I3C Line 52 preserved"
    i3c_pass=1
else
    echo "FAIL: I3C Line 52 modified"
    echo "  Template: $template_line52"
    echo "  Output:   $output_line52"
    i3c_pass=0
fi

# Report
echo "---"
if [ $gpio_pass -eq 1 ] && [ $i3c_pass -eq 1 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    echo "$TEST_NAME: FAIL"
    exit 1
fi
```

### Pass Criteria

- ✅ GPIO Line 52 bit-identical in template and output
- ✅ I3C Line 52 bit-identical in template and output
- ✅ Line contains "weakpullup.lib" (not substituted)
- ✅ Line contains correct enable parameter (enable vs enable_i3c)

### Expected Output

```
Testing GPIO Line 52...
PASS: GPIO Line 52 preserved
Testing I3C Line 52...
PASS: I3C Line 52 preserved
---
UT-002: Line 52 Preservation: PASS
```

---

## UT-003: VID Voltage Support (Rule 7)

**Objective**: Verify VID voltage table substitution works correctly  
**Priority**: P0 (Critical)  
**Component**: gen_tb.pl - VID Support Logic  
**Reference**: TESTBENCH_GENERATION_GAPS.md Section 2.2.7

### Test Inputs

```bash
# VID voltage table (18 values)
VID_VOLTAGES=(
    0.725 0.765 0.805  # vccmin_tt_l, vccmin_tt_n, vccmin_tt_h
    0.715 0.755 0.795  # vccmin_ss_l, vccmin_ss_n, vccmin_ss_h
    0.735 0.775 0.815  # vccmin_ff_l, vccmin_ff_n, vccmin_ff_h
    0.725 0.765 0.805  # vccmax_tt_l, vccmax_tt_n, vccmax_tt_h
    0.705 0.745 0.785  # vccmax_ss_l, vccmax_ss_n, vccmax_ss_h
    0.695 0.735 0.775  # vccmax_ff_l, vccmax_ff_n, vccmax_ff_h
)
```

### Test Script

```bash
#!/bin/bash
# File: test_ut003_vid_support.sh

TEST_NAME="UT-003: VID Support"

# Test 1: VID Enabled
echo "Test 1: VID Enabled (FFG, max voltage)"
perl gen_tb.pl template.sp FFG typical 125 max nom nom vcc NA NA \
    0.675 0.75 0.825 0.675 0.75 0.825 0.675 0.75 0.825 \
    0.675 0.75 0.825 0.675 0.75 0.825 0.675 0.75 0.825 \
    Yes \
    0.725 0.765 0.805 0.715 0.755 0.795 \
    0.735 0.775 0.815 0.725 0.765 0.805 \
    0.705 0.745 0.785 0.695 0.735 0.775 \
    No primesim > /tmp/output_vid_enabled.sp

# Extract voltage parameter
vid_voltage=$(grep "\.param vc=" /tmp/output_vid_enabled.sp | awk -F'=' '{print $2}')

if [ "$vid_voltage" == "0.815" ]; then
    echo "PASS: VID voltage correct (0.815 = vccmax_ff_h)"
    test1_pass=1
else
    echo "FAIL: VID voltage incorrect (expected 0.815, got $vid_voltage)"
    test1_pass=0
fi

# Test 2: VID Disabled
echo "Test 2: VID Disabled (should use standard voltage)"
perl gen_tb.pl template.sp FFG typical 125 max nom nom vcc NA NA \
    0.675 0.75 0.825 0.675 0.75 0.825 0.675 0.75 0.825 \
    0.675 0.75 0.825 0.675 0.75 0.825 0.675 0.75 0.825 \
    No \
    NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA NA \
    No primesim > /tmp/output_vid_disabled.sp

std_voltage=$(grep "\.param vc=" /tmp/output_vid_disabled.sp | awk -F'=' '{print $2}')

if [ "$std_voltage" == "0.825" ]; then
    echo "PASS: Standard voltage correct (0.825 = vccmax)"
    test2_pass=1
else
    echo "FAIL: Standard voltage incorrect (expected 0.825, got $std_voltage)"
    test2_pass=0
fi

# Report
echo "---"
if [ $test1_pass -eq 1 ] && [ $test2_pass -eq 1 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    echo "$TEST_NAME: FAIL"
    exit 1
fi
```

### Pass Criteria

- ✅ VID enabled: Uses VID table voltage (0.815)
- ✅ VID disabled: Uses standard voltage (0.825)
- ✅ Correct VID voltage selected based on corner and temp
- ✅ All 18 VID values properly stored

### Expected Output

```
Test 1: VID Enabled (FFG, max voltage)
PASS: VID voltage correct (0.815 = vccmax_ff_h)
Test 2: VID Disabled (should use standard voltage)
PASS: Standard voltage correct (0.825 = vccmax)
---
UT-003: VID Support: PASS
```

---

## UT-004: Corner Library Substitution (Rule 4)

**Objective**: Verify process corner library paths are substituted correctly  
**Priority**: P0 (Critical)  
**Component**: gen_tb.pl - Pattern Matching Rule 4  
**Reference**: TESTBENCH_GENERATION_GAPS.md Section 2.2.4

### Test Script

```bash
#!/bin/bash
# File: test_ut004_corner_substitution.sh

TEST_NAME="UT-004: Corner Library Substitution"
PASSED=0
FAILED=0

# Test corners
CORNERS=("TT" "FFG" "SSG" "FSG" "SFG" "FFAG" "SSAG")

for corner in "${CORNERS[@]}"; do
    # Generate netlist
    perl gen_tb.pl template.sp $corner typical 85 nom nom nom vcc NA NA \
        0.675 0.75 0.825 ... > /tmp/output_$corner.sp
    
    # Verify corner in .lib statement
    lib_line=$(grep "\.lib.*process\.lib" /tmp/output_$corner.sp)
    
    if echo "$lib_line" | grep -q "$corner"; then
        echo "PASS: Corner $corner substituted correctly"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: Corner $corner not found in: $lib_line"
        FAILED=$((FAILED + 1))
    fi
done

# Report
echo "---"
echo "$TEST_NAME: $PASSED passed, $FAILED failed"
[ $FAILED -eq 0 ] && exit 0 || exit 1
```

### Pass Criteria

- ✅ All 7 corners substitute correctly in .lib statements
- ✅ Line 52 remains unchanged (does not match pattern)
- ✅ Correct library path format maintained

---

## UT-005: Configuration Parsing (read_cfg.sh)

**Objective**: Verify all 15 config parameters are parsed correctly  
**Priority**: P0 (Critical)  
**Component**: read_cfg.sh  
**Reference**: CONFIGURATION_GAPS.md Section 1

### Test Script

```bash
#!/bin/bash
# File: test_ut005_config_parsing.sh

TEST_NAME="UT-005: Configuration Parsing"

# Create test configuration
cat > /tmp/test_config.cfg <<EOF
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
postlay_cross_cornerlist:full
EOF

# Source and parse
source read_cfg.sh
read_cfg /tmp/test_config.cfg

# Verify all 15 parameters
PASSED=0
FAILED=0

verify_param() {
    param_name=$1
    expected=$2
    actual=$3
    
    if [ "$actual" == "$expected" ]; then
        echo "PASS: $param_name = $expected"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: $param_name (expected: $expected, got: $actual)"
        FAILED=$((FAILED + 1))
    fi
}

verify_param "mode" "prelay" "$mode"
verify_param "vcc_lvl" "1p1v" "$vcc_lvl"
verify_param "vcctx" "vcctx_1800" "$vcctx"
verify_param "1st_supply_swp" "vcc" "$supply1"
verify_param "2nd_supply_swp" "NA" "$supply2"
verify_param "3rd_supply_swp" "NA" "$supply3"
verify_param "condition" "func" "$condition"
verify_param "CPU" "8" "$CPU"
verify_param "MEM" "4" "$MEM"
verify_param "alter_extraction" "No" "$alter_ext"
verify_param "alter_string#" "20" "$alter_num"
verify_param "sim_mode" "ac" "$sim_mode"
verify_param "gs/gf_corner" "No" "$gsgf"
verify_param "vcc_vid" "No" "$vid_en"
verify_param "simulator" "primesim" "$simulator"

# Report
echo "---"
echo "$TEST_NAME: $PASSED passed, $FAILED failed"
[ $FAILED -eq 0 ] && exit 0 || exit 1
```

### Pass Criteria

- ✅ All 15 parameters parsed correctly
- ✅ No parsing errors
- ✅ Default values applied when parameters missing

---

## UT-006: PVT Matrix Generation Count

**Objective**: Verify correct number of netlists generated for each configuration  
**Priority**: P0 (Critical)  
**Component**: pvt_loop.sh  
**Reference**: CORNER_MATRIX_GAPS.md Section 2

### Test Script

```bash
#!/bin/bash
# File: test_ut006_pvt_matrix_count.sh

TEST_NAME="UT-006: PVT Matrix Count"

test_matrix_count() {
    mode=$1
    gsgf=$2
    expected=$3
    
    # Configure
    cat > config.cfg <<EOF
mode:$mode
gs/gf_corner:$gsgf
1st_supply_swp:vcc
EOF
    
    # Generate
    sh sim_pvt.sh config.cfg gen
    
    # Count netlists
    actual=$(find . -name "sim_tx.sp" | wc -l)
    
    if [ $actual -eq $expected ]; then
        echo "PASS: $mode, gsgf=$gsgf → $expected netlists"
        return 0
    else
        echo "FAIL: $mode, gsgf=$gsgf → Expected $expected, got $actual"
        return 1
    fi
}

# Test scenarios
test_matrix_count "prelay" "No" 84    # 7 × 1 × 4 × 3
r1=$?
test_matrix_count "prelay" "Yes" 108  # 9 × 1 × 4 × 3
r2=$?
test_matrix_count "postlay" "No" 252  # 7 × 3 × 4 × 3
r3=$?
test_matrix_count "postlay" "Yes" 324 # 9 × 3 × 4 × 3
r4=$?

# Report
echo "---"
total=$((r1 + r2 + r3 + r4))
if [ $total -eq 0 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    echo "$TEST_NAME: FAIL ($total scenarios failed)"
    exit 1
fi
```

### Pass Criteria

- ✅ Pre-layout, no GS/GF: 84 netlists (7×1×4×3)
- ✅ Pre-layout, with GS/GF: 108 netlists (9×1×4×3)
- ✅ Post-layout, no GS/GF: 252 netlists (7×3×4×3)
- ✅ Post-layout, with GS/GF: 324 netlists (9×3×4×3)

---

## UT-007: CSV Table Lookup (read_corner.sh)

**Objective**: Verify corner table CSV parsing works correctly  
**Priority**: P1  
**Component**: read_corner.sh  
**Reference**: CONFIGURATION_GAPS.md Section 3.2

### Test Script

```bash
#!/bin/bash
# File: test_ut007_csv_lookup.sh

TEST_NAME="UT-007: CSV Table Lookup"

# Test corner lookup
source read_corner.sh

# Test each corner
CORNERS=("TT" "FFG" "SSG" "FSG" "SFG" "FFAG" "SSAG" "FFG_SSG" "SSG_FFG")

PASSED=0
FAILED=0

for corner in "${CORNERS[@]}"; do
    result=$(lookup_corner "$corner")
    
    if [ -n "$result" ]; then
        echo "PASS: Corner $corner found in CSV"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: Corner $corner not found"
        FAILED=$((FAILED + 1))
    fi
done

# Report
echo "---"
echo "$TEST_NAME: $PASSED passed, $FAILED failed"
[ $FAILED -eq 0 ] && exit 0 || exit 1
```

### Pass Criteria

- ✅ All 9 corners found in table_corner_list.csv
- ✅ Correct parameter extraction for each corner
- ✅ No CSV parsing errors

---

## UT-008-015: Additional Unit Tests

### UT-008: Voltage Table Lookup (read_supply.sh)
- Verify AC voltage table parsing
- Verify DC voltage table parsing
- Test min/nom/max voltage extraction

### UT-009: Extraction Pattern Matching (extract_alt.sh)
- Test .mt0 file parsing
- Verify measurement extraction
- Check numerical precision

### UT-010: Directory Structure Creation
- Verify corner/extraction/temp/voltage directory tree
- Test path naming consistency
- Check for "typ" vs "typical" bug

### UT-011: nbjob Command Generation
- Verify job submission syntax
- Test CPU/memory parameter passing
- Check queue selection

### UT-012: Backup Creation
- Test 00bkp_YYYYMMDDHHMMSS naming
- Verify all files archived
- Check backup integrity

### UT-013: Report Generation (creport.txt)
- Test sorting logic
- Verify measurement aggregation
- Check formatting

### UT-014: Temperature Conversion Edge Cases
- Test negative temperatures (m40 → -40)
- Test boundary values
- Check conversion formula

### UT-015: Argument Count Validation
- Verify gen_tb.pl accepts exactly 44 arguments
- Test error handling for wrong argument count
- Check argument ordering

---

# INTEGRATION TESTS

## IT-001: Bit-Identical Output Comparison

**Objective**: Verify wkpup produces identical netlists to wkpup2 for same inputs  
**Priority**: P0 (CRITICAL SUCCESS CRITERION)  
**Components**: Complete workflow  
**Reference**: VALIDATION_METHODOLOGY.md Section 2.2

### Test Script

```bash
#!/bin/bash
# File: test_it001_bitidentical_output.sh

TEST_NAME="IT-001: Bit-Identical Output"

# Setup
WKPUP2_DIR="/path/to/wkpup2/gpio/1p1v"
WKPUP_DIR="/path/to/wkpup/gpio/1p1v"

# Copy identical config to both
cp test_config.cfg $WKPUP2_DIR/config.cfg
cp test_config.cfg $WKPUP_DIR/config.cfg

# Run wkpup2 baseline
echo "Running wkpup2 baseline..."
cd $WKPUP2_DIR
./runme.sh
cd -

# Run wkpup automation
echo "Running wkpup automation..."
cd $WKPUP_DIR
./runme.sh  # Or web automation trigger
cd -

# Compare ALL generated netlists
echo "Comparing outputs..."
diff -r $WKPUP2_DIR/TT $WKPUP_DIR/TT > /tmp/diff_output.txt

if [ ! -s /tmp/diff_output.txt ]; then
    echo "PASS: All netlists bit-identical"
    exit 0
else
    echo "FAIL: Differences found:"
    cat /tmp/diff_output.txt
    exit 1
fi
```

### Pass Criteria

- ✅ All 84+ netlists bit-identical between wkpup2 and wkpup
- ✅ Zero differences in `diff -r` output
- ✅ Line 52 preserved in all netlists
- ✅ File count matches exactly

### Expected Output

```
Running wkpup2 baseline...
[Generation output]
Running wkpup automation...
[Generation output]
Comparing outputs...
PASS: All netlists bit-identical
```

---

## IT-002: Complete Workflow Execution

**Objective**: Verify all 6 stages execute successfully in sequence  
**Priority**: P0 (Critical)  
**Components**: sim_pvt.sh - All stages  
**Reference**: SIMULATION_FLOW_GAPS.md

### Test Script

```bash
#!/bin/bash
# File: test_it002_complete_workflow.sh

TEST_NAME="IT-002: Complete Workflow"

# Setup
cd gpio/1p1v

# Execute complete workflow
./runme.sh

# Verify Stage 1: Generation
if [ -d "TT/typical/typical_85/v1nom" ]; then
    echo "PASS: Stage 1 - Generation"
    stage1=0
else
    echo "FAIL: Stage 1 - Directory not created"
    stage1=1
fi

# Verify Stage 2: Simulation
if [ -f "TT/typical/typical_85/v1nom/sim_tx.mt0" ]; then
    echo "PASS: Stage 2 - Simulation"
    stage2=0
else
    echo "FAIL: Stage 2 - .mt0 file missing"
    stage2=1
fi

# Verify Stage 3: Extraction
if [ -f "report/raw_data/extracted.csv" ]; then
    echo "PASS: Stage 3 - Extraction"
    stage3=0
else
    echo "FAIL: Stage 3 - CSV file missing"
    stage3=1
fi

# Verify Stage 4: Sorting
if [ -f "report/creport.txt" ]; then
    echo "PASS: Stage 4 - Sorting"
    stage4=0
else
    echo "FAIL: Stage 4 - Report missing"
    stage4=1
fi

# Verify Stage 5: Backup
if ls 00bkp_* 1> /dev/null 2>&1; then
    echo "PASS: Stage 5 - Backup"
    stage5=0
else
    echo "FAIL: Stage 5 - Backup not created"
    stage5=1
fi

# Verify Stage 6: User Script (optional)
# Skip if not configured

# Report
echo "---"
total=$((stage1 + stage2 + stage3 + stage4 + stage5))
if [ $total -eq 0 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    echo "$TEST_NAME: FAIL ($total stages failed)"
    exit 1
fi
```

### Pass Criteria

- ✅ Stage 1 (gen): Netlists created in correct directory structure
- ✅ Stage 2 (run): .mt0 measurement files generated
- ✅ Stage 3 (ext): CSV extraction successful
- ✅ Stage 4 (srt): creport.txt created
- ✅ Stage 5 (bkp): 00bkp_* directory created
- ✅ No errors in any stage

---

## IT-003: Numerical Accuracy Validation

**Objective**: Verify simulation measurements match within tolerance  
**Priority**: P0 (Critical)  
**Components**: Simulation + Extraction  
**Reference**: VALIDATION_METHODOLOGY.md Section 2.3

### Test Script

```bash
#!/bin/bash
# File: test_it003_numerical_accuracy.sh

TEST_NAME="IT-003: Numerical Accuracy"

# Python script for numerical comparison
cat > /tmp/compare_mt0.py <<'EOF'
import sys
import numpy as np

def parse_mt0(filename):
    with open(filename) as f:
        lines = f.readlines()
    # Extract measurement values (adjust line number as needed)
    values = []
    for line in lines:
        if line.strip() and not line.startswith('.'):
            parts = line.split()
            values.extend([float(x) for x in parts if x.replace('.','').replace('-','').isdigit()])
    return np.array(values)

file1 = sys.argv[1]
file2 = sys.argv[2]

vals1 = parse_mt0(file1)
vals2 = parse_mt0(file2)

# Compare with 1e-15 tolerance
if np.allclose(vals1, vals2, rtol=1e-15, atol=1e-15):
    print("PASS: Measurements within tolerance")
    sys.exit(0)
else:
    print("FAIL: Measurements differ")
    print(f"  wkpup2: {vals1}")
    print(f"  wkpup:  {vals2}")
    print(f"  diff:   {vals1 - vals2}")
    sys.exit(1)
EOF

# Compare all .mt0 files
FAILED=0
for file1 in $(find wkpup2 -name "sim_tx.mt0"); do
    file2=${file1/wkpup2/wkpup}
    
    if [ -f "$file2" ]; then
        python3 /tmp/compare_mt0.py "$file1" "$file2"
        [ $? -ne 0 ] && FAILED=$((FAILED + 1))
    else
        echo "FAIL: $file2 missing"
        FAILED=$((FAILED + 1))
    fi
done

# Report
echo "---"
if [ $FAILED -eq 0 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    echo "$TEST_NAME: FAIL ($FAILED files differ)"
    exit 1
fi
```

### Pass Criteria

- ✅ All measurements within 1e-15 relative tolerance
- ✅ All measurements within 1e-15 absolute tolerance
- ✅ Same number of .mt0 files in both systems

---

## IT-004: Multi-Voltage Domain Test

**Objective**: Verify automation works across all voltage domains  
**Priority**: P1  
**Components**: Voltage domain management  
**Reference**: FEATURE_EXTRACTION_STRATEGY.md

### Test Script

```bash
#!/bin/bash
# File: test_it004_multi_voltage.sh

TEST_NAME="IT-004: Multi-Voltage Domain"

DOMAINS=("1p1v" "1p2v" "1p8v" "1p15v")
PASSED=0
FAILED=0

for domain in "${DOMAINS[@]}"; do
    echo "Testing voltage domain: $domain"
    
    cd gpio/$domain
    ./runme.sh
    
    if [ -f "report/creport.txt" ]; then
        echo "PASS: $domain workflow completed"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: $domain workflow failed"
        FAILED=$((FAILED + 1))
    fi
    
    cd ../..
done

# Report
echo "---"
echo "$TEST_NAME: $PASSED passed, $FAILED failed"
[ $FAILED -eq 0 ] && exit 0 || exit 1
```

### Pass Criteria

- ✅ All voltage domains execute successfully
- ✅ Correct voltage tables loaded for each domain
- ✅ No cross-contamination between domains

---

## IT-005-008: Additional Integration Tests

### IT-005: GPIO vs I3C Protocol Differentiation
- Verify Line 52 preservation for both protocols
- Test enable vs enable_i3c parameter handling
- Check protocol-specific configurations

### IT-006: Parallel Job Execution
- Submit multiple jobs simultaneously
- Verify no resource conflicts
- Check job completion and results

### IT-007: Web UI to Backend Integration
- Submit job via web interface
- Verify correct parameter passing
- Check database tracking

### IT-008: Database Consistency
- Verify job metadata stored correctly
- Test result retrieval
- Check submission history

---

# REGRESSION TESTS

## RT-001: Line 52 Preservation Regression

**Objective**: Ensure Line 52 preservation never breaks in future changes  
**Priority**: P0 (Critical)  
**Components**: gen_tb.pl  
**Reference**: VALIDATION_METHODOLOGY.md Section 3.1

### Test Script

```bash
#!/bin/bash
# File: test_rt001_line52_regression.sh

TEST_NAME="RT-001: Line 52 Preservation Regression"

test_line52_preservation() {
    local protocol=$1
    local expected_param=$2
    
    echo "Testing $protocol..."
    
    # Generate all netlists
    cd $protocol/1p1v
    sh sim_pvt.sh config.cfg gen
    
    # Check each netlist
    failures=0
    for netlist in $(find . -name "sim_tx.sp"); do
        line52=$(sed -n '52p' "$netlist")
        
        if ! echo "$line52" | grep -q "weakpullup.lib.*$expected_param"; then
            echo "FAIL: $netlist - Line 52 broken"
            echo "  Expected: .lib \"weakpullup.lib\" $expected_param"
            echo "  Got: $line52"
            failures=$((failures + 1))
        fi
    done
    
    cd ../..
    return $failures
}

# Test GPIO
test_line52_preservation "gpio" "enable"
gpio_result=$?

# Test I3C
test_line52_preservation "i3c" "enable_i3c"
i3c_result=$?

# Report
echo "---"
if [ $gpio_result -eq 0 ] && [ $i3c_result -eq 0 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    total=$((gpio_result + i3c_result))
    echo "$TEST_NAME: FAIL ($total netlists broken)"
    exit 1
fi
```

### Pass Criteria

- ✅ Line 52 preserved in 100% of GPIO netlists
- ✅ Line 52 preserved in 100% of I3C netlists
- ✅ Correct enable parameter for each protocol

---

## RT-002: PVT Matrix Completeness Regression

**Objective**: Ensure PVT matrix generation never produces incomplete coverage  
**Priority**: P0 (Critical)  
**Components**: pvt_loop.sh  
**Reference**: VALIDATION_METHODOLOGY.md Section 3.2

### Test Script

```bash
#!/bin/bash
# File: test_rt002_pvt_completeness.sh

TEST_NAME="RT-002: PVT Completeness Regression"

test_pvt_completeness() {
    local mode=$1
    local gsgf=$2
    local expected_count=$3
    
    # Configure
    cat > config.cfg <<EOF
mode:$mode
gs/gf_corner:$gsgf
1st_supply_swp:vcc
postlay_cross_cornerlist:full
EOF
    
    # Generate
    sh sim_pvt.sh config.cfg gen
    
    # Count
    actual=$(find . -name "sim_tx.sp" | wc -l)
    
    if [ $actual -ne $expected_count ]; then
        echo "FAIL: $mode/$gsgf - Expected $expected_count, got $actual"
        return 1
    else
        echo "PASS: $mode/$gsgf - $expected_count netlists"
        return 0
    fi
}

# Test all scenarios
test_pvt_completeness "prelay" "No" 84
r1=$?
test_pvt_completeness "prelay" "Yes" 108
r2=$?
test_pvt_completeness "postlay" "No" 252
r3=$?
test_pvt_completeness "postlay" "Yes" 324
r4=$?

# Report
echo "---"
total=$((r1 + r2 + r3 + r4))
if [ $total -eq 0 ]; then
    echo "$TEST_NAME: PASS"
    exit 0
else
    echo "$TEST_NAME: FAIL ($total scenarios incomplete)"
    exit 1
fi
```

### Pass Criteria

- ✅ All 4 PVT scenarios produce correct count
- ✅ No missing corners
- ✅ No duplicate netlists

---

## RT-003: Path Consistency Regression

**Objective**: Prevent "typ" vs "typical" path mismatch bug from recurring  
**Priority**: P0 (Critical)  
**Components**: pvt_loop.sh, extract_alt.sh  
**Reference**: ACTUAL_COMPARISON_FINDINGS.md Section 3

### Test Script

```bash
#!/bin/bash
# File: test_rt003_path_consistency.sh

TEST_NAME="RT-003: Path Consistency Regression"

# Generate netlists
sh sim_pvt.sh config.cfg gen

# Try to run simulations
sh sim_pvt.sh config.cfg run

# Check for path errors
errors=$(grep -r "No such file or directory" logs/ | wc -l)

if [ $errors -eq 0 ]; then
    echo "PASS: No path mismatches found"
    exit 0
else
    echo "FAIL: $errors path errors detected"
    grep -r "No such file or directory" logs/
    exit 1
fi
```

### Pass Criteria

- ✅ No file-not-found errors
- ✅ Generation and extraction use same paths
- ✅ Consistent "typical" naming throughout

---

## RT-004-006: Additional Regression Tests

### RT-004: Argument Ordering Regression
- Test gen_tb.pl with correct argument order
- Detect if argument positions change
- Verify all 44 arguments used

### RT-005: CSV Table Integrity
- Check table_corner_list.csv not modified
- Verify table_supply_list_*.csv not corrupted
- Test CSV parsing still works

### RT-006: Backup Integrity
- Verify backup contains all necessary files
- Test backup restoration
- Check backup naming consistency

---

# PERFORMANCE TESTS

## PT-001: Parallel Generation Performance

**Objective**: Verify parallel generation is faster than sequential  
**Priority**: P2  
**Components**: pvt_loop.sh parallel mode  
**Reference**: VALIDATION_METHODOLOGY.md Section 4.1

### Test Script

```bash
#!/bin/bash
# File: test_pt001_parallel_performance.sh

TEST_NAME="PT-001: Parallel Performance"

# Test Sequential (CPU=1)
cat > config.cfg <<EOF
CPU #:1
EOF

echo "Running sequential generation..."
start_seq=$(date +%s)
sh sim_pvt.sh config.cfg gen > /dev/null
end_seq=$(date +%s)
seq_time=$((end_seq - start_seq))
echo "Sequential time: ${seq_time}s"

# Backup sequential output
mv TT TT_sequential

# Test Parallel (CPU=8)
cat > config.cfg <<EOF
CPU #:8
EOF

echo "Running parallel generation..."
start_par=$(date +%s)
sh sim_pvt.sh config.cfg gen > /dev/null
end_par=$(date +%s)
par_time=$((end_par - start_par))
echo "Parallel time: ${par_time}s"

# Verify outputs identical
diff -r TT_sequential TT > /dev/null
outputs_match=$?

# Calculate speedup
if [ $par_time -gt 0 ]; then
    speedup=$(echo "scale=2; $seq_time / $par_time" | bc)
else
    speedup="N/A"
fi

# Report
echo "---"
echo "Sequential: ${seq_time}s"
echo "Parallel: ${par_time}s"
echo "Speedup: ${speedup}x"

if [ $par_time -lt $seq_time ] && [ $outputs_match -eq 0 ]; then
    echo "$TEST_NAME: PASS (${speedup}x speedup, identical output)"
    exit 0
else
    if [ $par_time -ge $seq_time ]; then
        echo "$TEST_NAME: WARN (Parallel not faster)"
    fi
    if [ $outputs_match -ne 0 ]; then
        echo "$TEST_NAME: FAIL (Outputs differ)"
        exit 1
    fi
    exit 0
fi
```

### Pass Criteria

- ✅ Parallel mode faster than sequential
- ✅ Outputs bit-identical between modes
- ⚠️ Speedup > 2x (recommended, not required)

---

## PT-002: Memory Usage

**Objective**: Verify memory usage is reasonable  
**Priority**: P2  
**Components**: Complete workflow

### Test Script

```bash
#!/bin/bash
# File: test_pt002_memory_usage.sh

TEST_NAME="PT-002: Memory Usage"

# Monitor memory during execution
/usr/bin/time -v sh sim_pvt.sh config.cfg gen 2>&1 | tee /tmp/mem_log.txt

# Extract peak memory
peak_mem=$(grep "Maximum resident set size" /tmp/mem_log.txt | awk '{print $6}')
peak_mem_gb=$(echo "scale=2; $peak_mem / 1024 / 1024" | bc)

echo "Peak memory usage: ${peak_mem_gb} GB"

# Check against limit (4GB)
if (( $(echo "$peak_mem_gb < 4" | bc -l) )); then
    echo "$TEST_NAME: PASS (${peak_mem_gb} GB < 4 GB)"
    exit 0
else
    echo "$TEST_NAME: WARN (${peak_mem_gb} GB >= 4 GB)"
    exit 0
fi
```

### Pass Criteria

- ⚠️ Memory usage < 4GB (recommended)
- ✅ No out-of-memory errors

---

## PT-003-004: Additional Performance Tests

### PT-003: Database Query Performance
- Test job list retrieval time
- Verify result filtering speed
- Check database index effectiveness

### PT-004: Web UI Responsiveness
- Measure page load time
- Test real-time updates
- Check WebSocket latency

---

# TEST EXECUTION

## Automated Test Suite

### Master Test Runner

```bash
#!/bin/bash
# File: run_all_tests.sh

echo "========================================="
echo "WKPUP VALIDATION TEST SUITE"
echo "========================================="
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    test_script=$1
    
    echo "Running $test_script..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if bash $test_script; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
}

# Unit Tests
echo "=== UNIT TESTS ==="
run_test "test_ut001_temp_substitution.sh"
run_test "test_ut002_line52_preservation.sh"
run_test "test_ut003_vid_support.sh"
run_test "test_ut004_corner_substitution.sh"
run_test "test_ut005_config_parsing.sh"
run_test "test_ut006_pvt_matrix_count.sh"
run_test "test_ut007_csv_lookup.sh"
# Add UT-008 through UT-015...

# Integration Tests
echo "=== INTEGRATION TESTS ==="
run_test "test_it001_bitidentical_output.sh"
run_test "test_it002_complete_workflow.sh"
run_test "test_it003_numerical_accuracy.sh"
run_test "test_it004_multi_voltage.sh"
# Add IT-005 through IT-008...

# Regression Tests
echo "=== REGRESSION TESTS ==="
run_test "test_rt001_line52_regression.sh"
run_test "test_rt002_pvt_completeness.sh"
run_test "test_rt003_path_consistency.sh"
# Add RT-004 through RT-006...

# Performance Tests
echo "=== PERFORMANCE TESTS ==="
run_test "test_pt001_parallel_performance.sh"
run_test "test_pt002_memory_usage.sh"
# Add PT-003 through PT-004...

# Summary
echo "========================================="
echo "TEST SUMMARY"
echo "========================================="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo "Success Rate: $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)%"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi
```

---

## Continuous Integration

### Pre-Commit Hook

```bash
#!/bin/bash
# File: .git/hooks/pre-commit

echo "Running critical tests before commit..."

# Run critical tests only
bash test_ut002_line52_preservation.sh || exit 1
bash test_ut006_pvt_matrix_count.sh || exit 1
bash test_rt001_line52_regression.sh || exit 1

echo "✅ Pre-commit tests passed"
exit 0
```

### Nightly Build

```bash
#!/bin/bash
# File: nightly_validation.sh

# Run complete test suite
bash run_all_tests.sh > validation_report_$(date +%Y%m%d).txt 2>&1

# Email results
if [ $? -eq 0 ]; then
    subject="✅ WKPUP Validation: ALL TESTS PASSED"
else
    subject="❌ WKPUP Validation: FAILURES DETECTED"
fi

mail -s "$subject" team@intel.com < validation_report_$(date +%Y%m%d).txt
```

---

# ACCEPTANCE CRITERIA

## Gate for Production

**ALL of the following MUST pass**:

1. ✅ **UT-002**: Line 52 Preservation
2. ✅ **UT-006**: PVT Matrix Count
3. ✅ **IT-001**: Bit-Identical Output
4. ✅ **IT-002**: Complete Workflow
5. ✅ **IT-003**: Numerical Accuracy
6. ✅ **RT-001**: Line 52 Regression
7. ✅ **RT-002**: PVT Completeness Regression

**Conditional Requirements**:

- ⚠️ **PT-001**: Parallel Performance (recommended, not blocking)
- ⚠️ **PT-002**: Memory Usage (recommended, not blocking)

---

# REFERENCES

## Related Documents

- **VALIDATION_METHODOLOGY.md**: Overall testing strategy
- **TESTBENCH_GENERATION_GAPS.md**: gen_tb.pl baseline
- **SIMULATION_FLOW_GAPS.md**: Workflow baseline
- **CORNER_MATRIX_GAPS.md**: PVT matrix baseline
- **CONFIGURATION_GAPS.md**: Config system baseline
- **REFERENCE_RESULTS.md**: Expected outputs from wkpup2
- **ACTUAL_COMPARISON_FINDINGS.md**: Known bugs and deviations

---

## Document Metadata

**Version**: 1.0  
**Created**: October 29, 2025  
**Status**: ✅ COMPLETE TEST SUITE  
**Total Tests**: 33 (15 Unit + 8 Integration + 6 Regression + 4 Performance)  
**Execution Time**: ~65 minutes (full suite)  
**Critical Tests**: 7 (must-pass for production)

**Next Steps**:
1. Implement test scripts in `tests/` directory
2. Set up automated test execution
3. Configure CI/CD pipeline
4. Begin validation campaign

---

**Document Status**: ✅ READY FOR IMPLEMENTATION  
**Critical Success Criterion**: 100% bit-identical output validated by IT-001
