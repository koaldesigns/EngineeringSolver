import pytest
import math
from solver.numerical import NumericalSolver

class TestExtremeUnits:
    def setup_method(self):
        self.solver = NumericalSolver()

    def test_summation_with_units(self):
        # Sum of i * 10 kg for i=1 to 5
        # 10 + 20 + 30 + 40 + 50 = 150 kg
        equations = [
            "total = sum(lambda i: i * 10 [kg], 1, 5)"
        ]
        results, _ = self.solver.solve(equations)
        assert results['total']['value'] == pytest.approx(150)
        assert results['total']['unit'] == 'kg' or results['total']['unit'] == 'kilogram'

    def test_integral_simple_units(self):
        # Integral of 5 [m/s] dt from 0 to 10 [s]
        # Should be 50 [m]
        equations = [
            "dist = integral(lambda t: 5 [m/s], 0 [s], 10 [s])"
        ]
        results, _ = self.solver.solve(equations)
        assert results['dist']['value'] == pytest.approx(50)
        assert results['dist']['unit'] == 'm' or results['dist']['unit'] == 'meter'

    def test_integral_variable_units(self):
        # Integral of (2*t [m/s^2]) dt from 0 to 5 [s]
        # v = at. Integral is distance.
        # int(2t) = t^2. [0,5] -> 25.
        # Unit: (m/s^2) * s * s (from t inside) * s (from dt) ???
        # Wait. lambda t: 2*t.
        # If t has units [s].
        # 2 * t -> [s].
        # If we want acceleration 2 [m/s^2].
        # lambda t: 2 [m/s^2] * t.
        # t is [s]. Result is [m/s].
        # Integral of [m/s] dt ([s]) -> [m].
        
        equations = [
            "dist = integral(lambda t: 2 [m/s^2] * t, 0 [s], 5 [s])"
        ]
        results, _ = self.solver.solve(equations)
        # int(2t) = t^2. 5^2 - 0 = 25.
        assert results['dist']['value'] == pytest.approx(25)
        assert results['dist']['unit'] == 'm' or results['dist']['unit'] == 'meter'

    def test_derivative_units(self):
        # Derivative of x^2 at x=3.
        # f(x) = x^2. f'(x) = 2x. at 3 -> 6.
        # If x has units [m]. f(x) -> [m^2].
        # f'(x) -> [m^2] / [m] = [m].
        
        equations = [
            "slope = derivative(lambda x: x^2, 3 [m])"
        ]
        results, _ = self.solver.solve(equations)
        assert results['slope']['value'] == pytest.approx(6, rel=1e-4)
        assert results['slope']['unit'] == 'm' or results['slope']['unit'] == 'meter'

    def test_derivative_velocity(self):
        # Position x(t) = 0.5 * a * t^2
        # a = 9.8 [m/s^2]
        # v(t) = dx/dt = a * t
        # at t=2s, v should be 19.6 [m/s]
        
        equations = [
            "a = 9.8 [m/s^2]",
            "v_at_2 = derivative(lambda t: 0.5 * a * t^2, 2 [s])"
        ]
        results, _ = self.solver.solve(equations)
        assert results['v_at_2']['value'] == pytest.approx(19.6, rel=1e-4)
        # Unit check: (m/s^2 * s^2) / s = m/s
        assert results['v_at_2']['unit'] == 'm/s' or results['v_at_2']['unit'] == 'meter / second'

    def test_nested_calculus(self):
        # Work = integral of Force dot dx
        # Force = mass * acceleration
        # mass = 10 kg
        # accel(t) = 2 * t [m/s^3] (jerk constant)
        # F(t) = 10 * 2 * t = 20t [N]
        # Distance x(t) ... wait, work is integral F dx.
        # Or integral F(t) * v(t) dt.
        # Let's do Impulse = integral F dt.
        # Impulse = integral(10 [kg] * 2 [m/s^3] * t, 0 [s], 5 [s])
        # integrand = 20t [kg m/s^3 * s] = 20t [kg m/s^2] = 20t [N]
        # integral 20t dt = 10t^2. [0,5] -> 10*25 = 250.
        # Unit: [N] * [s] = [N s] = [kg m/s].
        
        equations = [
            "mass = 10 [kg]",
            "impulse = integral(lambda t: mass * 2 [m/s^3] * t, 0 [s], 5 [s])"
        ]
        results, _ = self.solver.solve(equations)
        assert results['impulse']['value'] == pytest.approx(250)
        # Check unit compatibility with kg*m/s
        # We can't easily check exact string match for complex units, 
        # but we can check if it contains expected dimensions.
        # Or we can rely on the solver's formatting.
        # Pint might format as 'kilogram * meter / second'
        u = results['impulse']['unit']
        assert 'kg' in u or 'kilogram' in u
        assert 'm' in u or 'meter' in u
        assert 's' in u or 'second' in u
