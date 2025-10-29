# Complete Implementation Plan: Pai Ho's System + wkpup Automation Features

## Document Purpose

This is the **MASTER IMPLEMENTATION DOCUMENT** containing:
- ✅ Complete analysis of both systems
- ✅ Detailed architecture for best-of-both-worlds solution
- ✅ Step-by-step implementation instructions
- ✅ Code templates for every component
- ✅ Testing strategies and validation
- ✅ Deployment procedures
- ✅ Troubleshooting guides

**Read Time**: 2-3 hours (complete), 30 minutes (executive summary)

---

## Executive Summary

### Mission Statement

**Transform Pai Ho's scientifically validated wkpup2 system into a user-friendly automation platform with:**
1. **100% Accuracy**: Pai Ho's proven simulation core (UNTOUCHED)
2. **Advanced Features**: Web UI, database tracking, flexible configuration
3. **Zero Compromise**: Features built as wrappers, never replacing core logic

### Critical Principle

```
┌─────────────────────────────────────────┐
│  NEVER MODIFY PAI HO'S ORIGINAL FILES   │
│                                         │
│  ALL features are EXTERNAL WRAPPERS     │
│  built ON TOP of validated core         │
└─────────────────────────────────────────┘
```

### Timeline

- **Phase 1**: Foundation (Week 1-2) - Web UI + Database
- **Phase 2**: Configuration (Week 3-4) - Flexible parameters
- **Phase 3**: Multi-Domain (Week 5-6) - Voltage domain support
- **Phase 4**: Validation (Week 7-8) - Complete testing
- **Total**: 8 weeks to production-ready system

### Success Metrics

- ✅ **Bit-identical output**: 100% (web submission = manual submission)
- ✅ **Database accuracy**: 100% (stored results = actual results)
- ✅ **Regression tests**: 100% pass rate (all Pai Ho scenarios work)
- ✅ **File protection**: 0 modifications to Pai Ho's core files

---

## Part 1: System Analysis

### 1.1 Pai Ho's wkpup2 (Baseline - CORRECT)

#### Core Components
```
wkpup2/
├── gpio/1p1v/
│   ├── dependencies/scripts/simulation_script/auto_pvt/ver03/
│   │   ├── sim_pvt.sh (589 lines) - Main orchestration
│   │   ├── tb_gen/
│   │   │   ├── gen_tb.pl (570 lines ver03) - Testbench generator
│   │   │   └── pvt_loop.sh (723 lines) - PVT matrix iteration
│   │   ├── configuration/
│   │   │   ├── read_cfg.sh - Config parser
│   │   │   ├── read_corner.sh - Corner definitions
│   │   │   ├── read_supply.sh - Voltage tables
│   │   │   ├── table_corner_list.csv - Corner whitelist
│   │   │   ├── table_supply_list_ac.csv - AC voltages
│   │   │   └── table_supply_list_dc.csv - DC voltages
│   │   ├── data_extraction/
│   │   │   ├── extract_alt.sh - Result parser
│   │   │   └── move.sh - File organizer
│   │   └── runme_script/
│   │       └── runme_func.sh - Helper functions
│   ├── template/
│   │   └── sim_tx.sp (111 lines) - SPICE template
│   ├── config.cfg - 15-parameter configuration
│   ├── runme.sh - Entry point
│   └── log/ - Execution logs
```

#### Workflow (6 Stages)
```
1. gen (Generation):
   - Reads config.cfg
   - Calls pvt_loop.sh
   - Generates 84-324 testbenches via gen_tb.pl
   - Creates corner/extraction/temp/voltage directories

2. run (Simulation):
   - Submits jobs via nbjob
   - Executes SPICE for each testbench
   - Produces .mt0 measurement files

3. ext (Extraction):
   - Parses .mt0 files via extract_alt.sh
   - Extracts timing/power metrics
   - Creates CSV data files

4. srt (Sorting):
   - Aggregates all results
   - Generates creport.txt
   - Identifies min/max corners

5. bkp (Backup):
   - Creates 00bkp_YYYYMMDDHHMMSS/
   - Copies all results
   - Preserves complete simulation state

6. usr (User Script):
   - Optional post-processing
   - Custom analysis scripts
```

#### Key Files (MUST NEVER MODIFY)

**File 1: gen_tb.pl ver03 (570 lines)**
```perl
# Location: .../ver03/tb_gen/gen_tb.pl
# Purpose: Generate SPICE testbench from template
# Critical: 10 pattern matching rules, Line 52 preservation
# Version: ver03 (45 lines more than ver02)
```

**File 2: sim_pvt.sh (589 lines)**
```bash
# Location: .../ver03/sim_pvt.sh
# Purpose: Main orchestration script
# Stages: gen, run, ext, srt, bkp, usr
# Dependencies: pvt_loop.sh, read_cfg.sh
```

**File 3: pvt_loop.sh (723 lines)**
```bash
# Location: .../ver03/tb_gen/pvt_loop.sh
# Purpose: Iterate through PVT matrix
# Logic: Nested loops (corners × extractions × temps × voltages)
# Calls: gen_tb.pl for each combination
```

**File 4: CSV Configuration Tables**
```csv
# table_corner_list.csv - Defines valid corners
TT,typical,0,0,0,0
FFG,cworst_CCworst_T,1,1,0,0
SSG,cbest_CCbest_T,-1,-1,0,0
...

# table_supply_list_ac.csv - AC voltage definitions
v1min,0.99,0.99
v1nom,1.10,1.10
v1max,1.21,1.21
...
```

#### Validated Parameters (15 total)
```bash
1.  mode="prelay" | "postlay"
2.  vccn="1p1v" | "1p2v" | "1p8v"
3.  vcctx="1p1v" | "1p2v" | "1p8v"
4.  1st_supply_swp="all" | "v1min" | "v1nom" | "v1max" | ...
5.  2nd_supply_swp="all" | ...
6.  3rd_supply_swp="all" | ...
7.  condition="perf" | "func" | "htol"
8.  CPU="8" | "16" | "32"
9.  MEM="16" | "32" | "64"
10. alter_extraction="typical" | "cworst_CCworst_T" | "cbest_CCbest_T"
11. alter_string1="" (custom SPICE alter)
12. alter_string2="" (custom SPICE alter)
13. sim_mode="ac" | "dc"
14. gs_corner="NA" | corner_name
15. gf_corner="NA" | corner_name
16. vcc_vid="no" | "yes"
17. simulator="primesim" | "finesim"
18. postlay_cross_cornerlist="" (post-layout cross corners)
```

---

### 1.2 wkpup Automation (Current - BUGGY)

#### Architecture Issues

**Issue 1: Version Mismatch**
```bash
# wkpup uses:
script_path=".../auto_pvt/ver02"  # ❌ OLD VERSION
gen_tb.pl = 525 lines  # Missing 45 lines

# Should use:
script_path=".../auto_pvt/ver03"  # ✅ CURRENT
gen_tb.pl = 570 lines  # Has vccn_vcctx support
```

**Issue 2: Script Rewrite (+11% code inflation)**
```bash
# Pai Ho's baseline:
sim_pvt.sh = 589 lines
pvt_loop.sh = 723 lines
TOTAL = 1,312 lines

# wkpup automation:
sim_pvt_local.sh = 685 lines  (+96 lines, +16%)
local_pvt_loop.sh = 880 lines  (+157 lines, +22%)
TOTAL = 1,565 lines  (+253 lines, +19%)
```

**Issue 3: Known Bugs**
```bash
# Path mismatch (documented in CONSOLIDATED_DOCUMENTATION.md):
Generation: tt_ex="typical" → Creates TT/typical/typical_85/
Extraction: tt_ex="typ"     → Looks for TT/typ/typ_85/
Result: cp: No such file or directory  # ❌ FAILS

# Status: Fixed in latest version (all use "typical")
# Risk: Could regress without proper testing
```

#### Valuable Features (TO EXTRACT)

**Feature 1: Web User Interface**
```python
# Tornado web server (main_tornado.py)
# - HTML forms for job submission
# - Real-time progress via WebSocket
# - Result visualization
# - Job history browser

VALUE: ✅ User-friendly interface
RISK: ⚠️ LOW (pure presentation layer)
STATUS: EXTRACT and rebuild on Pai Ho's core
```

**Feature 2: Database Tracking**
```python
# SQLite database (database/simulation.db)
# Schema:
# - jobs (submission metadata)
# - results (parsed measurements)
# - configurations (parameter history)

VALUE: ✅ Historical tracking, searchability
RISK: ⚠️ MEDIUM (must accurately reflect Pai Ho's results)
STATUS: EXTRACT, validate data accuracy
```

**Feature 3: Flexible Temperature Selection**
```bash
# wkpup: User selects subset of temperatures
get_temperature_list() {
    # Reads from config.cfg
    # Returns: "m40 125" (user-selected)
}

# Pai Ho: Hardcoded full list
temperatures="m40 85 100 125"

VALUE: ✅ Flexibility for partial runs
RISK: ⚠️ HIGH (custom temps not validated by Pai Ho)
STATUS: EXTRACT with whitelist (only Pai Ho's temps allowed)
```

**Feature 4: Multi-Voltage Domain Support**
```
wkpup/
├── gpio/1p1v/
├── i3c/1p1v/
├── i3c/1p2v/
├── i3c/1p8v/
└── i3c/1p15v/

VALUE: ✅ Scalability across domains
RISK: ⚠️ LOW (each domain independent)
STATUS: EXTRACT, use symlinks to Pai Ho's scripts
```

**Feature 5: Background Job Management**
```python
# subprocess execution in background
# WebSocket progress monitoring
# Job queue management

VALUE: ✅ Concurrent job execution
RISK: ⚠️ LOW (orchestration layer only)
STATUS: EXTRACT unchanged
```

#### Features to REJECT

**Rejected 1: local_pvt_loop.sh Override**
```bash
# wkpup allows local script override
if [ -f "./local_pvt_loop.sh" ]; then
    source ./local_pvt_loop.sh  # ❌ BYPASSES PAI HO
fi

REASON: Defeats entire purpose of using validated baseline
STATUS: ❌ DO NOT IMPLEMENT
```

**Rejected 2: Custom Temperature Values**
```bash
# wkpup allows arbitrary temps (e.g., "50 75 90")
# Not validated by Pai Ho

REASON: Could produce nonsensical results
STATUS: ❌ DO NOT IMPLEMENT (use whitelist only)
```

**Rejected 3: Per-Temperature Voltage Config**
```bash
# Different voltages per temperature
get_voltages_for_temp -40  → "v1min_v2min"
get_voltages_for_temp 125  → "v1max_v2max"

REASON: Arbitrary combinations not validated
STATUS: ❌ DO NOT IMPLEMENT (use Pai Ho's CSV tables)
```

---

## Part 2: Architecture Design

### 2.1 Layered Architecture

```
┌────────────────────────────────────────────────────────┐
│                 USER INTERFACE LAYER                   │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Web Browser │  │   REST API   │  │  CLI Wrapper│ │
│  │  (HTML/JS)   │  │   (JSON)     │  │   (Bash)    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
└─────────┼──────────────────┼──────────────────┼────────┘
          │                  │                  │
          │ HTTP             │ HTTP             │ exec
          ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER (Python)              │
│                                                        │
│  ┌────────────────┐  ┌────────────────┐              │
│  │ Job Manager    │  │ Config         │              │
│  │ - Queue mgmt   │  │ Validator      │              │
│  │ - Progress     │  │ - Whitelist    │              │
│  │ - Notifications│  │ - Schema check │              │
│  └────────┬───────┘  └────────┬───────┘              │
│           │                    │                       │
│  ┌────────┴────────┐  ┌────────┴───────┐             │
│  │ Database        │  │ Result Parser  │             │
│  │ Tracker         │  │ - creport.txt  │             │
│  │ - SQLite        │  │ - .mt0 files   │             │
│  └─────────────────┘  └────────────────┘             │
└─────────┬──────────────────────────────────────────────┘
          │
          │ subprocess.run(['bash', 'sim_pvt.sh', ...])
          ▼
┌────────────────────────────────────────────────────────┐
│       PAI HO'S SIMULATION CORE (UNTOUCHED)             │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ sim_pvt.sh (589 lines) - Main orchestrator       │ │
│  │   ├── gen  → pvt_loop.sh → gen_tb.pl ver03      │ │
│  │   ├── run  → nbjob → SPICE simulation           │ │
│  │   ├── ext  → extract_alt.sh → parse .mt0        │ │
│  │   ├── srt  → aggregate → creport.txt            │ │
│  │   ├── bkp  → 00bkp_timestamp/ → archive         │ │
│  │   └── usr  → optional user scripts              │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Configuration:                                        │
│  - config.cfg (15 parameters)                         │
│  - table_corner_list.csv                              │
│  - table_supply_list_*.csv                            │
│                                                        │
│  Templates:                                            │
│  - template/sim_tx.sp (Line 52 critical)              │
└────────┬───────────────────────────────────────────────┘
         │
         │ SPICE execution
         ▼
┌────────────────────────────────────────────────────────┐
│                 RESULTS LAYER (Python)                 │
│                                                        │
│  ┌─────────────────┐  ┌──────────────────┐           │
│  │ Result Parser   │  │ Visualization    │           │
│  │ - Read Pai Ho's │  │ - Graphs         │           │
│  │   creport.txt   │  │ - Tables         │           │
│  │ - Validate      │  │ - Comparisons    │           │
│  └────────┬────────┘  └──────────────────┘           │
│           │                                            │
│           ▼                                            │
│  ┌─────────────────┐                                  │
│  │ Database        │                                  │
│  │ Storage         │                                  │
│  └─────────────────┘                                  │
└────────────────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
wkpup2_enhanced/
├── pai_ho_core/          # Pai Ho's ORIGINAL files (read-only)
│   └── ver03/
│       ├── sim_pvt.sh
│       ├── tb_gen/
│       │   ├── gen_tb.pl
│       │   └── pvt_loop.sh
│       ├── configuration/
│       │   ├── read_cfg.sh
│       │   ├── read_corner.sh
│       │   ├── read_supply.sh
│       │   └── *.csv
│       ├── data_extraction/
│       └── runme_script/
│
├── web_automation/       # NEW: Web interface layer
│   ├── main.py           # Tornado web server
│   ├── modules/
│   │   ├── config_generator.py    # Generate config.cfg
│   │   ├── paiho_executor.py      # Execute Pai Ho's scripts
│   │   ├── job_manager.py         # Background job queue
│   │   ├── database.py            # SQLite tracking
│   │   └── result_parser.py       # Parse creport.txt
│   ├── templates/
│   │   ├── index.html             # Job submission form
│   │   ├── results.html           # Result viewer
│   │   └── history.html           # Job history
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── tests/
│       ├── test_bit_identical.py  # Critical validation
│       ├── test_config_gen.py
│       ├── test_database.py
│       └── test_integration.py
│
├── voltage_domains/      # NEW: Multi-domain support
│   ├── domain_manager.py
│   ├── gpio/
│   │   └── 1p1v/        # Symlinks to pai_ho_core/
│   └── i3c/
│       ├── 1p1v/        # Symlinks to pai_ho_core/
│       ├── 1p2v/        # Symlinks to pai_ho_core/
│       ├── 1p8v/        # Symlinks to pai_ho_core/
│       └── 1p15v/       # Symlinks to pai_ho_core/
│
├── config/               # System configuration
│   ├── web_config.yaml
│   ├── database_config.yaml
│   └── domain_config.yaml
│
├── logs/                 # Application logs
│   ├── web_server.log
│   ├── job_execution.log
│   └── database.log
│
├── database/             # SQLite database
│   └── simulation_tracking.db
│
└── docs/                 # Documentation
    ├── COMPLETE_IMPLEMENTATION_PLAN.md (this file)
    ├── API_REFERENCE.md
    ├── USER_GUIDE.md
    └── TROUBLESHOOTING.md
```

### 2.3 Data Flow

```
USER INTERACTION:
┌─────────────┐
│ User visits │
│ web UI      │
└──────┬──────┘
       │
       │ Selects parameters:
       │ - mode: prelay
       │ - vccn: 1p1v
       │ - sim_mode: ac
       │ - condition: perf
       ▼
┌──────────────────────────┐
│ Web Server (main.py)     │
│ - Receives form POST     │
│ - Validates input        │
└──────┬───────────────────┘
       │
       │ Calls config_generator.py
       ▼
┌──────────────────────────────────┐
│ Config Generator                 │
│ 1. Validate against whitelists   │
│ 2. Read Pai Ho's CSV tables      │
│ 3. Generate config.cfg           │
└──────┬───────────────────────────┘
       │
       │ config.cfg (Pai Ho's format)
       ▼
┌──────────────────────────────────┐
│ Database Tracker                 │
│ - Record job submission          │
│ - Store metadata                 │
└──────┬───────────────────────────┘
       │
       │ Calls paiho_executor.py
       ▼
┌──────────────────────────────────┐
│ Pai Ho Executor                  │
│ subprocess.run([                 │
│   'bash',                        │
│   'pai_ho_core/sim_pvt.sh',     │
│   'config.cfg',                  │
│   'gen'                          │
│ ])                               │
└──────┬───────────────────────────┘
       │
       │ Executes Pai Ho's ORIGINAL script
       ▼
┌─────────────────────────────────────────────┐
│ PAI HO'S sim_pvt.sh                         │
│ Stage 1: gen                                │
│   - Reads config.cfg                        │
│   - Sources read_cfg.sh                     │
│   - Calls pvt_loop.sh                       │
│     ├── Iterates corners (TT, FFG, ...)    │
│     ├── Iterates temps (m40, 85, ...)      │
│     ├── Iterates voltages (v1min, ...)     │
│     └── Calls gen_tb.pl for each combo     │
│         └── Generates testbench SPICE      │
│   - Creates directory structure             │
│   - Generates 84-324 netlists               │
└──────┬──────────────────────────────────────┘
       │
       │ Returns to executor
       ▼
┌──────────────────────────────────┐
│ Pai Ho Executor                  │
│ - Check exit code                │
│ - Capture stdout/stderr          │
└──────┬───────────────────────────┘
       │
       │ Calls stages: run, ext, srt, bkp
       ▼
┌──────────────────────────────────┐
│ PAI HO'S sim_pvt.sh (stages)     │
│ Stage 2: run → SPICE simulation  │
│ Stage 3: ext → Parse .mt0        │
│ Stage 4: srt → Generate creport  │
│ Stage 5: bkp → Archive results   │
└──────┬───────────────────────────┘
       │
       │ Results: 00bkp_timestamp/creport.txt
       ▼
┌──────────────────────────────────┐
│ Result Parser                    │
│ - Read creport.txt (READ-ONLY)   │
│ - Parse measurements             │
│ - Validate data integrity        │
└──────┬───────────────────────────┘
       │
       │ Parsed results (JSON)
       ▼
┌──────────────────────────────────┐
│ Database Tracker                 │
│ - Store results in database      │
│ - Update job status              │
│ - Record completion time         │
└──────┬───────────────────────────┘
       │
       │ Job complete notification
       ▼
┌──────────────────────────────────┐
│ Web Server                       │
│ - Update progress bar            │
│ - Show results to user           │
│ - Provide download links         │
└──────────────────────────────────┘
```

---

## Part 3: Detailed Implementation

### 3.1 Configuration Generator (COMPLETE CODE)

**File**: `web_automation/modules/config_generator.py`

```python
"""
Configuration Generator for Pai Ho's sim_pvt.sh

CRITICAL REQUIREMENTS:
1. ONLY generate parameters from Pai Ho's whitelists
2. Use Pai Ho's EXACT config.cfg format
3. Validate ALL inputs before generation
4. Never allow custom values not in Pai Ho's CSV tables

Author: Web Automation Layer
Version: 1.0
Dependencies: Pai Ho's CSV files (table_corner_list.csv, table_supply_list_*.csv)
"""

import os
import csv
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of parameter validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]


class PaiHoConfigGenerator:
    """
    Generate config.cfg compatible with Pai Ho's sim_pvt.sh
    
    This class ensures 100% compatibility with Pai Ho's parameter expectations.
    All parameters are validated against Pai Ho's CSV whitelists before generation.
    """
    
    # Pai Ho's validated parameter values (from COMPREHENSIVE_ANALYSIS.md)
    VALID_MODES = {'prelay', 'postlay'}
    VALID_SIM_MODES = {'ac', 'dc'}
    VALID_CONDITIONS = {'perf', 'func', 'htol'}
    VALID_SIMULATORS = {'primesim', 'finesim'}
    VALID_VCC_VID = {'no', 'yes'}
    
    # Pai Ho's default values (use when user doesn't specify)
    DEFAULTS = {
        'mode': 'prelay',
        'vccn': '1p1v',
        'vcctx': '1p1v',  # Defaults to vccn if not specified
        '1st_supply_swp': 'all',
        '2nd_supply_swp': 'all',
        '3rd_supply_swp': 'all',
        'condition': 'perf',
        'CPU': '8',
        'MEM': '16',
        'alter_extraction': 'typical',
        'alter_string1': '',
        'alter_string2': '',
        'sim_mode': 'ac',
        'gs_corner': 'NA',
        'gf_corner': 'NA',
        'vcc_vid': 'no',
        'simulator': 'primesim',
        'postlay_cross_cornerlist': '',
    }
    
    def __init__(self, paiho_csv_dir: str):
        """
        Initialize configuration generator
        
        Args:
            paiho_csv_dir: Path to Pai Ho's configuration/*.csv files
                          Example: /path/to/ver03/configuration/
        
        Raises:
            FileNotFoundError: If CSV directory or required files not found
        """
        self.csv_dir = Path(paiho_csv_dir)
        
        if not self.csv_dir.exists():
            raise FileNotFoundError(f"Pai Ho's CSV directory not found: {self.csv_dir}")
        
        # Load whitelists from Pai Ho's CSV files
        self.valid_corners = self._load_corners()
        self.valid_voltages = self._load_voltages()
        self.valid_extractions = self._load_extractions()
        
        # Validate we loaded data successfully
        if not self.valid_corners:
            raise ValueError("No corners loaded from table_corner_list.csv")
        if not self.valid_voltages['ac'] and not self.valid_voltages['dc']:
            raise ValueError("No voltages loaded from table_supply_list_*.csv")
    
    def _load_corners(self) -> Set[str]:
        """
        Load valid corner names from Pai Ho's table_corner_list.csv
        
        CSV Format:
        corner_name,extraction,nmos,pmos,rs,ls
        TT,typical,0,0,0,0
        FFG,cworst_CCworst_T,1,1,0,0
        ...
        
        Returns:
            Set of valid corner names (e.g., {'TT', 'FFG', 'SSG', ...})
        """
        csv_file = self.csv_dir / 'table_corner_list.csv'
        
        if not csv_file.exists():
            raise FileNotFoundError(f"Corner CSV not found: {csv_file}")
        
        corners = set()
        
        with open(csv_file, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                if line.strip().startswith('#') or not line.strip():
                    continue
                
                # Parse CSV (first column is corner name)
                parts = line.strip().split(',')
                if parts:
                    corners.add(parts[0].strip())
        
        return corners
    
    def _load_extractions(self) -> Set[str]:
        """
        Load valid extraction names from Pai Ho's table_corner_list.csv
        
        Returns:
            Set of valid extraction names (e.g., {'typical', 'cworst_CCworst_T', ...})
        """
        csv_file = self.csv_dir / 'table_corner_list.csv'
        
        extractions = set()
        
        with open(csv_file, 'r') as f:
            for line in f:
                if line.strip().startswith('#') or not line.strip():
                    continue
                
                # Second column is extraction name
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    extractions.add(parts[1].strip())
        
        return extractions
    
    def _load_voltages(self) -> Dict[str, Set[str]]:
        """
        Load valid voltage names from Pai Ho's table_supply_list_*.csv
        
        CSV Format:
        voltage_name,vccn,vcctx
        v1min,0.99,0.99
        v1nom,1.10,1.10
        ...
        
        Returns:
            Dict with 'ac' and 'dc' keys, each containing set of voltage names
        """
        voltages = {'ac': set(), 'dc': set()}
        
        for sim_mode in ['ac', 'dc']:
            csv_file = self.csv_dir / f'table_supply_list_{sim_mode}.csv'
            
            if not csv_file.exists():
                print(f"WARNING: Voltage CSV not found: {csv_file}")
                continue
            
            with open(csv_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('#') or not line.strip():
                        continue
                    
                    # First column is voltage name
                    parts = line.strip().split(',')
                    if parts:
                        voltages[sim_mode].add(parts[0].strip())
        
        return voltages
    
    def validate_parameters(self, params: Dict) -> ValidationResult:
        """
        Validate ALL parameters against Pai Ho's whitelists
        
        Args:
            params: Dictionary of user-provided parameters
        
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Validate mode
        if 'mode' in params:
            if params['mode'] not in self.VALID_MODES:
                errors.append(f"Invalid mode '{params['mode']}'. "
                            f"Valid: {sorted(self.VALID_MODES)}")
        
        # Validate sim_mode
        if 'sim_mode' in params:
            if params['sim_mode'] not in self.VALID_SIM_MODES:
                errors.append(f"Invalid sim_mode '{params['sim_mode']}'. "
                            f"Valid: {sorted(self.VALID_SIM_MODES)}")
        
        # Validate condition
        if 'condition' in params:
            if params['condition'] not in self.VALID_CONDITIONS:
                errors.append(f"Invalid condition '{params['condition']}'. "
                            f"Valid: {sorted(self.VALID_CONDITIONS)}")
        
        # Validate simulator
        if 'simulator' in params:
            if params['simulator'] not in self.VALID_SIMULATORS:
                errors.append(f"Invalid simulator '{params['simulator']}'. "
                            f"Valid: {sorted(self.VALID_SIMULATORS)}")
        
        # Validate vcc_vid
        if 'vcc_vid' in params:
            if params['vcc_vid'] not in self.VALID_VCC_VID:
                errors.append(f"Invalid vcc_vid '{params['vcc_vid']}'. "
                            f"Valid: {sorted(self.VALID_VCC_VID)}")
        
        # Validate corners (if specified)
        if 'corner_selection' in params:
            # User can specify subset of corners
            requested = params['corner_selection'].split(',')
            for corner in requested:
                corner = corner.strip()
                if corner and corner not in self.valid_corners:
                    errors.append(f"Invalid corner '{corner}'. "
                                f"Valid: {sorted(self.valid_corners)}")
        
        # Validate voltages
        sim_mode = params.get('sim_mode', self.DEFAULTS['sim_mode'])
        if 'voltage_selection' in params:
            requested = params['voltage_selection'].split(',')
            for voltage in requested:
                voltage = voltage.strip()
                if voltage and voltage not in self.valid_voltages[sim_mode]:
                    errors.append(f"Invalid voltage '{voltage}' for {sim_mode}. "
                                f"Valid: {sorted(self.valid_voltages[sim_mode])}")
        
        # Validate extraction
        if 'alter_extraction' in params:
            extraction = params['alter_extraction']
            if extraction and extraction not in self.valid_extractions:
                errors.append(f"Invalid extraction '{extraction}'. "
                            f"Valid: {sorted(self.valid_extractions)}")
        
        # Validate CPU/MEM are integers
        if 'CPU' in params:
            try:
                cpu = int(params['CPU'])
                if cpu < 1 or cpu > 128:
                    warnings.append(f"CPU count {cpu} is outside typical range (1-128)")
            except ValueError:
                errors.append(f"CPU must be integer, got: {params['CPU']}")
        
        if 'MEM' in params:
            try:
                mem = int(params['MEM'])
                if mem < 1 or mem > 512:
                    warnings.append(f"MEM {mem}GB is outside typical range (1-512)")
            except ValueError:
                errors.append(f"MEM must be integer, got: {params['MEM']}")
        
        return ValidationResult(
            valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings
        )
    
    def generate(self, user_params: Dict, output_path: Optional[str] = None) -> str:
        """
        Generate config.cfg from user parameters
        
        Args:
            user_params: Dictionary of user-provided parameters
            output_path: Optional path for output file (default: /tmp/config.cfg)
        
        Returns:
            Path to generated config.cfg file
        
        Raises:
            ValueError: If validation fails
        """
        # Validate FIRST
        validation = self.validate_parameters(user_params)
        
        if not validation.valid:
            error_msg = "Parameter validation failed:\n" + "\n".join(validation.errors)
            raise ValueError(error_msg)
        
        # Print warnings (don't fail, just inform)
        for warning in validation.warnings:
            print(f"WARNING: {warning}")
        
        # Merge user params with defaults
        config = self.DEFAULTS.copy()
        config.update(user_params)
        
        # Special handling: vcctx defaults to vccn if not specified
        if 'vcctx' not in user_params and 'vccn' in user_params:
            config['vcctx'] = user_params['vccn']
        
        # Generate config.cfg content in Pai Ho's EXACT format
        config_lines = [
            "# Auto-generated config.cfg",
            "# Compatible with Pai Ho's sim_pvt.sh ver03",
            "# Generated by web automation layer",
            "",
            f"mode={config['mode']}",
            f"vccn={config['vccn']}",
            f"vcctx={config['vcctx']}",
            f"1st_supply_swp={config['1st_supply_swp']}",
            f"2nd_supply_swp={config['2nd_supply_swp']}",
            f"3rd_supply_swp={config['3rd_supply_swp']}",
            f"condition={config['condition']}",
            f"CPU={config['CPU']}",
            f"MEM={config['MEM']}",
            f"alter_extraction={config['alter_extraction']}",
            f"alter_string1={config['alter_string1']}",
            f"alter_string2={config['alter_string2']}",
            f"sim_mode={config['sim_mode']}",
            f"gs_corner={config['gs_corner']}",
            f"gf_corner={config['gf_corner']}",
            f"vcc_vid={config['vcc_vid']}",
            f"simulator={config['simulator']}",
            f"postlay_cross_cornerlist={config['postlay_cross_cornerlist']}",
            ""
        ]
        
        content = "\n".join(config_lines)
        
        # Write to file
        if output_path is None:
            output_path = '/tmp/generated_config.cfg'
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"Generated config.cfg: {output_path}")
        return output_path
    
    def get_valid_options(self) -> Dict:
        """
        Get all valid options for UI dropdowns
        
        Returns:
            Dictionary with all valid parameter values
        """
        return {
            'modes': sorted(self.VALID_MODES),
            'sim_modes': sorted(self.VALID_SIM_MODES),
            'conditions': sorted(self.VALID_CONDITIONS),
            'simulators': sorted(self.VALID_SIMULATORS),
            'corners': sorted(self.valid_corners),
            'voltages_ac': sorted(self.valid_voltages['ac']),
            'voltages_dc': sorted(self.valid_voltages['dc']),
            'extractions': sorted(self.valid_extractions),
            'vcc_vid': sorted(self.VALID_VCC_VID),
        }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    # Initialize generator with Pai Ho's CSV directory
    csv_dir = '/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03/configuration'
    
    generator = PaiHoConfigGenerator(csv_dir)
    
    # Example 1: Valid parameters
    print("=" * 70)
    print("Example 1: Valid parameters")
    print("=" * 70)
    
    valid_params = {
        'mode': 'prelay',
        'sim_mode': 'ac',
        'vccn': '1p1v',
        'condition': 'perf',
        'CPU': '16',
        'MEM': '32',
    }
    
    try:
        config_file = generator.generate(valid_params)
        print(f"✅ SUCCESS: Generated {config_file}")
        
        # Show generated content
        with open(config_file, 'r') as f:
            print("\nGenerated config.cfg:")
            print(f.read())
    except ValueError as e:
        print(f"❌ ERROR: {e}")
    
    # Example 2: Invalid parameters
    print("\n" + "=" * 70)
    print("Example 2: Invalid parameters (should fail)")
    print("=" * 70)
    
    invalid_params = {
        'mode': 'invalid_mode',  # ❌ Not in whitelist
        'sim_mode': 'ac',
        'vccn': '1p1v',
    }
    
    try:
        config_file = generator.generate(invalid_params)
        print(f"❌ UNEXPECTED: Should have failed but generated {config_file}")
    except ValueError as e:
        print(f"✅ EXPECTED ERROR: {e}")
    
    # Example 3: Get valid options (for UI dropdowns)
    print("\n" + "=" * 70)
    print("Example 3: Valid options for UI")
    print("=" * 70)
    
    options = generator.get_valid_options()
    print(f"Available corners: {options['corners']}")
    print(f"Available AC voltages: {options['voltages_ac']}")
    print(f"Available DC voltages: {options['voltages_dc']}")
```

---

### 3.2 Pai Ho Executor (COMPLETE CODE)

**File**: `web_automation/modules/paiho_executor.py`

```python
"""
Pai Ho Executor - Execute Pai Ho's sim_pvt.sh WITHOUT modification

CRITICAL REQUIREMENTS:
1. NEVER modify Pai Ho's original scripts
2. Execute via subprocess ONLY
3. Validate script version before execution
4. Capture ALL output for debugging
5. Handle errors gracefully

Author: Web Automation Layer
Version: 1.0
Dependencies: Pai Ho's sim_pvt.sh ver03
"""

import subprocess
import os
import shutil
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import hashlib


@dataclass
class SimulationResult:
    """Result of Pai Ho's simulation execution"""
    job_id: str
    stage: str
    status: str  # 'success', 'failed', 'running', 'killed'
    stdout: str
    stderr: str
    start_time: datetime
    end_time: Optional[datetime]
    exit_code: int
    result_dir: Optional[str]
    duration_seconds: float = 0.0
    
    def __post_init__(self):
        """Calculate duration if end_time is set"""
        if self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()


class PaiHoExecutor:
    """
    Execute Pai Ho's simulation scripts WITHOUT modification
    
    This executor acts as a wrapper around Pai Ho's sim_pvt.sh,
    ensuring 100% compatibility while providing user-friendly interface.
    """
    
    # Expected file sizes for version verification
    EXPECTED_VERSIONS = {
        'sim_pvt.sh': {
            'ver03': 589,  # lines
            'sha256': None,  # Optional: add checksum for extra validation
        },
        'gen_tb.pl': {
            'ver03': 570,  # lines (45 more than ver02)
            'sha256': None,
        },
        'pvt_loop.sh': {
            'ver03': 723,  # lines
            'sha256': None,
        }
    }
    
    def __init__(self, paiho_workdir: str, paiho_script_dir: str, strict_validation: bool = True):
        """
        Initialize Pai Ho executor
        
        Args:
            paiho_workdir: Working directory (e.g., gpio/1p1v/)
            paiho_script_dir: Path to Pai Ho's ver03 scripts
            strict_validation: If True, fail on version mismatch
        
        Raises:
            FileNotFoundError: If required scripts not found
            ValueError: If script version validation fails
        """
        self.workdir = Path(paiho_workdir)
        self.script_dir = Path(paiho_script_dir)
        self.strict_validation = strict_validation
        
        # Pai Ho's ORIGINAL scripts
        self.sim_pvt_script = self.script_dir / 'sim_pvt.sh'
        self.gen_tb_script = self.script_dir / 'tb_gen' / 'gen_tb.pl'
        self.pvt_loop_script = self.script_dir / 'tb_gen' / 'pvt_loop.sh'
        
        # Verify scripts exist and are correct version
        self._verify_scripts()
        
        # Create log directory if needed
        self.log_dir = self.workdir / 'log' / 'web_automation'
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _count_lines(self, filepath: Path) -> int:
        """Count lines in a file"""
        try:
            with open(filepath, 'r') as f:
                return len(f.readlines())
        except Exception as e:
            print(f"WARNING: Could not count lines in {filepath}: {e}")
            return 0
    
    def _compute_checksum(self, filepath: Path) -> str:
        """Compute SHA256 checksum of file"""
        try:
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"WARNING: Could not compute checksum for {filepath}: {e}")
            return ""
    
    def _verify_scripts(self):
        """
        Verify Pai Ho's scripts exist and are correct version
        
        Checks:
        1. File exists
        2. Line count matches expected (ver03)
        3. File is readable
        4. (Optional) Checksum matches
        
        Raises:
            FileNotFoundError: If required script not found
            ValueError: If version validation fails (strict mode only)
        """
        print("Verifying Pai Ho's scripts...")
        
        # Check sim_pvt.sh
        if not self.sim_pvt_script.exists():
            raise FileNotFoundError(f"Pai Ho's sim_pvt.sh not found: {self.sim_pvt_script}")
        
        sim_pvt_lines = self._count_lines(self.sim_pvt_script)
        expected_lines = self.EXPECTED_VERSIONS['sim_pvt.sh']['ver03']
        
        if sim_pvt_lines != expected_lines:
            msg = (f"WARNING: sim_pvt.sh has {sim_pvt_lines} lines, "
                  f"expected {expected_lines} (ver03)")
            if self.strict_validation:
                raise ValueError(msg + " - Set strict_validation=False to bypass")
            else:
                print(msg)
        
        # Check gen_tb.pl
        if not self.gen_tb_script.exists():
            raise FileNotFoundError(f"Pai Ho's gen_tb.pl not found: {self.gen_tb_script}")
        
        gen_tb_lines = self._count_lines(self.gen_tb_script)
        expected_gen_tb = self.EXPECTED_VERSIONS['gen_tb.pl']['ver03']
        
        if gen_tb_lines != expected_gen_tb:
            msg = (f"WARNING: gen_tb.pl has {gen_tb_lines} lines, "
                  f"expected {expected_gen_tb} (ver03)")
            if self.strict_validation:
                raise ValueError(msg + " - May be using ver02 (525 lines)!")
            else:
                print(msg)
        
        # Check pvt_loop.sh
        if not self.pvt_loop_script.exists():
            raise FileNotFoundError(f"Pai Ho's pvt_loop.sh not found: {self.pvt_loop_script}")
        
        pvt_loop_lines = self._count_lines(self.pvt_loop_script)
        expected_pvt = self.EXPECTED_VERSIONS['pvt_loop.sh']['ver03']
        
        if pvt_loop_lines != expected_pvt:
            msg = (f"WARNING: pvt_loop.sh has {pvt_loop_lines} lines, "
                  f"expected {expected_pvt} (ver03)")
            if self.strict_validation:
                raise ValueError(msg)
            else:
                print(msg)
        
        # Verify files are readable (not write-protected is OK, but warn)
        for script in [self.sim_pvt_script, self.gen_tb_script, self.pvt_loop_script]:
            if not os.access(script, os.R_OK):
                raise PermissionError(f"Cannot read {script}")
            
            if os.access(script, os.W_OK):
                print(f"WARNING: {script.name} is writable - consider chmod 444 for protection")
        
        print("✅ Script verification passed")
    
    def execute_stage(self, config_file: str, stage: str) -> SimulationResult:
        """
        Execute ONE stage of Pai Ho's simulation
        
        Args:
            config_file: Path to config.cfg (Pai Ho's format)
            stage: 'gen', 'run', 'ext', 'srt', 'bkp', or 'usr'
        
        Returns:
            SimulationResult with execution details
        
        Raises:
            ValueError: If stage is invalid
            FileNotFoundError: If config file not found
        """
        # Validate stage
        valid_stages = ['gen', 'run', 'ext', 'srt', 'bkp', 'usr']
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage '{stage}'. Valid: {valid_stages}")
        
        # Verify config file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        # Copy config.cfg to Pai Ho's working directory
        dest_config = self.workdir / 'config.cfg'
        shutil.copy(config_file, dest_config)
        print(f"Copied config to: {dest_config}")
        
        # Generate job ID
        job_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stage}"
        start_time = datetime.now()
        
        # Construct command (call Pai Ho's ORIGINAL sim_pvt.sh)
        cmd = [
            'bash',
            str(self.sim_pvt_script),
            str(dest_config),
            stage
        ]
        
        # Log the command
        log_file = self.log_dir / f"{job_id}.log"
        print(f"Executing: {' '.join(cmd)}")
        print(f"Working directory: {self.workdir}")
        print(f"Log file: {log_file}")
        
        # Execute Pai Ho's script
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workdir,  # Run in Pai Ho's working directory
                capture_output=True,
                text=True,
                env=os.environ.copy(),  # Pass through environment
                timeout=36000  # 10 hour timeout (adjust as needed)
            )
            
            end_time = datetime.now()
            exit_code = result.returncode
            status = 'success' if exit_code == 0 else 'failed'
            
        except subprocess.TimeoutExpired as e:
            end_time = datetime.now()
            exit_code = -1
            status = 'killed'
            result = type('obj', (object,), {
                'stdout': str(e.stdout) if e.stdout else '',
                'stderr': f"TIMEOUT after {e.timeout}s\n" + (str(e.stderr) if e.stderr else '')
            })()
        
        # Save log file
        with open(log_file, 'w') as f:
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Start: {start_time}\n")
            f.write(f"End: {end_time}\n")
            f.write(f"Exit code: {exit_code}\n")
            f.write(f"\n{'=' * 70}\nSTDOUT:\n{'=' * 70}\n")
            f.write(result.stdout)
            f.write(f"\n{'=' * 70}\nSTDERR:\n{'=' * 70}\n")
            f.write(result.stderr)
        
        # Determine result directory
        result_dir = None
        if status == 'success' and stage == 'bkp':
            # Pai Ho creates 00bkp_YYYYMMDDHHMMSS/ directory
            bkp_dirs = list(self.workdir.glob('00bkp_*'))
            if bkp_dirs:
                # Get most recent
                result_dir = str(sorted(bkp_dirs, key=lambda p: p.name)[-1])
        
        return SimulationResult(
            job_id=job_id,
            stage=stage,
            status=status,
            stdout=result.stdout,
            stderr=result.stderr,
            start_time=start_time,
            end_time=end_time,
            exit_code=exit_code,
            result_dir=result_dir
        )
    
    def execute_full_workflow(self, config_file: str, stages: Optional[List[str]] = None) -> List[SimulationResult]:
        """
        Execute complete Pai Ho's workflow
        
        Default workflow: gen → run → ext → srt → bkp
        
        Args:
            config_file: Path to config.cfg
            stages: Optional list of stages (default: ['gen', 'run', 'ext', 'srt', 'bkp'])
        
        Returns:
            List of SimulationResult for each stage
        """
        if stages is None:
            stages = ['gen', 'run', 'ext', 'srt', 'bkp']
        
        results = []
        overall_start = datetime.now()
        
        print(f"\n{'=' * 70}")
        print(f"Starting full workflow: {' → '.join(stages)}")
        print(f"{'=' * 70}\n")
        
        for i, stage in enumerate(stages, 1):
            print(f"\n[{i}/{len(stages)}] Executing stage: {stage}")
            print("-" * 70)
            
            result = self.execute_stage(config_file, stage)
            results.append(result)
            
            if result.status != 'success':
                print(f"\n❌ Stage '{stage}' FAILED")
                print(f"Exit code: {result.exit_code}")
                print(f"Error output:\n{result.stderr}")
                print(f"\nStopping workflow (Pai Ho's behavior)")
                break
            else:
                print(f"✅ Stage '{stage}' completed ({result.duration_seconds:.1f}s)")
        
        overall_end = datetime.now()
        overall_duration = (overall_end - overall_start).total_seconds()
        
        print(f"\n{'=' * 70}")
        print(f"Workflow complete")
        print(f"Total time: {overall_duration:.1f}s ({overall_duration/60:.1f}m)")
        print(f"Stages completed: {sum(1 for r in results if r.status == 'success')}/{len(stages)}")
        print(f"{'=' * 70}\n")
        
        return results
    
    def get_simulation_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status of a running/completed simulation
        
        Args:
            job_id: Job identifier
        
        Returns:
            Dictionary with status info, or None if not found
        """
        log_file = self.log_dir / f"{job_id}.log"
        
        if not log_file.exists():
            return None
        
        # Parse log file
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract info (simplified - full implementation would parse structured data)
        status = {
            'job_id': job_id,
            'log_file': str(log_file),
            'exists': True,
            # Could parse more details from log
        }
        
        return status


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == '__main__':
    # Initialize executor
    workdir = '/nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup2/gpio/1p1v'
    script_dir = '/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03'
    
    executor = PaiHoExecutor(workdir, script_dir, strict_validation=True)
    
    # Example 1: Execute single stage
    print("=" * 70)
    print("Example 1: Execute single stage (gen)")
    print("=" * 70)
    
    config_file = '/tmp/test_config.cfg'
    result = executor.execute_stage(config_file, 'gen')
    
    if result.status == 'success':
        print(f"✅ Generation successful")
        print(f"Duration: {result.duration_seconds:.1f}s")
    else:
        print(f"❌ Generation failed")
        print(f"Error: {result.stderr}")
    
    # Example 2: Execute full workflow
    print("\n" + "=" * 70)
    print("Example 2: Execute full workflow")
    print("=" * 70)
    
    results = executor.execute_full_workflow(config_file)
    
    # Print summary
    print("\nSummary:")
    for result in results:
        status_icon = "✅" if result.status == 'success' else "❌"
        print(f"{status_icon} {result.stage:5s}: {result.status:8s} ({result.duration_seconds:6.1f}s)")
```

---

### 3.3 Web Server Implementation (COMPLETE CODE)

**File**: `web_automation/main.py`

```python
"""
Tornado Web Server - User-Friendly Interface for Pai Ho's Simulation Core

This web server provides a user-friendly interface while maintaining 100%
compatibility with Pai Ho's validated simulation core.

Features:
- Job submission via web forms
- Real-time progress monitoring (WebSocket)
- Result visualization
- Job history browser
- Multi-user support

Author: Web Automation Layer
Version: 1.0
Port: 8888 (default)
"""

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape
import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import our modules
from modules.config_generator import PaiHoConfigGenerator, ValidationResult
from modules.paiho_executor import PaiHoExecutor, SimulationResult
from modules.database import SimulationDatabase
from modules.job_manager import JobManager, Job
from modules.result_parser import ResultParser

# Configuration
PAIHO_CSV_DIR = os.getenv('PAIHO_CSV_DIR', 
    '/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03/configuration')
PAIHO_SCRIPT_DIR = os.getenv('PAIHO_SCRIPT_DIR',
    '/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03')
PAIHO_WORKDIR = os.getenv('PAIHO_WORKDIR',
    '/nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup2/gpio/1p1v')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/simulation_tracking.db')

# Global instances
config_generator = PaiHoConfigGenerator(PAIHO_CSV_DIR)
executor = PaiHoExecutor(PAIHO_WORKDIR, PAIHO_SCRIPT_DIR)
database = SimulationDatabase(DATABASE_PATH)
job_manager = JobManager(executor, database)


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with common functionality"""
    
    def get_current_user(self):
        """Get current user from cookie or environment"""
        user = self.get_secure_cookie("user")
        if user:
            return user.decode('utf-8')
        return os.getenv('USER', 'unknown')
    
    def write_json(self, data: Dict):
        """Write JSON response"""
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data, indent=2))


class IndexHandler(BaseHandler):
    """Main page - job submission form"""
    
    def get(self):
        # Get valid options for dropdowns
        options = config_generator.get_valid_options()
        
        self.render('templates/index.html',
                   user=self.get_current_user(),
                   options=options,
                   defaults=config_generator.DEFAULTS)


class SubmitHandler(BaseHandler):
    """Handle job submission"""
    
    async def post(self):
        try:
            # Extract parameters from form
            user_params = {
                'mode': self.get_argument('mode'),
                'sim_mode': self.get_argument('sim_mode'),
                'vccn': self.get_argument('vccn'),
                'vcctx': self.get_argument('vcctx', None),
                'condition': self.get_argument('condition'),
                'CPU': self.get_argument('CPU', '8'),
                'MEM': self.get_argument('MEM', '16'),
                'simulator': self.get_argument('simulator', 'primesim'),
                'alter_extraction': self.get_argument('alter_extraction', 'typical'),
                '1st_supply_swp': self.get_argument('1st_supply_swp', 'all'),
                '2nd_supply_swp': self.get_argument('2nd_supply_swp', 'all'),
                '3rd_supply_swp': self.get_argument('3rd_supply_swp', 'all'),
            }
            
            # Generate config.cfg (with validation)
            config_file = config_generator.generate(user_params)
            
            # Submit job to background queue
            job_id = await job_manager.submit_job(
                config_file=config_file,
                user=self.get_current_user(),
                params=user_params
            )
            
            # Return success with job_id
            self.write_json({
                'status': 'success',
                'job_id': job_id,
                'message': 'Job submitted successfully',
                'config_file': config_file
            })
            
        except ValueError as e:
            # Validation error
            self.set_status(400)
            self.write_json({
                'status': 'error',
                'error_type': 'validation',
                'message': str(e)
            })
            
        except Exception as e:
            # Other errors
            self.set_status(500)
            self.write_json({
                'status': 'error',
                'error_type': 'server',
                'message': f'Server error: {str(e)}'
            })


class JobStatusHandler(BaseHandler):
    """Get status of a specific job"""
    
    def get(self, job_id: str):
        job_status = job_manager.get_job_status(job_id)
        
        if job_status is None:
            self.set_status(404)
            self.write_json({
                'status': 'error',
                'message': f'Job {job_id} not found'
            })
        else:
            self.write_json(job_status)


class JobListHandler(BaseHandler):
    """List all jobs (with optional filters)"""
    
    def get(self):
        # Get filter parameters
        user = self.get_argument('user', None)
        status = self.get_argument('status', None)
        limit = int(self.get_argument('limit', '50'))
        
        # Build filters
        filters = {}
        if user:
            filters['user'] = user
        if status:
            filters['status'] = status
        
        # Query database
        jobs = database.query_jobs(filters, limit=limit)
        
        self.write_json({
            'status': 'success',
            'count': len(jobs),
            'jobs': jobs
        })


class ResultsHandler(BaseHandler):
    """View results for a specific job"""
    
    def get(self, job_id: str):
        # Get job info from database
        jobs = database.query_jobs({'job_id': job_id})
        
        if not jobs:
            self.set_status(404)
            self.render('templates/error.html',
                       message=f'Job {job_id} not found')
            return
        
        job = jobs[0]
        
        # Get results from database
        results = database.get_results(job_id)
        
        # Parse result directory (if available)
        result_data = None
        if job['result_dir']:
            parser = ResultParser(job['result_dir'])
            result_data = parser.parse_all()
        
        self.render('templates/results.html',
                   job=job,
                   results=results,
                   result_data=result_data)


class ProgressMonitor(tornado.websocket.WebSocketHandler):
    """WebSocket for real-time progress monitoring"""
    
    clients = set()  # All connected clients
    
    def open(self):
        """Client connected"""
        ProgressMonitor.clients.add(self)
        print(f"WebSocket opened (total clients: {len(ProgressMonitor.clients)})")
    
    def on_message(self, message: str):
        """
        Client sent message
        Expected format: {"action": "subscribe", "job_id": "..."}
        """
        try:
            data = json.loads(message)
            action = data.get('action')
            job_id = data.get('job_id')
            
            if action == 'subscribe':
                # Subscribe to job updates
                job_manager.subscribe_to_job(job_id, self)
                self.write_message({
                    'type': 'subscribed',
                    'job_id': job_id
                })
            
            elif action == 'unsubscribe':
                # Unsubscribe from job updates
                job_manager.unsubscribe_from_job(job_id, self)
                self.write_message({
                    'type': 'unsubscribed',
                    'job_id': job_id
                })
            
        except json.JSONDecodeError:
            self.write_message({
                'type': 'error',
                'message': 'Invalid JSON'
            })
    
    def on_close(self):
        """Client disconnected"""
        ProgressMonitor.clients.discard(self)
        job_manager.unsubscribe_all(self)
        print(f"WebSocket closed (total clients: {len(ProgressMonitor.clients)})")
    
    @classmethod
    def broadcast_update(cls, job_id: str, update: Dict):
        """Broadcast update to all subscribed clients"""
        message = {
            'type': 'progress',
            'job_id': job_id,
            'update': update,
            'timestamp': datetime.now().isoformat()
        }
        
        for client in cls.clients:
            try:
                client.write_message(message)
            except:
                pass  # Client disconnected


class ValidateConfigHandler(BaseHandler):
    """Validate configuration without submitting"""
    
    def post(self):
        try:
            # Extract parameters
            user_params = json.loads(self.request.body)
            
            # Validate only
            validation = config_generator.validate_parameters(user_params)
            
            self.write_json({
                'status': 'success',
                'valid': validation.valid,
                'errors': validation.errors,
                'warnings': validation.warnings
            })
            
        except Exception as e:
            self.set_status(400)
            self.write_json({
                'status': 'error',
                'message': str(e)
            })


class ValidOptionsHandler(BaseHandler):
    """Get valid options for UI dropdowns"""
    
    def get(self):
        options = config_generator.get_valid_options()
        self.write_json({
            'status': 'success',
            'options': options
        })


class CancelJobHandler(BaseHandler):
    """Cancel a running job"""
    
    def post(self, job_id: str):
        success = job_manager.cancel_job(job_id)
        
        if success:
            self.write_json({
                'status': 'success',
                'message': f'Job {job_id} cancelled'
            })
        else:
            self.set_status(404)
            self.write_json({
                'status': 'error',
                'message': f'Job {job_id} not found or already completed'
            })


class HealthCheckHandler(BaseHandler):
    """Health check endpoint"""
    
    def get(self):
        # Check all components
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'config_generator': 'ok',
                'executor': 'ok',
                'database': 'ok',
                'job_manager': 'ok'
            }
        }
        
        # Verify Pai Ho's scripts
        try:
            executor._verify_scripts()
        except Exception as e:
            health['status'] = 'degraded'
            health['components']['executor'] = f'error: {str(e)}'
        
        # Verify database connection
        try:
            database.conn.execute('SELECT 1').fetchone()
        except Exception as e:
            health['status'] = 'degraded'
            health['components']['database'] = f'error: {str(e)}'
        
        self.write_json(health)


def make_app():
    """Create Tornado application"""
    
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/submit", SubmitHandler),
        (r"/jobs", JobListHandler),
        (r"/jobs/([^/]+)", JobStatusHandler),
        (r"/jobs/([^/]+)/cancel", CancelJobHandler),
        (r"/results/([^/]+)", ResultsHandler),
        (r"/progress", ProgressMonitor),
        (r"/validate", ValidateConfigHandler),
        (r"/options", ValidOptionsHandler),
        (r"/health", HealthCheckHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret="__CHANGE_THIS_SECRET__",  # Change in production!
    debug=True,
    autoreload=True
    )


if __name__ == "__main__":
    # Start job manager background thread
    job_manager.start()
    
    # Create and start web server
    app = make_app()
    port = int(os.getenv('PORT', '8888'))
    
    app.listen(port)
    
    print("=" * 70)
    print("WKPUP Automation Server")
    print("=" * 70)
    print(f"Server started on http://localhost:{port}")
    print(f"Using Pai Ho's scripts from: {PAIHO_SCRIPT_DIR}")
    print(f"Working directory: {PAIHO_WORKDIR}")
    print(f"Database: {DATABASE_PATH}")
    print("=" * 70)
    print("\nPress Ctrl+C to stop")
    
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        job_manager.stop()
        print("Server stopped")
```

---

### 3.4 Database Layer (COMPLETE CODE)

**File**: `web_automation/modules/database.py`

```python
"""
Database Layer - Track Pai Ho's Simulation Jobs and Results

This module provides SQLite-based tracking for all simulation jobs,
storing metadata and results WITHOUT modifying Pai Ho's execution logic.

Tables:
- jobs: Job metadata (submission, config, status)
- results: Parsed simulation results (from Pai Ho's creport.txt)
- job_stages: Individual stage execution records

Author: Web Automation Layer
Version: 1.0
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


class SimulationDatabase:
    """SQLite database for tracking simulations"""
    
    def __init__(self, db_path: str = 'simulation_tracking.db'):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Initialize schema
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create database schema if not exists"""
        cursor = self.conn.cursor()
        
        # Jobs table - main job metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                submitted_at TIMESTAMP NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                user TEXT NOT NULL,
                status TEXT NOT NULL,  -- 'queued', 'running', 'success', 'failed', 'cancelled'
                
                -- Configuration parameters
                mode TEXT,
                sim_mode TEXT,
                vccn TEXT,
                vcctx TEXT,
                condition TEXT,
                cpu INTEGER,
                mem INTEGER,
                simulator TEXT,
                alter_extraction TEXT,
                
                -- Full config JSON
                config_json TEXT,
                config_file TEXT,
                
                -- Results
                result_dir TEXT,
                error_message TEXT,
                
                -- Metadata
                duration_seconds REAL,
                stages_completed TEXT  -- JSON array
            )
        """)
        
        # Job stages table - track each stage execution
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_stages (
                stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                stage TEXT NOT NULL,  -- 'gen', 'run', 'ext', 'srt', 'bkp'
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                exit_code INTEGER,
                stdout_log TEXT,
                stderr_log TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            )
        """)
        
        # Results table - parsed simulation results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                
                -- PVT coordinates
                corner TEXT NOT NULL,
                extraction TEXT,
                temperature TEXT NOT NULL,
                voltage TEXT NOT NULL,
                
                -- Measurements
                tphl REAL,
                tplh REAL,
                ipeak REAL,
                iavg REAL,
                power REAL,
                
                -- Pass/fail
                pass_fail TEXT,
                
                -- Raw data from Pai Ho's creport.txt
                raw_data TEXT,
                
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            )
        """)
        
        # Create indices for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_user ON jobs(user)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_submitted ON jobs(submitted_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_results_job ON results(job_id)
        """)
        
        self.conn.commit()
    
    def create_job(self, job_id: str, user: str, params: Dict) -> None:
        """
        Create new job record
        
        Args:
            job_id: Unique job identifier
            user: Username
            params: Job parameters (config.cfg values)
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (
                job_id, submitted_at, user, status,
                mode, sim_mode, vccn, vcctx, condition,
                cpu, mem, simulator, alter_extraction,
                config_json, config_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            datetime.now(),
            user,
            'queued',
            params.get('mode'),
            params.get('sim_mode'),
            params.get('vccn'),
            params.get('vcctx'),
            params.get('condition'),
            params.get('CPU'),
            params.get('MEM'),
            params.get('simulator'),
            params.get('alter_extraction'),
            json.dumps(params),
            params.get('config_file')
        ))
        
        self.conn.commit()
    
    def update_job_status(self, job_id: str, status: str, **kwargs) -> None:
        """
        Update job status and optional fields
        
        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Additional fields to update
        """
        cursor = self.conn.cursor()
        
        # Build dynamic UPDATE statement
        fields = ['status = ?']
        values = [status]
        
        # Handle common updates
        if status == 'running' and 'started_at' not in kwargs:
            kwargs['started_at'] = datetime.now()
        
        if status in ('success', 'failed', 'cancelled') and 'completed_at' not in kwargs:
            kwargs['completed_at'] = datetime.now()
        
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(job_id)  # For WHERE clause
        
        query = f"UPDATE jobs SET {', '.join(fields)} WHERE job_id = ?"
        cursor.execute(query, values)
        
        self.conn.commit()
    
    def record_stage(self, job_id: str, stage: str, status: str, 
                    exit_code: int = 0, stdout: str = '', stderr: str = '',
                    started_at: datetime = None, completed_at: datetime = None) -> None:
        """
        Record stage execution
        
        Args:
            job_id: Job identifier
            stage: Stage name ('gen', 'run', etc.)
            status: Stage status
            exit_code: Exit code
            stdout: Standard output
            stderr: Standard error
            started_at: Start time
            completed_at: Completion time
        """
        cursor = self.conn.cursor()
        
        if started_at is None:
            started_at = datetime.now()
        
        duration = None
        if completed_at:
            duration = (completed_at - started_at).total_seconds()
        
        cursor.execute("""
            INSERT INTO job_stages (
                job_id, stage, status, started_at, completed_at,
                duration_seconds, exit_code, stdout_log, stderr_log
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id, stage, status, started_at, completed_at,
            duration, exit_code, stdout, stderr
        ))
        
        self.conn.commit()
    
    def store_results(self, job_id: str, results: List[Dict]) -> None:
        """
        Store parsed simulation results
        
        Args:
            job_id: Job identifier
            results: List of result dictionaries (from ResultParser)
        """
        cursor = self.conn.cursor()
        
        for result in results:
            cursor.execute("""
                INSERT INTO results (
                    job_id, corner, extraction, temperature, voltage,
                    tphl, tplh, ipeak, iavg, power,
                    pass_fail, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                result.get('corner'),
                result.get('extraction'),
                result.get('temperature'),
                result.get('voltage'),
                result.get('tphl'),
                result.get('tplh'),
                result.get('ipeak'),
                result.get('iavg'),
                result.get('power'),
                result.get('pass_fail'),
                result.get('raw_data')
            ))
        
        self.conn.commit()
    
    def query_jobs(self, filters: Optional[Dict] = None, 
                   limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Query jobs with optional filters
        
        Args:
            filters: Dictionary of filter conditions
            limit: Maximum results to return
            offset: Offset for pagination
        
        Returns:
            List of job dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM jobs"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY submitted_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get single job by ID"""
        jobs = self.query_jobs({'job_id': job_id}, limit=1)
        return jobs[0] if jobs else None
    
    def get_results(self, job_id: str) -> List[Dict]:
        """Get all results for a job"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM results WHERE job_id = ?
            ORDER BY corner, temperature, voltage
        """, (job_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_job_stages(self, job_id: str) -> List[Dict]:
        """Get all stages for a job"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM job_stages WHERE job_id = ?
            ORDER BY started_at
        """, (job_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Jobs by status
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM jobs
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Jobs by user
        cursor.execute("""
            SELECT user, COUNT(*) as count FROM jobs
            GROUP BY user
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_users'] = {row['user']: row['count'] for row in cursor.fetchall()}
        
        # Average duration
        cursor.execute("""
            SELECT AVG(duration_seconds) as avg_duration FROM jobs
            WHERE status = 'success' AND duration_seconds IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_duration_seconds'] = result['avg_duration'] if result['avg_duration'] else 0
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
```

---

### 3.5 Job Manager (COMPLETE CODE)

**File**: `web_automation/modules/job_manager.py`

```python
"""
Job Manager - Background Job Execution Queue

Manages asynchronous execution of Pai Ho's simulations,
allowing multiple jobs to run concurrently without blocking the web server.

Features:
- Job queue (FIFO)
- Background execution thread
- Progress tracking
- WebSocket notifications
- Job cancellation

Author: Web Automation Layer
Version: 1.0
"""

import threading
import queue
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid


@dataclass
class Job:
    """Job definition"""
    job_id: str
    config_file: str
    user: str
    params: Dict
    submitted_at: datetime = field(default_factory=datetime.now)
    status: str = 'queued'
    progress: int = 0
    current_stage: Optional[str] = None
    result_dir: Optional[str] = None
    error_message: Optional[str] = None
    
    # Subscribers (WebSocket clients)
    subscribers: Set = field(default_factory=set)


class JobManager:
    """Manage background job execution"""
    
    def __init__(self, executor, database, max_concurrent: int = 3):
        """
        Initialize job manager
        
        Args:
            executor: PaiHoExecutor instance
            database: SimulationDatabase instance
            max_concurrent: Maximum concurrent jobs
        """
        self.executor = executor
        self.database = database
        self.max_concurrent = max_concurrent
        
        # Job queue and tracking
        self.job_queue = queue.Queue()
        self.active_jobs: Dict[str, Job] = {}
        self.completed_jobs: Dict[str, Job] = {}
        
        # Worker threads
        self.workers: List[threading.Thread] = []
        self.running = False
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def start(self):
        """Start background worker threads"""
        if self.running:
            return
        
        self.running = True
        
        # Start worker threads
        for i in range(self.max_concurrent):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"JobWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        print(f"Job manager started with {self.max_concurrent} workers")
    
    def stop(self):
        """Stop background worker threads"""
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        print("Job manager stopped")
    
    async def submit_job(self, config_file: str, user: str, params: Dict) -> str:
        """
        Submit job to queue
        
        Args:
            config_file: Path to config.cfg
            user: Username
            params: Job parameters
        
        Returns:
            Job ID
        """
        # Generate unique job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create job object
        job = Job(
            job_id=job_id,
            config_file=config_file,
            user=user,
            params=params
        )
        
        # Store in database
        self.database.create_job(job_id, user, params)
        
        # Add to queue
        with self.lock:
            self.job_queue.put(job)
            self.active_jobs[job_id] = job
        
        print(f"Job {job_id} submitted by {user}")
        
        return job_id
    
    def _worker_loop(self):
        """Worker thread main loop"""
        while self.running:
            try:
                # Get job from queue (with timeout)
                try:
                    job = self.job_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Execute job
                self._execute_job(job)
                
                # Mark queue task as done
                self.job_queue.task_done()
                
            except Exception as e:
                print(f"Worker error: {e}")
    
    def _execute_job(self, job: Job):
        """
        Execute a single job (all stages)
        
        Args:
            job: Job to execute
        """
        print(f"\n{'=' * 70}")
        print(f"Executing job: {job.job_id}")
        print(f"User: {job.user}")
        print(f"Config: {job.config_file}")
        print(f"{'=' * 70}\n")
        
        # Update status
        job.status = 'running'
        self.database.update_job_status(job.job_id, 'running')
        self._notify_subscribers(job, {'status': 'running', 'progress': 0})
        
        try:
            # Execute all stages
            stages = ['gen', 'run', 'ext', 'srt', 'bkp']
            
            for i, stage in enumerate(stages):
                job.current_stage = stage
                job.progress = int((i / len(stages)) * 100)
                
                self._notify_subscribers(job, {
                    'status': 'running',
                    'stage': stage,
                    'progress': job.progress
                })
                
                print(f"[{job.job_id}] Stage {i+1}/{len(stages)}: {stage}")
                
                # Execute stage via Pai Ho executor
                result = self.executor.execute_stage(job.config_file, stage)
                
                # Record stage in database
                self.database.record_stage(
                    job.job_id, stage, result.status,
                    result.exit_code, result.stdout, result.stderr,
                    result.start_time, result.end_time
                )
                
                if result.status != 'success':
                    # Stage failed - stop execution
                    raise Exception(f"Stage '{stage}' failed: {result.stderr}")
                
                # Store result directory (from bkp stage)
                if stage == 'bkp' and result.result_dir:
                    job.result_dir = result.result_dir
            
            # All stages succeeded
            job.status = 'success'
            job.progress = 100
            
            # Parse and store results
            if job.result_dir:
                from modules.result_parser import ResultParser
                parser = ResultParser(job.result_dir)
                results = parser.parse_creport()
                self.database.store_results(job.job_id, results)
            
            # Update database
            self.database.update_job_status(
                job.job_id, 'success',
                result_dir=job.result_dir
            )
            
            # Notify subscribers
            self._notify_subscribers(job, {
                'status': 'success',
                'progress': 100,
                'result_dir': job.result_dir
            })
            
            print(f"✅ Job {job.job_id} completed successfully")
            
        except Exception as e:
            # Job failed
            job.status = 'failed'
            job.error_message = str(e)
            
            self.database.update_job_status(
                job.job_id, 'failed',
                error_message=str(e)
            )
            
            self._notify_subscribers(job, {
                'status': 'failed',
                'error': str(e)
            })
            
            print(f"❌ Job {job.job_id} failed: {e}")
        
        finally:
            # Move to completed
            with self.lock:
                self.active_jobs.pop(job.job_id, None)
                self.completed_jobs[job.job_id] = job
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get current status of a job
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job status dictionary, or None if not found
        """
        # Check active jobs first
        with self.lock:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    'job_id': job.job_id,
                    'status': job.status,
                    'progress': job.progress,
                    'current_stage': job.current_stage,
                    'user': job.user,
                    'submitted_at': job.submitted_at.isoformat(),
                }
            
            if job_id in self.completed_jobs:
                job = self.completed_jobs[job_id]
                return {
                    'job_id': job.job_id,
                    'status': job.status,
                    'progress': job.progress,
                    'result_dir': job.result_dir,
                    'error_message': job.error_message,
                    'user': job.user,
                    'submitted_at': job.submitted_at.isoformat(),
                }
        
        # Check database
        job_data = self.database.get_job(job_id)
        return job_data
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a queued or running job
        
        Args:
            job_id: Job identifier
        
        Returns:
            True if cancelled, False if not found or already completed
        """
        with self.lock:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                
                if job.status == 'queued':
                    # Remove from queue (if not yet started)
                    job.status = 'cancelled'
                    self.database.update_job_status(job_id, 'cancelled')
                    self._notify_subscribers(job, {'status': 'cancelled'})
                    return True
                
                # TODO: Implement running job cancellation (kill subprocess)
                # For now, only queued jobs can be cancelled
                return False
        
        return False
    
    def subscribe_to_job(self, job_id: str, subscriber):
        """
        Subscribe to job updates (WebSocket client)
        
        Args:
            job_id: Job identifier
            subscriber: WebSocket handler instance
        """
        with self.lock:
            if job_id in self.active_jobs:
                self.active_jobs[job_id].subscribers.add(subscriber)
            elif job_id in self.completed_jobs:
                self.completed_jobs[job_id].subscribers.add(subscriber)
    
    def unsubscribe_from_job(self, job_id: str, subscriber):
        """Unsubscribe from job updates"""
        with self.lock:
            if job_id in self.active_jobs:
                self.active_jobs[job_id].subscribers.discard(subscriber)
            elif job_id in self.completed_jobs:
                self.completed_jobs[job_id].subscribers.discard(subscriber)
    
    def unsubscribe_all(self, subscriber):
        """Unsubscribe from all jobs"""
        with self.lock:
            for job in list(self.active_jobs.values()) + list(self.completed_jobs.values()):
                job.subscribers.discard(subscriber)
    
    def _notify_subscribers(self, job: Job, update: Dict):
        """
        Notify all subscribers of job update
        
        Args:
            job: Job instance
            update: Update dictionary
        """
        for subscriber in job.subscribers:
            try:
                subscriber.write_message({
                    'type': 'progress',
                    'job_id': job.job_id,
                    'update': update,
                    'timestamp': datetime.now().isoformat()
                })
            except:
                # Subscriber disconnected
                pass
```

Let me continue with more sections...
