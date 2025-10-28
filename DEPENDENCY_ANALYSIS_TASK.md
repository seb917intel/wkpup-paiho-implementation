# Task: Complete Dependency Analysis for WKPUP Simulation Framework

## Objective
Perform comprehensive analysis of all available dependency files, backup configurations, and simulation artifacts for GPIO and I3C WKPUP implementations to understand the complete workflow and identify the key difference (enable vs enable_i3c parameter).

## Available Resources in Repository

### 1. Dependency Files (291 files total)
Located in: `gpio/1p1v/dependencies/scripts/simulation_script/`

#### Active Dependencies (78 files):
- **Alias/Parameter Sources**: `alias_param_source/script_alias`, `script_param`
- **Auto PVT Framework**: 
  - `auto_pvt/ver01/`, `auto_pvt/ver02/`, `auto_pvt/ver03/`
  - Configuration scripts, data extraction, testbench generation
- **Utility Scripts**: `ultilities/libgen.py`, `nb_sim/nb_sim.sh`
- **Examples**: `auto_pvt/Example/` with templates and config files

#### Backup Samples for Reference (213 files):
- **Test Configurations**: `prelay/` and `polo/` test cases
- **Backup Directories**: `00bkp_202508191107/`, `00bkp_202508191118/`, `00bkp_202508191157/`
- **PVT Reports**: Corner analysis reports (TT, FF, SS, FS, SF) across temperatures (-40°C to 125°C)
- **Testbench Backups**: Historical `sim_tx.sp` versions showing parameter evolution

### 2. Analysis Documents Already Available
- `GPIO_ANALYSIS.md` (18.8 KB) - Documents 23 GPIO dependencies
- `I3C_ANALYSIS.md` (25.2 KB) - Documents 34+ I3C dependencies  
- `COMPARISON.md` (15.4 KB) - Shows 99% similarity, identifies line 52 difference
- `INDEX.md` (13.3 KB) - Navigation guide
- `DEPENDENCY_MIGRATION_STATUS.md` (14.5 KB) - External dependency mapping

## Analysis Workflow

### Phase 1: Read All Available Dependency Files
**Goal**: Understand complete automation framework structure

#### 1.1 Core Configuration Scripts
Read and analyze:
- `alias_param_source/script_param` - Parameter definitions and paths
- `alias_param_source/script_alias` - Script aliases and shortcuts
- `auto_pvt/ver*/configuration/read_cfg.sh` - Config file parsers
- `auto_pvt/ver*/configuration/read_corner.sh` - Corner extraction logic
- `auto_pvt/ver*/configuration/read_supply.sh` - Supply voltage handling
- `auto_pvt/ver*/configuration/table_*.csv` - Corner and supply tables

**Extract**:
- How `script_path` is defined
- How configurations are parsed
- What parameters control GPIO vs I3C mode

#### 1.2 Simulation Orchestration Scripts
Read and analyze:
- `auto_pvt/ver*/sim_pvt.sh` - Main PVT simulation driver
- `auto_pvt/ver*/runme_script/runme.sh` - Top-level execution script
- `auto_pvt/ver*/runme_script/runme_func.sh` - Helper functions
- `nb_sim/nb_sim.sh` - Non-batch simulation wrapper

**Extract**:
- Simulation flow from start to finish
- How testbenches are generated and executed
- Where `.lib` file selection happens (enable vs enable_i3c)

#### 1.3 Testbench Generation
Read and analyze:
- `auto_pvt/ver*/tb_gen/gen_tb.pl` - Perl testbench generator
- `auto_pvt/ver*/tb_gen/pvt_loop.sh` - PVT loop generator
- `auto_pvt/Example/*/template/sim_tx.sp` - Template SPICE files

**Extract**:
- How line 52 `.lib "weakpullup.lib" enable` gets inserted
- Template substitution mechanism
- Parameter propagation from config to netlist

#### 1.4 Data Extraction Scripts
Read and analyze:
- `auto_pvt/ver*/data_extraction/extract_alt.sh` - Alternative extraction
- `auto_pvt/ver*/data_extraction/move.sh` - Results organization
- `ultilities/alter_extraction_script/extract_alt.sh` - Utility extractor

**Extract**:
- What simulation outputs are collected
- How reports are generated
- Post-processing workflow

#### 1.5 Utility Scripts
Read and analyze:
- `ultilities/libgen.py` - Library generation Python script
- `debug/test_log/runlog.sh` - Logging utilities

**Extract**:
- Tool dependencies (Python, Perl, shell)
- Helper functionality

### Phase 2: Analyze Backup Files for Historical Context
**Goal**: Understand parameter evolution and testing patterns

#### 2.1 Test Configuration Analysis
Read backup configs from `00bkp_*/`:
- `prelay/` test configurations (pre-layout simulation)
- `polo/` test configurations (post-layout simulation)
- `config.cfg` files - Parameter settings over time
- `runme.sh` scripts - Execution commands

**Extract**:
- Testing methodology differences
- Parameter variations across test runs
- Pre-layout vs post-layout differences

#### 2.2 Testbench Evolution Analysis
Compare `sim_tx.sp` files across:
- `template/sim_tx.sp` (current template)
- `00bkp_202508191107/tb_bkp/*/sim_tx.sp` (backup set 1)
- `00bkp_202508191118/tb_bkp/*/sim_tx.sp` (backup set 2)
- `00bkp_202508191157/tb_bkp/*/sim_tx.sp` (backup set 3)

**Extract**:
- How line 52 evolved
- What other parameters changed
- Voltage/corner variations (v1nom, v1max, v1min)

#### 2.3 PVT Report Analysis
Read reports from `00bkp_*/report/`:
- `report_TT_*.txt` - Typical corner results
- `report_FF*_*.txt` - Fast corner results  
- `report_SS*_*.txt` - Slow corner results
- `report_FS*_*.txt`, `report_SF*_*.txt` - Mixed corners

**Extract**:
- What metrics are reported
- Pass/fail criteria
- Temperature sweep patterns (-40°C, 85°C, 100°C, 125°C)

### Phase 3: Cross-Reference with Existing Analysis
**Goal**: Validate and extend findings from Copilot-generated docs

#### 3.1 Validate GPIO Analysis
Compare Phase 1-2 findings with `GPIO_ANALYSIS.md`:
- Confirm 23 identified dependencies
- Validate file paths and relationships
- Check for missing files

#### 3.2 Validate I3C Analysis  
Compare Phase 1-2 findings with `I3C_ANALYSIS.md`:
- Confirm 34+ identified dependencies
- Validate the enable_i3c parameter usage
- Check for unique I3C requirements

#### 3.3 Extend Comparison Analysis
Build on `COMPARISON.md`:
- Confirm line 52 is the ONLY difference
- Verify 99% code reuse claim
- Document the parameter propagation chain

### Phase 4: Map External Dependencies
**Goal**: Document files NOT in repository that need access

#### 4.1 Circuit Netlists
From existing analysis, identify:
- `ioss3_txana_x2.sp` - Wrapper netlist location
- `eqgen.sp`, `txcfg.sp`, `no_tcoil_prelay.sp` - Model files
- Any subcircuits referenced in templates

#### 4.2 Library Files
From existing analysis, identify:
- `weakpullup.lib` location and sections
- Other 11 `.lib` files
- PDK model files

#### 4.3 Tool Dependencies
From scripts, identify:
- SPICE simulator requirements
- Python/Perl versions
- Shell requirements

## Deliverables

### 1. TIER1_FRAMEWORK_ANALYSIS.md
**Contents**:
- Complete automation framework architecture
- Script-to-script call chain
- Configuration flow (CSV → shell → testbench)
- Parameter propagation mechanism
- Tool dependencies

**Structure**:
```markdown
# Framework Overview
## Automation Versions (ver01, ver02, ver03)
## Configuration System
## Testbench Generation Pipeline
## Simulation Execution Flow
## Data Extraction Workflow
## Tool Requirements
```

### 2. TIER2_TESTBENCH_ANALYSIS.md
**Contents**:
- Template structure analysis
- Line 52 parameter insertion mechanism
- Backup file evolution timeline
- GPIO vs I3C testbench differences
- PVT corner/voltage sweep patterns

**Structure**:
```markdown
# Testbench Architecture
## Template System (sim_tx.sp)
## Parameter Substitution
## Backup Analysis (3 timestamped sets)
## Critical Line 52: enable vs enable_i3c
## Corner/Temperature/Voltage Matrix
```

### 3. TIER3_DEPENDENCY_MAP.md
**Contents**:
- Visual dependency tree (ASCII art or Mermaid diagram)
- File-to-file relationships
- In-repo vs external file classification
- Missing file identification
- Access requirements

**Structure**:
```markdown
# Complete Dependency Graph

## Level 1: Entry Points
runme.sh → runme_func.sh → sim_pvt.sh

## Level 2: Configuration
script_param → read_cfg.sh → table_*.csv

## Level 3: Testbench Generation  
gen_tb.pl → template/sim_tx.sp → [EXTERNAL: netlists]

## Level 4: Libraries
sim_tx.sp → weakpullup.lib (enable/enable_i3c) → [EXTERNAL: PDK]

## Level 5: PDK Models
[EXTERNAL: PDK includes chain]

## Files Available in Repo: [list]
## Files Requiring External Access: [list with paths]
```

### 4. CRITICAL_FINDINGS.md
**Contents**:
- The enable vs enable_i3c parameter mechanism
- How one codebase serves both GPIO and I3C
- Configuration-based switching mechanism
- Implications for reuse

**Structure**:
```markdown
# Key Discoveries

## The Single-Parameter Difference
- Location: Line 52 of sim_tx.sp
- Mechanism: .lib section selection
- Impact: Complete circuit behavior change

## Code Reuse Strategy
- 99% shared automation code
- Parameter-driven differentiation
- Template-based generation

## Workflow Insights
- [Findings from backup analysis]
- [Findings from PVT reports]

## Recommendations
- [For future development]
- [For I3C implementation]
```

### 5. UPDATED_DEPENDENCY_MIGRATION_STATUS.md
**Contents**:
- Update existing file with:
  - ✅ Files successfully analyzed in repo
  - ⚠️ Files requiring external access
  - 📊 Analysis completion status
  - 🔍 New dependencies discovered

## Success Criteria

- [ ] All 78 active dependency files read and analyzed
- [ ] All 213 backup files examined for context
- [ ] Complete call chain documented (runme.sh → PDK)
- [ ] Enable vs enable_i3c mechanism fully explained
- [ ] Dependency graph shows complete file relationships
- [ ] Clear separation: in-repo vs external dependencies
- [ ] All 4 deliverable documents created
- [ ] Existing analysis documents validated and extended

## Instructions for Agent

1. **Start with Available Files**: Read all 291 dependency files in the repository
2. **Analyze Incrementally**: Work through script_param → configs → testbenches → reports
3. **Document as You Go**: Create deliverable files progressively
4. **Cross-Reference**: Validate against existing GPIO_ANALYSIS.md, I3C_ANALYSIS.md, COMPARISON.md
5. **Identify Gaps**: Note files referenced but not available (external dependencies)
6. **Focus on Line 52**: Trace how the enable/enable_i3c parameter flows through the system
7. **No External Access Required**: Work entirely with repository contents
8. **Deliverable Priority**: 
   - First: TIER1_FRAMEWORK_ANALYSIS.md (understand structure)
   - Second: TIER2_TESTBENCH_ANALYSIS.md (understand line 52)
   - Third: TIER3_DEPENDENCY_MAP.md (map everything)
   - Fourth: CRITICAL_FINDINGS.md (summarize insights)
   - Fifth: Update DEPENDENCY_MIGRATION_STATUS.md

## Notes
- This is a code archaeology task using available artifacts
- Backup files are historical snapshots showing evolution
- The goal is complete understanding of the single-parameter differentiation strategy
- All analysis should support the "99% code reuse" finding from COMPARISON.md
