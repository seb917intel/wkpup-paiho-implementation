#!/usr/bin/env python3
"""
Test script for custom voltage domain functionality.
Tests the complete flow from voltage input to domain creation.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voltage_domain_manager import (
    voltage_to_domain_id,
    domain_id_to_voltage,
    validate_voltage_input,
    validate_voltage_domain,
    get_voltage_value
)


def test_voltage_to_domain_id():
    """Test voltage to domain ID conversion"""
    print("\n" + "="*60)
    print("TEST 1: voltage_to_domain_id()")
    print("="*60)
    
    test_cases = [
        (1.1, "1p1v"),
        (1.8, "1p8v"),
        (0.9, "0p9v"),
        (2.5, "2p5v"),
        (3.3, "3p3v"),
        (1.65, "1p65v"),
        (0.75, "0p75v"),
        (1.234, "1p234v"),
    ]
    
    passed = 0
    failed = 0
    
    for voltage, expected in test_cases:
        result = voltage_to_domain_id(voltage)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} {voltage}V → {result} (expected: {expected})")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return failed == 0


def test_domain_id_to_voltage():
    """Test domain ID to voltage conversion"""
    print("\n" + "="*60)
    print("TEST 2: domain_id_to_voltage()")
    print("="*60)
    
    test_cases = [
        ("1p1v", 1.1),
        ("1p8v", 1.8),
        ("0p9v", 0.9),
        ("2p5v", 2.5),
        ("3p3v", 3.3),
        ("1p65v", 1.65),
        ("0p75v", 0.75),
        ("invalid", None),
        ("1p1", None),  # Missing 'v'
        ("abc", None),
    ]
    
    passed = 0
    failed = 0
    
    for domain_id, expected in test_cases:
        result = domain_id_to_voltage(domain_id)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} {domain_id} → {result} (expected: {expected})")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return failed == 0


def test_validate_voltage_input():
    """Test voltage input validation"""
    print("\n" + "="*60)
    print("TEST 3: validate_voltage_input()")
    print("="*60)
    
    test_cases = [
        # (input, should_be_valid, expected_voltage, expected_domain_id)
        ("1.1", True, 1.1, "1p1v"),
        ("1.8", True, 1.8, "1p8v"),
        ("0.9", True, 0.9, "0p9v"),
        ("2.5", True, 2.5, "2p5v"),
        ("1.65", True, 1.65, "1p65v"),
        ("0.1", True, 0.1, "0p1v"),  # Minimum
        ("5.0", True, 5.0, "5p0v"),  # Maximum
        
        # Invalid cases
        ("", False, None, None),  # Empty
        ("abc", False, None, None),  # Non-numeric
        ("-1.5", False, None, None),  # Negative
        ("0", False, None, None),  # Zero
        ("0.05", False, None, None),  # Below minimum
        ("6.0", False, None, None),  # Above maximum
        ("1.1234", False, None, None),  # Too many decimals
        ("1.5V", False, None, None),  # Contains letters
        ("1,5", False, None, None),  # Wrong decimal separator
    ]
    
    passed = 0
    failed = 0
    
    for input_val, should_be_valid, expected_v, expected_d in test_cases:
        result = validate_voltage_input(input_val)
        
        is_valid = result['valid']
        matches_expected = is_valid == should_be_valid
        
        if is_valid and should_be_valid:
            matches_expected = matches_expected and (
                result['voltage'] == expected_v and
                result['domain_id'] == expected_d
            )
        
        status = "✓" if matches_expected else "✗"
        
        if matches_expected:
            passed += 1
        else:
            failed += 1
        
        if is_valid:
            print(f"{status} '{input_val}' → Valid: {result['voltage']}V ({result['domain_id']})")
        else:
            print(f"{status} '{input_val}' → Invalid: {result['error']}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return failed == 0


def test_validate_voltage_domain():
    """Test voltage domain validation"""
    print("\n" + "="*60)
    print("TEST 4: validate_voltage_domain()")
    print("="*60)
    
    test_cases = [
        ("1p1v", True),
        ("1p8v", True),
        ("0p9v", True),
        ("1p65v", True),
        ("5p0v", True),
        ("0p1v", True),
        ("invalid", False),
        ("6p0v", False),  # Above max
        ("0p05v", False),  # Below min
    ]
    
    passed = 0
    failed = 0
    
    for domain_id, expected in test_cases:
        result = validate_voltage_domain(domain_id)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} {domain_id} → {result} (expected: {expected})")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return failed == 0


def test_get_voltage_value():
    """Test get_voltage_value()"""
    print("\n" + "="*60)
    print("TEST 5: get_voltage_value()")
    print("="*60)
    
    test_cases = [
        ("1p1v", 1.1),
        ("1p8v", 1.8),
        ("0p9v", 0.9),
        ("1p65v", 1.65),
        ("invalid", None),
    ]
    
    passed = 0
    failed = 0
    
    for domain_id, expected in test_cases:
        result = get_voltage_value(domain_id)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} {domain_id} → {result}V (expected: {expected})")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return failed == 0


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("CUSTOM VOLTAGE DOMAIN VALIDATION TESTS")
    print("="*60)
    
    tests = [
        ("voltage_to_domain_id", test_voltage_to_domain_id),
        ("domain_id_to_voltage", test_domain_id_to_voltage),
        ("validate_voltage_input", test_validate_voltage_input),
        ("validate_voltage_domain", test_validate_voltage_domain),
        ("get_voltage_value", test_get_voltage_value),
    ]
    
    results = []
    
    for name, test_func in tests:
        passed = test_func()
        results.append((name, passed))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
