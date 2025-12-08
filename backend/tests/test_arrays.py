"""
Tests for array parsing and solving functionality.

Tests:
- Array syntax parsing (linspace, arange, explicit arrays)
- Array mode detection (@parallel, @grid)
- Plot directive extraction
- Array solving with unit propagation
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solver.parser import EquationParser
from solver.numerical import NumericalSolver


class TestArrayParsing(unittest.TestCase):
    """Tests for array syntax parsing"""
    
    def setUp(self):
        self.parser = EquationParser()
    
    def test_linspace_parsing(self):
        """Test parsing of linspace() array definition"""
        equations = ['t = linspace(0, 10, 5)']
        arrays = self.parser.extract_arrays(equations)
        
        self.assertIn('t', arrays)
        self.assertEqual(arrays['t']['type'], 'linspace')
        self.assertEqual(len(arrays['t']['values']), 5)
        self.assertAlmostEqual(arrays['t']['values'][0], 0.0)
        self.assertAlmostEqual(arrays['t']['values'][-1], 10.0)
    
    def test_linspace_with_unit(self):
        """Test linspace with unit annotation"""
        equations = ['t = linspace(0, 10, 5) [s]']
        arrays = self.parser.extract_arrays(equations)
        
        self.assertIn('t', arrays)
        self.assertEqual(arrays['t']['unit'], 's')
    
    def test_arange_parsing(self):
        """Test parsing of arange() array definition"""
        equations = ['x = arange(0, 5, 1)']
        arrays = self.parser.extract_arrays(equations)
        
        self.assertIn('x', arrays)
        self.assertEqual(arrays['x']['type'], 'arange')
        # arange(0, 5, 1) should give [0, 1, 2, 3, 4]
        self.assertEqual(len(arrays['x']['values']), 5)
    
    def test_explicit_array_parsing(self):
        """Test parsing of explicit array [1, 2, 3]"""
        equations = ['vals = [1, 2, 3, 4, 5]']
        arrays = self.parser.extract_arrays(equations)
        
        self.assertIn('vals', arrays)
        self.assertEqual(arrays['vals']['type'], 'explicit')
        self.assertEqual(arrays['vals']['values'], [1.0, 2.0, 3.0, 4.0, 5.0])
    
    def test_array_mode_parallel(self):
        """Test @parallel mode extraction"""
        equations = ['@parallel', 't = linspace(0, 10, 5)']
        mode = self.parser.extract_array_mode(equations)
        self.assertEqual(mode, 'parallel')
    
    def test_array_mode_grid(self):
        """Test @grid mode extraction"""
        equations = ['@grid', 't = linspace(0, 10, 5)']
        mode = self.parser.extract_array_mode(equations)
        self.assertEqual(mode, 'grid')
    
    def test_default_array_mode(self):
        """Test default mode is parallel"""
        equations = ['t = linspace(0, 10, 5)']
        mode = self.parser.extract_array_mode(equations)
        self.assertEqual(mode, 'parallel')


class TestPlotParsing(unittest.TestCase):
    """Tests for plot directive parsing"""
    
    def setUp(self):
        self.parser = EquationParser()
    
    def test_basic_plot(self):
        """Test basic plot(x, y) parsing"""
        equations = ['plot(t, x)']
        plots = self.parser.extract_plot_directives(equations)
        
        self.assertEqual(len(plots), 1)
        self.assertEqual(plots[0]['x_var'], 't')
        self.assertEqual(plots[0]['y_vars'], ['x'])
    
    def test_multi_y_plot(self):
        """Test plot with multiple Y variables"""
        equations = ['plot(t, [x, v, a])']
        plots = self.parser.extract_plot_directives(equations)
        
        self.assertEqual(len(plots), 1)
        self.assertEqual(plots[0]['x_var'], 't')
        self.assertEqual(plots[0]['y_vars'], ['x', 'v', 'a'])
    
    def test_scatter_plot(self):
        """Test scatter plot type"""
        equations = ['scatter(t, x)']
        plots = self.parser.extract_plot_directives(equations)
        
        self.assertEqual(len(plots), 1)
        self.assertEqual(plots[0]['plot_type'], 'scatter')


class TestParseWithArrays(unittest.TestCase):
    """Tests for the unified parse_with_arrays method"""
    
    def setUp(self):
        self.parser = EquationParser()
    
    def test_full_parse(self):
        """Test complete parsing with arrays and plots"""
        text = """
t = linspace(0, 10, 5)
v = 5
x = v * t
plot(t, x)
"""
        result = self.parser.parse_with_arrays(text)
        
        self.assertIn('t', result['arrays'])
        self.assertIn('t', result['variables'])
        self.assertIn('v', result['variables'])
        self.assertIn('x', result['variables'])
        self.assertEqual(len(result['plots']), 1)
        self.assertTrue(result['is_array_solve'])
    
    def test_no_arrays(self):
        """Test parsing without arrays returns is_array_solve=False"""
        text = "x = 5\ny = x * 2"
        result = self.parser.parse_with_arrays(text)
        
        self.assertFalse(result['is_array_solve'])
        self.assertEqual(len(result['arrays']), 0)


class TestArraySolving(unittest.TestCase):
    """Tests for the solve_with_arrays method"""
    
    def setUp(self):
        self.solver = NumericalSolver()
    
    def test_simple_array_solve(self):
        """Test simple array sweep calculation"""
        equations = [
            't = linspace(0, 4, 5)',
            'v = 2',
            'x = v * t'
        ]
        
        results, warnings, is_array, plots = self.solver.solve_with_arrays(equations)
        
        self.assertTrue(is_array)
        self.assertIn('t', results)
        self.assertIn('x', results)
        self.assertTrue(results['x'].get('is_array'))
        
        # x = v * t, v = 2, t = [0, 1, 2, 3, 4]
        # x should be [0, 2, 4, 6, 8]
        x_values = results['x']['value']
        self.assertEqual(len(x_values), 5)
        self.assertAlmostEqual(x_values[0], 0.0)
        self.assertAlmostEqual(x_values[4], 8.0)
    
    def test_array_with_units(self):
        """Test array solve with unit propagation"""
        equations = [
            't = linspace(0, 10, 3) [s]',
            'v = 5 [m/s]',
            'x = v * t'
        ]
        
        results, warnings, is_array, plots = self.solver.solve_with_arrays(equations)
        
        self.assertTrue(is_array)
        self.assertIn('x', results)
        # x should have units of m (m/s * s)
        self.assertIn('m', results['x']['unit'])
    
    def test_non_array_fallback(self):
        """Test that non-array equations fall back to standard solve"""
        equations = [
            'x = 5',
            'y = x * 2'
        ]
        
        results, warnings, is_array, plots = self.solver.solve_with_arrays(equations)
        
        self.assertFalse(is_array)
        self.assertIn('x', results)
        self.assertIn('y', results)
        self.assertEqual(results['x']['value'], 5)
        self.assertEqual(results['y']['value'], 10)
    
    def test_parallel_mode(self):
        """Test parallel array mode (same-length arrays paired)"""
        equations = [
            't = [1, 2, 3]',
            'P = [100, 200, 300]',
            'result = t * P'
        ]
        
        results, warnings, is_array, plots = self.solver.solve_with_arrays(
            equations, array_mode='parallel'
        )
        
        self.assertTrue(is_array)
        result_values = results['result']['value']
        self.assertEqual(len(result_values), 3)
        self.assertAlmostEqual(result_values[0], 100)
        self.assertAlmostEqual(result_values[1], 400)
        self.assertAlmostEqual(result_values[2], 900)
    
    def test_grid_mode(self):
        """Test grid array mode (cartesian product)"""
        equations = [
            't = [1, 2]',
            'P = [10, 20]',
            'result = t * P'
        ]
        
        results, warnings, is_array, plots = self.solver.solve_with_arrays(
            equations, array_mode='grid'
        )
        
        self.assertTrue(is_array)
        result_values = results['result']['value']
        # Grid mode: 2x2 = 4 combinations
        # (1,10)=10, (1,20)=20, (2,10)=20, (2,20)=40
        self.assertEqual(len(result_values), 4)


if __name__ == '__main__':
    unittest.main()
