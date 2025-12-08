import pytest
import math
from solver.numerical import NumericalSolver

class TestAngleUnits:
    def setup_method(self):
        self.solver = NumericalSolver()

    def test_explicit_degrees(self):
        equations = [
            "x = 30 [deg]",
            "y = sin(x)"
        ]
        results, _ = self.solver.solve(equations)
        assert results['y']['value'] == pytest.approx(0.5)
        assert results['x']['value'] == 30

    def test_explicit_radians(self):
        equations = [
            "x = 3.14159265359 / 6 [rad]",
            "y = sin(x)"
        ]
        results, _ = self.solver.solve(equations)
        assert results['y']['value'] == pytest.approx(0.5)

    def test_implicit_degrees_default(self):
        equations = [
            "x = 30",
            "y = sin(x)"
        ]
        results, _ = self.solver.solve(equations, angle_unit='deg')
        assert results['y']['value'] == pytest.approx(0.5)

    def test_implicit_radians_default(self):
        equations = [
            "x = 3.14159265359 / 6",
            "y = sin(x)"
        ]
        results, _ = self.solver.solve(equations, angle_unit='rad')
        assert results['y']['value'] == pytest.approx(0.5)

    def test_inverse_trig_units(self):
        equations = [
            "y = 0.5",
            "x = asin(y)"
        ]
        results, _ = self.solver.solve(equations, angle_unit='deg')
        assert results['x']['value'] == pytest.approx(30)
        # Check inferred unit
        assert results['x']['unit'] == 'deg' or results['x']['unit'] == 'degree'

    def test_inverse_trig_units_rad(self):
        equations = [
            "y = 0.5",
            "x = asin(y)"
        ]
        results, _ = self.solver.solve(equations, angle_unit='rad')
        assert results['x']['value'] == pytest.approx(math.pi/6)
        # Check inferred unit
        assert results['x']['unit'] == 'rad' or results['x']['unit'] == 'radian'

    def test_mixed_units_conversion(self):
        # x is in rad, but we calculate sin(x). 
        # Should work regardless of default angle_unit because x has explicit units.
        equations = [
            "x = 1 [rad]",
            "y = sin(x)"
        ]
        # Even if default is deg, sin(1 rad) should be sin(1 radian) approx 0.84, not sin(1 degree) approx 0.017
        results, _ = self.solver.solve(equations, angle_unit='deg')
        assert results['y']['value'] == pytest.approx(math.sin(1))
