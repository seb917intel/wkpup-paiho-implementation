#!/usr/bin/env python3
"""
Pai Ho Executor

Executes Pai Ho's validated scripts via subprocess.
NEVER modifies Pai Ho's files - only calls them.

This module is part of the WKPUP reconciliation project, implementing the wrapper
pattern around Pai Ho's untouched, validated wkpup2 core system.

Reference: ULTIMATE_MASTER_PLAN.md - Module 2: paiho_executor.py (~500 lines)
Ground Truth: COMPREHENSIVE_ANALYSIS.md - Pai Ho's 6-stage workflow
"""

import subprocess
import os
import logging
import time
from typing import Optional, List, Dict
from pathlib import Path


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


class PaiHoExecutor:
    """
    Executes Pai Ho's validated scripts.
    All execution via subprocess.run() - NO file modifications.
    
    This class implements the wrapper pattern - it orchestrates Pai Ho's scripts
    but NEVER modifies them.
    """
    
    # Valid stages from Pai Ho's workflow
    STAGES = ['gen', 'run', 'ext', 'srt', 'bkp', 'usr']
    
    # Timeout per stage (in seconds)
    STAGE_TIMEOUTS = {
        'gen': 600,     # 10 minutes
        'run': 21600,   # 6 hours
        'ext': 300,     # 5 minutes
        'srt': 120,     # 2 minutes
        'bkp': 300,     # 5 minutes
        'usr': 3600     # 1 hour
    }
    
    def __init__(self, domain_path: str, script_version: str = 'ver03'):
        """
        Initialize executor.
        
        Args:
            domain_path: Path to voltage domain (e.g., gpio/1p1v)
            script_version: Version to use (must be 'ver03')
            
        Raises:
            ValueError: If script_version is not 'ver03'
            FileNotFoundError: If sim_pvt.sh doesn't exist
            PermissionError: If sim_pvt.sh is not executable
        """
        if script_version != 'ver03':
            raise ValueError("Only ver03 is supported")
        
        self.domain_path = Path(domain_path)
        self.sim_pvt_script = self.domain_path / 'sim_pvt.sh'
        
        # Verify script exists
        if not self.sim_pvt_script.exists():
            raise FileNotFoundError(
                f"sim_pvt.sh not found at {self.sim_pvt_script}"
            )
        
        # Verify script is executable
        if not os.access(self.sim_pvt_script, os.X_OK):
            raise PermissionError(
                f"sim_pvt.sh is not executable: {self.sim_pvt_script}"
            )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def run_simulation(self, config_file: str, 
                      stages: Optional[List[str]] = None) -> Dict:
        """
        Run full simulation workflow.
        
        Args:
            config_file: Path to config.cfg
            stages: List of stages to run (default: all except usr)
            
        Returns:
            Dict with execution results per stage and overall status
        """
        if stages is None:
            # Default: run all stages except optional usr_script
            stages = ['gen', 'run', 'ext', 'srt', 'bkp']
        
        results = {}
        overall_start = time.time()
        
        for stage in stages:
            self.logger.info(f"Running stage: {stage}")
            result = self.run_stage(config_file, stage)
            results[stage] = result
            
            if result['returncode'] != 0:
                self.logger.error(f"Stage {stage} failed with exit code {result['returncode']}")
                # Stop on first failure
                break
        
        overall_elapsed = time.time() - overall_start
        
        # Determine overall success
        all_success = all(r.get('success', False) for r in results.values())
        failed_stage = None
        if not all_success:
            failed_stage = next(
                (stage for stage, r in results.items() if not r.get('success', False)),
                None
            )
        
        return {
            **results,
            'overall_success': all_success,
            'failed_stage': failed_stage,
            'total_elapsed': overall_elapsed
        }
    
    def run_stage(self, config_file: str, stage: str) -> Dict:
        """
        Run a single simulation stage.
        
        Args:
            config_file: Path to config.cfg
            stage: Stage name (gen/run/ext/srt/bkp/usr)
            
        Returns:
            Dict with stdout, stderr, returncode, timing info
            
        Raises:
            ValueError: If stage is invalid
        """
        if stage not in self.STAGES:
            raise ValueError(
                f"Invalid stage: {stage}. Must be one of {self.STAGES}"
            )
        
        cmd = [
            'bash',
            str(self.sim_pvt_script),
            config_file,
            stage
        ]
        
        self.logger.info(f"Starting stage: {stage}")
        self.logger.debug(f"Working directory: {self.domain_path}")
        self.logger.debug(f"Config file: {config_file}")
        self.logger.debug(f"Command: {' '.join(cmd)}")
        
        start_time = time.time()
        start_timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')
        
        try:
            # Get timeout for this stage
            timeout = self.STAGE_TIMEOUTS.get(stage, 3600)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise on non-zero exit
                timeout=timeout,
                cwd=str(self.domain_path)
            )
            
            elapsed = time.time() - start_time
            end_timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')
            
            self.logger.info(
                f"Stage {stage} completed in {elapsed:.2f}s with exit code {result.returncode}"
            )
            
            if result.returncode != 0:
                self.logger.error(f"stderr: {result.stderr[:500]}")  # Log first 500 chars
            
            return {
                'stage': stage,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0,
                'elapsed_time': elapsed,
                'start_time': start_timestamp,
                'end_time': end_timestamp
            }
        
        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Stage {stage} timed out after {elapsed:.2f}s")
            
            return {
                'stage': stage,
                'returncode': -1,
                'stdout': e.stdout.decode() if e.stdout else '',
                'stderr': e.stderr.decode() if e.stderr else '',
                'success': False,
                'elapsed_time': elapsed,
                'start_time': start_timestamp,
                'end_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'error': 'Timeout'
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.exception(f"Exception during stage {stage}")
            
            return {
                'stage': stage,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'elapsed_time': elapsed,
                'start_time': start_timestamp,
                'end_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'error': 'Exception'
            }
    
    def verify_output(self, expected_files: List[str]) -> bool:
        """
        Verify expected output files exist.
        
        Args:
            expected_files: List of file paths to check (relative to domain_path)
            
        Returns:
            True if all files exist, False otherwise
        """
        for filepath in expected_files:
            full_path = self.domain_path / filepath
            if not full_path.exists():
                self.logger.error(f"Expected file not found: {full_path}")
                return False
        
        return True
    
    def retry_stage(self, config_file: str, stage: str, 
                   max_retries: int = 3, backoff: float = 2.0) -> Dict:
        """
        Retry a failed stage with exponential backoff.
        
        Args:
            config_file: Path to config.cfg
            stage: Stage name to retry
            max_retries: Maximum retry attempts
            backoff: Backoff multiplier (seconds between retries double each time)
            
        Returns:
            Result dict from successful attempt or final failure
        """
        wait_time = 1.0
        
        for attempt in range(max_retries):
            self.logger.info(f"Retry attempt {attempt + 1}/{max_retries} for stage {stage}")
            
            result = self.run_stage(config_file, stage)
            
            if result['success']:
                self.logger.info(f"Stage {stage} succeeded on retry {attempt + 1}")
                result['retry_attempt'] = attempt + 1
                return result
            
            if attempt < max_retries - 1:
                self.logger.warning(f"Retry {attempt + 1} failed, waiting {wait_time}s before next attempt")
                time.sleep(wait_time)
                wait_time *= backoff
        
        self.logger.error(f"Stage {stage} failed after {max_retries} retries")
        result['retry_attempt'] = max_retries
        result['retry_exhausted'] = True
        return result
    
    def monitor_progress(self, stage: str) -> Dict:
        """
        Monitor current stage execution progress.
        
        This is a placeholder for monitoring logic. In a real implementation,
        this could check log files, count generated files, etc.
        
        Args:
            stage: Current stage being monitored
            
        Returns:
            Dict with progress information
        """
        # Placeholder implementation
        return {
            'stage': stage,
            'status': 'running',
            'message': f'Monitoring {stage} stage'
        }
    
    def check_simulation_progress(self) -> Dict:
        """
        Count completed simulations by checking for .mt0 files.
        
        Returns:
            Dict with completion count and percentage
        """
        # Count .mt0 files (simulation results)
        mt0_files = list(self.domain_path.glob('**/*.mt0'))
        completed_count = len(mt0_files)
        
        # Note: total count would need to be calculated from config
        # For now, just return completed count
        return {
            'completed_simulations': completed_count,
            'mt0_files': [str(f.relative_to(self.domain_path)) for f in mt0_files]
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Run simulation
    executor = PaiHoExecutor(
        domain_path="/path/to/gpio/1p1v",
        script_version="ver03"
    )
    
    # Run all stages
    results = executor.run_simulation(
        config_file="config.cfg",
        stages=['gen', 'run', 'ext']
    )
    
    # Print results
    for stage, result in results.items():
        if stage in ['overall_success', 'failed_stage', 'total_elapsed']:
            print(f"{stage}: {result}")
        else:
            print(f"{stage}: {'✅' if result['success'] else '❌'} ({result['elapsed_time']:.2f}s)")
