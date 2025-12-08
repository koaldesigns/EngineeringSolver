from solver.numerical import NumericalSolver
from solver.units import UnitRegistry

def test_solver_prop():
    print("\nTesting Solver Prop")
    solver = NumericalSolver()
    units = UnitRegistry()
    print(f"Formatted 'deg': '{units.format_unit_display('deg')}'")
    print(f"Formatted 'degree': '{units.format_unit_display('degree')}'")
    
    eqs = [
        "angle = 45 [deg]",
        "s = sin(angle)",
        "c = cos(angle)",
        "t = tan(angle)",
        "check = s^2 + c^2"
    ]
    try:
        res, warnings = solver.solve(eqs)
        print(f"Solver Result: {res}")
    except Exception as e:
        print(f"Solver Error: {e}")

if __name__ == "__main__":
    test_solver_prop()
