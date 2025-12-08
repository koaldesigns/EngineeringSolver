"""
Tests for plotting functionality.

Tests:
- Plot configuration generation
- Axis labels with units
- Multiple trace handling
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solver.plotting import generate_plot_config, generate_plots_from_results


class TestPlotConfigGeneration(unittest.TestCase):
    """Tests for plot configuration generation"""
    
    def test_basic_line_plot(self):
        """Test basic line plot configuration"""
        x_data = [1, 2, 3, 4, 5]
        y_data = {'y': [2, 4, 6, 8, 10]}
        y_units = {'y': 'm'}
        
        config = generate_plot_config(
            x_data=x_data,
            y_data=y_data,
            x_var='x',
            x_unit='s',
            y_units=y_units,
            plot_type='line'
        )
        
        self.assertIn('data', config)
        self.assertIn('layout', config)
        self.assertEqual(len(config['data']), 1)
        self.assertEqual(config['data'][0]['type'], 'scatter')
        self.assertEqual(config['data'][0]['mode'], 'lines')
    
    def test_scatter_plot(self):
        """Test scatter plot configuration"""
        x_data = [1, 2, 3]
        y_data = {'y': [2, 4, 6]}
        y_units = {'y': ''}
        
        config = generate_plot_config(
            x_data=x_data,
            y_data=y_data,
            x_var='x',
            x_unit='',
            y_units=y_units,
            plot_type='scatter'
        )
        
        self.assertEqual(config['data'][0]['mode'], 'markers')
    
    def test_axis_labels_with_units(self):
        """Test that axis labels include units"""
        x_data = [1, 2, 3]
        y_data = {'velocity': [2, 4, 6]}
        y_units = {'velocity': 'm/s'}
        
        config = generate_plot_config(
            x_data=x_data,
            y_data=y_data,
            x_var='time',
            x_unit='s',
            y_units=y_units
        )
        
        # Check X axis label includes unit
        x_label = config['layout']['xaxis']['title']['text']
        self.assertIn('s', x_label)
        self.assertIn('time', x_label)
        
        # Check Y axis label includes unit
        y_label = config['layout']['yaxis']['title']['text']
        self.assertIn('m/s', y_label)
    
    def test_multiple_y_traces(self):
        """Test plot with multiple Y variables"""
        x_data = [1, 2, 3]
        y_data = {
            'x': [1, 2, 3],
            'v': [1, 1, 1],
            'a': [0, 0, 0]
        }
        y_units = {'x': 'm', 'v': 'm/s', 'a': 'm/s²'}
        
        config = generate_plot_config(
            x_data=x_data,
            y_data=y_data,
            x_var='t',
            x_unit='s',
            y_units=y_units
        )
        
        # Should have 3 traces
        self.assertEqual(len(config['data']), 3)
        
        # Legend should be shown for multiple traces
        self.assertTrue(config['layout']['showlegend'])


class TestGeneratePlotsFromResults(unittest.TestCase):
    """Tests for generating plots from solver results"""
    
    def test_generate_from_results(self):
        """Test generating plot from solved results"""
        results = {
            't': {'value': [0, 1, 2, 3, 4], 'unit': 's', 'is_array': True},
            'x': {'value': [0, 2, 4, 6, 8], 'unit': 'm', 'is_array': True},
            'v': {'value': [2, 2, 2, 2, 2], 'unit': 'm/s', 'is_array': True}
        }
        
        plot_directives = [
            {'x_var': 't', 'y_vars': ['x'], 'plot_type': 'line'}
        ]
        
        plots = generate_plots_from_results(results, plot_directives)
        
        self.assertEqual(len(plots), 1)
        self.assertIn('data', plots[0])
        self.assertIn('layout', plots[0])
    
    def test_missing_variable(self):
        """Test handling of missing variables in plot directive"""
        results = {
            't': {'value': [0, 1, 2], 'unit': 's', 'is_array': True}
        }
        
        # Directive references 'x' which doesn't exist
        plot_directives = [
            {'x_var': 't', 'y_vars': ['x'], 'plot_type': 'line'}
        ]
        
        plots = generate_plots_from_results(results, plot_directives)
        
        # Should return empty list since y_var is missing
        self.assertEqual(len(plots), 0)


if __name__ == '__main__':
    unittest.main()
