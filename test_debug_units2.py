"""
Debug test for end-of-line unit specification
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver
from backend.solver.parser import EquationParser

solver = NumericalSolver()
parser = EquationParser()

# Test with end-of-line unit (not inline)
equations = [
    "x = 5",
    "z = x^2",  # No units
    "y [kg] = z"  # Unit on LHS
]

eq_text = "\n".join(equations)
variables, normalized_eqs, variable_units = parser.parse(eq_text)

print("Test 1: LHS unit specification")
print(f"  Variables: {variables}")
print(f"  Variable units: {variable_units}")

assignments = parser.extract_assignments(equations)
print(f"  Assignments: {assignments}")

try:
    results, warnings = solver.solve(equations)
    print("\nResults:")
    for var, data in results.items():
        print(f"  {var} = {data['value']} [{data['unit']}]")
    print(f"\nWarnings: {warnings if warnings else 'None'}")
except Exception as e:
    print(f"Error: {e}")

# Another test - simpler
print("\n" + "="*60)
equations2 = [
    "a = 5 + 3 [m]"  # This should be: dimensionless + 3m, but the parser might interpret differently
]

eq_text2 = "\n".join(equations2)
variables2, normalized_eqs2, variable_units2 = parser.parse(eq_text2)

print("\nTest 2: Inline unit in expression")
print(f"  Variables: {variables2}")
print(f"  Variable units: {variable_units2}")

assignments2 = parser.extract_assignments(equations2)
print(f"  Assignments: {assignments2}")

try:
    results2, warnings2 = solver.solve(equations2)
    print("\nResults:")
    for var, data in results2.items():
        print(f"  {var} = {data['value']} [{data['unit']}]")
    print(f"\nWarnings: {warnings2 if warnings2 else 'None'}")
except Exception as e:
    print(f"Error: {e}")
