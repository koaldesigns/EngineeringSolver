import pint
import math
from backend.solver.numerical import NumericalSolver

solver = NumericalSolver()

def test_log_unit_behavior():
    print("Testing log(kg)...")
    equations = [
        "a = exp(1) [kg]",
        "b = log(a)"
    ]
    try:
        results, _ = solver.solve(equations)
        print("Result:", results)
    except Exception as e:
        print(f"Caught expected error: {e}")

    print("\nTesting log(ratio)...")
    equations_ratio = [
        "a = exp(1) [kg]",
        "b = log(a / 1 [kg])"
    ]
    try:
        results, _ = solver.solve(equations_ratio)
        print("Result (ratio):", results)
    except Exception as e:
        print(f"Caught error (ratio): {e}")

if __name__ == "__main__":
    test_log_unit_behavior()
