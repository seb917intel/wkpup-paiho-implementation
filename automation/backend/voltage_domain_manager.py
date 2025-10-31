#!/usr/bin/env python3
"""
Voltage Domain Manager
Dynamically creates and manages voltage domain directories for WKP characterization.

This script:
1. Checks if voltage domain directory exists
2. Creates directory structure if needed
3. Copies and modifies template files for the voltage
4. Returns path information for main workflow

Usage:
    from voltage_domain_manager import ensure_voltage_domain
    
    domain_info = ensure_voltage_domain(
        project='i3c',
        voltage_domain='1p8v'
    )
    
    if domain_info['success']:
        work_dir = domain_info['base_path']
    else:
        print(domain_info['error'])
"""

import os
import shutil
import re
from typing import Dict, Optional
from pathlib import Path

# Import configuration
from config import get_project_root, get_voltage_domain_path


# ============================================
# Voltage Conversion Helpers
# ============================================

def voltage_to_domain_id(voltage: float) -> str:
    """
    Convert voltage value to domain ID.
    
    Examples:
        1.1 → "1p1v"
        1.8 → "1p8v"
        0.9 → "0p9v"
        1.65 → "1p65v"
    
    Args:
        voltage: Voltage value as float
        
    Returns:
        Domain ID string
    """
    voltage_str = str(voltage)
    domain_id = voltage_str.replace('.', 'p') + 'v'
    return domain_id


def domain_id_to_voltage(domain_id: str) -> Optional[float]:
    """
    Convert domain ID to voltage value.
    
    Examples:
        "1p1v" → 1.1
        "1p8v" → 1.8
        "0p9v" → 0.9
        "1p65v" → 1.65
    
    Args:
        domain_id: Domain ID string (e.g., "1p1v")
        
    Returns:
        float voltage value, or None if invalid format
    """
    try:
        if not isinstance(domain_id, str) or not domain_id.endswith('v'):
            return None
        
        # Remove 'v' suffix and replace 'p' with decimal point
        voltage_str = domain_id[:-1].replace('p', '.')
        return float(voltage_str)
    except (ValueError, AttributeError):
        return None


def validate_voltage_input(voltage_input) -> Dict:
    """
    Validate user voltage input.
    
    Args:
        voltage_input: String or number from user input (e.g., "1.1", 1.8, "custom_text")
    
    Returns:
        Dict with validation results:
        {
            'valid': bool,
            'voltage': float (if valid),
            'domain_id': str (if valid),
            'error': str (if invalid)
        }
    """
    # Check empty
    if voltage_input is None or str(voltage_input).strip() == '':
        return {'valid': False, 'error': 'Voltage cannot be empty'}
    
    voltage_str = str(voltage_input).strip()
    
    # Try to parse as float
    try:
        voltage = float(voltage_str)
    except ValueError:
        return {
            'valid': False,
            'error': f'Invalid voltage format: "{voltage_str}". Must be a number (e.g., 1.1, 1.8)'
        }
    
    # Check positive
    if voltage <= 0:
        return {
            'valid': False,
            'error': f'Voltage must be positive (> 0). Got: {voltage}V'
        }
    
    # Check reasonable range (safety)
    if voltage < 0.1:
        return {
            'valid': False,
            'error': f'Voltage too low: {voltage}V. Minimum is 0.1V'
        }
    
    if voltage > 5.0:
        return {
            'valid': False,
            'error': f'Voltage too high: {voltage}V. Maximum is 5.0V for safety'
        }
    
    # Check precision (max 3 decimal places to avoid floating point issues)
    if '.' in voltage_str:
        decimal_places = len(voltage_str.split('.')[-1])
        if decimal_places > 3:
            return {
                'valid': False,
                'error': f'Maximum 3 decimal places allowed. Got: {voltage_str}'
            }
    
    # Generate domain ID
    domain_id = voltage_to_domain_id(voltage)
    
    return {
        'valid': True,
        'voltage': voltage,
        'domain_id': domain_id,
        'error': None
    }


def get_base_path(project: str) -> str:
    """Get base path for project"""
    return str(get_project_root(project))


def validate_voltage_domain(voltage_domain: str) -> bool:
    """
    Check if voltage domain ID is valid format.
    Now accepts ANY voltage (not just predefined).
    
    Args:
        voltage_domain: Domain ID string (e.g., "1p1v", "1p8v", "1p65v")
        
    Returns:
        True if valid format and reasonable voltage value
    """
    # Try to parse voltage from domain ID
    voltage = domain_id_to_voltage(voltage_domain)
    
    if voltage is None:
        return False
    
    # Validate the extracted voltage
    validation = validate_voltage_input(str(voltage))
    return validation['valid']


def get_voltage_value(voltage_domain: str) -> Optional[float]:
    """
    Get voltage value from domain ID.
    Dynamic parsing instead of dictionary lookup.
    
    Args:
        voltage_domain: Domain ID string (e.g., "1p1v")
        
    Returns:
        Voltage value as float, or None if invalid
    """
    return domain_id_to_voltage(voltage_domain)


def voltage_domain_exists(project: str, voltage_domain: str) -> bool:
    """Check if voltage domain directory already exists"""
    base_path = get_base_path(project)
    domain_path = os.path.join(base_path, voltage_domain)
    
    # Check if directory exists and has required structure
    if not os.path.exists(domain_path):
        return False
    
    # Verify required files/directories exist (based on Pai Ho implementation)
    required_items = [
        'config.cfg',
        'runme.sh',
        'template'
    ]
    
    # Optional items (may or may not exist)
    optional_items = [
        'dependencies',
        'configuration'
    ]
    
    for item in required_items:
        item_path = os.path.join(domain_path, item)
        if not os.path.exists(item_path):
            return False
    
    return True


def create_voltage_domain_directory(project: str, voltage_domain: str) -> Dict:
    """
    Create voltage domain directory structure from 1p1v template.
    
    Args:
        project: Project name (i3c or gpio)
        voltage_domain: Voltage domain ID (e.g., 1p8v, 0p9v, 1p65v)
        
    Returns:
        Dict with success status and path information
    """
    # Parse voltage from domain ID
    voltage_value = domain_id_to_voltage(voltage_domain)
    
    if voltage_value is None:
        return {
            'success': False,
            'error': f"Invalid voltage domain format: {voltage_domain}. Expected format like '1p1v', '1p8v', etc."
        }
    
    # Validate voltage value
    validation = validate_voltage_input(str(voltage_value))
    if not validation['valid']:
        return {
            'success': False,
            'error': f"Invalid voltage: {validation['error']}"
        }
    
    base_path = get_base_path(project)
    source_domain = os.path.join(base_path, '1p1v')  # Use 1p1v as template
    target_domain = os.path.join(base_path, voltage_domain)
    
    # Check if source exists
    if not os.path.exists(source_domain):
        return {
            'success': False,
            'error': f"Source template not found: {source_domain}"
        }
    
    # Check if target already exists
    if os.path.exists(target_domain):
        return {
            'success': False,
            'error': f"Voltage domain already exists: {target_domain}. Use existing domain."
        }
    
    try:
        print(f"📁 Creating voltage domain: {voltage_domain} ({voltage_value}V)")
        
        # Create main directory structure
        os.makedirs(target_domain, exist_ok=True)
        os.makedirs(os.path.join(target_domain, 'template'), exist_ok=True)
        os.makedirs(os.path.join(target_domain, 'configuration'), exist_ok=True)
        os.makedirs(os.path.join(target_domain, 'runs'), exist_ok=True)
        
        print(f"  ✓ Created directory structure")
        
        # Copy and modify config.cfg
        source_config = os.path.join(source_domain, 'config.cfg')
        target_config = os.path.join(target_domain, 'config.cfg')
        modify_config_file(source_config, target_config, voltage_domain)
        print(f"  ✓ Created config.cfg with vccn:{voltage_domain}")
        
        # Copy shell scripts (no modification needed)
        scripts = [
            'sim_pvt_local.sh',
            'local_extract.sh',
            'local_move.sh',
            'runme_local.sh'
        ]
        
        for script in scripts:
            source_file = os.path.join(source_domain, script)
            target_file = os.path.join(target_domain, script)
            if os.path.exists(source_file):
                shutil.copy2(source_file, target_file)
        
        print(f"  ✓ Copied shell scripts")
        
        # Copy and modify template files
        source_template = os.path.join(source_domain, 'template')
        target_template = os.path.join(target_domain, 'template')
        
        for filename in os.listdir(source_template):
            source_file = os.path.join(source_template, filename)
            target_file = os.path.join(target_template, filename)
            
            if os.path.isfile(source_file):
                # Check if file needs voltage modification
                if filename.endswith('.sp') or filename.endswith('.scs'):
                    modify_spice_template(source_file, target_file, voltage_domain, voltage_value)
                else:
                    shutil.copy2(source_file, target_file)
        
        print(f"  ✓ Created templates with .param vcn={voltage_value}")
        
        # Copy configuration files
        source_config_dir = os.path.join(source_domain, 'configuration')
        target_config_dir = os.path.join(target_domain, 'configuration')
        
        if os.path.exists(source_config_dir):
            for filename in os.listdir(source_config_dir):
                source_file = os.path.join(source_config_dir, filename)
                target_file = os.path.join(target_config_dir, filename)
                if os.path.isfile(source_file):
                    shutil.copy2(source_file, target_file)
        
        print(f"  ✓ Copied configuration files")
        
        return {
            'success': True,
            'message': f"Created voltage domain: {voltage_domain} ({voltage_value}V)",
            'base_path': target_domain,
            'voltage_value': voltage_value,
            'created': True
        }
        
    except Exception as e:
        # Clean up partial creation
        if os.path.exists(target_domain):
            shutil.rmtree(target_domain)
        
        return {
            'success': False,
            'error': f"Failed to create voltage domain: {str(e)}"
        }


def modify_config_file(source_path: str, target_path: str, voltage_domain: str):
    """
    Modify config.cfg to use new voltage domain.
    
    Changes:
        vccn:1p1v → vccn:{voltage_domain}
    """
    with open(source_path, 'r') as f:
        content = f.read()
    
    # Replace voltage domain identifier
    content = re.sub(r'vccn:1p1v', f'vccn:{voltage_domain}', content)
    
    with open(target_path, 'w') as f:
        f.write(content)


def modify_spice_template(source_path: str, target_path: str, voltage_domain: str, voltage_value: float):
    """
    Modify SPICE template files to use new voltage.
    
    Changes:
        .param vcn=1.1 → .param vcn={voltage_value}
        .param vsh="vcn*0.35/1.1" → .param vsh="vcn*0.35/{voltage_value}"
    """
    with open(source_path, 'r') as f:
        content = f.read()
    
    # Replace vcn parameter
    content = re.sub(r'\.param\s+vcn\s*=\s*1\.1', f'.param vcn={voltage_value}', content)
    
    # Replace vsh scaling factor (if exists)
    content = re.sub(r'vcn\*0\.35/1\.1', f'vcn*0.35/{voltage_value}', content)
    
    # Replace any other 1.1 references in voltage context
    # Be careful not to replace unrelated 1.1 values
    # This pattern looks for 1.1 in voltage-related contexts
    content = re.sub(r'(vccn.*?)1\.1', rf'\g<1>{voltage_value}', content, flags=re.IGNORECASE)
    
    with open(target_path, 'w') as f:
        f.write(content)


def ensure_voltage_domain(project: str, voltage_domain: str) -> Dict:
    """
    Ensure voltage domain exists. Create if needed, return path if exists.
    
    This is the main entry point for the voltage domain manager.
    
    Args:
        project: Project name (i3c or gpio)
        voltage_domain: Voltage domain ID (e.g., 1p1v, 1p8v, 1p65v)
        
    Returns:
        Dict with:
            - success: True if domain is ready
            - base_path: Path to voltage domain directory
            - voltage_value: Actual voltage value
            - created: True if newly created, False if already existed
            - error: Error message if failed
    """
    # Parse and validate voltage
    voltage_value = domain_id_to_voltage(voltage_domain)
    
    if voltage_value is None:
        return {
            'success': False,
            'error': f"Invalid voltage domain format: {voltage_domain}. Expected format like '1p1v', '1p8v', etc."
        }
    
    validation = validate_voltage_input(str(voltage_value))
    if not validation['valid']:
        return {
            'success': False,
            'error': f"Invalid voltage: {validation['error']}"
        }
    
    # Check if exists
    if voltage_domain_exists(project, voltage_domain):
        base_path = os.path.join(get_base_path(project), voltage_domain)
        
        print(f"✓ Voltage domain exists: {voltage_domain} ({voltage_value}V) at {base_path}")
        
        return {
            'success': True,
            'message': f"Using existing voltage domain: {voltage_domain}",
            'base_path': base_path,
            'voltage_value': voltage_value,
            'created': False
        }
    
    # Create new voltage domain
    print(f"ℹ️ Voltage domain {voltage_domain} does not exist. Creating...")
    return create_voltage_domain_directory(project, voltage_domain)


def get_available_voltage_domains(project: str) -> list:
    """
    Get list of available voltage domains for a project by scanning filesystem.
    
    Returns list of dicts with domain information for all existing voltage domains.
    """
    available = []
    base_path = get_base_path(project)
    
    # Check if base path exists
    if not os.path.exists(base_path):
        return available
    
    # Scan directory for voltage domain folders
    try:
        for entry in os.listdir(base_path):
            entry_path = os.path.join(base_path, entry)
            
            # Check if it's a directory and matches voltage domain pattern
            if os.path.isdir(entry_path) and entry.endswith('v'):
                # Try to parse voltage from directory name
                voltage_value = domain_id_to_voltage(entry)
                
                if voltage_value is not None:
                    # Validate that it's a proper voltage domain directory
                    # (has config.cfg and template/ subdirectory)
                    config_file = os.path.join(entry_path, 'config.cfg')
                    template_dir = os.path.join(entry_path, 'template')
                    
                    if os.path.exists(config_file) and os.path.isdir(template_dir):
                        available.append({
                            'id': entry,
                            'voltage': voltage_value,
                            'label': f"{voltage_value}V Domain",
                            'description': f"Voltage domain at {voltage_value}V",
                            'exists': True,
                            'path': entry_path
                        })
    except Exception as e:
        print(f"Warning: Error scanning voltage domains: {e}")
    
    # Sort by voltage value
    available.sort(key=lambda x: x['voltage'])
    
    return available


def list_voltage_domains(project: str):
    """Print available voltage domains (for CLI usage)"""
    print(f"\n📊 Voltage Domains for {project.upper()}:\n")
    
    domains = get_available_voltage_domains(project)
    
    for domain in domains:
        status = "✅ Exists" if domain['exists'] else "❌ Not created"
        print(f"  {domain['id']:6s} | {domain['voltage']:4.1f}V | {domain['label']:25s} | {status}")
    
    print()


# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
Voltage Domain Manager

Usage:
    python voltage_domain_manager.py list <project>
    python voltage_domain_manager.py create <project> <voltage_domain>
    python voltage_domain_manager.py check <project> <voltage_domain>

Examples:
    python voltage_domain_manager.py list i3c
    python voltage_domain_manager.py create i3c 1p8v
    python voltage_domain_manager.py check i3c 1p1v
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        project = sys.argv[2] if len(sys.argv) > 2 else 'i3c'
        list_voltage_domains(project)
    
    elif command == 'create':
        if len(sys.argv) < 4:
            print("Error: Missing arguments. Usage: create <project> <voltage_domain>")
            sys.exit(1)
        
        project = sys.argv[2]
        voltage_domain = sys.argv[3]
        
        result = ensure_voltage_domain(project, voltage_domain)
        
        if result['success']:
            print(f"\n✅ {result['message']}")
            print(f"   Path: {result['base_path']}")
            print(f"   Voltage: {result['voltage_value']}V")
        else:
            print(f"\n❌ Error: {result['error']}")
            sys.exit(1)
    
    elif command == 'check':
        if len(sys.argv) < 4:
            print("Error: Missing arguments. Usage: check <project> <voltage_domain>")
            sys.exit(1)
        
        project = sys.argv[2]
        voltage_domain = sys.argv[3]
        
        exists = voltage_domain_exists(project, voltage_domain)
        
        if exists:
            base_path = os.path.join(get_base_path(project), voltage_domain)
            voltage_value = get_voltage_value(voltage_domain)
            print(f"✅ Voltage domain exists: {voltage_domain} ({voltage_value}V)")
            print(f"   Path: {base_path}")
        else:
            print(f"❌ Voltage domain does not exist: {voltage_domain}")
            print(f"   Run: python voltage_domain_manager.py create {project} {voltage_domain}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
