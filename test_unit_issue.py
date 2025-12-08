"""
Test script to reproduce the unit double-counting issue
"""
from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

equations = [
    "L = 10 [m]",
    "T = 25 [degC]",
    "P = 100 [kPa]",
    "// Calculate area",
    "A = L^2 [m^2]"
]

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
