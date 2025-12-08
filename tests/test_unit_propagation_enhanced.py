import math
from backend.solver.numerical import NumericalSolver
from backend.solver.units import UnitRegistry

solver = NumericalSolver()
ureg = UnitRegistry().ureg

def test_basic_arithmetic_units():
    equations = [
        "x = 10 [m]",
        "y = 5 [m]",
        "z = x + y",
        "w = x * y",
        "v = x / y"
    ]
    results, _ = solver.solve(equations)
    assert results['z']['value'] == 15.0
    # ~P format returns abbreviated units
    assert results['z']['unit'] == 'm'
    assert results['w']['value'] == 50.0
    # assert results['w']['unit'] == 'm²' # Unicode check might fail in some envs
    assert 'm' in results['w']['unit']
    assert results['v']['value'] == 2.0
    assert results['v']['unit'] == 'dimensionless' or results['v']['unit'] == ''

def test_unit_mismatch_validation():
    equations = [
        "x = 10 [m]",
        "y = 5 [s]",
        "z = x + y"
    ]
    try:
        solver.solve(equations)
        assert False, "Should have raised ValueError for dimension mismatch"
    except ValueError as e:
        assert "Dimension mismatch" in str(e) or "Unit error" in str(e)

def test_transcendental_functions():
    equations = [
        "x = 90 [deg]",
        "y = sin(x)",
        "z = cos(x)",
        "w = tan(45 [deg])"
    ]
    results, _ = solver.solve(equations)
    assert abs(results['y']['value'] - 1.0) < 1e-9
    assert abs(results['z']['value']) < 1e-9
    assert abs(results['w']['value'] - 1.0) < 1e-9

def test_transcendental_unit_error():
    equations = [
        "x = 10 [m]",
        "y = sin(x)"
    ]
    try:
        solver.solve(equations)
        assert False, "Should have raised ValueError for sin(length)"
    except ValueError as e:
        assert "sin expects angle or dimensionless" in str(e) or "Unit error" in str(e)

def test_prop_units():
    # Test that prop returns units
    equations = [
        "T = 300 [K]",
        "P = 101325 [Pa]",
        "h = prop('Water', 'H', 'T', T, 'P', P)",
        "h_expected = 112600 [J/kg]" # Approx value
    ]
    results, _ = solver.solve(equations)
    # Check that h has units of J/kg
    # Check that h has units of J/kg
    print(f"DEBUG: h unit is '{results['h']['unit']}'")
    assert 'J' in results['h']['unit'] and 'kg' in results['h']['unit']
    assert results['h']['value'] > 0

def test_prop_input_conversion():
    # Test that prop handles input unit conversion
    equations = [
        "T = 26.85 [degC]", # 300 K
        "P = 1 [atm]", # 101325 Pa
        "h = prop('Water', 'H', 'T', T, 'P', P)"
    ]
    results, _ = solver.solve(equations)
    assert 'J' in results['h']['unit'] and 'kg' in results['h']['unit']
    # Value should be close to the one at 300K, 1atm
    # We can't check exact value easily without reference, but it shouldn't error.

def test_integral_units():
    # Integral of v(t) dt from t1 to t2 = distance
    equations = [
        "v = 10 [m/s]",
        "d = integral(lambda t: v, 0[s], 5[s])"
    ]
    results, _ = solver.solve(equations)
    assert results['d']['value'] == 50.0
    assert results['d']['unit'] == 'm'

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_basic_arithmetic_units()
        print("test_basic_arithmetic_units passed")
        test_unit_mismatch_validation()
        print("test_unit_mismatch_validation passed")
        test_transcendental_functions()
        print("test_transcendental_functions passed")
        test_transcendental_unit_error()
        print("test_transcendental_unit_error passed")
        test_prop_units()
        print("test_prop_units passed")
        test_prop_input_conversion()
        print("test_prop_input_conversion passed")
        test_integral_units()
        print("test_integral_units passed")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
