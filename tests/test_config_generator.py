#!/usr/bin/env python3
"""
Unit Tests for PaiHoConfigGenerator

Tests parameter validation, config generation, and CSV loading functionality.
Target: 50+ test cases for comprehensive coverage.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_generator import PaiHoConfigGenerator, ConfigValidationError, ConfigGenerationError


class TestConfigGeneratorInitialization(unittest.TestCase):
    """Test cases for initialization and CSV loading"""
    
    def setUp(self):
        """Create temporary CSV files for testing"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create mock table_corner_list.csv
        corner_csv = os.path.join(self.test_dir, 'table_corner_list.csv')
        with open(corner_csv, 'w') as f:
            f.write("type,extraction,corner list\n")
            f.write("nom_tt,typical,TT\n")
            f.write("full_tt,typical,TT FSG SFG FFG FFAG SSG SSAG\n")
        
        # Create mock table_supply_list.csv
        supply_csv = os.path.join(self.test_dir, 'table_supply_list.csv')
        with open(supply_csv, 'w') as f:
            f.write("1st_supply,2nd_supply,3rd_supply\n")
            f.write("vcc,NA,NA\n")
            f.write("vccn,NA,NA\n")
        
        # Create mock table_supply_list_ac.csv
        supply_ac_csv = os.path.join(self.test_dir, 'table_supply_list_ac.csv')
        with open(supply_ac_csv, 'w') as f:
            f.write("1st_supply,2nd_supply,3rd_supply\n")
            f.write("vcc,vcctx,NA\n")
        
        # Create mock table_supply_list_dc.csv
        supply_dc_csv = os.path.join(self.test_dir, 'table_supply_list_dc.csv')
        with open(supply_dc_csv, 'w') as f:
            f.write("1st_supply,2nd_supply,3rd_supply\n")
            f.write("vccn,vcctx,vccana\n")
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.test_dir)
    
    def test_01_valid_initialization(self):
        """Test successful initialization with valid path"""
        generator = PaiHoConfigGenerator(self.test_dir)
        self.assertIsNotNone(generator)
        self.assertEqual(generator.script_path, self.test_dir)
    
    def test_02_invalid_path_raises_error(self):
        """Test initialization with non-existent path raises error"""
        with self.assertRaises(FileNotFoundError):
            PaiHoConfigGenerator("/nonexistent/path")
    
    def test_03_load_corners_success(self):
        """Test corner loading from CSV"""
        generator = PaiHoConfigGenerator(self.test_dir)
        corners = generator.get_valid_corners()
        
        # Should have TT, FSG, SFG, FFG, FFAG, SSG, SSAG (sorted alphabetically)
        expected = ['FFAG', 'FFG', 'FSG', 'SFG', 'SSAG', 'SSG', 'TT']
        self.assertEqual(corners, expected)
    
    def test_04_load_voltages_success(self):
        """Test voltage loading from CSV files"""
        generator = PaiHoConfigGenerator(self.test_dir)
        voltages_ac = generator.get_valid_voltages('ac')
        
        self.assertEqual(len(voltages_ac), 1)
        self.assertEqual(voltages_ac[0], ('vcc', 'vcctx', 'NA'))
    
    def test_05_missing_corner_csv_raises_error(self):
        """Test error when corner CSV is missing"""
        os.remove(os.path.join(self.test_dir, 'table_corner_list.csv'))
        
        with self.assertRaises(FileNotFoundError):
            PaiHoConfigGenerator(self.test_dir)


class TestParameterValidation(unittest.TestCase):
    """Test cases for parameter validation logic"""
    
    def setUp(self):
        """Create generator with mock CSV files"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create minimal CSV files
        corner_csv = os.path.join(self.test_dir, 'table_corner_list.csv')
        with open(corner_csv, 'w') as f:
            f.write("type,extraction,corner list\n")
            f.write("full,typical,TT FFG SSG\n")
        
        for csv_name in ['table_supply_list.csv', 'table_supply_list_ac.csv', 'table_supply_list_dc.csv']:
            csv_path = os.path.join(self.test_dir, csv_name)
            with open(csv_path, 'w') as f:
                f.write("1st_supply,2nd_supply,3rd_supply\n")
                f.write("vcc,NA,NA\n")
        
        self.generator = PaiHoConfigGenerator(self.test_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_06_valid_params_pass(self):
        """Test valid parameters pass validation"""
        params = {
            'mode': 'prelay',
            'vccn': '1p1v',
            'condition': 'perf',
            'simulator': 'primesim',
            'sim_mode': 'ac',
            'CPU': '16',
            'MEM': '32G'
        }
        
        is_valid, error = self.generator.validate_params(params)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_07_invalid_mode_rejected(self):
        """Test invalid mode is rejected"""
        params = {'mode': 'invalid_mode', 'vccn': '1p1v'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('mode must be one of', error)
    
    def test_08_invalid_vccn_rejected(self):
        """Test invalid vccn is rejected"""
        params = {'mode': 'prelay', 'vccn': '1p5v'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('vccn must be one of', error)
    
    def test_09_invalid_condition_rejected(self):
        """Test invalid condition is rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'condition': 'invalid'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('condition must be one of', error)
    
    def test_10_invalid_simulator_rejected(self):
        """Test invalid simulator is rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'simulator': 'invalid'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('simulator must be one of', error)
    
    def test_11_invalid_sim_mode_rejected(self):
        """Test invalid sim_mode is rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'sim_mode': 'invalid'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('sim_mode must be one of', error)
    
    def test_12_invalid_corner_rejected(self):
        """Test invalid corner is rejected"""
        params = {
            'mode': 'prelay',
            'vccn': '1p1v',
            'corners': ['TT', 'INVALID_CORNER']
        }
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('Invalid corner', error)
    
    def test_13_valid_corners_accepted(self):
        """Test valid corners are accepted"""
        params = {
            'mode': 'prelay',
            'vccn': '1p1v',
            'corners': ['TT', 'FFG', 'SSG']
        }
        
        is_valid, error = self.generator.validate_params(params)
        self.assertTrue(is_valid)
    
    def test_14_invalid_cpu_rejected(self):
        """Test invalid CPU value rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'CPU': 'invalid'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('CPU must be integer', error)
    
    def test_15_negative_cpu_rejected(self):
        """Test negative CPU value rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'CPU': '-4'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('CPU must be positive', error)
    
    def test_16_zero_cpu_rejected(self):
        """Test zero CPU value rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'CPU': '0'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('CPU must be positive', error)
    
    def test_17_invalid_mem_format_rejected(self):
        """Test invalid MEM format rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'MEM': '32'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('MEM must end with', error)
    
    def test_18_invalid_mem_value_rejected(self):
        """Test invalid MEM value rejected"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'MEM': 'invalidG'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertFalse(is_valid)
        self.assertIn('MEM must be number', error)
    
    def test_19_valid_mem_gigabytes(self):
        """Test valid MEM in gigabytes"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'MEM': '32G'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertTrue(is_valid)
    
    def test_20_valid_mem_megabytes(self):
        """Test valid MEM in megabytes"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'MEM': '4096M'}
        
        is_valid, error = self.generator.validate_params(params)
        self.assertTrue(is_valid)


class TestConfigGeneration(unittest.TestCase):
    """Test cases for config.cfg file generation"""
    
    def setUp(self):
        """Create generator and temp directory"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create minimal CSV files
        corner_csv = os.path.join(self.test_dir, 'table_corner_list.csv')
        with open(corner_csv, 'w') as f:
            f.write("type,extraction,corner list\n")
            f.write("full,typical,TT FFG SSG\n")
        
        for csv_name in ['table_supply_list.csv', 'table_supply_list_ac.csv', 'table_supply_list_dc.csv']:
            csv_path = os.path.join(self.test_dir, csv_name)
            with open(csv_path, 'w') as f:
                f.write("1st_supply,2nd_supply,3rd_supply\n")
                f.write("vcc,NA,NA\n")
        
        self.generator = PaiHoConfigGenerator(self.test_dir)
        self.output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)
    
    def test_21_generate_config_success(self):
        """Test successful config generation"""
        params = {
            'mode': 'prelay',
            'vccn': '1p1v',
            'vcctx': '1p0v',
            'condition': 'perf',
            'CPU': '16',
            'MEM': '32G',
            'simulator': 'primesim'
        }
        
        output_path = os.path.join(self.output_dir, 'config.cfg')
        result = self.generator.generate_config(params, output_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
    
    def test_22_config_file_format(self):
        """Test generated config file has correct format"""
        params = {
            'mode': 'prelay',
            'vccn': '1p1v',
            'condition': 'perf'
        }
        
        output_path = os.path.join(self.output_dir, 'config.cfg')
        self.generator.generate_config(params, output_path)
        
        with open(output_path, 'r') as f:
            content = f.read()
        
        # Check key parameters are present
        self.assertIn('mode=prelay', content)
        self.assertIn('vccn=1p1v', content)
        self.assertIn('condition=perf', content)
    
    def test_23_config_has_all_15_parameters(self):
        """Test generated config has all 15 required parameters"""
        params = {'mode': 'prelay', 'vccn': '1p1v'}
        
        output_path = os.path.join(self.output_dir, 'config.cfg')
        self.generator.generate_config(params, output_path)
        
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        # Should have 16 lines (15 params + postlay_cross_cornerlist)
        self.assertEqual(len(lines), 16)
    
    def test_24_invalid_params_raise_validation_error(self):
        """Test invalid params raise ConfigValidationError"""
        params = {'mode': 'invalid_mode', 'vccn': '1p1v'}
        
        output_path = os.path.join(self.output_dir, 'config.cfg')
        
        with self.assertRaises(ConfigValidationError):
            self.generator.generate_config(params, output_path)
    
    def test_25_default_values_used(self):
        """Test default values are used when params not provided"""
        params = {'mode': 'prelay', 'vccn': '1p1v'}
        
        output_path = os.path.join(self.output_dir, 'config.cfg')
        self.generator.generate_config(params, output_path)
        
        with open(output_path, 'r') as f:
            content = f.read()
        
        # Check defaults
        self.assertIn('simulator=primesim', content)  # Default simulator
        self.assertIn('condition=perf', content)      # Default condition
        self.assertIn('CPU #=16', content)            # Default CPU


class TestHelperMethods(unittest.TestCase):
    """Test cases for helper/utility methods"""
    
    def setUp(self):
        """Create generator"""
        self.test_dir = tempfile.mkdtemp()
        
        corner_csv = os.path.join(self.test_dir, 'table_corner_list.csv')
        with open(corner_csv, 'w') as f:
            f.write("type,extraction,corner list\n")
            f.write("full,typical,TT FFG SSG FSG SFG\n")
        
        for csv_name in ['table_supply_list.csv', 'table_supply_list_ac.csv', 'table_supply_list_dc.csv']:
            csv_path = os.path.join(self.test_dir, csv_name)
            with open(csv_path, 'w') as f:
                f.write("1st_supply,2nd_supply,3rd_supply\n")
                f.write("vcc,NA,NA\n")
                f.write("vccn,vcctx,NA\n")
        
        self.generator = PaiHoConfigGenerator(self.test_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_26_get_valid_corners_returns_list(self):
        """Test get_valid_corners returns list"""
        corners = self.generator.get_valid_corners()
        self.assertIsInstance(corners, list)
    
    def test_27_get_valid_corners_not_empty(self):
        """Test get_valid_corners returns non-empty list"""
        corners = self.generator.get_valid_corners()
        self.assertGreater(len(corners), 0)
    
    def test_28_get_valid_corners_returns_copy(self):
        """Test get_valid_corners returns a copy, not reference"""
        corners1 = self.generator.get_valid_corners()
        corners2 = self.generator.get_valid_corners()
        
        # Modify one
        corners1.append('FAKE_CORNER')
        
        # Other should be unchanged
        self.assertNotIn('FAKE_CORNER', corners2)
    
    def test_29_get_valid_voltages_ac_mode(self):
        """Test get_valid_voltages for AC mode"""
        voltages = self.generator.get_valid_voltages('ac')
        self.assertIsInstance(voltages, list)
        self.assertGreater(len(voltages), 0)
    
    def test_30_get_valid_voltages_dc_mode(self):
        """Test get_valid_voltages for DC mode"""
        voltages = self.generator.get_valid_voltages('dc')
        self.assertIsInstance(voltages, list)
    
    def test_31_get_valid_voltages_default_mode(self):
        """Test get_valid_voltages with default mode"""
        voltages = self.generator.get_valid_voltages()
        self.assertIsInstance(voltages, list)


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error conditions"""
    
    def setUp(self):
        """Create generator"""
        self.test_dir = tempfile.mkdtemp()
        
        corner_csv = os.path.join(self.test_dir, 'table_corner_list.csv')
        with open(corner_csv, 'w') as f:
            f.write("type,extraction,corner list\n")
            f.write("full,typical,TT\n")
        
        for csv_name in ['table_supply_list.csv', 'table_supply_list_ac.csv', 'table_supply_list_dc.csv']:
            csv_path = os.path.join(self.test_dir, csv_name)
            with open(csv_path, 'w') as f:
                f.write("1st_supply,2nd_supply,3rd_supply\n")
                f.write("vcc,NA,NA\n")
        
        self.generator = PaiHoConfigGenerator(self.test_dir)
        self.output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.output_dir)
    
    def test_32_empty_params_dict(self):
        """Test with empty params dictionary"""
        params = {}
        is_valid, error = self.generator.validate_params(params)
        
        # Should fail because 'mode' is required
        self.assertFalse(is_valid)
    
    def test_33_none_values_in_params(self):
        """Test with None values"""
        params = {'mode': None, 'vccn': '1p1v'}
        is_valid, error = self.generator.validate_params(params)
        
        self.assertFalse(is_valid)
    
    def test_34_empty_corners_list(self):
        """Test with empty corners list"""
        params = {'mode': 'prelay', 'vccn': '1p1v', 'corners': []}
        is_valid, error = self.generator.validate_params(params)
        
        # Empty list should be valid (no corners specified)
        self.assertTrue(is_valid)
    
    def test_35_case_sensitive_mode(self):
        """Test that mode is case-sensitive"""
        params = {'mode': 'PRELAY', 'vccn': '1p1v'}
        is_valid, error = self.generator.validate_params(params)
        
        # Should fail - must be lowercase 'prelay'
        self.assertFalse(is_valid)
    
    def test_36_write_to_readonly_location(self):
        """Test error handling when writing to read-only location"""
        params = {'mode': 'prelay', 'vccn': '1p1v'}
        
        # Try to write to root (should fail)
        output_path = '/config.cfg'
        
        with self.assertRaises(ConfigGenerationError):
            self.generator.generate_config(params, output_path)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
