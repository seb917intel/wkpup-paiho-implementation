#!/usr/bin/env python3
"""
Database Manager for Job Tracking and Result Storage

SQLite-based storage for simulation jobs and results.
This module is part of the WKPUP reconciliation project, extracting and adapting
the database tracking feature from wkpup-simulation.

Reference: ULTIMATE_MASTER_PLAN.md - Module 3: database.py (~400 lines)
Feature Extraction: Database tracking from @seb917intel/wkpup-simulation
Ground Truth: COMPREHENSIVE_ANALYSIS.md - Data flow and report generation
"""

import sqlite3
import json
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class DatabaseError(Exception):
    """Base class for database errors"""
    pass


class IntegrityError(DatabaseError):
    """Raised when data integrity is violated"""
    pass


class DatabaseManager:
    """
    Manages SQLite database for job tracking and result storage.
    Thread-safe for concurrent access from web server and job manager.
    
    This class extracts the database tracking feature from wkpup-simulation
    and adapts it as a wrapper for Pai Ho's validated workflow.
    """
    
    DB_VERSION = 1
    
    def __init__(self, db_path: str):
        """
        Initialize database connection and create tables.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    def _get_conn(self):
        """
        Get thread-local connection.
        
        Returns:
            Tuple of (connection, cursor)
        """
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute('PRAGMA foreign_keys = ON')
            self._local.cursor = self._local.conn.cursor()
        
        return self._local.conn, self._local.cursor
    
    def _init_db(self):
        """Create database schema if it doesn't exist"""
        conn, cursor = self._get_conn()
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
                
                -- Configuration parameters
                mode TEXT,
                vccn TEXT,
                vcctx TEXT,
                supply_1st TEXT,
                supply_2nd TEXT,
                supply_3rd TEXT,
                condition TEXT,
                cpu_count INTEGER,
                memory_gb TEXT,
                sim_mode TEXT,
                simulator TEXT,
                
                -- Execution tracking
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                elapsed_seconds REAL,
                
                -- Stage tracking
                current_stage TEXT,
                completed_stages TEXT,
                
                -- Results summary
                total_simulations INTEGER,
                successful_simulations INTEGER,
                failed_simulations INTEGER,
                
                -- Paths
                domain_path TEXT,
                config_file_path TEXT,
                backup_path TEXT,
                
                -- Error information
                error_message TEXT,
                error_stage TEXT,
                
                -- Metadata
                user TEXT,
                description TEXT
            )
        ''')
        
        # Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                
                -- PVT corner identification
                corner TEXT,
                extraction TEXT,
                temperature TEXT,
                voltage_combo TEXT,
                
                -- Measurements (from .mt0 files)
                del_rr REAL,
                del_ff REAL,
                power REAL,
                current REAL,
                
                -- Additional measurements (JSON for flexibility)
                measurements_json TEXT,
                
                -- File paths
                netlist_path TEXT,
                mt0_file_path TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_results_job_id ON results(job_id)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_results_corner ON results(corner)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)'
        )
        
        conn.commit()
    
    # Job Management Methods
    
    def create_job(self, params: Dict) -> str:
        """
        Create a new job record.
        
        Args:
            params: Dictionary with configuration parameters
            
        Returns:
            job_id (UUID string)
        """
        job_id = str(uuid.uuid4())
        conn, cursor = self._get_conn()
        
        cursor.execute('''
            INSERT INTO jobs (
                job_id, status, mode, vccn, vcctx,
                supply_1st, supply_2nd, supply_3rd,
                condition, cpu_count, memory_gb,
                sim_mode, simulator, domain_path,
                user, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            'queued',
            params.get('mode'),
            params.get('vccn'),
            params.get('vcctx'),
            params.get('1st_supply_swp'),
            params.get('2nd_supply_swp'),
            params.get('3rd_supply_swp'),
            params.get('condition'),
            params.get('CPU'),
            params.get('MEM'),
            params.get('sim_mode'),
            params.get('simulator'),
            params.get('domain_path'),
            params.get('user'),
            params.get('description')
        ))
        
        conn.commit()
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job details by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job dictionary or None if not found
        """
        conn, cursor = self._get_conn()
        cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """
        Update job status and optional fields.
        
        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Additional fields to update (stage, error_message, etc.)
            
        Returns:
            True if successful
        """
        conn, cursor = self._get_conn()
        
        # Build update fields
        updates = {'status': status, 'updated_at': datetime.now().isoformat()}
        
        # Handle status-specific updates
        if status == 'running':
            job = self.get_job(job_id)
            if job and not job.get('started_at'):
                updates['started_at'] = datetime.now().isoformat()
        
        if status in ('completed', 'failed', 'cancelled'):
            updates['completed_at'] = datetime.now().isoformat()
            
            # Calculate elapsed time
            job = self.get_job(job_id)
            if job and job.get('started_at'):
                started = datetime.fromisoformat(job['started_at'])
                elapsed = (datetime.now() - started).total_seconds()
                updates['elapsed_seconds'] = elapsed
        
        # Add additional kwargs
        for key, value in kwargs.items():
            updates[key] = value
        
        # Build SQL
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [job_id]
        
        cursor.execute(f'''
            UPDATE jobs SET {set_clause} WHERE job_id = ?
        ''', values)
        
        conn.commit()
        return True
    
    def mark_stage_complete(self, job_id: str, stage: str) -> bool:
        """
        Mark a stage as completed.
        
        Args:
            job_id: Job identifier
            stage: Stage name
            
        Returns:
            True if successful
        """
        conn, cursor = self._get_conn()
        
        # Get current completed stages
        cursor.execute('SELECT completed_stages FROM jobs WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        
        if row:
            completed_json = row['completed_stages']
            completed = json.loads(completed_json) if completed_json else []
            
            if stage not in completed:
                completed.append(stage)
            
            cursor.execute('''
                UPDATE jobs 
                SET completed_stages = ?,
                    updated_at = ?
                WHERE job_id = ?
            ''', (json.dumps(completed), datetime.now().isoformat(), job_id))
            
            conn.commit()
            return True
        
        return False
    
    def get_job_history(self, limit: int = 100, 
                       status_filter: Optional[str] = None,
                       user_filter: Optional[str] = None) -> List[Dict]:
        """
        Get job history with optional filtering.
        
        Args:
            limit: Maximum number of jobs to return
            status_filter: Filter by status
            user_filter: Filter by user
            
        Returns:
            List of job dictionaries
        """
        conn, cursor = self._get_conn()
        
        query = 'SELECT * FROM jobs'
        params = []
        conditions = []
        
        if status_filter:
            conditions.append('status = ?')
            params.append(status_filter)
        
        if user_filter:
            conditions.append('user = ?')
            params.append(user_filter)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # Result Management Methods
    
    def store_results(self, job_id: str, results: List[Dict]) -> bool:
        """
        Store simulation results for a job.
        
        Args:
            job_id: Job identifier
            results: List of result dictionaries
            
        Returns:
            True if successful
        """
        conn, cursor = self._get_conn()
        
        for result in results:
            cursor.execute('''
                INSERT INTO results (
                    job_id, corner, extraction, temperature, voltage_combo,
                    del_rr, del_ff, power, current,
                    measurements_json, netlist_path, mt0_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                result.get('corner'),
                result.get('extraction'),
                result.get('temperature'),
                result.get('voltage_combo'),
                result.get('del_rr'),
                result.get('del_ff'),
                result.get('power'),
                result.get('current'),
                json.dumps(result.get('measurements', {})),
                result.get('netlist_path'),
                result.get('mt0_file_path')
            ))
        
        # Update job statistics
        cursor.execute('''
            UPDATE jobs
            SET total_simulations = ?,
                successful_simulations = ?,
                updated_at = ?
            WHERE job_id = ?
        ''', (len(results), len(results), datetime.now().isoformat(), job_id))
        
        conn.commit()
        return True
    
    def get_job_results(self, job_id: str) -> List[Dict]:
        """
        Get all results for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of result dictionaries
        """
        conn, cursor = self._get_conn()
        
        cursor.execute('''
            SELECT * FROM results 
            WHERE job_id = ?
            ORDER BY corner, temperature, voltage_combo
        ''', (job_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Maintenance Methods
    
    def cleanup_old_jobs(self, days: int = 90) -> int:
        """
        Delete jobs older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of jobs deleted
        """
        conn, cursor = self._get_conn()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            DELETE FROM jobs WHERE created_at < ?
        ''', (cutoff_date,))
        
        deleted = cursor.rowcount
        conn.commit()
        
        # Vacuum to reclaim space
        cursor.execute('VACUUM')
        
        return deleted
    
    def optimize_database(self):
        """Optimize database for better performance"""
        conn, cursor = self._get_conn()
        cursor.execute('ANALYZE')
        cursor.execute('VACUUM')
        conn.commit()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create database backup.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if successful
        """
        conn, _ = self._get_conn()
        
        backup_conn = sqlite3.connect(backup_path)
        with backup_conn:
            conn.backup(backup_conn)
        backup_conn.close()
        
        return True
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()


# Example usage
if __name__ == "__main__":
    # Create database
    db = DatabaseManager('wkpup.db')
    
    # Create a job
    params = {
        'mode': 'prelay',
        'vccn': '1p1v',
        'condition': 'perf',
        'CPU': '16',
        'MEM': '32G',
        'sim_mode': 'ac',
        'simulator': 'primesim',
        'domain_path': 'gpio/1p1v',
        'user': 'test_user',
        'description': 'Test simulation'
    }
    
    job_id = db.create_job(params)
    print(f"Created job: {job_id}")
    
    # Update status
    db.update_job_status(job_id, 'running', current_stage='gen')
    
    # Mark stage complete
    db.mark_stage_complete(job_id, 'gen')
    
    # Store results
    results = [
        {
            'corner': 'TT',
            'extraction': 'typical',
            'temperature': '85',
            'voltage_combo': 'v1nom',
            'del_rr': 3.12e-11,
            'del_ff': 3.18e-11
        }
    ]
    db.store_results(job_id, results)
    
    # Update to completed
    db.update_job_status(job_id, 'completed')
    
    # Get job
    job = db.get_job(job_id)
    print(f"Job status: {job['status']}")
    print(f"Elapsed: {job['elapsed_seconds']}s")
    
    db.close()
