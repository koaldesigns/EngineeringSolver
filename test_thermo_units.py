
import unittest
from backend.solver.numerical import NumericalSolver

class TestThermoUnitPropagation(unittest.TestCase):
    def test_mass_flow_with_density(self):
        solver = NumericalSolver()
        equations = [
            "// Pipe flow calculation",
            "D = 0.1 [m]              // Diameter",
            "L = 50 [m]               // Length",
            "V = 2 [m/s]              // Velocity",
            "rho = prop('Air', 'D', 'T', 300, 'P', 101325)",
            "",
            "// Calculate area and volume",
            "A = 3.14159 * (D/2)^2",
            "Vol = A * L",
            "",
            "// Flow rate (mass flow)",
            "Q = A * V * rho"
        ]
        
        results, warnings = solver.solve(equations)
        
        print("Results:")
        for var, data in sorted(results.items()):
            print(f"  {var} = {data['value']:.6g} [{data['unit']}]")
        print("Warnings:", warnings)
        
        # Check units
        # A should be m^2
        self.assertEqual(str(results["A"]["unit"]), "m ** 2")
        # Vol should be m^3
        self.assertEqual(str(results["Vol"]["unit"]), "m ** 3")
        # rho should be kg/m^3
        self.assertEqual(str(results["rho"]["unit"]), "kg / m ** 3")
        # Q should be kg/s (mass flow rate = area * velocity * density)
        # m^2 * m/s * kg/m^3 = kg/s
        self.assertEqual(str(results["Q"]["unit"]), "kg / s")

if __name__ == "__main__":
    unittest.main()
