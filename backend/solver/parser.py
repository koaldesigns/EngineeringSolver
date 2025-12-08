import re
import ast
import numpy as np
from typing import List, Set, Tuple, Dict, Any, Optional

class EquationParser:
    """
    Parses user-inputted equations to identify variables and prepare them for the numerical solver.
    
    NOTE FOR DEVELOPERS/AGENTS:
    When modifying parsing behavior or adding new syntax features:
    1. Update FEATURE_REFERENCE.md in project root
    2. Update frontend/src/Documentation.jsx
    3. Update the reserved_words set below if adding new function names
    
    ARRAY/SWEEP SUPPORT:
    - linspace(start, end, count) - Generate evenly spaced values
    - arange(start, end, step) - Generate range with step
    - [val1, val2, val3, ...] - Explicit array literals
    - @parallel or @grid - Array combination mode directive
    - plot(x_var, y_var) or plot(x_var, [y1, y2]) - Plot directives
    """

    def __init__(self):
        self.reserved_words = {
            'sin', 'cos', 'tan', 'exp', 'log', 'log10', 'sqrt', 'pi',
            'abs', 'min', 'max', 'pow', 'sinh', 'cosh', 'tanh', 'asin', 'acos', 'atan',
            'sum', 'integral', 'derivative', 'diff', 'convert', 'prop', 'Q_',
            'linspace', 'arange', 'plot', 'scatter'  # Array and plotting functions
        }

    def _preprocess(self, eq: str) -> str:
        """
        Transforms inline units like '5 [m]' into 'Q_(5, "m")'.
        """
        # Regex to match number followed by [unit]
        # Captures: 1. Number (int or float) 2. Unit string
        def repl(match):
            # Check characters before the match to see if it's an exponent
            start_idx = match.start()
            # Scan backwards to find first non-whitespace
            i = start_idx - 1
            while i >= 0 and eq[i].isspace():
                i -= 1
            
            # If we hit a caret, it's an exponent -> Don't convert
            if i >= 0 and eq[i] == '^':
                return match.group(0) # Return original text
            
            # Otherwise convert to Quantity
            number = match.group(1)
            unit = match.group(2)
            return f'Q_({number}, "{unit}")'

        # Regex to match number followed by [unit]
        # Captures: 1. Number (int, float, or scientific notation) 2. Unit string
        # Scientific notation: 200e9, 1.5e-10, 3.14E+5, etc.
        return re.sub(r'(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*\[(.*?)\]', repl, eq)

    def extract_array_mode(self, equations: List[str]) -> str:
        """
        Extracts the array combination mode from directive comments.
        
        Looks for @parallel or @grid directive at the start of any line.
        Default is 'parallel' if not specified.
        
        Returns:
            'parallel' or 'grid'
        """
        for eq in equations:
            eq_stripped = eq.strip().lower()
            if eq_stripped.startswith('@parallel'):
                return 'parallel'
            elif eq_stripped.startswith('@grid'):
                return 'grid'
        return 'parallel'  # Default

    def extract_arrays(self, equations: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Extracts array variable definitions from equations.
        
        Supports:
        - linspace(start, end, count) - evenly spaced values
        - arange(start, end, step) - values with step
        - [val1, val2, val3, ...] - explicit array literals
        
        Returns:
            Dict[var_name, {
                'type': 'linspace' | 'arange' | 'explicit',
                'values': List[float],
                'unit': Optional[str]
            }]
        """
        arrays = {}
        
        for eq in equations:
            # Skip directives and comments
            if eq.strip().startswith('@') or eq.strip().startswith('//') or eq.strip().startswith('#'):
                continue
            
            # Skip plot directives
            if 'plot(' in eq.lower():
                continue
            
            # Check for linspace: var = linspace(start, end, count) [unit]
            linspace_match = re.match(
                r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*linspace\s*\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(\d+)\s*\)\s*(?:\[([^\]]+)\])?\s*$',
                eq, re.IGNORECASE
            )
            if linspace_match:
                var = linspace_match.group(1)
                start = float(linspace_match.group(2))
                end = float(linspace_match.group(3))
                count = int(linspace_match.group(4))
                unit = linspace_match.group(5)
                
                arrays[var] = {
                    'type': 'linspace',
                    'values': np.linspace(start, end, count).tolist(),
                    'unit': unit.strip() if unit else None,
                    'start': start,
                    'end': end,
                    'count': count
                }
                continue
            
            # Check for arange: var = arange(start, end, step) [unit]
            arange_match = re.match(
                r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*arange\s*\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)\s*(?:\[([^\]]+)\])?\s*$',
                eq, re.IGNORECASE
            )
            if arange_match:
                var = arange_match.group(1)
                start = float(arange_match.group(2))
                end = float(arange_match.group(3))
                step = float(arange_match.group(4))
                unit = arange_match.group(5)
                
                arrays[var] = {
                    'type': 'arange',
                    'values': np.arange(start, end, step).tolist(),
                    'unit': unit.strip() if unit else None,
                    'start': start,
                    'end': end,
                    'step': step
                }
                continue
            
            # Check for explicit array: var = [val1, val2, ...] [unit]
            explicit_match = re.match(
                r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\[\s*([^\]]+)\s*\]\s*(?:\[([^\]]+)\])?\s*$',
                eq
            )
            if explicit_match:
                var = explicit_match.group(1)
                values_str = explicit_match.group(2)
                unit = explicit_match.group(3)
                
                # Parse the comma-separated values (supports scientific notation)
                try:
                    values = []
                    for v in values_str.split(','):
                        v_clean = v.strip()
                        # Handle scientific notation: 1e-6, 2.5E+10, etc.
                        values.append(float(v_clean))
                    
                    # Validate: at least 1 value
                    if len(values) >= 1:
                        arrays[var] = {
                            'type': 'explicit',
                            'values': values,
                            'unit': unit.strip() if unit else None
                        }
                except (ValueError, TypeError):
                    # Not a valid numeric array, skip
                    pass
        
        return arrays

    def extract_plot_directives(self, equations: List[str]) -> List[Dict[str, Any]]:
        """
        Extracts plot() directives from equations.
        
        Supports:
        - plot(x_var, y_var) - single Y variable
        - plot(x_var, [y1, y2, y3]) - multiple Y variables
        - plot(x_var, y_var, type='scatter') - specify plot type
        
        Returns:
            List of plot configurations: [
                {
                    'x_var': str,
                    'y_vars': List[str],
                    'plot_type': 'line' | 'scatter'
                },
                ...
            ]
        """
        plots = []
        
        for eq in equations:
            eq_clean = eq.strip()
            
            # Check for plot() or scatter() call
            plot_match = re.match(
                r'^(plot|scatter)\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*(.+?)\s*(?:,\s*type\s*=\s*[\'"](\w+)[\'"]\s*)?\)\s*$',
                eq_clean, re.IGNORECASE
            )
            
            if plot_match:
                func_name = plot_match.group(1).lower()
                x_var = plot_match.group(2)
                y_spec = plot_match.group(3).strip()
                explicit_type = plot_match.group(4)
                
                # Determine plot type: explicit type > function name > default
                if explicit_type:
                    plot_type = explicit_type.lower()
                elif func_name == 'scatter':
                    plot_type = 'scatter'
                else:
                    plot_type = 'line'
                
                # Parse y_vars - could be single var or [var1, var2, ...]
                if y_spec.startswith('[') and y_spec.endswith(']'):
                    # Multiple Y variables
                    y_inner = y_spec[1:-1]
                    y_vars = [v.strip() for v in y_inner.split(',')]
                else:
                    # Single Y variable
                    y_vars = [y_spec]
                
                plots.append({
                    'x_var': x_var,
                    'y_vars': y_vars,
                    'plot_type': plot_type
                })
        
        return plots

    def filter_equations_for_solving(self, equations: List[str], arrays: Dict[str, Dict]) -> List[str]:
        """
        Filters out array definitions, directives, and plot calls from equations,
        returning only equations that should be passed to the solver.
        """
        filtered = []
        array_vars = set(arrays.keys())
        
        for eq in equations:
            eq_stripped = eq.strip()
            
            # Skip empty lines
            if not eq_stripped:
                continue
            
            # Skip directives
            if eq_stripped.startswith('@'):
                continue
            
            # Skip plot calls
            if eq_stripped.lower().startswith('plot('):
                continue
            
            # Skip array variable definitions (they're handled separately)
            if '=' in eq_stripped:
                lhs = eq_stripped.split('=')[0].strip()
                # Remove any unit brackets from LHS
                lhs_clean = re.sub(r'\s*\[.*?\]', '', lhs).strip()
                if lhs_clean in array_vars:
                    continue
            
            filtered.append(eq)
        
        return filtered

    def _extract_bound_variables(self, equations: List[str]) -> Set[str]:
        """
        Extracts bound variables from functions like sum(), integral(), derivative().
        
        These are variables that appear as the iteration/integration variable in
        special functions and should NOT be treated as unknowns.
        
        Patterns:
        - sum(expr, var, start, end) - 'var' is bound
        - integral(expr, var, lower, upper) - 'var' is bound
        - derivative(expr, var, point) - 'var' is bound
        """
        bound_vars = set()
        
        # Patterns for extracting bound variables
        # sum(expr, var, start, end)
        sum_pattern = r'\bsum\s*\(\s*[^,]+\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,'
        # integral(expr, var, lower, upper)
        integral_pattern = r'\bintegral\s*\(\s*[^,]+\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,'
        # derivative(expr, var, ...)
        derivative_pattern = r'\b(?:derivative|diff)\s*\(\s*[^,]+\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[,)]'
        
        for eq in equations:
            # Remove comments
            clean_eq = re.sub(r'//.*|#.*', '', eq)
            
            # Find sum bound variables
            for match in re.finditer(sum_pattern, clean_eq, re.IGNORECASE):
                bound_vars.add(match.group(1))
            
            # Find integral bound variables
            for match in re.finditer(integral_pattern, clean_eq, re.IGNORECASE):
                bound_vars.add(match.group(1))
            
            # Find derivative bound variables
            for match in re.finditer(derivative_pattern, clean_eq, re.IGNORECASE):
                bound_vars.add(match.group(1))
        
        return bound_vars

    def extract_variables(self, equations: List[str]) -> Tuple[Set[str], Dict[str, str]]:
        """
        Identifies all unique variables and their units using AST to avoid capturing strings.
        """
        variables = set()
        variable_units = {}
        
        # First, extract bound variables that should be excluded
        bound_vars = self._extract_bound_variables(equations)
        
        # Combine all equations into a single script for AST parsing
        clean_lines = []
        
        for eq in equations:
            # Preprocess to handle inline units (converts 5 [m] to Q_(5, "m"))
            pre_eq = self._preprocess(eq)
            
            # Extract unit if present (remaining [unit] blocks, e.g. casts or LHS units)
            # We search in original eq to capture 'x = 5 [m]' style which preprocess hides
            unit_match = re.search(r'\[(.*?)\]', eq)
            current_unit = None
            if unit_match:
                current_unit = unit_match.group(1).strip()
            
            # Remove comments and units
            clean_eq = re.sub(r'//.*|#.*', '', pre_eq)
            clean_eq = re.sub(r'\[.*?\]', '', clean_eq).strip()
            
            if not clean_eq:
                continue
                
            clean_lines.append(clean_eq)
            
            # Heuristic for associating units with LHS variable
            if '=' in clean_eq:
                parts = clean_eq.split('=', 1)
                lhs_part = parts[0].strip()
                
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', lhs_part):
                    # Check for explicit LHS declaration: "x [m] = ..."
                    # We need to look at original `eq` relative to `=` position to support this robustly.
                    
                    base_eq = re.sub(r'//.*|#.*', '', eq).strip()
                    eq_sign_pos = base_eq.find('=')
                    
                    target_unit = None
                    if eq_sign_pos != -1:
                        # Find all units
                        unit_iter = re.finditer(r'\[(.*?)\]', base_eq)
                        for m in unit_iter:
                            u_str = m.group(1).strip()
                            start, end = m.span()
                            
                            # Case 1: Unit is on LHS (before = or immediately adjacent)
                            if end <= eq_sign_pos:
                                target_unit = u_str
                                break 
                            
                            # Case 2: Unit is at END of line
                            # Must be strictly at end (ignoring whitespace)
                            if not base_eq[end:].strip():
                                target_unit = u_str
                    
                    if target_unit:
                        variable_units[lhs_part] = target_unit

        full_code = "\n".join(clean_lines)
        
        try:
            tree = ast.parse(full_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if node.id not in self.reserved_words and node.id not in bound_vars:
                        variables.add(node.id)
        except SyntaxError:
            # Fallback to regex if AST fails
            for line in clean_lines:
                tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', line)
                for token in tokens:
                    if token not in self.reserved_words and token not in bound_vars:
                        variables.add(token)

        return variables, variable_units

    def extract_assignments(self, equations: List[str]) -> Dict[str, str]:
        """
        Extracts explicit assignments (var = expr) for unit inference.
        """
        assignments = {}
        for eq in equations:
            # Preprocess inline units
            pre_eq = self._preprocess(eq)
            
            # Remove comments and units
            clean_eq = re.sub(r'//.*|#.*', '', pre_eq)
            clean_eq = re.sub(r'\[.*?\]', '', clean_eq).strip()
            
            if '=' in clean_eq:
                # Replace ^ with ** for exponentiation
                clean_eq = clean_eq.replace('^', '**')
                
                parts = clean_eq.split('=')
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    rhs = parts[1].strip()
                    # Check if LHS is a single variable
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', lhs):
                        assignments[lhs] = rhs
        return assignments

    def normalize_equations(self, equations: List[str]) -> List[str]:
        """
        Converts equations to 'lhs - (rhs)' format for root finding.
        """
        normalized = []
        for eq in equations:
            # Preprocess inline units
            pre_eq = self._preprocess(eq)
            
            # Remove comments and units
            clean_eq = re.sub(r'//.*|#.*', '', pre_eq)
            clean_eq = re.sub(r'\[.*?\]', '', clean_eq).strip()
            
            if not clean_eq:
                continue
            
            # Replace ^ with ** for exponentiation
            clean_eq = clean_eq.replace('^', '**')
                
            if '=' in clean_eq:
                lhs, rhs = clean_eq.split('=', 1)
                # Convert to (lhs) - (rhs)
                normalized.append(f"({lhs.strip()}) - ({rhs.strip()})")
            else:
                # Assume it's already an expression equal to 0
                normalized.append(clean_eq)
        return normalized

    def parse(self, text: str) -> Tuple[Set[str], List[str], Dict[str, str]]:
        """
        Main entry point (backwards compatible).
        Parses the full equation text, extracts variables, units, and normalizes equations.
        
        NOTE: For array support, use parse_with_arrays() instead.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        variables, variable_units = self.extract_variables(lines)
        normalized_eqs = self.normalize_equations(lines)
        return variables, normalized_eqs, variable_units

    def parse_with_arrays(self, text: str) -> Dict[str, Any]:
        """
        Enhanced entry point that supports array/sweep variables and plot directives.
        
        Returns:
            {
                'variables': Set[str],          # All variable names
                'variable_units': Dict[str, str],  # Explicit unit specs
                'normalized_equations': List[str],  # Equations for solving
                'arrays': Dict[str, Dict],      # Array variable definitions
                'array_mode': str,              # 'parallel' or 'grid'
                'plots': List[Dict],            # Plot directives
                'is_array_solve': bool          # True if any arrays present
            }
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract array definitions first
        arrays = self.extract_arrays(lines)
        array_mode = self.extract_array_mode(lines)
        plots = self.extract_plot_directives(lines)
        
        # Filter out array definitions and directives before regular parsing
        filtered_lines = self.filter_equations_for_solving(lines, arrays)
        
        # Standard parsing on filtered equations
        variables, variable_units = self.extract_variables(filtered_lines)
        normalized_eqs = self.normalize_equations(filtered_lines)
        
        # Add array variables to the set
        for var in arrays.keys():
            variables.add(var)
            if arrays[var].get('unit'):
                variable_units[var] = arrays[var]['unit']
        
        return {
            'variables': variables,
            'variable_units': variable_units,
            'normalized_equations': normalized_eqs,
            'arrays': arrays,
            'array_mode': array_mode,
            'plots': plots,
            'is_array_solve': len(arrays) > 0
        }
