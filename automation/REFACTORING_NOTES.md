# Wrapper Architecture Refactoring - Implementation Notes

## Overview

This document tracks the refactoring of the WKP Automation WebApp to implement proper wrapper architecture per ULTIMATE_MASTER_PLAN.md and COMPREHENSIVE_ANALYSIS.md.

## Reference Documents

- **Master Plan**: https://github.com/seb917intel/wkpup-paiho-implementation/blob/master/ULTIMATE_MASTER_PLAN.md
- **Analysis**: https://github.com/seb917intel/wkpup-paiho-implementation/blob/master/COMPREHENSIVE_ANALYSIS.md
- **Reference Repo**: https://github.com/seb917intel/wkpup-simulation

## Key Principle

**Create a thin wrapper around Pai Ho's validated ver03 scripts WITHOUT modification**

- ✅ Call Pai Ho's original scripts via subprocess
- ❌ Do NOT create custom implementations
- ❌ Do NOT modify Pai Ho's files
- ✅ Validate inputs against Pai Ho's CSV tables

## Completed Work

### 1. PaiHoExecutor Wrapper Class

**File**: `automation/backend/paiho_executor.py`

Wraps Pai Ho's `dependencies/scripts/simulation_script/auto_pvt/ver03/sim_pvt.sh`:

```python
executor = PaiHoExecutor(
    project_root=REPO_ROOT,
    project='gpio',
    voltage_domain='1p1v'
)

# Calls: bash .../ver03/sim_pvt.sh config.cfg gen
result = executor.run_generation(work_dir)
```

**Features**:
- All stages supported (gen/run/ext/srt/bkp)
- Proper error handling and logging
- Timeout protection
- Path validation

### 2. Backend Refactoring

**Files Modified**:
- `automation/backend/simulation.py` - All stage functions now use PaiHoExecutor
- `automation/backend/main_tornado.py` - Updated callers
- `automation/backend/background_monitor.py` - Updated background threads

**Changes**:
- Replaced `subprocess.run(['bash', 'sim_pvt_local.sh', ...])` 
- With `executor.run_stage(work_dir, config_file, stage)`
- Removed custom script copying

### 3. File Copying Simplification

Per COMPREHENSIVE_ANALYSIS.md, Pai Ho's sim_pvt.sh only needs:
1. `config.cfg` - simulation configuration
2. `template/` - circuit netlist (sim_tx.sp)

**Removed**:
- ❌ Copy of `sim_pvt_local.sh` (custom)
- ❌ Copy of `local_pvt_loop.sh` (custom)
- ❌ Copy of `dependencies/` directory (huge, unnecessary)
- ❌ Copy of `runme.sh` (not needed)

## Remaining Work

### Phase 4: Config Generator

Create `automation/backend/config_generator.py`:

```python
class PaiHoConfigGenerator:
    def __init__(self, project, voltage_domain):
        # Load CSV tables from dependencies/
        self.corners = self._load_csv('table_corner_list.csv')
        self.voltages = self._load_csv('table_supply_list.csv')
    
    def validate_corners(self, corner_list):
        # Check against table_corner_list.csv
        pass
    
    def validate_voltages(self, voltage_config):
        # Check against table_supply_list.csv
        pass
    
    def generate_config(self, params, output_path):
        # Create config.cfg with validated params
        pass
```

**CSV Tables Location**:
- `{project}/{voltage_domain}/dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/`
- `table_corner_list.csv` - Valid PVT corners
- `table_supply_list.csv` - Valid voltage configurations

### Phase 5: Frontend Simplification

**Current Issue**: Frontend allows arbitrary configurations not in Pai Ho's tables

**Required Changes**:
1. Remove custom temperature/voltage matrix
2. Keep only preset buttons (Pai Ho Standard PVT, Full Sweep)
3. Validate corner selections against table_corner_list.csv
4. Validate voltage selections against table_supply_list.csv

### Phase 6: Testing

**Test Checklist**:
- [ ] Submit test simulation via web UI
- [ ] Verify PaiHoExecutor calls ver03 scripts
- [ ] Check generation stage creates testbenches
- [ ] Verify submission stage creates job_log.txt
- [ ] Check bit-identical output vs manual Pai Ho execution
- [ ] Validate no modifications to Pai Ho's files

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│  Frontend (index.html)                  │
│  ⚠️ Needs simplification                │
└──────────────────┬──────────────────────┘
                   │ HTTP POST /api/submit
                   ↓
┌─────────────────────────────────────────┐
│  main_tornado.py                        │
│  ✅ Updated to use PaiHoExecutor        │
└──────────────────┬──────────────────────┘
                   │ function call
                   ↓
┌─────────────────────────────────────────┐
│  simulation.py                          │
│  ✅ Refactored stage functions          │
└──────────────────┬──────────────────────┘
                   │ instantiate
                   ↓
┌─────────────────────────────────────────┐
│  PaiHoExecutor                          │
│  ✅ Wrapper class                       │
└──────────────────┬──────────────────────┘
                   │ subprocess.run()
                   ↓
┌─────────────────────────────────────────┐
│  Pai Ho's ver03/sim_pvt.sh              │
│  ✅ UNTOUCHED, read-only                │
└─────────────────────────────────────────┘
```

## Test Results

✅ Server starts: `http://localhost:5000`
✅ Frontend loads without errors
✅ WebSocket connects successfully
✅ All imports working
⚠️ Simulation submission not tested (next phase)

## Success Criteria

Per ULTIMATE_MASTER_PLAN.md:

1. ✅ Zero modifications to Pai Ho's ver03 files
2. ✅ All execution via subprocess wrapper
3. ⚠️ Whitelist validation against CSV tables (TODO)
4. ⚠️ Bit-identical output to manual execution (TODO)
5. ⚠️ Frontend only allows validated configurations (TODO)

## Next Steps

1. Create config_generator.py with CSV validation
2. Test simulation submission end-to-end
3. Simplify frontend to remove custom configurations
4. Validate bit-identical output
5. Document any remaining issues

## Related Commits

- 2c282fd - Created PaiHoExecutor wrapper class
- cbfbd57 - Replaced custom calls with PaiHoExecutor
- 99cf90e - Removed custom script copying

## Notes

- PaiHoExecutor references scripts from original location in dependencies/
- No copying of dependencies/ directory (saves disk space and time)
- Work directory only contains config.cfg and template/
- All validation should happen BEFORE calling Pai Ho's scripts
