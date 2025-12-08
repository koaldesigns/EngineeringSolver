import pytest
import math
from solver.numerical import NumericalSolver

@pytest.fixture
def solver():
    return NumericalSolver()

def test_e_constant(solver):
    # Test e as a constant
    eqs = ["y = e"]
    res, warnings = solver.solve(eqs)
    assert abs(res['y']['value'] - math.e) < 1e-10
    
    # Test e as a variable
    eqs = ["e = 5", "y = e"]
    res, warnings = solver.solve(eqs)
    assert abs(res['y']['value'] - 5.0) < 1e-10
    assert abs(res['e']['value'] - 5.0) < 1e-10

def test_trig_units(solver):
    # Test sin with degrees
    eqs = ["x = sin(90 [deg])"]
    res, warnings = solver.solve(eqs)
    assert abs(res['x']['value'] - 1.0) < 1e-10
    
    # Test sin with radians
    eqs = ["x = sin(pi/2 [rad])"]
    res, warnings = solver.solve(eqs)
    assert abs(res['x']['value'] - 1.0) < 1e-10

    # Test output unit of asin (should be deg by default)
    eqs = ["x = asin(1)"]
    res, warnings = solver.solve(eqs)
    assert abs(res['x']['value'] - 90.0) < 1e-10
    assert res['x']['unit'] == 'deg'

def test_log_exp_units(solver):
    # Test exp with units
    # a = exp(1) [m] -> a should be e meters
    eqs = ["a = exp(1) [m]"]
    res, warnings = solver.solve(eqs)
    assert abs(res['a']['value'] - math.e) < 1e-10
    assert res['a']['unit'] == 'm'
    
    # Test log
    # b = log(a/1[m])
    eqs = ["a = exp(1) [m]", "b = log(a/1[m])"]
    res, warnings = solver.solve(eqs)
    assert abs(res['b']['value'] - 1.0) < 1e-10

def test_water_properties(solver):
    # Test prop call with units
    # Enthalpy of water at 100C and 1 bar
    # 100 C = 373.15 K
    # 1 bar = 100000 Pa
    # CoolProp H for Water at 373.15K, 1e5Pa is approx 2676 kJ/kg (vapor) or 419 kJ/kg (liquid)?
    # At 100C, 1 bar is saturation. It might be tricky.
    # Let's use 300K, 1 bar (liquid)
    # T=300K, P=100kPa.
    eqs = ["h = prop('Water', 'H', 'T', 300[K], 'P', 1[bar])"]
    res, warnings = solver.solve(eqs)
    # Just check it runs and returns a value with units
    assert res['h']['value'] > 0
    assert res['h']['unit'] == 'J/kg'

    # Test with C and kPa
    eqs = ["h = prop('Water', 'H', 'T', 25[C], 'P', 100[kPa])"]
    res, warnings = solver.solve(eqs)
    assert res['h']['value'] > 0
    assert res['h']['unit'] == 'J/kg'

def test_unit_display(solver):
    # Test Reynolds number simplification
    # Re = (rho * v * L) / mu
    # rho: kg/m^3, v: m/s, L: m, mu: Pa*s = kg/(m*s)
    # Re units: (kg/m^3 * m/s * m) / (kg/(m*s))
    # = (kg/m/s) / (kg/m/s) = dimensionless
    
    eqs = [
        "rho = 1000 [kg/m^3]",
        "v = 2 [m/s]",
        "L = 0.1 [m]",
        "mu = 0.001 [Pa*s]",
        "Re = rho * v * L / mu"
    ]
    res, warnings = solver.solve(eqs)
    assert res['Re']['unit'] == "" # Should be dimensionless

    # Test J/K/kg display
    # cp = 4180 [J/kg/K]
    eqs = ["cp = 4180 [J/kg/K]"]
    res, warnings = solver.solve(eqs)
    # We expect some formatting, maybe J/K/kg or J/(K·kg)
    # Just check it's not crazy
    print(f"CP Unit: {res['cp']['unit']}")
    assert 'J' in res['cp']['unit']
