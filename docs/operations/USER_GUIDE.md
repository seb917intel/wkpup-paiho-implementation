# User Guide - WKPUP Web Automation

## Quick Start (5 minutes)

### Step 1: Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8888
```

You should see the WKPUP Automation homepage.

### Step 2: Configure Your Simulation

Fill out the form with your simulation parameters:

**Required Fields**:
- **Mode**: Choose "Pre-layout" or "Post-layout"
- **Simulation Mode**: Choose "AC" or "DC"
- **Voltage Domain**: Choose voltage level (1.1V, 1.2V, 1.8V)
- **Condition**: Choose "Performance", "Functional", or "HTOL"

**Optional Fields**:
- **CPU Cores**: Default 8 (adjust based on available resources)
- **Memory**: Default 16GB (adjust based on simulation size)
- **Simulator**: Choose "PrimeSim" or "FineSim"

### Step 3: Submit the Job

Click "Submit Simulation" button.

You'll receive:
- Job ID (e.g., `job_20250501_120000_abc123`)
- Status confirmation
- Link to monitor progress

### Step 4: Monitor Progress

Click the "Monitor Progress" link or navigate to:
```
http://localhost:8888/jobs/{job_id}
```

You'll see real-time updates as the job progresses through stages:
- ✅ gen (Generation): Creating testbenches
- ⏳ run (Simulation): Running SPICE
- ⏳ ext (Extraction): Parsing results
- ⏳ srt (Sorting): Aggregating data
- ⏳ bkp (Backup): Archiving results

### Step 5: View Results

Once complete, click "View Results" to see:
- All simulation measurements
- Corner-by-corner data
- Pass/fail status
- Download links for detailed reports

---

## Detailed Usage

### Understanding Parameters

#### Mode
- **Pre-layout**: Schematic-level simulation
- **Post-layout**: Includes parasitic extraction

#### Simulation Mode
- **AC**: AC analysis (frequency response)
- **DC**: DC analysis (steady-state)

#### Voltage Domain
Defines the primary operating voltage:
- **1.1V**: Standard low-power domain
- **1.2V**: Medium voltage domain
- **1.8V**: High voltage domain

#### Condition
- **Performance (perf)**: Typical operating conditions
- **Functional (func)**: Worst-case functional verification
- **HTOL**: High-temperature operating life stress

#### Extraction Type (Advanced)
- **typical**: Typical extraction
- **cworst_CCworst_T**: Worst-case capacitance
- **cbest_CCbest_T**: Best-case capacitance

### Parameter Combinations

#### Example 1: Quick Pre-Layout Check
```
Mode: Pre-layout
Sim Mode: AC
Voltage: 1.1V
Condition: Performance
CPU: 8
Memory: 16GB
```
**Use Case**: Fast initial verification  
**Duration**: ~15 minutes  
**Simulations**: 84 (7 corners × 4 temps × 3 voltages)

#### Example 2: Full Post-Layout Validation
```
Mode: Post-layout
Sim Mode: AC
Voltage: 1.1V
Condition: Performance
Extraction: typical,cworst_CCworst_T,cbest_CCbest_T
CPU: 16
Memory: 32GB
```
**Use Case**: Complete design sign-off  
**Duration**: ~2-4 hours  
**Simulations**: 252 (7 corners × 3 extractions × 4 temps × 3 voltages)

#### Example 3: HTOL Stress Test
```
Mode: Post-layout
Sim Mode: DC
Voltage: 1.1V
Condition: HTOL
CPU: 16
Memory: 32GB
```
**Use Case**: Reliability verification  
**Duration**: ~1-2 hours  
**Simulations**: 84+

---

## Advanced Features

### Job History

Access all previous jobs:
```
http://localhost:8888/jobs
```

Filter by:
- **User**: See only your jobs
- **Status**: Filter by success/failed/running
- **Date**: View jobs from specific time period

### Result Comparison

Compare two simulation runs:
1. Open first result page
2. Click "Compare with..." button
3. Select second job
4. View side-by-side comparison

### Batch Submission (via API)

Submit multiple jobs programmatically:

```python
import requests

jobs = []

for voltage in ['1p1v', '1p2v', '1p8v']:
    params = {
        'mode': 'prelay',
        'sim_mode': 'ac',
        'vccn': voltage,
        'condition': 'perf'
    }
    
    response = requests.post('http://localhost:8888/submit', data=params)
    result = response.json()
    jobs.append(result['job_id'])

print(f"Submitted {len(jobs)} jobs: {jobs}")
```

### Custom Alerts

Configure email notifications for job completion:

```yaml
# config/notifications.yaml
email:
  enabled: true
  smtp_server: smtp.example.com
  recipients:
    - user@example.com
  
  on_success: true
  on_failure: true
```

---

## Best Practices

### 1. Start Small

- First job: Use pre-layout with default settings
- Verify results before scaling up
- Gradually increase complexity

### 2. Resource Management

- **CPU**: Use 8 cores for quick jobs, 16+ for production
- **Memory**: 16GB for pre-layout, 32GB+ for post-layout
- **Concurrent Jobs**: Limit to 3-5 to avoid resource contention

### 3. Result Verification

Always check:
- ✅ All corners completed
- ✅ No SPICE errors in logs
- ✅ Pass/fail status as expected
- ✅ Results match previous runs (for regression)

### 4. Data Organization

Use consistent naming:
- Job descriptions: `{project}_{block}_{version}`
- Archive old results periodically
- Keep database backed up

### 5. Collaboration

- Add comments to jobs (metadata)
- Share job IDs with team
- Export results for documentation

---

## Troubleshooting (Quick Reference)

### Job Failed

1. Check job status page for error message
2. Review SPICE log: `{result_dir}/log/spice.log`
3. Verify parameters are correct
4. Re-submit if transient error

### No Results Shown

1. Wait for job to complete (check status)
2. Verify result directory exists
3. Check `creport.txt` file manually
4. Contact admin if database issue

### Slow Performance

1. Reduce CPU count (contention)
2. Check nbjob queue: `nbq`
3. Free up disk space
4. Reduce concurrent jobs

### WebSocket Issues

1. Refresh browser page
2. Clear browser cache
3. Try different browser
4. Check firewall settings

---

## API Reference (Quick)

### Submit Job
```
POST /submit
Content-Type: application/x-www-form-urlencoded

mode=prelay&sim_mode=ac&vccn=1p1v&condition=perf
```

**Response**:
```json
{
  "status": "success",
  "job_id": "job_20250501_120000_abc123",
  "message": "Job submitted successfully"
}
```

### Get Job Status
```
GET /jobs/{job_id}
```

**Response**:
```json
{
  "job_id": "job_20250501_120000_abc123",
  "status": "running",
  "progress": 50,
  "current_stage": "run",
  "user": "chinseba"
}
```

### List Jobs
```
GET /jobs?user=chinseba&status=success&limit=10
```

### View Results
```
GET /results/{job_id}
```

### Cancel Job
```
POST /jobs/{job_id}/cancel
```

### Health Check
```
GET /health
```

---

## Keyboard Shortcuts

- `Ctrl+Enter`: Submit form
- `Ctrl+R`: Refresh job status
- `Esc`: Close modals
- `?`: Show help

---

## Tips & Tricks

### Tip 1: Save Parameter Templates

Bookmark URLs with pre-filled parameters:
```
http://localhost:8888/?mode=prelay&sim_mode=ac&vccn=1p1v
```

### Tip 2: Monitor from Command Line

```bash
# Watch job progress
watch -n 5 'curl -s http://localhost:8888/jobs/YOUR_JOB_ID | jq ".progress"'
```

### Tip 3: Bulk Result Export

```bash
# Export all results to CSV
curl http://localhost:8888/jobs | jq -r '.jobs[] | [.job_id, .status, .result_dir] | @csv'
```

### Tip 4: Quick Re-Run

From result page, click "Re-run with same parameters"

### Tip 5: Result Caching

Results are cached - identical parameters use cached data (saves time!)

---

## FAQs

**Q: How long does a typical simulation take?**  
A: Pre-layout: 15-30 min, Post-layout: 1-4 hours (depends on complexity)

**Q: Can I modify Pai Ho's scripts?**  
A: NO! They are intentionally read-only. All customization via web interface.

**Q: What if I need custom corners?**  
A: Contact admin to add to Pai Ho's CSV tables, then they'll appear in dropdown.

**Q: Can I run simulations offline?**  
A: No, web server must be running. Use manual Pai Ho method for offline.

**Q: How many jobs can I run simultaneously?**  
A: Default 3. Can be increased in config, but watch resource usage.

**Q: Where are results stored?**  
A: In `{workdir}/00bkp_{timestamp}/` and database tracks metadata.

**Q: Can I delete old jobs?**  
A: Yes, but only from database (web UI → Job History → Delete). Files persist.

**Q: What browsers are supported?**  
A: Chrome, Firefox, Safari, Edge (latest versions)

**Q: Is there a dark mode?**  
A: Not yet, but can be added in static/css/

**Q: Can I export results to Excel?**  
A: Yes, use "Export to CSV" button on results page

---

## Getting More Help

- **Documentation**: `/docs/` directory
- **Examples**: `/examples/` directory
- **Health Check**: http://localhost:8888/health
- **Admin**: Contact your local administrator

---

## Changelog

### Version 1.0 (May 2025)
- Initial release
- Web UI for job submission
- Real-time progress monitoring
- Database tracking
- Result visualization

### Future Enhancements
- Email notifications
- Result comparison tool
- Batch submission UI
- Custom report templates
- Dark mode
