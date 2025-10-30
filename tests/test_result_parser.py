#!/usr/bin/env python3
"""
Unit Tests for ResultParser

Tests .mt0 file parsing, measurement extraction, and bit-identical verification.
Target: 20+ test cases with CRITICAL bit-identical verification.
"""

import unittest
import os
import tempfile
import shutil
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from result_parser import ResultParser, ParseError


class TestResultParserInitialization(unittest.TestCase):
    """Test cases for initialization"""
    
    def test_01_initialization(self):
        """Test parser initialization"""
        parser = ResultParser()
        self.assertIsNotNone(parser)


class TestMT0FileParsing(unittest.TestCase):
    """Test cases for .mt0 file parsing"""
    
    def setUp(self):
        """Create temporary test files"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create mock .mt0 file with measurements
        self.mt0_file = os.path.join(self.test_dir, 'sim_tx.mt0')
        with open(self.mt0_file, 'w') as f:
            f.write("""
.TITLE SPICE Simulation Results

.measure del_rr = 3.12398102e-11
.measure del_ff = 3.18924935e-11
.measure power = 1.234e-3
.measure current = 5.678e-4
.measure temper = 85.0
""")
        
        self.parser = ResultParser()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_02_parse_valid_file(self):
        """Test parsing valid .mt0 file"""
        measurements = self.parser.parse_mt0_file(self.mt0_file)
        
        self.assertIsNotNone(measurements)
        self.assertIn('del_rr', measurements)
        self.assertIn('del_ff', measurements)
    
    def test_03_extract_del_rr_measurement(self):
        """Test extracting del_rr measurement"""
        measurements = self.parser.parse_mt0_file(self.mt0_file)
        
        self.assertAlmostEqual(measurements['del_rr'], 3.12398102e-11, places=15)
    
    def test_04_extract_del_ff_measurement(self):
        """Test extracting del_ff measurement"""
        measurements = self.parser.parse_mt0_file(self.mt0_file)
        
        self.assertAlmostEqual(measurements['del_ff'], 3.18924935e-11, places=15)
    
    def test_05_extract_power_measurement(self):
        """Test extracting power measurement"""
        measurements = self.parser.parse_mt0_file(self.mt0_file)
        
        self.assertAlmostEqual(measurements['power'], 1.234e-3, places=10)
    
    def test_06_extract_temperature(self):
        """Test extracting temperature"""
        measurements = self.parser.parse_mt0_file(self.mt0_file)
        
        self.assertEqual(measurements['temper'], 85.0)
    
    def test_07_missing_file_raises_error(self):
        """Test parsing non-existent file raises error"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_mt0_file('nonexistent.mt0')
    
    def test_08_empty_file_returns_dict(self):
        """Test parsing empty file returns dict"""
        empty_file = os.path.join(self.test_dir, 'empty.mt0')
        with open(empty_file, 'w') as f:
            f.write("")
        
        measurements = self.parser.parse_mt0_file(empty_file)
        
        self.assertIsInstance(measurements, dict)


class TestDirectoryParsing(unittest.TestCase):
    """Test cases for directory parsing"""
    
    def setUp(self):
        """Create directory structure with .mt0 files"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create PVT directory structure
        # TT/typical/typical_85/v1nom/sim_tx.mt0
        mt0_path = os.path.join(self.test_dir, 'TT/typical/typical_85/v1nom')
        os.makedirs(mt0_path)
        
        with open(os.path.join(mt0_path, 'sim_tx.mt0'), 'w') as f:
            f.write(".measure del_rr = 3.12e-11\n")
        
        # FFG/typical/typical_125/v1min/sim_tx.mt0
        mt0_path2 = os.path.join(self.test_dir, 'FFG/typical/typical_125/v1min')
        os.makedirs(mt0_path2)
        
        with open(os.path.join(mt0_path2, 'sim_tx.mt0'), 'w') as f:
            f.write(".measure del_rr = 2.98e-11\n")
        
        self.parser = ResultParser()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_09_parse_directory_finds_files(self):
        """Test parsing directory finds .mt0 files"""
        results = self.parser.parse_directory(self.test_dir)
        
        self.assertEqual(len(results), 2)
    
    def test_10_extracts_corner_from_path(self):
        """Test corner is extracted from file path"""
        results = self.parser.parse_directory(self.test_dir)
        
        corners = [r.get('corner') for r in results]
        self.assertIn('TT', corners)
        self.assertIn('FFG', corners)
    
    def test_11_extracts_temperature_from_path(self):
        """Test temperature is extracted from file path"""
        results = self.parser.parse_directory(self.test_dir)
        
        temps = [r.get('temperature') for r in results]
        self.assertIn('85', temps)
        self.assertIn('125', temps)
    
    def test_12_extracts_voltage_from_path(self):
        """Test voltage combo is extracted from file path"""
        results = self.parser.parse_directory(self.test_dir)
        
        voltages = [r.get('voltage_combo') for r in results]
        self.assertIn('v1nom', voltages)
        self.assertIn('v1min', voltages)


class TestMeasurementExtraction(unittest.TestCase):
    """Test cases for measurement extraction from content"""
    
    def setUp(self):
        """Create parser"""
        self.parser = ResultParser()
    
    def test_13_extract_from_content(self):
        """Test extracting measurements from content string"""
        content = """
.measure del_rr = 3.12e-11
.measure del_ff = 3.18e-11
"""
        
        measurements = self.parser.extract_measurements(content)
        
        self.assertIn('del_rr', measurements)
        self.assertIn('del_ff', measurements)
    
    def test_14_handles_scientific_notation(self):
        """Test handling scientific notation"""
        content = ".measure power = 1.234e-3\n"
        
        measurements = self.parser.extract_measurements(content)
        
        self.assertAlmostEqual(measurements['power'], 1.234e-3)
    
    def test_15_handles_negative_values(self):
        """Test handling negative values"""
        content = ".measure voltage = -1.5\n"
        
        measurements = self.parser.extract_measurements(content)
        
        self.assertEqual(measurements['voltage'], -1.5)


class TestSummaryGeneration(unittest.TestCase):
    """Test cases for summary generation"""
    
    def setUp(self):
        """Create parser"""
        self.parser = ResultParser()
    
    def test_16_generate_summary_from_results(self):
        """Test generating summary from results"""
        results = [
            {'del_rr': 3.12e-11, 'corner': 'TT'},
            {'del_rr': 2.98e-11, 'corner': 'FFG'},
            {'del_rr': 3.25e-11, 'corner': 'SSG'}
        ]
        
        summary = self.parser.generate_summary(results)
        
        self.assertEqual(summary['total_results'], 3)
        self.assertIn('measurements', summary)
    
    def test_17_summary_calculates_min_max_avg(self):
        """Test summary calculates min, max, avg"""
        results = [
            {'del_rr': 3.0e-11},
            {'del_rr': 2.0e-11},
            {'del_rr': 4.0e-11}
        ]
        
        summary = self.parser.generate_summary(results)
        
        stats = summary['measurements']['del_rr']
        self.assertEqual(stats['min'], 2.0e-11)
        self.assertEqual(stats['max'], 4.0e-11)
        self.assertEqual(stats['avg'], 3.0e-11)
    
    def test_18_empty_results_returns_empty_summary(self):
        """Test empty results returns empty summary"""
        summary = self.parser.generate_summary([])
        
        self.assertEqual(summary, {})


class TestBitIdenticalVerification(unittest.TestCase):
    """CRITICAL test cases for bit-identical verification"""
    
    def setUp(self):
        """Create test files"""
        self.test_dir = tempfile.mkdtemp()
        self.parser = ResultParser()
        
        # Create two identical files
        self.file1 = os.path.join(self.test_dir, 'file1.mt0')
        self.file2 = os.path.join(self.test_dir, 'file2.mt0')
        self.file3 = os.path.join(self.test_dir, 'file3.mt0')
        
        content = ".measure del_rr = 3.12398102e-11\n"
        
        with open(self.file1, 'w') as f:
            f.write(content)
        
        with open(self.file2, 'w') as f:
            f.write(content)
        
        with open(self.file3, 'w') as f:
            f.write(".measure del_rr = 3.12398103e-11\n")  # Different
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_19_identical_files_return_true(self):
        """CRITICAL: Test identical files return True"""
        result = self.parser.validate_bit_identical(self.file1, self.file2)
        
        self.assertTrue(result)
    
    def test_20_different_files_return_false(self):
        """CRITICAL: Test different files return False"""
        result = self.parser.validate_bit_identical(self.file1, self.file3)
        
        self.assertFalse(result)
    
    def test_21_missing_file_returns_false(self):
        """Test missing file returns False"""
        result = self.parser.validate_bit_identical(self.file1, 'nonexistent.mt0')
        
        self.assertFalse(result)


class TestMeasurementComparison(unittest.TestCase):
    """Test cases for measurement comparison"""
    
    def setUp(self):
        """Create parser"""
        self.parser = ResultParser()
    
    def test_22_identical_measurements(self):
        """Test comparing identical measurements"""
        meas1 = {'del_rr': 3.12e-11, 'del_ff': 3.18e-11}
        meas2 = {'del_rr': 3.12e-11, 'del_ff': 3.18e-11}
        
        comparison = self.parser.compare_measurements(meas1, meas2)
        
        self.assertTrue(comparison['identical'])
        self.assertEqual(len(comparison['differences']), 0)
    
    def test_23_different_measurements(self):
        """Test comparing different measurements"""
        meas1 = {'del_rr': 3.12e-11}
        meas2 = {'del_rr': 3.15e-11}
        
        # Use smaller tolerance so difference is detected
        comparison = self.parser.compare_measurements(meas1, meas2, tolerance=1e-14)
        
        self.assertFalse(comparison['identical'])
        self.assertGreater(len(comparison['differences']), 0)
    
    def test_24_missing_keys_detected(self):
        """Test missing keys are detected"""
        meas1 = {'del_rr': 3.12e-11}
        meas2 = {'del_rr': 3.12e-11, 'del_ff': 3.18e-11}
        
        comparison = self.parser.compare_measurements(meas1, meas2)
        
        self.assertFalse(comparison['identical'])
    
    def test_25_tolerance_applied(self):
        """Test tolerance is applied to floating point comparison"""
        meas1 = {'del_rr': 3.120000000001e-11}
        meas2 = {'del_rr': 3.120000000002e-11}
        
        # With default tolerance (1e-12), should be identical
        comparison = self.parser.compare_measurements(meas1, meas2, tolerance=1e-10)
        
        self.assertTrue(comparison['identical'])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
