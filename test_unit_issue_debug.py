"""
Test script to reproduce the unit double-counting issue with debugging
"""
from backend.solver.numerical import NumericalSolver
from backend.solver.parser import EquationParser

solver = NumericalSolver()
parser = EquationParser()

equations = [
    "L = 10 [m]",
    "T = 25 [degC]",
    "P = 100 [kPa]",
    "// Calculate area",
    "A = L^2 [m^2]"
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
print("Running solver...")
print("="*60 + "\n")

try:
    results, warnings = solver.solve(equations)
    print("Results:")
    for var, data in results.items():
        print(f"  {var} = {data['value']} {data['unit']}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
