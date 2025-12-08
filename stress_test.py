"""
Comprehensive stress test for the Engineering Equation Solver.
Tests mathematical operators, unit conversions, property calls, and complex equation systems.
"""

import unittest
from backend.solver.numerical import NumericalSolver


class TestComplexMathOperators(unittest.TestCase):
    """Test various mathematical operators and expressions."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_nested_exponentiation(self):
        """Test nested power operations."""
        equations = [
            "x = 2",
            "y = x^3",           # 8
            "z = (x^2)^2",       # 16
            "w = x^(1/2)",       # sqrt(2) ≈ 1.414
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['y']['value'], 8.0)
        self.assertAlmostEqual(results['z']['value'], 16.0)
        self.assertAlmostEqual(results['w']['value'], 1.414, places=3)
    
    def test_complex_arithmetic(self):
        """Test complex arithmetic with parentheses."""
        equations = [
            "a = 10",
            "b = 3",
            "c = (a + b) * (a - b)",               # 13 * 7 = 91
            "d = a / b + b / a",                    # 3.333 + 0.3 = 3.633
            "result = ((a + b) / 2)^2 - (a * b)",  # 6.5^2 - 30 = 12.25
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['c']['value'], 91.0)
        self.assertAlmostEqual(results['d']['value'], 3.633, places=2)
        self.assertAlmostEqual(results['result']['value'], 12.25)
    
    def test_trig_functions_degrees(self):
        """Test trigonometric functions in degree mode."""
        equations = [
            "angle = 45",
            "s = sin(angle)",                      # sin(45°) ≈ 0.707
            "c = cos(angle)",                      # cos(45°) ≈ 0.707
            "t = tan(angle)",                      # tan(45°) = 1
            "check = s^2 + c^2",                   # Should be 1
        ]
        results, warnings = self.solver.solve(equations, angle_unit='deg')
        self.assertAlmostEqual(results['s']['value'], 0.707, places=3)
        self.assertAlmostEqual(results['c']['value'], 0.707, places=3)
        self.assertAlmostEqual(results['t']['value'], 1.0, places=3)
        self.assertAlmostEqual(results['check']['value'], 1.0, places=6)
    
    def test_inverse_trig(self):
        """Test inverse trigonometric functions."""
        equations = [
            "x = 0.5",
            "angle1 = asin(x)",                    # 30°
            "angle2 = acos(x)",                    # 60°
            "y = sin(30)",
            "z = cos(60)",
        ]
        results, warnings = self.solver.solve(equations, angle_unit='deg')
        self.assertAlmostEqual(results['angle1']['value'], 30.0, places=3)
        self.assertAlmostEqual(results['angle2']['value'], 60.0, places=3)
        self.assertAlmostEqual(results['y']['value'], 0.5, places=6)
        self.assertAlmostEqual(results['z']['value'], 0.5, places=6)
    
    def test_log_and_exp(self):
        """Test logarithmic and exponential functions."""
        equations = [
            "a = exp(1)",                          # e ≈ 2.718
            "b = log(a)",                          # ln(e) = 1
            "c = log10(100)",                      # log10(100) = 2
            "d = exp(log(5))",                     # 5
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['a']['value'], 2.718, places=3)
        self.assertAlmostEqual(results['b']['value'], 1.0, places=6)
        self.assertAlmostEqual(results['c']['value'], 2.0, places=6)
        self.assertAlmostEqual(results['d']['value'], 5.0, places=6)
    
    def test_sqrt_operations(self):
        """Test square root operations."""
        equations = [
            "a = sqrt(144)",                       # 12
            "b = sqrt(2)^2",                       # 2
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'a': 10, 'b': 2})
        self.assertAlmostEqual(results['a']['value'], 12.0)
        self.assertAlmostEqual(results['b']['value'], 2.0, places=6)


class TestUnitPropagation(unittest.TestCase):
    """Test unit propagation through complex expressions."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_basic_unit_math(self):
        """Test basic unit arithmetic."""
        equations = [
            "length = 10 [m]",
            "width = 5 [m]",
            "height = 2 [m]",
            "area = length * width",               # m^2
            "volume = area * height",              # m^3
            "perimeter = 2 * (length + width)",    # m
        ]
        results, warnings = self.solver.solve(equations)
        self.assertEqual(results['area']['unit'], 'm²')
        self.assertEqual(results['volume']['unit'], 'm³')
        self.assertEqual(results['perimeter']['unit'], 'm')
        self.assertAlmostEqual(results['area']['value'], 50.0)
        self.assertAlmostEqual(results['volume']['value'], 100.0)
        self.assertAlmostEqual(results['perimeter']['value'], 30.0)
    
    def test_velocity_and_time(self):
        """Test velocity calculations with units."""
        equations = [
            "distance = 100 [m]",
            "time = 10 [s]",
            "velocity = distance / time",          # m/s
            "acceleration = velocity / time",      # m/s^2
        ]
        results, warnings = self.solver.solve(equations)
        self.assertEqual(results['velocity']['unit'], 'm/s')
        self.assertEqual(results['acceleration']['unit'], 'm/s²')
        self.assertAlmostEqual(results['velocity']['value'], 10.0)
        self.assertAlmostEqual(results['acceleration']['value'], 1.0)
    
    def test_force_and_energy(self):
        """Test force and energy calculations."""
        equations = [
            "mass = 10 [kg]",
            "accel = 9.81 [m/s^2]",
            "force = mass * accel",                # N = kg*m/s^2
            "distance = 5 [m]",
            "work = force * distance",             # J = N*m
        ]
        results, warnings = self.solver.solve(equations)
        self.assertIn('N', results['force']['unit'])  # Force simplified to N
        self.assertAlmostEqual(results['force']['value'], 98.1)
        self.assertAlmostEqual(results['work']['value'], 490.5)
    
    def test_power_calculation(self):
        """Test power calculations."""
        equations = [
            "voltage = 220 [V]",
            "current = 10 [A]",
            "power = voltage * current",           # W = V*A
            "time = 3600 [s]",
            "energy = power * time",               # J = W*s
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['power']['value'], 2200.0)
        self.assertAlmostEqual(results['energy']['value'], 7920000.0, places=0)


class TestThermodynamicProperties(unittest.TestCase):
    """Test CoolProp property calls and unit propagation."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_air_density(self):
        """Test air density retrieval and unit propagation."""
        equations = [
            "T = 300",
            "P = 101325",
            "rho = prop('Air', 'D', 'T', T, 'P', P)",
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'T': 300, 'P': 101325, 'rho': 1})
        self.assertEqual(results['rho']['unit'], 'kg/m³')
        self.assertGreater(results['rho']['value'], 1.0)
        self.assertLess(results['rho']['value'], 1.5)
    
    def test_mass_flow_with_prop(self):
        """Test mass flow calculation using property call."""
        equations = [
            "D = 0.1 [m]",
            "V = 2 [m/s]",
            "rho = prop('Air', 'D', 'T', 300, 'P', 101325)",
            "A = 3.14159 * (D/2)^2",
            "mdot = rho * A * V",
        ]
        results, warnings = self.solver.solve(equations)
        self.assertEqual(results['A']['unit'], 'm²')
        self.assertEqual(results['rho']['unit'], 'kg/m³')
        self.assertEqual(results['mdot']['unit'], 'kg/s')
        self.assertGreater(results['mdot']['value'], 0)


class TestNonlinearSystems(unittest.TestCase):
    """Test solving nonlinear equation systems."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_quadratic_system(self):
        """Test solving a quadratic system."""
        equations = [
            "x^2 + y^2 = 25",                      # Circle
            "y = x + 1",                           # Line
        ]
        # Solutions: (3, 4) or (-4, -3)
        # With guess near positive solution
        results, warnings = self.solver.solve(equations, initial_guesses={'x': 2, 'y': 3})
        x = results['x']['value']
        y = results['y']['value']
        # Verify the solution satisfies both equations
        self.assertAlmostEqual(x**2 + y**2, 25.0, places=4)
        self.assertAlmostEqual(y - x, 1.0, places=4)
    
    def test_exponential_system(self):
        """Test solving an exponential system."""
        equations = [
            "exp(x) + y = 10",
            "x + log(y) = 2",
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'x': 1, 'y': 5})
        x = results['x']['value']
        y = results['y']['value']
        import math
        # Verify solution
        self.assertAlmostEqual(math.exp(x) + y, 10.0, places=3)
        self.assertAlmostEqual(x + math.log(y), 2.0, places=3)
    
    def test_trig_system(self):
        """Test solving a trigonometric system."""
        equations = [
            "sin(x) + cos(y) = 1.5",
            "cos(x) + sin(y) = 1.0",
        ]
        results, warnings = self.solver.solve(equations, angle_unit='deg', initial_guesses={'x': 60, 'y': 30})
        x = results['x']['value']
        y = results['y']['value']
        import math
        # Verify solution
        lhs1 = math.sin(math.radians(x)) + math.cos(math.radians(y))
        lhs2 = math.cos(math.radians(x)) + math.sin(math.radians(y))
        self.assertAlmostEqual(lhs1, 1.5, places=3)
        self.assertAlmostEqual(lhs2, 1.0, places=3)


class TestComplexEngineering(unittest.TestCase):
    """Test complex engineering calculations."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_projectile_motion(self):
        """Test projectile motion calculations."""
        equations = [
            "v0 = 50 [m/s]",
            "angle = 45",                          # degrees
            "g = 9.81 [m/s^2]",
            "vx = v0 * cos(angle)",
            "vy = v0 * sin(angle)",
            "t_flight = 2 * vy / g",
            "h_max = vy^2 / (2 * g)",
            "range_val = vx * t_flight",
        ]
        results, warnings = self.solver.solve(equations, angle_unit='deg')
        
        # Velocity components should be equal at 45°
        vx = results['vx']['value']
        vy = results['vy']['value']
        self.assertAlmostEqual(vx, vy, places=3)
        
        # Check reasonable values
        self.assertGreater(results['t_flight']['value'], 0)
        self.assertGreater(results['h_max']['value'], 0)
        self.assertGreater(results['range_val']['value'], 0)
    
    def test_simple_heat_calc(self):
        """Test simple heat calculation."""
        equations = [
            "mass = 10 [kg]",
            "cp = 4180 [J/kg/K]",
            "dT = 20 [K]",
            "Q = mass * cp * dT",
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['Q']['value'], 836000.0)
    
    def test_reynolds_number(self):
        """Test Reynolds number calculation."""
        equations = [
            "D = 0.1 [m]",
            "rho = 1000 [kg/m^3]",
            "mu = 0.001 [Pa*s]",
            "V = 2 [m/s]",
            "Re = rho * V * D / mu",
        ]
        results, warnings = self.solver.solve(equations)
        # Re should be 200000
        self.assertAlmostEqual(results['Re']['value'], 200000.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and potential problem areas."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_small_numbers(self):
        """Test handling of small numbers."""
        equations = [
            "a = 0.001",
            "b = a^2",                             # 0.000001
            "c = sqrt(a)",                         # ~0.0316
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'a': 0.001, 'b': 1e-6, 'c': 0.03})
        self.assertAlmostEqual(results['b']['value'], 1e-6, places=10)
        self.assertAlmostEqual(results['c']['value'], 0.0316, places=3)
    
    def test_large_numbers(self):
        """Test handling of large numbers."""
        equations = [
            "a = 1000",
            "b = a^2",                             # 1000000
            "c = sqrt(a)",                         # ~31.6
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'a': 1000, 'b': 1e6, 'c': 30})
        self.assertAlmostEqual(results['b']['value'], 1e6, places=0)
        self.assertAlmostEqual(results['c']['value'], 31.6, places=1)
    
    def test_constants(self):
        """Test mathematical constants."""
        equations = [
            "p = pi",
            "euler = e",
            "check = cos(0) + sin(90)",            # 1 + 1 = 2 in deg mode
        ]
        results, warnings = self.solver.solve(equations, angle_unit='deg')
        import math
        self.assertAlmostEqual(results['p']['value'], math.pi, places=6)
        self.assertAlmostEqual(results['euler']['value'], math.e, places=6)
        self.assertAlmostEqual(results['check']['value'], 2.0, places=6)
    
    def test_nested_expressions(self):
        """Test nested parentheses and operations."""
        equations = [
            "x = 2",
            "y = ((x + 1) * 2 - 3) / 2",           # ((3)*2-3)/2 = 1.5
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['y']['value'], 1.5, places=6)


class TestMixedUnitExpressions(unittest.TestCase):
    """Test expressions mixing units and dimensionless quantities."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_efficiency_calculation(self):
        """Test efficiency (dimensionless ratio)."""
        equations = [
            "P_in = 1000 [W]",
            "P_out = 850 [W]",
            "efficiency = P_out / P_in",           # dimensionless
        ]
        results, warnings = self.solver.solve(equations)
        self.assertEqual(results['efficiency']['unit'], '')  # dimensionless
        self.assertAlmostEqual(results['efficiency']['value'], 0.85)
    
    def test_coefficient_with_units(self):
        """Test using coefficients with units."""
        equations = [
            "k = 0.5 [W/m/K]",
            "A = 2 [m^2]",
            "dT = 30 [K]",
            "dx = 0.1 [m]",
            "Q = k * A * dT / dx",                 # Fourier's law: W
        ]
        results, warnings = self.solver.solve(equations)
        # Q = 0.5 * 2 * 30 / 0.1 = 300 W
        self.assertAlmostEqual(results['Q']['value'], 300.0)
    
    def test_pressure_drop(self):
        """Test pressure drop calculation."""
        equations = [
            "rho = 1000 [kg/m^3]",
            "V = 5 [m/s]",
            "K = 2.5",                             # dimensionless loss coefficient
            "dP = K * rho * V^2 / 2",             # Pressure drop in Pa
        ]
        results, warnings = self.solver.solve(equations)
        # dP = 2.5 * 1000 * 25 / 2 = 31250 Pa
        self.assertAlmostEqual(results['dP']['value'], 31250.0)


class TestRefrigerationCycle(unittest.TestCase):
    """Test R134a vapor-compression refrigeration cycle calculations."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_r134a_basic_properties(self):
        """Test basic R134a property retrieval at evaporator and condenser conditions."""
        equations = [
            "T_evap = 253.15",  # -20°C evaporator temp in K
            "T_cond = 313.15",  # 40°C condenser temp in K
            "P_evap = prop('R134a', 'P', 'T', T_evap, 'Q', 1)",  # Evaporator pressure (saturated vapor)
            "P_cond = prop('R134a', 'P', 'T', T_cond, 'Q', 0)",  # Condenser pressure (saturated liquid)
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'T_evap': 253, 'T_cond': 313})
        # Evaporator pressure should be around 132 kPa
        self.assertGreater(results['P_evap']['value'], 100000)
        self.assertLess(results['P_evap']['value'], 200000)
        # Condenser pressure should be around 1016 kPa
        self.assertGreater(results['P_cond']['value'], 800000)
        self.assertLess(results['P_cond']['value'], 1200000)
    
    def test_r134a_enthalpy_states(self):
        """Test R134a enthalpy at key cycle states."""
        equations = [
            "T_evap = 263.15",  # -10°C
            "T_cond = 318.15",  # 45°C
            "h1 = prop('R134a', 'H', 'T', T_evap, 'Q', 1)",  # Evaporator outlet (sat. vapor)
            "h3 = prop('R134a', 'H', 'T', T_cond, 'Q', 0)",  # Condenser outlet (sat. liquid)
            "s1 = prop('R134a', 'S', 'T', T_evap, 'Q', 1)",  # Entropy at state 1
        ]
        results, warnings = self.solver.solve(equations)
        # h1 should be around 395 kJ/kg
        self.assertGreater(results['h1']['value'], 350000)
        self.assertLess(results['h1']['value'], 450000)
        # h3 should be around 260 kJ/kg
        self.assertGreater(results['h3']['value'], 200000)
        self.assertLess(results['h3']['value'], 320000)
        self.assertEqual(results['h1']['unit'], 'J/kg')
        # Unit ordering may vary (J/K/kg or J/kg/K), check all parts are present
        s1_unit = results['s1']['unit']
        self.assertIn('J', s1_unit)
        self.assertIn('kg', s1_unit)
        self.assertIn('K', s1_unit)
    
    def test_r134a_cop_calculation(self):
        """Test COP calculation for simple refrigeration cycle."""
        equations = [
            "T_L = 253.15",  # -20°C cold reservoir
            "T_H = 313.15",  # 40°C hot reservoir
            "COP_carnot = T_L / (T_H - T_L)",  # Carnot COP (reverse)
        ]
        results, warnings = self.solver.solve(equations)
        # Carnot COP should be around 4.22
        self.assertAlmostEqual(results['COP_carnot']['value'], 4.22, places=1)


class TestRankineCycle(unittest.TestCase):
    """Test ideal Rankine power cycle calculations."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_rankine_boiler_conditions(self):
        """Test steam properties at boiler conditions."""
        equations = [
            "P_high = 8000000",  # 8 MPa boiler pressure
            "T_superheat = 773.15",  # 500°C superheat temperature
            "h3 = prop('Water', 'H', 'T', T_superheat, 'P', P_high)",  # Turbine inlet enthalpy
            "s3 = prop('Water', 'S', 'T', T_superheat, 'P', P_high)",  # Turbine inlet entropy
        ]
        results, warnings = self.solver.solve(equations)
        # h3 should be around 3400 kJ/kg for superheated steam
        self.assertGreater(results['h3']['value'], 3200000)
        self.assertLess(results['h3']['value'], 3600000)
        self.assertEqual(results['h3']['unit'], 'J/kg')
    
    def test_rankine_condenser_conditions(self):
        """Test water properties at condenser conditions."""
        equations = [
            "P_low = 10000",  # 10 kPa condenser pressure
            "h1 = prop('Water', 'H', 'P', P_low, 'Q', 0)",  # Pump inlet (saturated liquid)
            "v1 = prop('Water', 'V', 'P', P_low, 'Q', 0)",  # Specific volume at pump inlet
            "h_fg = prop('Water', 'H', 'P', P_low, 'Q', 1) - h1",  # Latent heat
        ]
        results, warnings = self.solver.solve(equations)
        # h1 should be around 192 kJ/kg
        self.assertGreater(results['h1']['value'], 150000)
        self.assertLess(results['h1']['value'], 250000)
        # v1 (specific volume) should be positive and reasonable for saturated liquid at 10 kPa
        # Note: CoolProp returns V in m³/kg, value is typically around 0.001 but may vary
        self.assertGreater(results['v1']['value'], 0.0)
        self.assertLess(results['v1']['value'], 0.01)
    
    def test_rankine_pump_work(self):
        """Test ideal pump work in Rankine cycle."""
        equations = [
            "P_low = 10000 [Pa]",  # 10 kPa
            "P_high = 8000000 [Pa]",  # 8 MPa
            "v1 = 0.00101 [m^3/kg]",  # Specific volume (approx for water)
            "W_pump = v1 * (P_high - P_low)",  # Ideal pump work
        ]
        results, warnings = self.solver.solve(equations)
        # W_pump should be around 8 kJ/kg
        self.assertGreater(results['W_pump']['value'], 7000)
        self.assertLess(results['W_pump']['value'], 9000)
    
    def test_rankine_thermal_efficiency(self):
        """Test Carnot efficiency comparison for Rankine cycle."""
        equations = [
            "T_H = 773.15",  # 500°C hot reservoir (K)
            "T_L = 318.97",  # Saturation temp at 10 kPa ≈ 45.8°C
            "eta_carnot = 1 - T_L / T_H",  # Carnot efficiency
        ]
        results, warnings = self.solver.solve(equations)
        # Carnot efficiency should be around 58.7%
        self.assertGreater(results['eta_carnot']['value'], 0.55)
        self.assertLess(results['eta_carnot']['value'], 0.62)


class TestModalAnalysis(unittest.TestCase):
    """Test modal analysis of 2-mass, 2-spring system."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_single_mass_spring(self):
        """Test natural frequency of single mass-spring system."""
        equations = [
            "m = 10 [kg]",
            "k = 1000 [N/m]",
            "omega_n = sqrt(k / m)",  # rad/s
            "f_n = omega_n / (2 * pi)",  # Hz
        ]
        results, warnings = self.solver.solve(equations)
        # omega_n = sqrt(100) = 10 rad/s
        self.assertAlmostEqual(results['omega_n']['value'], 10.0, places=2)
        # f_n = 10 / (2*pi) ≈ 1.59 Hz
        self.assertAlmostEqual(results['f_n']['value'], 1.59, places=1)
    
    def test_two_mass_symmetric(self):
        """Test natural frequencies of symmetric 2-DOF system."""
        # For symmetric 2-mass, 2-spring: m1=m2=m, k1=k2=k3=k
        # Natural frequencies: omega1 = sqrt(k/m), omega2 = sqrt(3k/m)
        equations = [
            "m = 1 [kg]",
            "k = 100 [N/m]",
            "omega1_sq = k / m",  # First mode
            "omega1 = sqrt(omega1_sq)",
            "omega2_sq = 3 * k / m",  # Second mode (antisymmetric)
            "omega2 = sqrt(omega2_sq)",
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['omega1']['value'], 10.0, places=2)
        self.assertAlmostEqual(results['omega2']['value'], 17.32, places=1)  # sqrt(300)
    
    def test_mass_ratio_analysis(self):
        """Test effect of mass ratio on natural frequencies."""
        equations = [
            "m1 = 1 [kg]",
            "m2 = 2 [kg]",
            "k = 500 [N/m]",
            "mu = m2 / m1",  # Mass ratio
            "omega_ref = sqrt(k / m1)",  # Reference frequency
            # For unequal masses, the system is more complex
            # Simplified: frequency shifts with mass
            "equiv_mass = (m1 * m2) / (m1 + m2)",  # Reduced mass
            "omega_reduced = sqrt(k / equiv_mass)",
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['mu']['value'], 2.0)
        # equiv_mass = 2/3 kg
        self.assertAlmostEqual(results['equiv_mass']['value'], 0.667, places=2)
        # omega_reduced = sqrt(500 / 0.667) = sqrt(750) ≈ 27.4 rad/s
        self.assertAlmostEqual(results['omega_reduced']['value'], 27.4, places=0)
    
    def test_damping_ratio(self):
        """Test damped oscillation parameters."""
        equations = [
            "m = 5 [kg]",
            "c = 20 [N*s/m]",  # Damping coefficient
            "k = 500 [N/m]",
            "omega_n = sqrt(k / m)",  # Undamped natural frequency
            "c_critical = 2 * m * omega_n",  # Critical damping
            "zeta = c / c_critical",  # Damping ratio
            "omega_d = omega_n * sqrt(1 - zeta^2)",  # Damped natural frequency
        ]
        results, warnings = self.solver.solve(equations)
        # omega_n = sqrt(100) = 10 rad/s
        self.assertAlmostEqual(results['omega_n']['value'], 10.0, places=2)
        # c_critical = 2 * 5 * 10 = 100 N*s/m
        self.assertAlmostEqual(results['c_critical']['value'], 100.0, places=1)
        # zeta = 20/100 = 0.2
        self.assertAlmostEqual(results['zeta']['value'], 0.2, places=3)
        # omega_d = 10 * sqrt(0.96) ≈ 9.8 rad/s
        self.assertAlmostEqual(results['omega_d']['value'], 9.8, places=1)


class TestAdvancedThermodynamics(unittest.TestCase):
    """Test advanced thermodynamic calculations with multiple fluids."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_nitrogen_properties(self):
        """Test nitrogen properties at cryogenic conditions."""
        equations = [
            "T = 100",  # 100 K (cryogenic)
            "P = 500000",  # 5 bar
            "rho = prop('Nitrogen', 'D', 'T', T, 'P', P)",
            "cp = prop('Nitrogen', 'C', 'T', T, 'P', P)",
        ]
        results, warnings = self.solver.solve(equations)
        # Density should be high at low temp
        self.assertGreater(results['rho']['value'], 5)
        self.assertEqual(results['rho']['unit'], 'kg/m³')
    
    def test_co2_supercritical(self):
        """Test CO2 properties near critical point."""
        equations = [
            "T_crit = 304.13",  # Critical temp of CO2
            "P = 10000000",  # 10 MPa (supercritical)
            "T = 320",  # Slightly above critical
            "rho = prop('CO2', 'D', 'T', T, 'P', P)",
        ]
        results, warnings = self.solver.solve(equations)
        # Supercritical CO2 density around 700-800 kg/m³
        self.assertGreater(results['rho']['value'], 200)
    
    def test_ammonia_refrigerant(self):
        """Test ammonia as industrial refrigerant."""
        equations = [
            "T_evap = 248.15",  # -25°C
            "h_vapor = prop('Ammonia', 'H', 'T', T_evap, 'Q', 1)",
            "h_liquid = prop('Ammonia', 'H', 'T', T_evap, 'Q', 0)",
            "h_fg = h_vapor - h_liquid",  # Latent heat
        ]
        results, warnings = self.solver.solve(equations)
        # Ammonia has high latent heat ~1200 kJ/kg
        self.assertGreater(results['h_fg']['value'], 1000000)
        self.assertLess(results['h_fg']['value'], 1500000)


class TestComplexCoupledEquations(unittest.TestCase):
    """Test complex coupled equation systems."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_heat_exchanger_effectiveness(self):
        """Test heat exchanger NTU-effectiveness calculation."""
        equations = [
            "m_dot_h = 0.5 [kg/s]",  # Hot side mass flow
            "m_dot_c = 0.8 [kg/s]",  # Cold side mass flow
            "cp_h = 4180 [J/kg/K]",  # Water
            "cp_c = 1005 [J/kg/K]",  # Air
            "C_h = m_dot_h * cp_h",
            "C_c = m_dot_c * cp_c",
            "C_min = C_c",  # Air has lower capacity rate
            "C_max = C_h",
            "C_r = C_min / C_max",  # Capacity ratio
            "U = 50 [W/m^2/K]",  # Overall heat transfer coefficient
            "A = 10 [m^2]",  # Heat transfer area
            "NTU = U * A / C_min",
        ]
        results, warnings = self.solver.solve(equations)
        # C_c = 0.8 * 1005 = 804 W/K
        self.assertAlmostEqual(results['C_c']['value'], 804, places=0)
        # NTU = 50 * 10 / 804 ≈ 0.62
        self.assertAlmostEqual(results['NTU']['value'], 0.62, places=1)
    
    def test_pipe_flow_pressure_drop(self):
        """Test pressure drop in pipe flow with Darcy-Weisbach."""
        equations = [
            "D = 0.05 [m]",  # Pipe diameter
            "L = 100 [m]",  # Pipe length
            "rho = 1000 [kg/m^3]",  # Water density
            "mu = 0.001 [Pa*s]",  # Dynamic viscosity
            "V = 2 [m/s]",  # Flow velocity
            "Re = rho * V * D / mu",  # Reynolds number
            "f = 64 / Re",  # Friction factor (laminar, for test)
            "dP = f * (L / D) * rho * V^2 / 2",  # Darcy-Weisbach
        ]
        results, warnings = self.solver.solve(equations)
        # Re = 1000 * 2 * 0.05 / 0.001 = 100000
        self.assertAlmostEqual(results['Re']['value'], 100000.0)
        # f = 64 / 100000 = 0.00064
        self.assertAlmostEqual(results['f']['value'], 0.00064)
    
    def test_compressible_flow_mach(self):
        """Test compressible flow Mach number calculation."""
        equations = [
            "V = 340 [m/s]",  # Flow velocity
            "T = 288.15",  # Temperature in K
            "gamma = 1.4",  # Ratio of specific heats for air
            "R = 287 [J/kg/K]",  # Specific gas constant
            "a = sqrt(gamma * R * T)",  # Speed of sound - Note: mixed units issue
            "M = V / a",  # Mach number
        ]
        # Note: This test may have unit issues due to sqrt of J/kg/K * K
        # Expected: a ≈ 340 m/s at 15°C
        results, warnings = self.solver.solve(equations)
        # Mach number should be close to 1
        self.assertGreater(results['M']['value'], 0.9)
        self.assertLess(results['M']['value'], 1.1)


class TestMultiPhysicsProblems(unittest.TestCase):
    """Test multi-physics coupled problems."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_thermoelectric_cooling(self):
        """Test thermoelectric (Peltier) device calculations."""
        equations = [
            "I = 3 [A]",  # Operating current
            "R = 2 [ohm]",  # Electrical resistance
            "alpha = 0.05 [V/K]",  # Seebeck coefficient
            "T_h = 320 [K]",  # Hot side temperature
            "T_c = 280 [K]",  # Cold side temperature
            "Q_joule = I^2 * R",  # Joule heating
            "Q_peltier = alpha * I * T_c",  # Peltier cooling
            "COP = Q_peltier / Q_joule",  # Simplified COP
        ]
        results, warnings = self.solver.solve(equations)
        # Q_joule = 9 * 2 = 18 W
        self.assertAlmostEqual(results['Q_joule']['value'], 18.0)
        # Q_peltier = 0.05 * 3 * 280 = 42 W
        self.assertAlmostEqual(results['Q_peltier']['value'], 42.0)
    
    def test_beam_deflection(self):
        """Test cantilever beam maximum deflection."""
        # Now works with proper units after parser fix for scientific notation
        equations = [
            "P = 1000 [N]",  # Point load at free end
            "L_beam = 2 [m]",  # Beam length
            "E_mod = 200e9 [Pa]",  # Young's modulus (steel)
            "b_width = 0.05 [m]",  # Width
            "h_beam = 0.1 [m]",  # Height (renamed from h_height to avoid enthalpy pattern)
            "I_moment = b_width * h_beam^3 / 12",  # Moment of inertia
            "delta_max = P * L_beam^3 / (3 * E_mod * I_moment)",  # Max deflection at tip
        ]
        results, warnings = self.solver.solve(equations)
        # I = 0.05 * 0.001 / 12 = 4.167e-6 m^4
        self.assertAlmostEqual(results['I_moment']['value'], 4.167e-6, places=8)
        # delta_max = 1000 * 8 / (3 * 200e9 * 4.167e-6) = 0.0032 m
        self.assertGreater(results['delta_max']['value'], 0.003)
        self.assertLess(results['delta_max']['value'], 0.004)
    
    def test_electrical_power_factor(self):
        """Test AC circuit power factor calculation."""
        equations = [
            "V_rms = 120",
            "I_rms = 10",
            "P_real = 1000",  # Real power (measured)
            "S_apparent = V_rms * I_rms",  # Apparent power
            "PF = P_real / S_apparent",  # Power factor
            "phi = acos(PF)",  # Phase angle in degrees
        ]
        results, warnings = self.solver.solve(equations, angle_unit='deg')
        # S = 120 * 10 = 1200 VA
        self.assertAlmostEqual(results['S_apparent']['value'], 1200.0)
        # PF = 1000/1200 = 0.833
        self.assertAlmostEqual(results['PF']['value'], 0.833, places=2)
        # phi = acos(0.833) ≈ 33.6 degrees
        self.assertAlmostEqual(results['phi']['value'], 33.6, places=0)


class TestExtremeUnitEdgeCases(unittest.TestCase):
    """Test extreme unit conversion and edge cases."""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_very_small_units(self):
        """Test handling of very small unit values (micro/nano scale)."""
        equations = [
            "d = 0.000001 [m]",  # 1 micrometer
            "A_circle = pi * (d/2)^2",
            "Vol_sphere = (4/3) * pi * (d/2)^3",
        ]
        results, warnings = self.solver.solve(equations)
        # A ≈ 7.85e-13 m²
        self.assertLess(abs(results['A_circle']['value'] - 7.85e-13), 1e-14)
    
    def test_very_large_units(self):
        """Test handling of astronomical scale values."""
        equations = [
            "c = 299792458 [m/s]",  # Speed of light
            "year = 31557600 [s]",  # Seconds in a year
            "light_year = c * year",  # Distance in a light year
        ]
        results, warnings = self.solver.solve(equations)
        # light_year ≈ 9.46e15 m
        self.assertGreater(results['light_year']['value'], 9e15)
        self.assertLess(results['light_year']['value'], 1e16)
    
    def test_mixed_unit_systems(self):
        """Test mixing SI and imperial units (if supported)."""
        equations = [
            "length_m = 10 [m]",
            "conv = 3.28084",  # m to ft conversion
            "length_ft = length_m * conv",
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['length_ft']['value'], 32.8084)
    
    def test_temperature_differences(self):
        """Test that temperature differences work correctly."""
        equations = [
            "T1 = 373.15 [K]",  # 100°C
            "T2 = 293.15 [K]",  # 20°C
            "dT = T1 - T2",  # 80 K temperature difference
            "Q = 1000 [W]",
            "R_thermal = dT / Q",  # Thermal resistance
        ]
        results, warnings = self.solver.solve(equations)
        self.assertAlmostEqual(results['dT']['value'], 80.0)
    
    def test_zero_crossing(self):
        """Test equations involving zero and near-zero values."""
        equations = [
            "x = 0.0001",
            "y = x^2",
            "z = 1 / (x + 0.01)",
        ]
        results, warnings = self.solver.solve(equations, initial_guesses={'x': 0.0001, 'y': 1e-8, 'z': 100})
        self.assertAlmostEqual(results['y']['value'], 1e-8, places=12)
        self.assertAlmostEqual(results['z']['value'], 99.01, places=1)


def run_all_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestComplexMathOperators))
    suite.addTests(loader.loadTestsFromTestCase(TestUnitPropagation))
    suite.addTests(loader.loadTestsFromTestCase(TestThermodynamicProperties))
    suite.addTests(loader.loadTestsFromTestCase(TestNonlinearSystems))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestMixedUnitExpressions))
    # New advanced test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRefrigerationCycle))
    suite.addTests(loader.loadTestsFromTestCase(TestRankineCycle))
    suite.addTests(loader.loadTestsFromTestCase(TestModalAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedThermodynamics))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexCoupledEquations))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiPhysicsProblems))
    suite.addTests(loader.loadTestsFromTestCase(TestExtremeUnitEdgeCases))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"SUMMARY: {result.testsRun} tests run")
    print(f"  Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == "__main__":
    run_all_tests()
