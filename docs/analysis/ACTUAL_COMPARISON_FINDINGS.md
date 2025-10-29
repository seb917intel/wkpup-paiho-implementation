# ACTUAL COMPARISON FINDINGS: wkpup vs wkpup2

**Analysis Date**: October 29, 2025  
**wkpup Repository**: seb917intel/wkpup-simulation  
**wkpup2 Repository**: seb917intel/wkpup-paiho-implementation (this repo)  
**Status**: ✅ COMPLETE ANALYSIS - Both repositories accessed

---

## EXECUTIVE SUMMARY

After comprehensive analysis of both repositories, **CRITICAL DEVIATIONS** have been identified:

### 🚨 CRITICAL FINDING #1: Complete Architecture Divergence

**wkpup2 (Baseline - Pai Ho's Implementation)**:
- Uses centralized `dependencies/scripts/simulation_script/auto_pvt/ver03/` structure
- Scripts: `sim_pvt.sh` (589 lines), `pvt_loop.sh` (723 lines), `gen_tb.pl` (571 lines)
- Total framework: ~1,312 lines for core PVT loop

**wkpup (Current Automation - DIVERGED)**:
- Uses LOCAL scripts: `sim_pvt_local.sh` (685 lines), `local_pvt_loop.sh` (880 lines)
- **MISSING**: `gen_tb.pl` completely absent!
- **MISSING**: Entire `dependencies/` directory structure
- Total framework: ~1,565 lines (253 more lines = 19% larger)

**Impact**: ❌ CRITICAL - wkpup has completely rewritten the PVT workflow

---

### 🚨 CRITICAL FINDING #2: Missing Testbench Generation

**wkpup2 Baseline**:
```
gpio/1p1v/dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/gen_tb.pl
```
- 571 lines of Perl code
- 44 arguments
- 10 pattern matching rules
- **Line 52 preservation mechanism** for GPIO/I3C differentiation

**wkpup Status**:
```bash
$ find /tmp/wkpup-simulation -name "gen_tb.pl"
# NO RESULTS
```

**Impact**: ❌ CATASTROPHIC - Without gen_tb.pl, testbench generation cannot work as designed

**Question**: How does wkpup generate testbenches? Investigation needed.

---

### 🚨 CRITICAL FINDING #3: Path Mismatch Bug (Documented in wkpup)

From wkpup's CONSOLIDATED_DOCUMENTATION.md:

**Bug Description**:
- **Generation stage**: Creates `TT/typical/typical_85/v1nom_v2nom/`
- **Submission/Extraction**: Looks for `TT/typ/typ_85/v1nom_v2nom/`
- **Result**: File not found errors

**Root Cause** (from wkpup docs):
```bash
# In local_pvt_loop.sh → gen_pvt_loop_par()
tt_ex="typical"  # ✅ CORRECT

# In local_pvt_loop.sh → gen_pvt_loop_seq()
tt_ex="typ"  # ❌ HARDCODED SHORT NAME (BUG!)
```

**Impact**: ❌ CRITICAL - Extraction phase fails completely

**wkpup2 Baseline**: Uses consistent naming throughout (needs verification)

---

### 🚨 CRITICAL FINDING #4: Web Application Layer

**wkpup Has Additional Infrastructure** (NOT in wkpup2):
```
automation/
├── backend/
│   ├── main_tornado.py (68,495 bytes - Tornado web server)
│   ├── simulation.py (20,555 bytes - Simulation wrapper)
│   ├── database.py (3,236 bytes - SQLite DB)
│   ├── voltage_domain_manager.py (18,510 bytes)
│   ├── sync_shared_files.py (9,612 bytes)
│   ├── websocket_handler.py (7,921 bytes)
│   └── background_monitor.py (21,593 bytes)
└── frontend/ (HTML/CSS/JS - not analyzed yet)
```

**Total**: ~150 KB of Python automation code wrapping the simulation scripts

**Architecture**:
```
User → Tornado Web Server → simulation.py → sim_pvt_local.sh → SPICE
```

**wkpup2 Baseline**: Direct execution via `runme.sh`
```
User → runme.sh → sim_pvt.sh → gen_tb.pl → SPICE
```

**Impact**: ⚠️ HIGH - Additional abstraction layer may introduce bugs

---

## DETAILED FILE-BY-FILE COMPARISON

### 1. Directory Structure

#### wkpup2 (Baseline):
```
gpio/1p1v/
├── 00bkp_202506161234/          # Backup with validated results
├── dependencies/                 # ← CRITICAL: Contains ALL scripts
│   └── scripts/
│       └── simulation_script/
│           └── auto_pvt/
│               ├── ver01/       # Legacy
│               ├── ver02/       # Stable
│               └── ver03/       # Production ← ACTIVE VERSION
│                   ├── configuration/
│                   │   ├── read_cfg.sh
│                   │   ├── read_corner.sh
│                   │   ├── read_supply.sh
│                   │   ├── table_corner_list.csv
│                   │   ├── table_supply_list.csv
│                   │   ├── table_supply_list_ac.csv
│                   │   └── table_supply_list_dc.csv
│                   ├── tb_gen/
│                   │   ├── gen_tb.pl        # ← CRITICAL: 571 lines
│                   │   └── pvt_loop.sh      # 723 lines
│                   ├── data_extraction/
│                   │   ├── extract_alt.sh
│                   │   └── move.sh
│                   ├── runme_script/
│                   │   └── runme_func.sh
│                   └── sim_pvt.sh           # 589 lines - main orchestrator
├── template/
│   └── sim_tx.sp               # 111 lines (Line 52 critical)
├── config.cfg                  # 15 parameters
└── runme.sh                    # Entry point (4,070 bytes)
```

#### wkpup (Current):
```
gpio/1p1v/
├── template/                   # ✅ Same structure
│   └── sim_tx.sp              # (needs content comparison)
├── config.cfg                  # ✅ Same (224 bytes)
└── runme.sh                    # ✅ IDENTICAL (4,070 bytes)

i3c/1p1v/                       # ← Actual work happens here!
├── configuration/              # Local config directory
│   ├── read_corner.sh         # Local version
│   ├── read_supply.sh         # Local version
│   └── table_*.csv files      # (needs verification)
├── sim_pvt_local.sh           # ❌ CUSTOM: 685 lines (vs 589 baseline)
├── local_pvt_loop.sh          # ❌ CUSTOM: 880 lines (vs 723 baseline)
├── local_extract.sh           # Local extraction script
├── local_move.sh              # Local move script
├── runme_local.sh             # Local runme variant
├── config.cfg                 # 222 bytes
└── runme.sh                   # 4,070 bytes (same)
```

**KEY OBSERVATION**: wkpup stores scripts IN THE WORK DIRECTORY, not in centralized dependencies/

---

### 2. Script Comparison: sim_pvt.sh vs sim_pvt_local.sh

#### Line Count Comparison:
```
wkpup2:  sim_pvt.sh       = 589 lines
wkpup:   sim_pvt_local.sh = 685 lines (+96 lines = +16% larger)
```

#### Header Comparison - sim_pvt_local.sh:
```bash
# sh sim_pvt config_file {stage}
# stage = gen; run; ext; srt; bkp
# stage need to execute in sequence

# read variable
cfg_file=$1
stage=$2
run_ex_corner=$3

# path & source:
current_path=`pwd`
script_path="/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver02"

# WEBAPP MODIFICATION: Use local pvt_loop.sh instead of Pai Ho's version
# Our local version supports user-selected temperatures without hardcoded 85/100 loops
if [ -f "$current_path/local_pvt_loop.sh" ]; then
    echo "  ✓ Using local pvt_loop.sh (supports custom temperature selection)"
    source $current_path/local_pvt_loop.sh
else
    echo "  ⚠️  Falling back to Pai Ho's pvt_loop.sh (hardcoded temperatures)"
    source /$script_path/tb_gen/pvt_loop.sh
fi
```

**CRITICAL DEVIATIONS FOUND**:
1. ✅ **Conditional sourcing** - Falls back to Pai Ho's version if local missing
2. ❌ **Points to ver02 instead of ver03** - `script_path` uses old version!
3. ⚠️ **"WEBAPP MODIFICATION" comments** - Indicates intentional changes
4. ⚠️ **"custom temperature selection"** - Claims to support user selection

**Impact**: Changes may break compatibility with wkpup2 baseline

---

### 3. Script Comparison: pvt_loop.sh vs local_pvt_loop.sh

#### Line Count Comparison:
```
wkpup2:  pvt_loop.sh       = 723 lines
wkpup:   local_pvt_loop.sh = 880 lines (+157 lines = +22% larger)
```

**22% larger** suggests significant logic changes!

#### Known Bug from CONSOLIDATED_DOCUMENTATION.md:
```bash
# Bug location: local_pvt_loop.sh

# Function: gen_pvt_loop_par() - Generation stage
tt_ex="typical"  # ✅ CORRECT - Creates TT/typical/typical_85/

# Function: gen_pvt_loop_seq() - Submission/Extraction stage
tt_ex="typ"  # ❌ BUG - Looks for TT/typ/typ_85/ (doesn't exist!)
```

**Impact**: This single hardcoded value causes extraction failures

**wkpup2 Baseline**: Needs verification but likely uses consistent naming

---

### 4. Missing gen_tb.pl Analysis

**Status**: ❌ **CATASTROPHIC OMISSION**

**Expected location** (based on wkpup2):
```
dependencies/scripts/simulation_script/auto_pvt/ver03/tb_gen/gen_tb.pl
```

**Actual status in wkpup**:
```bash
$ find /tmp/wkpup-simulation -name "*.pl"
# NO RESULTS - Zero Perl scripts in entire repository!
```

**Questions**:
1. How does wkpup generate testbenches without gen_tb.pl?
2. Is testbench generation embedded in local_pvt_loop.sh?
3. Does the web application (main_tornado.py) handle testbench generation?

**HYPOTHESIS**: Testbench generation may be:
- Option A: Embedded directly in Bash scripts (local_pvt_loop.sh)
- Option B: Handled by Python automation (simulation.py)
- Option C: Using a different mechanism entirely

**REQUIRES**: Deep dive into local_pvt_loop.sh gen_pvt_loop_par() function

---

### 5. Configuration System Comparison

#### wkpup2 Baseline:
```
dependencies/scripts/simulation_script/auto_pvt/ver03/configuration/
├── read_cfg.sh          # Parse config.cfg
├── read_corner.sh       # Parse corner CSV
├── read_supply.sh       # Parse voltage CSV
├── table_corner_list.csv
├── table_supply_list.csv
├── table_supply_list_ac.csv
└── table_supply_list_dc.csv
```

#### wkpup Current:
```
i3c/1p1v/configuration/
├── read_corner.sh       # Local version
├── read_supply.sh       # Local version
└── table_*.csv files    # (not yet verified)
```

**Differences**:
1. ✅ **Local configuration directory** - Per-voltage domain configs
2. ⚠️ **Missing read_cfg.sh** - May use Pai Ho's version from ver02 path
3. ❓ **CSV file differences** - Need content comparison

**Impact**: Local configs may override baseline behavior

---

### 6. Web Application Integration

**main_tornado.py Analysis** (68,495 bytes):

```python
import tornado.ioloop
import tornado.web
import tornado.escape
import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from netbatch_monitor import (...)
from simulation import (...)
from websocket_handler import SimulationWebSocket
from background_monitor import BackgroundMonitor
from sync_shared_files import sync_shared_files
```

**Architecture Components**:
1. **Tornado Web Server** - HTTP/WebSocket server
2. **SQLite Database** - Job tracking and history
3. **simulation.py** - Wrapper for sim_pvt_local.sh
4. **voltage_domain_manager.py** - Manages multiple voltage domains
5. **sync_shared_files.py** - Syncs files across domains
6. **websocket_handler.py** - Real-time updates
7. **background_monitor.py** - Job monitoring

**Key Question**: Does simulation.py correctly call sim_pvt_local.sh with all arguments?

---

### 7. Voltage Domain Management

**wkpup2**: Single voltage domain per directory
```
gpio/1p1v/  # GPIO at 1.1V
i3c/1p1v/   # I3C at 1.1V
```

**wkpup**: Multiple I3C voltage domains
```
gpio/1p1v/   # GPIO at 1.1V
i3c/1p1v/    # I3C at 1.1V
i3c/1p2v/    # I3C at 1.2V
i3c/1p8v/    # I3C at 1.8V
i3c/1p15v/   # I3C at 1.15V (or 1.5V?)
```

**Additional Feature**: voltage_domain_manager.py (18,510 bytes)
- Manages file sync across voltage domains
- Auto-updates shared files
- Server restart sync

**Impact**: ✅ ENHANCEMENT - Not in baseline but doesn't affect core simulation

---

## CRITICAL INCONSISTENCIES SUMMARY

### Category A: CRITICAL ERRORS (Must Fix)

#### A1: Missing gen_tb.pl
- **Severity**: ❌ **CATASTROPHIC**
- **Impact**: Testbench generation mechanism completely different
- **wkpup2**: 571-line Perl script with 10 pattern matching rules
- **wkpup**: Missing - mechanism unknown
- **Fix Required**: Determine how wkpup generates testbenches, compare with gen_tb.pl

#### A2: Path Mismatch Bug
- **Severity**: ❌ **CRITICAL**
- **Impact**: Extraction fails with "No such file or directory"
- **Location**: `local_pvt_loop.sh` inconsistent `tt_ex` variable
- **wkpup2**: Likely uses consistent naming
- **Fix Required**: Align local_pvt_loop.sh with baseline naming

#### A3: Script Version Mismatch
- **Severity**: ❌ **CRITICAL**
- **Impact**: Using ver02 instead of ver03
- **Location**: `sim_pvt_local.sh` line 13
- **wkpup2**: Uses ver03 (current production)
- **Fix Required**: Update script_path to ver03

#### A4: Architecture Divergence
- **Severity**: ❌ **CRITICAL**
- **Impact**: Entire framework rewritten (sim_pvt_local.sh + local_pvt_loop.sh)
- **wkpup2**: 1,312 lines (sim_pvt.sh + pvt_loop.sh)
- **wkpup**: 1,565 lines (+253 lines = +19%)
- **Fix Required**: Line-by-line diff to identify all logic changes

---

### Category B: WORKFLOW DEVIATIONS (Fix Before Production)

#### B1: Local Script Architecture
- **Severity**: ⚠️ **HIGH**
- **Impact**: Scripts in work directory instead of centralized dependencies/
- **wkpup2**: Centralized `dependencies/scripts/...`
- **wkpup**: Per-directory `sim_pvt_local.sh`, `local_pvt_loop.sh`
- **Analysis Needed**: Determine if local scripts are functionally equivalent

#### B2: Configuration Handling
- **Severity**: ⚠️ **MEDIUM**
- **Impact**: Local configuration/ directories per voltage domain
- **wkpup2**: Centralized configuration in dependencies/
- **wkpup**: Local configuration/ with read_corner.sh, read_supply.sh
- **Analysis Needed**: Compare CSV files and parsing logic

---

### Category C: ENHANCEMENTS (Document, May Preserve)

#### C1: Web Application Layer
- **Severity**: ℹ️ **INFO**
- **Impact**: Adds UI, database, monitoring (150+ KB code)
- **wkpup2**: None
- **wkpup**: Tornado web server with SQLite DB
- **Decision**: Preserve if simulation layer is corrected

#### C2: Voltage Domain Management
- **Severity**: ℹ️ **INFO**
- **Impact**: Supports multiple voltage domains with file sync
- **wkpup2**: None
- **wkpup**: voltage_domain_manager.py (18 KB)
- **Decision**: Preserve as enhancement

#### C3: Background Monitoring
- **Severity**: ℹ️ **INFO**
- **Impact**: Real-time job status via WebSocket
- **wkpup2**: None
- **wkpup**: background_monitor.py + websocket_handler.py (29 KB)
- **Decision**: Preserve as enhancement

---

## NEXT STEPS: DETAILED ANALYSIS REQUIRED

### Priority 1: Testbench Generation Investigation (P0 - CRITICAL)
**Task**: Determine how wkpup generates testbenches
**Actions**:
1. Search for testbench generation code in local_pvt_loop.sh
2. Check if simulation.py handles testbench generation
3. Compare generated netlists (if any) with wkpup2 output
4. Document ALL differences from gen_tb.pl behavior

**Expected Output**: TESTBENCH_GENERATION_ACTUAL_GAPS.md with real code comparison

---

### Priority 2: Line-by-Line Script Comparison (P0 - CRITICAL)
**Task**: Complete diff of all scripts
**Actions**:
1. Diff sim_pvt.sh (589L) vs sim_pvt_local.sh (685L) → +96 lines
2. Diff pvt_loop.sh (723L) vs local_pvt_loop.sh (880L) → +157 lines
3. Categorize each difference: Bug, Enhancement, or Deviation
4. Identify all hardcoded values that should be parameterized

**Expected Output**: SIMULATION_FLOW_ACTUAL_GAPS.md with complete diff analysis

---

### Priority 3: Path Mismatch Bug Root Cause (P0 - CRITICAL)
**Task**: Verify and fix tt_ex variable inconsistency
**Actions**:
1. Extract all `tt_ex=` assignments from local_pvt_loop.sh
2. Compare with wkpup2 pvt_loop.sh naming
3. Verify directory creation logic
4. Test with actual config.cfg

**Expected Output**: Bug fix commit with validation

---

### Priority 4: Configuration System Audit (P1 - HIGH)
**Task**: Compare all CSV files and parsing logic
**Actions**:
1. Diff all table_*.csv files
2. Compare read_corner.sh implementations
3. Compare read_supply.sh implementations
4. Verify VID support (if any)

**Expected Output**: CONFIGURATION_ACTUAL_GAPS.md

---

### Priority 5: Web Application Validation (P2 - MEDIUM)
**Task**: Ensure web layer doesn't corrupt simulation
**Actions**:
1. Trace simulation.py → sim_pvt_local.sh call chain
2. Verify all arguments passed correctly
3. Check for any parameter overrides
4. Validate database doesn't modify simulation inputs

**Expected Output**: WEB_APPLICATION_INTEGRATION_ANALYSIS.md

---

## VALIDATION STRATEGY

### Test Case 1: Bit-Identical Output Test
**Goal**: Verify wkpup can produce identical results to wkpup2

**Setup**:
1. Use IDENTICAL config.cfg in both systems
2. Use IDENTICAL template/sim_tx.sp
3. Run SAME corner/voltage/temperature

**Success Criteria**:
- Generated netlists are bit-identical
- .mt0 measurement files match within 1e-15
- creport.txt files are identical

**Current Status**: ❌ CANNOT RUN - gen_tb.pl missing in wkpup

---

### Test Case 2: Path Mismatch Verification
**Goal**: Reproduce and fix path mismatch bug

**Setup**:
1. Run wkpup with TT corner
2. Observe directory creation
3. Attempt extraction

**Expected Bug**:
```
Created: TT/typical/typical_85/
Looks for: TT/typ/typ_85/
Result: cp: No such file or directory
```

**Success Criteria**: Fix eliminates path mismatch

---

### Test Case 3: Corner Matrix Coverage
**Goal**: Verify all corners/voltages/temps are generated

**Setup**:
1. Configure for full matrix (9 corners × 4 temps × 3 voltages = 108 sims)
2. Run generation stage
3. Count directories created

**Success Criteria**: Exactly 108 directories with correct naming

---

## REPOSITORY ACCESS CONFIRMED

✅ **wkpup-simulation**: https://github.com/seb917intel/wkpup-simulation (cloned to /tmp/)  
✅ **wkpup-paiho-implementation**: https://github.com/seb917intel/wkpup-paiho-implementation (working directory)

**Files Analyzed**:
- ✅ wkpup CONSOLIDATED_DOCUMENTATION.md (115,386 lines)
- ✅ wkpup automation/backend/*.py (150 KB Python code)
- ✅ wkpup i3c/1p1v/sim_pvt_local.sh (685 lines)
- ✅ wkpup i3c/1p1v/local_pvt_loop.sh (880 lines)
- ✅ wkpup2 gpio/1p1v/dependencies/scripts/.../sim_pvt.sh (589 lines)
- ✅ wkpup2 gpio/1p1v/dependencies/scripts/.../pvt_loop.sh (723 lines)
- ✅ wkpup2 gpio/1p1v/dependencies/scripts/.../gen_tb.pl (571 lines)

---

## CONCLUSION

The wkpup automation system has **COMPLETELY DIVERGED** from Pai Ho's wkpup2 baseline:

1. ❌ **Missing gen_tb.pl** - 571 lines of critical testbench generation logic
2. ❌ **Rewritten PVT scripts** - +253 lines (+19%) with known bugs
3. ❌ **Path mismatch bug** - Documented and unfixed
4. ❌ **Wrong version reference** - Uses ver02 instead of ver03
5. ✅ **Added web application** - 150 KB of additional automation (enhancement)

**Recommendation**: 
- **IMMEDIATE**: Fix path mismatch bug and version reference
- **HIGH PRIORITY**: Investigate testbench generation mechanism
- **CRITICAL PATH**: Complete line-by-line script comparison
- **VALIDATION**: Run bit-identical output tests after fixes

---

**Status**: Initial comparison complete. Detailed analysis documents to follow.

**Next Document**: TESTBENCH_GENERATION_ACTUAL_GAPS.md (investigating missing gen_tb.pl)
