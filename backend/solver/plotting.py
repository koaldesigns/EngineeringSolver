"""
Plotting utilities for generating Plotly chart configurations.

This module generates Plotly-compatible JSON configurations that can be
rendered by react-plotly.js on the frontend.

NOTE FOR DEVELOPERS/AGENTS:
When modifying plotting behavior or adding new plot types:
1. Update FEATURE_REFERENCE.md in project root
2. Update frontend/src/Documentation.jsx
3. Ensure plot configs are compatible with react-plotly.js
"""

from typing import Dict, List, Any, Optional
import json


def generate_plot_config(
    x_data: List[float],
    y_data: Dict[str, List[float]],
    x_var: str,
    x_unit: str,
    y_units: Dict[str, str],
    plot_type: str = "line",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Plotly JSON configuration for frontend rendering.
    
    Args:
        x_data: List of X-axis values
        y_data: Dict mapping variable names to their value lists
        x_var: Name of X-axis variable
        x_unit: Unit string for X-axis
        y_units: Dict mapping Y variable names to their units
        plot_type: "line" or "scatter"
        title: Optional plot title (auto-generated if None)
    
    Returns:
        Plotly configuration dict compatible with react-plotly.js
    """
    traces = []
    
    # Color palette for multiple traces
    colors = [
        '#00d4ff',  # Cyan
        '#ff6b6b',  # Coral
        '#4ecdc4',  # Teal
        '#ffe66d',  # Yellow
        '#95e1d3',  # Mint
        '#f38181',  # Pink
        '#aa96da',  # Purple
        '#a8e6cf',  # Light green
        '#ffc8dd',  # Light pink
        '#bde0fe',  # Light blue
    ]
    
    # Filter out NaN/None values for robustness
    def clean_values(x_vals, y_vals):
        """Remove points where either x or y is NaN/None."""
        clean_x, clean_y = [], []
        for x, y in zip(x_vals, y_vals):
            if x is not None and y is not None:
                try:
                    # Check for NaN
                    if x == x and y == y:  # NaN != NaN
                        clean_x.append(x)
                        clean_y.append(y)
                except (TypeError, ValueError):
                    pass
        return clean_x, clean_y
    
    for idx, (var_name, values) in enumerate(y_data.items()):
        unit = y_units.get(var_name, '')
        label = f"{var_name}" + (f" [{unit}]" if unit else "")
        
        # Clean data (remove NaN/None)
        clean_x, clean_y = clean_values(x_data, values)
        
        # Skip if no valid data points
        if not clean_x or not clean_y:
            continue
        
        trace = {
            "x": clean_x,
            "y": clean_y,
            "name": label,
            "type": "scatter",
            "mode": "lines" if plot_type == "line" else "markers",
            "line": {"color": colors[idx % len(colors)], "width": 2},
            "marker": {"color": colors[idx % len(colors)], "size": 8}
        }
        traces.append(trace)
    
    # Build X-axis label
    x_label = x_var + (f" [{x_unit}]" if x_unit else "")
    
    # Build Y-axis label (use first Y variable's unit if only one)
    if len(y_data) == 1:
        first_var = list(y_data.keys())[0]
        y_unit = y_units.get(first_var, '')
        y_label = first_var + (f" [{y_unit}]" if y_unit else "")
    else:
        y_label = "Value"
    
    # Auto-generate title if not provided
    if not title:
        if len(y_data) == 1:
            first_var = list(y_data.keys())[0]
            title = f"{first_var} vs {x_var}"
        else:
            y_names = ", ".join(y_data.keys())
            title = f"{y_names} vs {x_var}"
    
    layout = {
        "title": {
            "text": title,
            "font": {"size": 16, "color": "#e0e0e0"}
        },
        "xaxis": {
            "title": {"text": x_label, "font": {"size": 14, "color": "#b0b0b0"}},
            "gridcolor": "rgba(255, 255, 255, 0.1)",
            "zerolinecolor": "rgba(255, 255, 255, 0.2)",
            "tickfont": {"color": "#a0a0a0"}
        },
        "yaxis": {
            "title": {"text": y_label, "font": {"size": 14, "color": "#b0b0b0"}},
            "gridcolor": "rgba(255, 255, 255, 0.1)",
            "zerolinecolor": "rgba(255, 255, 255, 0.2)",
            "tickfont": {"color": "#a0a0a0"}
        },
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        "plot_bgcolor": "rgba(30, 30, 30, 0.8)",
        "font": {"color": "#e0e0e0"},
        "showlegend": len(y_data) > 1,
        "legend": {
            "bgcolor": "rgba(30, 30, 30, 0.8)",
            "bordercolor": "rgba(255, 255, 255, 0.1)",
            "font": {"color": "#e0e0e0"}
        },
        "margin": {"l": 60, "r": 30, "t": 70, "b": 70},
        "hovermode": "x unified"
    }
    
    return {
        "data": traces,
        "layout": layout
    }



def generate_plots_from_results(
    results: Dict[str, Dict],
    plot_directives: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate all plot configurations from solved results and plot directives.
    
    Args:
        results: Solver results dict {var: {value: ..., unit: ..., is_array: ...}}
        plot_directives: List of plot directives from parser
            [{'x_var': str, 'y_vars': [str], 'plot_type': str}, ...]
    
    Returns:
        List of Plotly configuration dicts
    """
    plots = []
    
    for directive in plot_directives:
        x_var = directive['x_var']
        y_vars = directive['y_vars']
        plot_type = directive.get('plot_type', 'line')
        
        # Get X data
        if x_var not in results:
            continue
        
        x_result = results[x_var]
        x_data = x_result.get('value', [])
        x_unit = x_result.get('unit', '')
        
        # Skip if X is not an array
        if not isinstance(x_data, list):
            x_data = [x_data]
        
        # Get Y data for each variable
        y_data = {}
        y_units = {}
        
        for y_var in y_vars:
            if y_var not in results:
                continue
            
            y_result = results[y_var]
            y_values = y_result.get('value', [])
            
            if not isinstance(y_values, list):
                y_values = [y_values]
            
            # Ensure same length
            if len(y_values) == len(x_data):
                y_data[y_var] = y_values
                y_units[y_var] = y_result.get('unit', '')
        
        if not y_data:
            continue
        
        # Generate plot config
        config = generate_plot_config(
            x_data=x_data,
            y_data=y_data,
            x_var=x_var,
            x_unit=x_unit,
            y_units=y_units,
            plot_type=plot_type
        )
        
        plots.append(config)
    
    return plots
