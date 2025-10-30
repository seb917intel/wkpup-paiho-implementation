#!/usr/bin/env python3
"""
Result Parser

Parses .mt0 measurement files and extracts simulation results.
This module is part of the WKPUP reconciliation project, implementing result
extraction from Pai Ho's SPICE simulation outputs.

Reference: ULTIMATE_MASTER_PLAN.md - Module 5: result_parser.py (~200 lines)
Ground Truth: COMPREHENSIVE_ANALYSIS.md - Measurement extraction and data flow
"""

import re
import os
from typing import Dict, List, Optional
from pathlib import Path


class ParseError(Exception):
    """Raised when .mt0 file parsing fails"""
    pass


class ResultParser:
    """
    Parses SPICE .mt0 measurement files and extracts simulation results.
    
    This class implements the extraction logic to read measurements from
    Pai Ho's simulation output files.
    """
    
    # Common measurement patterns in .mt0 files
    MEASUREMENT_PATTERNS = {
        'del_rr': r'del_rr\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'del_ff': r'del_ff\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'del_rf': r'del_rf\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'del_fr': r'del_fr\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'power': r'power\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'current': r'current\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'voltage': r'voltage\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'resistance': r'resistance\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
        'temper': r'temper\s*=\s*([-+]?[\d.]+[eE]?[-+]?\d*)',
    }
    
    def __init__(self):
        """Initialize result parser"""
        self.logger = None  # Could add logging if needed
    
    def parse_mt0_file(self, filepath: str) -> Dict:
        """
        Parse a single .mt0 measurement file.
        
        Args:
            filepath: Path to .mt0 file
            
        Returns:
            Dict with extracted measurements
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ParseError: If parsing fails
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f".mt0 file not found: {filepath}")
        
        measurements = {}
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract measurements using regex patterns
            for name, pattern in self.MEASUREMENT_PATTERNS.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    try:
                        measurements[name] = float(match.group(1))
                    except ValueError:
                        # Skip if conversion fails
                        pass
            
            # Store raw content for debugging
            measurements['_raw_content'] = content
            measurements['_filepath'] = filepath
            
            return measurements
            
        except IOError as e:
            raise ParseError(f"Failed to read .mt0 file: {e}")
    
    def parse_directory(self, directory: str, pattern: str = '**/*.mt0') -> List[Dict]:
        """
        Parse all .mt0 files in a directory.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern for finding .mt0 files
            
        Returns:
            List of measurement dictionaries
        """
        dir_path = Path(directory)
        results = []
        
        for mt0_file in dir_path.glob(pattern):
            try:
                measurements = self.parse_mt0_file(str(mt0_file))
                
                # Extract corner/temp/voltage from path
                # Example path: TT/typical/typical_85/v1nom/sim_tx.mt0
                parts = mt0_file.parts
                if len(parts) >= 5:
                    measurements['corner'] = parts[-5]
                    measurements['extraction'] = parts[-4] if parts[-4] != parts[-5] else parts[-3].split('_')[0]
                    measurements['temperature'] = parts[-3].split('_')[-1]  # '85' from 'typical_85'
                    measurements['voltage_combo'] = parts[-2]
                
                results.append(measurements)
                
            except (FileNotFoundError, ParseError) as e:
                # Log error but continue processing other files
                if self.logger:
                    self.logger.warning(f"Failed to parse {mt0_file}: {e}")
        
        return results
    
    def extract_measurements(self, content: str) -> Dict:
        """
        Extract measurements from .mt0 file content.
        
        Args:
            content: Content of .mt0 file
            
        Returns:
            Dict with extracted measurements
        """
        measurements = {}
        
        for name, pattern in self.MEASUREMENT_PATTERNS.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    measurements[name] = float(match.group(1))
                except ValueError:
                    pass
        
        return measurements
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """
        Generate summary statistics from multiple results.
        
        Args:
            results: List of measurement dictionaries
            
        Returns:
            Dict with summary statistics (min, max, avg, count)
        """
        if not results:
            return {}
        
        summary = {
            'total_results': len(results),
            'measurements': {}
        }
        
        # Collect all measurement values
        measurement_names = set()
        for result in results:
            for key in result.keys():
                if not key.startswith('_') and key not in ['corner', 'extraction', 'temperature', 'voltage_combo']:
                    measurement_names.add(key)
        
        # Calculate statistics for each measurement
        for name in measurement_names:
            values = [r[name] for r in results if name in r and isinstance(r[name], (int, float))]
            
            if values:
                summary['measurements'][name] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }
        
        return summary
    
    def validate_bit_identical(self, file1: str, file2: str) -> bool:
        """
        Validate two .mt0 files are bit-identical.
        
        This is a CRITICAL test to ensure wrapper produces identical results
        to manual execution.
        
        Args:
            file1: Path to first .mt0 file
            file2: Path to second .mt0 file
            
        Returns:
            True if files are bit-identical
        """
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                content1 = f1.read()
                content2 = f2.read()
            
            return content1 == content2
            
        except IOError:
            return False
    
    def compare_measurements(self, meas1: Dict, meas2: Dict, 
                           tolerance: float = 1e-12) -> Dict:
        """
        Compare two measurement dictionaries.
        
        Args:
            meas1: First measurement dict
            meas2: Second measurement dict
            tolerance: Tolerance for floating point comparison
            
        Returns:
            Dict with comparison results
        """
        comparison = {
            'identical': True,
            'differences': []
        }
        
        # Get all measurement keys (excluding metadata)
        keys1 = set(k for k in meas1.keys() if not k.startswith('_'))
        keys2 = set(k for k in meas2.keys() if not k.startswith('_'))
        
        # Check for missing keys
        missing_in_1 = keys2 - keys1
        missing_in_2 = keys1 - keys2
        
        if missing_in_1:
            comparison['identical'] = False
            comparison['differences'].append(f"Missing in file1: {missing_in_1}")
        
        if missing_in_2:
            comparison['identical'] = False
            comparison['differences'].append(f"Missing in file2: {missing_in_2}")
        
        # Compare common keys
        common_keys = keys1 & keys2
        for key in common_keys:
            val1 = meas1[key]
            val2 = meas2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical comparison with tolerance
                if abs(val1 - val2) > tolerance:
                    comparison['identical'] = False
                    comparison['differences'].append(
                        f"{key}: {val1} vs {val2} (diff: {abs(val1 - val2)})"
                    )
            else:
                # Exact comparison for non-numerical
                if val1 != val2:
                    comparison['identical'] = False
                    comparison['differences'].append(
                        f"{key}: {val1} vs {val2}"
                    )
        
        return comparison


# Example usage
if __name__ == "__main__":
    parser = ResultParser()
    
    # Example: Parse a single .mt0 file
    try:
        measurements = parser.parse_mt0_file('path/to/sim_tx.mt0')
        print(f"Extracted measurements: {measurements}")
    except FileNotFoundError:
        print("Example file not found")
    
    # Example: Parse all .mt0 files in a directory
    results = parser.parse_directory('gpio/1p1v')
    print(f"Parsed {len(results)} .mt0 files")
    
    # Example: Generate summary
    summary = parser.generate_summary(results)
    print(f"Summary: {summary}")
    
    # Example: Bit-identical verification
    # identical = parser.validate_bit_identical('file1.mt0', 'file2.mt0')
    # print(f"Bit-identical: {identical}")
