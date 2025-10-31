#!/usr/bin/env python3
"""
Background Monitoring Service for Simulations

Periodically checks active simulations and triggers actions based on state.
Uses Tornado IOLoop PeriodicCallback for non-blocking background tasks.
Phase 2B: Added auto-extraction with threading support.
"""

import tornado.ioloop
import sqlite3
import json
import time
import traceback
import threading
import os
from netbatch_monitor import query_netbatch_status, get_summary_stats


class BackgroundMonitor(object):
    """
    Background service that monitors active simulations.
    
    Features:
    - Polls NetBatch status every N seconds (default: 3 seconds)
    - Updates simulation progress in database
    - Broadcasts real-time updates via WebSocket
    - Detects completion and marks simulations as ready for extraction
    - Phase 2B: Auto-triggers extraction in background thread
    
    Usage:
        monitor = BackgroundMonitor(db_path='automation/webapp.db', check_interval=3000)
        monitor.start()  # Start monitoring
        
        # Later...
        monitor.stop()   # Stop monitoring
    """
    
    def __init__(self, db_path, check_interval=3000, auto_extract=True):
        """
        Initialize background monitor.
        
        Args:
            db_path (str): Path to SQLite database
            check_interval (int): Check interval in milliseconds (default: 3000ms = 3 seconds)
            auto_extract (bool): Automatically trigger extraction on completion (default: True)
        """
        self.db_path = db_path
        self.check_interval = check_interval
        self.auto_extract = auto_extract
        self.periodic_callback = None
        self.is_running = False
        self.extraction_threads = {}  # Track active extraction threads
        
        print("[BackgroundMonitor] Initialized (interval: {0}ms, auto_extract: {1})".format(
            check_interval, auto_extract))
    
    def start(self):
        """
        Start periodic monitoring.
        Creates PeriodicCallback and starts it in the Tornado IOLoop.
        """
        if self.is_running:
            print("[BackgroundMonitor] Already running")
            return
        
        self.periodic_callback = tornado.ioloop.PeriodicCallback(
            self.check_all_simulations,
            self.check_interval
        )
        self.periodic_callback.start()
        self.is_running = True
        
        print("[BackgroundMonitor] Started (checking every {0}ms)".format(self.check_interval))
    
    def stop(self):
        """
        Stop periodic monitoring.
        Stops the PeriodicCallback.
        """
        if not self.is_running:
            print("[BackgroundMonitor] Not running")
            return
        
        if self.periodic_callback:
            self.periodic_callback.stop()
            self.periodic_callback = None
        
        self.is_running = False
        print("[BackgroundMonitor] Stopped")
    
    def _is_phantom_submission(self, sim_id, work_dir, state):
        """
        Detect if submission is phantom (marked as submitted but no actual jobs/directories).
        
        A phantom submission occurs when:
        1. No job IDs in database
        2. No corner directories in work_dir (TT/, FFG/, etc.)
        3. Submission is old (> 5 minutes without jobs)
        
        Args:
            sim_id (str): Simulation ID
            work_dir (str): Working directory path
            state (str): Current state ('submitted' or 'running')
            
        Returns:
            bool: True if phantom submission detected
        """
        # Must be in 'submitted' or 'running' state to be considered
        if state not in ['submitted', 'running']:
            return False
        
        # Check if work_dir exists
        if not os.path.exists(work_dir):
            print("[BackgroundMonitor] Work directory does not exist: {0}".format(work_dir))
            return True
        
        # Check for corner directories (simulation outputs)
        # Exclude template/configuration directories
        try:
            all_dirs = [d for d in os.listdir(work_dir) if os.path.isdir(os.path.join(work_dir, d))]
            corner_dirs = [d for d in all_dirs if d not in ['template', 'configuration', 'report']]
            
            if not corner_dirs:
                print("[BackgroundMonitor] No corner directories found in: {0}".format(work_dir))
                return True
        except Exception as e:
            print("[BackgroundMonitor] Error checking work_dir: {0}".format(e))
            return False
        
        # Check submission age
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT submitted_at FROM simulations WHERE sim_id = ?', (sim_id,))
            row = c.fetchone()
            conn.close()
            
            if row and row[0]:
                from datetime import datetime, timedelta
                submitted_time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                age = datetime.now() - submitted_time
                
                # If stuck for > 5 minutes with no jobs, likely phantom
                if age > timedelta(minutes=5):
                    print("[BackgroundMonitor] Submission is {0} old with no jobs".format(age))
                    return True
        except Exception as e:
            print("[BackgroundMonitor] Error checking submission age: {0}".format(e))
        
        return False
    
    def _mark_as_failed(self, sim_id, reason):
        """
        Mark simulation as failed with error message.
        
        Args:
            sim_id (str): Simulation ID
            reason (str): Failure reason
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                UPDATE simulations 
                SET state = 'failed',
                    progress_pct = 0.0,
                    completed_at = CURRENT_TIMESTAMP
                WHERE sim_id = ?
            ''', (sim_id,))
            conn.commit()
            conn.close()
            
            # Broadcast failure update
            from websocket_handler import SimulationWebSocket
            SimulationWebSocket.broadcast_update(sim_id, {
                'sim_id': sim_id,
                'state': 'failed',
                'error_message': reason,
                'progress_pct': 0.0
            })
            
            print("[BackgroundMonitor] Marked as failed: {0} - {1}".format(sim_id, reason))
            
        except Exception as e:
            print("[BackgroundMonitor] Error marking as failed: {0}".format(e))
    
    def check_all_simulations(self):
        """
        Check all active simulations.
        
        Called periodically by PeriodicCallback.
        Must be fast and non-blocking to avoid delaying IOLoop.
        """
        try:
            # Query active simulations (state = 'submitted' or 'running')
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('''
                SELECT sim_id, netbatch_job_ids, work_dir, state, total_jobs, username
                FROM simulations
                WHERE state IN ('submitted', 'running')
            ''')
            
            rows = c.fetchall()
            conn.close()
            
            if not rows:
                # No active simulations
                return
            
            print("[BackgroundMonitor] Checking {0} active simulations...".format(len(rows)))
            
            # Check each simulation
            for row in rows:
                sim_id = row['sim_id']
                job_ids_json = row['netbatch_job_ids']
                work_dir = row['work_dir']
                state = row['state']
                total_jobs = row['total_jobs']
                username = row['username']
                
                self.check_simulation(sim_id, job_ids_json, work_dir, state, total_jobs, username)
        
        except Exception as e:
            print("[BackgroundMonitor] Error in check_all_simulations: {0}".format(e))
            traceback.print_exc()
    
    def check_simulation(self, sim_id, job_ids_json, work_dir, state, total_jobs, username):
        """
        Check single simulation status using improved job tracking.
        
        Args:
            sim_id (str): Simulation ID
            job_ids_json (str): JSON array of NetBatch job IDs
            work_dir (str): Working directory path
            state (str): Current simulation state
            total_jobs (int): Total number of jobs
            username (str): User who submitted simulation
        """
        try:
            # Import the new tracking function
            from main_tornado import get_simulation_status_from_tracking
            
            # Parse job IDs for phantom detection
            if not job_ids_json:
                print("[BackgroundMonitor] No job IDs for sim_id: {0}".format(sim_id))
                if self._is_phantom_submission(sim_id, work_dir, state):
                    print("[BackgroundMonitor]   -> Phantom submission detected, marking as failed")
                    self._mark_as_failed(sim_id, "No jobs submitted - gen/run stage failed")
                return
            
            job_ids = json.loads(job_ids_json)
            
            if not job_ids:
                print("[BackgroundMonitor] Empty job IDs for sim_id: {0}".format(sim_id))
                if self._is_phantom_submission(sim_id, work_dir, state):
                    print("[BackgroundMonitor]   -> Phantom submission detected, marking as failed")
                    self._mark_as_failed(sim_id, "No jobs submitted - gen/run stage failed")
                return
            
            # Use improved job tracking system
            print("[BackgroundMonitor] Checking status for sim_id: {0} ({1} jobs)".format(
                sim_id, len(job_ids)))
            
            stats = get_simulation_status_from_tracking(sim_id)
            
            if stats is None:
                # No tracking data - may be old simulation, skip or use fallback
                print("[BackgroundMonitor] No tracking data for {0}, skipping".format(sim_id))
                return
            
            print("[BackgroundMonitor] Status for {0}: completed={1}, running={2}, waiting={3}, errors={4}".format(
                sim_id, stats['completed'], stats['running'], stats['waiting'], stats['errors']))
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Update progress
            c.execute('''
                UPDATE simulations SET
                    jobs_completed = ?,
                    jobs_running = ?,
                    jobs_waiting = ?,
                    jobs_errors = ?,
                    progress_pct = ?
                WHERE sim_id = ?
            ''', (
                stats['completed'],
                stats['running'],
                stats['waiting'],
                stats['errors'],
                stats['progress_pct'],
                sim_id
            ))
            
            # Check if all jobs finished (may include errors)
            if stats.get('all_jobs_finished', False):
                if state == 'submitted' or state == 'running':
                    # Determine final state based on errors
                    if stats['errors'] > 0:
                        new_state = 'failed'
                        print("[BackgroundMonitor] Simulation failed: {0} ({1} completed, {2} errors)".format(
                            sim_id, stats['completed'], stats['errors']))
                    else:
                        new_state = 'completed'
                        print("[BackgroundMonitor] Simulation completed: {0}".format(sim_id))
                    
                    c.execute('''
                        UPDATE simulations SET
                            state = ?,
                            completed_at = CURRENT_TIMESTAMP
                        WHERE sim_id = ?
                    ''', (new_state, sim_id))
                    conn.commit()
                    
                    # Phase 2B: Auto-trigger extraction for completed simulations
                    # UPDATED: Also extract partial failures if >50% jobs succeeded
                    if self.auto_extract:
                        if new_state == 'completed':
                            # No errors - extract everything
                            print("[BackgroundMonitor] Auto-extracting results for {0}".format(sim_id))
                            self.trigger_extraction(sim_id, work_dir)
                        elif new_state == 'failed' and stats['completed'] > (total_jobs / 2):
                            # Partial failure but majority succeeded - extract successful jobs
                            print("[BackgroundMonitor] Auto-extracting partial results for {0} ({1}/{2} jobs succeeded)".format(
                                sim_id, stats['completed'], total_jobs))
                            self.trigger_extraction(sim_id, work_dir)
                        else:
                            print("[BackgroundMonitor] Skipping auto-extraction for {0} ({1}/{2} jobs succeeded)".format(
                                sim_id, stats['completed'], total_jobs))
                else:
                    new_state = state
            else:
                # Jobs still running or waiting
                if state == 'submitted':
                    c.execute('''
                        UPDATE simulations SET state = 'running'
                        WHERE sim_id = ?
                    ''', (sim_id,))
                    new_state = 'running'
                else:
                    new_state = state
            
            conn.commit()
            conn.close()
            
            # Broadcast update via WebSocket
            from websocket_handler import SimulationWebSocket
            
            update_data = {
                'sim_id': sim_id,
                'state': new_state,
                'total_jobs': total_jobs,
                'jobs_completed': stats['completed'],
                'jobs_running': stats['running'],
                'jobs_waiting': stats['waiting'],
                'jobs_errors': stats['errors'],
                'progress_pct': stats['progress_pct'],
                'all_complete': stats['all_complete']
            }
            
            SimulationWebSocket.broadcast_update(sim_id, update_data)
            
            print("[BackgroundMonitor] Updated sim_id: {0} (progress: {1:.1f}%, state: {2})".format(
                sim_id, stats['progress_pct'], new_state))
        
        except json.JSONDecodeError as e:
            print("[BackgroundMonitor] Invalid JSON for job_ids in sim_id {0}: {1}".format(
                sim_id, e))
        
        except Exception as e:
            print("[BackgroundMonitor] Error checking sim_id {0}: {1}".format(sim_id, e))
            traceback.print_exc()
    
    def trigger_extraction(self, sim_id, work_dir):
        """
        Trigger extraction for completed simulation.
        
        Phase 2B: Run extraction in background thread to avoid blocking IOLoop.
        
        Args:
            sim_id (str): Simulation ID
            work_dir (str): Working directory path
        """
        # Check if extraction already running for this sim
        if sim_id in self.extraction_threads:
            thread = self.extraction_threads[sim_id]
            if thread.is_alive():
                print("[BackgroundMonitor] Extraction already running for {0}".format(sim_id))
                return
        
        print("[BackgroundMonitor] AUTO-EXTRACTION: Starting for {0}".format(sim_id))
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=self._run_extraction,
            args=(sim_id, work_dir),
            name="extraction-{0}".format(sim_id)
        )
        thread.daemon = True
        thread.start()
        
        self.extraction_threads[sim_id] = thread
    
    def _run_extraction(self, sim_id, work_dir):
        """
        Run extraction stages in background thread.
        
        Phase 2B: Full implementation with progress tracking.
        
        Args:
            sim_id (str): Simulation ID
            work_dir (str): Working directory path
        """
        from simulation import run_extraction_stage, run_sorting_stage, run_backup_stage
        from websocket_handler import SimulationWebSocket
        
        try:
            # Get simulation details including project and voltage_domain
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM simulations WHERE sim_id = ?', (sim_id,))
            sim = dict(c.fetchone())
            
            project = sim['project']
            voltage_domain = sim['voltage_domain']
            
            # Update state to extracting
            c.execute('UPDATE simulations SET state = ? WHERE sim_id = ?', ('extracting', sim_id))
            conn.commit()
            conn.close()
            
            # Broadcast state change
            SimulationWebSocket.broadcast_update(sim_id, {
                'sim_id': sim_id,
                'state': 'extracting',
                'extraction_stage': 'extraction',
                'message': 'Extracting results from .mt0 files...'
            })
            
            print("[AUTO-EXTRACT] [{0}] Stage 1/3: Running extraction...".format(sim_id))
            ext_result = run_extraction_stage(work_dir, project=project, voltage_domain=voltage_domain)
            
            if not ext_result:
                raise Exception("Extraction stage failed")
            
            # Update to sorting
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('UPDATE simulations SET state = ? WHERE sim_id = ?', ('sorting', sim_id))
            conn.commit()
            conn.close()
            
            SimulationWebSocket.broadcast_update(sim_id, {
                'sim_id': sim_id,
                'state': 'sorting',
                'extraction_stage': 'sorting',
                'message': 'Compiling results into creport.txt...'
            })
            
            print("[AUTO-EXTRACT] [{0}] Stage 2/3: Running sorting...".format(sim_id))
            srt_result = run_sorting_stage(work_dir, project=project, voltage_domain=voltage_domain)
            
            if not srt_result:
                raise Exception("Sorting stage failed")
            
            # Update to backing up
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('UPDATE simulations SET state = ? WHERE sim_id = ?', ('backing_up', sim_id))
            conn.commit()
            conn.close()
            
            SimulationWebSocket.broadcast_update(sim_id, {
                'sim_id': sim_id,
                'state': 'backing_up',
                'extraction_stage': 'backup',
                'message': 'Creating timestamped backup...'
            })
            
            print("[AUTO-EXTRACT] [{0}] Stage 3/3: Running backup...".format(sim_id))
            backup_dir = run_backup_stage(work_dir, project=project, voltage_domain=voltage_domain)
            
            if not backup_dir:
                raise Exception("Backup stage failed")
            
            # Mark as finished
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                UPDATE simulations SET
                    state = 'finished',
                    backup_dir = ?,
                    finished_at = CURRENT_TIMESTAMP
                WHERE sim_id = ?
            ''', (backup_dir, sim_id))
            conn.commit()
            conn.close()
            
            SimulationWebSocket.broadcast_update(sim_id, {
                'sim_id': sim_id,
                'state': 'finished',
                'extraction_stage': 'complete',
                'backup_dir': backup_dir,
                'message': 'Extraction complete! Results ready.'
            })
            
            print("[AUTO-EXTRACT] [{0}] ✅ COMPLETE - Results in {1}".format(sim_id, backup_dir))
            
        except Exception as e:
            print("[AUTO-EXTRACT] [{0}] ❌ FAILED: {1}".format(sim_id, e))
            traceback.print_exc()
            
            # Mark as failed
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('UPDATE simulations SET state = ? WHERE sim_id = ?', ('failed', sim_id))
            conn.commit()
            conn.close()
            
            SimulationWebSocket.broadcast_update(sim_id, {
                'sim_id': sim_id,
                'state': 'failed',
                'extraction_stage': 'failed',
                'message': 'Extraction failed: {0}'.format(str(e))
            })
        
        finally:
            # Clean up thread tracking
            if sim_id in self.extraction_threads:
                del self.extraction_threads[sim_id]


# Example usage:
if __name__ == '__main__':
    import os
    from pathlib import Path
    
    # Test the monitor - use absolute path
    script_dir = Path(__file__).parent.resolve()
    automation_dir = script_dir.parent.resolve()
    db_path = str(automation_dir / 'webapp.db')
    
    print("Testing BackgroundMonitor...")
    print("Database: {0}".format(db_path))
    
    monitor = BackgroundMonitor(db_path, check_interval=1000)
    
    # Start monitoring
    monitor.start()
    
    # Run for 10 seconds
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\nStopping...")
        monitor.stop()
