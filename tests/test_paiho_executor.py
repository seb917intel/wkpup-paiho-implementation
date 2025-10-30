#!/usr/bin/env python3
"""
Unit Tests for PaiHoExecutor

Tests subprocess execution, error handling, and workflow orchestration.
Target: 30+ test cases for comprehensive coverage.
"""

import unittest
import os
import tempfile
import shutil
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from paiho_executor import (
    PaiHoExecutor, ExecutionError, ScriptNotFoundError, 
    StageFailedError, TimeoutError
)


class TestExecutorInitialization(unittest.TestCase):
    """Test cases for initialization"""
    
    def setUp(self):
        """Create temporary domain directory with mock script"""
        self.test_dir = tempfile.mkdtemp()
        self.domain_path = os.path.join(self.test_dir, 'gpio/1p1v')
        os.makedirs(self.domain_path)
        
        # Copy mock sim_pvt.sh
        mock_script_src = os.path.join(
            os.path.dirname(__file__), 'mock_scripts', 'sim_pvt.sh'
        )
        mock_script_dst = os.path.join(self.domain_path, 'sim_pvt.sh')
        shutil.copy(mock_script_src, mock_script_dst)
        os.chmod(mock_script_dst, 0o755)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_01_valid_initialization(self):
        """Test successful initialization"""
        executor = PaiHoExecutor(self.domain_path)
        self.assertIsNotNone(executor)
        self.assertEqual(str(executor.domain_path), self.domain_path)
    
    def test_02_invalid_script_version(self):
        """Test error with invalid script version"""
        with self.assertRaises(ValueError):
            PaiHoExecutor(self.domain_path, script_version='ver02')
    
    def test_03_missing_script_raises_error(self):
        """Test error when sim_pvt.sh doesn't exist"""
        os.remove(os.path.join(self.domain_path, 'sim_pvt.sh'))
        
        with self.assertRaises(FileNotFoundError):
            PaiHoExecutor(self.domain_path)
    
    def test_04_non_executable_script_raises_error(self):
        """Test error when sim_pvt.sh is not executable"""
        script_path = os.path.join(self.domain_path, 'sim_pvt.sh')
        os.chmod(script_path, 0o644)  # Remove execute permission
        
        with self.assertRaises(PermissionError):
            PaiHoExecutor(self.domain_path)


class TestSingleStageExecution(unittest.TestCase):
    """Test cases for single stage execution"""
    
    def setUp(self):
        """Create executor with mock script"""
        self.test_dir = tempfile.mkdtemp()
        self.domain_path = os.path.join(self.test_dir, 'gpio/1p1v')
        os.makedirs(self.domain_path)
        
        # Copy mock script
        mock_script_src = os.path.join(
            os.path.dirname(__file__), 'mock_scripts', 'sim_pvt.sh'
        )
        mock_script_dst = os.path.join(self.domain_path, 'sim_pvt.sh')
        shutil.copy(mock_script_src, mock_script_dst)
        os.chmod(mock_script_dst, 0o755)
        
        # Create mock config file
        self.config_file = os.path.join(self.domain_path, 'config.cfg')
        with open(self.config_file, 'w') as f:
            f.write("mode=prelay\n")
        
        self.executor = PaiHoExecutor(self.domain_path)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_05_gen_stage_executes(self):
        """Test gen stage executes successfully"""
        result = self.executor.run_stage('config.cfg', 'gen')
        
        self.assertEqual(result['stage'], 'gen')
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['success'])
        self.assertIn('Generating testbenches', result['stdout'])
    
    def test_06_run_stage_executes(self):
        """Test run stage executes successfully"""
        result = self.executor.run_stage('config.cfg', 'run')
        
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['success'])
    
    def test_07_ext_stage_executes(self):
        """Test ext stage executes successfully"""
        result = self.executor.run_stage('config.cfg', 'ext')
        
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['success'])
    
    def test_08_srt_stage_executes(self):
        """Test srt stage executes successfully"""
        result = self.executor.run_stage('config.cfg', 'srt')
        
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['success'])
    
    def test_09_bkp_stage_executes(self):
        """Test bkp stage executes successfully"""
        result = self.executor.run_stage('config.cfg', 'bkp')
        
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['success'])
    
    def test_10_invalid_stage_raises_error(self):
        """Test invalid stage name raises error"""
        with self.assertRaises(ValueError):
            self.executor.run_stage('config.cfg', 'invalid_stage')
    
    def test_11_result_contains_timing(self):
        """Test result contains timing information"""
        result = self.executor.run_stage('config.cfg', 'gen')
        
        self.assertIn('elapsed_time', result)
        self.assertIn('start_time', result)
        self.assertIn('end_time', result)
        self.assertGreater(result['elapsed_time'], 0)
    
    def test_12_result_contains_stdout_stderr(self):
        """Test result contains stdout and stderr"""
        result = self.executor.run_stage('config.cfg', 'gen')
        
        self.assertIn('stdout', result)
        self.assertIn('stderr', result)
        self.assertIsInstance(result['stdout'], str)
        self.assertIsInstance(result['stderr'], str)


class TestMultiStageExecution(unittest.TestCase):
    """Test cases for multi-stage workflow"""
    
    def setUp(self):
        """Create executor"""
        self.test_dir = tempfile.mkdtemp()
        self.domain_path = os.path.join(self.test_dir, 'gpio/1p1v')
        os.makedirs(self.domain_path)
        
        # Copy mock script
        mock_script_src = os.path.join(
            os.path.dirname(__file__), 'mock_scripts', 'sim_pvt.sh'
        )
        mock_script_dst = os.path.join(self.domain_path, 'sim_pvt.sh')
        shutil.copy(mock_script_src, mock_script_dst)
        os.chmod(mock_script_dst, 0o755)
        
        # Create config
        with open(os.path.join(self.domain_path, 'config.cfg'), 'w') as f:
            f.write("mode=prelay\n")
        
        self.executor = PaiHoExecutor(self.domain_path)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_13_full_workflow_executes(self):
        """Test full workflow execution"""
        results = self.executor.run_simulation('config.cfg')
        
        self.assertIn('overall_success', results)
        self.assertTrue(results['overall_success'])
        self.assertIsNone(results['failed_stage'])
    
    def test_14_partial_workflow_gen_only(self):
        """Test partial workflow (gen only)"""
        results = self.executor.run_simulation('config.cfg', stages=['gen'])
        
        self.assertIn('gen', results)
        self.assertNotIn('run', results)
        self.assertTrue(results['overall_success'])
    
    def test_15_partial_workflow_multiple_stages(self):
        """Test partial workflow (gen + run + ext)"""
        results = self.executor.run_simulation('config.cfg', stages=['gen', 'run', 'ext'])
        
        self.assertIn('gen', results)
        self.assertIn('run', results)
        self.assertIn('ext', results)
        self.assertNotIn('srt', results)
    
    def test_16_results_accumulate(self):
        """Test results accumulate correctly"""
        results = self.executor.run_simulation('config.cfg', stages=['gen', 'run'])
        
        # Should have both stage results plus overall results
        self.assertIn('gen', results)
        self.assertIn('run', results)
        self.assertIn('overall_success', results)
        self.assertIn('total_elapsed', results)
    
    def test_17_total_elapsed_calculated(self):
        """Test total elapsed time is calculated"""
        results = self.executor.run_simulation('config.cfg', stages=['gen', 'run'])
        
        self.assertIn('total_elapsed', results)
        self.assertGreater(results['total_elapsed'], 0)


class TestOutputVerification(unittest.TestCase):
    """Test cases for output verification"""
    
    def setUp(self):
        """Create executor and run gen stage"""
        self.test_dir = tempfile.mkdtemp()
        self.domain_path = os.path.join(self.test_dir, 'gpio/1p1v')
        os.makedirs(self.domain_path)
        
        # Copy mock script
        mock_script_src = os.path.join(
            os.path.dirname(__file__), 'mock_scripts', 'sim_pvt.sh'
        )
        mock_script_dst = os.path.join(self.domain_path, 'sim_pvt.sh')
        shutil.copy(mock_script_src, mock_script_dst)
        os.chmod(mock_script_dst, 0o755)
        
        # Create config
        with open(os.path.join(self.domain_path, 'config.cfg'), 'w') as f:
            f.write("mode=prelay\n")
        
        self.executor = PaiHoExecutor(self.domain_path)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_18_verify_output_files_exist(self):
        """Test verification passes when files exist"""
        # Run gen stage to create files
        self.executor.run_stage('config.cfg', 'gen')
        
        # Verify
        result = self.executor.verify_output([
            'TT/typical/typical_85/v1nom/sim_tx.sp'
        ])
        
        self.assertTrue(result)
    
    def test_19_verify_output_files_missing(self):
        """Test verification fails when files missing"""
        result = self.executor.verify_output([
            'nonexistent/file.txt'
        ])
        
        self.assertFalse(result)
    
    def test_20_verify_multiple_files(self):
        """Test verification with multiple files"""
        self.executor.run_stage('config.cfg', 'gen')
        
        # Create additional file
        os.makedirs(os.path.join(self.domain_path, 'TT/typical/typical_85/v1min'), exist_ok=True)
        with open(os.path.join(self.domain_path, 'TT/typical/typical_85/v1min/sim_tx.sp'), 'w') as f:
            f.write("netlist")
        
        result = self.executor.verify_output([
            'TT/typical/typical_85/v1nom/sim_tx.sp',
            'TT/typical/typical_85/v1min/sim_tx.sp'
        ])
        
        self.assertTrue(result)


class TestProgressMonitoring(unittest.TestCase):
    """Test cases for progress monitoring"""
    
    def setUp(self):
        """Create executor"""
        self.test_dir = tempfile.mkdtemp()
        self.domain_path = os.path.join(self.test_dir, 'gpio/1p1v')
        os.makedirs(self.domain_path)
        
        # Copy mock script
        mock_script_src = os.path.join(
            os.path.dirname(__file__), 'mock_scripts', 'sim_pvt.sh'
        )
        mock_script_dst = os.path.join(self.domain_path, 'sim_pvt.sh')
        shutil.copy(mock_script_src, mock_script_dst)
        os.chmod(mock_script_dst, 0o755)
        
        self.executor = PaiHoExecutor(self.domain_path)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_21_monitor_progress_returns_dict(self):
        """Test monitor_progress returns dict"""
        progress = self.executor.monitor_progress('gen')
        
        self.assertIsInstance(progress, dict)
        self.assertIn('stage', progress)
    
    def test_22_check_simulation_progress(self):
        """Test check_simulation_progress counts mt0 files"""
        # Create config and run simulation
        with open(os.path.join(self.domain_path, 'config.cfg'), 'w') as f:
            f.write("mode=prelay\n")
        
        self.executor.run_stage('config.cfg', 'run')
        
        progress = self.executor.check_simulation_progress()
        
        self.assertIn('completed_simulations', progress)
        self.assertGreaterEqual(progress['completed_simulations'], 0)


class TestRetryLogic(unittest.TestCase):
    """Test cases for retry functionality"""
    
    def setUp(self):
        """Create executor"""
        self.test_dir = tempfile.mkdtemp()
        self.domain_path = os.path.join(self.test_dir, 'gpio/1p1v')
        os.makedirs(self.domain_path)
        
        # Copy mock script
        mock_script_src = os.path.join(
            os.path.dirname(__file__), 'mock_scripts', 'sim_pvt.sh'
        )
        mock_script_dst = os.path.join(self.domain_path, 'sim_pvt.sh')
        shutil.copy(mock_script_src, mock_script_dst)
        os.chmod(mock_script_dst, 0o755)
        
        # Create config
        with open(os.path.join(self.domain_path, 'config.cfg'), 'w') as f:
            f.write("mode=prelay\n")
        
        self.executor = PaiHoExecutor(self.domain_path)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_23_retry_successful_stage(self):
        """Test retry on successful stage returns immediately"""
        result = self.executor.retry_stage('config.cfg', 'gen', max_retries=3)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['retry_attempt'], 1)  # Should succeed on first try
    
    def test_24_retry_includes_attempt_count(self):
        """Test retry result includes attempt count"""
        result = self.executor.retry_stage('config.cfg', 'gen', max_retries=2)
        
        self.assertIn('retry_attempt', result)


class TestStageConstants(unittest.TestCase):
    """Test cases for stage constants and configurations"""
    
    def test_25_has_all_six_stages(self):
        """Test STAGES constant has all 6 stages"""
        self.assertEqual(len(PaiHoExecutor.STAGES), 6)
        self.assertIn('gen', PaiHoExecutor.STAGES)
        self.assertIn('run', PaiHoExecutor.STAGES)
        self.assertIn('ext', PaiHoExecutor.STAGES)
        self.assertIn('srt', PaiHoExecutor.STAGES)
        self.assertIn('bkp', PaiHoExecutor.STAGES)
        self.assertIn('usr', PaiHoExecutor.STAGES)
    
    def test_26_has_timeouts_for_all_stages(self):
        """Test STAGE_TIMEOUTS defined for all stages"""
        for stage in PaiHoExecutor.STAGES:
            self.assertIn(stage, PaiHoExecutor.STAGE_TIMEOUTS)
            self.assertGreater(PaiHoExecutor.STAGE_TIMEOUTS[stage], 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
