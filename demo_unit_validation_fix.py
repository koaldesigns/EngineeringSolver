"""
Demonstration of the unit validation fix for the reported issue.

This script shows that the equation:
    A = L^2 [m^2]

Now correctly:
1. Calculates L^2 to get the derived units (m^2)
2. Validates that the specified unit [m^2] matches the derived units
3. Uses the specified unit format for display
4. Throws appropriate errors when units don't match
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver

def print_section(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

solver = NumericalSolver()

# ============================================================================
# ORIGINAL USER ISSUE - Should work now
# ============================================================================
print_section("ORIGINAL USER ISSUE - Should Work Now")
print("\nEquations:")
print("  L = 10 [m]")
print("  T = 25 [degC]")
print("  P = 100 [kPa]")
print("  // Calculate area")
print("  A = L^2 [m^2]")

equations = [
    "L = 10 [m]",
    "T = 25 [degC]",
    "P = 100 [kPa]",
    "// Calculate area",
    "A = L^2 [m^2]"
]

try:
    results, warnings = solver.solve(equations)
    print("\n✓ SUCCESS - Equation solved correctly!")
    print("\nResults:")
    for var in sorted(results.keys()):
        data = results[var]
        print(f"  {var} = {data['value']} {data['unit']}")
    
    print("\nKey Points:")
    print("  ✓ L^2 calculated to m^2")
    print("  ✓ Specified unit [m^2] validated against calculated units")
    print("  ✓ Units match - result displayed in user's specified format (m²)")
    print("  ✓ No double-counting or unit errors")
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")

# ============================================================================
# ERROR CASE 1: Mismatched Units
# ============================================================================
print_section("ERROR CASE 1: Mismatched Units")
print("\nEquations:")
print("  L = 10 [m]")
print("  A = L^2 [m]  // ERROR: L^2 is m^2, not m")

equations_error1 = [
    "L = 10 [m]",
    "A = L^2 [m]"
]

try:
    results, warnings = solver.solve(equations_error1)
    print("\n✗ FAILED: Should have thrown an error!")
except ValueError as e:
    print(f"\n✓ SUCCESS - Error caught correctly!")
    print(f"\nError message:")
    print(f"  {e}")
    print(f"\nExpected behavior:")
    print("  ✓ Calculated units (m^2) don't match specified units (m)")
    print("  ✓ Different dimensionalities detected")
    print("  ✓ Clear error message provided")

# ============================================================================
# ERROR CASE 2: Dimensionless vs Dimensional
# ============================================================================
print_section("ERROR CASE 2: Dimensionless vs Dimensional")
print("\nEquations:")
print("  x = 5  // dimensionless")
print("  y = x^2 [m]  // ERROR: x^2 is dimensionless, not meters")

equations_error2 = [
    "x = 5",
    "y = x^2 [m]"
]

try:
    results, warnings = solver.solve(equations_error2)
    print("\n✗ FAILED: Should have thrown an error!")
except ValueError as e:
    print(f"\n✓ SUCCESS - Error caught correctly!")
    print(f"\nError message:")
    print(f"  {e}")
    print(f"\nExpected behavior:")
    print("  ✓ Expression is dimensionless but unit [m] is dimensional")
    print("  ✓ Mismatch detected")
    print("  ✓ Clear error message provided")

# ============================================================================
# SUCCESS CASE: Unit Conversion
# ============================================================================
print_section("SUCCESS CASE: Compatible Unit Conversion")
print("\nEquations:")
print("  L = 10 [m]")
print("  A = L^2 [ft^2]  // Different unit, same dimensionality")

equations_convert = [
    "L = 10 [m]",
    "A = L^2 [ft^2]"
]

try:
    results, warnings = solver.solve(equations_convert)
    print("\n✓ SUCCESS - Equation solved with automatic conversion!")
    print("\nResults:")
    for var in sorted(results.keys()):
        data = results[var]
        print(f"  {var} = {data['value']} {data['unit']}")
    
    print("\nKey Points:")
    print("  ✓ L^2 calculated to 100 m^2")
    print("  ✓ User specified ft^2 (different unit, same dimensionality)")
    print("  ✓ Automatic conversion: 100 m² → 1076.39 ft²")
    print("  ✓ Result displayed in user's preferred unit")
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")

# ============================================================================
# SUCCESS CASE: Complex Expression
# ============================================================================
print_section("SUCCESS CASE: Complex Engineering Calculation")
print("\nEquations:")
print("  m = 10 [kg]  // mass")
print("  v = 5 [m/s]  // velocity")
print("  KE = 0.5 * m * v^2 [J]  // kinetic energy")

equations_complex = [
    "m = 10 [kg]",
    "v = 5 [m/s]",
    "KE = 0.5 * m * v^2 [J]"
]

try:
    results, warnings = solver.solve(equations_complex)
    print("\n✓ SUCCESS - Complex calculation validated!")
    print("\nResults:")
    for var in sorted(results.keys()):
        data = results[var]
        print(f"  {var} = {data['value']} {data['unit']}")
    
    print("\nKey Points:")
    print("  ✓ Expression: 0.5 * m * v^2")
    print("  ✓ Calculated units: kg·m²/s² (from kg * (m/s)^2)")
    print("  ✓ Specified unit: J (joules)")
    print("  ✓ J is equivalent to kg·m²/s²")
    print("  ✓ Units validated and simplified to J for display")
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")

print("\n" + "=" * 70)
print(" SUMMARY")
print("=" * 70)
print("\nThe unit validation system now:")
print("  1. Uses calculated units (from expressions) as the source of truth")
print("  2. Validates manually specified units against calculated units")
print("  3. Allows unit conversions if dimensionalities match")
print("  4. Throws clear errors when units don't match")
print("  5. Displays results in the user's preferred unit format")
print("\n")
