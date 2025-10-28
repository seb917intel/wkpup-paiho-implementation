# Dependency Migration Status

## Overview
This document tracks the status of migrating external dependencies from Pai Ho's NFS shared storage into the local repository structure.

**Date**: October 28, 2025  
**Repository**: wkpup-paiho-implementation  
**Source Analysis**: GPIO_ANALYSIS.md, I3C_ANALYSIS.md  

---

## Dependency Classification

### 🔵 Shared Dependencies (Both GPIO and I3C)

These files are used by **BOTH** GPIO and I3C implementations identically:

#### 1. Simulation Scripts (4 files)
**Source Location**: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/`

| File | Purpose | Status |
|------|---------|--------|
| `alias_param_source/script_param` | Global script paths | ⚠️ Permission denied |
| `configuration/read_cfg.sh` | Config file parser | ⚠️ Permission denied |
| `runme_script/runme_func.sh` | Utility functions | ⚠️ Permission denied |
| `auto_pvt/ver02/sim_pvt.sh` | Main simulation engine | ⚠️ Permission denied |

#### 2. Circuit Files (4 files)
**Source Location**: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/`

| File | Purpose | Status |
|------|---------|--------|
| `wrapper_netlist/ioss3_txana_x2.sp` | TX analog wrapper netlist | ⚠️ Permission denied |
| `models/eqgen.sp` | Equalization generator | ⚠️ Permission denied |
| `models/txcfg.sp` | TX configuration | ⚠️ Permission denied |
| `models/no_tcoil_prelay.sp` | Pre-layout model without T-coil | ⚠️ Permission denied |

#### 3. Library Files (12 files)
**Source Location**: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/`

| File | Purpose | Shared by Both |
|------|---------|---------------|
| `cb.lib` | Clock buffer library | ✅ GPIO + I3C |
| `tco_ctrl.lib` | TCO control library | ✅ GPIO + I3C |
| `equalization.lib` | Equalization library | ✅ GPIO + I3C |
| `uncal_vsshffc.lib` | VSS high-freq filtering | ✅ GPIO + I3C |
| `uncal_vsshleak.lib` | VSS leakage model | ✅ GPIO + I3C |
| `weakpullup.lib` | ⚠️ **CRITICAL** - See below | ✅ GPIO + I3C |
| `uncomp_slewrate.lib` | Uncompensated slew rate | ✅ GPIO + I3C |
| `xtalk.lib` | Crosstalk library | ✅ GPIO + I3C |
| `xover.lib` | Crossover library | ✅ GPIO + I3C |
| `txmode.lib` | TX mode library | ✅ GPIO + I3C |
| `uncal_oct_rs.lib` | Uncalibrated OCT RS | ✅ GPIO + I3C |
| `uncal_oct_rt.lib` | Uncalibrated OCT RT | ✅ GPIO + I3C |

**Status**: ⚠️ Permission denied on all library files

#### 4. PDK Model Files (8+ files)
**Source Location**: `/nfs/site/disks/psg_pdkalynx_1/alynx_pdk/PDK_CLN3P_v1.0_2p1a_2025WW23/models/`

| File | Purpose | Status |
|------|---------|--------|
| `hspice/include.hsp` | Main HSPICE include | ⚠️ Permission denied |
| `hspice/include_TT` | Typical-typical corner | ⚠️ Permission denied |
| `hspice/hspice.subckt` | HSPICE subcircuits | ⚠️ Permission denied |
| `hspice/hspice_AnalogCell_toBulk.subckt` | Analog cell models | ⚠️ Permission denied |
| `hspice/cln3p_1d2_sp_v1d0_2p7_usage.l` | Usage guidelines | ⚠️ Permission denied |
| `hspice/cln3p_1d2_sp_v1d0_2p7.l` | Main model library | ⚠️ Permission denied |
| `hspice/crn3p_lct_1d2_sp_v1d0_2p7.l` | LCT model library | ⚠️ Permission denied |
| `hspice/net_divider.l` | Net divider models | ⚠️ Permission denied |

**Status**: ⚠️ Permission denied (PDK files are restricted)

---

### 🔴 GPIO-Specific Dependencies

#### SPICE Netlist Parameter
**File**: `gpio/1p1v/template/sim_tx.sp`  
**Line 52**: `.lib "weakpullup.lib" enable`

**Dependency**: Uses the `enable` parameter from `weakpullup.lib`

---

### 🟢 I3C-Specific Dependencies

#### SPICE Netlist Parameter  
**File**: `i3c/1p1v/template/sim_tx.sp`  
**Line 52**: `.lib "weakpullup.lib" enable_i3c`

**Dependency**: Uses the `enable_i3c` parameter from `weakpullup.lib`

#### Simulation Log
**File**: `i3c/1p1v/template/##Jun-16-10:48:53#.apgcp0k601201.altera_png_vp.800670626`  
**Status**: ✅ **Available in repository**  
**Contains**: Actual simulation execution log from June 16, 2025

---

## The ONE Critical Difference

### weakpullup.lib Parameter Selection

The **ONLY** difference between GPIO and I3C implementations is the library parameter used in `sim_tx.sp` line 52:

```spice
# GPIO uses:
.lib "weakpullup.lib" enable

# I3C uses:
.lib "weakpullup.lib" enable_i3c
```

This single-parameter difference enables:
- 99% code reuse between GPIO and I3C
- Protocol-specific behavior through library parameterization
- Scalable architecture for future protocols

---

## Access Issues and Workarounds

### Permission Denied Files

**Root Cause**: External dependencies on Pai Ho's NFS storage (`/nfs/site/disks/km6_io_22/users/paihobon/`) have restricted permissions.

**Affected Categories**:
- ✅ Simulation scripts (4 files)
- ✅ Circuit files (4 files)  
- ✅ Library files (12 files)
- ✅ PDK models (8+ files)

**Total**: 28+ files inaccessible

### Recommended Actions

#### Option 1: Request Access from Pai Ho
```bash
# Contact Pai Ho to grant read permissions
chmod -R o+r /nfs/site/disks/km6_io_22/users/paihobon/simulation/
```

#### Option 2: Copy via Authorized User
```bash
# Have Pai Ho or authorized user copy files
sudo -u paihobon cp -r /nfs/site/disks/km6_io_22/users/paihobon/simulation/ <destination>
```

#### Option 3: Document Dependencies (Current Approach)
- Keep external references in sim_tx.sp
- Document all dependencies in this file
- Maintain compatibility with shared infrastructure

---

## Repository Structure (Proposed)

```
wkpup2/
├── gpio/
│   └── 1p1v/
│       ├── runme.sh
│       ├── config.cfg
│       ├── template/
│       │   └── sim_tx.sp (references external libs)
│       └── dependencies/          # ← To be populated
│           ├── scripts/           # Simulation automation
│           ├── circuits/          # SPICE netlists
│           ├── libraries/         # .lib files
│           └── pdk/              # PDK models (restricted)
│
├── i3c/
│   └── 1p1v/
│       ├── runme.sh
│       ├── config.cfg
│       ├── template/
│       │   ├── sim_tx.sp (references external libs)
│       │   └── ##Jun-16...626 (simulation log) ✅
│       └── dependencies/          # ← To be populated
│           ├── scripts/           # Simulation automation
│           ├── circuits/          # SPICE netlists
│           ├── libraries/         # .lib files (enable_i3c param)
│           └── pdk/              # PDK models (restricted)
│
└── shared_dependencies/           # ← Common files (if permissions granted)
    ├── scripts/
    ├── circuits/
    ├── libraries/
    └── pdk/
```

---

## Next Steps for Copilot Agent

### Phase 1: Access Resolution
1. **Coordinate with Pai Ho** to grant read access to dependency files
2. **Copy accessible files** to local `dependencies/` directories
3. **Verify file integrity** after copying

### Phase 2: Recursive Analysis
Once files are accessible, perform recursive analysis on:

#### Tier 2 Dependencies (from sourced scripts)
- [ ] `script_param` - May reference additional configuration files
- [ ] `read_cfg.sh` - Config parsing logic
- [ ] `runme_func.sh` - Function definitions and external calls
- [ ] `sim_pvt.sh` - Main simulation engine (critical!)

#### Tier 3 Dependencies (from SPICE files)
- [ ] `ioss3_txana_x2.sp` - Wrapper netlist, may include sub-circuits
- [ ] `eqgen.sp` - Equalization model definitions
- [ ] `txcfg.sp` - TX configuration subcircuits
- [ ] `no_tcoil_prelay.sp` - Pre-layout models

#### Tier 4 Dependencies (from library files)
- [ ] `weakpullup.lib` - **CRITICAL** - Contains `enable` and `enable_i3c` parameters
- [ ] All 11 other `.lib` files - May reference additional models

#### Tier 5 Dependencies (from PDK)
- [ ] PDK include chains - Recursive model includes
- [ ] Subcircuit definitions - Standard cell models
- [ ] Corner files - Process variation models

### Phase 3: Documentation
For each tier, document:
- File contents
- All referenced files (includes, sources, calls)
- Parameter definitions
- Critical differences between GPIO/I3C usage
- External tool dependencies

---

## Copilot Agent Prompt for Recursive Analysis

```markdown
# Task: Recursive Dependency Analysis for WKPUP Simulation Framework

## Objective
Perform exhaustive recursive analysis of all dependency files for GPIO and I3C WKPUP simulations.

## Prerequisites
1. Obtain read access to: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/`
2. Verify PDK access: `/nfs/site/disks/psg_pdkalynx_1/alynx_pdk/PDK_CLN3P_v1.0_2p1a_2025WW23/`

## Analysis Workflow

### Step 1: Read Tier 2 Scripts
For each script in the list below:
1. Read full file contents
2. Document purpose and functionality  
3. Extract all sourced files, included files, and called scripts
4. Add extracted files to analysis queue
5. Document findings in `TIER2_SCRIPTS_ANALYSIS.md`

**Files to analyze**:
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/alias_param_source/script_param`
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/configuration/read_cfg.sh`
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/runme_script/runme_func.sh`
- `$script_path/auto_pvt/ver02/sim_pvt.sh` (path determined from script_param)

### Step 2: Read Tier 3 Circuit Files
For each SPICE file:
1. Read full netlist
2. Document circuit topology
3. Extract all `.include` statements
4. Extract all `.lib` references
5. List all subcircuit calls (`.subckt`)
6. Document in `TIER3_CIRCUITS_ANALYSIS.md`

**Files to analyze**:
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/wrapper_netlist/ioss3_txana_x2.sp`
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/eqgen.sp`
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/txcfg.sp`
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/no_tcoil_prelay.sp`

### Step 3: Read Tier 4 Library Files
For each `.lib` file:
1. Read full library contents
2. Document all parameter sections
3. **CRITICAL**: Extract `enable` and `enable_i3c` parameter definitions from `weakpullup.lib`
4. List all model references
5. Document in `TIER4_LIBRARIES_ANALYSIS.md`

**Files to analyze**:
- `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/weakpullup.lib` ⚠️ **HIGHEST PRIORITY**
- All 11 other `.lib` files from the list

### Step 4: Read Tier 5 PDK Files
For each PDK file:
1. Read include hierarchy
2. Map model definitions
3. Document corner variations
4. Document in `TIER5_PDK_ANALYSIS.md`

**Files to analyze**:
- Start with `/nfs/site/disks/psg_pdkalynx_1/alynx_pdk/PDK_CLN3P_v1.0_2p1a_2025WW23/models/hspice/include.hsp`
- Follow all recursive includes

### Step 5: Create Dependency Graph
Generate visual dependency tree showing:
- File-to-file relationships
- Include chains
- Parameter flow (especially enable vs enable_i3c)
- Tool dependencies

### Step 6: Update Documentation
Update this file with:
- [ ] Access status (granted/denied)
- [ ] Files successfully copied
- [ ] Analysis completion status
- [ ] New dependencies discovered

## Deliverables
1. `TIER2_SCRIPTS_ANALYSIS.md`
2. `TIER3_CIRCUITS_ANALYSIS.md`
3. `TIER4_LIBRARIES_ANALYSIS.md` (with critical weakpullup.lib analysis)
4. `TIER5_PDK_ANALYSIS.md`
5. `DEPENDENCY_GRAPH.md` (visual tree)
6. Updated `DEPENDENCY_MIGRATION_STATUS.md`

## Success Criteria
- All 28+ dependency files read and documented
- Complete closure (no unexplored references)
- GPIO vs I3C differences fully mapped
- Dependency graph shows complete call chain from runme.sh to PDK
```

---

## Summary

**Total Dependencies Identified**: 28+ files  
**Accessible**: 4 files (repository files)  
**Restricted**: 24+ files (external NFS storage)  
**Critical File**: `weakpullup.lib` (contains GPIO/I3C differentiation)  
**Next Action**: Obtain permissions and perform recursive analysis per above prompt

---

**Document Version**: 1.0  
**Last Updated**: October 28, 2025  
**Maintainer**: Sebastian Chin (seb917intel)
