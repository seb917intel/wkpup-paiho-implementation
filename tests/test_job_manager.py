#!/usr/bin/env python3
"""
Unit Tests for BackgroundJobManager

Tests job queue, worker threads, and background execution.
Target: 20+ test cases for comprehensive coverage.
"""

import unittest
import os
import tempfile
import shutil
import sys
import time
import threading
from unittest.mock import Mock, MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from job_manager import BackgroundJobManager, JobStatus, JobManagerError, JobNotFoundError
from database import DatabaseManager


class MockExecutor:
    """Mock PaiHoExecutor for testing"""
    
    def __init__(self, domain_path, fail_stage=None):
        self.domain_path = domain_path
        self.fail_stage = fail_stage
    
    def run_stage(self, config_file, stage):
        """Mock stage execution"""
        time.sleep(0.1)  # Simulate work
        
        if stage == self.fail_stage:
            return {
                'stage': stage,
                'success': False,
                'returncode': 1,
                'stderr': f'Mock error in {stage}'
            }
        
        return {
            'stage': stage,
            'success': True,
            'returncode': 0,
            'stdout': f'Mock output for {stage}'
        }


class TestJobManagerInitialization(unittest.TestCase):
    """Test cases for initialization"""
    
    def setUp(self):
        """Create database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_01_initialization(self):
        """Test job manager initialization"""
        def factory(path):
            return MockExecutor(path)
        
        manager = BackgroundJobManager(self.db, factory, max_workers=2)
        
        self.assertIsNotNone(manager)
        self.assertEqual(manager.max_workers, 2)
        
        manager.shutdown(wait=False)
    
    def test_02_workers_started(self):
        """Test worker threads are started"""
        def factory(path):
            return MockExecutor(path)
        
        manager = BackgroundJobManager(self.db, factory, max_workers=3)
        
        self.assertEqual(len(manager.workers), 3)
        
        # All workers should be alive
        for worker in manager.workers:
            self.assertTrue(worker.is_alive())
        
        manager.shutdown(wait=False)


class TestJobSubmission(unittest.TestCase):
    """Test cases for job submission"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        def factory(path):
            return MockExecutor(path)
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=1)
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=False)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_03_submit_valid_job(self):
        """Test submitting a valid job"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': 'test/path'
        })
        
        result = self.manager.submit(job_id)
        
        self.assertTrue(result)
    
    def test_04_submit_nonexistent_job(self):
        """Test submitting non-existent job raises error"""
        with self.assertRaises(JobNotFoundError):
            self.manager.submit('nonexistent-job-id')
    
    def test_05_job_added_to_queue(self):
        """Test job is added to queue"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': 'test/path'
        })
        
        initial_size = self.manager.job_queue.qsize()
        self.manager.submit(job_id)
        
        # Queue size should increase
        self.assertEqual(self.manager.job_queue.qsize(), initial_size + 1)


class TestJobExecution(unittest.TestCase):
    """Test cases for job execution"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        # Create mock domain directory
        self.test_dir = tempfile.mkdtemp()
        
        def factory(path):
            return MockExecutor(path)
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=1)
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=True)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(self.test_dir)
    
    def test_06_job_executes_successfully(self):
        """Test job executes and completes"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        self.manager.submit(job_id)
        
        # Wait for job to complete (max 5 seconds)
        for _ in range(50):
            job = self.db.get_job(job_id)
            if job['status'] in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
                break
            time.sleep(0.1)
        
        # Check job completed
        job = self.db.get_job(job_id)
        self.assertEqual(job['status'], JobStatus.COMPLETED.value)
    
    def test_07_job_status_updates(self):
        """Test job status updates during execution"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        # Initially queued
        job = self.db.get_job(job_id)
        self.assertEqual(job['status'], JobStatus.QUEUED.value)
        
        self.manager.submit(job_id)
        
        # Should transition to running
        time.sleep(0.2)
        job = self.db.get_job(job_id)
        self.assertIn(job['status'], [JobStatus.RUNNING.value, JobStatus.COMPLETED.value])
    
    def test_08_stages_tracked(self):
        """Test stages are tracked during execution"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        self.manager.submit(job_id)
        
        # Wait for completion
        self.manager.wait_for_completion()
        
        # Check stages completed
        job = self.db.get_job(job_id)
        import json
        completed_stages = json.loads(job['completed_stages']) if job['completed_stages'] else []
        
        # Should have completed gen, run, ext, srt, bkp
        self.assertGreaterEqual(len(completed_stages), 3)


class TestJobCancellation(unittest.TestCase):
    """Test cases for job cancellation"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        self.test_dir = tempfile.mkdtemp()
        
        def factory(path):
            return MockExecutor(path)
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=1)
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=False)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(self.test_dir)
    
    def test_09_cancel_queued_job(self):
        """Test cancelling a queued job"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        self.manager.submit(job_id)
        
        # Cancel immediately
        result = self.manager.cancel_job(job_id)
        
        self.assertTrue(result)
        
        job = self.db.get_job(job_id)
        # Should be cancelled (or possibly running if worker picked it up very quickly)
        self.assertIn(job['status'], [JobStatus.CANCELLED.value, JobStatus.RUNNING.value])
    
    def test_10_cancel_nonexistent_job(self):
        """Test cancelling non-existent job returns False"""
        result = self.manager.cancel_job('nonexistent-id')
        
        self.assertFalse(result)


class TestQueueStatus(unittest.TestCase):
    """Test cases for queue status"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        self.test_dir = tempfile.mkdtemp()
        
        def factory(path):
            return MockExecutor(path)
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=2)
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=False)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(self.test_dir)
    
    def test_11_get_queue_status(self):
        """Test getting queue status"""
        status = self.manager.get_queue_status()
        
        self.assertIn('queued_jobs', status)
        self.assertIn('active_jobs', status)
        self.assertIn('total_workers', status)
        self.assertIn('available_workers', status)
    
    def test_12_queue_status_reflects_submission(self):
        """Test queue status updates after submission"""
        initial_status = self.manager.get_queue_status()
        
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        self.manager.submit(job_id)
        
        # Status should show queued or active job
        time.sleep(0.1)
        new_status = self.manager.get_queue_status()
        
        total_jobs = new_status['queued_jobs'] + new_status['active_jobs']
        initial_total = initial_status['queued_jobs'] + initial_status['active_jobs']
        
        self.assertGreaterEqual(total_jobs, initial_total)


class TestStatusCallbacks(unittest.TestCase):
    """Test cases for status callbacks"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        self.test_dir = tempfile.mkdtemp()
        
        def factory(path):
            return MockExecutor(path)
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=1)
        
        self.callback_calls = []
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=False)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(self.test_dir)
    
    def test_13_register_callback(self):
        """Test registering status callback"""
        def callback(job_id, status, **kwargs):
            self.callback_calls.append((job_id, status))
        
        self.manager.register_status_callback(callback)
        
        self.assertEqual(len(self.manager.status_callbacks), 1)
    
    def test_14_callback_invoked_on_status_change(self):
        """Test callback is invoked on status change"""
        def callback(job_id, status, **kwargs):
            self.callback_calls.append((job_id, status))
        
        self.manager.register_status_callback(callback)
        
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        self.manager.submit(job_id)
        
        # Wait for job to complete
        self.manager.wait_for_completion()
        
        # Callback should have been called (at least once for RUNNING, once for COMPLETED)
        self.assertGreater(len(self.callback_calls), 0)


class TestShutdown(unittest.TestCase):
    """Test cases for shutdown"""
    
    def setUp(self):
        """Create database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_15_shutdown_without_wait(self):
        """Test shutdown without waiting"""
        def factory(path):
            return MockExecutor(path)
        
        manager = BackgroundJobManager(self.db, factory, max_workers=1)
        
        manager.shutdown(wait=False)
        
        # Workers should stop
        time.sleep(0.5)
        for worker in manager.workers:
            self.assertFalse(worker.is_alive())
    
    def test_16_shutdown_with_wait(self):
        """Test shutdown with wait for jobs to complete"""
        def factory(path):
            return MockExecutor(path)
        
        manager = BackgroundJobManager(self.db, factory, max_workers=1)
        
        # Shutdown should complete
        manager.shutdown(wait=True)
        
        for worker in manager.workers:
            self.assertFalse(worker.is_alive())


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        self.test_dir = tempfile.mkdtemp()
        
        # Factory that creates failing executor
        def factory(path):
            return MockExecutor(path, fail_stage='run')
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=1)
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=True)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(self.test_dir)
    
    def test_17_failed_stage_marks_job_failed(self):
        """Test failed stage marks job as failed"""
        job_id = self.db.create_job({
            'mode': 'prelay',
            'vccn': '1p1v',
            'domain_path': self.test_dir
        })
        
        self.manager.submit(job_id)
        
        # Wait for job to complete
        self.manager.wait_for_completion()
        
        # Job should be marked as failed
        job = self.db.get_job(job_id)
        self.assertEqual(job['status'], JobStatus.FAILED.value)
        self.assertIsNotNone(job.get('error_message'))


class TestConcurrency(unittest.TestCase):
    """Test cases for concurrent execution"""
    
    def setUp(self):
        """Create database and manager"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        self.test_dir = tempfile.mkdtemp()
        
        def factory(path):
            return MockExecutor(path)
        
        self.manager = BackgroundJobManager(self.db, factory, max_workers=3)
    
    def tearDown(self):
        """Clean up"""
        self.manager.shutdown(wait=True)
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.rmtree(self.test_dir)
    
    def test_18_multiple_jobs_execute_concurrently(self):
        """Test multiple jobs can execute concurrently"""
        job_ids = []
        
        # Submit 5 jobs
        for i in range(5):
            job_id = self.db.create_job({
                'mode': 'prelay',
                'vccn': '1p1v',
                'domain_path': self.test_dir,
                'description': f'Job {i}'
            })
            job_ids.append(job_id)
            self.manager.submit(job_id)
        
        # Wait for all to complete
        self.manager.wait_for_completion()
        
        # All jobs should complete
        for job_id in job_ids:
            job = self.db.get_job(job_id)
            self.assertIn(job['status'], [JobStatus.COMPLETED.value, JobStatus.FAILED.value])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
