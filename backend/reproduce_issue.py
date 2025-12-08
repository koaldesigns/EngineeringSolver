from solver.numerical import NumericalSolver
import pprint

solver = NumericalSolver()
equations = [
    "L = 10 [m]",
    "T = 25 [degC]",
    "P = 100 [kPa]",
    "// Calculate area",
    "A = L^2  [m^2]"
]

print("Solving equations:")
pprint.pprint(equations)

try:
    solution, warnings = solver.solve(equations)
    print("\nSolution:")
    for var, details in solution.items():
        print(f"{var}: {details['value']} {details.get('unit', '')}")
    
    print("\nWarnings:")
    pprint.pprint(warnings)

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"\nError: {e}")
