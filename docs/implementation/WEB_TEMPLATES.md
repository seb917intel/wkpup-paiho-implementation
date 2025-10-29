# HTML Templates for Web Interface

## Template 1: Main Page (Job Submission)

**File**: `web_automation/templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WKPUP Automation - Powered by Pai Ho's Validated Core</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .notice {
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }
        
        .notice strong {
            color: #1976D2;
        }
        
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .form-section {
            margin-bottom: 30px;
        }
        
        .form-section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .form-group label .required {
            color: #f44336;
        }
        
        .form-group select,
        .form-group input {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group select:focus,
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 8px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            border-left: 4px solid #28a745;
        }
        
        .result.error {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        
        .result strong {
            display: block;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .loading .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 WKPUP Automation System</h1>
        <div class="subtitle">
            Powered by Pai Ho's Scientifically Validated Simulation Core (ver03) | User: {{ user }}
        </div>
    </div>
    
    <div class="container">
        <div class="notice">
            <strong>🔒 100% Accuracy Guaranteed</strong><br>
            This interface uses Pai Ho's original simulation core WITHOUT modification.
            All parameters are validated against Pai Ho's whitelists to ensure correctness.
        </div>
        
        <div class="form-container">
            <form id="simulationForm">
                <!-- Basic Configuration -->
                <div class="form-section">
                    <h2>📋 Basic Configuration</h2>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Mode <span class="required">*</span></label>
                            <select name="mode" required>
                                {% for mode in options['modes'] %}
                                <option value="{{ mode }}" {% if mode == defaults['mode'] %}selected{% endif %}>
                                    {{ mode.capitalize() }}
                                </option>
                                {% endfor %}
                            </select>
                            <span class="help-text">Pre-layout or post-layout simulation</span>
                        </div>
                        
                        <div class="form-group">
                            <label>Simulation Mode <span class="required">*</span></label>
                            <select name="sim_mode" required>
                                {% for mode in options['sim_modes'] %}
                                <option value="{{ mode }}" {% if mode == defaults['sim_mode'] %}selected{% endif %}>
                                    {{ mode.upper() }}
                                </option>
                                {% endfor %}
                            </select>
                            <span class="help-text">AC or DC analysis</span>
                        </div>
                        
                        <div class="form-group">
                            <label>Voltage Domain (vccn) <span class="required">*</span></label>
                            <select name="vccn" required>
                                <option value="1p1v">1.1V</option>
                                <option value="1p2v">1.2V</option>
                                <option value="1p8v">1.8V</option>
                            </select>
                            <span class="help-text">Primary voltage domain</span>
                        </div>
                        
                        <div class="form-group">
                            <label>TX Voltage (vcctx)</label>
                            <select name="vcctx">
                                <option value="">Same as vccn</option>
                                <option value="1p1v">1.1V</option>
                                <option value="1p2v">1.2V</option>
                                <option value="1p8v">1.8V</option>
                            </select>
                            <span class="help-text">TX voltage (optional, defaults to vccn)</span>
                        </div>
                    </div>
                </div>
                
                <!-- Simulation Settings -->
                <div class="form-section">
                    <h2>⚙️ Simulation Settings</h2>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Condition <span class="required">*</span></label>
                            <select name="condition" required>
                                {% for cond in options['conditions'] %}
                                <option value="{{ cond }}" {% if cond == defaults['condition'] %}selected{% endif %}>
                                    {{ cond.upper() }}
                                </option>
                                {% endfor %}
                            </select>
                            <span class="help-text">Performance, functional, or HTOL</span>
                        </div>
                        
                        <div class="form-group">
                            <label>Simulator <span class="required">*</span></label>
                            <select name="simulator" required>
                                {% for sim in options['simulators'] %}
                                <option value="{{ sim }}" {% if sim == defaults['simulator'] %}selected{% endif %}>
                                    {{ sim.capitalize() }}
                                </option>
                                {% endfor %}
                            </select>
                            <span class="help-text">SPICE simulator</span>
                        </div>
                        
                        <div class="form-group">
                            <label>CPU Cores</label>
                            <input type="number" name="CPU" value="{{ defaults['CPU'] }}" min="1" max="128">
                            <span class="help-text">Number of CPU cores for parallel execution</span>
                        </div>
                        
                        <div class="form-group">
                            <label>Memory (GB)</label>
                            <input type="number" name="MEM" value="{{ defaults['MEM'] }}" min="1" max="512">
                            <span class="help-text">Memory allocation per job</span>
                        </div>
                    </div>
                </div>
                
                <!-- Advanced Options -->
                <div class="form-section">
                    <h2>🔧 Advanced Options</h2>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Extraction Type</label>
                            <select name="alter_extraction">
                                {% for ext in options['extractions'] %}
                                <option value="{{ ext }}" {% if ext == defaults['alter_extraction'] %}selected{% endif %}>
                                    {{ ext }}
                                </option>
                                {% endfor %}
                            </select>
                            <span class="help-text">Post-layout extraction type</span>
                        </div>
                        
                        <div class="form-group">
                            <label>1st Supply Sweep</label>
                            <select name="1st_supply_swp">
                                <option value="all" selected>All (default)</option>
                                {% for volt in options['voltages_ac'][:5] %}
                                <option value="{{ volt }}">{{ volt }}</option>
                                {% endfor %}
                            </select>
                            <span class="help-text">First supply sweep range</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <button type="submit" class="submit-btn">
                        ▶️ Submit Simulation
                    </button>
                </div>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 15px;">Submitting job...</p>
            </div>
            
            <div class="result" id="result"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('simulationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const formData = new FormData(form);
            const params = {};
            formData.forEach((value, key) => params[key] = value);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            form.querySelector('.submit-btn').disabled = true;
            
            try {
                // Submit to server
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: new URLSearchParams(params)
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                
                if (result.status === 'success') {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <strong>✅ Job Submitted Successfully!</strong>
                        <p><strong>Job ID:</strong> ${result.job_id}</p>
                        <p><strong>Config File:</strong> ${result.config_file}</p>
                        <p style="margin-top: 15px;">
                            <a href="/jobs/${result.job_id}" style="color: #28a745; text-decoration: underline;">
                                Monitor Progress →
                            </a>
                        </p>
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <strong>❌ Submission Failed</strong>
                        <p>${result.message}</p>
                    `;
                }
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                const resultDiv = document.getElementById('result');
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `
                    <strong>❌ Network Error</strong>
                    <p>${error.message}</p>
                `;
                resultDiv.style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
                form.querySelector('.submit-btn').disabled = false;
            }
        });
    </script>
</body>
</html>
```

---

## Template 2: Results Viewer

**File**: `web_automation/templates/results.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results - {{ job['job_id'] }} | WKPUP Automation</title>
    <style>
        /* Reuse styles from index.html */
        /* ... (same styles) ... */
        
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .results-table th,
        .results-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        .results-table th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }
        
        .results-table tr:nth-child(even) {
            background: #f9f9f9;
        }
        
        .results-table tr:hover {
            background: #f0f0f0;
        }
        
        .metric {
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Simulation Results</h1>
        <div class="subtitle">Job ID: {{ job['job_id'] }} | Status: {{ job['status'] }}</div>
    </div>
    
    <div class="container">
        <!-- Job Info -->
        <div class="form-container">
            <h2>Job Information</h2>
            <table style="width: 100%; margin-top: 15px;">
                <tr>
                    <td><strong>User:</strong></td>
                    <td>{{ job['user'] }}</td>
                </tr>
                <tr>
                    <td><strong>Submitted:</strong></td>
                    <td>{{ job['submitted_at'] }}</td>
                </tr>
                <tr>
                    <td><strong>Mode:</strong></td>
                    <td>{{ job['mode'] }}</td>
                </tr>
                <tr>
                    <td><strong>Voltage:</strong></td>
                    <td>{{ job['vccn'] }}</td>
                </tr>
                <tr>
                    <td><strong>Result Directory:</strong></td>
                    <td>{{ job['result_dir'] }}</td>
                </tr>
            </table>
        </div>
        
        <!-- Results Table -->
        <div class="form-container" style="margin-top: 30px;">
            <h2>Simulation Measurements</h2>
            
            {% if results %}
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Corner</th>
                        <th>Extraction</th>
                        <th>Temp</th>
                        <th>Voltage</th>
                        <th>tphl</th>
                        <th>tplh</th>
                        <th>ipeak</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in results %}
                    <tr>
                        <td>{{ result['corner'] }}</td>
                        <td>{{ result['extraction'] or 'N/A' }}</td>
                        <td>{{ result['temperature'] }}°C</td>
                        <td>{{ result['voltage'] }}</td>
                        <td class="metric">{{ "%.3e" % result['tphl'] if result['tphl'] else 'N/A' }}</td>
                        <td class="metric">{{ "%.3e" % result['tplh'] if result['tplh'] else 'N/A' }}</td>
                        <td class="metric">{{ "%.3e" % result['ipeak'] if result['ipeak'] else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No results available yet.</p>
            {% endif %}
        </div>
        
        <div style="margin-top: 30px; text-align: center;">
            <a href="/" style="color: #667eea; text-decoration: none; font-weight: 600;">
                ← Back to Home
            </a>
        </div>
    </div>
</body>
</html>
```

Let me continue with more implementation sections...
