# TIER 1: Framework Architecture Analysis

## Document Overview
This document provides a comprehensive analysis of the WKPUP (Weak Pull-Up) simulation automation framework architecture. Based on examination of 291 dependency files in the repository, this analysis maps the complete automation system from configuration to simulation execution.

**Analysis Date**: October 28, 2025  
**Repository**: wkpup-paiho-implementation  
**Files Analyzed**: 291 dependency files in `gpio/1p1v/dependencies/scripts/simulation_script/`

---

## Table of Contents
1. [Framework Overview](#framework-overview)
2. [Automation Architecture Versions](#automation-architecture-versions)
3. [Configuration System](#configuration-system)
4. [Testbench Generation Pipeline](#testbench-generation-pipeline)
5. [Simulation Execution Flow](#simulation-execution-flow)
6. [Data Extraction Workflow](#data-extraction-workflow)
7. [Tool Requirements](#tool-requirements)
8. [Complete Call Chain](#complete-call-chain)

---

## Framework Overview

### Directory Structure
```
gpio/1p1v/dependencies/scripts/simulation_script/
├── alias_param_source/        # Global path and alias definitions
│   ├── script_param           # Main path variables
│   └── script_alias           # Shell command aliases
├── auto_pvt/                  # Automated PVT simulation framework
│   ├── ver01/                 # Version 1 automation
│   ├── ver02/                 # Version 2 automation
│   ├── ver03/                 # Version 3 automation (current)
│   ├── Example/               # Reference examples and templates
│   └── debug/                 # Debugging and logging utilities
├── nb_sim/                    # Non-batch simulation wrapper
│   └── nb_sim.sh
└── ultilities/                # Utility scripts
    ├── libgen.py              # Library generation
    └── alter_extraction_script/
        └── extract_alt.sh
```

### Framework Philosophy

The automation framework is built on three core principles:

1. **Configuration-Driven Execution**: All simulation parameters controlled via `config.cfg`
2. **Version Coexistence**: Multiple framework versions (ver01-03) maintained simultaneously
3. **Parameterized Differentiation**: Single codebase serves both GPIO and I3C via library parameters

### Key Statistics
- **Total Files**: 291 scripts, configuration files, and templates
- **Active Versions**: 3 (ver01, ver02, ver03)
- **Backup Test Sets**: 3 timestamped backup directories
- **Supported Simulators**: PrimeSim, FineSim
- **Languages**: Bash shell, Perl, Python

---

## Automation Architecture Versions

### Version Comparison

| Feature | ver01 | ver02 | ver03 (Current) |
|---------|-------|-------|-----------------|
| Configuration Parser | ✅ read_cfg.sh | ✅ Enhanced | ✅ Enhanced + VCC_VID |
| Corner Support | Basic PVT | Extended corners | Full corner matrix |
| Supply Sweep | 1-2 supplies | 1-3 supplies | 1-3 supplies + VID |
| Testbench Generator | gen_tb.pl | gen_tb.pl (improved) | gen_tb.pl (full featured) |
| Data Extraction | Basic | Enhanced + alternative | Full automation |
| Runme Functions | Basic | Enhanced | Full featured |

### Version 3 (Current) - Detailed Architecture

Version 3 is the production version used by both GPIO and I3C implementations.

#### Directory Structure
```
auto_pvt/ver03/
├── configuration/
│   ├── read_cfg.sh              # Config file parser
│   ├── read_corner.sh           # Corner list extractor
│   ├── read_supply.sh           # Voltage sweep handler
│   ├── table_corner_list.csv   # PVT corner definitions
│   ├── table_supply_list.csv   # Voltage tables (default)
│   ├── table_supply_list_ac.csv # AC simulation voltages
│   └── table_supply_list_dc.csv # DC simulation voltages
├── runme_script/
│   ├── runme_func.sh            # Helper functions
│   └── test/                    # Test configurations
│       ├── prelay/              # Pre-layout test cases
│       └── polo/                # Post-layout test cases
├── tb_gen/
│   ├── gen_tb.pl                # Perl testbench generator
│   └── pvt_loop.sh              # PVT loop generator
├── data_extraction/
│   ├── extract_alt.sh           # Alternative data extractor
│   └── move.sh                  # Result organizer
└── sim_pvt.sh                   # Main orchestration script
```

---

## Configuration System

### Entry Point: script_param

**File**: `alias_param_source/script_param`

```bash
sim="/nfs/site/disks/.../nb_sim/nb_sim.sh"
sim_pvt="/nfs/site/disks/.../auto_pvt/ver03/sim_pvt.sh"
script_path="/nfs/site/disks/.../auto_pvt/ver03"
```

**Purpose**: 
- Defines global paths to simulation scripts
- Sets `$script_path` variable used throughout framework
- Points to version 3 (ver03) as current production version

### Configuration Parser: read_cfg.sh

**Function**: `read_cfg()`

**Reads**: `$current_path/config.cfg`

**Supported Parameters** (15 total):

| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `mode` | Simulation mode | `prelay`, `postlay` |
| `vccn` | VCC nominal voltage | `1p1v`, `1p2v` |
| `vcctx` | VCC TX voltage | `vcctx_600`, `vcctx_NA` |
| `vccana` | VCC analog voltage | `vccana` |
| `vcc` | Main VCC level | `vcc` |
| `1st_supply_swp` | First supply to sweep | `vcc`, `vccn`, `NA` |
| `2nd_supply_swp` | Second supply to sweep | `vcc`, `vccn`, `NA` |
| `3rd_supply_swp` | Third supply to sweep | `vcc`, `vccn`, `NA` |
| `condition` | Operating condition | `perf`, `func`, `htol`, `hvqk` |
| `CPU #` | CPU cores for simulation | `4`, `8`, `16` |
| `MEM [G]` | Memory allocation (GB) | `4`, `8`, `16` |
| `alter_extraction` | Enable alternative extraction | `Yes`, `No` |
| `alter_string#` | Alternative string count | Integer |
| `sim_mode` | Simulation type | `ac`, `dc`, `tran` |
| `gs/gf_corner` | Global/Fast corners | `Yes`, `No` |
| `vcc_vid` | VID voltage support | `Yes`, `No` |
| `simulator` | SPICE simulator | `primesim`, `finesim` |
| `postlay_cross_cornerlist` | Post-layout corners | `default`, `full`, `custom` |

**Default Values**:
```bash
mode="prelay"
vcn_lvl="1p1v"
vctx_lvl="vcctx_600"
vca_lvl="vccana"
vcc_lvl="vcc"
supply1="vcc"
supply2="NA"
supply3="NA"
condition="perf"
ncpu="4"
nmem="4"
alt_ext_mode="No"
alt_ext_n="0"
sim_mode="ac"
gsgf_corner="No"
vcc_vid="No"
simulator="finesim"
postlay_cross_cornerlist="default"
```

### Corner Definition: table_corner_list.csv

**File**: `configuration/table_corner_list.csv`

**Content**:
```csv
type,extraction,corner list
nom_tt,typical,TT
full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG
full_tt_gsgf,typical,TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG
cross_default,cworst_CCworst_T cbest_CCbest_T,FSG SFG SSG FFG
cross_default_gsgf,cworst_CCworst_T cbest_CCbest_T,FSG SFG SSG FFG FFG_SSG SSG_FFG
cross_full,cworst_CCworst_T cbest_CCbest_T,TT FSG SFG FFG FFAG SSG SSAG
cross_full_gsgf,cworst_CCworst_T cbest_CCbest_T,TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG
```

**Corner Definitions**:
- **TT**: Typical-Typical (nominal process, nominal voltage, nominal temperature)
- **FSG**: Fast Si, Slow Global (fast transistors, slow interconnect)
- **SFG**: Slow Si, Fast Global (slow transistors, fast interconnect)
- **FFG**: Fast-Fast Global (fast process)
- **FFAG**: Fast-Fast Analog Global (fast process, optimized for analog)
- **SSG**: Slow-Slow Global (slow process)
- **SSAG**: Slow-Slow Analog Global (slow process, optimized for analog)
- **FFG_SSG**: Mixed corner (fast-to-slow)
- **SSG_FFG**: Mixed corner (slow-to-fast)

### Supply Voltage Tables

The framework supports three voltage table modes:
1. **AC Mode**: `table_supply_list_ac.csv` - For AC simulations
2. **DC Mode**: `table_supply_list_dc.csv` - For DC simulations
3. **Default Mode**: `table_supply_list.csv` - General purpose

**Supply Parser**: `read_supply.sh`

**Voltage Conditions**:
- **func**: Functional (wide voltage range)
- **perf**: Performance (tighter voltage range, typical use)
- **htol**: High temperature operating life
- **hvqk**: High voltage qualification

**Voltage Trends**:
- **min**: Minimum voltage (worst case for timing)
- **nom**: Nominal voltage (typical operation)
- **max**: Maximum voltage (worst case for reliability)

**VID Support** (Voltage Identification):
When `vcc_vid=Yes`, the framework supports corner-specific voltage tables:
- `vcc_vid_tt_h`: TT corner, hot temperature
- `vcc_vid_tt_c`: TT corner, cold temperature
- `vcc_vid_ff_h`: FF corner, hot temperature
- `vcc_vid_ff_c`: FF corner, cold temperature
- `vcc_vid_ss_h`: SS corner, hot temperature
- `vcc_vid_ss_c`: SS corner, cold temperature

---

## Testbench Generation Pipeline

### Overview

The testbench generation creates SPICE netlists for each PVT corner from a template file.

**Flow**: Template → Parameter Substitution → Generated Netlist

### Main Generator: gen_tb.pl

**File**: `tb_gen/gen_tb.pl`  
**Language**: Perl

**Command Line Arguments** (43 parameters):
```perl
$infile          # Template file (sim_tx.sp)
$si_corner       # Silicon corner (TT, FF, SS, etc.)
$ex_corner       # Extraction corner (typical, cworst, cbest)
$temperature     # Temperature (m40, 0, 25, 85, 100, 125)
$vtrend_v1       # Voltage trend for supply 1 (min/nom/max)
$vtrend_v2       # Voltage trend for supply 2
$vtrend_v3       # Voltage trend for supply 3
$supply1         # First supply name
$supply2         # Second supply name
$supply3         # Third supply name
$vccmin          # VCC minimum voltage
$vccnom          # VCC nominal voltage
$vccmax          # VCC maximum voltage
$vcnmin          # VCCN minimum voltage
$vcnnom          # VCCN nominal voltage
$vcnmax          # VCCN maximum voltage
# ... (VCC VID parameters for each corner)
```

### Template Substitution Rules

The Perl script performs these transformations on the template:

1. **Temperature Update**:
   ```perl
   .temp <value>  →  .temp -40  # for m40 corner
   ```

2. **Model File Update**:
   ```perl
   <path>DP_HSPICE_MODEL<suffix>  →  <path>DP_HSPICE_MODEL TT
   ```

3. **Extraction File Update**:
   ```perl
   _tparam_typical.spf  →  _tparam_cworst_CCworst_T.spf
   ```

4. **Library Parameter Update**:
   ```perl
   .lib "..._lib.lib" <params>  →  
   .lib "..._lib.lib" TT_typical_85_v1nom
   ```

5. **Voltage Parameter Updates**:
   ```perl
   .param vcn=<value>  →  .param vcn=1.1  # for nom voltage
   ```

### PVT Loop Generator: pvt_loop.sh

**File**: `tb_gen/pvt_loop.sh`

**Function**: `gen_pvt_loop_par()`

**Purpose**: Creates nested loops for PVT matrix

**Loop Structure**:
```bash
for i in $si_corner_list; do          # Si corners (TT, FF, SS, etc.)
  for j in $ex_corner_list; do        # Extraction corners
    for k in $temperature_list; do    # Temperatures (-40 to 125)
      for l in $voltage_trends; do    # Voltage sweeps (min/nom/max)
        core_func                     # Execute action (gen/run/extract)
      done
    done
  done
done
```

**Example Generated Directory Structure**:
```
TT/                              # Si corner
└── typical/                     # Extraction corner
    ├── typical_85/              # Temperature 85°C
    │   ├── v1nom/               # Voltage nominal
    │   │   └── sim_tx.sp       # Generated netlist
    │   ├── v1min/
    │   │   └── sim_tx.sp
    │   └── v1max/
    │       └── sim_tx.sp
    ├── typical_125/
    └── typical_m40/
```

---

## Simulation Execution Flow

### Main Orchestrator: sim_pvt.sh

**File**: `auto_pvt/ver03/sim_pvt.sh`

**Command Syntax**:
```bash
sh sim_pvt.sh <config_file> <stage> [run_ex_corner]
```

**Stages**:
1. `gen` - Generate testbench directories and files
2. `run` - Submit simulations to compute farm
3. `ext` - Extract measurement data from results
4. `srt` - Sort and organize extracted data
5. `bkp` - Backup results to timestamped directory
6. `usr_script` - Run custom user-defined post-processing

### Stage 1: Generation (gen)

**Actions**:
1. Source configuration scripts
2. Call `read_cfg()`, `read_supply()`, `read_corner()`
3. Display configuration summary
4. Execute `gen_pvt_loop_par()`
5. For each PVT combination:
   - Create directory structure
   - Call `gen_tb.pl` to generate netlist

**Output**: Complete directory tree with SPICE netlists

### Stage 2: Simulation (run)

**Actions**:
1. Validate CPU and memory parameters
2. Select simulation mode (prelay vs postlay)

**Pre-layout Mode**:
```bash
# Run all corners without corner specification
gen_pvt_loop_seq
```

**Post-layout Mode**:
```bash
# Run specific extraction corner set
run_pvt_loop_polo <typical|cworst_CCworst_T|cbest_CCbest_T>
```

**Job Submission** (PrimeSim example):
```bash
nbjob run \
  --target altera_png_normal \
  --qslot /psg/km/phe/ckt/gen \
  --class 'SLES15&&4G&&8C' \
  primesim -np 8 -spice sim_tx.sp -o sim_tx \
  >> job_log.txt
```

**Job Submission** (FineSim example):
```bash
nbjob run \
  --target altera_png_normal \
  --qslot /psg/km/phe/ckt/gen \
  --class 'SLES15&&4G&&8C' \
  finesim -np 8 sim_tx.sp -o sim_tx \
  >> job_log.txt
```

### Stage 3: Extraction (ext)

**Script**: `data_extraction/extract_alt.sh`

**Actions**:
1. Navigate through PVT directory tree
2. For each simulation:
   - Extract measurement results from `.mt0` files
   - Parse `.measure` statements
   - Compile data into text files
3. Alternative extraction mode (if enabled):
   - Extract additional parameters
   - Handle custom measurement strings

**Output**: Result files per corner (e.g., `report_TT_typical_85_v1nom.txt`)

### Stage 4: Sorting (srt)

**Actions**:
1. Collect all extracted data files
2. Sort by corner, temperature, voltage
3. Create summary tables
4. Identify min/max values across corners

### Stage 5: Backup (bkp)

**Actions**:
1. Create timestamped backup directory: `00bkp_YYYYMMDDHHmm/`
2. Copy all results, reports, and data files
3. Archive testbench files (optional)
4. Preserve configuration for reproducibility

**Example Backup**:
```
00bkp_202508191157/
├── report/
│   ├── report_TT_typical_85_v1nom.txt
│   ├── report_FF_typical_125_v1min.txt
│   └── ...
├── data/
│   └── extracted_measurements.csv
└── tb_bkp/
    └── <testbench snapshots>
```

### Stage 6: User Script (usr_script)

**Conditional Execution**: Only if `usr_script=Yes` in runme.sh

**Purpose**: Custom post-processing automation
- Additional data analysis
- Report generation
- Plot creation
- Database updates

---

## Data Extraction Workflow

### Primary Extractor: extract_alt.sh

**File**: `data_extraction/extract_alt.sh`

**Purpose**: Extract SPICE measurement results

**Input**: `.mt0` files from SPICE simulations

**Output**: Text files with measurement data

**Measurement Types** (common for WKPUP):
- `rwkpull`: Weak pull-up resistance
- `ioh`: Output high current
- `vwkp`: Weak pull-up voltage
- `del_rr`: Rising-to-rising delay
- `del_ff`: Falling-to-falling delay

### Result File Format

**Example**: `report_TT_typical_85_v1nom.txt`
```
del_rr          del_ff          temper          alter#
3.12398102e-11  3.18924935e-11  8.50000000e+01  1.00000000e+00
```

### Data Organization Utility: move.sh

**File**: `data_extraction/move.sh`

**Purpose**: Organize extracted data into report directories

**Actions**:
1. Create `report/` directory
2. Move/copy extracted files
3. Create index of available results
4. Generate summary statistics

---

## Tool Requirements

### Required Software

#### 1. SPICE Simulators
- **Synopsys PrimeSim** (preferred)
  - Version: W-2024.09-SP1 or later
  - Features: Parallel simulation, FSDB waveforms
- **Synopsys FineSim** (alternative)
  - Version: 2024.x or later
  - Features: Fast SPICE simulation

#### 2. Scripting Interpreters
- **Bash Shell**: Version 4.0+
  - Features: Array support, associative arrays
- **Perl**: Version 5.x
  - Required for `gen_tb.pl` testbench generator
- **Python**: Version 3.x (for libgen.py)
  - Required modules: Standard library only

#### 3. Compute Farm Infrastructure
- **Job Scheduler**: NetBatch (nbjob command)
  - Target: altera_png_normal
  - Queue Slot: /psg/km/phe/ckt/gen
  - Resource Classes: SLES15, CPU cores, Memory

#### 4. File System
- **NFS Storage**: Network file system access
  - Shared script repository
  - PDK model files
  - Library files

### Platform Requirements

**Operating System**: Linux (SLES12/RHEL/SLES15)

**CPU**: 
- Minimum: 4 cores per simulation
- Recommended: 8-16 cores for large netlists
- Maximum: Configurable via `CPU #` parameter

**Memory**:
- Minimum: 4 GB per simulation
- Recommended: 8-16 GB for large circuits
- Maximum: Configurable via `MEM [G]` parameter

### PDK Requirements

**Process**: Intel CLN3P (3nm)
- **Version**: v1.0_2p1a_2025WW23 or compatible
- **Models**: BSIM-CMG Level 72
- **Files**: HSPICE format (`.subckt`, `.l`, `.hsp`)

---

## Complete Call Chain

### Level 0: User Entry Point

```
User: ./runme.sh
Location: gpio/1p1v/runme.sh or i3c/1p1v/runme.sh
```

### Level 1: Initialization

```
runme.sh
├── Source: alias_param_source/script_param
│   └── Defines: $sim_pvt, $script_path
├── Source: $script_path/configuration/read_cfg.sh
│   └── Loads: config.cfg parameters
└── Source: $script_path/runme_script/runme_func.sh
    └── Provides: logging(), run_sim()
```

### Level 2: Generation Phase

```
runme.sh: sh $sim_pvt config.cfg gen
│
└── sim_pvt.sh (stage=gen)
    ├── Source: configuration/read_cfg.sh → read_cfg()
    ├── Source: configuration/read_supply.sh → read_supply()
    ├── Source: configuration/read_corner.sh → read_corner()
    │   └── Read: table_corner_list.csv
    ├── Source: tb_gen/pvt_loop.sh → gen_pvt_loop_par()
    │   └── Loop over: corners × temps × voltages
    │       └── Call: gen_tb.pl for each combination
    │           └── Read: template/sim_tx.sp
    │           └── Output: <corner>/<ex>/<temp>/<volt>/sim_tx.sp
    └── Result: Complete PVT directory tree
```

### Level 3: Simulation Phase

```
runme.sh: run_sim "<corner>"
│
└── runme_func.sh: run_sim()
    └── sim_pvt.sh (stage=run, run_ex_corner=<corner>)
        └── run_pvt_loop_polo
            └── For each PVT combination:
                └── nbjob run ... primesim -np 8 -spice sim_tx.sp
                    ├── Read: Generated sim_tx.sp
                    ├── Include: Circuit netlists (ioss3_txana_x2.sp, etc.)
                    ├── Include: Library files (weakpullup.lib ← CRITICAL)
                    ├── Include: PDK models (CLN3P)
                    └── Output: .mt0, .log, .fsdb files
```

### Level 4: Extraction Phase

```
runme.sh: sh $sim_pvt config.cfg ext
│
└── sim_pvt.sh (stage=ext)
    └── data_extraction/extract_alt.sh
        └── For each PVT directory:
            ├── Read: sim_tx.mt0 (measurement results from simulation)
            ├── Parse: .measure statements from SPICE output
            ├── Extract: Measurement data (delays, voltages, currents)
            └── Write: extracted_data.txt (per corner/temp/voltage)
            └── Output: Individual data files ready for sorting
```

### Level 5: Sorting Phase

```
runme.sh: sh $sim_pvt config.cfg srt
│
└── sim_pvt.sh (stage=srt)
    └── Sort and organize extracted data
        ├── Group by: corner, temperature, voltage
        ├── Aggregate: Data across all PVT combinations
        ├── Generate: Individual report files (report_<corner>_<temp>_<volt>.txt)
        └── Generate: Consolidated report (creport.txt with all results)
        └── Output: Organized report/ directory with analysis results
```

### Level 6: Backup Phase

```
runme.sh: sh $sim_pvt config.cfg bkp
│
└── sim_pvt.sh (stage=bkp)
    ├── Create: 00bkp_<timestamp>/ directory
    ├── Backup Structure:
    │   ├── report/ directory
    │   │   ├── Copy: All report_*.txt files (individual corner reports)
    │   │   └── Copy: creport.txt (consolidated report)
    │   └── tb_bkp/ directory
    │       └── Copy: Testbench files (sim_tx.sp) organized by corner/temp/voltage
    │       └── Copy: Simulation output files (.mt0, .log, .fsdb if configured)
    └── data_extraction/move.sh
        └── Organize files into backup structure
        └── Preserve complete simulation artifacts for reproducibility
        
Final Output:
  00bkp_<YYYYMMDDHHmm>/
  ├── report/
  │   ├── creport.txt (consolidated results across all corners)
  │   ├── report_TT_typical_85_v1nom.txt
  │   ├── report_FF_typical_125_v1min.txt
  │   └── ... (84+ individual corner reports)
  └── tb_bkp/
      ├── typical_m40/v1nom/sim_tx.sp
      ├── typical_85/v1nom/sim_tx.sp
      └── ... (testbench snapshots for all simulated corners)
```

### Level 7: Optional User Script

```
runme.sh: sh $sim_pvt config.cfg usr_script (if usr_script=Yes)
│
└── sim_pvt.sh (stage=usr_script)
    └── Execute: User-defined post-processing
```

### Critical Parameter Flow: enable vs enable_i3c

```
config.cfg
└── (No GPIO/I3C differentiation at config level)
    └── template/sim_tx.sp
        ├── GPIO: .lib "weakpullup.lib" enable       ← Line 52
        └── I3C:  .lib "weakpullup.lib" enable_i3c   ← Line 52
            └── gen_tb.pl substitutes parameters but preserves line 52
                └── Generated netlist maintains enable/enable_i3c
                    └── SPICE simulator reads library parameter
                        └── weakpullup.lib selects appropriate subcircuit
                            └── Circuit behavior differentiates GPIO from I3C
```

### Complete End-to-End Flow: runme.sh → creport.txt & Backup

```
User Executes: ./runme.sh
│
├─► STAGE 1: Generation (gen)
│   ├─ Input: config.cfg, template/sim_tx.sp
│   ├─ Process: gen_tb.pl creates 84 netlists (7 corners × 4 temps × 3 voltages)
│   └─ Output: Complete PVT directory tree with sim_tx.sp in each corner/temp/volt folder
│
├─► STAGE 2: Simulation (run)
│   ├─ Input: Generated sim_tx.sp files (84 netlists)
│   ├─ Process: PrimeSim/FineSim executes SPICE simulations
│   │   ├─ Reads: Circuit netlists (ioss3_txana_x2.sp, etc.)
│   │   ├─ Reads: Library files (weakpullup.lib with enable/enable_i3c ← CRITICAL)
│   │   └─ Reads: PDK models (CLN3P)
│   └─ Output: sim_tx.mt0 (measurements), .log (simulation log), .fsdb (waveforms)
│       └─ Generated in each corner/temp/volt directory
│
├─► STAGE 3: Extraction (ext)
│   ├─ Input: sim_tx.mt0 files (84 measurement files)
│   ├─ Process: extract_alt.sh parses .measure statements
│   └─ Output: extracted_data.txt files with measurement results
│       └─ Data includes: delays, resistances, voltages, currents per corner
│
├─► STAGE 4: Sorting (srt)
│   ├─ Input: Extracted data files from all corners
│   ├─ Process: Aggregate and organize by corner/temp/voltage
│   └─ Output: 
│       ├─ report_TT_typical_85_v1nom.txt (individual corner report)
│       ├─ report_FF_typical_125_v1min.txt (another corner report)
│       ├─ ... (84+ individual reports, one per simulated corner)
│       └─ creport.txt (CONSOLIDATED REPORT - all corners aggregated)
│
├─► STAGE 5: Backup (bkp)
│   ├─ Input: All reports and simulation artifacts
│   ├─ Process: Create timestamped backup directory
│   │   ├─ Create: 00bkp_YYYYMMDDHHmm/
│   │   ├─ Copy reports → 00bkp_*/report/
│   │   │   ├─ creport.txt (consolidated results)
│   │   │   └─ report_*.txt (all individual corner reports)
│   │   └─ Copy testbenches → 00bkp_*/tb_bkp/
│   │       ├─ sim_tx.sp files (testbench snapshots)
│   │       └─ .mt0 files (measurement outputs - if configured)
│   └─ Output: Complete backup preserving all simulation artifacts
│       └─ 00bkp_202508191157/ (example: Aug 19, 2025, 11:57 AM)
│           ├─ report/ (45+ files: creport.txt + individual reports)
│           └─ tb_bkp/ (testbench snapshots organized by corner/temp/voltage)
│
└─► STAGE 6 (Optional): User Script (usr_script)
    ├─ Input: All generated data and reports
    ├─ Process: Custom user-defined post-processing
    └─ Output: Additional analysis, plots, or database updates

FINAL DELIVERABLES:
├─ report/creport.txt                    ← Consolidated analysis across all PVT corners
├─ report/report_<corner>_<temp>_<volt>.txt  ← Individual corner results (84+ files)
└─ 00bkp_<timestamp>/                    ← Timestamped backup for reproducibility
    ├─ report/ (all reports backed up)
    └─ tb_bkp/ (testbenches + mt0 files backed up)
```

**Key Points**:
- **creport.txt**: Final consolidated report aggregating results from all 84 PVT corners
- **mt0 files**: SPICE measurement output files, backed up in 00bkp_*/tb_bkp/ structure
- **Timestamped backups**: Enable reproducibility and historical tracking (e.g., 00bkp_202508191157)
- **Complete traceability**: From template → simulation → measurements → reports → backup

---

## Framework Design Insights

### Strengths

1. **Parameterization**:
   - Single framework serves multiple protocols
   - Library-based differentiation enables 99% code reuse
   - Configuration-driven execution minimizes hard-coding

2. **Scalability**:
   - Version coexistence allows gradual migration
   - Modular design enables feature addition
   - PVT loop structure handles arbitrary corner expansion

3. **Robustness**:
   - Default values prevent configuration errors
   - Validation checks (CPU/MEM integers)
   - Timestamped backups preserve history

4. **Automation**:
   - Testbench generation eliminates manual netlist creation
   - Parallel job submission utilizes compute farm
   - Data extraction standardizes result collection

### Areas for Enhancement

1. **Documentation**:
   - Inline comments minimal in scripts
   - Library parameter meanings not documented in framework
   - Example configurations limited

2. **Error Handling**:
   - Some scripts lack comprehensive error checking
   - Job submission failures not always caught
   - Path validation minimal

3. **Tool Flexibility**:
   - Spectre simulator support commented out
   - Other SPICE simulators not easily added
   - Hard-coded tool paths limit portability

---

## Summary Statistics

**Framework Components**:
- **Versions**: 3 (ver01, ver02, ver03)
- **Total Files**: 291
- **Configuration Files**: 15+
- **Shell Scripts**: 20+
- **Perl Scripts**: 3+
- **Python Scripts**: 1
- **CSV Tables**: 9+

**Supported Features**:
- **Corners**: 9 (TT, FSG, SFG, FFG, FFAG, SSG, SSAG, FFG_SSG, SSG_FFG)
- **Temperatures**: Configurable (-40°C to 125°C typical)
- **Voltage Sweeps**: 1-3 supplies, min/nom/max
- **Conditions**: 4 (perf, func, htol, hvqk)
- **Simulators**: 2 (PrimeSim, FineSim)
- **Simulation Modes**: 3 (AC, DC, transient)

---

**Document Status**: ✅ Complete  
**Next Document**: TIER2_TESTBENCH_ANALYSIS.md  
**Cross-References**: GPIO_ANALYSIS.md, I3C_ANALYSIS.md, COMPARISON.md
