#!/usr/bin/env python3
"""
Background Job Manager

Manages background execution of simulation jobs using threading and queue.
This module is part of the WKPUP reconciliation project, implementing asynchronous
job execution for Pai Ho's simulation workflow.

Reference: ULTIMATE_MASTER_PLAN.md - Module 4: job_manager.py (~300 lines)
Feature Extraction: Background job queue from wkpup-simulation
Ground Truth: COMPREHENSIVE_ANALYSIS.md - Complete workflow execution
"""

import threading
import queue
import logging
import time
from typing import Dict, Optional, Callable
from datetime import datetime
from enum import Enum


class JobStatus(Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobManagerError(Exception):
    """Base class for job manager errors"""
    pass


class JobNotFoundError(JobManagerError):
    """Raised when job is not found"""
    pass


class BackgroundJobManager:
    """
    Manages background execution of simulation jobs.
    
    Uses threading and queue for asynchronous job processing.
    Integrates with DatabaseManager for persistence and PaiHoExecutor for execution.
    
    This class extracts the background job queue feature from wkpup-simulation
    and adapts it for Pai Ho's workflow.
    """
    
    def __init__(self, database_manager, paiho_executor_factory: Callable,
                 max_workers: int = 2):
        """
        Initialize job manager.
        
        Args:
            database_manager: DatabaseManager instance for job persistence
            paiho_executor_factory: Factory function to create PaiHoExecutor instances
            max_workers: Maximum number of concurrent worker threads
        """
        self.db = database_manager
        self.executor_factory = paiho_executor_factory
        self.max_workers = max_workers
        
        # Job queue
        self.job_queue = queue.Queue()
        
        # Active jobs tracking (job_id -> thread)
        self.active_jobs = {}
        self.active_jobs_lock = threading.Lock()
        
        # Worker threads
        self.workers = []
        self.shutdown_event = threading.Event()
        
        # Status callbacks (for WebSocket updates)
        self.status_callbacks = []
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Start workers
        self._start_workers()
    
    def _start_workers(self):
        """Start worker threads"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_thread,
                name=f"JobWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
            self.logger.info(f"Started worker thread: {worker.name}")
    
    def _worker_thread(self):
        """
        Worker thread that processes jobs from the queue.
        
        This is the core execution loop that:
        1. Gets job from queue
        2. Updates status to running
        3. Executes simulation via PaiHoExecutor
        4. Updates status to completed/failed
        5. Stores results in database
        """
        while not self.shutdown_event.is_set():
            try:
                # Get job from queue (with timeout to check shutdown)
                try:
                    job_id = self.job_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Track active job
                with self.active_jobs_lock:
                    self.active_jobs[job_id] = threading.current_thread()
                
                try:
                    self._execute_job(job_id)
                finally:
                    # Remove from active jobs
                    with self.active_jobs_lock:
                        self.active_jobs.pop(job_id, None)
                    
                    self.job_queue.task_done()
                
            except Exception as e:
                self.logger.exception(f"Worker thread error: {e}")
    
    def _execute_job(self, job_id: str):
        """
        Execute a single job.
        
        Args:
            job_id: Job identifier
        """
        self.logger.info(f"Executing job: {job_id}")
        
        # Get job details from database
        job = self.db.get_job(job_id)
        if not job:
            self.logger.error(f"Job not found: {job_id}")
            return
        
        # Update status to running
        self.db.update_job_status(job_id, JobStatus.RUNNING.value)
        self._notify_status_change(job_id, JobStatus.RUNNING.value)
        
        try:
            # Create executor for this job's domain
            domain_path = job.get('domain_path')
            if not domain_path:
                raise ValueError("Job missing domain_path")
            
            executor = self.executor_factory(domain_path)
            
            # Determine stages to run
            stages = ['gen', 'run', 'ext', 'srt', 'bkp']
            
            # Execute simulation with progress tracking
            results = {}
            for stage in stages:
                self.logger.info(f"Job {job_id}: Running stage {stage}")
                
                # Update current stage
                self.db.update_job_status(
                    job_id, 
                    JobStatus.RUNNING.value,
                    current_stage=stage
                )
                self._notify_status_change(job_id, JobStatus.RUNNING.value, stage=stage)
                
                # Execute stage
                result = executor.run_stage('config.cfg', stage)
                results[stage] = result
                
                if not result['success']:
                    # Stage failed
                    error_msg = f"Stage {stage} failed: {result.get('stderr', 'Unknown error')}"
                    self.logger.error(f"Job {job_id}: {error_msg}")
                    
                    self.db.update_job_status(
                        job_id,
                        JobStatus.FAILED.value,
                        error_message=error_msg,
                        error_stage=stage
                    )
                    self._notify_status_change(job_id, JobStatus.FAILED.value)
                    return
                
                # Mark stage complete
                self.db.mark_stage_complete(job_id, stage)
            
            # All stages completed successfully
            self.logger.info(f"Job {job_id}: Completed successfully")
            self.db.update_job_status(job_id, JobStatus.COMPLETED.value)
            self._notify_status_change(job_id, JobStatus.COMPLETED.value)
            
        except Exception as e:
            self.logger.exception(f"Job {job_id} execution error: {e}")
            self.db.update_job_status(
                job_id,
                JobStatus.FAILED.value,
                error_message=str(e)
            )
            self._notify_status_change(job_id, JobStatus.FAILED.value)
    
    def submit(self, job_id: str) -> bool:
        """
        Submit a job for background execution.
        
        Args:
            job_id: Job identifier (must already exist in database)
            
        Returns:
            True if submitted successfully
            
        Raises:
            JobNotFoundError: If job doesn't exist in database
        """
        # Verify job exists
        job = self.db.get_job(job_id)
        if not job:
            raise JobNotFoundError(f"Job not found: {job_id}")
        
        # Add to queue
        self.job_queue.put(job_id)
        self.logger.info(f"Submitted job to queue: {job_id}")
        
        return True
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a queued or running job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled, False if job not found or already completed
        """
        job = self.db.get_job(job_id)
        if not job:
            return False
        
        status = job.get('status')
        
        if status == JobStatus.QUEUED.value:
            # Job is in queue - mark as cancelled
            self.db.update_job_status(job_id, JobStatus.CANCELLED.value)
            self.logger.info(f"Cancelled queued job: {job_id}")
            return True
        
        elif status == JobStatus.RUNNING.value:
            # Job is running - mark as cancelled (worker will see this)
            # Note: We can't forcefully stop the worker thread,
            # but we mark it as cancelled for user visibility
            self.db.update_job_status(job_id, JobStatus.CANCELLED.value)
            self.logger.warning(f"Marked running job as cancelled: {job_id}")
            return True
        
        else:
            # Job already completed/failed/cancelled
            self.logger.info(f"Cannot cancel job in status: {status}")
            return False
    
    def get_queue_status(self) -> Dict:
        """
        Get current queue status.
        
        Returns:
            Dict with queue statistics
        """
        with self.active_jobs_lock:
            active_count = len(self.active_jobs)
            active_job_ids = list(self.active_jobs.keys())
        
        queued_count = self.job_queue.qsize()
        
        return {
            'queued_jobs': queued_count,
            'active_jobs': active_count,
            'active_job_ids': active_job_ids,
            'total_workers': self.max_workers,
            'available_workers': self.max_workers - active_count
        }
    
    def register_status_callback(self, callback: Callable):
        """
        Register a callback for status updates.
        
        Useful for WebSocket real-time updates.
        
        Args:
            callback: Function to call with (job_id, status, **kwargs)
        """
        self.status_callbacks.append(callback)
    
    def _notify_status_change(self, job_id: str, status: str, **kwargs):
        """
        Notify all registered callbacks of status change.
        
        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Additional status information
        """
        for callback in self.status_callbacks:
            try:
                callback(job_id, status, **kwargs)
            except Exception as e:
                self.logger.exception(f"Status callback error: {e}")
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the job manager.
        
        Args:
            wait: If True, wait for all jobs to complete
        """
        self.logger.info("Shutting down job manager")
        
        if wait:
            # Wait for queue to empty
            self.job_queue.join()
        
        # Signal workers to shutdown
        self.shutdown_event.set()
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.logger.info("Job manager shutdown complete")
    
    def wait_for_completion(self):
        """Wait for all queued jobs to complete"""
        self.job_queue.join()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Create job manager
    from database import DatabaseManager
    from paiho_executor import PaiHoExecutor
    
    db = DatabaseManager('test.db')
    
    def executor_factory(domain_path):
        return PaiHoExecutor(domain_path)
    
    manager = BackgroundJobManager(db, executor_factory, max_workers=2)
    
    # Create and submit a job
    job_id = db.create_job({
        'mode': 'prelay',
        'vccn': '1p1v',
        'domain_path': 'gpio/1p1v',
        'user': 'test_user'
    })
    
    manager.submit(job_id)
    
    # Check queue status
    status = manager.get_queue_status()
    print(f"Queue status: {status}")
    
    # Wait for completion
    manager.wait_for_completion()
    
    # Shutdown
    manager.shutdown()
    
    db.close()
