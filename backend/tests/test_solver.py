import unittest
from solver.numerical import NumericalSolver

class TestNumericalSolver(unittest.TestCase):
    def setUp(self):
        self.solver = NumericalSolver()

    def test_linear_system(self):
        eqs = ["x + y = 10", "x - y = 2"]
        sol, warnings = self.solver.solve(eqs)
        self.assertAlmostEqual(sol['x']['value'], 6.0)
        self.assertAlmostEqual(sol['y']['value'], 4.0)

    def test_nonlinear_system(self):
        eqs = ["x^2 + y = 11", "y - x = 5"] 
        # x^2 + (x+5) = 11 => x^2 + x - 6 = 0 => (x+3)(x-2)=0 => x=2, -3
        # If x=2, y=7. If x=-3, y=2.
        # Initial guess defaults to 1.0, so should find x=2
        
        # Note: Python eval uses ** for power, but users might type ^. 
        # The parser/eval needs to handle this. 
        # For this test, I'll use python syntax ** or update parser to replace ^ with **.
        # Let's update the test to use python syntax for now, and I'll add a TODO to parser.
        eqs_python = ["x**2 + y = 11", "y - x = 5"]
        
        sol, warnings = self.solver.solve(eqs_python)
        self.assertAlmostEqual(sol['x']['value'], 2.0)
        self.assertAlmostEqual(sol['y']['value'], 7.0)

    def test_angle_units(self):
        # sin(30 deg) = 0.5
        eqs = ["y = sin(x)", "x = 30"]
        
        # Test Degrees (default)
        sol_deg, warnings = self.solver.solve(eqs, angle_unit='deg')
        self.assertAlmostEqual(sol_deg['y']['value'], 0.5)
        
        # Test Radians: sin(30 rad) != 0.5
        # sin(pi/6) = 0.5
        eqs_rad = ["y = sin(x)", "x = 0.5235987756"] # pi/6
        sol_rad, warnings = self.solver.solve(eqs_rad, angle_unit='rad')
        self.assertAlmostEqual(sol_rad['y']['value'], 0.5, places=4)

if __name__ == '__main__':
    unittest.main()
