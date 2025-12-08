"""
Debug test for dimensionless + dimensional unit case
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver
from backend.solver.parser import EquationParser

solver = NumericalSolver()
parser = EquationParser()

equations = [
    "x = 5",
    "y = x * 2 [kg]"
]

# Parse to see what we get
eq_text = "\n".join(equations)
variables, normalized_eqs, variable_units = parser.parse(eq_text)

print("Parser output:")
print(f"  Variables: {variables}")
print(f"  Variable units: {variable_units}")

assignments = parser.extract_assignments(equations)
print(f"  Assignments: {assignments}")

print("\nSolving...")
try:
    results, warnings = solver.solve(equations)
    print("\nResults:")
    for var, data in results.items():
        print(f"  {var} = {data['value']} [{data['unit']}]")
    print(f"\nWarnings: {warnings}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
