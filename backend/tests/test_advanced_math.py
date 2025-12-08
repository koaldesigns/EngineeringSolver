import unittest
from solver.numerical import NumericalSolver

class TestAdvancedMath(unittest.TestCase):
    def setUp(self):
        self.solver = NumericalSolver()

    def test_summation(self):
        # sum(i^2, i, 1, 3) = 1 + 4 + 9 = 14
        eqs = ["y = sum(i^2, i, 1, 3)"]
        sol, warnings = self.solver.solve(eqs)
        self.assertAlmostEqual(sol['y']['value'], 14.0)

    def test_integral(self):
        # integral(x^2, x, 0, 1) = [x^3/3] from 0 to 1 = 1/3
        eqs = ["area = integral(x^2, x, 0, 1)"]
        sol, warnings = self.solver.solve(eqs)
        self.assertAlmostEqual(sol['area']['value'], 1.0/3.0)

    def test_integral_with_trig(self):
        # integral(cos(x), x, 0, 90) with deg mode?
        # Note: The integral function inside uses scipy.integrate.quad which expects the function to return values.
        # Our context['cos'] handles degrees if angle_unit='deg'.
        # So if we pass angle_unit='deg', cos(x) expects x in degrees.
        # But quad passes x. Does quad pass x in degrees? No, quad just passes numbers.
        # If we say integral(cos(theta), theta, 0, 90), we expect theta to go 0..90.
        # And cos(theta) should treat theta as degrees.
        # Let's verify this behavior.
        
        eqs = ["val = integral(cos(t), t, 0, 90)"]
        # integral of cos(x) dx from 0 to 90 degrees.
        # If x is in degrees, we are integrating cos(x_deg) dx_deg?
        # Mathematically, integral(cos(x degrees) dx) = sin(x degrees) * (180/pi) ?
        # No, usually integration is over the variable as is.
        # If t goes 0 to 90, and we evaluate cos(t) where t is degrees.
        # Then we are computing sum(cos(t_i) * dt).
        # This is effectively integral of cos(t) dt where t is in degrees.
        # Result should be roughly sum of cos(0)..cos(90).
        # Real integral of cos(x) from 0 to pi/2 is 1.
        # Here we integrate from 0 to 90.
        # If we want the result to be 1, we need to convert dx too? 
        # EES usually handles this by assuming the variable of integration matches the trig mode?
        # Let's just check what our code does:
        # It integrates `lambda t: cos(t)` from 0 to 90.
        # `cos(t)` converts t (deg) to rad, then takes cos.
        # So it integrates cos(t * pi/180) dt from 0 to 90.
        # Let u = t * pi/180 => du = pi/180 dt => dt = 180/pi du
        # Limits: 0 -> 0, 90 -> pi/2
        # Integral = integral(cos(u) * 180/pi du) = 180/pi * [sin(u)]_0^pi/2 = 180/pi * 1 = 57.29...
        
        sol, warnings = self.solver.solve(eqs, angle_unit='deg')
        import math
        self.assertAlmostEqual(sol['val']['value'], 180/math.pi, places=2)

if __name__ == '__main__':
    unittest.main()
