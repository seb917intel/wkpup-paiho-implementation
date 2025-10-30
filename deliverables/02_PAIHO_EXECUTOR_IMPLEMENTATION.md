# Deliverable 2: paiho_executor.py Implementation Specification

## Overview

**Module**: `paiho_executor.py`  
**Purpose**: Execute Pai Ho's validated scripts via subprocess, monitor progress, handle errors  
**Lines of Code**: ~500 lines  
**Priority**: P0 (Week 3-4, Core Implementation)  
**Dependencies**: Deliverable 1 (config_generator.py)

## Ground Truth Validation

This specification is validated against **COMPREHENSIVE_ANALYSIS.md**, which documents Pai Ho's proven wkpup2 simulation workflow.

### Key References from COMPREHENSIVE_ANALYSIS.md:

1. **Complete End-to-End Workflow** (6 Stages):
   ```
   STAGE 1 (gen):  Generation - Creates 84 PVT netlists
   STAGE 2 (run):  Simulation - Executes SPICE simulations
   STAGE 3 (ext):  Extraction - Parses .mt0 measurement files
   STAGE 4 (srt):  Sorting - Creates consolidated reports
   STAGE 5 (bkp):  Backup - Archives results with timestamp
   STAGE 6 (usr):  User Script - Optional custom processing
   ```

2. **sim_pvt.sh Orchestration**:
   - Main script: 589 lines (ver03)
   - Command format: `bash sim_pvt.sh config.cfg <stage>`
   - Working directory: Domain path (e.g., `gpio/1p1v/`)

3. **Critical Principle** (Golden Rule):
   > "NEVER modify Pai Ho's original files"
   > 
   > "All files chmod 444 (read-only)"
   > 
   > "NO modifications to Pai Ho's files - only calls them"

## Functional Requirements

### FR-1: Script Execution via Subprocess

**Function**: Execute Pai Ho's sim_pvt.sh without any modifications

**Implementation**:
```python
def run_stage(self, config_file: str, stage: str) -> Dict:
    """
    Run a single simulation stage
    
    Args:
        config_file: Path to config.cfg
        stage: Stage name (gen/run/ext/srt/bkp/usr)
        
    Returns:
        Dict with stdout, stderr, returncode
    """
    cmd = [
        'bash',
        str(self.sim_pvt_script),
        config_file,
        stage
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,  # Don't raise on non-zero exit
        cwd=str(self.domain_path)
    )
    
    return {
        'stage': stage,
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'success': result.returncode == 0
    }
```

**Critical Requirements**:
- Must execute in correct working directory (`domain_path`)
- Must capture both stdout and stderr for logging
- Must NOT raise exceptions on sim_pvt.sh errors (handle gracefully)
- Must preserve exact exit codes from Pai Ho's scripts

### FR-2: Multi-Stage Workflow Execution

**Function**: Execute complete 6-stage workflow or selected stages

**Supported Workflows**:

1. **Full Workflow** (default):
   ```python
   stages = ['gen', 'run', 'ext', 'srt', 'bkp']
   # usr_script optional, controlled by parameter
   ```

2. **Partial Workflows**:
   - Generation only: `['gen']`
   - Run and extract: `['run', 'ext']`
   - Compile only: `['ext', 'srt', 'bkp']`

**Implementation**:
```python
def run_simulation(self, config_file: str, stages: Optional[List[str]] = None) -> Dict:
    """
    Run full simulation workflow
    
    Args:
        config_file: Path to config.cfg
        stages: List of stages to run (default: all)
        
    Returns:
        Dict with execution results per stage
    """
    if stages is None:
        stages = self.STAGES  # ['gen', 'run', 'ext', 'srt', 'bkp', 'usr']
    
    results = {}
    
    for stage in stages:
        self.logger.info(f"Running stage: {stage}")
        result = self.run_stage(config_file, stage)
        results[stage] = result
        
        if result['returncode'] != 0:
            self.logger.error(f"Stage {stage} failed")
            break  # Stop on first failure
    
    return results
```

**Failure Handling**:
- Stop execution on first stage failure
- Return partial results (all stages attempted up to failure)
- Preserve all error messages for debugging

### FR-3: Progress Monitoring

**Function**: Track execution progress and provide status updates

**Monitoring Levels**:

1. **Stage-Level Progress**:
   ```python
   def monitor_progress(self) -> Dict:
       """
       Monitor current stage execution
       
       Returns:
           Dict with stage name, status, elapsed time
       """
       # Track which stage is currently running
       # Measure elapsed time per stage
       # Detect hung/stalled executions
   ```

2. **File-Based Progress** (for long stages like 'run'):
   ```python
   def check_simulation_progress(self) -> int:
       """
       Count completed simulations by checking .mt0 files
       
       Returns:
           Number of completed simulations
       """
       # Count existing .mt0 files in corner directories
       # Compare to expected total (from PVT matrix)
       # Return completion percentage
   ```

3. **Log Streaming** (optional):
   ```python
   def stream_logs(self, callback: Callable[[str], None]):
       """
       Stream stdout/stderr to callback for real-time display
       
       Args:
           callback: Function to call with each log line
       """
       # Useful for web UI live updates
   ```

### FR-4: Error Handling and Recovery

**Function**: Detect and report errors with actionable information

**Error Categories**:

1. **Setup Errors**:
   - sim_pvt.sh not found
   - Working directory doesn't exist
   - config.cfg file invalid or missing

2. **Execution Errors**:
   - Script exits with non-zero code
   - Timeout (stage running too long)
   - Resource exhaustion (disk full, memory)

3. **Output Errors**:
   - Expected files not created
   - Incomplete results
   - Corrupted output files

**Implementation**:
```python
class ExecutionError(Exception):
    """Base class for execution errors"""
    pass

class ScriptNotFoundError(ExecutionError):
    """Raised when sim_pvt.sh cannot be located"""
    pass

class StageFailedError(ExecutionError):
    """Raised when a stage fails with non-zero exit"""
    pass

class TimeoutError(ExecutionError):
    """Raised when execution exceeds timeout"""
    pass
```

**Error Recovery**:
```python
def retry_stage(self, stage: str, max_retries: int = 3) -> Dict:
    """
    Retry a failed stage with exponential backoff
    
    Args:
        stage: Stage name to retry
        max_retries: Maximum retry attempts
        
    Returns:
        Result dict from successful attempt or final failure
    """
    # Useful for transient failures (network, cluster)
```

### FR-5: Output Verification

**Function**: Verify expected outputs are created

**Verification Points**:

After **gen** stage:
```python
expected_files = [
    f"{corner}/{extraction}/{extraction}_{temp}/{voltage}/sim_tx.sp"
    for corner, extraction, temp, voltage in pvt_matrix
]
```

After **run** stage:
```python
expected_files = [
    f"{corner}/{extraction}/{extraction}_{temp}/{voltage}/sim_tx.mt0"
    for corner, extraction, temp, voltage in pvt_matrix
]
```

After **srt** stage:
```python
expected_files = [
    "report/creport.txt",
    "report/report_TT_typical_85_v1nom.txt",
    # ... more reports
]
```

**Implementation**:
```python
def verify_output(self, expected_files: List[str]) -> bool:
    """
    Verify expected output files exist
    
    Args:
        expected_files: List of file paths to check
        
    Returns:
        True if all files exist
    """
    for filepath in expected_files:
        full_path = self.domain_path / filepath
        if not full_path.exists():
            self.logger.error(f"Expected file not found: {full_path}")
            return False
    return True
```

## Non-Functional Requirements

### NFR-1: Absolutely Zero Modifications to Pai Ho's Files

**Requirement**: This module must NEVER write to Pai Ho's scripts

**Enforcement**:
```python
def __init__(self, domain_path: str, script_version: str = 'ver03'):
    """
    Initialize executor
    
    Args:
        domain_path: Path to voltage domain (e.g., gpio/1p1v)
        script_version: Version to use (must be 'ver03')
    """
    if script_version != 'ver03':
        raise ValueError("Only ver03 is supported")
        
    self.domain_path = Path(domain_path)
    self.sim_pvt_script = self.domain_path / 'sim_pvt.sh'
    
    # Verify script exists and is readable
    if not self.sim_pvt_script.exists():
        raise FileNotFoundError(f"sim_pvt.sh not found at {self.sim_pvt_script}")
    
    # Verify script is executable
    if not os.access(self.sim_pvt_script, os.X_OK):
        raise PermissionError(f"sim_pvt.sh is not executable")
```

**Verification**:
- No file writes to Pai Ho's directories
- Only read access to sim_pvt.sh
- Only subprocess.run() calls, never file edits

### NFR-2: Bit-Identical Execution

**Requirement**: subprocess execution must produce identical results to manual execution

**Test**:
```python
def test_bit_identical_execution():
    # Manual execution
    os.system("cd gpio/1p1v && bash sim_pvt.sh config.cfg gen")
    manual_netlist = "TT/typical/typical_85/v1nom/sim_tx.sp"
    
    # Automated execution
    executor = PaiHoExecutor("gpio/1p1v")
    executor.run_stage("config.cfg", "gen")
    auto_netlist = "TT/typical/typical_85/v1nom/sim_tx.sp"
    
    # Compare
    assert filecmp.cmp(manual_netlist, auto_netlist)
```

### NFR-3: Performance and Timeout

**Requirements**:

| Stage | Expected Duration | Timeout |
|-------|------------------|---------|
| gen | 1-5 minutes | 10 minutes |
| run | 1-3 hours | 6 hours |
| ext | 10-60 seconds | 5 minutes |
| srt | 1-10 seconds | 2 minutes |
| bkp | 5-30 seconds | 5 minutes |
| usr | Variable | User-defined |

**Implementation**:
```python
STAGE_TIMEOUTS = {
    'gen': 600,   # 10 minutes
    'run': 21600, # 6 hours
    'ext': 300,   # 5 minutes
    'srt': 120,   # 2 minutes
    'bkp': 300,   # 5 minutes
    'usr': 3600   # 1 hour (configurable)
}

def run_stage(self, config_file: str, stage: str) -> Dict:
    """Run with timeout"""
    timeout = self.STAGE_TIMEOUTS.get(stage, 3600)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,  # Add timeout
        cwd=str(self.domain_path)
    )
```

### NFR-4: Logging and Debugging

**Requirements**:
- All subprocess calls logged with full command
- All stdout/stderr captured and stored
- Stage start/end times logged
- Working directory logged

**Implementation**:
```python
import logging

self.logger = logging.getLogger(__name__)

def run_stage(self, config_file: str, stage: str) -> Dict:
    """Run with comprehensive logging"""
    
    self.logger.info(f"Starting stage: {stage}")
    self.logger.debug(f"Working directory: {self.domain_path}")
    self.logger.debug(f"Config file: {config_file}")
    self.logger.debug(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    result = subprocess.run(...)
    elapsed = time.time() - start_time
    
    self.logger.info(f"Stage {stage} completed in {elapsed:.2f}s")
    
    if result.returncode != 0:
        self.logger.error(f"Stage {stage} failed with exit code {result.returncode}")
        self.logger.error(f"stderr: {result.stderr}")
```

## Implementation Structure

### Class Design

```python
#!/usr/bin/env python3
"""
Pai Ho Executor
Executes Pai Ho's scripts via subprocess
NEVER modifies Pai Ho's files - only calls them
"""

import subprocess
import os
import logging
import time
from typing import Optional, List, Dict
from pathlib import Path

class PaiHoExecutor:
    """
    Executes Pai Ho's validated scripts
    All execution via subprocess.run() - NO file modifications
    """
    
    STAGES = ['gen', 'run', 'ext', 'srt', 'bkp', 'usr']
    
    STAGE_TIMEOUTS = {
        'gen': 600,
        'run': 21600,
        'ext': 300,
        'srt': 120,
        'bkp': 300,
        'usr': 3600
    }
    
    def __init__(self, domain_path: str, script_version: str = 'ver03'):
        """Initialize executor"""
        
    def run_simulation(self, config_file: str, stages: Optional[List[str]] = None) -> Dict:
        """Run full simulation workflow"""
        
    def run_stage(self, config_file: str, stage: str) -> Dict:
        """Run a single simulation stage"""
        
    def monitor_progress(self) -> Dict:
        """Monitor current stage execution"""
        
    def check_simulation_progress(self) -> int:
        """Count completed simulations"""
        
    def verify_output(self, expected_files: List[str]) -> bool:
        """Verify expected output files exist"""
        
    def retry_stage(self, stage: str, max_retries: int = 3) -> Dict:
        """Retry a failed stage"""
```

### Return Value Structures

**Single Stage Result**:
```python
{
    'stage': 'gen',
    'returncode': 0,
    'stdout': '...',
    'stderr': '',
    'success': True,
    'elapsed_time': 45.2,
    'start_time': '2025-10-30T10:15:00',
    'end_time': '2025-10-30T10:15:45'
}
```

**Multi-Stage Result**:
```python
{
    'gen': { 'stage': 'gen', 'success': True, ... },
    'run': { 'stage': 'run', 'success': True, ... },
    'ext': { 'stage': 'ext', 'success': False, 'returncode': 1, ... },
    'overall_success': False,
    'failed_stage': 'ext',
    'total_elapsed': 7245.8
}
```

## Testing Strategy

### Unit Tests (30+ test cases)

**Test Categories**:

1. **Initialization Tests** (5 tests)
   - Valid domain path initializes correctly
   - Invalid domain path raises error
   - Missing sim_pvt.sh raises FileNotFoundError
   - Non-executable sim_pvt.sh raises PermissionError
   - Only ver03 accepted

2. **Single Stage Execution Tests** (12 tests)
   - gen stage executes successfully
   - run stage executes successfully
   - ext stage executes successfully
   - srt stage executes successfully
   - bkp stage executes successfully
   - Invalid stage raises ValueError
   - Stage failure captured correctly
   - Timeout handled gracefully
   - Working directory set correctly
   - Config file path passed correctly
   - stdout/stderr captured
   - Exit code preserved

3. **Multi-Stage Execution Tests** (8 tests)
   - Full workflow executes all stages
   - Partial workflow (gen only) works
   - Partial workflow (ext+srt+bkp) works
   - Failure in middle stage stops execution
   - Results accumulate correctly
   - Overall success flag set correctly
   - Failed stage identified
   - Timing information accurate

4. **Error Handling Tests** (5 tests)
   - Missing config.cfg handled
   - Script error captured
   - Timeout raises TimeoutError
   - Retry logic works
   - Max retries respected

### Integration Tests

```python
def test_end_to_end_execution():
    """Test complete workflow with real sim_pvt.sh"""
    
    # Setup
    executor = PaiHoExecutor('gpio/1p1v')
    config_file = 'test_config.cfg'
    
    # Execute gen stage only (fast test)
    results = executor.run_simulation(config_file, stages=['gen'])
    
    # Verify
    assert results['gen']['success'] == True
    assert results['gen']['returncode'] == 0
    
    # Verify netlists created
    expected = [
        'TT/typical/typical_85/v1nom/sim_tx.sp',
        'TT/typical/typical_85/v1min/sim_tx.sp',
        # ... check a few key files
    ]
    assert executor.verify_output(expected)
```

```python
def test_bit_identical_to_manual():
    """Verify subprocess execution matches manual execution"""
    
    # Run manually
    subprocess.run(['bash', 'sim_pvt.sh', 'config.cfg', 'gen'], cwd='gpio/1p1v')
    manual_file = 'gpio/1p1v/TT/typical/typical_85/v1nom/sim_tx.sp'
    manual_hash = hashlib.md5(open(manual_file, 'rb').read()).hexdigest()
    
    # Clean and run via executor
    # ... cleanup ...
    executor = PaiHoExecutor('gpio/1p1v')
    executor.run_stage('config.cfg', 'gen')
    auto_file = 'gpio/1p1v/TT/typical/typical_85/v1nom/sim_tx.sp'
    auto_hash = hashlib.md5(open(auto_file, 'rb').read()).hexdigest()
    
    # Must be bit-identical
    assert manual_hash == auto_hash
```

## Verification Checklist

Before considering this deliverable complete, verify:

- [ ] All 6 stages execute via subprocess.run()
- [ ] No Pai Ho files modified (read-only access only)
- [ ] Bit-identical execution to manual (hash comparison test passes)
- [ ] All unit tests pass (30+ tests)
- [ ] Integration test passes (end-to-end workflow)
- [ ] Timeout handling works
- [ ] Error messages are clear and actionable
- [ ] Logging comprehensive and useful
- [ ] Code reviewed against COMPREHENSIVE_ANALYSIS.md
- [ ] Performance targets met (within expected durations)

## Dependencies

**Python Standard Library**:
- `subprocess` - Execute external scripts
- `os` - File and permission checks
- `logging` - Comprehensive logging
- `time` - Timing and timestamps
- `pathlib` - Path operations

**Pai Ho's Scripts** (ver03):
- `sim_pvt.sh` - Main orchestration script (589 lines)

**External Dependencies**: None (pure Python stdlib)

## Success Criteria

This deliverable is complete when:

1. ✅ All 6 stages can be executed via subprocess
2. ✅ Bit-identical output to manual execution (verified)
3. ✅ All 30+ unit tests pass
4. ✅ Integration test demonstrates end-to-end functionality
5. ✅ Comprehensive error handling and recovery
6. ✅ Zero modifications to Pai Ho's files
7. ✅ Logging enables debugging
8. ✅ Code review confirms alignment with COMPREHENSIVE_ANALYSIS.md

## References

- **ULTIMATE_MASTER_PLAN.md**: Module 2: paiho_executor.py (~500 lines)
- **COMPREHENSIVE_ANALYSIS.md**: Complete End-to-End Workflow (6 stages), sim_pvt.sh orchestration
- **Ground Truth**: Pai Ho's sim_pvt.sh, pvt_loop.sh

## Next Deliverable

After completing paiho_executor.py:
- **Deliverable 3**: database.py - Job tracking and result storage

---

**Status**: Not Started  
**Created**: 2025-10-30  
**Dependencies**: Deliverable 1 (config_generator.py)  
**Validated Against**: COMPREHENSIVE_ANALYSIS.md (Pai Ho's wkpup2 ground truth)
