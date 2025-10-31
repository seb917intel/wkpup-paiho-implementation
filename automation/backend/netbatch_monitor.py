"""
NetBatch monitoring module
Polls NetBatch status and parses output
"""

import subprocess
import re
import os
import getpass
from typing import Dict, List, Tuple
from datetime import datetime


# Get current user (automatically detect)
CURRENT_USER = os.getenv('USER') or getpass.getuser()


def query_netbatch_status(job_ids: List[int]) -> Dict[int, str]:
    """
    Query NetBatch for job statuses
    
    Args:
        job_ids: List of NetBatch job IDs to query
        
    Returns:
        Dictionary mapping job_id -> status
        Status values: "Wait", "Run", "Comp", "Error", "Remote Send", "Remote Approved"
    """
    if not job_ids:
        return {}
    
    # Build query filter for specific job IDs
    job_filter = " || ".join([f"jobid=={jid}" for jid in job_ids])
    
    cmd = [
        "nbstatus", "jobs",
        "--target", "altera_png_normal",
        f"({job_filter}) && qslot=='/psg/km/phe/ckt/gen' && user=='{CURRENT_USER}'"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"⚠️ nbstatus command failed: {result.stderr}")
            return {}
        
        # Parse output
        return parse_nbstatus_output(result.stdout, job_ids)
        
    except subprocess.TimeoutExpired:
        print("⚠️ nbstatus command timed out")
        return {}
    except Exception as e:
        print(f"⚠️ Error querying NetBatch: {e}")
        return {}


def parse_nbstatus_output(output: str, job_ids: List[int]) -> Dict[int, str]:
    """
    Parse nbstatus output and extract job statuses
    
    Args:
        output: Raw nbstatus command output
        job_ids: List of job IDs we're tracking
        
    Returns:
        Dictionary mapping job_id -> status
    """
    statuses = {}
    lines = output.strip().split('\n')
    
    # Find header line
    header_idx = None
    for i, line in enumerate(lines):
        if 'Status' in line and 'Jobid' in line:
            header_idx = i
            break
    
    if header_idx is None:
        # No header found - might be empty output
        return statuses
    
    # Skip header and separator line
    data_lines = lines[header_idx + 2:]
    
    for line in data_lines:
        if not line.strip():
            continue
        
        # Parse line - format: "Status  Jobid  Class  Qslot  User  Cmdline  Workstation"
        parts = line.split()
        if len(parts) < 2:
            continue
        
        # Handle multi-word status (e.g., "Remote Send", "Remote Approved", "Wait Remote")
        if len(parts) >= 2 and parts[0] in ["Remote", "Wait"]:
            if parts[0] == "Wait" and len(parts) >= 2 and parts[1] == "Remote":
                # "Wait Remote"
                status = f"{parts[0]} {parts[1]}"
                try:
                    job_id = int(parts[2])
                except (ValueError, IndexError):
                    continue
            elif parts[0] == "Remote" and len(parts) >= 2:
                # "Remote Send" or "Remote Approved"
                status = f"{parts[0]} {parts[1]}"
                try:
                    job_id = int(parts[2])
                except (ValueError, IndexError):
                    continue
            else:
                # Just "Wait" or other single-word status
                status = parts[0]
                try:
                    job_id = int(parts[1])
                except (ValueError, IndexError):
                    continue
        else:
            status = parts[0]
            try:
                job_id = int(parts[1])
            except (ValueError, IndexError):
                continue
        
        # Only track jobs we care about
        if job_id in job_ids:
            statuses[job_id] = status
    
    return statuses


def get_summary_stats(statuses: Dict[int, str], total_jobs: int, prev_completed: int = 0, prev_started: int = 0) -> Dict:
    """
    Calculate summary statistics from job statuses
    
    Args:
        statuses: Dictionary of job_id -> status
        total_jobs: Total number of jobs expected
        prev_completed: Previously recorded completed count (for monotonic progress)
        prev_started: Previously recorded started count (for monotonic progress)
        
    Returns:
        Summary dictionary with counts and percentages
        
    NetBatch Status States:
    - Comp: Completed successfully
    - Run: Currently running
    - Wait: Queued, not started
    - Wait Remote: Waiting to be sent to remote host
    - Remote Send: Being transferred to remote execution host
    - Remote Approved: Approved to run on remote host
    - Error/Fail/Aborted: Failed
    
    Note: Progress is monotonic - it never decreases. This handles cases where
    completed jobs are purged from NetBatch queue before next poll.
    """
    completed = sum(1 for s in statuses.values() if s == "Comp")
    running = sum(1 for s in statuses.values() if s == "Run")
    
    # Count all waiting states (not yet running)
    wait = sum(1 for s in statuses.values() if s == "Wait")
    wait_remote = sum(1 for s in statuses.values() if s == "Wait Remote")
    remote_send = sum(1 for s in statuses.values() if s == "Remote Send")
    remote_approved = sum(1 for s in statuses.values() if s == "Remote Approved")
    
    # Total waiting = all pre-execution states
    waiting = wait + wait_remote + remote_send + remote_approved
    
    errors = sum(1 for s in statuses.values() if s.lower() in ["error", "fail", "aborted"])
    
    # Jobs not yet reported (might still be queuing or purged)
    not_reported = total_jobs - len(statuses)
    
    # MONOTONIC PROGRESS CALCULATION
    # Current state from NetBatch
    jobs_started_current = running + completed
    
    # Use maximum ever seen (handles purged jobs)
    # If we previously saw 5 jobs started, and now only see 3, use 5
    jobs_started = max(jobs_started_current, prev_started)
    
    # If completed count decreased (jobs purged), use previous max
    # But if we see more completed now, use the higher number
    completed_max = max(completed, prev_completed)
    
    # If jobs are missing from NetBatch and we had progress before,
    # assume missing jobs completed (most likely scenario for purged jobs)
    if not_reported > 0 and prev_started > 0:
        # Missing jobs are likely completed and purged
        # Add them to completed count if it makes sense
        potential_purged = not_reported - (total_jobs - prev_started)
        if potential_purged > 0:
            completed_max = min(completed_max + potential_purged, total_jobs)
    
    # Progress calculation: 
    # - First 50%: Jobs that have started (running or finished)
    # - Second 50%: Jobs that have finished (completed OR errors)
    # Formula: 50% * (jobs_started/total) + 50% * (finished/total)
    # where finished = completed + errors
    # Use max values to ensure monotonic progress
    finished = completed_max + errors
    progress_pct = (50.0 * jobs_started / total_jobs + 50.0 * finished / total_jobs) if total_jobs > 0 else 0
    
    all_complete = (completed_max >= total_jobs) and (errors == 0)
    
    return {
        "total": total_jobs,
        "completed": completed,  # Current count from NetBatch
        "completed_max": completed_max,  # Maximum ever seen (monotonic)
        "running": running,
        "waiting": waiting,
        "errors": errors,
        "not_reported": not_reported,
        "jobs_started": jobs_started,  # Maximum started (monotonic)
        "progress_pct": round(progress_pct, 1),
        "all_complete": all_complete,
        "has_errors": errors > 0,
        # Detailed breakdown for debugging
        "waiting_breakdown": {
            "wait": wait,
            "wait_remote": wait_remote,
            "remote_send": remote_send,
            "remote_approved": remote_approved
        }
    }


def capture_job_ids_from_log(job_log_path: str) -> List[int]:
    """
    Parse job_log.txt to extract NetBatch job IDs
    
    Args:
        job_log_path: Path to job_log.txt file
        
    Returns:
        List of job IDs
    """
    job_ids = []
    
    if not os.path.exists(job_log_path):
        print(f"⚠️ Job log not found: {job_log_path}")
        return job_ids
    
    with open(job_log_path, 'r') as f:
        for line in f:
            # Example line: "Job 1668177568 submitted"
            # or just: "1668177568"
            match = re.search(r'\b(\d{10,})\b', line)
            if match:
                job_id = int(match.group(1))
                if job_id not in job_ids:
                    job_ids.append(job_id)
    
    print(f"📋 Captured {len(job_ids)} job IDs from {job_log_path}")
    return job_ids


def estimate_completion_time(stats: Dict, start_time: datetime) -> Tuple[int, str]:
    """
    Estimate remaining time based on progress
    
    Args:
        stats: Summary statistics dictionary
        start_time: When simulation started
        
    Returns:
        Tuple of (remaining_seconds, formatted_time_string)
    """
    if stats["completed"] == 0:
        return None, "Calculating..."
    
    elapsed = (datetime.now() - start_time).total_seconds()
    avg_time_per_job = elapsed / stats["completed"]
    remaining_jobs = stats["total"] - stats["completed"]
    remaining_seconds = int(avg_time_per_job * remaining_jobs)
    
    # Format time
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60
    
    if hours > 0:
        time_str = f"{hours}h {minutes}m"
    elif minutes > 0:
        time_str = f"{minutes}m {seconds}s"
    else:
        time_str = f"{seconds}s"
    
    return remaining_seconds, time_str


# Test function
if __name__ == "__main__":
    print(f"Current user: {CURRENT_USER}")
    print("\nTesting NetBatch status query...")
    
    # Test with dummy job IDs (replace with real ones for testing)
    test_job_ids = [1668177568, 1668177570]
    statuses = query_netbatch_status(test_job_ids)
    
    print(f"\nStatuses: {statuses}")
    
    stats = get_summary_stats(statuses, len(test_job_ids))
    print(f"\nSummary: {stats}")
