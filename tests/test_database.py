#!/usr/bin/env python3
"""
Unit Tests for DatabaseManager

Tests job CRUD operations, result storage, and database maintenance.
Target: 40+ test cases for comprehensive coverage.
"""

import unittest
import os
import tempfile
import sys
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import DatabaseManager, DatabaseError, IntegrityError


class TestDatabaseInitialization(unittest.TestCase):
    """Test cases for database initialization"""
    
    def setUp(self):
        """Create temporary database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_01_database_creation(self):
        """Test database file is created"""
        db = DatabaseManager(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))
        db.close()
    
    def test_02_tables_created(self):
        """Test tables are created"""
        db = DatabaseManager(self.db_path)
        conn, cursor = db._get_conn()
        
        # Check jobs table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
        )
        self.assertIsNotNone(cursor.fetchone())
        
        # Check results table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='results'"
        )
        self.assertIsNotNone(cursor.fetchone())
        
        db.close()
    
    def test_03_indexes_created(self):
        """Test indexes are created"""
        db = DatabaseManager(self.db_path)
        conn, cursor = db._get_conn()
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('idx_results_job_id', indexes)
        self.assertIn('idx_results_corner', indexes)
        
        db.close()
    
    def test_04_foreign_keys_enabled(self):
        """Test foreign keys are enabled"""
        db = DatabaseManager(self.db_path)
        conn, cursor = db._get_conn()
        
        cursor.execute('PRAGMA foreign_keys')
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)  # Should be enabled (1)
        
        db.close()


class TestJobCRUD(unittest.TestCase):
    """Test cases for job CRUD operations"""
    
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
    
    def test_05_create_job(self):
        """Test job creation"""
        params = {
            'mode': 'prelay',
            'vccn': '1p1v',
            'condition': 'perf'
        }
        
        job_id = self.db.create_job(params)
        
        self.assertIsNotNone(job_id)
        self.assertIsInstance(job_id, str)
    
    def test_06_get_job_by_id(self):
        """Test retrieving job by ID"""
        params = {'mode': 'prelay', 'vccn': '1p1v'}
        job_id = self.db.create_job(params)
        
        job = self.db.get_job(job_id)
        
        self.assertIsNotNone(job)
        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['mode'], 'prelay')
    
    def test_07_get_nonexistent_job(self):
        """Test getting non-existent job returns None"""
        job = self.db.get_job('nonexistent-id')
        self.assertIsNone(job)
    
    def test_08_job_defaults(self):
        """Test job created with default values"""
        params = {'mode': 'prelay', 'vccn': '1p1v'}
        job_id = self.db.create_job(params)
        
        job = self.db.get_job(job_id)
        
        self.assertEqual(job['status'], 'queued')
        self.assertIsNotNone(job['created_at'])
    
    def test_09_update_job_status(self):
        """Test updating job status"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        self.db.update_job_status(job_id, 'running')
        
        job = self.db.get_job(job_id)
        self.assertEqual(job['status'], 'running')
    
    def test_10_update_sets_started_at(self):
        """Test status change to running sets started_at"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        self.db.update_job_status(job_id, 'running')
        
        job = self.db.get_job(job_id)
        self.assertIsNotNone(job['started_at'])
    
    def test_11_update_sets_completed_at(self):
        """Test status change to completed sets completed_at"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        self.db.update_job_status(job_id, 'running')
        self.db.update_job_status(job_id, 'completed')
        
        job = self.db.get_job(job_id)
        self.assertIsNotNone(job['completed_at'])
        self.assertIsNotNone(job['elapsed_seconds'])
    
    def test_12_update_with_additional_fields(self):
        """Test updating with additional fields"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        self.db.update_job_status(job_id, 'running', current_stage='gen')
        
        job = self.db.get_job(job_id)
        self.assertEqual(job['current_stage'], 'gen')


class TestStageTracking(unittest.TestCase):
    """Test cases for stage tracking"""
    
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
    
    def test_13_mark_stage_complete(self):
        """Test marking stage as complete"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        result = self.db.mark_stage_complete(job_id, 'gen')
        
        self.assertTrue(result)
    
    def test_14_multiple_stages_tracked(self):
        """Test tracking multiple completed stages"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        self.db.mark_stage_complete(job_id, 'gen')
        self.db.mark_stage_complete(job_id, 'run')
        self.db.mark_stage_complete(job_id, 'ext')
        
        job = self.db.get_job(job_id)
        completed = json.loads(job['completed_stages'])
        
        self.assertEqual(len(completed), 3)
        self.assertIn('gen', completed)
        self.assertIn('run', completed)
        self.assertIn('ext', completed)
    
    def test_15_duplicate_stage_not_added(self):
        """Test duplicate stage is not added twice"""
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        self.db.mark_stage_complete(job_id, 'gen')
        self.db.mark_stage_complete(job_id, 'gen')  # Duplicate
        
        job = self.db.get_job(job_id)
        completed = json.loads(job['completed_stages'])
        
        self.assertEqual(len(completed), 1)


class TestJobHistory(unittest.TestCase):
    """Test cases for job history queries"""
    
    def setUp(self):
        """Create database with multiple jobs"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        # Create test jobs
        for i in range(5):
            self.db.create_job({
                'mode': 'prelay',
                'vccn': '1p1v',
                'user': 'user1' if i < 3 else 'user2'
            })
    
    def tearDown(self):
        """Clean up"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_16_get_job_history(self):
        """Test getting job history"""
        history = self.db.get_job_history(limit=10)
        
        self.assertEqual(len(history), 5)
    
    def test_17_limit_job_history(self):
        """Test limiting job history"""
        history = self.db.get_job_history(limit=3)
        
        self.assertEqual(len(history), 3)
    
    def test_18_filter_by_user(self):
        """Test filtering job history by user"""
        history = self.db.get_job_history(limit=10, user_filter='user1')
        
        self.assertEqual(len(history), 3)
        for job in history:
            self.assertEqual(job['user'], 'user1')
    
    def test_19_filter_by_status(self):
        """Test filtering job history by status"""
        # Update one job to running
        history = self.db.get_job_history(limit=1)
        self.db.update_job_status(history[0]['job_id'], 'running')
        
        running_jobs = self.db.get_job_history(status_filter='running')
        queued_jobs = self.db.get_job_history(status_filter='queued')
        
        self.assertEqual(len(running_jobs), 1)
        self.assertEqual(len(queued_jobs), 4)


class TestResultStorage(unittest.TestCase):
    """Test cases for result storage and retrieval"""
    
    def setUp(self):
        """Create database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()
        self.db = DatabaseManager(self.db_path)
        
        # Create a job
        self.job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
    
    def tearDown(self):
        """Clean up"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_20_store_single_result(self):
        """Test storing single result"""
        results = [{
            'corner': 'TT',
            'extraction': 'typical',
            'temperature': '85',
            'voltage_combo': 'v1nom',
            'del_rr': 3.12e-11,
            'del_ff': 3.18e-11
        }]
        
        success = self.db.store_results(self.job_id, results)
        
        self.assertTrue(success)
    
    def test_21_store_multiple_results(self):
        """Test storing multiple results"""
        results = [
            {
                'corner': 'TT',
                'extraction': 'typical',
                'temperature': '85',
                'voltage_combo': 'v1nom',
                'del_rr': 3.12e-11
            },
            {
                'corner': 'FFG',
                'extraction': 'typical',
                'temperature': '85',
                'voltage_combo': 'v1nom',
                'del_rr': 2.98e-11
            }
        ]
        
        success = self.db.store_results(self.job_id, results)
        
        self.assertTrue(success)
    
    def test_22_get_job_results(self):
        """Test retrieving job results"""
        # Store results
        results = [{
            'corner': 'TT',
            'del_rr': 3.12e-11
        }]
        self.db.store_results(self.job_id, results)
        
        # Retrieve
        stored = self.db.get_job_results(self.job_id)
        
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]['corner'], 'TT')
    
    def test_23_results_sorted_by_corner(self):
        """Test results are sorted by corner"""
        results = [
            {'corner': 'TT'},
            {'corner': 'FFG'},
            {'corner': 'SSG'}
        ]
        self.db.store_results(self.job_id, results)
        
        stored = self.db.get_job_results(self.job_id)
        
        # Should be sorted alphabetically by corner
        corners = [r['corner'] for r in stored]
        self.assertEqual(corners, ['FFG', 'SSG', 'TT'])
    
    def test_24_measurements_json_stored(self):
        """Test additional measurements stored as JSON"""
        results = [{
            'corner': 'TT',
            'measurements': {'custom_param': 123.45}
        }]
        self.db.store_results(self.job_id, results)
        
        stored = self.db.get_job_results(self.job_id)
        measurements = json.loads(stored[0]['measurements_json'])
        
        self.assertEqual(measurements['custom_param'], 123.45)
    
    def test_25_job_statistics_updated(self):
        """Test job statistics updated after storing results"""
        results = [{'corner': 'TT'}, {'corner': 'FFG'}]
        self.db.store_results(self.job_id, results)
        
        job = self.db.get_job(self.job_id)
        
        self.assertEqual(job['total_simulations'], 2)
        self.assertEqual(job['successful_simulations'], 2)


class TestDatabaseMaintenance(unittest.TestCase):
    """Test cases for database maintenance operations"""
    
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
    
    def test_26_cleanup_old_jobs(self):
        """Test cleaning up old jobs"""
        # Create job
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        # Manually set old created_at (simulate old job)
        conn, cursor = self.db._get_conn()
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        cursor.execute('UPDATE jobs SET created_at = ? WHERE job_id = ?', (old_date, job_id))
        conn.commit()
        
        # Cleanup jobs older than 90 days
        deleted = self.db.cleanup_old_jobs(days=90)
        
        self.assertEqual(deleted, 1)
        
        # Job should be gone
        job = self.db.get_job(job_id)
        self.assertIsNone(job)
    
    def test_27_optimize_database(self):
        """Test database optimization runs without error"""
        self.db.optimize_database()  # Should not raise exception
    
    def test_28_backup_database(self):
        """Test database backup creation"""
        # Create some data
        self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        
        # Backup
        backup_path = self.db_path + '.backup'
        success = self.db.backup_database(backup_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup contains data
        backup_db = DatabaseManager(backup_path)
        jobs = backup_db.get_job_history()
        self.assertEqual(len(jobs), 1)
        backup_db.close()
        
        os.remove(backup_path)


class TestForeignKeyConstraints(unittest.TestCase):
    """Test cases for foreign key constraints"""
    
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
    
    def test_29_results_deleted_with_job(self):
        """Test results are deleted when job is deleted (CASCADE)"""
        # Create job and results
        job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
        self.db.store_results(job_id, [{'corner': 'TT'}])
        
        # Verify results exist
        results = self.db.get_job_results(job_id)
        self.assertEqual(len(results), 1)
        
        # Delete job
        conn, cursor = self.db._get_conn()
        cursor.execute('DELETE FROM jobs WHERE job_id = ?', (job_id,))
        conn.commit()
        
        # Results should be gone too
        results = self.db.get_job_results(job_id)
        self.assertEqual(len(results), 0)


class TestThreadSafety(unittest.TestCase):
    """Test cases for thread safety"""
    
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
    
    def test_30_multiple_connections(self):
        """Test multiple threads can get connections"""
        import threading
        
        results = []
        
        def create_job():
            job_id = self.db.create_job({'mode': 'prelay', 'vccn': '1p1v'})
            results.append(job_id)
        
        threads = [threading.Thread(target=create_job) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have created 3 jobs
        self.assertEqual(len(results), 3)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
