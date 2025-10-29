# Regression Prevention Strategy

## Document Purpose

This document defines the **continuous validation framework** to prevent regression and maintain parity between wkpup automation and wkpup2 baseline after fixes are implemented.

**Status**: 📋 PREVENTION FRAMEWORK  
**Goal**: Ensure wkpup never diverges from wkpup2 again  
**Approach**: Automated testing, pre-commit checks, continuous monitoring

---

## 1. Automated Test Infrastructure

### Test Suite Structure

```
tests/
├── unit/
│   ├── test_gen_tb_patterns.sh          # gen_tb.pl pattern matching
│   ├── test_config_parsing.sh            # config.cfg parsing
│   ├── test_csv_reading.sh               # CSV table reading
│   └── test_voltage_calculation.sh       # VID voltage logic
├── integration/
│   ├── test_complete_workflow.sh         # End-to-end workflow
│   ├── test_pvt_matrix.sh                # PVT matrix generation
│   └── test_bitidentical_output.sh       # Output comparison
├── regression/
│   ├── test_line52_preservation.sh       # Line 52 regression
│   ├── test_corner_coverage.sh           # PVT completeness
│   └── test_parameter_propagation.sh     # Config→gen_tb flow
└── run_all_tests.sh                      # Master test runner
```

---

## 2. Pre-Commit Hooks

### Installation

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running pre-commit validation..."

# Run critical tests
./tests/regression/test_line52_preservation.sh || exit 1
./tests/regression/test_corner_coverage.sh || exit 1
./tests/unit/test_gen_tb_patterns.sh || exit 1

echo "Pre-commit validation passed."
exit 0
```

**Make executable**:
```bash
chmod +x .git/hooks/pre-commit
```

---

### Test Categories for Pre-Commit

**Must-Pass Tests** (block commit if failed):
1. Line 52 preservation
2. gen_tb.pl pattern matching
3. Configuration parsing
4. PVT matrix completeness

**Duration**: < 30 seconds (fast feedback)

---

## 3. Continuous Integration (CI)

### Nightly Build Pipeline

```yaml
# .github/workflows/nightly-validation.yml

name: Nightly WKPUP Validation

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
  workflow_dispatch:      # Manual trigger

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run unit tests
        run: ./tests/unit/run_all_unit_tests.sh
      
      - name: Run integration tests
        run: ./tests/integration/run_all_integration_tests.sh
      
      - name: Run regression tests
        run: ./tests/regression/run_all_regression_tests.sh
      
      - name: Generate validation report
        run: ./tests/generate_report.sh > validation_report.txt
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation_report.txt
      
      - name: Notify on failure
        if: failure()
        run: |
          echo "Validation failed - see artifacts for details"
          # Send email/Slack notification
```

---

### Pull Request Validation

```yaml
# .github/workflows/pr-validation.yml

name: Pull Request Validation

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  validate-pr:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run fast tests
        run: |
          ./tests/unit/test_gen_tb_patterns.sh
          ./tests/regression/test_line52_preservation.sh
      
      - name: Compare against wkpup2 baseline
        run: ./tests/integration/test_bitidentical_output.sh
      
      - name: Block merge if tests fail
        if: failure()
        run: exit 1
```

---

## 4. Monitoring and Alerts

### Daily Health Check

**Script**: `daily_health_check.sh`

```bash
#!/bin/bash

# Run subset of tests
./tests/regression/test_line52_preservation.sh
./tests/regression/test_corner_coverage.sh

# Check for unexpected file changes
find . -name "gen_tb.pl" -mtime -1 | while read file; do
    echo "WARNING: $file modified recently"
    # Trigger review
done

# Verify wkpup2 baseline still accessible
test -f /nfs/.../wkpup2/gpio/1p1v/config.cfg || \
    echo "ERROR: wkpup2 baseline not accessible"

# Report status
if [ $errors -eq 0 ]; then
    echo "Health check: PASS"
else
    echo "Health check: FAIL ($errors errors)"
    # Send alert
fi
```

**Schedule**: Run daily via cron

```bash
# crontab -e
0 8 * * * /path/to/daily_health_check.sh >> /var/log/wkpup_health.log 2>&1
```

---

## 5. Baseline Synchronization

### wkpup2 Baseline Tracking

**Purpose**: Ensure wkpup2 baseline hasn't changed unexpectedly

**Script**: `check_baseline_changes.sh`

```bash
#!/bin/bash

# Compute checksums of critical wkpup2 files
wkpup2_path="/nfs/.../wkpup2/gpio/1p1v"

md5sum $wkpup2_path/dependencies/.../gen_tb.pl > wkpup2_checksums.txt
md5sum $wkpup2_path/dependencies/.../sim_pvt.sh >> wkpup2_checksums.txt
md5sum $wkpup2_path/config.cfg >> wkpup2_checksums.txt

# Compare against stored reference
diff wkpup2_checksums.txt wkpup2_checksums_reference.txt

if [ $? -ne 0 ]; then
    echo "WARNING: wkpup2 baseline has changed!"
    echo "Review changes and update wkpup automation if needed"
    # Send alert
fi
```

**Schedule**: Run weekly

---

## 6. Documentation Requirements

### Change Control Process

**For any change to wkpup automation**:

1. **Document Intent**
   - What is being changed?
   - Why is it being changed?
   - Does it affect parity with wkpup2?

2. **Impact Analysis**
   - Which components affected?
   - Does it affect simulation accuracy?
   - Are tests updated?

3. **Validation Plan**
   - Which tests will verify the change?
   - Are new tests needed?
   - Bit-identical output still guaranteed?

4. **Review Process**
   - Technical review required
   - Run full test suite before merge
   - Update documentation

---

### Mandatory Documentation Updates

**When changing these files, MUST update docs**:

| File Changed | Documentation to Update |
|--------------|------------------------|
| gen_tb.pl | TESTBENCH_GENERATION_GAPS.md |
| sim_pvt.sh | SIMULATION_FLOW_GAPS.md |
| table_*.csv | CORNER_MATRIX_GAPS.md |
| read_cfg.sh | CONFIGURATION_GAPS.md |
| Any core script | INCONSISTENCY_ANALYSIS.md |

---

## 7. Versioning Strategy

### Semantic Versioning

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (affects parity with wkpup2)
- **MINOR**: New features (maintains parity)
- **PATCH**: Bug fixes (improves parity)

**Examples**:
- `1.0.0` - Initial parity achieved
- `1.1.0` - Added web UI feature (maintains parity)
- `1.0.1` - Fixed Line 52 preservation bug
- `2.0.0` - Changed gen_tb.pl logic (REQUIRES VALIDATION)

---

### Git Tagging

```bash
# Tag releases
git tag -a v1.0.0 -m "Initial wkpup2 parity achieved"
git push origin v1.0.0

# Maintain changelog
echo "v1.0.0 - 2025-10-28 - Initial parity" >> CHANGELOG.md
```

---

## 8. Rollback Procedures

### Emergency Rollback

**If critical regression detected**:

```bash
# Identify last known good version
git log --oneline | grep "validation PASS"

# Rollback to that commit
git checkout <commit-hash>

# Verify parity restored
./tests/integration/test_bitidentical_output.sh

# If PASS, create hotfix branch
git checkout -b hotfix/restore-parity
```

---

### Rollback Validation

After rollback:
1. Run full test suite
2. Verify bit-identical output
3. Document root cause
4. Plan proper fix

---

## 9. Training and Knowledge Transfer

### Team Training

**Required Training**:
1. wkpup2 baseline architecture (read COMPREHENSIVE_ANALYSIS.md)
2. Critical preservation mechanisms (Line 52, PVT matrix)
3. Test suite usage
4. Change control process

**Training Schedule**: Quarterly refresher

---

### Knowledge Base

**Maintain Wiki/Docs with**:
- Common errors and solutions
- Test failure troubleshooting
- Baseline comparison procedures
- Contact list for escalation

---

## 10. Success Metrics

### Key Performance Indicators (KPIs)

**Metric 1: Test Pass Rate**
- **Target**: 100% of tests pass on main branch
- **Measured**: Daily via CI
- **Action**: Block merges if <100%

**Metric 2: Time to Detect Regression**
- **Target**: <24 hours
- **Measured**: Time between regression introduction and detection
- **Action**: Improve test coverage if >24 hours

**Metric 3: Time to Fix Regression**
- **Target**: <7 days
- **Measured**: Time from detection to fix deployed
- **Action**: Prioritize regression fixes

**Metric 4: Baseline Parity**
- **Target**: 100% bit-identical output
- **Measured**: Weekly full comparison
- **Action**: Immediate fix if any deviation

---

## 11. Escalation Process

### Levels of Escalation

**Level 1: Developer** (0-2 days)
- Run tests locally
- Attempt fix
- Create PR with fix

**Level 2: Team Lead** (2-5 days)
- Review failed tests
- Coordinate fix effort
- Approve emergency rollback if needed

**Level 3: Architecture Review** (>5 days)
- Assess fundamental issue
- Decide on architectural change
- Schedule re-validation

---

## 12. Audit and Compliance

### Monthly Audit

**Checklist**:
- [ ] All tests passing
- [ ] Baseline parity maintained
- [ ] Documentation up to date
- [ ] CI pipeline functioning
- [ ] No outstanding regressions

**Output**: Audit report

---

### Quarterly Review

**Activities**:
- Review test coverage
- Assess new test needs
- Update baseline if wkpup2 changes
- Train new team members

---

## 13. Tools and Automation

### Recommended Tools

**1. Git Pre-Commit Framework**
```bash
pip install pre-commit
pre-commit install
```

**2. Continuous Integration**
- GitHub Actions (cloud)
- Jenkins (on-premise)

**3. Test Automation**
- Bash scripts (current)
- Python pytest (future)

**4. Monitoring**
- Cron jobs (current)
- Prometheus/Grafana (future)

---

## 14. Implementation Checklist

### Phase 1: Infrastructure Setup (Week 1)
- [ ] Create tests/ directory structure
- [ ] Implement unit tests
- [ ] Implement regression tests
- [ ] Create run_all_tests.sh

### Phase 2: Automation (Week 2)
- [ ] Set up pre-commit hooks
- [ ] Configure CI pipeline
- [ ] Schedule daily health checks
- [ ] Set up alerting

### Phase 3: Documentation (Week 3)
- [ ] Write change control process
- [ ] Create training materials
- [ ] Build knowledge base
- [ ] Define escalation process

### Phase 4: Validation (Week 4)
- [ ] Run full test suite
- [ ] Verify CI triggers
- [ ] Test rollback procedure
- [ ] Conduct team training

---

## References

- **VALIDATION_METHODOLOGY.md**: Test design
- **FIX_ROADMAP.md**: Implementation sequence
- **REFERENCE_RESULTS.md**: Expected outputs

---

## Document Status

**Version**: 1.0  
**Date**: October 28, 2025  
**Status**: 📋 PREVENTION FRAMEWORK READY  
**Implementation**: Start after Fix Roadmap Phase 1  
**Goal**: Zero regressions after parity achieved
