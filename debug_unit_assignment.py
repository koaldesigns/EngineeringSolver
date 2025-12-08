
from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

print("--- Test Case 1: Dimensionless -> Dimensional ---")
# x has no units. y gets assigned [kg].
eq1 = [
    "x = 5",
    "y = x * 2 [kg]"
]
res1, warn1 = solver.solve(eq1)
print(f"Results: {res1}")
print(f"Warnings: {warn1}")

print("\n--- Test Case 2: Dimensional A -> Dimensional B (Mismatch) ---")
# x is meters. y is assigned [kg].
eq2 = [
    "x = 5 [m]",
    "y = x [kg]"
]
try:
    res2, warn2 = solver.solve(eq2)
    print(f"Results: {res2}")
    print(f"Warnings: {warn2}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Test Case 3: Dimensional A -> Dimensional A (Match) ---")
# x is meters. y is assigned [ft]. Should convert.
eq3 = [
    "x = 10 [m]",
    "y = x [ft]"
]
res3, warn3 = solver.solve(eq3)
print(f"Results: {res3}")
print(f"Warnings: {warn3}")
