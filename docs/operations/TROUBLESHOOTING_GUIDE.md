# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Version Mismatch Error

**Symptom**:
```
ValueError: gen_tb.pl has 525 lines, expected 570 (ver03)
```

**Cause**: Using gen_tb.pl ver02 instead of ver03

**Solution**:
1. Check script_path in configuration:
   ```bash
   grep "script_path" /path/to/sim_pvt_local.sh
   ```

2. If it points to ver02, update to ver03:
   ```bash
   # Old (WRONG):
   script_path=".../auto_pvt/ver02"
   
   # New (CORRECT):
   script_path=".../auto_pvt/ver03"
   ```

3. Verify the change:
   ```bash
   wc -l /path/to/ver03/tb_gen/gen_tb.pl
   # Should output: 570
   ```

**Prevention**: Set `strict_validation=True` in PaiHoExecutor

---

### Issue 2: Parameter Validation Fails

**Symptom**:
```
ValueError: Invalid corner 'CUSTOM_CORNER'. Valid: ['TT', 'FFG', ...]
```

**Cause**: Trying to use parameter not in Pai Ho's whitelist

**Solution**:
1. Check available options:
   ```python
   from modules.config_generator import PaiHoConfigGenerator
   
   generator = PaiHoConfigGenerator('/path/to/csv')
   options = generator.get_valid_options()
   print("Valid corners:", options['corners'])
   ```

2. Use only whitelisted values from Pai Ho's CSV files

3. If you truly need a custom parameter, add it to Pai Ho's CSV files FIRST, then test thoroughly

**Prevention**: Always use dropdowns in web UI (auto-populated from whitelists)

---

### Issue 3: Bit-Identical Test Fails

**Symptom**:
```
AssertionError: Different files found: ['TT/typical/typical_85/sim_tx.sp']
```

**Cause**: Web automation and manual execution producing different output

**Root Causes**:
1. Different config.cfg format
2. Different environment variables
3. Timing-dependent randomness
4. File path differences

**Debugging Steps**:
1. Compare config files:
   ```bash
   diff /tmp/web_config.cfg /tmp/manual_config.cfg
   ```

2. Compare generated netlists:
   ```bash
   diff TT/typical/typical_85/sim_tx.sp TT/typical/typical_85/sim_tx.sp.manual
   ```

3. Check environment:
   ```bash
   # Run both with same environment
   env > web_env.txt
   env > manual_env.txt
   diff web_env.txt manual_env.txt
   ```

4. Verify paths are absolute (not relative)

**Solution**:
- Ensure PaiHoConfigGenerator uses EXACT same format as manual config
- Run both executions in same directory
- Use absolute paths throughout

---

### Issue 4: Database Not Updating

**Symptom**: Results not appearing in database

**Cause**: Result parsing failed or database connection issue

**Debugging**:
1. Check if results exist:
   ```bash
   ls -la /path/to/00bkp_*/creport.txt
   ```

2. Try parsing manually:
   ```python
   from modules.result_parser import ResultParser
   
   parser = ResultParser('/path/to/00bkp_20250501120000')
   results = parser.parse_creport()
   print(f"Parsed {len(results)} measurements")
   ```

3. Check database connection:
   ```python
   from modules.database import SimulationDatabase
   
   db = SimulationDatabase('database/simulation_tracking.db')
   db.conn.execute('SELECT 1').fetchone()
   ```

**Solution**:
- Verify result_dir path is correct
- Check creport.txt format matches expected pattern
- Ensure database file has write permissions

---

### Issue 5: Job Stuck in "Running" Status

**Symptom**: Job shows "running" but no progress

**Causes**:
1. Subprocess hung
2. SPICE simulation waiting for license
3. nbjob queue full
4. Disk space full

**Debugging**:
1. Check job status:
   ```bash
   ps aux | grep sim_pvt.sh
   ```

2. Check nbjob queue:
   ```bash
   nbq
   ```

3. Check disk space:
   ```bash
   df -h /path/to/workdir
   ```

4. Check logs:
   ```bash
   tail -f logs/web_server.log
   tail -f /path/to/workdir/log/sim.log
   ```

**Solution**:
- Kill hung process: `kill <pid>`
- Wait for license availability
- Clear nbjob queue
- Free up disk space

---

### Issue 6: WebSocket Connection Failed

**Symptom**: Real-time progress monitoring not working

**Cause**: WebSocket connection issues

**Debugging**:
1. Check browser console for errors (F12)

2. Verify WebSocket endpoint:
   ```javascript
   ws://localhost:8888/progress
   ```

3. Check server logs:
   ```bash
   grep "WebSocket" logs/web_server.log
   ```

**Solution**:
- Ensure port 8888 is not blocked by firewall
- Check if multiple browser tabs are connected (connection limit)
- Restart web server

---

### Issue 7: Permission Denied Errors

**Symptom**:
```
PermissionError: [Errno 13] Permission denied: '/path/to/config.cfg'
```

**Causes**:
1. Pai Ho's scripts are read-only (this is intentional)
2. Working directory not writable
3. Database file not writable

**Solution**:
1. For Pai Ho's scripts (READ-ONLY is correct):
   - Don't modify Pai Ho's original files
   - Copy config.cfg to writable location

2. For working directory:
   ```bash
   chmod 755 /path/to/workdir
   ```

3. For database:
   ```bash
   chmod 644 database/simulation_tracking.db
   ```

---

### Issue 8: Import Errors

**Symptom**:
```
ModuleNotFoundError: No module named 'tornado'
```

**Cause**: Missing Python dependencies

**Solution**:
```bash
pip3 install --user tornado pytest
```

Or use requirements.txt:
```bash
pip3 install --user -r requirements.txt
```

---

## Diagnostic Commands

### Check System Health

```bash
# Check all components
curl http://localhost:8888/health

# Expected output:
{
  "status": "healthy",
  "components": {
    "config_generator": "ok",
    "executor": "ok",
    "database": "ok",
    "job_manager": "ok"
  }
}
```

### Verify Pai Ho's Scripts

```bash
# Check versions
PAI_HO_DIR="/path/to/ver03"

echo "sim_pvt.sh: $(wc -l < $PAI_HO_DIR/sim_pvt.sh) lines (expected: 589)"
echo "gen_tb.pl: $(wc -l < $PAI_HO_DIR/tb_gen/gen_tb.pl) lines (expected: 570)"
echo "pvt_loop.sh: $(wc -l < $PAI_HO_DIR/tb_gen/pvt_loop.sh) lines (expected: 723)"

# Check if read-only
ls -la $PAI_HO_DIR/sim_pvt.sh
# Should show: -r--r--r--
```

### Test Configuration Generator

```python
from modules.config_generator import PaiHoConfigGenerator

generator = PaiHoConfigGenerator('/path/to/csv')

# Test valid parameters
params = {'mode': 'prelay', 'sim_mode': 'ac', 'vccn': '1p1v'}
config_file = generator.generate(params)
print(f"Generated: {config_file}")

# Test invalid parameters (should fail)
try:
    invalid = {'mode': 'INVALID'}
    generator.generate(invalid)
    print("ERROR: Should have failed!")
except ValueError as e:
    print(f"Correctly rejected: {e}")
```

### Test Database

```python
from modules.database import SimulationDatabase

db = SimulationDatabase('database/simulation_tracking.db')

# Check statistics
stats = db.get_statistics()
print(f"Total jobs: {stats['total_jobs']}")
print(f"By status: {stats['by_status']}")
print(f"Top users: {stats['top_users']}")

# Query recent jobs
recent = db.query_jobs(limit=5)
for job in recent:
    print(f"{job['job_id']}: {job['status']}")
```

### Test Executor

```python
from modules.paiho_executor import PaiHoExecutor

executor = PaiHoExecutor(
    '/path/to/workdir',
    '/path/to/ver03'
)

# Verify scripts
executor._verify_scripts()
print("✓ Scripts verified")

# Test single stage (gen only, fast)
result = executor.execute_stage('/tmp/test_config.cfg', 'gen')
print(f"Status: {result.status}")
print(f"Duration: {result.duration_seconds}s")
```

---

## Performance Tuning

### Increase Concurrent Jobs

Edit `config/web_config.yaml`:
```yaml
web:
  max_concurrent_jobs: 5  # Increase from 3 to 5
```

Restart server.

### Database Optimization

```sql
-- Add indices for common queries
CREATE INDEX IF NOT EXISTS idx_jobs_completed ON jobs(completed_at);
CREATE INDEX IF NOT EXISTS idx_results_corner ON results(corner, temperature);

-- Vacuum database periodically
VACUUM;
```

### Log Rotation

```bash
# Add to crontab
0 0 * * * find /path/to/logs -name "*.log" -mtime +7 -delete
```

---

## Recovery Procedures

### Recover from Crashed Job

```python
from modules.database import SimulationDatabase

db = SimulationDatabase('database/simulation_tracking.db')

# Find stuck jobs
stuck = db.query_jobs({'status': 'running'})

for job in stuck:
    # Check if actually still running
    # If not, update status
    db.update_job_status(job['job_id'], 'failed', 
                         error_message='Job crashed')
```

### Database Corruption

```bash
# Backup database
cp database/simulation_tracking.db database/simulation_tracking.db.bak

# Check integrity
sqlite3 database/simulation_tracking.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp database/simulation_tracking.db.bak database/simulation_tracking.db
```

### Clean Workspace

```bash
# Remove all generated files
cd /path/to/workdir
rm -rf TT/ FFG/ SSG/ FSG/ SFG/ FFAG/ SSAG/
rm -rf 00bkp_*/
rm -f config.cfg

# Keep only templates and dependencies
```

---

## Monitoring

### Real-Time Job Monitoring

```bash
# Watch job queue
watch -n 2 'curl -s http://localhost:8888/jobs | jq ".jobs[] | {job_id, status}"'
```

### Log Monitoring

```bash
# Tail all logs
tail -f logs/*.log

# Filter errors
tail -f logs/web_server.log | grep ERROR
```

### Resource Monitoring

```bash
# CPU/Memory usage
top -p $(pgrep -f main.py)

# Disk usage
du -sh /path/to/workdir/*
```

---

## Getting Help

1. **Check Logs**: Start with `logs/web_server.log`
2. **Run Health Check**: `curl http://localhost:8888/health`
3. **Test Components**: Use diagnostic commands above
4. **Check Pai Ho's Scripts**: Ensure ver03 is being used
5. **Review Documentation**: Re-read COMPLETE_IMPLEMENTATION_PLAN.md

If issue persists, collect diagnostics:
```bash
# Create diagnostic bundle
tar czf diagnostics.tar.gz \
    logs/ \
    config/ \
    database/simulation_tracking.db \
    /path/to/workdir/log/
```
