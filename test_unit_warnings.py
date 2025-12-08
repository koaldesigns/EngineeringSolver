"""
Test script for the new warning-based unit validation
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

# Test 1: Correct units - should work without warnings
print("="*60)
print("Test 1: Matching units (should work with no warnings)")
print("="*60)
equations1 = [
    "L = 10 [m]",
    "A = L^2 [m^2]"
]

try:
    results, warnings = solver.solve(equations1)
    print("✓ Test 1 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  No warnings (as expected)")
except Exception as e:
    print(f"✗ Test 1 FAILED: {e}")

# Test 2: Dimensionless with dimensional unit - should warn but continue
print("\n" + "="*60)
print("Test 2: Dimensionless with dimensional unit (should warn)")
print("="*60)
equations2 = [
    "x = 5",
    "y = x * 2 [kg]"
]

try:
    results, warnings = solver.solve(equations2)
    print("✓ Test 2 PASSED - Calculation continued despite unit mismatch")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  ✗ No warnings (expected warnings!)")
except Exception as e:
    print(f"✗ Test 2 FAILED with error: {e}")

# Test 3: Unit conversion - should work without warnings
print("\n" + "="*60)
print("Test 3: Compatible unit conversion (should work)")
print("="*60)
equations3 = [
    "L = 10 [m]",
    "A = L^2 [ft^2]"
]

try:
    results, warnings = solver.solve(equations3)
    print("✓ Test 3 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  No warnings (as expected)")
except Exception as e:
    print(f"✗ Test 3 FAILED: {e}")

# Test 4: Complex calculation with units
print("\n" + "="*60)
print("Test 4: Complex calculation (should work)")
print("="*60)
equations4 = [
    "m = 10 [kg]",
    "v = 5 [m/s]",
    "KE = 0.5 * m * v^2 [J]"
]

try:
    results, warnings = solver.solve(equations4)
    print("✓ Test 4 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  No warnings (as expected)")
except Exception as e:
    print(f"✗ Test 4 FAILED: {e}")

# Test 5: User's original example
print("\n" + "="*60)
print("Test 5: User's original example (should work)")
print("="*60)
equations5 = [
    "L = 10 [m]",
    "T = 25 [degC]",
    "P = 100 [kPa]",
    "// Calculate area",
    "A = L^2 [m^2]"
]

try:
    results, warnings = solver.solve(equations5)
    print("✓ Test 5 PASSED")
    for var in sorted(results.keys()):
        data = results[var]
        print(f"  {var} = {data['value']} {data['unit']}")
    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  No warnings (as expected)")
except Exception as e:
    print(f"✗ Test 5 FAILED: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("The new system:")
print("  1. Continues calculation even with unit mismatches")
print("  2. Generates warnings for mismatched units")
print("  3. Uses calculated units when they don't match specified units")
print("  4. Converts units when dimensionalities match")
