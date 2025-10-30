# Deliverable 3: database.py Implementation Specification

## Overview

**Module**: `database.py`  
**Purpose**: Job tracking and result storage using SQLite database  
**Lines of Code**: ~400 lines  
**Priority**: P0 (Week 3-4, Core Implementation)  
**Dependencies**: None (standalone database module)

## Feature Extraction Context

**Source**: This module extracts and adapts the database tracking feature from @seb917intel/wkpup-simulation

**Extraction Strategy** (from ULTIMATE_MASTER_PLAN.md):
- ✅ **Extract**: Database tracking (SQLite job history, results storage)
- ✅ **Value**: Historical analysis, debugging capability
- ✅ **Risk**: Low (read-only for simulations)
- ❌ **Reject**: Any custom logic that bypasses Pai Ho's validated core

**Key Principle**:
> "Extract wkpup's valuable UI/database features and apply them as WRAPPERS around Pai Ho's UNTOUCHED, validated core."

## Ground Truth Validation

This specification is validated against **COMPREHENSIVE_ANALYSIS.md** for understanding Pai Ho's workflow and expected data structures.

### Key References:

1. **Workflow Stages** (from COMPREHENSIVE_ANALYSIS.md):
   - Each job executes 6 stages: gen → run → ext → srt → bkp → usr
   - Results include creport.txt and individual corner reports
   - Backup directories have timestamp format: `00bkp_YYYYMMDDHHmm/`

2. **PVT Matrix Data**:
   - 84-324 simulations per job (depending on configuration)
   - Each simulation produces measurements in .mt0 files
   - Consolidated results in creport.txt

3. **Expected Measurements** (from .mt0 files):
   ```
   del_rr: 3.12398102e-11  (rise-to-rise delay)
   del_ff: 3.18924935e-11  (fall-to-fall delay)
   temper: 85°C
   ```

## Functional Requirements

### FR-1: Job Creation and Tracking

**Function**: Create and track simulation jobs with all parameters

**Database Schema**:
```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    
    -- Configuration parameters (from config.cfg)
    mode TEXT,
    vccn TEXT,
    vcctx TEXT,
    supply_1st TEXT,
    supply_2nd TEXT,
    supply_3rd TEXT,
    condition TEXT,
    cpu_count INTEGER,
    memory_gb INTEGER,
    sim_mode TEXT,
    simulator TEXT,
    
    -- Execution tracking
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    elapsed_seconds REAL,
    
    -- Stage tracking
    current_stage TEXT,
    completed_stages TEXT,  -- JSON array: ["gen", "run", "ext"]
    
    -- Results
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
);
```

**Implementation**:
```python
def create_job(self, params: Dict) -> str:
    """
    Create a new job record
    
    Args:
        params: Dictionary with configuration parameters
        
    Returns:
        job_id (UUID string)
    """
    job_id = str(uuid.uuid4())
    
    self.cursor.execute('''
        INSERT INTO jobs (
            job_id, status, mode, vccn, vcctx,
            supply_1st, supply_2nd, supply_3rd,
            condition, cpu_count, memory_gb,
            sim_mode, simulator, domain_path,
            user, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id, 'queued',
        params.get('mode'),
        params.get('vccn'),
        params.get('vcctx'),
        # ... all parameters
    ))
    
    self.conn.commit()
    return job_id
```

### FR-2: Job Status Updates

**Function**: Update job status and progress in real-time

**Status Transitions**:
```
queued → running → completed
         ↓
         failed
         ↓
         cancelled (manual intervention)
```

**Implementation**:
```python
def update_job_status(self, job_id: str, status: str, 
                      stage: Optional[str] = None,
                      error_message: Optional[str] = None) -> bool:
    """
    Update job status and current stage
    
    Args:
        job_id: Job identifier
        status: New status (queued/running/completed/failed/cancelled)
        stage: Current stage being executed
        error_message: Error message if status is 'failed'
        
    Returns:
        Success status
    """
    updates = {
        'status': status,
        'updated_at': datetime.now()
    }
    
    if status == 'running' and not self._get_started_at(job_id):
        updates['started_at'] = datetime.now()
    
    if status in ('completed', 'failed', 'cancelled'):
        updates['completed_at'] = datetime.now()
        # Calculate elapsed time
        started_at = self._get_started_at(job_id)
        if started_at:
            updates['elapsed_seconds'] = (datetime.now() - started_at).total_seconds()
    
    if stage:
        updates['current_stage'] = stage
        
    if error_message:
        updates['error_message'] = error_message
        updates['error_stage'] = stage
    
    # Build SQL UPDATE statement dynamically
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [job_id]
    
    self.cursor.execute(f'''
        UPDATE jobs SET {set_clause} WHERE job_id = ?
    ''', values)
    
    self.conn.commit()
    return True
```

**Stage Progress Tracking**:
```python
def mark_stage_complete(self, job_id: str, stage: str) -> bool:
    """
    Mark a stage as completed
    
    Args:
        job_id: Job identifier
        stage: Stage name (gen/run/ext/srt/bkp/usr)
        
    Returns:
        Success status
    """
    # Retrieve current completed stages
    completed = self._get_completed_stages(job_id)
    if stage not in completed:
        completed.append(stage)
    
    # Update database
    self.cursor.execute('''
        UPDATE jobs 
        SET completed_stages = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = ?
    ''', (json.dumps(completed), job_id))
    
    self.conn.commit()
    return True
```

### FR-3: Result Storage

**Function**: Store simulation results for historical analysis and comparison

**Results Schema**:
```sql
CREATE TABLE results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    
    -- PVT corner identification
    corner TEXT,           -- TT, FFG, SSG, etc.
    extraction TEXT,       -- typical, cworst_CCworst_T, cbest_CCbest_T
    temperature TEXT,      -- m40, 85, 100, 125
    voltage_combo TEXT,    -- v1min, v1nom, v1max (or v1min_v2min_v3min)
    
    -- Measurements (from .mt0 files)
    del_rr REAL,          -- rise-to-rise delay
    del_ff REAL,          -- fall-to-fall delay
    power REAL,           -- power consumption
    current REAL,         -- current
    
    -- Additional measurements (JSON for flexibility)
    measurements_json TEXT,
    
    -- File paths
    netlist_path TEXT,
    mt0_file_path TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

CREATE INDEX idx_results_job_id ON results(job_id);
CREATE INDEX idx_results_corner ON results(corner);
```

**Implementation**:
```python
def store_results(self, job_id: str, results: List[Dict]) -> bool:
    """
    Store simulation results for a job
    
    Args:
        job_id: Job identifier
        results: List of result dictionaries (one per corner/temp/voltage)
        
    Returns:
        Success status
    """
    for result in results:
        self.cursor.execute('''
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
    self.cursor.execute('''
        UPDATE jobs
        SET total_simulations = ?,
            successful_simulations = ?
        WHERE job_id = ?
    ''', (len(results), len(results), job_id))
    
    self.conn.commit()
    return True
```

### FR-4: Job Query and Retrieval

**Function**: Query jobs with filtering and sorting

**Implementation**:
```python
def get_job(self, job_id: str) -> Optional[Dict]:
    """
    Get job details by ID
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job dictionary or None if not found
    """
    self.cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
    row = self.cursor.fetchone()
    
    if row:
        return dict(row)
    return None

def get_job_history(self, limit: int = 100, 
                    status_filter: Optional[str] = None,
                    user_filter: Optional[str] = None) -> List[Dict]:
    """
    Get job history with optional filtering
    
    Args:
        limit: Maximum number of jobs to return
        status_filter: Filter by status (optional)
        user_filter: Filter by user (optional)
        
    Returns:
        List of job dictionaries
    """
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
    
    self.cursor.execute(query, params)
    return [dict(row) for row in self.cursor.fetchall()]

def get_job_results(self, job_id: str) -> List[Dict]:
    """
    Get all results for a job
    
    Args:
        job_id: Job identifier
        
    Returns:
        List of result dictionaries
    """
    self.cursor.execute('''
        SELECT * FROM results WHERE job_id = ?
        ORDER BY corner, temperature, voltage_combo
    ''', (job_id,))
    
    return [dict(row) for row in self.cursor.fetchall()]
```

### FR-5: Database Maintenance

**Function**: Cleanup old jobs and optimize database

**Implementation**:
```python
def cleanup_old_jobs(self, days: int = 90) -> int:
    """
    Delete jobs older than specified days
    
    Args:
        days: Age threshold in days
        
    Returns:
        Number of jobs deleted
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    self.cursor.execute('''
        DELETE FROM jobs WHERE created_at < ?
    ''', (cutoff_date,))
    
    deleted = self.cursor.rowcount
    self.conn.commit()
    
    # Vacuum to reclaim space
    self.cursor.execute('VACUUM')
    
    return deleted

def optimize_database(self):
    """Optimize database for better performance"""
    self.cursor.execute('ANALYZE')
    self.cursor.execute('VACUUM')
    self.conn.commit()
```

## Non-Functional Requirements

### NFR-1: Data Integrity

**Requirement**: Ensure database consistency and prevent corruption

**Enforcement**:
- Foreign key constraints enabled
- CHECK constraints on enum fields (status)
- Transaction management for multi-step operations
- Automatic backups

**Implementation**:
```python
def __init__(self, db_path: str):
    """Initialize with foreign key support"""
    self.conn = sqlite3.connect(db_path)
    self.conn.row_factory = sqlite3.Row  # Dict-like rows
    self.conn.execute('PRAGMA foreign_keys = ON')  # Enable FK constraints
    self.cursor = self.conn.cursor()
    self._create_tables()
```

### NFR-2: Performance

**Requirements**:

| Operation | Target | Strategy |
|-----------|--------|----------|
| Job creation | < 10ms | Single INSERT |
| Status update | < 5ms | Indexed UPDATE |
| Result storage | < 100ms for 84 results | Batch INSERT |
| Job query | < 50ms | Indexed SELECT |
| History query (100 jobs) | < 100ms | Indexed ORDER BY + LIMIT |

**Optimization**:
- Indexes on frequently queried columns (job_id, status, created_at)
- Batch inserts for results
- Connection pooling (for multi-threaded access)

### NFR-3: Thread Safety

**Requirement**: Support concurrent access from web server and job manager

**Implementation**:
```python
import threading

class DatabaseManager:
    """Thread-safe database manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()
    
    def _get_conn(self):
        """Get thread-local connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute('PRAGMA foreign_keys = ON')
            self._local.cursor = self._local.conn.cursor()
        return self._local.conn, self._local.cursor
```

### NFR-4: Backup and Recovery

**Requirement**: Database must be backed up and recoverable

**Implementation**:
```python
def backup_database(self, backup_path: str) -> bool:
    """
    Create database backup
    
    Args:
        backup_path: Path for backup file
        
    Returns:
        Success status
    """
    import shutil
    
    # Use SQLite backup API for consistency
    backup_conn = sqlite3.connect(backup_path)
    with backup_conn:
        self.conn.backup(backup_conn)
    backup_conn.close()
    
    return True

def restore_database(self, backup_path: str) -> bool:
    """
    Restore database from backup
    
    Args:
        backup_path: Path to backup file
        
    Returns:
        Success status
    """
    # Close current connection
    self.conn.close()
    
    # Copy backup to main database
    import shutil
    shutil.copy2(backup_path, self.db_path)
    
    # Reopen
    self.__init__(self.db_path)
    return True
```

## Implementation Structure

### Class Design

```python
#!/usr/bin/env python3
"""
Database Manager for Job Tracking and Result Storage
SQLite-based storage for simulation jobs and results
"""

import sqlite3
import json
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DatabaseManager:
    """
    Manages SQLite database for job tracking and result storage
    Thread-safe for concurrent access
    """
    
    def __init__(self, db_path: str):
        """Initialize database connection and create tables"""
        
    def _create_tables(self):
        """Create database schema"""
        
    # Job Management
    def create_job(self, params: Dict) -> str:
        """Create new job record"""
        
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        
    def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """Update job status"""
        
    def mark_stage_complete(self, job_id: str, stage: str) -> bool:
        """Mark stage as completed"""
        
    def get_job_history(self, limit: int = 100, **filters) -> List[Dict]:
        """Get job history with filtering"""
        
    # Result Management
    def store_results(self, job_id: str, results: List[Dict]) -> bool:
        """Store simulation results"""
        
    def get_job_results(self, job_id: str) -> List[Dict]:
        """Get all results for a job"""
        
    # Maintenance
    def cleanup_old_jobs(self, days: int = 90) -> int:
        """Delete old jobs"""
        
    def optimize_database(self):
        """Optimize database performance"""
        
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        
    def restore_database(self, backup_path: str) -> bool:
        """Restore from backup"""
```

## Testing Strategy

### Unit Tests (40+ test cases)

**Test Categories**:

1. **Database Initialization** (5 tests)
   - Tables created correctly
   - Indexes created
   - Foreign keys enabled
   - Schema version correct
   - Empty database starts clean

2. **Job CRUD Operations** (15 tests)
   - Create job with valid params
   - Create job with minimal params
   - Get job by ID (exists)
   - Get job by ID (not found)
   - Update job status (all transitions)
   - Mark stages complete
   - Query job history
   - Filter by status
   - Filter by user
   - Sort by date
   - Limit results

3. **Result Storage** (10 tests)
   - Store single result
   - Store batch results (84 corners)
   - Store results with all measurements
   - Store results with minimal data
   - Query results by job_id
   - Results deleted when job deleted (FK cascade)
   - Measurements JSON parsed correctly
   - Handle duplicate results

4. **Thread Safety** (5 tests)
   - Concurrent job creation
   - Concurrent status updates
   - Concurrent result storage
   - No database locks
   - Thread-local connections work

5. **Maintenance Operations** (5 tests)
   - Cleanup old jobs
   - Optimize database
   - Backup database
   - Restore database
   - Backup consistency verified

### Integration Tests

```python
def test_complete_job_lifecycle():
    """Test full lifecycle from creation to result storage"""
    
    db = DatabaseManager('test.db')
    
    # Create job
    params = {
        'mode': 'prelay',
        'vccn': '1p1v',
        'condition': 'perf',
        'user': 'test_user'
    }
    job_id = db.create_job(params)
    assert job_id is not None
    
    # Update to running
    db.update_job_status(job_id, 'running', stage='gen')
    job = db.get_job(job_id)
    assert job['status'] == 'running'
    assert job['current_stage'] == 'gen'
    
    # Mark stages complete
    db.mark_stage_complete(job_id, 'gen')
    db.mark_stage_complete(job_id, 'run')
    
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
    
    # Verify final state
    job = db.get_job(job_id)
    assert job['status'] == 'completed'
    assert job['elapsed_seconds'] > 0
    
    stored_results = db.get_job_results(job_id)
    assert len(stored_results) == 1
    assert stored_results[0]['corner'] == 'TT'
```

## Verification Checklist

Before considering this deliverable complete, verify:

- [ ] Database schema created correctly
- [ ] All CRUD operations work
- [ ] Foreign key constraints enforced
- [ ] Indexes improve query performance
- [ ] Thread safety verified
- [ ] All 40+ unit tests pass
- [ ] Integration test passes
- [ ] Backup/restore works
- [ ] No data corruption under concurrent access
- [ ] Code reviewed against feature extraction strategy

## Success Criteria

This deliverable is complete when:

1. ✅ Database stores all job and result data
2. ✅ Thread-safe for concurrent access
3. ✅ All 40+ unit tests pass
4. ✅ Integration test demonstrates full lifecycle
5. ✅ Backup and recovery verified
6. ✅ Performance targets met
7. ✅ Feature extracted from wkpup-simulation and adapted as wrapper
8. ✅ No modifications to Pai Ho's core workflow

## References

- **ULTIMATE_MASTER_PLAN.md**: Module 3: database.py (~400 lines)
- **COMPREHENSIVE_ANALYSIS.md**: Data Flow and Report Generation
- **Feature Source**: @seb917intel/wkpup-simulation (database tracking feature)

## Next Deliverable

After completing database.py:
- **Deliverable 4**: job_manager.py - Background job queue and execution

---

**Status**: Not Started  
**Created**: 2025-10-30  
**Feature Extraction**: Database tracking from wkpup-simulation  
**Validated Against**: COMPREHENSIVE_ANALYSIS.md + ULTIMATE_MASTER_PLAN.md feature extraction strategy
