"""
Debug test 3 issue
"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from backend.solver.numerical import NumericalSolver
from backend.solver.parser import EquationParser

solver = NumericalSolver()
parser = EquationParser()

equations = [
    "x = 5",
    "y = x^2 [m]"
]

# First, let's see what the parser extracts
eq_text = "\n".join(equations)
variables, normalized_eqs, variable_units = parser.parse(eq_text)

print("Parser Output:")
print(f"  Variables: {variables}")
print(f"  Variable Units: {variable_units}")
print(f"  Normalized Equations: {normalized_eqs}")

assignments = parser.extract_assignments(equations)
print(f"  Assignments: {assignments}")

print("\n" + "="*60)

try:
    results, warnings = solver.solve(equations)
    print("Results:")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
