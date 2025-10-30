# Deliverable 1: config_generator.py Implementation Specification

## Overview

**Module**: `config_generator.py`  
**Purpose**: Validate user parameters against Pai Ho's CSV whitelists and generate config.cfg files  
**Lines of Code**: ~400 lines  
**Priority**: P0 (Week 3-4, Core Implementation)  
**Dependencies**: None (foundational module)

## Ground Truth Validation

This specification is validated against **COMPREHENSIVE_ANALYSIS.md**, which documents Pai Ho's proven wkpup2 system.

### Key References from COMPREHENSIVE_ANALYSIS.md:

1. **Configuration System** (Section on Configuration)
   - 15 parameters in config.cfg
   - CSV-driven validation tables
   - Whitelist approach for parameter validation

2. **Parameter Validation** (Recursive Analysis: Configuration System)
   - `table_corner_list.csv`: Defines valid corners
   - `table_supply_list.csv`: Defines voltage combinations
   - `table_supply_list_ac.csv`: AC mode voltages
   - `table_supply_list_dc.csv`: DC mode voltages

3. **15 Parameters** (from config.cfg):
   ```
   mode, vccn, vcctx, 1st_supply_swp, 2nd_supply_swp, 3rd_supply_swp,
   condition, CPU, MEM, alter_extraction, alter_string1, sim_mode,
   gs/gf_corner, vcc_vid, simulator, postlay_cross_cornerlist
   ```

## Functional Requirements

### FR-1: CSV Table Loading

**Function**: Load and parse Pai Ho's validation tables

**Input Files** (from ver03/configuration/):
- `table_corner_list.csv` - Corner definitions
- `table_supply_list.csv` - General voltage combinations  
- `table_supply_list_ac.csv` - AC mode voltages
- `table_supply_list_dc.csv` - DC mode voltages

**Implementation**:
```python
def __init__(self, paiho_script_path: str):
    """
    Initialize with path to Pai Ho's ver03 scripts
    
    Args:
        paiho_script_path: Path to .../auto_pvt/ver03/configuration/
    """
    self.script_path = paiho_script_path
    self.valid_corners = self._load_corners()
    self.valid_voltages = self._load_voltages()
```

**Validation**:
- Must load CSV files from exact paths used by Pai Ho's read_cfg.sh, read_corner.sh, read_supply.sh
- Must preserve CSV structure and relationships
- Must handle missing files gracefully with clear error messages

### FR-2: Parameter Validation

**Function**: Validate ALL parameters against whitelists

**Validation Rules**:

1. **mode**: Must be `'prelay'` or `'postlay'`
2. **vccn**: Must be in `['1p1v', '1p2v', '1p8v', '1p15v']`
3. **corners**: Must ALL be in `table_corner_list.csv`
4. **voltages**: Combination `(1st_supply_swp, 2nd_supply_swp, 3rd_supply_swp)` must exist in appropriate CSV table
5. **condition**: Must be `'perf'`, `'func'`, or `'htol'`
6. **simulator**: Must be `'primesim'` or `'finesim'`
7. **CPU**: Must be positive integer
8. **MEM**: Must be valid memory specification (e.g., '32G')

**Implementation**:
```python
def validate_params(self, params: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate all parameters against whitelists
    
    Args:
        params: Dictionary of user-provided parameters
        
    Returns:
        (is_valid, error_message)
    """
    # Check each parameter against whitelist
    # Return False with specific error message on first failure
    # Return True, None if all validations pass
```

**Key Principle** (from COMPREHENSIVE_ANALYSIS.md):
> "All parameters must be validated against CSV tables"
> 
> "Whitelist validation - only allow CSV-defined values"

### FR-3: Config File Generation

**Function**: Generate config.cfg in Pai Ho's exact format

**Output Format** (must match Pai Ho's read_cfg.sh expectations):
```
mode=prelay
vccn=1p1v
vcctx=1p0v
1st_supply_swp=v1nom
2nd_supply_swp=v2nom
3rd_supply_swp=v3nom
condition=perf
CPU #=16
MEM [G]=32
alter_extraction=0
alter_string#=
sim_mode=ac
gs/gf_corner=1
vcc_vid=0
simulator=primesim
postlay_cross_cornerlist=
```

**Critical Requirements**:
- **Exact format**: Must match Pai Ho's parser expectations
- **No modifications**: Generate EXACTLY what Pai Ho's scripts expect
- **No defaults**: Only write parameters provided by user (with explicit defaults if needed)

**Implementation**:
```python
def generate_config(self, params: Dict, output_path: str) -> bool:
    """
    Generate config.cfg file for Pai Ho's scripts
    
    Args:
        params: Validated parameters
        output_path: Path to write config.cfg
        
    Returns:
        Success status
    """
    # Validate first
    is_valid, error = self.validate_params(params)
    if not is_valid:
        raise ValueError(f"Invalid parameters: {error}")
    
    # Write in Pai Ho's exact format
    # Each parameter on its own line: "key=value\n"
```

### FR-4: Helper Methods

**Function**: Provide UI-friendly access to valid options

```python
def get_valid_corners(self) -> List[str]:
    """Return list of valid corners for UI dropdown"""
    return self.valid_corners

def get_valid_voltages(self, sim_mode: str = 'ac') -> List[Tuple[str, str, str]]:
    """Return list of valid voltage combinations for UI"""
    return self.valid_voltages.get(sim_mode, [])
```

## Non-Functional Requirements

### NFR-1: Zero Modifications to Pai Ho's Core

**Requirement**: This module must NOT modify any Pai Ho files

**Verification**:
- Only reads CSV files, never writes to them
- Generates NEW config.cfg files, doesn't modify existing ones
- No subprocess calls to Pai Ho's scripts (that's paiho_executor.py's job)

### NFR-2: Bit-Identical Config Generation

**Requirement**: Generated config.cfg must be identical to manual creation

**Test**:
```python
def test_bit_identical_config():
    # Manually create config.cfg
    manual_config = create_manual_config()
    
    # Generate via config_generator.py
    generator = PaiHoConfigGenerator(script_path)
    generator.generate_config(params, 'auto_config.cfg')
    
    # Compare
    assert filecmp.cmp('manual_config.cfg', 'auto_config.cfg')
    # Must be byte-for-byte identical
```

### NFR-3: Performance

**Requirement**: Fast parameter validation for responsive UI

**Targets**:
- CSV loading: < 100ms (one-time on init)
- Parameter validation: < 10ms per request
- Config generation: < 50ms per file

## Implementation Structure

### Class Design

```python
#!/usr/bin/env python3
"""
PaiHo Configuration Generator
Validates parameters against CSV whitelists and generates config.cfg files
"""

import os
import csv
from typing import Dict, List, Optional, Tuple

class PaiHoConfigGenerator:
    """
    Generates config.cfg files for Pai Ho's scripts
    All parameters validated against CSV whitelists
    """
    
    def __init__(self, paiho_script_path: str):
        """Initialize with path to Pai Ho's ver03 scripts"""
        
    def _load_corners(self) -> List[str]:
        """Load valid corners from table_corner_list.csv"""
        
    def _load_voltages(self) -> Dict[str, List[str]]:
        """Load valid voltages from table_supply_list*.csv"""
        
    def _load_voltage_csv(self, filename: str) -> List[Tuple[str, str, str]]:
        """Load voltage combinations from specific CSV"""
        
    def validate_params(self, params: Dict) -> Tuple[bool, Optional[str]]:
        """Validate all parameters against whitelists"""
        
    def generate_config(self, params: Dict, output_path: str) -> bool:
        """Generate config.cfg file for Pai Ho's scripts"""
        
    def get_valid_corners(self) -> List[str]:
        """Return list of valid corners for UI"""
        
    def get_valid_voltages(self, sim_mode: str = 'ac') -> List[Tuple[str, str, str]]:
        """Return list of valid voltage combinations for UI"""
```

### Error Handling

```python
class ConfigValidationError(Exception):
    """Raised when parameter validation fails"""
    pass

class ConfigGenerationError(Exception):
    """Raised when config file generation fails"""
    pass
```

## Testing Strategy

### Unit Tests (50+ test cases)

**Test Categories**:

1. **CSV Loading Tests** (10 tests)
   - Valid CSV files load correctly
   - Missing CSV files raise appropriate errors
   - Malformed CSV files handled gracefully
   - Empty CSV files detected
   - Duplicate entries handled

2. **Parameter Validation Tests** (30 tests)
   - Valid parameters pass
   - Invalid mode rejected (e.g., 'invalid_mode')
   - Invalid vccn rejected (e.g., '1p5v')
   - Invalid corner combinations rejected
   - Invalid voltage combinations rejected
   - Missing required parameters detected
   - Extra unknown parameters handled
   - Edge cases (empty strings, None values)

3. **Config Generation Tests** (10 tests)
   - Correct format generated
   - All parameters included
   - Line format matches Pai Ho's expectations
   - File permissions correct
   - Overwrite behavior controlled
   - Special characters handled

4. **Helper Method Tests** (5 tests)
   - get_valid_corners() returns correct list
   - get_valid_voltages() filters by sim_mode correctly
   - Methods handle missing data

### Integration Tests

```python
def test_end_to_end_config_generation():
    """Test complete flow from validation to file generation"""
    generator = PaiHoConfigGenerator('/path/to/ver03')
    
    params = {
        'mode': 'prelay',
        'vccn': '1p1v',
        'vcctx': '1p0v',
        'corners': ['TT', 'FFG', 'SSG'],
        '1st_supply_swp': 'v1nom',
        '2nd_supply_swp': 'v2nom',
        '3rd_supply_swp': 'v3nom',
        'condition': 'perf',
        'CPU': '16',
        'MEM': '32G',
        'sim_mode': 'ac',
        'simulator': 'primesim'
    }
    
    # Should succeed
    assert generator.validate_params(params)[0] == True
    assert generator.generate_config(params, 'test_config.cfg') == True
    
    # Verify file exists and is readable by Pai Ho's scripts
    assert os.path.exists('test_config.cfg')
```

## Verification Checklist

Before considering this deliverable complete, verify:

- [ ] All CSV tables load correctly from Pai Ho's ver03/configuration/
- [ ] All 15 parameters validated against whitelists
- [ ] Generated config.cfg format exactly matches Pai Ho's expectations
- [ ] No Pai Ho files modified (read-only access)
- [ ] All unit tests pass (50+ tests)
- [ ] Integration test passes (end-to-end flow)
- [ ] Code reviewed against COMPREHENSIVE_ANALYSIS.md
- [ ] Performance targets met (< 100ms total)
- [ ] Error messages are clear and actionable
- [ ] Documentation complete (docstrings, comments)

## Implementation Notes

### CSV Table Structure (from COMPREHENSIVE_ANALYSIS.md)

**table_corner_list.csv**:
```csv
type,extraction,corner list
nom_tt,typical,TT
full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG
cross_default,cworst_CCworst_T cbest_CCbest_T,FSG SFG SSG FFG
cross_full,cworst_CCworst_T cbest_CCbest_T,TT FSG SFG FFG FFAG SSG SSAG
```

**table_supply_list.csv** (example):
```csv
1st_supply,2nd_supply,3rd_supply
vcc,NA,NA
vccn,NA,NA
vcc,vcctx,NA
vccn,vcctx,NA
vccana,NA,NA
```

### Parameter Dependencies

Some parameters interact:
- `sim_mode` determines which voltage CSV to use (ac vs dc)
- `mode` (prelay vs postlay) affects extraction options
- `vcc_vid=Yes` requires additional VID voltage tables

These interactions must be handled correctly in validation logic.

## Dependencies

**Python Standard Library**:
- `os` - File path operations
- `csv` - CSV file parsing
- `typing` - Type hints

**External Files** (Pai Ho's ver03):
- `table_corner_list.csv`
- `table_supply_list.csv`
- `table_supply_list_ac.csv`
- `table_supply_list_dc.csv`

**No external Python packages required** - keep it simple and dependency-free.

## Success Criteria

This deliverable is complete when:

1. ✅ All validation logic implemented and tested
2. ✅ Config generation produces Pai Ho-compatible files
3. ✅ All 50+ unit tests pass
4. ✅ Integration test demonstrates end-to-end functionality
5. ✅ Code review confirms alignment with COMPREHENSIVE_ANALYSIS.md
6. ✅ Zero modifications to Pai Ho's files
7. ✅ Performance targets met
8. ✅ Documentation complete

## References

- **ULTIMATE_MASTER_PLAN.md**: Module 1: config_generator.py (~400 lines)
- **COMPREHENSIVE_ANALYSIS.md**: Configuration System, Parameter Validation
- **Ground Truth**: Pai Ho's read_cfg.sh, read_corner.sh, read_supply.sh

## Next Deliverable

After completing config_generator.py:
- **Deliverable 2**: paiho_executor.py - Execute Pai Ho's scripts via subprocess

---

**Status**: Not Started  
**Created**: 2025-10-30  
**Validated Against**: COMPREHENSIVE_ANALYSIS.md (Pai Ho's wkpup2 ground truth)
