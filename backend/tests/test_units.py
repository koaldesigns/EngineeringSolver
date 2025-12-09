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

    # ===== Compound Unit Tests =====
    
    def test_compound_velocity_conversion(self):
        """Test velocity compound unit conversions (m/s)"""
        # m/s to km/h (1 m/s = 3.6 km/h)
        val = self.registry.convert(10, 'm/s', 'km/h')
        self.assertAlmostEqual(val, 36.0, places=2)
        
        # m/s to ft/s (1 m/s ≈ 3.28084 ft/s)
        val = self.registry.convert(1, 'm/s', 'ft/s')
        self.assertAlmostEqual(val, 3.28084, places=4)
    
    def test_compound_density_conversion(self):
        """Test density compound unit conversions (kg/m^3)"""
        # kg/m^3 to g/cm^3 (1000 kg/m^3 = 1 g/cm^3)
        val = self.registry.convert(1000, 'kg/m^3', 'g/cm^3')
        self.assertAlmostEqual(val, 1.0, places=4)
        
        # kg/m^3 to lb/ft^3 (1 kg/m^3 ≈ 0.0624 lb/ft^3)
        val = self.registry.convert(1, 'kg/m^3', 'lb/ft^3')
        self.assertAlmostEqual(val, 0.0624, places=3)
    
    def test_compound_mass_flow_conversion(self):
        """Test mass flow rate compound unit conversions (kg/s)"""
        # kg/s to lb/s (1 kg/s ≈ 2.205 lb/s)
        val = self.registry.convert(1, 'kg/s', 'lb/s')
        self.assertAlmostEqual(val, 2.205, places=2)
        
        # kg/s to g/min (1 kg/s = 60000 g/min)
        val = self.registry.convert(1, 'kg/s', 'g/min')
        self.assertAlmostEqual(val, 60000.0, places=0)
    
    def test_compound_specific_heat_conversion(self):
        """Test specific heat compound unit conversions (J/(kg*K))"""
        # J/(kg*K) to kJ/(kg*K) (4186 J/(kg*K) = 4.186 kJ/(kg*K))
        val = self.registry.convert(4186, 'J/(kg*K)', 'kJ/(kg*K)')
        self.assertAlmostEqual(val, 4.186, places=3)

    # ===== Unit Suggestion Tests =====
    
    def test_suggestions_basic_units(self):
        """Test suggestions for basic single units"""
        # Length
        suggestions = self.registry.get_compatible_units('m')
        self.assertIn('ft', suggestions)
        self.assertIn('cm', suggestions)
        
        # Mass
        suggestions = self.registry.get_compatible_units('kg')
        self.assertIn('lb', suggestions)
        self.assertIn('g', suggestions)
        
        # Time
        suggestions = self.registry.get_compatible_units('s')
        self.assertIn('min', suggestions)
        self.assertIn('h', suggestions)
    
    def test_suggestions_compound_units(self):
        """Test suggestions for common compound units"""
        # Velocity
        suggestions = self.registry.get_compatible_units('m/s')
        self.assertIn('km/h', suggestions)
        self.assertIn('ft/s', suggestions)
        
        # Density
        suggestions = self.registry.get_compatible_units('kg/m^3')
        self.assertIn('g/cm^3', suggestions)
        self.assertIn('lbm/ft^3', suggestions)
        
        # Specific heat
        suggestions = self.registry.get_compatible_units('J/(kg*K)')
        self.assertIn('kJ/(kg*K)', suggestions)
        self.assertIn('BTU/(lbm*R)', suggestions)
    
    def test_suggestions_edge_case_units(self):
        """Test suggestions for edge case units that were previously missing"""
        # Specific volume (m^3/kg)
        suggestions = self.registry.get_compatible_units('m^3/kg')
        self.assertIn('L/kg', suggestions)
        self.assertIn('ft^3/lbm', suggestions)
        
        # Second moment of area (m^4)
        suggestions = self.registry.get_compatible_units('m^4')
        self.assertIn('cm^4', suggestions)
        self.assertIn('in^4', suggestions)
        
        # Heat transfer coefficient (W/(m^2*K))
        suggestions = self.registry.get_compatible_units('W/(m^2*K)')
        self.assertIn('W/(m^2*degC)', suggestions)
        
        # Thermal conductivity (W/(m*K))
        suggestions = self.registry.get_compatible_units('W/(m*K)')
        self.assertIn('BTU/(hr*ft*R)', suggestions)
        
        # Momentum (kg*m/s)
        suggestions = self.registry.get_compatible_units('kg*m/s')
        self.assertIn('N*s', suggestions)
    
    def test_suggestions_electrical_units(self):
        """Test suggestions for electrical units"""
        # Electric charge - use 'coulomb' since 'C' maps to Celsius
        suggestions = self.registry.get_compatible_units('coulomb')
        self.assertIn('mC', suggestions)
        self.assertIn('A*h', suggestions)
        
        # Current density
        suggestions = self.registry.get_compatible_units('A/m^2')
        self.assertIn('A/cm^2', suggestions)
    
    def test_suggestions_chemistry_units(self):
        """Test suggestions for chemistry units"""
        # Molar energy
        suggestions = self.registry.get_compatible_units('J/mol')
        self.assertIn('kJ/mol', suggestions)
        self.assertIn('kcal/mol', suggestions)
        
        # Molar flow rate
        suggestions = self.registry.get_compatible_units('mol/s')
        self.assertIn('kmol/h', suggestions)
        
        # Concentration
        suggestions = self.registry.get_compatible_units('mol/L')
        self.assertIn('mol/m^3', suggestions)
    
    def test_suggestions_mechanical_units(self):
        """Test suggestions for mechanical units"""
        # Moment of inertia
        suggestions = self.registry.get_compatible_units('kg*m^2')
        self.assertIn('lb*ft^2', suggestions)
        
        # Linear density
        suggestions = self.registry.get_compatible_units('kg/m')
        self.assertIn('lb/ft', suggestions)
        
        # Stiffness / spring constant
        suggestions = self.registry.get_compatible_units('N/m')
        self.assertIn('lbf/in', suggestions)
    
    def test_suggestions_unknown_dimension(self):
        """Test that unknown dimension combinations return empty list"""
        # Made-up complex dimension that's unlikely to be in our mapping
        suggestions = self.registry.get_compatible_units('kg^3*m^5/s^7')
        self.assertEqual(suggestions, [])
    
    def test_suggestions_invalid_unit(self):
        """Test that invalid units return empty list without crashing"""
        suggestions = self.registry.get_compatible_units('not_a_real_unit')
        self.assertEqual(suggestions, [])
        
        suggestions = self.registry.get_compatible_units('')
        self.assertEqual(suggestions, [])

    # ===== Robustness & Edge Case Verification =====

    def test_energy_torque_merge(self):
        """Verify that Energy and Torque lists are merged correctly (no overwrite)"""
        # J (Energy) should suggest Torque units (N*m) and Energy units (kJ)
        suggestions = self.registry.get_compatible_units('J')
        self.assertIn('kJ', suggestions) # From Energy list
        self.assertIn('N*m', suggestions) # From Torque list
        
        # N*m (Torque) should suggest Energy units
        suggestions = self.registry.get_compatible_units('N*m')
        self.assertIn('J', suggestions)
        self.assertIn('BTU', suggestions)

    def test_alias_conflicts(self):
        """Verify handling of conflicting aliases (C, F, G)"""
        # 1. G -> gauss logic (Use full name)
        # 'G' should NOT be interpreted as gauss anymore
        # 'gauss' full name should convert to Tesla (10,000 G = 1 T)
        val = self.registry.convert(10000, 'gauss', 'T')
        self.assertAlmostEqual(val, 1.0)
        
        # 2. C -> coulomb logic
        # Suggestions for charge should use 'coulomb', not 'C' (which is Celsius)
        # Note: inputting 'coulomb' will filter it out of suggestions
        suggestions = self.registry.get_compatible_units('coulomb')
        self.assertIn('mC', suggestions)
        self.assertNotIn('C', suggestions) # C is Celsius, should not be suggested for charge
        
        # 3. F -> farad logic
        # Suggestions for capacitance should use 'farad', not 'F' (which is Fahrenheit)
        suggestions = self.registry.get_compatible_units('farad')
        self.assertIn('mF', suggestions)
        self.assertNotIn('F', suggestions) # F is Fahrenheit, should not be suggested

if __name__ == '__main__':
    unittest.main()
