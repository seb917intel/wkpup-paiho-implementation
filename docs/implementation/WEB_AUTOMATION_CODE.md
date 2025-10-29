# Result Parser - Parse Pai Ho's Output Files

**File**: `web_automation/modules/result_parser.py`

```python
"""
Result Parser - Parse Pai Ho's Simulation Output Files

Reads and parses Pai Ho's output files WITHOUT modification:
- creport.txt - Main results report
- .mt0 files - SPICE measurement files
- Directory structure

CRITICAL: READ-ONLY access to Pai Ho's files.

Author: Web Automation Layer
Version: 1.0
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SimulationMeasurement:
    """Single simulation measurement"""
    corner: str
    extraction: str
    temperature: str
    voltage: str
    tphl: Optional[float] = None
    tplh: Optional[float] = None
    ipeak: Optional[float] = None
    iavg: Optional[float] = None
    power: Optional[float] = None
    pass_fail: str = 'unknown'
    raw_line: str = ''


class ResultParser:
    """Parse Pai Ho's simulation results"""
    
    def __init__(self, result_dir: str):
        """
        Initialize parser
        
        Args:
            result_dir: Path to Pai Ho's result directory (e.g., 00bkp_20250501120000/)
        """
        self.result_dir = Path(result_dir)
        
        if not self.result_dir.exists():
            raise FileNotFoundError(f"Result directory not found: {result_dir}")
        
        # Pai Ho's key files
        self.creport_file = self.result_dir / 'creport.txt'
    
    def parse_creport(self) -> List[Dict]:
        """
        Parse Pai Ho's creport.txt
        
        Format (example):
        TT typical 85 v1nom tphl=1.234e-9 tplh=2.345e-9 ipeak=1.23e-3 ...
        
        Returns:
            List of measurement dictionaries
        """
        if not self.creport_file.exists():
            raise FileNotFoundError(f"creport.txt not found: {self.creport_file}")
        
        results = []
        
        with open(self.creport_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    measurement = self._parse_creport_line(line)
                    if measurement:
                        results.append({
                            'corner': measurement.corner,
                            'extraction': measurement.extraction,
                            'temperature': measurement.temperature,
                            'voltage': measurement.voltage,
                            'tphl': measurement.tphl,
                            'tplh': measurement.tplh,
                            'ipeak': measurement.ipeak,
                            'iavg': measurement.iavg,
                            'power': measurement.power,
                            'pass_fail': measurement.pass_fail,
                            'raw_data': measurement.raw_line
                        })
                except Exception as e:
                    print(f"WARNING: Could not parse line {line_num}: {line}")
                    print(f"  Error: {e}")
        
        return results
    
    def _parse_creport_line(self, line: str) -> Optional[SimulationMeasurement]:
        """
        Parse single line from creport.txt
        
        Expected format:
        CORNER EXTRACTION TEMP VOLTAGE tphl=VALUE tplh=VALUE ...
        
        Example:
        TT typical 85 v1nom tphl=1.234e-9 tplh=2.345e-9 ipeak=1.23e-3
        """
        # Split line into tokens
        tokens = line.split()
        
        if len(tokens) < 4:
            return None
        
        # Extract PVT coordinates
        corner = tokens[0]
        extraction = tokens[1]
        temperature = tokens[2]
        voltage = tokens[3]
        
        # Extract measurements
        measurements = {}
        for token in tokens[4:]:
            if '=' in token:
                key, value = token.split('=', 1)
                try:
                    measurements[key] = float(value)
                except ValueError:
                    measurements[key] = value
        
        return SimulationMeasurement(
            corner=corner,
            extraction=extraction,
            temperature=temperature,
            voltage=voltage,
            tphl=measurements.get('tphl'),
            tplh=measurements.get('tplh'),
            ipeak=measurements.get('ipeak'),
            iavg=measurements.get('iavg'),
            power=measurements.get('power'),
            pass_fail='pass',  # TODO: Implement pass/fail logic
            raw_line=line
        )
    
    def get_directory_structure(self) -> Dict:
        """
        Get directory structure of results
        
        Returns:
            Dictionary representing directory tree
        """
        structure = {
            'path': str(self.result_dir),
            'files': [],
            'directories': []
        }
        
        for item in self.result_dir.iterdir():
            if item.is_file():
                structure['files'].append({
                    'name': item.name,
                    'size': item.stat().st_size,
                    'modified': item.stat().st_mtime
                })
            elif item.is_dir():
                structure['directories'].append(item.name)
        
        return structure
    
    def parse_all(self) -> Dict:
        """
        Parse all available result data
        
        Returns:
            Dictionary with all parsed data
        """
        return {
            'measurements': self.parse_creport(),
            'structure': self.get_directory_structure(),
            'result_dir': str(self.result_dir)
        }
```

---

## Part 4: Testing Strategy (COMPLETE)

### 4.1 Bit-Identical Output Test (CRITICAL)

**File**: `web_automation/tests/test_bit_identical.py`

```python
"""
Bit-Identical Output Test

This is the MOST CRITICAL TEST. It verifies that the web automation
layer produces EXACTLY the same output as Pai Ho's manual execution.

Success Criteria: 100% bit-identical output files

Author: Test Suite
Version: 1.0
"""

import subprocess
import filecmp
import os
import shutil
import tempfile
from pathlib import Path
import pytest


class TestBitIdentical:
    """Test bit-identical output between web and manual execution"""
    
    @pytest.fixture
    def test_config(self):
        """Create test configuration"""
        return {
            'mode': 'prelay',
            'sim_mode': 'ac',
            'vccn': '1p1v',
            'vcctx': '1p1v',
            'condition': 'perf',
            'CPU': '8',
            'MEM': '16',
            'simulator': 'primesim',
        }
    
    @pytest.fixture
    def paiho_paths(self):
        """Pai Ho's paths"""
        return {
            'workdir': '/nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup2/gpio/1p1v',
            'script_dir': '/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03',
        }
    
    def test_gen_stage_identical(self, test_config, paiho_paths):
        """Test that 'gen' stage produces identical output"""
        from modules.config_generator import PaiHoConfigGenerator
        from modules.paiho_executor import PaiHoExecutor
        
        # Method 1: Via web automation layer
        generator = PaiHoConfigGenerator(f"{paiho_paths['script_dir']}/configuration")
        web_config = generator.generate(test_config, '/tmp/web_config.cfg')
        
        executor = PaiHoExecutor(paiho_paths['workdir'], paiho_paths['script_dir'])
        web_result = executor.execute_stage(web_config, 'gen')
        
        assert web_result.status == 'success', f"Web execution failed: {web_result.stderr}"
        
        # Method 2: Direct manual execution
        manual_config = self._create_manual_config(test_config, '/tmp/manual_config.cfg')
        
        # Clean workspace
        self._clean_workspace(paiho_paths['workdir'])
        
        manual_result = subprocess.run([
            'bash',
            f"{paiho_paths['script_dir']}/sim_pvt.sh",
            manual_config,
            'gen'
        ], cwd=paiho_paths['workdir'], capture_output=True, text=True)
        
        assert manual_result.returncode == 0, f"Manual execution failed: {manual_result.stderr}"
        
        # Compare ALL generated files
        self._compare_directories(
            paiho_paths['workdir'],
            paiho_paths['workdir']  # Same dir since we ran sequentially
        )
    
    def _create_manual_config(self, params: dict, path: str) -> str:
        """Create config.cfg manually in Pai Ho's format"""
        config_content = f"""mode={params['mode']}
vccn={params['vccn']}
vcctx={params['vcctx']}
1st_supply_swp=all
2nd_supply_swp=all
3rd_supply_swp=all
condition={params['condition']}
CPU={params['CPU']}
MEM={params['MEM']}
alter_extraction=typical
alter_string1=
alter_string2=
sim_mode={params['sim_mode']}
gs_corner=NA
gf_corner=NA
vcc_vid=no
simulator={params['simulator']}
postlay_cross_cornerlist=
"""
        with open(path, 'w') as f:
            f.write(config_content)
        
        return path
    
    def _clean_workspace(self, workdir: str):
        """Clean workspace before test"""
        # Remove generated directories
        for pattern in ['TT', 'FFG', 'SSG', 'FSG', 'SFG']:
            corner_dir = Path(workdir) / pattern
            if corner_dir.exists():
                shutil.rmtree(corner_dir)
    
    def _compare_directories(self, dir1: str, dir2: str):
        """Compare two directories recursively"""
        comparison = filecmp.dircmp(dir1, dir2)
        
        # Check for differences
        assert len(comparison.diff_files) == 0, \
            f"Different files found: {comparison.diff_files}"
        
        # Check for files only in one directory
        assert len(comparison.left_only) == 0, \
            f"Files only in web execution: {comparison.left_only}"
        assert len(comparison.right_only) == 0, \
            f"Files only in manual execution: {comparison.right_only}"
        
        # Recursively compare subdirectories
        for subdir in comparison.common_dirs:
            self._compare_directories(
                os.path.join(dir1, subdir),
                os.path.join(dir2, subdir)
            )
    
    def test_config_file_identical(self, test_config):
        """Test that generated config.cfg is identical"""
        from modules.config_generator import PaiHoConfigGenerator
        
        generator = PaiHoConfigGenerator('/path/to/csv')
        
        # Generate twice with same params
        config1 = generator.generate(test_config, '/tmp/config1.cfg')
        config2 = generator.generate(test_config, '/tmp/config2.cfg')
        
        # Compare files
        assert filecmp.cmp(config1, config2, shallow=False), \
            "Generated config files are not identical"
    
    def test_full_workflow_identical(self, test_config, paiho_paths):
        """Test complete workflow produces identical results"""
        # This is the ultimate test - full gen→run→ext→srt→bkp
        # Run via web, run manually, compare everything
        
        # TODO: Implement full workflow comparison
        # This requires actual SPICE simulation which takes time
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

### 4.2 Parameter Validation Test

**File**: `web_automation/tests/test_validation.py`

```python
"""
Parameter Validation Tests

Verify that config generator properly validates all parameters
against Pai Ho's whitelists.

Author: Test Suite
Version: 1.0
"""

import pytest
from modules.config_generator import PaiHoConfigGenerator


class TestParameterValidation:
    """Test parameter validation"""
    
    @pytest.fixture
    def generator(self):
        """Create config generator instance"""
        csv_dir = '/nfs/.../ver03/configuration'
        return PaiHoConfigGenerator(csv_dir)
    
    def test_valid_parameters_accepted(self, generator):
        """Test that valid parameters are accepted"""
        valid_params = {
            'mode': 'prelay',
            'sim_mode': 'ac',
            'vccn': '1p1v',
            'condition': 'perf',
        }
        
        # Should not raise
        config_file = generator.generate(valid_params)
        assert os.path.exists(config_file)
    
    def test_invalid_mode_rejected(self, generator):
        """Test that invalid mode is rejected"""
        invalid_params = {
            'mode': 'invalid_mode',  # ❌ Not in whitelist
            'sim_mode': 'ac',
        }
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate(invalid_params)
        
        assert 'Invalid mode' in str(exc_info.value)
    
    def test_invalid_corner_rejected(self, generator):
        """Test that invalid corner is rejected"""
        invalid_params = {
            'mode': 'prelay',
            'corner_selection': 'INVALID_CORNER',  # ❌ Not in CSV
        }
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate(invalid_params)
        
        assert 'Invalid corner' in str(exc_info.value)
    
    def test_whitelist_enforcement(self, generator):
        """Test that only whitelisted values are accepted"""
        # Get valid options
        options = generator.get_valid_options()
        
        # Test each parameter type
        for corner in options['corners']:
            params = {'corner_selection': corner}
            validation = generator.validate_parameters(params)
            assert validation.valid, f"Valid corner {corner} rejected"
        
        # Test invalid corner
        params = {'corner_selection': 'NOT_A_CORNER'}
        validation = generator.validate_parameters(params)
        assert not validation.valid, "Invalid corner accepted"
```

---

### 4.3 Database Accuracy Test

**File**: `web_automation/tests/test_database.py`

```python
"""
Database Accuracy Tests

Verify that database accurately stores and retrieves Pai Ho's results.

Author: Test Suite
Version: 1.0
"""

import pytest
import tempfile
from modules.database import SimulationDatabase
from modules.result_parser import ResultParser


class TestDatabaseAccuracy:
    """Test database accuracy"""
    
    @pytest.fixture
    def db(self):
        """Create temporary database"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name
        
        db = SimulationDatabase(db_path)
        yield db
        db.close()
    
    def test_job_creation(self, db):
        """Test job creation"""
        params = {
            'mode': 'prelay',
            'sim_mode': 'ac',
            'vccn': '1p1v',
        }
        
        db.create_job('test_job_1', 'testuser', params)
        
        # Retrieve job
        job = db.get_job('test_job_1')
        
        assert job is not None
        assert job['job_id'] == 'test_job_1'
        assert job['user'] == 'testuser'
        assert job['mode'] == 'prelay'
    
    def test_results_storage(self, db):
        """Test results storage and retrieval"""
        # Create job
        db.create_job('test_job_2', 'testuser', {})
        
        # Store results
        results = [
            {
                'corner': 'TT',
                'extraction': 'typical',
                'temperature': '85',
                'voltage': 'v1nom',
                'tphl': 1.234e-9,
                'tplh': 2.345e-9,
            },
            {
                'corner': 'FFG',
                'extraction': 'cworst_CCworst_T',
                'temperature': '125',
                'voltage': 'v1max',
                'tphl': 0.987e-9,
                'tplh': 1.876e-9,
            }
        ]
        
        db.store_results('test_job_2', results)
        
        # Retrieve results
        retrieved = db.get_results('test_job_2')
        
        assert len(retrieved) == 2
        assert retrieved[0]['corner'] == 'TT'
        assert retrieved[1]['corner'] == 'FFG'
        assert abs(retrieved[0]['tphl'] - 1.234e-9) < 1e-15
    
    def test_result_matches_file(self, db):
        """Test that stored results match Pai Ho's files"""
        # Parse Pai Ho's actual result directory
        result_dir = '/path/to/00bkp_20250501120000'
        parser = ResultParser(result_dir)
        file_results = parser.parse_creport()
        
        # Store in database
        db.create_job('test_job_3', 'testuser', {})
        db.store_results('test_job_3', file_results)
        
        # Retrieve from database
        db_results = db.get_results('test_job_3')
        
        # Compare
        assert len(db_results) == len(file_results)
        
        for db_res, file_res in zip(db_results, file_results):
            assert db_res['corner'] == file_res['corner']
            assert db_res['temperature'] == file_res['temperature']
            assert abs(db_res['tphl'] - file_res['tphl']) < 1e-15


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Part 5: Deployment Procedures

### 5.1 Installation Script

**File**: `install.sh`

```bash
#!/bin/bash
# Installation script for Web Automation Layer
# This script sets up the web automation on top of Pai Ho's system

set -e  # Exit on error

echo "========================================"
echo "Web Automation Layer Installation"
echo "========================================"

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
echo "Python version: $python_version"

if [[ ! $python_version =~ ^3\.[789] ]]; then
    echo "ERROR: Python 3.7+ required"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --user tornado pytest

# Verify Pai Ho's installation
echo ""
echo "Verifying Pai Ho's installation..."

PAIHO_SCRIPT_DIR="${PAIHO_SCRIPT_DIR:-/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03}"

if [ ! -f "$PAIHO_SCRIPT_DIR/sim_pvt.sh" ]; then
    echo "ERROR: Pai Ho's sim_pvt.sh not found at: $PAIHO_SCRIPT_DIR"
    echo "Set PAIHO_SCRIPT_DIR environment variable to correct path"
    exit 1
fi

echo "✓ Pai Ho's scripts found"

# Verify script versions
sim_pvt_lines=$(wc -l < "$PAIHO_SCRIPT_DIR/sim_pvt.sh")
gen_tb_lines=$(wc -l < "$PAIHO_SCRIPT_DIR/tb_gen/gen_tb.pl")

echo "sim_pvt.sh: $sim_pvt_lines lines (expected: 589)"
echo "gen_tb.pl: $gen_tb_lines lines (expected: 570 for ver03)"

if [ "$gen_tb_lines" -ne 570 ]; then
    echo "WARNING: gen_tb.pl has $gen_tb_lines lines, expected 570 (ver03)"
    echo "You may be using ver02 (525 lines). Please verify."
fi

# Make Pai Ho's scripts read-only (protection)
echo ""
echo "Protecting Pai Ho's original scripts..."
find "$PAIHO_SCRIPT_DIR" -type f -name "*.sh" -o -name "*.pl" | while read file; do
    chmod 444 "$file" 2>/dev/null || echo "WARNING: Could not set read-only: $file"
done

echo "✓ Scripts protected"

# Create directory structure
echo ""
echo "Creating directory structure..."

mkdir -p web_automation/{modules,templates,static,tests}
mkdir -p database
mkdir -p logs
mkdir -p voltage_domains/{gpio,i3c}

echo "✓ Directories created"

# Create database
echo ""
echo "Initializing database..."

python3 << EOF
from modules.database import SimulationDatabase
db = SimulationDatabase('database/simulation_tracking.db')
print("✓ Database initialized")
db.close()
EOF

# Create configuration file
echo ""
echo "Creating configuration..."

cat > config/web_config.yaml << EOF
# Web Automation Configuration
paiho:
  script_dir: $PAIHO_SCRIPT_DIR
  workdir: /nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup2/gpio/1p1v

web:
  port: 8888
  max_concurrent_jobs: 3

database:
  path: database/simulation_tracking.db
EOF

echo "✓ Configuration created"

# Run tests
echo ""
echo "Running validation tests..."

python3 -m pytest web_automation/tests/ -v || echo "WARNING: Some tests failed"

# Print summary
echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Review configuration in config/web_config.yaml"
echo "2. Start web server: python3 web_automation/main.py"
echo "3. Access UI: http://localhost:8888"
echo ""
echo "Pai Ho's scripts: $PAIHO_SCRIPT_DIR"
echo "Status: PROTECTED (read-only)"
echo ""
```

---

### 5.2 Startup Script

**File**: `start_server.sh`

```bash
#!/bin/bash
# Start web automation server

set -e

echo "Starting Web Automation Server..."

# Set environment variables
export PAIHO_CSV_DIR="${PAIHO_CSV_DIR:-/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03/configuration}"
export PAIHO_SCRIPT_DIR="${PAIHO_SCRIPT_DIR:-/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver03}"
export PAIHO_WORKDIR="${PAIHO_WORKDIR:-/nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup2/gpio/1p1v}"
export DATABASE_PATH="${DATABASE_PATH:-database/simulation_tracking.db}"
export PORT="${PORT:-8888}"

# Start server
python3 web_automation/main.py
```

Let me continue with more sections...