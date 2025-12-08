"""
Final Demo: Warning-Based Unit Validation System

This demonstrates the new behavior where unit mismatches generate warnings
instead of errors, allowing calculations to proceed.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver

def print_results(title, equations_text, results, warnings):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)
    print("\nEquations:")
    for eq in equations_text:
        print(f"  {eq}")
    print("\nResults:")
    for var in sorted(results.keys()):
        data = results[var]
        unit_str = f" {data['unit']}" if data['unit'] else ""
        print(f"  {var} = {data['value']}{unit_str}")
    if warnings:
        print("\n⚠️  Warnings:")
        for w in warnings:
            print(f"  • {w}")
    else:
        print("\n✓ No warnings")

solver = NumericalSolver()

# =============================================================================
# Example 1: USER'S ORIGINAL CASE - Correct Units
# =============================================================================
eqs1 = [
    "L = 10 [m]",
    "T = 25 [degC]",
    "P = 100 [kPa]",
    "// Calculate area",
    "A = L^2 [m^2]"
]

results1, warnings1 = solver.solve(eqs1)
print_results(
    "Example 1: User's Original Case (Matching Units)",
    eqs1,
    results1,
    warnings1
)
print("\nExplanation:")
print("  • L^2 calculates to m²")
print("  • Specified unit is [m^2]")
print("  • Units match ✓")
print("  • Result displayed in user's preferred format (m²)")

# =============================================================================
# Example 2: Unit Mismatch - Now Warns Instead of Failing
# =============================================================================
eqs2 = [
    "x = 5",
    "y [kg] = x + 20"  # y is dimensionless but user specified [kg]
]

results2, warnings2 = solver.solve(eqs2)
print_results(
    "Example 2: Dimensionless Result with Dimensional Unit Specified",
    eqs2,
    results2,
    warnings2
)
print("\nExplanation:")
print("  • x + 20 is dimensionless (no units)")
print("  • User specified [kg] for variable y")
print("  • System generates WARNING instead of error")
print("  • Calculation proceeds using dimensionless result")

# =============================================================================
# Example 3: Compatible Unit Conversion
# =============================================================================
eqs3 = [
    "L = 10 [m]",
    "A = L^2 [ft^2]"  # User wants area in ft^2 instead of m^2
]

results3, warnings3 = solver.solve(eqs3)
print_results(
    "Example 3: Automatic Unit Conversion (Matching Dimensionality)",
    eqs3,
    results3,
    warnings3
)
print("\nExplanation:")
print("  • L^2 calculates to 100 m²")
print("  • User specified [ft^2]")
print("  • Both are area units (same dimensionality)")
print("  • System automatically converts: 100 m² → 1076.39 ft²")

# =============================================================================
# Example 4: Complex Engineering Calculation
# =============================================================================
eqs4 = [
    "mass = 50 [kg]",
    "velocity = 20 [m/s]",
    "// Kinetic energy in Joules",
    "KE = 0.5 * mass * velocity^2 [J]"
]

results4, warnings4 = solver.solve(eqs4)
print_results(
    "Example 4: Complex Calculation with Unit Validation",
    eqs4,
    results4,
    warnings4
)
print("\nExplanation:")
print("  • Expression: 0.5 * 50 kg * (20 m/s)^2")
print("  • Calculated units: kg·m²/s²")
print("  • Specified unit: J (Joules)")
print("  • J ≡ kg·m²/s² (equivalent units)")
print("  • System validates and displays as J")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print(" SUMMARY: Warning-Based Unit Validation")
print("=" * 70)
print("""
Key Features:
  1. ✓ Calculations CONTINUE even when units don't match
  2. ✓ Clear WARNINGS generated for unit mismatches
  3. ✓ Calculated units used when they don't match specified units
  4. ✓ Automatic conversion when dimensionalities match
  5. ✓ User's preferred unit format respected when valid
  
Benefits:
  • No more calculation failures due to unit typos
  • Users are informed about unit issues via warnings
  • Flexibility to specify output unit format
  • Safer iteration during equation development
  
Warning Messages Are Clear:
  "Variable '{name}': Calculated units ({calc}) do not match 
   specified units ({spec}). Using calculated units."
""")
