"""
Test script to verify unit mismatch detection
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

# Test 1: Correct units - should work
print("="*60)
print("Test 1: Matching units (should work)")
print("="*60)
equations1 = [
    "L = 10 [m]",
    "A = L^2 [m^2]"  # Should work - m^2 matches m*m
]

try:
    results, warnings = solver.solve(equations1)
    print("✓ Test 1 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except Exception as e:
    print(f"✗ Test 1 FAILED: {e}")

# Test 2: Incompatible units - should fail
print("\n" + "="*60)
print("Test 2: Incompatible units (should fail)")
print("="*60)
equations2 = [
    "L = 10 [m]",
    "A = L^2 [m]"  # Should fail - m^2 doesn't match m
]

try:
    results, warnings = solver.solve(equations2)
    print("✗ Test 2 FAILED: Should have thrown an error")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except ValueError as e:
    if "Unit mismatch" in str(e):
        print(f"✓ Test 2 PASSED: {e}")
    else:
        print(f"✗ Test 2 FAILED (wrong error): {e}")
except Exception as e:
    print(f"✗ Test 2 FAILED (unexpected error): {e}")

# Test 3: Dimensionless expression with dimensional unit - should fail
print("\n" + "="*60)
print("Test 3: Dimensionless expression with dimensional unit (should fail)")
print("="*60)
equations3 = [
    "x = 5",
    "y = x^2 [m]"  # Should fail - x^2 is dimensionless but m is dimensional
]

try:
    results, warnings = solver.solve(equations3)
    print("✗ Test 3 FAILED: Should have thrown an error")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except ValueError as e:
    if "Unit mismatch" in str(e) or "dimensionless" in str(e).lower():
        print(f"✓ Test 3 PASSED: {e}")
    else:
        print(f"✗ Test 3 FAILED (wrong error): {e}")
except Exception as e:
    print(f"✗ Test 3 FAILED (unexpected error): {e}")

# Test 4: Units in different formats but same dimensionality - should work
print("\n" + "="*60)
print("Test 4: Different unit formats, same dimensionality (should work)")
print("="*60)
equations4 = [
    "L = 10 [m]",
    "A = L^2 [ft^2]"  # Should work - different units but same dimensionality (area)
]

try:
    results, warnings = solver.solve(equations4)
    print("✓ Test 4 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except Exception as e:
    print(f"✗ Test 4 FAILED: {e}")
