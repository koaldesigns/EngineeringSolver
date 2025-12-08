
from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

print("--- Test Case 4: Explicit Dimensionless '[-]' -> Dimensional ---")
# x is explicitly dimensionless. y is assigned [kg].
# We expect a WARNING here because x is not just a raw number, it's a Quantity(5, 'dimensionless')
eq4 = [
    "x = 5 [-]",
    "y = x [kg]"
]
res4, warn4 = solver.solve(eq4)
print(f"Results: {res4}")
print(f"Warnings: {warn4}")
