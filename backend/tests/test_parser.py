import unittest
from solver.parser import EquationParser

class TestEquationParser(unittest.TestCase):
    def setUp(self):
        self.parser = EquationParser()

    def test_extract_variables_simple(self):
        eqs = ["x + y = 10", "x - y = 2"]
        vars, units = self.parser.extract_variables(eqs)
        self.assertEqual(vars, {'x', 'y'})

    def test_extract_variables_with_functions(self):
        eqs = ["y = sin(x) + 5"]
        vars, units = self.parser.extract_variables(eqs)
        self.assertEqual(vars, {'x', 'y'})

    def test_normalize_equations(self):
        eqs = ["x + y = 10"]
        norm = self.parser.normalize_equations(eqs)
        self.assertEqual(norm, ["(x + y) - (10)"])

    def test_parse_full_text(self):
        text = """
        x = 5
        y = x^2 + 2
        """
        vars, eqs, units = self.parser.parse(text)
        self.assertEqual(vars, {'x', 'y'})
        self.assertEqual(len(eqs), 2)

    def test_unit_extraction(self):
        text = """
        L = 10 [m]
        t = 5 [s]
        """
        vars, eqs, units = self.parser.parse(text)
        self.assertEqual(units['L'], 'm')
        self.assertEqual(units['t'], 's')

    def test_string_literals_ignored(self):
        # Strings like 'C', 'F' should not be treated as variables
        text = "T_F = convert(100, 'C', 'F')"
        vars, eqs, units = self.parser.parse(text)
        self.assertEqual(vars, {'T_F'})
        
    def test_exponentiation_conversion(self):
        # ^ should be converted to **
        text = "y = x^2"
        vars, eqs, units = self.parser.parse(text)
        self.assertIn("(y) - (x**2)", eqs)

if __name__ == '__main__':
    unittest.main()
