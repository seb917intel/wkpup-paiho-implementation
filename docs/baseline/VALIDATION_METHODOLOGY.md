# Validation Methodology

## Document Purpose

This document defines the **comprehensive testing and validation strategy** to ensure wkpup automation produces scientifically accurate results equivalent to wkpup2 baseline.

**Status**: 📋 VALIDATION FRAMEWORK  
**Scope**: Testbench generation, simulation execution, data extraction, and reporting  
**Acceptance Criteria**: Bit-identical outputs for identical inputs

---

## Executive Summary

### Validation Approach

**Three-Tier Testing Strategy**:

1. **Unit Tests** - Validate individual components (gen_tb.pl, read_cfg.sh, etc.)
2. **Integration Tests** - Validate complete workflow (gen → run → ext → srt → bkp)
3. **Regression Tests** - Prevent backsliding after fixes

**Success Criterion**: **100% bit-identical output** between wkpup and wkpup2 for identical inputs

---

## 1. Unit Test Suite

### Test 1.1: gen_tb.pl Pattern Matching

**Objective**: Verify all 10 pattern matching rules work correctly

**Test Cases**:

#### Test 1.1.1: Temperature Substitution (Rule 1)
```bash
# Input template line
.temp 100

# Test all 4 temperatures
perl gen_tb.pl template.sp TT typical m40 ... > output_m40.sp
perl gen_tb.pl template.sp TT typical 85 ... > output_85.sp
perl gen_tb.pl template.sp TT typical 100 ... > output_100.sp
perl gen_tb.pl template.sp TT typical 125 ... > output_125.sp

# Verify
grep "\.temp" output_m40.sp  # Should be: .temp -40
grep "\.temp" output_85.sp   # Should be: .temp 85
grep "\.temp" output_100.sp  # Should be: .temp 100
grep "\.temp" output_125.sp  # Should be: .temp 125
```

**Pass Criteria**: All 4 temperatures convert correctly

---

#### Test 1.1.2: Line 52 Preservation (Rule 4 Exception)
```bash
# Input template line 52
.lib "weakpullup.lib" enable

# Generate netlist
perl gen_tb.pl template.sp TT typical 85 nom nom nom vcc NA NA \
  0.675 0.75 0.825 ... > output.sp

# Verify Line 52 is unchanged
sed -n '52p' template.sp > template_line52.txt
sed -n '52p' output.sp > output_line52.txt
diff template_line52.txt output_line52.txt

# Should output: (empty - files identical)
```

**Pass Criteria**: Line 52 is bit-identical in template and output

---

#### Test 1.1.3: VID Support (Rule 7)
```bash
# Test VID enabled
perl gen_tb.pl template.sp FFG typical 125 max nom nom vcc NA NA \
  0.675 0.75 0.825 ... \
  Yes \
  0.725 0.765 0.805 0.715 0.755 0.795 \
  0.735 0.775 0.815 0.725 0.765 0.805 \
  0.705 0.745 0.785 0.695 0.735 0.775 > output_vid.sp

# Verify VID voltage used
grep "\.param vc=" output_vid.sp
# Should be: .param vc=0.815  (vccmax_ff_h, not standard vccmax)

# Test VID disabled
perl gen_tb.pl ... No ... > output_no_vid.sp
grep "\.param vc=" output_no_vid.sp
# Should be: .param vc=0.825  (standard vccmax)
```

**Pass Criteria**: VID voltage selection logic works correctly

---

### Test 1.2: Configuration Parsing

**Objective**: Verify read_cfg.sh extracts all 15 parameters correctly

```bash
# Create test config
cat > test_config.cfg <<EOF
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
EOF

# Parse config
source read_cfg.sh
read_cfg test_config.cfg

# Verify all 15 parameters
test "$mode" == "prelay" || echo "FAIL: mode"
test "$vcc_lvl" == "1p1v" || echo "FAIL: vccn"
test "$CPU" == "8" || echo "FAIL: CPU"
test "$simulator" == "primesim" || echo "FAIL: simulator"
# ... test all 15 parameters
```

**Pass Criteria**: All 15 parameters parsed correctly

---

### Test 1.3: PVT Matrix Generation

**Objective**: Verify correct number of netlists generated

```bash
# Test pre-layout (7 corners × 1 extraction × 4 temps × 3 voltages = 84)
cat > config.cfg <<EOF
mode:prelay
gs/gf_corner:No
1st_supply_swp:vcc
2nd_supply_swp:NA
3rd_supply_swp:NA
EOF

# Generate matrix
sh sim_pvt.sh config.cfg gen

# Count netlists
netlist_count=$(find . -name "sim_tx.sp" | wc -l)
test "$netlist_count" -eq 84 || echo "FAIL: Expected 84, got $netlist_count"

# Test post-layout (7 × 3 × 4 × 3 = 252)
cat > config.cfg <<EOF
mode:postlay
gs/gf_corner:No
postlay_cross_cornerlist:full
EOF

sh sim_pvt.sh config.cfg gen
netlist_count=$(find . -name "sim_tx.sp" | wc -l)
test "$netlist_count" -eq 252 || echo "FAIL: Expected 252, got $netlist_count"
```

**Pass Criteria**: Netlist count matches expected value

---

## 2. Integration Test Suite

### Test 2.1: Complete Workflow (End-to-End)

**Objective**: Verify all stages execute correctly in sequence

```bash
# Setup
cp wkpup2_baseline/config.cfg test_config.cfg
cp wkpup2_baseline/template/sim_tx.sp test_template.sp

# Execute full workflow
./runme.sh

# Verify each stage completed
test -d TT/typical/typical_85/v1nom || echo "FAIL: Generation"
test -f TT/typical/typical_85/v1nom/sim_tx.mt0 || echo "FAIL: Simulation"
test -f report/raw_data/extracted.csv || echo "FAIL: Extraction"
test -f report/creport.txt || echo "FAIL: Sorting"
test -d 00bkp_* || echo "FAIL: Backup"
```

**Pass Criteria**: All stages complete successfully, all expected files exist

---

### Test 2.2: Bit-Identical Output Comparison

**Objective**: Verify wkpup produces identical netlists to wkpup2

```bash
# Run wkpup2 baseline
cd wkpup2
./runme.sh
cd ..

# Run wkpup automation
cd wkpup
./runme.sh  # (or equivalent)
cd ..

# Compare all generated netlists
diff -r wkpup2/TT wkpup/TT > diff_output.txt

# Should be empty (no differences)
test ! -s diff_output.txt || echo "FAIL: Netlists differ"

# Compare specific critical lines
for corner in TT FFG SSG FSG SFG FFAG SSAG; do
    for temp in m40 85 100 125; do
        for voltage in v1min v1nom v1max; do
            file1="wkpup2/$corner/typical/typical_$temp/$voltage/sim_tx.sp"
            file2="wkpup/$corner/typical/typical_$temp/$voltage/sim_tx.sp"
            
            # Compare Line 52
            diff <(sed -n '52p' "$file1") <(sed -n '52p' "$file2") \
                || echo "FAIL: Line 52 differs in $corner/$temp/$voltage"
        done
    done
done
```

**Pass Criteria**: All files bit-identical, Line 52 preserved in all netlists

---

### Test 2.3: Numerical Accuracy (Simulation Results)

**Objective**: Verify simulation measurements match

```bash
# Compare .mt0 files (measurement outputs)
for file in $(find wkpup2 -name "sim_tx.mt0"); do
    file2=${file/wkpup2/wkpup}
    
    # Extract numerical values and compare with tolerance
    python3 - <<EOF
import numpy as np

def parse_mt0(filename):
    with open(filename) as f:
        lines = f.readlines()
    # Parse measurement values (line 6 typically)
    values = lines[5].split()
    return [float(v) for v in values]

vals1 = parse_mt0("$file")
vals2 = parse_mt0("$file2")

# Compare with tolerance (1e-15 for numerical precision)
if not np.allclose(vals1, vals2, rtol=1e-15):
    print(f"FAIL: Measurements differ in $file")
    print(f"  wkpup2: {vals1}")
    print(f"  wkpup:  {vals2}")
EOF
done
```

**Pass Criteria**: All measurements within 1e-15 tolerance

---

## 3. Regression Test Suite

### Test 3.1: Line 52 Preservation Regression

**Objective**: Ensure Line 52 preservation never breaks in future changes

```bash
#!/bin/bash
# Save as: test_line52_regression.sh

# Test function
test_line52_preservation() {
    local protocol=$1  # "gpio" or "i3c"
    local expected_param=$2  # "enable" or "enable_i3c"
    
    # Generate netlists
    cd $protocol/1p1v
    sh sim_pvt.sh config.cfg gen
    
    # Check all generated netlists
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
if [ $gpio_result -eq 0 ] && [ $i3c_result -eq 0 ]; then
    echo "PASS: Line 52 preservation regression test"
    exit 0
else
    echo "FAIL: Line 52 preservation broken"
    exit 1
fi
```

**Pass Criteria**: All netlists preserve Line 52 correctly for both GPIO and I3C

---

### Test 3.2: PVT Matrix Completeness Regression

**Objective**: Ensure PVT matrix generation never produces incomplete coverage

```bash
#!/bin/bash
# Save as: test_pvt_completeness.sh

test_pvt_completeness() {
    local mode=$1
    local gsgf=$2
    local expected_count=$3
    
    # Configure
    cat > config.cfg <<EOF
mode:$mode
gs/gf_corner:$gsgf
postlay_cross_cornerlist:full
EOF
    
    # Generate
    sh sim_pvt.sh config.cfg gen
    
    # Count
    actual=$(find . -name "sim_tx.sp" | wc -l)
    
    if [ $actual -ne $expected_count ]; then
        echo "FAIL: Expected $expected_count netlists, got $actual"
        return 1
    fi
    
    return 0
}

# Test scenarios
test_pvt_completeness "prelay" "No" 84    # 7 × 1 × 4 × 3
test_pvt_completeness "prelay" "Yes" 108  # 9 × 1 × 4 × 3
test_pvt_completeness "postlay" "No" 252  # 7 × 3 × 4 × 3
test_pvt_completeness "postlay" "Yes" 324 # 9 × 3 × 4 × 3

echo "PASS: PVT matrix completeness regression test"
```

**Pass Criteria**: All scenarios produce correct netlist count

---

## 4. Performance Validation

### Test 4.1: Parallel Generation Performance

**Objective**: Verify parallel generation works correctly and is faster

```bash
# Baseline: Sequential (CPU=1)
cat > config.cfg <<EOF
CPU #:1
EOF

time sh sim_pvt.sh config.cfg gen > /dev/null
seq_time=$?

# Test: Parallel (CPU=8)
cat > config.cfg <<EOF
CPU #:8
EOF

time sh sim_pvt.sh config.cfg gen > /dev/null
par_time=$?

# Verify parallel is faster
if [ $par_time -lt $seq_time ]; then
    echo "PASS: Parallel generation faster ($par_time < $seq_time)"
else
    echo "WARN: Parallel not faster ($par_time >= $seq_time)"
fi

# Verify outputs identical
diff -r sequential_output/ parallel_output/
```

**Pass Criteria**: Parallel mode faster AND produces identical output

---

## 5. Continuous Validation

### Automated Test Execution

**Pre-Commit Hook** (`pre-commit.sh`):
```bash
#!/bin/bash

echo "Running validation tests..."

# Run unit tests
./test_gen_tb_patterns.sh || exit 1
./test_config_parsing.sh || exit 1

# Run regression tests
./test_line52_regression.sh || exit 1
./test_pvt_completeness.sh || exit 1

echo "All tests passed. Commit allowed."
exit 0
```

**Nightly Build** (`nightly_validation.sh`):
```bash
#!/bin/bash

# Full integration test
./test_complete_workflow.sh

# Bit-identical comparison
./test_bitidentical_output.sh

# Generate validation report
./generate_validation_report.sh > validation_report_$(date +%Y%m%d).txt

# Email results
mail -s "WKPUP Validation Report" team@example.com < validation_report_*.txt
```

---

## 6. Acceptance Criteria

### Must-Pass Criteria (Gate for Production)

1. ✅ **All unit tests pass** (gen_tb.pl, config parsing, PVT matrix)
2. ✅ **Complete workflow test passes** (gen → run → ext → srt → bkp)
3. ✅ **Bit-identical output** for identical inputs
4. ✅ **Line 52 preserved** in 100% of generated netlists
5. ✅ **Numerical accuracy** within 1e-15 tolerance
6. ✅ **Regression tests pass** (no backsliding)
7. ✅ **PVT matrix completeness** verified
8. ✅ **All deviations from wkpup2 documented and justified**

### Should-Pass Criteria (Quality Goals)

1. ⚠️ Parallel generation faster than sequential
2. ⚠️ Memory usage reasonable (<4GB per job)
3. ⚠️ All warnings addressed
4. ⚠️ Code style consistent

---

## 7. Validation Report Template

```markdown
# WKPUP Validation Report

## Date: [Date]
## Tester: [Name]
## Version: [commit hash]

---

## Test Summary

| Category | Tests Run | Passed | Failed |
|----------|-----------|--------|--------|
| Unit Tests | X | X | X |
| Integration Tests | X | X | X |
| Regression Tests | X | X | X |
| Performance Tests | X | X | X |
| **TOTAL** | **X** | **X** | **X** |

---

## Critical Results

### Bit-Identical Output
- [ ] PASS - All netlists identical to wkpup2
- [ ] FAIL - Differences found: [list files]

### Line 52 Preservation
- [ ] PASS - Preserved in 100% of netlists
- [ ] FAIL - Broken in [X] netlists

### PVT Matrix Completeness
- [ ] PASS - Correct netlist count
- [ ] FAIL - Expected [X], got [Y]

---

## Detailed Failures

[List each failed test with details]

---

## Recommendation

- [ ] **APPROVED FOR PRODUCTION** - All critical tests passed
- [ ] **CONDITIONAL APPROVAL** - Minor issues, acceptable risk
- [ ] **NOT APPROVED** - Critical failures must be fixed
```

---

## 8. References

- **TESTBENCH_GENERATION_GAPS.md**: gen_tb.pl baseline
- **SIMULATION_FLOW_GAPS.md**: Workflow baseline
- **CORNER_MATRIX_GAPS.md**: PVT matrix baseline
- **CONFIGURATION_GAPS.md**: Config system baseline
- **REFERENCE_RESULTS.md**: Expected outputs from wkpup2
- **TEST_CASES.md**: Additional test scenarios

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: 📋 VALIDATION FRAMEWORK READY  
**Next Step**: Implement automated test suite using this methodology  
**Critical Success**: 100% bit-identical output for identical inputs
