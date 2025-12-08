"""
Additional test cases for unit validation
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

# Test 5: Incompatible units that bypass early validation
print("="*60)
print("Test 5: Incompatible units via expression (should fail)")
print("="*60)
equations5 = [
    "L = 10 [m]",
    "W = 5 [m]",
    "V = L * W  [m]"  # Should fail - L*W is m^2 but m was specified
]

try:
    results, warnings = solver.solve(equations5)
    print("✗ Test 5 FAILED: Should have thrown an error  ")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except ValueError as e:
    if "Unit mismatch" in str(e):
        print(f"✓ Test 5 PASSED: {e}")
    else:
        print(f"✗ Test 5 FAILED (wrong error): {e}")
except Exception as e:
    print(f"✗ Test 5 FAILED (unexpected error): {e}")

# Test 6: Units with exponents
print("\n" + "="*60)
print("Test 6: Correct units with exponents (should work)")
print("="*60)
equations6 = [
    "r = 5 [m]",
    "V = (4/3) * 3.14159 * r^3 [m^3]"  # Volume of sphere
]

try:
    results, warnings = solver.solve(equations6)
    print("✓ Test 6 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except Exception as e:
    print(f"✗ Test 6 FAILED: {e}")

# Test 7: Complex expressions
print("\n" + "="*60)
print("Test 7: Complex unit calculation (should work)")
print("="*60)
equations7 = [
    "m = 10 [kg]",
    "v = 5 [m/s]",
    "KE = 0.5 * m * v^2 [J]"  # Kinetic energy in Joules
]

try:
    results, warnings = solver.solve(equations7)
    print("✓ Test 7 PASSED")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except Exception as e:
    print(f"✗ Test 7 FAILED: {e}")
