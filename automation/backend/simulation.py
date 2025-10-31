"""
Simulation orchestration module
Handles simulation lifecycle: gen, run, extract, sort, backup

REFACTORED: Now uses PaiHoExecutor wrapper to call Pai Ho's original ver03 scripts
instead of custom sim_pvt_local.sh scripts.
"""

import os
import subprocess
import shutil
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path
import logging

# Import configuration
from config import get_voltage_domain_path, get_project_root, REPO_ROOT

# Import PaiHoExecutor wrapper
from paiho_executor import PaiHoExecutor

# Import voltage domain manager
from voltage_domain_manager import (
    ensure_voltage_domain, 
    get_available_voltage_domains
)

# Setup logging
logger = logging.getLogger(__name__)

# Valid PVT corner names
VALID_CORNERS = [
    'TT',       # Typical-Typical
    'FFG',      # Fast-Fast Global
    'SSG',      # Slow-Slow Global
    'FSG',      # Fast-Slow Global
    'SFG',      # Slow-Fast Global
    'FFAG',     # Fast-Fast Alternate Global
    'SSAG',     # Slow-Slow Alternate Global
    'FFG_SSG',  # Mixed corner
    'SSG_FFG',  # Mixed corner
]


def validate_custom_corners(corners: List[str]) -> Dict:
    """
    Validate custom corner selection.
    
    Args:
        corners: List of corner names (e.g., ['TT', 'FFG', 'SSG'])
        
    Returns:
        Dictionary with validation result:
        - valid: bool
        - error: str (if invalid)
        - warning: str (optional)
        - corners: List[str] (if valid)
    """
    if not corners or len(corners) == 0:
        return {'valid': False, 'error': 'No corners selected'}
    
    # Check for invalid corner names
    invalid = [c for c in corners if c not in VALID_CORNERS]
    if invalid:
        return {
            'valid': False, 
            'error': f'Invalid corner names: {", ".join(invalid)}. Valid corners: {", ".join(VALID_CORNERS)}'
        }
    
    # Check for duplicates
    if len(corners) != len(set(corners)):
        duplicates = [c for c in set(corners) if corners.count(c) > 1]
        return {'valid': False, 'error': f'Duplicate corners: {", ".join(duplicates)}'}
    
    # Warning if TT not selected (recommended baseline)
    warning = None
    if 'TT' not in corners:
        warning = 'TT (baseline) not selected - recommended to include for comparison'
    
    result = {'valid': True, 'corners': corners}
    if warning:
        result['warning'] = warning
    
    return result


def generate_sim_id() -> str:
    """Generate unique simulation ID"""
    return f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def create_work_directory(project: str, voltage_domain: str, sim_id: str) -> str:
    """
    Create working directory for simulation.
    Automatically creates voltage domain structure if it doesn't exist.
    
    Args:
        project: "i3c" or "gpio"
        voltage_domain: "1p1v", "1p8v", "0p9v", etc.
        sim_id: Unique simulation ID
        
    Returns:
        Path to working directory
        
    Raises:
        ValueError: If voltage domain is invalid or creation fails
    """
    # Ensure voltage domain exists (creates if needed)
    domain_info = ensure_voltage_domain(project, voltage_domain)
    
    if not domain_info['success']:
        error_msg = domain_info.get('error', 'Unknown error')
        raise ValueError(f"Voltage domain setup failed: {error_msg}")
    
    if domain_info.get('created'):
        print(f"🆕 Created new voltage domain: {voltage_domain} ({domain_info['voltage_value']}V)")
    
    # Use base_path from voltage domain manager
    base_path = domain_info['base_path']
    
    # Create runs directory if it doesn't exist
    runs_dir = os.path.join(base_path, "runs")
    os.makedirs(runs_dir, exist_ok=True)
    
    # Create simulation-specific directory
    work_dir = os.path.join(runs_dir, sim_id)
    os.makedirs(work_dir, exist_ok=True)
    
    print(f"📁 Created work directory: {work_dir}")
    return work_dir


def copy_simulation_files(work_dir: str, project: str, voltage_domain: str, custom_template_path: Optional[str] = None) -> bool:
    """
    Copy ONLY necessary files for Pai Ho's ver03 scripts to work
    
    Per ULTIMATE_MASTER_PLAN.md: Minimal file copying, NO custom scripts
    Pai Ho's sim_pvt.sh only needs:
    1. config.cfg (will be created/modified by update_config_file)
    2. template/ directory with sim_tx.sp circuit netlist
    
    Args:
        work_dir: Working directory path
        project: "i3c" or "gpio"
        voltage_domain: "1p1v"
        custom_template_path: Optional custom path to template directory
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"📋 Setting up work directory for Pai Ho's ver03 scripts...")
    
    # Use repository paths
    source_dir = str(get_voltage_domain_path(project, voltage_domain))
    
    try:
        # Create config.cfg from template (will be modified by update_config_file)
        config_src = os.path.join(source_dir, "config.cfg")
        config_dst = os.path.join(work_dir, "config.cfg")
        
        if os.path.exists(config_src):
            shutil.copy2(config_src, config_dst)
            logger.info(f"  ✓ Copied config.cfg template")
        else:
            # Create minimal config.cfg if not found
            logger.warning(f"  ⚠️ config.cfg not found, will be created by update_config_file")
        
        # Copy template directory (contains circuit netlist sim_tx.sp)
        if custom_template_path and os.path.exists(custom_template_path):
            # Use custom template
            template_dst = os.path.join(work_dir, "template")
            if os.path.exists(custom_template_path):
                shutil.copytree(custom_template_path, template_dst, dirs_exist_ok=True)
                logger.info(f"  ✓ Copied CUSTOM template/ from: {custom_template_path}")
        else:
            # Use default template from source
            template_src = os.path.join(source_dir, "template")
            if os.path.exists(template_src):
                template_dst = os.path.join(work_dir, "template")
                shutil.copytree(template_src, template_dst, dirs_exist_ok=True)
                logger.info(f"  ✓ Copied default template/ directory")
            else:
                logger.error(f"  ❌ template/ directory not found at: {template_src}")
                return False
        
        # NO copying of:
        # - sim_pvt_local.sh (custom, we use PaiHoExecutor now)
        # - local_pvt_loop.sh (custom)  
        # - dependencies/ (huge, referenced from original location)
        # - runme.sh (not needed, we call sim_pvt.sh directly)
        
        logger.info(f"  ✓ Work directory setup complete (minimal files only)")
        return True
        
    except Exception as e:
        logger.exception(f"❌ Error setting up work directory: {e}")
        return False


def update_config_file(work_dir: str, corners: List[str], temperatures: List[str], temp_voltages: Optional[dict] = None,
                      nb_cores: int = 2, nb_memory: int = 2, project: str = 'i3c', voltage_domain: str = '1p1v', voltage_condition: str = 'perf') -> bool:
    """
    Update config.cfg with validated parameters using PaiHoConfigGenerator
    
    REFACTORED: Now validates all inputs against Pai Ho's CSV tables before modification
    
    Args:
        work_dir: Working directory path
        corners: List of corner names (must be in table_corner_list.csv)
        temperatures: List of temperatures (e.g., ['-40', '85', '100', '125'])
        temp_voltages: Dict of per-temp voltage specs
        nb_cores: Number of CPU cores for NetBatch (default: 2)
        nb_memory: Memory in GB for NetBatch (default: 2)
        project: Project name (default: 'i3c')
        voltage_domain: Voltage domain (must be in table_supply_list.csv)
        voltage_condition: Voltage condition (must be func/perf/htol/hvqk)
        
    Returns:
        True if successful
    """
    from config_generator import PaiHoConfigGenerator
    
    config_path = os.path.join(work_dir, "config.cfg")
    
    if not os.path.exists(config_path):
        logger.error(f"❌ config.cfg not found at {config_path}")
        return False
    
    try:
        # Initialize config generator for CSV validation
        generator = PaiHoConfigGenerator(project, voltage_domain, REPO_ROOT)
        
        # Validate corners against table_corner_list.csv
        generator.validate_corners(corners)
        
        # Validate voltage domain (used as vccn)
        generator.validate_voltage_rail(voltage_domain)
        
        # Validate voltage condition
        generator.validate_voltage_condition(voltage_condition)
        
        logger.info(f"✅ All parameters validated against Pai Ho's CSV tables")
        
    except ValueError as e:
        logger.error(f"❌ CSV validation failed: {e}")
        return False
    except Exception as e:
        logger.exception(f"❌ Error during validation: {e}")
        return False
    
    # Read config
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # Use 'perf' condition (performance) - valid voltage condition recognized by read_supply.sh
    # Valid conditions: func, perf, htol, hvqk (NOT 'custom' - that's for corner sets only!)
    condition_value = voltage_condition
    
    # Supply sweep settings remain unchanged (controlled by project config)
    # We don't modify supply_swp settings - they're set per project
    
    # Remove old temp_list and any existing temp_XX_voltages lines
    lines = [line for line in lines if not line.startswith('temp_')]
    
    # Update condition, CPU #, MEM [G], postlay_cross_cornerlist
    updated_condition = False
    updated_cpu = False
    updated_mem = False
    updated_postlay = False
    
    for i, line in enumerate(lines):
        if line.startswith('condition:'):
            lines[i] = f"condition:{condition_value}\n"
            updated_condition = True
        elif line.startswith('CPU #:'):
            lines[i] = f"CPU #:{nb_cores}\n"
            updated_cpu = True
        elif line.startswith('MEM [G]:'):
            lines[i] = f"MEM [G]:{nb_memory}\n"
            updated_mem = True
        elif line.startswith('postlay_cross_cornerlist:'):
            # Keep default value (already in config.cfg template)
            updated_postlay = True
    
    # If postlay_cross_cornerlist doesn't exist, add it at the end
    if not updated_postlay:
        lines.append("postlay_cross_cornerlist:default\n")

    # Add temp_list
    temp_list_line = f"temp_list:{','.join(temperatures)}\n"
    
    # Add per-temperature voltage specifications
    temp_voltage_lines = []
    if temp_voltages:
        for temp in temperatures:
            # Look for temp_XX_voltages in the dict
            volt_key = f"temp_{temp}_voltages"
            if volt_key in temp_voltages:
                voltages = temp_voltages[volt_key]
                temp_voltage_lines.append(f"{volt_key}:{voltages}\n")
            else:
                # Fallback: if no voltage spec, use all 5 dual-supply combinations
                default_voltages = 'v1min_v2min,v1min_v2max,v1max_v2min,v1max_v2max,v1nom_v2nom'
                temp_voltage_lines.append(f"{volt_key}:{default_voltages}\n")
    
    # Insert temp_list and temp voltage lines after condition line
    inserted = False
    for i, line in enumerate(lines):
        if line.startswith('condition:'):
            lines.insert(i + 1, temp_list_line)
            for j, temp_line in enumerate(temp_voltage_lines):
                lines.insert(i + 2 + j, temp_line)
            inserted = True
            break
    
    if not inserted:
        lines.append(temp_list_line)
        lines.extend(temp_voltage_lines)

    # Write updated config
    with open(config_path, 'w') as f:
        f.writelines(lines)
    
    temp_str = ', '.join([f"{t}°C" for t in temperatures])
    volt_summary = ''
    if temp_voltages:
        volt_counts = [len(temp_voltages.get(f"temp_{t}_voltages", '').split(',')) for t in temperatures]
        volt_summary = f", voltages={volt_counts}"
    
    print(f"  ✓ Updated config.cfg: condition={condition_value}, temp_list={temp_str}{volt_summary}, CPU={nb_cores}, MEM={nb_memory}GB")
    
    # Generate custom table_corner_list.csv
    config_dir = os.path.join(work_dir, "configuration")
    os.makedirs(config_dir, exist_ok=True)
    
    corner_list_str = ' '.join(corners)
    
    # Always use typical extraction (no cross extraction in new UI)
    extraction_type = 'typical'
    
    csv_content = "type,extraction,corner list\n"
    csv_content += f"custom,{extraction_type},{corner_list_str}\n"
    
    csv_path = os.path.join(config_dir, "table_corner_list.csv")
    with open(csv_path, 'w') as f:
        f.write(csv_content)
    
    print(f"  ✓ Created custom corner CSV: {corner_list_str}")
    
    # Copy read_corner.sh (same for all corner sets) - use repository path
    source_voltage_domain = str(get_voltage_domain_path(project, voltage_domain))
    source_corner_sh = os.path.join(source_voltage_domain, "configuration", "read_corner.sh")
    
    # Fallback to i3c/1p1v if project-specific doesn't exist
    if not os.path.exists(source_corner_sh):
        source_corner_sh = str(REPO_ROOT / "i3c" / "1p1v" / "configuration" / "read_corner.sh")
    
    if os.path.exists(source_corner_sh):
        shutil.copy(source_corner_sh, os.path.join(config_dir, "read_corner.sh"))
        print(f"  ✓ Copied read_corner.sh")
    
    # Copy voltage configuration files (CRITICAL for correct voltage values)
    voltage_files = [
        'read_supply.sh',
        'table_supply_list.csv',
        'table_supply_list_ac.csv',
        'table_supply_list_dc.csv'
    ]
    
    source_config_dir = os.path.join(source_voltage_domain, "configuration")
    
    for voltage_file in voltage_files:
        source_file = os.path.join(source_config_dir, voltage_file)
        if os.path.exists(source_file):
            shutil.copy(source_file, os.path.join(config_dir, voltage_file))
            print(f"  ✓ Copied {voltage_file}")
        else:
            print(f"  ⚠ Warning: {voltage_file} not found in {source_config_dir}")
            # Try fallback to i3c/1p1v
            fallback_file = str(REPO_ROOT / "i3c" / "1p1v" / "configuration" / voltage_file)
            if os.path.exists(fallback_file):
                shutil.copy(fallback_file, os.path.join(config_dir, voltage_file))
                print(f"  ✓ Copied {voltage_file} from fallback location")
            else:
                raise FileNotFoundError(f"CRITICAL: Missing voltage config file: {voltage_file}")
    
    return True


def run_generation_stage(work_dir: str, project: str = 'gpio', voltage_domain: str = '1p1v') -> bool:
    """
    Run generation stage using PaiHoExecutor wrapper
    Calls Pai Ho's ver03/sim_pvt.sh script with 'gen' stage
    
    Args:
        work_dir: Working directory path containing config.cfg
        project: Project name ('gpio' or 'i3c')
        voltage_domain: Voltage domain (e.g., '1p1v')
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("🔧 Running generation stage (via PaiHoExecutor)...")
    
    try:
        # Initialize PaiHoExecutor with proper paths
        executor = PaiHoExecutor(
            project_root=str(REPO_ROOT),
            project=project,
            voltage_domain=voltage_domain
        )
        
        # Run generation stage: bash ver03/sim_pvt.sh config.cfg gen
        result = executor.run_generation(work_dir=work_dir, config_file='config.cfg')
        
        if result['success']:
            logger.info("  ✓ Generation completed successfully")
            return True
        else:
            logger.error(f"  ❌ Generation failed: {result['stderr'][:200]}")
            return False
        
    except Exception as e:
        logger.exception(f"❌ Generation error: {e}")
        return False


def run_submission_stage(work_dir: str, project: str = 'gpio', voltage_domain: str = '1p1v') -> Optional[str]:
    """
    Run submission stage using PaiHoExecutor wrapper
    Calls Pai Ho's ver03/sim_pvt.sh script with 'run' stage
    
    Args:
        work_dir: Working directory path
        project: Project name ('gpio' or 'i3c')
        voltage_domain: Voltage domain (e.g., '1p1v')
        
    Returns:
        Path to job_log.txt if successful, None otherwise
    """
    logger.info("🚀 Running submission stage (via PaiHoExecutor)...")
    
    try:
        # Initialize PaiHoExecutor
        executor = PaiHoExecutor(
            project_root=str(REPO_ROOT),
            project=project,
            voltage_domain=voltage_domain
        )
        
        # Run submission stage: bash ver03/sim_pvt.sh config.cfg run
        result = executor.run_submission(work_dir=work_dir, config_file='config.cfg')
        
        if result['success']:
            job_log_path = os.path.join(work_dir, "job_log.txt")
            
            if os.path.exists(job_log_path):
                logger.info("  ✓ Submission completed")
                return job_log_path
            else:
                logger.error("❌ job_log.txt not found after submission")
                return None
        else:
            logger.error(f"  ❌ Submission failed: {result['stderr'][:200]}")
            return None
        
    except Exception as e:
        logger.exception(f"❌ Submission error: {e}")
        return None


def run_extraction_stage(work_dir: str, project: str = 'gpio', voltage_domain: str = '1p1v') -> bool:
    """
    Run extraction stage using PaiHoExecutor wrapper
    Calls Pai Ho's ver03/sim_pvt.sh script with 'ext' stage
    
    Args:
        work_dir: Working directory path
        project: Project name ('gpio' or 'i3c')
        voltage_domain: Voltage domain (e.g., '1p1v')
        
    Returns:
        True if successful
    """
    logger.info("📊 Running extraction stage (via PaiHoExecutor)...")
    
    try:
        # Initialize PaiHoExecutor
        executor = PaiHoExecutor(
            project_root=str(REPO_ROOT),
            project=project,
            voltage_domain=voltage_domain
        )
        
        # Run extraction stage: bash ver03/sim_pvt.sh config.cfg ext
        result = executor.run_extraction(work_dir=work_dir, config_file='config.cfg')
        
        if result['success']:
            logger.info("  ✓ Extraction completed")
            return True
        else:
            # Don't fail completely - extraction might partially succeed
            logger.warning(f"  ⚠️ Extraction had warnings: {result['stderr'][:200]}")
            return True  # Allow partial success
        
    except Exception as e:
        logger.exception(f"❌ Extraction error: {e}")
        return False


def run_sorting_stage(work_dir: str, project: str = 'gpio', voltage_domain: str = '1p1v') -> bool:
    """
    Run sorting stage using PaiHoExecutor wrapper
    Calls Pai Ho's ver03/sim_pvt.sh script with 'srt' stage
    
    Args:
        work_dir: Working directory path
        project: Project name ('gpio' or 'i3c')
        voltage_domain: Voltage domain (e.g., '1p1v')
        
    Returns:
        True if successful
    """
    logger.info("📋 Running sorting stage (via PaiHoExecutor)...")
    
    try:
        # Initialize PaiHoExecutor
        executor = PaiHoExecutor(
            project_root=str(REPO_ROOT),
            project=project,
            voltage_domain=voltage_domain
        )
        
        # Run sorting stage: bash ver03/sim_pvt.sh config.cfg srt
        result = executor.run_sorting(work_dir=work_dir, config_file='config.cfg')
        
        if result['success']:
            # Check for creport.txt
            creport_path = os.path.join(work_dir, "report", "creport.txt")
            
            if not os.path.exists(creport_path):
                logger.error(f"❌ creport.txt not created")
                return False
            
            logger.info(f"  ✓ Sorting completed, creport at: {creport_path}")
            return True
        else:
            logger.error(f"  ❌ Sorting failed: {result['stderr'][:200]}")
            return False
        
    except Exception as e:
        logger.exception(f"❌ Sorting error: {e}")
        return False


def run_backup_stage(work_dir: str, project: str = 'gpio', voltage_domain: str = '1p1v') -> Optional[str]:
    """
    Run backup stage using PaiHoExecutor wrapper
    Calls Pai Ho's ver03/sim_pvt.sh script with 'bkp' stage
    
    Args:
        work_dir: Working directory path
        project: Project name ('gpio' or 'i3c')
        voltage_domain: Voltage domain (e.g., '1p1v')
        
    Returns:
        Path to backup directory if successful, None otherwise
    """
    logger.info("💾 Running backup stage (via PaiHoExecutor)...")
    
    try:
        # Initialize PaiHoExecutor
        executor = PaiHoExecutor(
            project_root=str(REPO_ROOT),
            project=project,
            voltage_domain=voltage_domain
        )
        
        # Run backup stage: bash ver03/sim_pvt.sh config.cfg bkp
        result = executor.run_backup(work_dir=work_dir, config_file='config.cfg')
        
        if result['success']:
            # Find backup directory (00bkp_YYYYMMDDHHMM)
            backup_dirs = [d for d in os.listdir(work_dir) if d.startswith('00bkp_')]
            
            if not backup_dirs:
                logger.error(f"❌ No backup directory created in {work_dir}")
                return None
            
            # Get most recent backup
            backup_dir = os.path.join(work_dir, sorted(backup_dirs)[-1])
            
            logger.info(f"  ✓ Backup completed at: {backup_dir}")
            return backup_dir
        else:
            logger.error(f"  ❌ Backup failed: {result['stderr'][:200]}")
            return None
        
    except Exception as e:
        logger.exception(f"❌ Backup error: {e}")
        return None
        return None


def get_simulation_status(sim_id: str) -> str:
    """Get simulation status from database"""
    # Dummy implementation - replace with actual database query
    import sqlite3
    
    conn = sqlite3.connect('simulations.db')
    c = conn.cursor()
    
    # Replace with actual query to get status
    c.execute("SELECT status FROM simulation_table WHERE sim_id = ?", (sim_id,))
    
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "Not Found"


def get_simulation_progress(sim_id: str) -> str:
    """Get simulation progress percentage"""
    # Dummy implementation - replace with actual calculation
    import sqlite3
    
    conn = sqlite3.connect('simulations.db')
    c = conn.cursor()
    
    # Replace with actual query to get progress
    c.execute("SELECT progress FROM simulation_table WHERE sim_id = ?", (sim_id,))
    
    result = c.fetchone()
    conn.close()
    if result:
        return str(result[0])
    else:
        return "0"


def get_simulation_runtime(sim_id: str) -> str:
    """Get simulation runtime"""
    # Dummy implementation - replace with actual calculation
    from datetime import datetime
    import sqlite3
    
    conn = sqlite3.connect('simulations.db')
    c = conn.cursor()
    
    # Replace with actual query to get start and end time
    c.execute("SELECT start_time, end_time FROM simulation_table WHERE sim_id = ?", (sim_id,))
    
    result = c.fetchone()
    conn.close()
    if result and result[0] and result[1]:
        start_time = datetime.fromisoformat(result[0])
        end_time = datetime.fromisoformat(result[1])
        return str(end_time - start_time)
    elif result and result[0]:
        start_time = datetime.fromisoformat(result[0])
        return str(datetime.now() - start_time)
    return "N/A"


def get_simulation_details(sim_id: str) -> str:
    """Get detailed simulation information"""
    # Dummy implementation - replace with actual database query
    import sqlite3
    
    conn = sqlite3.connect('simulations.db')
    c = conn.cursor()
    
    # Replace with actual query to get details
    c.execute("SELECT details FROM simulation_table WHERE sim_id = ?", (sim_id,))
    
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return ""


# Test function
if __name__ == "__main__":
    print("Testing simulation orchestration...")
    sim_id = generate_sim_id()
    print(f"Generated sim_id: {sim_id}")
    
    # Note: Don't actually create directories in test mode
    print("\n✅ Module loaded successfully")
