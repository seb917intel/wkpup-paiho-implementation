# Custom PVT Feasibility Analysis

## Document Purpose

This document evaluates the **extensibility** of the wkpup2 framework for supporting custom Process-Voltage-Temperature (PVT) corners beyond the standard definitions. Based on comprehensive analysis of the implementation, it provides clear guidance on what can and cannot be customized.

**Status**: 📊 FEASIBILITY ASSESSMENT  
**Source**: COMPREHENSIVE_ANALYSIS.md and wkpup2 architecture analysis  
**Scope**: Custom corners, voltages, temperatures, and matrix expansion

---

## Executive Summary

### Can Users Customize PVT Corners?

| Customization Type | Feasibility | Effort | Constraints |
|-------------------|-------------|--------|-------------|
| **Add New Silicon Corners** | ✅ YES | Low | Must update CSV |
| **Add New Voltage Points** | ✅ YES | Low | Must update CSV |
| **Add New Temperature Points** | ✅ YES | Medium | Must update code |
| **Add New Extraction Corners** | ⚠️ LIMITED | High | Library-dependent |
| **Expand PVT Matrix (e.g., 200+ sims)** | ✅ YES | Low | Performance impact |
| **Custom Corner Naming** | ✅ YES | Low | Must be consistent |

**Overall Assessment**: **Framework is HIGHLY EXTENSIBLE** with proper configuration

---

## 1. Custom Silicon Corner Support

### Question: Can users add new silicon corners beyond TT, FFG, SSG, FSG, SFG, FFAG, SSAG?

**Answer**: ✅ **YES, easily customizable**

### How to Add Custom Corners

**Step 1: Update table_corner_list.csv**

```csv
type,extraction,corner list
full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG CUSTOM1 CUSTOM2
```

**Step 2: Verify gen_tb.pl Compatibility**

gen_tb.pl treats corner names as **string parameters**, no hardcoded logic:

```perl
$si_corner  # Arg 2: Any string works (TT, FFG, CUSTOM1, etc.)

# Used in pattern matching (Rule 2):
print "$1\DP_HSPICE_MODEL\" $si_corner\n";
# Output: .lib "$DP_HSPICE_MODEL" CUSTOM1
```

**No code changes needed** - corner name is a pass-through parameter

### VID Corner Mapping Limitation

**Issue**: VID support only maps to tt/ff/ss categories

```perl
# gen_tb.pl Lines 47-63
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

**Solution**: Add custom corner to appropriate category

```perl
# Modified gen_tb.pl to support CUSTOM1 corner
elsif ($si_corner eq "FFG" || $si_corner eq "FFG_SSG" || 
       $si_corner eq "FFAG" || $si_corner eq "CUSTOM1") {
    $vcc_vid_corner = "ff";
}
```

### Library Support Requirement

**Critical Constraint**: HSPICE library must support the corner

```spice
# Generated netlist will have:
.lib "$DP_HSPICE_MODEL" CUSTOM1
```

**User must ensure**:
- Library file defines "CUSTOM1" section
- Transistor models exist for CUSTOM1
- Otherwise, simulation will fail

---

## 2. Custom Voltage Point Support

### Question: Can users add voltage points beyond min/nom/max?

**Answer**: ✅ **YES, but requires architectural change**

### Current Limitation

**wkpup2 is hardcoded to 3 voltage points**:
```bash
# pvt_loop.sh
voltage_list="v1min v1nom v1max"  # Only 3 values
```

### How to Add Custom Voltage Points

**Option 1: Add Fourth Voltage Point (e.g., v1ultra)**

**Step 1: Update pvt_loop.sh**

```bash
# Modified voltage list
voltage_list="v1min v1nom v1max v1ultra"
```

**Step 2: Update table_supply_list_ac.csv**

```csv
rail,func_min,perf_min,nom,perf_max,func_max,htol,hvqk,ultra
vcc,0.68,0.69,0.78,0.88,0.89,0.945,1.6,0.95
```

**Step 3: Update read_supply.sh**

```bash
# Add ultra voltage extraction
if [ "$condition" == "ultra" ]; then
    vccmin=$col2
    vccnom=$col4
    vccmax=$col9  # New column
fi
```

**Step 4: Test**

```bash
# Generate matrix
sh sim_pvt.sh config.cfg gen

# Count netlists
find . -name "sim_tx.sp" | wc -l
# Expected: 7 × 1 × 4 × 4 = 112 (was 84)
```

**Effort**: Medium (requires code changes to pvt_loop.sh, read_supply.sh)

---

### Option 2: Continuous Voltage Sweep (Advanced)

**Use Case**: Sweep VCC from 0.68V to 0.89V in 0.01V steps

**Approach**: Use .alter in SPICE netlist

```spice
* Base netlist
.param vc=0.68

* Sweep from 0.68 to 0.89 in 0.01V steps
.alter
.param vc=0.69
.alter
.param vc=0.70
... (21 alter points)
.alter
.param vc=0.89
```

**Implementation**:
- Modify gen_tb.pl to add .alter statements
- Use extract_alt.sh (already supports multi-sweep)
- Single netlist with 21 sweep points instead of 21 netlists

**Effort**: High (requires gen_tb.pl modification)

---

## 3. Custom Temperature Point Support

### Question: Can users add temperatures beyond m40, 85, 100, 125?

**Answer**: ✅ **YES, relatively easy**

### How to Add Custom Temperatures

**Step 1: Update pvt_loop.sh**

```bash
# Modified temperature list
temp_list="m40 0 25 85 100 125 150"  # Added 0, 25, 150
```

**Step 2: Update gen_tb.pl Temperature Conversion**

```perl
# gen_tb.pl Lines 66-71 - ADD new mappings
if ($temperature eq "m40") { $temp_num = "-40"; }
elsif ($temperature eq "0") { $temp_num = "0"; }      # NEW
elsif ($temperature eq "25") { $temp_num = "25"; }    # NEW
elsif ($temperature eq "85") { $temp_num = "85"; }
elsif ($temperature eq "100") { $temp_num = "100"; }
elsif ($temperature eq "125") { $temp_num = "125"; }
elsif ($temperature eq "150") { $temp_num = "150"; }  # NEW
```

**Step 3: VID Temperature Handling (Optional)**

```perl
# If VID enabled, decide if new temps are hot/cold
if ($temperature eq "0") { 
    # Use cold VID table (vcc*_c)
}
elsif ($temperature eq "150") { 
    # Use hot VID table (vcc*_h)
}
```

**Step 4: Test**

```bash
# Generate matrix
sh sim_pvt.sh config.cfg gen

# Count netlists
find . -name "sim_tx.sp" | wc -l
# Expected: 7 × 1 × 7 × 3 = 147 (was 84)
```

**Effort**: Low-Medium (straightforward code addition)

---

## 4. Custom Extraction Corner Support

### Question: Can users add extraction corners beyond typical/cworst/cbest?

**Answer**: ⚠️ **LIMITED - Depends on parasitic extraction**

### Constraint: Parasitic Extraction Files

**Extraction corners require .spf files**:

```spice
# Template uses:
.inc "layout_tparam_typical.spf"
.inc "layout_tparam_cworst_CCworst_T.spf"
.inc "layout_tparam_cbest_CCbest_T.spf"

# gen_tb.pl Rule 3 substitutes:
.inc "layout_tparam_$ex_corner.spf"
```

**To add CUSTOM_EX extraction corner**:
1. Parasitic extraction tool must generate `layout_tparam_CUSTOM_EX.spf`
2. Update table_corner_list.csv:
   ```csv
   cross_custom,typical cworst_CCworst_T cbest_CCbest_T CUSTOM_EX,TT FSG SFG
   ```
3. Update read_corner.sh to handle CUSTOM_EX

**Feasibility**: Depends on extraction tool support

**Effort**: High (requires tool integration)

---

## 5. PVT Matrix Expansion Analysis

### Question: Will framework handle 200+ simulations?

**Answer**: ✅ **YES, no fundamental limits**

### Performance Analysis

**Current Matrix Sizes**:
- Pre-layout: 84 netlists
- Post-layout: 252 netlists
- Post-layout + GS/GF: 324 netlists

**Hypothetical Large Matrix**:
- 10 corners × 5 temps × 4 voltages = 200 netlists (pre-layout)
- 10 corners × 3 extractions × 5 temps × 4 voltages = 600 netlists (post-layout)

### Component Analysis

#### gen_tb.pl Scalability

**No array size limits** - streams data line-by-line:

```perl
while (<INFILE>) {
    # Process each line independently
    # No arrays that grow with matrix size
}
```

**Conclusion**: ✅ Can handle unlimited netlists

---

#### pvt_loop.sh Scalability

**Nested loops are dynamic**:

```bash
for si_corner in $si_corner_list; do      # 10 iterations OK
    for ex_corner in $ex_corner_list; do  # 3 iterations OK
        for temp in $temp_list; do        # 5 iterations OK
            for voltage in $voltage_list; do  # 4 iterations OK
                # 10 × 3 × 5 × 4 = 600 iterations
            done
        done
    done
done
```

**Conclusion**: ✅ Can handle any matrix size

---

#### Parallel Generation Performance

**With CPU=8**:

```bash
# 600 netlists / 8 CPUs = 75 iterations per CPU
# Generation time: ~15-30 seconds (estimated)
```

**With CPU=32**:

```bash
# 600 netlists / 32 CPUs = 19 iterations per CPU
# Generation time: ~5-10 seconds (estimated)
```

**Conclusion**: ✅ Performance scales with CPU count

---

#### Storage Requirements

**Per Netlist** (sim_tx.sp): ~10 KB

**600 Netlists**: 600 × 10 KB = 6 MB (negligible)

**With Simulation Outputs**:
- .mt0 files: 600 × 5 KB = 3 MB
- .log files: 600 × 50 KB = 30 MB
- .fsdb files: 600 × 500 KB = 300 MB

**Total**: ~350 MB for 600 simulations (acceptable)

**Conclusion**: ✅ Storage is not a constraint

---

#### Simulation Queue Time

**Cluster Job Submission**:

```bash
# 600 jobs submitted via nbjob
# Assuming queue has 100 slots available
# Queue time: 600 / 100 = 6 batches
# Total time: 6 × (job runtime) ≈ 6-12 hours
```

**Conclusion**: ⚠️ Time increases linearly with matrix size

---

## 6. Custom Corner Naming Conventions

### Question: Can users use custom corner names?

**Answer**: ✅ **YES, with consistency requirements**

### Naming Flexibility

**gen_tb.pl doesn't validate corner names** - any string works:

```bash
# Valid corner names:
TT
FFG
MY_CUSTOM_CORNER
corner_123
fast_nmos_slow_pmos
```

**Requirements**:
1. No spaces in corner names (shell variable compatibility)
2. No special characters ($, *, ?, etc.)
3. Consistent across CSV files and library definitions

### Best Practices

**Recommended Naming**:
- Use uppercase for silicon corners (TT, FFG, CUSTOM)
- Use descriptive names (FAST_NMOS_SLOW_PMOS better than FSG2)
- Document custom corners in README

**Example**:
```csv
# table_corner_list.csv
type,extraction,corner list
full_custom,typical,TT FAST_ALL SLOW_ALL MIXED_SPATIAL EXTREME_TEMP
```

---

## 7. Constraints and Limitations

### Hard Constraints (Cannot Change Without Major Rework)

1. **Supply Count Limit**: Max 3 supplies (vcc, vcctx, vccn)
   - Hardcoded in gen_tb.pl (args 5-10)
   - Expanding requires gen_tb.pl rewrite

2. **VID Corner Categories**: Only tt/ff/ss supported
   - Would need to add new VID tables for custom categories

3. **Extraction File Format**: Must be .spf
   - gen_tb.pl Pattern 3 expects `_tparam_*.spf`

### Soft Constraints (Can Change With Effort)

1. **Voltage Points**: Currently 3 (min/nom/max)
   - Medium effort to add more

2. **Temperature List**: Currently 4 points
   - Low effort to add more

3. **Directory Naming**: Follows pattern `corner/extraction/extraction_temp/voltage/`
   - Would break scripts if changed

---

## 8. Recommended Customization Workflow

### Safe Customization Process

**Step 1: Plan Custom Matrix**
```
Corners: TT, FFG, SSG, CUSTOM1, CUSTOM2 (5 total)
Temps: m40, 25, 85, 125 (4 total)
Voltages: min, nom, max (3 total)
Total: 5 × 1 × 4 × 3 = 60 netlists
```

**Step 2: Update CSV Files**
```csv
# table_corner_list.csv
full_custom,typical,TT FFG SSG CUSTOM1 CUSTOM2
```

**Step 3: Update Code (if needed)**
```bash
# gen_tb.pl - add VID mapping for CUSTOM1
elsif ($si_corner eq "CUSTOM1") {
    $vcc_vid_corner = "ff";  # Treat as fast corner
}
```

**Step 4: Validate**
```bash
# Generate test matrix
sh sim_pvt.sh config.cfg gen

# Count netlists
find . -name "sim_tx.sp" | wc -l
# Should be 60

# Check corner directories
ls -d */
# Should see: TT/ FFG/ SSG/ CUSTOM1/ CUSTOM2/
```

**Step 5: Verify Library Support**
```bash
# Test one custom corner simulation
cd CUSTOM1/typical/typical_85/v1nom
primesim -spice sim_tx.sp -o sim_tx

# If error "CUSTOM1 not found in library"
# → Update HSPICE library to define CUSTOM1
```

---

## 9. Future Extensibility Recommendations

### Enhancements for Better Customization

**Recommendation 1: Parameterize Voltage Points**

**Current**: Hardcoded to min/nom/max

**Proposed**: Read from CSV

```csv
# table_voltage_points.csv
point_name,point_value
v1min,func_min
v1nom,nom
v1max,func_max
v1ultra,htol
```

**Benefit**: Add voltage points without code changes

---

**Recommendation 2: Generalize VID Corner Mapping**

**Current**: Hardcoded if-else chain

**Proposed**: CSV-based mapping

```csv
# table_vid_mapping.csv
si_corner,vid_category
TT,tt
FFG,ff
SSG,ss
CUSTOM1,ff
CUSTOM2,ss
```

**Benefit**: Support arbitrary custom corners

---

**Recommendation 3: Configurable Temperature List**

**Current**: Hardcoded in pvt_loop.sh

**Proposed**: Read from config.cfg

```bash
# config.cfg
temperature_list:m40 25 85 125 150
```

**Benefit**: Add temperatures without script editing

---

## 10. Feasibility Summary

### What Users CAN Do

✅ Add new silicon corners (update CSV)  
✅ Use custom corner names (with library support)  
✅ Expand PVT matrix to 200+ simulations  
✅ Add new temperature points (minor code change)  
✅ Add custom voltage points (moderate code change)  
✅ Select subset of corners (postlay_cross_cornerlist:custom)  

### What Users CANNOT Do (Without Major Rework)

❌ Add 4th supply rail  
❌ Change extraction file format  
❌ Use non-numeric temperatures (e.g., "cold" instead of -40)  
❌ Bypass HSPICE library dependency  

---

## 11. Conclusion

**Overall Assessment**: ✅ **FRAMEWORK IS HIGHLY EXTENSIBLE**

The wkpup2 framework was designed with flexibility in mind:
- Corner names are parameters, not hardcoded
- PVT loops are dynamic
- CSV configuration enables easy expansion
- No fundamental architectural limits on matrix size

**Recommended Next Steps**:
1. Implement CSV-based voltage points
2. Generalize VID corner mapping
3. Make temperature list configurable
4. Document customization procedures

**With these enhancements, users can create custom PVT matrices with minimal code changes.**

---

## References

- **COMPREHENSIVE_ANALYSIS.md**: Complete framework analysis
- **CORNER_MATRIX_GAPS.md**: PVT matrix structure
- **TESTBENCH_GENERATION_GAPS.md**: gen_tb.pl extensibility
- **CONFIGURATION_GAPS.md**: Configuration flexibility

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: ✅ FEASIBILITY ANALYSIS COMPLETE  
**Conclusion**: Framework supports extensive customization  
**Recommendation**: Implement proposed enhancements for even better extensibility
