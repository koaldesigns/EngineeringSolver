import unittest
from solver.units import UnitRegistry

class TestUnitRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = UnitRegistry()

    def test_basic_conversion(self):
        val = self.registry.convert(1, 'meter', 'centimeter')
        self.assertAlmostEqual(val, 100.0)

    def test_temperature_conversion(self):
        # Pint handles temp conversions (requires delta for offset units usually, but let's check basic)
        val = self.registry.convert(0, 'degC', 'degF')
        self.assertAlmostEqual(val, 32.0)

    def test_incompatible_units(self):
        with self.assertRaises(ValueError):
            self.registry.convert(1, 'meter', 'second')

    def test_unknown_unit(self):
        with self.assertRaises(ValueError):
            self.registry.convert(1, 'flibberflabber', 'meter')

    def test_ees_aliases(self):
        # Test C -> F
        val = self.registry.convert(100, 'C', 'F')
        self.assertAlmostEqual(val, 212.0)
        
        # Test psia -> psi
        val = self.registry.convert(100, 'psia', 'psi')
        self.assertAlmostEqual(val, 100.0)
        
        # Test lbm
        val = self.registry.convert(1, 'lbm', 'kg')
        self.assertAlmostEqual(val, 0.45359237)

if __name__ == '__main__':
    unittest.main()
