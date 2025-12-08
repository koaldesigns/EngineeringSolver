
import unittest
from backend.solver.numerical import NumericalSolver

class TestUnitPropagation(unittest.TestCase):
    def test_complex_example_propagation(self):
        solver = NumericalSolver()
        equations = [
            "// Pipe flow calculation",
            "D = 0.1 [m]              // Diameter",
            "L = 50 [m]               // Length",
            "V = 2 [m/s]              // Velocity",
            "",
            "// Calculate area and volume",
            "A = 3.14159 * (D/2)^2",
            "Vol = A * L",
            "",
            "// Flow rate",
            "Q = A * V"
        ]
        
        results, warnings = solver.solve(equations)
        
        print("Results:", results)
        print("Warnings:", warnings)
        
        self.assertIn("A", results)
        self.assertIn("Vol", results)
        self.assertIn("Q", results)
        
        # Check units
        # A should be m^2
        self.assertEqual(str(results["A"]["unit"]), "m ** 2")
        # Vol should be m^3
        self.assertEqual(str(results["Vol"]["unit"]), "m ** 3")
        # Q should be m^3/s
        self.assertEqual(str(results["Q"]["unit"]), "m ** 3 / s")

if __name__ == "__main__":
    unittest.main()
