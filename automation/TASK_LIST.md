# Phase 4-6 Task List: Completing Wrapper Architecture

## Current Status
- ✅ Phase 1-3: PaiHoExecutor created, backend refactored
- ⚠️ Phase 4-6: Config validation, frontend simplification, testing

## Identified Issues

### Frontend Issues
1. Voltage table loading inconsistency - clears when voltage input changes
2. Custom temperature/voltage selections still present (should validate against CSV)
3. No CSV whitelist validation before submission
4. Arbitrary corner combinations allowed

### Backend Issues  
1. No config_generator.py for CSV validation
2. update_config_file() doesn't validate against Pai Ho's tables
3. No verification that generated config matches Pai Ho's requirements

## Task List (Recursive Execution)

### Task 1: Create Config Generator with CSV Validation
**Priority**: HIGH
**Status**: ✅ COMPLETED

Created `automation/backend/config_generator.py`:
- ✅ Load table_corner_list.csv from dependencies/
- ✅ Load table_supply_list.csv from dependencies/
- ✅ Validate corner combinations against CSV
- ✅ Validate voltage configurations against CSV
- ✅ Generate config.cfg matching Pai Ho's format
- ✅ Tested successfully with gpio/1p1v
- ✅ All validations working correctly

**Dependencies**: None
**Verification**: ✅ Config generator validates against CSVs correctly
**Test Results**: 9 valid corners, 22 valid voltage rails loaded

### Task 2: Fix Voltage Table Loading Bug
**Priority**: HIGH  
**Status**: IDENTIFIED

Frontend JavaScript issue:
- Voltage table loads initially
- Clears when voltage domain input changes
- Fix: Ensure table persists after loading

**Files**: `automation/frontend/index.html`
**Verification**: Voltage table stays loaded when typing voltage

### Task 3: Simplify Frontend to Match Pai Ho's Allowed Configs
**Priority**: MEDIUM
**Status**: NOT STARTED

Per ULTIMATE_MASTER_PLAN.md:
- Remove arbitrary custom temperature selections
- Remove arbitrary custom voltage combinations
- Keep only presets that match Pai Ho's CSV tables
- Add validation against CSV whitelists

**Files**: `automation/frontend/index.html`
**Verification**: Frontend only allows configurations in Pai Ho's CSVs

### Task 4: Update update_config_file() to Use Config Generator
**Priority**: MEDIUM
**Status**: ✅ COMPLETED

Updated `update_config_file()` in simulation.py:
- ✅ Import PaiHoConfigGenerator for CSV validation
- ✅ Validate corners against table_corner_list.csv before modification
- ✅ Validate voltage_domain against table_supply_list.csv
- ✅ Validate voltage_condition (func/perf/htol/hvqk)
- ✅ Raise clear errors for invalid parameters
- ✅ Only proceed with config update if all validations pass

**Files**: `automation/backend/simulation.py`
**Verification**: ✅ Function imports successfully, validation integrated
**Integration**: All simulation submissions now validated against CSV tables

### Task 5: End-to-End Simulation Test
**Priority**: HIGH
**Status**: NOT STARTED

Test complete workflow:
1. Submit simulation via web UI
2. Verify PaiHoExecutor calls ver03 scripts
3. Check generation stage creates testbenches
4. Verify config.cfg format
5. Check for errors in execution

**Verification**: Simulation completes without errors

### Task 6: Verify Bit-Identical Output
**Priority**: CRITICAL
**Status**: NOT STARTED

Per ULTIMATE_MASTER_PLAN.md success criteria:
- Run simulation via web UI
- Run same simulation manually with Pai Ho's scripts
- Compare outputs with `diff`
- Verify 100% identical

**Verification**: `diff` shows no differences

### Task 7: Document Remaining Issues
**Priority**: LOW
**Status**: NOT STARTED

Create issue tracker:
- Document any bugs found during testing
- List features that need CSV validation
- Note any deviations from Pai Ho's scripts

**Verification**: Complete issue list created

## Execution Order
1. Task 1: Config Generator (enables validation)
2. Task 4: Update config file generation (uses generator)
3. Task 2: Fix voltage table bug (UI improvement)
4. Task 5: End-to-end test (find more issues)
5. Task 3: Simplify frontend (final cleanup)
6. Task 6: Bit-identical verification (final validation)
7. Task 7: Documentation (capture learnings)

## Success Criteria (from ULTIMATE_MASTER_PLAN.md)

| Criterion | Status |
|-----------|--------|
| Zero modifications to Pai Ho's ver03 files | ✅ Met |
| All execution via subprocess wrapper | ✅ Met |
| Whitelist validation against CSV tables | ⚠️ Task 1 |
| Bit-identical output to manual execution | ⚠️ Task 6 |
| Frontend only allows validated configs | ⚠️ Task 3 |

## Notes
- Recursive execution: Each task may reveal more issues
- Add new tasks as discovered during testing
- Commit after each working change
- Verify against master plan documents before marking complete
