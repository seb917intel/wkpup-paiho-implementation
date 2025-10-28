# GPIO runme.sh Analysis and Documentation

## Overview
This document provides a comprehensive analysis of the GPIO weak pull-up (WKPUP) simulation framework located in `gpio/1p1v/`. This analysis includes all scripts, configuration files, dependencies, and external resources referenced by the simulation system.

## Repository Structure
```
gpio/
└── 1p1v/
    ├── runme.sh           # Main execution script
    ├── config.cfg         # Configuration parameters
    └── template/
        └── sim_tx.sp      # SPICE simulation template
```

## 1. Main Execution Script: runme.sh

### Location
`/home/runner/work/wkpup-paiho-implementation/wkpup-paiho-implementation/gpio/1p1v/runme.sh`

### Purpose
The `runme.sh` script is the main automation framework for running Process-Voltage-Temperature (PVT) corner simulations for GPIO weak pull-up circuits.

### Script Analysis

#### Dependencies and Sourced Scripts
The runme.sh script sources several external scripts from a shared simulation framework:

1. **Script Parameter File** (Line 7)
   - Path: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/alias_param_source/script_param`
   - Purpose: Defines global script paths and parameters
   - Sets the `$script_path` variable for locating other scripts

2. **Configuration Reader** (Line 14)
   - Path: `/$script_path/configuration/read_cfg.sh`
   - Purpose: Parses and reads the config.cfg file
   - Function: `read_cfg` - Loads configuration parameters into environment

3. **Runtime Functions** (Line 15)
   - Path: `/$script_path/runme_script/runme_func.sh`
   - Purpose: Provides utility functions used by the main script
   - Functions include:
     - `logging()` - Logs messages to script_logging.log
     - `run_sim()` - Executes simulations for specified corners

4. **PVT Simulation Script** (Referenced via `$sim_pvt` variable)
   - Path: Defined in script_param or can be manually set
   - Purpose: Main simulation engine that generates, runs, and processes simulations
   - Operations: gen, ext, srt, bkp, usr_script

#### Script Variables

**User Customization Variables:**
- `script_opt`: Controls execution mode
  - Options: `Gen_run_compile_all`, `Gen_only`, `run_only_all`, `run_only_typical`, 
    `run_only_cworst_CCworst_T`, `run_only_cbest_CCbest_T`, `compile_only`
  - Current: `Gen_run_compile_all`
- `usr_script`: Enable user-defined scripts (`Yes` or `No`)
  - Current: `No`

**System Variables:**
- `current_path`: Working directory (PWD)
- `cfg_file`: Configuration file name (`config.cfg`)
- `timestamp`: Execution timestamp in YYYYMMDDHHmm format
- `start_time`: Script start time in epoch seconds
- `end_time`: Script end time in epoch seconds
- `delta`: Execution duration in seconds
- `hours`: Execution duration in hours (calculated)

#### Execution Flow

**Phase 1: Generation** (Lines 48-54)
- Triggered when: `script_opt` is `Gen_run_compile_all` or `Gen_only`
- Command: `sh $sim_pvt config.cfg gen`
- Purpose: Generate PVT testbench directories and files
- Wait: 10 seconds after generation

**Phase 2: Simulation** (Lines 56-76)
- Triggered when: `script_opt` is `Gen_run_compile_all` or `run_only_all`
- Conditional execution based on `mode` from config.cfg:
  
  **If mode = "prelay":**
  - Run: `run_sim` (without corner specification)
  - Purpose: Pre-layout simulation
  
  **If mode ≠ "prelay":**
  - Run: `run_sim "typical"` - Typical corner simulation
  - Run: `run_sim "cworst_CCworst_T"` - Worst case corner (capacitance worst, temperature)
  - Run: `run_sim "cbest_CCbest_T"` - Best case corner (capacitance best, temperature)

**Phase 3: Compilation/Data Processing** (Lines 92-113)
- Triggered when: `script_opt` is `Gen_run_compile_all` or `compile_only`
- Steps:
  1. Data Extraction: `sh $sim_pvt config.cfg ext` - Extract results from simulations
  2. Data Sorting: `sh $sim_pvt config.cfg srt` - Sort and organize data
  3. Data Backup: `sh $sim_pvt config.cfg bkp` - Backup results
  4. User Script (Optional): `sh $sim_pvt config.cfg usr_script` - Run custom post-processing

**Phase 4: Completion** (Lines 116-121)
- Calculate execution time
- Report completion with duration in hours
- Log to script_logging.log

#### Logging Mechanism
- All major operations are logged using the `logging()` function
- Log file: `script_logging.log` in the current directory
- Log format: Timestamp + Message

## 2. Configuration File: config.cfg

### Location
`/home/runner/work/wkpup-paiho-implementation/wkpup-paiho-implementation/gpio/1p1v/config.cfg`

### Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `mode` | `prelay` | Simulation mode (prelay or postlay) |
| `vccn` | `1p1v` | VCCN voltage domain (1.1V) |
| `vcctx` | `vcctx_NA` | VCCTX voltage (Not Applicable for this config) |
| `1st_supply_swp` | `vcc` | First supply to sweep |
| `2nd_supply_swp` | `vccn` | Second supply to sweep |
| `3rd_supply_swp` | `NA` | Third supply (not used) |
| `condition` | `perf` | Simulation condition (performance) |
| `CPU #` | `4` | Number of CPU cores for simulation |
| `MEM [G]` | `4` | Memory allocation in GB |
| `alter_extraction` | `No` | Alternative extraction method |
| `alter_string#` | `11` | Alternative string number |
| `sim_mode` | `ac` | Simulation mode (AC analysis) |
| `gs/gf_corner` | `Yes` | Global/Fast corner sweeping |
| `vcc_vid` | `Yes` | VCC VID (Voltage Identification) |
| `simulator` | `primesim` | SPICE simulator to use |

### Configuration Usage
These parameters are read by the `read_cfg.sh` script and used to:
- Configure simulation corner variations
- Set resource allocation (CPU/Memory)
- Determine simulation type and modes
- Select the appropriate simulator

## 3. SPICE Simulation Template: sim_tx.sp

### Location
`/home/runner/work/wkpup-paiho-implementation/wkpup-paiho-implementation/gpio/1p1v/template/sim_tx.sp`

### Purpose
This is the SPICE netlist template for weak pull-up GPIO circuit simulation. It defines the circuit under test, simulation parameters, and measurement criteria.

### File Structure Analysis

#### Section 1: Title and Process Corner (Lines 1-6)
```spice
.title fmax
.lib "$DP_HSPICE_MODEL" TT
```
- Simulation title: `fmax` (frequency maximum)
- Process corner: `TT` (Typical-Typical)
- Model library: Specified by environment variable `$DP_HSPICE_MODEL`

#### Section 2: Simulator Options (Lines 8-19)
Key SPICE/PrimeSim options:
- `numdgt=10`: Number of digits for output precision
- `measdgt=8`: Measurement digits precision
- `post=2`: Post-processing output level
- `probe=1`: Enable probing
- `runlvl=5`: Simulation run level (convergence control)
- `accurate=1`: Accurate mode
- `method=gear`: Integration method (Gear method for stiff circuits)
- `post_version=2001`: Post-processor version
- `finesim_mode=spicehd`: FineSim HD mode
- `finesim_method=gear`: FineSim integration method
- `cmi00opt=1`, `cmi01opt=1`: CMI (Compact Model Interface) optimizations
- `finesim_warn_limit=3000`: Warning limit
- `finesim_maxicout=0`: Max initial condition output

#### Section 3: Simulation Parameters (Lines 21-36)
**Temperature:**
- `.temp 100`: 100°C junction temperature

**Voltage Parameters:**
- `vcn=1.1`: VCCN voltage = 1.1V
- `vc=0.75`: VCC voltage = 0.75V
- `vctx=0.7`: VCCTX voltage = 0.7V
- `vccana=0.75`: VCCANA (analog supply) = 0.75V
- `vsh="vcn*0.35/1.1"`: VSS high calculation

**Timing Parameters:**
- `gts=9.2e9`: Gate transfer speed = 9.2 GHz
- `frq="gts/2"`: Frequency = 4.6 GHz
- `prd="1/frq"`: Period calculation
- `tdly="1*prd"`: Time delay = 1 period
- `trf=20p`: Rise/fall time = 20 picoseconds

**Pad Parameters:**
- `pad_parest = 5`: Pad parasitic resistance

#### Section 4: Include Files and Libraries (Lines 38-59)

**SPICE Netlists (.inc files):**
1. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/wrapper_netlist/ioss3_txana_x2.sp`
   - Main circuit wrapper: IOSS3 TX analog x2 transmitter

2. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/eqgen.sp`
   - Equalization generator models

3. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/txcfg.sp`
   - Transmitter configuration models

4. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/no_tcoil_prelay.sp`
   - Pre-layout model without T-coil

**SPICE Libraries (.lib files):**
All from base path: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/`

1. `cb.lib` (default) - Callback/Control block library
2. `tco_ctrl.lib` (default) - T-coil control library
3. `equalization.lib` (disable) - Equalization library (disabled)
4. `uncal_vsshffc.lib` (default) - Uncalibrated VSS high FFC
5. `uncal_vsshleak.lib` (default) - Uncalibrated VSS high leakage
6. `weakpullup.lib` (enable) - **Weak pull-up library (ENABLED)** ← Key for GPIO
7. `uncomp_slewrate.lib` (fast) - Uncompensated slew rate (fast mode)
8. `xtalk.lib` (disable) - Crosstalk library (disabled)
9. `xover.lib` (gear4) - Crossover library (gear4 mode)
10. `txmode.lib` (ctt) - Transmitter mode (CTT - Center Tap Termination)
11. `uncal_oct_rs.lib` (off) - Uncalibrated OCT RS (off)
12. `uncal_oct_rt.lib` (off) - Uncalibrated OCT RT (off)

#### Section 5: Device Under Test (DUT) Instantiation (Line 62)
```spice
xdut datain0 datain1 drven0 drven1 odten padsig0 padsig1 vcc_io vccana_io vccldo_io vccn_io vss_io vssh_io ioss3_txana_x2
```
- Subcircuit instance: `xdut`
- Type: `ioss3_txana_x2` (dual-channel TX analog)
- Inputs: `datain0`, `datain1`, `drven0`, `drven1`, `odten`
- Outputs: `padsig0`, `padsig1`
- Power supplies: `vcc_io`, `vccana_io`, `vccldo_io`, `vccn_io`, `vss_io`, `vssh_io`

#### Section 6: Power Supplies (Lines 64-70)
```spice
vvcc_io vcc_io 0 vc
vvccn_io vccn_io 0 vcn
vvccldo_io vccldo_io 0 vctx
vvccana_io vccana_io 0 vccana
vvssh_io vssh_io 0 vsh
vvss_io vss_io 0 0
```
All voltage sources defined with their respective parameter values.

#### Section 7: Stimulus Signals (Lines 72-79)
```spice
vodten odten 0 0         # ODT enable = 0V (off)
vdrven0 drven0 0 0       # Driver enable 0 = 0V (off)
vdatain0 datain0 0 0     # Data input 0 = 0V
vdrven1 drven1 0 0       # Driver enable 1 = 0V (off)
vdatain1 datain1 0 0     # Data input 1 = 0V
```
All control signals set to 0V (inactive state) for weak pull-up testing.

#### Section 8: Package/PCB Models (Lines 81-87)
Commented out PKG models (not used in pre-layout):
- FMp2 PKG SL global models
- pkg_bump_trace S-parameter model
- pkg_pth_bga S-parameter model
- Package model instance

#### Section 9: Load Termination (Lines 89-92)
```spice
rball0 padsig0 ball0 1   # 1Ω resistance to ball
rball1 padsig1 ball1 1   # 1Ω resistance to ball
vball0 ball0 0 PWL ( 0 0, 10u vcn)  # PWL: 0V→1.1V ramp over 10μs
```
- Simulates package ball connection
- PWL (Piecewise Linear) voltage ramp to test weak pull-up behavior

#### Section 10: Analysis Commands (Lines 95-97)
```spice
.tran 20p 10u   # Transient analysis: 20ps steps, 10μs total
.probe v(*) level = 2 filter="*@*" filter="*:*"  # Probe all voltages
```

#### Section 11: Measurements (Lines 100-110)
**Current Measurements:**
1. `ioh_0`: Initial current at t=0
2. `ioh`: Current when ball0 reaches 0.65×VCN (VOH level)
3. `ioh0`: Current at VOH + 50mV
4. `ioh1`: Current at VOH - 50mV

**Resistance Calculations:**
5. `rwkpull0`: Weak pull-up resistance at t=0 = VCN/ioh_0
6. `rwkpull_vih`: Weak pull-up resistance at VIH = 0.35×VCN/ioh
7. `rwkpull_vih2`: Differential resistance = 100mV/(ioh0-ioh1)

**Voltage Measurements:**
8. `vwkp`: Weak pull-up voltage at end (10μs)
9. `vwkp_drop`: Voltage drop = VCN - vwkp

These measurements characterize:
- DC weak pull-up resistance
- Pull-up strength at different voltage levels
- Final settling voltage
- Voltage droop under load

## 4. External Dependencies

### Shared Simulation Framework
Base path: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/`

**Directory Structure:**
```
simulation_script/
├── alias_param_source/
│   └── script_param              # Global parameters and paths
├── configuration/
│   └── read_cfg.sh              # Configuration file parser
├── runme_script/
│   └── runme_func.sh            # Runtime utility functions
└── auto_pvt/
    └── ver02/
        └── sim_pvt.sh           # Main PVT simulation engine
```

### Circuit Libraries
Base path: `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/`

**Directory Structure:**
```
circuitsim/common/
├── cir_wrap/
│   ├── wrapper_netlist/
│   │   └── ioss3_txana_x2.sp   # Main TX wrapper
│   ├── models/
│   │   ├── eqgen.sp            # Equalization
│   │   ├── txcfg.sp            # TX configuration
│   │   └── no_tcoil_prelay.sp  # Pre-layout model
│   └── pcb_pkg/                # Package models (unused in prelay)
└── lib/
    └── bkp/                     # Backup library files
        ├── cb.lib
        ├── tco_ctrl.lib
        ├── equalization.lib
        ├── uncal_vsshffc.lib
        ├── uncal_vsshleak.lib
        ├── weakpullup.lib      # ← GPIO weak pull-up models
        ├── uncomp_slewrate.lib
        ├── xtalk.lib
        ├── xover.lib
        ├── txmode.lib
        ├── uncal_oct_rs.lib
        └── uncal_oct_rt.lib
```

### PDK Models
Path: Environment variable `$DP_HSPICE_MODEL` points to process technology models
- Expected to contain TT (Typical-Typical) corner definitions
- Likely points to Intel's CLN3P (3nm process) PDK

### Simulator
- **Tool**: Synopsys PrimeSim
- **Version**: Expected W-2024.09-SP1 or compatible
- **Invocation**: Through automation scripts
- **Modes**: SPICE HD, Gear integration method

## 5. Workflow Summary

### Complete Execution Flow
1. **Initialization**
   - Source global parameters from script_param
   - Read configuration from config.cfg
   - Load utility functions

2. **Generation Phase** (if enabled)
   - Generate PVT corner directories
   - Create simulation netlists from template
   - Copy/modify sim_tx.sp for each corner

3. **Simulation Phase** (if enabled)
   - Submit jobs for each corner (typical, cworst, cbest)
   - Run PrimeSim simulations
   - Generate waveform and measurement data

4. **Compilation Phase** (if enabled)
   - Extract measurement results
   - Sort and organize data
   - Create backup of results
   - Optional: Run user-defined post-processing

5. **Reporting**
   - Log execution time
   - Output completion status

### Key Simulation Objectives
The GPIO weak pull-up simulation measures:
1. **Pull-up resistance** at different voltage levels
2. **Current drive capability** at VOH (output high voltage)
3. **Voltage droop** under static load
4. **Settling behavior** during voltage ramp
5. **PVT corner variations** (across process, voltage, temperature)

### Output Files (Expected)
- `script_logging.log` - Execution log
- Simulation results directories (per corner)
- Measurement files (.mt0 format)
- Waveform databases (.fsdb or .wdb)
- Extracted data files
- Backup archives

## 6. Key Findings

### GPIO-Specific Configuration
- **Weak pull-up library is ENABLED**: Line 52 in sim_tx.sp
  ```spice
  .lib "weakpullup.lib" enable
  ```
- This is the critical differentiator for GPIO weak pull-up characterization

### Simulation Type
- **Pre-layout simulation**: mode=prelay in config.cfg
- No package models active (all commented out)
- Simplified load model (1Ω + PWL voltage source)

### Measurement Focus
- Primary metric: Weak pull-up resistance (rwkpull)
- Secondary metrics: Current capability, voltage drop
- Test condition: Ramp from 0V to VCN (1.1V) over 10μs

### Resource Requirements
- 4 CPU cores
- 4GB memory
- PrimeSim simulator license
- Access to shared NFS storage for libraries

## 7. Dependencies Summary Table

| Category | Count | Purpose |
|----------|-------|---------|
| Shell Scripts | 4 | Automation and orchestration |
| Configuration Files | 1 | Parameter specification |
| SPICE Templates | 1 | Circuit netlist |
| SPICE Include Files | 4 | Circuit components |
| SPICE Libraries | 12 | Behavioral models |
| External Tools | 1 | PrimeSim simulator |
| PDK Models | 1 | Process technology |

## 8. File Access List

### Repository Files (Local)
1. `/home/runner/work/wkpup-paiho-implementation/wkpup-paiho-implementation/gpio/1p1v/runme.sh`
2. `/home/runner/work/wkpup-paiho-implementation/wkpup-paiho-implementation/gpio/1p1v/config.cfg`
3. `/home/runner/work/wkpup-paiho-implementation/wkpup-paiho-implementation/gpio/1p1v/template/sim_tx.sp`

### External Files (NFS Shared Storage)
**Simulation Scripts:**
4. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/alias_param_source/script_param`
5. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/configuration/read_cfg.sh`
6. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/runme_script/runme_func.sh`
7. `$script_path/sim_pvt.sh` (auto_pvt/ver02/)

**Circuit Files:**
8. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/wrapper_netlist/ioss3_txana_x2.sp`
9. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/eqgen.sp`
10. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/txcfg.sp`
11. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/no_tcoil_prelay.sp`

**Library Files:**
12. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/cb.lib`
13. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/tco_ctrl.lib`
14. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/equalization.lib`
15. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_vsshffc.lib`
16. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_vsshleak.lib`
17. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/weakpullup.lib` ← **Critical for GPIO**
18. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncomp_slewrate.lib`
19. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/xtalk.lib`
20. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/xover.lib`
21. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/txmode.lib`
22. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_oct_rs.lib`
23. `/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_oct_rt.lib`

**Total Files**: 23 files accessed/referenced

---

*Documentation generated by comprehensive recursive analysis of GPIO runme.sh and all dependencies*
*Analysis Date: 2025-10-28*
