# Fix Implementation Roadmap

## Document Purpose

This document provides a **prioritized sequence** for implementing fixes to reconcile wkpup automation with wkpup2 baseline. It assumes the inconsistency analysis has been completed and deviations have been identified.

**Status**: 📋 IMPLEMENTATION GUIDE  
**Prerequisites**: INCONSISTENCY_ANALYSIS.md completed  
**Approach**: Fix critical errors first, validate incrementally

---

## Fix Implementation Priorities

### Priority Levels

**P0 - Critical** (Breaks Simulation Accuracy)
- Must fix before ANY simulations can be trusted
- Affects scientific correctness
- Examples: gen_tb.pl pattern matching, Line 52 preservation

**P1 - High** (Breaks Workflow Reliability)
- Must fix before production use
- Affects reproducibility and completeness
- Examples: Stage sequencing, PVT matrix gaps

**P2 - Medium** (Improves Consistency)
- Should fix for operational clarity
- Doesn't affect correctness
- Examples: Directory naming, logging format

**P3 - Low** (Documentation)
- Can defer
- Cosmetic improvements
- Examples: Comment style, variable naming

---

## Implementation Sequence

### Phase 1: Testbench Generation Fixes (P0)

**Duration**: 1-2 weeks  
**Risk**: Highest impact - affects all downstream operations  
**Validation**: Bit-identical netlist test

#### Fix 1.1: gen_tb.pl Pattern Matching Rules

**Issue**: Pattern matching rules differ from wkpup2

**Implementation Steps**:
1. Backup current gen_tb.pl
2. Copy wkpup2/auto_pvt/ver03/tb_gen/gen_tb.pl to wkpup
3. Verify 571 lines, 10 rules present
4. Test with known inputs
5. Validate Line 52 preservation

**Validation**:
```bash
# Compare generated netlists
diff wkpup2/TT/typical/typical_85/v1nom/sim_tx.sp \
     wkpup/TT/typical/typical_85/v1nom/sim_tx.sp
# Should be identical
```

**Acceptance Criteria**:
- [ ] All 10 pattern matching rules identical
- [ ] Line 52 preserved in 100% of netlists
- [ ] Generated netlists bit-identical to wkpup2

---

#### Fix 1.2: Argument Passing to gen_tb.pl

**Issue**: gen_tb.pl receives incorrect or incomplete arguments

**Implementation Steps**:
1. Review pvt_loop.sh call to gen_tb.pl
2. Verify all 44 arguments passed in correct order
3. Check argument value sources (read_cfg, read_supply, read_corner)
4. Test with logging to verify actual values

**Validation**:
```bash
# Add debug logging
echo "Args: $@" >> gen_tb_args.log

# Run generation
sh sim_pvt.sh config.cfg gen

# Verify 44 arguments logged
wc -w gen_tb_args.log  # Should be 44 per invocation
```

**Acceptance Criteria**:
- [ ] All 44 arguments passed
- [ ] Argument order matches wkpup2
- [ ] Argument values correct (verified via logging)

---

#### Fix 1.3: VID Support Implementation

**Issue**: VID voltage table not implemented or incorrect

**Implementation Steps**:
1. Verify table_supply_list_ac.csv has VID rows
2. Check read_supply.sh initializes 18 VID values
3. Verify gen_tb.pl receives VID table (args 24-44)
4. Test VID enabled vs disabled scenarios

**Validation**:
```bash
# Test VID enabled
cat > config.cfg <<EOF
vcc_vid:Yes
EOF

sh sim_pvt.sh config.cfg gen

# Check VID voltage used
grep "\.param vc=" FFG/typical/typical_125/v1max/sim_tx.sp
# Should use vccmax_ff_h, not standard vccmax
```

**Acceptance Criteria**:
- [ ] VID table has 18 values
- [ ] VID enabled uses corner/temp-specific voltages
- [ ] VID disabled uses standard voltages

---

### Phase 2: Configuration System Fixes (P0)

**Duration**: 1 week  
**Risk**: High - affects all parameter propagation  
**Validation**: Parameter parsing test

#### Fix 2.1: config.cfg Parsing

**Issue**: Missing or incorrectly parsed parameters

**Implementation Steps**:
1. Verify read_cfg.sh supports all 15 parameters
2. Check colon-separated parsing logic
3. Verify variable export to shell environment
4. Test with missing parameters (default handling)

**Validation**:
```bash
source read_cfg.sh
read_cfg config.cfg

# Verify all 15 variables set
echo "$mode $vcc_lvl $CPU $simulator ..."
# All should have values
```

**Acceptance Criteria**:
- [ ] All 15 parameters supported
- [ ] Parsing logic identical to wkpup2
- [ ] Defaults handled correctly

---

#### Fix 2.2: CSV Table Reading

**Issue**: Voltage or corner tables not read correctly

**Implementation Steps**:
1. Verify table_corner_list.csv exists and is complete
2. Verify table_supply_list*.csv exist for ac/dc/default
3. Check read_corner.sh parsing logic
4. Check read_supply.sh parsing logic
5. Verify CSV rows match wkpup2 exactly

**Validation**:
```bash
source read_supply.sh
read_supply 1p1v vcctx_1800 ac

# Verify voltages loaded
echo "$vccmin $vccnom $vccmax"
# Should match wkpup2 values
```

**Acceptance Criteria**:
- [ ] All CSV tables present and complete
- [ ] Parsing logic matches wkpup2
- [ ] Voltage/corner values correct

---

### Phase 3: PVT Matrix Generation Fixes (P1)

**Duration**: 1 week  
**Risk**: Medium - affects coverage completeness  
**Validation**: Netlist count test

#### Fix 3.1: PVT Loop Structure

**Issue**: Nested loop order or iteration incorrect

**Implementation Steps**:
1. Review pvt_loop.sh loop structure
2. Verify loop order: corner → extraction → temp → voltage
3. Check parallel vs sequential logic
4. Verify directory creation for each iteration

**Validation**:
```bash
# Generate matrix
sh sim_pvt.sh config.cfg gen

# Count netlists
find . -name "sim_tx.sp" | wc -l
# Should be 84 (prelay) or 252 (postlay full)
```

**Acceptance Criteria**:
- [ ] Loop order matches wkpup2
- [ ] Correct total netlist count
- [ ] Directory structure matches

---

#### Fix 3.2: Corner Selection Logic

**Issue**: Wrong corners selected based on configuration

**Implementation Steps**:
1. Verify GS/GF corner toggle works
2. Check postlay_cross_cornerlist selection
3. Test all scenarios (default, full, custom)

**Validation**:
```bash
# Test GS/GF enabled
cat > config.cfg <<EOF
gs/gf_corner:Yes
EOF

# Verify FFG_SSG and SSG_FFG directories created
test -d FFG_SSG && test -d SSG_FFG || echo "FAIL"
```

**Acceptance Criteria**:
- [ ] GS/GF toggle works correctly
- [ ] Cross-extraction corner selection correct
- [ ] Custom corner lists supported

---

### Phase 4: Simulation Workflow Fixes (P1)

**Duration**: 1-2 weeks  
**Risk**: Medium - affects execution reliability  
**Validation**: Complete workflow test

#### Fix 4.1: Stage Sequencing

**Issue**: Stages don't execute in correct order

**Implementation Steps**:
1. Verify sim_pvt.sh calls stages as: gen run ext srt bkp
2. Check stage functions exist and work
3. Verify inter-stage dependencies

**Validation**:
```bash
./runme.sh

# Verify all stages completed
test -f report/creport.txt && \
test -d 00bkp_* && \
echo "PASS"
```

**Acceptance Criteria**:
- [ ] All 6 stages implemented
- [ ] Stage order matches wkpup2
- [ ] Dependencies satisfied

---

#### Fix 4.2: Job Submission (nbjob)

**Issue**: nbjob commands differ from wkpup2

**Implementation Steps**:
1. Compare nbjob command structure
2. Verify target, qslot, class parameters
3. Check CPU and memory allocation
4. Test job submission and tracking

**Validation**:
```bash
# Check nbjob command
grep "nbjob run" runme_func.sh

# Should match:
# nbjob run --target altera_png_normal \
#   --qslot /psg/km/phe/ckt/gen \
#   --class "SLES15&&4G&&8C" \
#   primesim -np 8 -spice sim_tx.sp -o sim_tx
```

**Acceptance Criteria**:
- [ ] nbjob parameters identical to wkpup2
- [ ] Job submission works
- [ ] Resource allocation correct

---

### Phase 5: Data Extraction Fixes (P1)

**Duration**: 1 week  
**Risk**: Low-Medium - affects report accuracy  
**Validation**: Report comparison test

#### Fix 5.1: Measurement Parsing

**Issue**: extract_alt.sh parsing logic differs

**Implementation Steps**:
1. Compare extract_alt.sh with wkpup2
2. Verify .mt0 file parsing
3. Check sweep parameter handling
4. Test with actual .mt0 files

**Validation**:
```bash
# Run extraction
sh sim_pvt.sh config.cfg ext

# Verify extracted data
cat report/raw_data/extracted.csv | wc -l
# Should be 84 (number of simulations)
```

**Acceptance Criteria**:
- [ ] Extraction logic matches wkpup2
- [ ] All measurements parsed correctly
- [ ] Sweep support works

---

### Phase 6: Feature Integration (P2)

**Duration**: 2-3 weeks  
**Risk**: Low - features are additive  
**Validation**: Feature-specific tests

#### Fix 6.1: Web UI Integration

**Issue**: Web UI may bypass correct workflow

**Implementation Steps**:
1. Review UI backend calls
2. Ensure UI uses fixed wkpup2-equivalent scripts
3. Verify no parameter overrides in UI
4. Test selective job execution through UI

**Validation**:
```bash
# Submit job via UI
# Verify generated netlists match batch mode
diff ui_generated/TT/typical/typical_85/v1nom/sim_tx.sp \
     batch_generated/TT/typical/typical_85/v1nom/sim_tx.sp
```

**Acceptance Criteria**:
- [ ] UI calls correct backend scripts
- [ ] No workflow shortcuts
- [ ] Bit-identical output to batch mode

---

### Phase 7: Regression Prevention (P1)

**Duration**: Ongoing  
**Risk**: High if not implemented  
**Validation**: Automated test suite

#### Fix 7.1: Automated Test Suite

**Issue**: No automated validation to prevent regression

**Implementation Steps**:
1. Implement unit tests from VALIDATION_METHODOLOGY.md
2. Create pre-commit hooks
3. Set up nightly builds
4. Generate validation reports

**Validation**:
```bash
# Run test suite
./run_all_tests.sh

# Should output:
# Unit Tests: PASS (X/X)
# Integration Tests: PASS (X/X)
# Regression Tests: PASS (X/X)
```

**Acceptance Criteria**:
- [ ] All test categories implemented
- [ ] Pre-commit hooks active
- [ ] Nightly validation runs
- [ ] Reports generated automatically

---

## Implementation Timeline

```
Week 1-2:   Phase 1 (Testbench Generation)
Week 3:     Phase 2 (Configuration System)
Week 4:     Phase 3 (PVT Matrix)
Week 5-6:   Phase 4 (Simulation Workflow)
Week 7:     Phase 5 (Data Extraction)
Week 8-10:  Phase 6 (Feature Integration)
Ongoing:    Phase 7 (Regression Prevention)
```

**Total Estimated Duration**: 10-12 weeks

---

## Risk Mitigation

### Strategy 1: Incremental Validation

After each phase:
1. Run bit-identical output test
2. Document any remaining deviations
3. Don't proceed until phase passes

### Strategy 2: Parallel Track

- **Track A**: Fix critical errors (P0)
- **Track B**: Build test infrastructure (P1)
- Converge when both complete

### Strategy 3: Rollback Plan

- Keep wkpup2 baseline available
- Version control all changes
- Document rollback procedure

---

## Success Metrics

### Phase Completion Criteria

Each phase complete when:
- [ ] All fixes implemented
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Code reviewed

### Overall Success Criteria

Project complete when:
- [ ] All P0 fixes implemented
- [ ] All P1 fixes implemented
- [ ] Bit-identical output validated
- [ ] Regression tests automated
- [ ] Production approval granted

---

## References

- **INCONSISTENCY_ANALYSIS.md**: Identified deviations
- **VALIDATION_METHODOLOGY.md**: Test procedures
- **REGRESSION_PREVENTION.md**: Automated testing

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: 📋 ROADMAP READY  
**Next Step**: Begin Phase 1 implementation  
**Duration**: 10-12 weeks estimated
