#!/usr/bin/env python3
"""
Config Generator with CSV Validation
Validates simulation parameters against Pai Ho's CSV tables before generating config.cfg

Per ULTIMATE_MASTER_PLAN.md:
- Load table_corner_list.csv for corner validation
- Load table_supply_list.csv for voltage validation
- Whitelist validation before config generation
- Generate config.cfg matching Pai Ho's exact format
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class PaiHoConfigGenerator:
    """
    Generates and validates config.cfg files against Pai Ho's CSV tables
    
    Ensures all parameters match Pai Ho's validated configurations from:
    - table_corner_list.csv: Valid PVT corner combinations
    - table_supply_list.csv: Valid voltage rail configurations
    """
    
    def __init__(self, project: str, voltage_domain: str, repo_root: Path):
        """
        Initialize config generator with CSV table loading
        
        Args:
            project: 'gpio' or 'i3c'
            voltage_domain: e.g., '1p1v', '1p2v'
            repo_root: Repository root path
        """
        self.project = project
        self.voltage_domain = voltage_domain
        self.repo_root = Path(repo_root)
        
        # Path to ver03 configuration CSVs
        self.config_path = (self.repo_root / project / voltage_domain / 
                           "dependencies/scripts/simulation_script/auto_pvt/ver03/configuration")
        
        # Load CSV tables
        self.corner_table = self._load_corner_table()
        self.supply_table = self._load_supply_table()
        
        logger.info(f"ConfigGenerator initialized for {project}/{voltage_domain}")
        logger.info(f"Loaded {len(self.corner_table)} corner configurations")
        logger.info(f"Loaded {len(self.supply_table)} supply configurations")
    
    def _load_corner_table(self) -> Dict[str, Dict]:
        """
        Load table_corner_list.csv
        
        Format:
        type,extraction,corner list
        nom_tt,typical,TT
        full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG
        ...
        
        Returns:
            Dict mapping type to {extraction, corners}
        """
        csv_file = self.config_path / "table_corner_list.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(f"Corner table not found: {csv_file}")
        
        corner_table = {}
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                corner_type = row['type']
                corner_table[corner_type] = {
                    'extraction': row['extraction'],
                    'corners': row['corner list'].split()
                }
        
        return corner_table
    
    def _load_supply_table(self) -> Dict[str, Dict]:
        """
        Load table_supply_list.csv
        
        Format:
        rail,func_min,perf_min,nom,perf_max,func_max,htol,hvqk
        vcc,0.68,0.69,0.78,0.88,0.89,0.945,1.6
        1p1v,0.98,0.99,1.1,1.188,,1.246,1.65
        ...
        
        Returns:
            Dict mapping rail name to voltage values
        """
        csv_file = self.config_path / "table_supply_list.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(f"Supply table not found: {csv_file}")
        
        supply_table = {}
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rail = row['rail']
                supply_table[rail] = {
                    'func_min': row['func_min'],
                    'perf_min': row['perf_min'],
                    'nom': row['nom'],
                    'perf_max': row['perf_max'],
                    'func_max': row['func_max'],
                    'htol': row['htol'],
                    'hvqk': row['hvqk']
                }
        
        return supply_table
    
    def get_valid_corners(self) -> Set[str]:
        """
        Get all valid corner names from CSV table
        
        Returns:
            Set of valid corner names (TT, FFG, SSG, etc.)
        """
        all_corners = set()
        
        for config in self.corner_table.values():
            all_corners.update(config['corners'])
        
        return all_corners
    
    def get_valid_voltage_rails(self) -> Set[str]:
        """
        Get all valid voltage rail names from CSV table
        
        Returns:
            Set of valid rail names (vcc, 1p1v, vcctx_600, etc.)
        """
        return set(self.supply_table.keys())
    
    def validate_corners(self, corners: List[str]) -> bool:
        """
        Validate corner list against table_corner_list.csv
        
        Args:
            corners: List of corner names to validate
            
        Returns:
            True if all corners are valid
            
        Raises:
            ValueError: If any corner is invalid
        """
        valid_corners = self.get_valid_corners()
        
        for corner in corners:
            if corner not in valid_corners:
                raise ValueError(
                    f"Invalid corner '{corner}'. "
                    f"Valid corners from CSV: {sorted(valid_corners)}"
                )
        
        logger.info(f"✅ Corner validation passed: {corners}")
        return True
    
    def validate_voltage_rail(self, rail: str) -> bool:
        """
        Validate voltage rail against table_supply_list.csv
        
        Args:
            rail: Rail name to validate (e.g., '1p1v', 'vcc')
            
        Returns:
            True if rail is valid
            
        Raises:
            ValueError: If rail is invalid
        """
        valid_rails = self.get_valid_voltage_rails()
        
        if rail not in valid_rails:
            raise ValueError(
                f"Invalid voltage rail '{rail}'. "
                f"Valid rails from CSV: {sorted(valid_rails)}"
            )
        
        logger.info(f"✅ Voltage rail validation passed: {rail}")
        return True
    
    def validate_voltage_condition(self, condition: str) -> bool:
        """
        Validate voltage condition (perf, func, htol, hvqk)
        
        Args:
            condition: Voltage condition
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If condition is invalid
        """
        valid_conditions = ['func', 'perf', 'htol', 'hvqk']
        
        if condition not in valid_conditions:
            raise ValueError(
                f"Invalid voltage condition '{condition}'. "
                f"Valid: {valid_conditions}"
            )
        
        logger.info(f"✅ Voltage condition validation passed: {condition}")
        return True
    
    def generate_config(self, params: Dict, output_path: str) -> bool:
        """
        Generate config.cfg file with validated parameters
        
        Args:
            params: Dictionary of configuration parameters
            output_path: Path to write config.cfg
            
        Returns:
            True if successful
        """
        # Validate all parameters first
        if 'corners' in params:
            self.validate_corners(params['corners'])
        
        if 'vccn' in params:
            self.validate_voltage_rail(params['vccn'])
        
        if 'condition' in params:
            self.validate_voltage_condition(params['condition'])
        
        # Generate config.cfg in Pai Ho's exact format
        config_lines = [
            f"mode:{params.get('mode', 'prelay')}",
            f"vccn:{params.get('vccn', '1p1v')}",
            f"vcctx:{params.get('vcctx', 'vcctx_NA')}",
            f"1st_supply_swp:{params.get('1st_supply_swp', 'vcc')}",
            f"2nd_supply_swp:{params.get('2nd_supply_swp', 'vccn')}",
            f"3rd_supply_swp:{params.get('3rd_supply_swp', 'NA')}",
            f"condition:{params.get('condition', 'perf')}",
            f"CPU #:{params.get('cpu', 4)}",
            f"MEM [G]:{params.get('memory', 4)}",
            f"alter_extraction:{params.get('alter_extraction', 'No')}",
            f"alter_string#:{params.get('alter_string', 11)}",
            f"sim_mode:{params.get('sim_mode', 'ac')}",
            f"gs/gf_corner:{params.get('gs_gf_corner', 'Yes')}",
            f"vcc_vid:{params.get('vcc_vid', 'Yes')}",
            f"simulator:{params.get('simulator', 'primesim')}",
            ""  # Empty line at end
        ]
        
        # Write config file
        with open(output_path, 'w') as f:
            f.write('\n'.join(config_lines))
        
        logger.info(f"✅ Generated config.cfg at: {output_path}")
        return True
    
    def get_corner_config_type(self, corners: List[str]) -> Optional[str]:
        """
        Find matching corner configuration type from table_corner_list.csv
        
        Args:
            corners: List of corners to match
            
        Returns:
            Configuration type name (e.g., 'full_tt', 'nom_tt') or None
        """
        corner_set = set(corners)
        
        for config_type, config in self.corner_table.items():
            if set(config['corners']) == corner_set:
                return config_type
        
        return None


if __name__ == "__main__":
    # Test the config generator
    logging.basicConfig(level=logging.INFO)
    
    from pathlib import Path
    
    # Get repository root (3 levels up from automation/backend/)
    repo_root = Path(__file__).parent.parent.parent
    
    print("=== Testing PaiHoConfigGenerator ===\n")
    
    # Test with gpio/1p1v
    generator = PaiHoConfigGenerator('gpio', '1p1v', repo_root)
    
    print(f"\n✅ Valid corners: {sorted(generator.get_valid_corners())}")
    print(f"\n✅ Valid voltage rails: {sorted(generator.get_valid_voltage_rails())}")
    
    # Test validation
    print("\n=== Testing Validation ===")
    
    try:
        generator.validate_corners(['TT', 'FFG', 'SSG'])
        print("✅ Corner validation: PASSED")
    except ValueError as e:
        print(f"❌ Corner validation: FAILED - {e}")
    
    try:
        generator.validate_voltage_rail('1p1v')
        print("✅ Voltage rail validation: PASSED")
    except ValueError as e:
        print(f"❌ Voltage rail validation: FAILED - {e}")
    
    try:
        generator.validate_voltage_condition('perf')
        print("✅ Voltage condition validation: PASSED")
    except ValueError as e:
        print(f"❌ Voltage condition validation: FAILED - {e}")
    
    print("\n=== Config Generator Test Complete ===")
