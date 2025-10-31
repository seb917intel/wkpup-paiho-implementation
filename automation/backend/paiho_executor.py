#!/usr/bin/env python3
"""
PaiHo Executor - Wrapper for Pai Ho's validated simulation scripts
Calls Pai Ho's original ver03 scripts WITHOUT modification
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

class PaiHoExecutor:
    """
    Executes Pai Ho's validated ver03 scripts
    All execution via subprocess - NO file modifications allowed
    """
    
    STAGES = ['gen', 'run', 'ext', 'srt', 'bkp']
    
    def __init__(self, project_root: str, project: str, voltage_domain: str):
        """
        Initialize executor
        
        Args:
            project_root: Repository root path
            project: 'gpio' or 'i3c'
            voltage_domain: e.g., '1p1v', '1p2v', '1p8v'
        """
        self.project_root = Path(project_root)
        self.project = project
        self.voltage_domain = voltage_domain
        
        # Path to voltage domain directory
        self.domain_path = self.project_root / project / voltage_domain
        
        # Path to ver03 scripts in dependencies
        self.script_path = (self.domain_path / 
                           "dependencies/scripts/simulation_script/auto_pvt/ver03")
        
        # Path to sim_pvt.sh (Pai Ho's main script)
        self.sim_pvt_script = self.script_path / "sim_pvt.sh"
        
        # Validate paths exist
        if not self.domain_path.exists():
            raise FileNotFoundError(f"Domain path not found: {self.domain_path}")
        
        if not self.script_path.exists():
            raise FileNotFoundError(f"Ver03 scripts not found: {self.script_path}")
            
        if not self.sim_pvt_script.exists():
            raise FileNotFoundError(f"sim_pvt.sh not found: {self.sim_pvt_script}")
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"PaiHoExecutor initialized for {project}/{voltage_domain}")
        self.logger.info(f"Using ver03 scripts at: {self.script_path}")
    
    def run_stage(self, work_dir: str, config_file: str, stage: str, 
                  timeout: int = 600) -> Dict:
        """
        Run a single simulation stage using Pai Ho's sim_pvt.sh
        
        Args:
            work_dir: Working directory containing config.cfg and template/
            config_file: Config filename (usually 'config.cfg')
            stage: Stage name ('gen', 'run', 'ext', 'srt', 'bkp')
            timeout: Command timeout in seconds
            
        Returns:
            Dict with execution results
        """
        if stage not in self.STAGES:
            raise ValueError(f"Invalid stage: {stage}. Valid: {self.STAGES}")
        
        # Command: bash sim_pvt.sh config.cfg {stage}
        cmd = [
            'bash',
            str(self.sim_pvt_script),
            config_file,
            stage
        ]
        
        self.logger.info(f"Executing stage '{stage}' in {work_dir}")
        self.logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Don't raise on non-zero exit
            )
            
            success = result.returncode == 0
            
            if success:
                self.logger.info(f"Stage '{stage}' completed successfully")
            else:
                self.logger.error(f"Stage '{stage}' failed with code {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr[:500]}")  # First 500 chars
            
            return {
                'stage': stage,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': success
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Stage '{stage}' timed out after {timeout}s")
            return {
                'stage': stage,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Timeout after {timeout}s',
                'success': False
            }
        except Exception as e:
            self.logger.exception(f"Exception during stage '{stage}'")
            return {
                'stage': stage,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def run_generation(self, work_dir: str, config_file: str = 'config.cfg') -> Dict:
        """Run generation stage (gen_tb.pl creates testbenches)"""
        return self.run_stage(work_dir, config_file, 'gen', timeout=600)
    
    def run_submission(self, work_dir: str, config_file: str = 'config.cfg') -> Dict:
        """Run submission stage (submit jobs to NetBatch)"""
        return self.run_stage(work_dir, config_file, 'run', timeout=1200)
    
    def run_extraction(self, work_dir: str, config_file: str = 'config.cfg') -> Dict:
        """Run extraction stage (parse .mt0 files)"""
        return self.run_stage(work_dir, config_file, 'ext', timeout=600)
    
    def run_sorting(self, work_dir: str, config_file: str = 'config.cfg') -> Dict:
        """Run sorting stage (consolidate reports)"""
        return self.run_stage(work_dir, config_file, 'srt', timeout=300)
    
    def run_backup(self, work_dir: str, config_file: str = 'config.cfg') -> Dict:
        """Run backup stage (create timestamped backup)"""
        return self.run_stage(work_dir, config_file, 'bkp', timeout=300)
    
    def run_full_workflow(self, work_dir: str, config_file: str = 'config.cfg',
                         stages: Optional[List[str]] = None) -> Dict:
        """
        Run complete simulation workflow
        
        Args:
            work_dir: Working directory
            config_file: Config filename
            stages: List of stages to run (default: all)
            
        Returns:
            Dict with results for each stage
        """
        if stages is None:
            stages = self.STAGES
        
        results = {}
        
        for stage in stages:
            self.logger.info(f"=== Running stage: {stage} ===")
            result = self.run_stage(work_dir, config_file, stage)
            results[stage] = result
            
            # Stop on first failure
            if not result['success']:
                self.logger.error(f"Workflow stopped at stage '{stage}' due to failure")
                break
        
        return results


if __name__ == "__main__":
    # Test the executor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python paiho_executor.py <work_dir>")
        sys.exit(1)
    
    work_dir = sys.argv[1]
    
    # Get repository root (3 levels up from automation/backend/)
    repo_root = Path(__file__).parent.parent.parent
    
    # Example: Execute for gpio/1p1v
    executor = PaiHoExecutor(
        project_root=str(repo_root),
        project='gpio',
        voltage_domain='1p1v'
    )
    
    print(f"\n=== Testing PaiHoExecutor ===")
    print(f"Work directory: {work_dir}")
    print(f"Repository root: {repo_root}")
    print(f"Ver03 scripts: {executor.script_path}")
    print()
    
    # Run generation stage as test
    result = executor.run_generation(work_dir)
    
    print(f"\nGeneration stage: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Return code: {result['returncode']}")
    if not result['success']:
        print(f"Error: {result['stderr'][:200]}")
