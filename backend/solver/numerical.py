import numpy as np
from scipy.optimize import root
import re
from typing import List, Dict, Callable
import sympy
import pint
from .parser import EquationParser
from .units import UnitRegistry

class NumericalSolver:
    """
    Solves a system of non-linear equations.
    
    ============================================================================
    IMPORTANT NOTE FOR DEVELOPERS/AGENTS:
    ============================================================================
    When adding new features, functions, or operators to this solver:
    
    1. Update the frontend Documentation component:
       frontend/src/Documentation.jsx
       
    2. Update the feature reference markdown file:
       FEATURE_REFERENCE.md (in project root)
       
    3. Add stress tests for the new feature:
       stress_test.py
       
    4. If the feature involves units, document the unit behavior
    
    This ensures users can discover and properly use all solver capabilities.
    ============================================================================
    """
    def __init__(self):
        self.parser = EquationParser()
        self.unit_registry = UnitRegistry()

    coolprop_units = {
        'D': 'kg/m**3', 'DMASS': 'kg/m**3', 'DMOLAR': 'mol/m**3',
        'V': 'm**3/kg', 'T': 'K', 'P': 'Pa',
        'H': 'J/kg', 'HMASS': 'J/kg', 'HMOLAR': 'J/mol',
        'U': 'J/kg', 'UMASS': 'J/kg', 'UMOLAR': 'J/mol',
        'S': 'J/kg/K', 'SMASS': 'J/kg/K', 'SMOLAR': 'J/mol/K',
        'C': 'J/kg/K', 'CPMASS': 'J/kg/K', 'CVMASS': 'J/kg/K',
        'CPMOLAR': 'J/mol/K', 'CVMOLAR': 'J/mol/K', 'CP': 'J/kg/K', 'CV': 'J/kg/K',
        'VISCOSITY': 'Pa*s', 'MU': 'Pa*s',
        'CONDUCTIVITY': 'W/m/K', 'K': 'W/m/K', 'L': 'W/m/K',
        'A': 'm/s', 'SPEED_OF_SOUND': 'm/s',
        'Q': '', 'M': 'kg/mol', 'MOLAR_MASS': 'kg/mol',
        'GAS_CONSTANT': 'J/mol/K',
    }

    def solve_with_arrays(self, equations: List[str], initial_guesses: Dict[str, float] = None, 
                          angle_unit: str = 'deg', array_mode: str = 'parallel') -> Dict[str, any]:
        """
        Solves a system of equations that may contain array/sweep variables.
        
        Array variables can be defined using:
        - linspace(start, end, count)
        - arange(start, end, step)
        - [val1, val2, val3, ...]
        
        Args:
            equations: List of equation strings
            initial_guesses: Optional dict of variable -> initial value
            angle_unit: 'deg' or 'rad' for trig functions
            array_mode: 'parallel' or 'grid'
                - parallel: Arrays are iterated together (must have same length)
                - grid: All combinations of array values (cartesian product)
        
        Returns:
            Tuple of (results_dict, unit_warnings, is_array_solve)
            
            For array solves, result values are lists:
            {
                'x': {'value': [1, 2, 3], 'unit': 'm', 'is_array': True},
                'y': {'value': [4, 5, 6], 'unit': 'm/s', 'is_array': True},
                ...
            }
        """
        import itertools
        
        # Parse with array support
        parse_result = self.parser.parse_with_arrays("\n".join(equations))
        
        arrays = parse_result['arrays']
        is_array_solve = parse_result['is_array_solve']
        plots = parse_result['plots']
        
        # If no arrays, use standard solve
        if not is_array_solve:
            results, warnings = self.solve(equations, initial_guesses, angle_unit)
            return results, warnings, False, plots
        
        # Get array variable names and their values
        array_vars = list(arrays.keys())
        array_values = [arrays[var]['values'] for var in array_vars]
        array_units = {var: arrays[var].get('unit') for var in array_vars}
        
        # Generate combinations based on mode
        if array_mode == 'parallel':
            # All arrays must have the same length for parallel mode
            lengths = [len(vals) for vals in array_values]
            if len(set(lengths)) > 1:
                raise ValueError(
                    f"Parallel mode requires all arrays to have the same length. "
                    f"Got lengths: {dict(zip(array_vars, lengths))}"
                )
            combinations = list(zip(*array_values))
        else:  # grid mode
            combinations = list(itertools.product(*array_values))
        
        num_cases = len(combinations)
        
        # Limit the number of cases to prevent runaway computation
        MAX_CASES = 1000
        if num_cases > MAX_CASES:
            raise ValueError(
                f"Too many combinations ({num_cases}). Grid mode with these arrays "
                f"creates {num_cases} solve cases. Maximum allowed is {MAX_CASES}. "
                f"Reduce array sizes or use 'parallel' mode."
            )
        
        # Filter equations to remove array definitions (they're handled here)
        filtered_equations = parse_result['normalized_equations']
        
        # But we need the original equation format for solve(), not normalized
        # So use filter_equations_for_solving from the parser
        solvable_equations = self.parser.filter_equations_for_solving(
            [e.strip() for e in equations if e.strip()], 
            arrays
        )
        
        # Initialize result collectors
        all_results = {}
        all_warnings = []
        first_error = None  # Track first error for better reporting

        
        # Solve for each combination
        for case_idx, combo in enumerate(combinations):
            # Build substituted equations
            case_equations = []
            
            # First, add the array variable assignments with their current values
            for var_idx, var in enumerate(array_vars):
                val = combo[var_idx]
                unit = array_units.get(var)
                if unit:
                    case_equations.append(f"{var} = {val} [{unit}]")
                else:
                    case_equations.append(f"{var} = {val}")
            
            # Add the rest of the equations
            case_equations.extend(solvable_equations)
            
            try:
                # Solve this case
                results, warnings = self.solve(case_equations, initial_guesses, angle_unit)
                
                # Collect results
                for var, data in results.items():
                    if var not in all_results:
                        all_results[var] = {
                            'values': [],
                            'unit': data.get('unit', ''),
                            'unit_source': data.get('unit_source', 'propagated'),
                            'is_array': True
                        }
                    all_results[var]['values'].append(data['value'])
                
                # Collect warnings (just from first case to avoid spam)
                if case_idx == 0 and warnings:
                    all_warnings.extend(warnings)
                    
            except Exception as e:
                # Track first error for better reporting
                if first_error is None:
                    first_error = str(e)
                    all_warnings.append(f"Some solve cases failed: {first_error}")
                
                # If a case fails, fill with NaN
                for var in all_results:
                    all_results[var]['values'].append(float('nan'))
        
        # Convert to final format
        final_results = {}
        for var, data in all_results.items():
            final_results[var] = {
                'value': data['values'],
                'unit': data['unit'],
                'unit_source': data.get('unit_source', 'propagated'),
                'is_array': True
            }
        
        # Also include array variable definitions in results (they are always explicit)
        for var in array_vars:
            if var not in final_results:
                final_results[var] = {
                    'value': arrays[var]['values'],
                    'unit': array_units.get(var, ''),
                    'unit_source': 'explicit',  # Array definitions are always user-explicit
                    'is_array': True
                }
        
        return final_results, all_warnings if all_warnings else None, True, plots

    def solve(self, equations: List[str], initial_guesses: Dict[str, float] = None, angle_unit: str = 'deg') -> Dict[str, any]:
        """
        Solves the system of equations.
        Returns dictionary with values and units.
        
        Strategy:
        1. Parse all equations to identify variables and their units
        2. Extract explicit assignments (var = literal or computable expression)
        3. Iteratively evaluate assignments where RHS is computable
        4. Use numerical solver only for remaining truly implicit equations
        """
        import math
        import scipy.integrate as integrate
        import re
        
        # Prepare context with math functions
        context = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
        
        # Smart Trig Functions that handle Units
        def smart_sin(x):
            if hasattr(x, 'units'):
                try:
                    return math.sin(x.to('radian').magnitude)
                except pint.DimensionalityError:
                    if x.dimensionless:
                        val = x.magnitude
                        return math.sin(math.radians(val) if angle_unit == 'deg' else val)
                    else:
                        raise ValueError(f"sin expects angle or dimensionless, got {x.units}")
            else:
                return math.sin(math.radians(x) if angle_unit == 'deg' else x)

        def smart_cos(x):
            if hasattr(x, 'units'):
                try:
                    return math.cos(x.to('radian').magnitude)
                except pint.DimensionalityError:
                    if x.dimensionless:
                        val = x.magnitude
                        return math.cos(math.radians(val) if angle_unit == 'deg' else val)
                    else:
                        raise ValueError(f"cos expects angle or dimensionless, got {x.units}")
            else:
                return math.cos(math.radians(x) if angle_unit == 'deg' else x)

        def smart_tan(x):
            if hasattr(x, 'units'):
                try:
                    return math.tan(x.to('radian').magnitude)
                except pint.DimensionalityError:
                    if x.dimensionless:
                        val = x.magnitude
                        return math.tan(math.radians(val) if angle_unit == 'deg' else val)
                    else:
                        raise ValueError(f"tan expects angle or dimensionless, got {x.units}")
            else:
                return math.tan(math.radians(x) if angle_unit == 'deg' else x)

        def smart_asin(x):
            val = x.magnitude if hasattr(x, 'units') else x
            res_rad = math.asin(val)
            if angle_unit == 'deg':
                return self.unit_registry.Q_(math.degrees(res_rad), 'deg')
            return self.unit_registry.Q_(res_rad, 'rad')

        def smart_acos(x):
            val = x.magnitude if hasattr(x, 'units') else x
            res_rad = math.acos(val)
            if angle_unit == 'deg':
                return self.unit_registry.Q_(math.degrees(res_rad), 'deg')
            return self.unit_registry.Q_(res_rad, 'rad')

        def smart_atan(x):
            val = x.magnitude if hasattr(x, 'units') else x
            res_rad = math.atan(val)
            if angle_unit == 'deg':
                return self.unit_registry.Q_(math.degrees(res_rad), 'deg')
            return self.unit_registry.Q_(res_rad, 'rad')

        context['sin'] = smart_sin
        context['cos'] = smart_cos
        context['tan'] = smart_tan
        context['asin'] = smart_asin
        context['acos'] = smart_acos
        context['atan'] = smart_atan
        
        # Unit-aware sqrt - properly handles unit propagation
        def smart_sqrt(x):
            if hasattr(x, 'units'):
                # Pint quantities support ** 0.5 which will handle unit square root
                try:
                    return x ** 0.5
                except Exception:
                    # Fallback: compute magnitude and try to propagate units
                    return self.unit_registry.Q_(math.sqrt(x.magnitude), x.units ** 0.5)
            else:
                return math.sqrt(x)
        
        # Unit-aware exp - requires dimensionless input
        def smart_exp(x):
            if hasattr(x, 'units'):
                if x.dimensionless:
                    return math.exp(x.magnitude)
                else:
                    # Exp of dimensional quantity is physically meaningless
                    # Strip units and compute, returning dimensionless
                    return math.exp(x.magnitude)
            else:
                return math.exp(x)
        
        # Unit-aware log (natural log) - requires dimensionless input
        def smart_log(x):
            if hasattr(x, 'units'):
                if x.dimensionless:
                    return math.log(x.magnitude)
                else:
                    # Log of dimensional quantity is physically meaningless
                    # Strip units and compute, returning dimensionless
                    return math.log(x.magnitude)
            else:
                return math.log(x)
        
        # Unit-aware log10 - requires dimensionless input
        def smart_log10(x):
            if hasattr(x, 'units'):
                if x.dimensionless:
                    return math.log10(x.magnitude)
                else:
                    # Log of dimensional quantity is physically meaningless
                    # Strip units and compute, returning dimensionless
                    return math.log10(x.magnitude)
            else:
                return math.log10(x)
        
        # Unit-aware abs - preserves units
        def smart_abs(x):
            if hasattr(x, 'units'):
                return self.unit_registry.Q_(abs(x.magnitude), x.units)
            else:
                return abs(x)
        
        context['sqrt'] = smart_sqrt
        context['exp'] = smart_exp
        context['log'] = smart_log
        context['log10'] = smart_log10
        context['abs'] = smart_abs
        
        context['Q_'] = self.unit_registry.Q_
        
        # Add advanced functions
        def math_sum(func, start, end):
            total = 0.0
            i_start = int(start)
            i_end = int(end)
            for i in range(i_start, i_end + 1):
                total += func(i)
            return total

        def smart_integral(func, lower, upper):
            # Handle units in limits
            t_unit = 1
            low_val = lower
            up_val = upper
            
            if hasattr(lower, 'units'):
                t_unit = lower.units
                low_val = lower.magnitude
                if hasattr(upper, 'units'):
                    up_val = upper.to(t_unit).magnitude
                else:
                    up_val = upper.magnitude # Assume compatible
            elif hasattr(upper, 'units'):
                t_unit = upper.units
                up_val = upper.magnitude
                low_val = lower # Assume compatible

            def wrapper(x):
                # x is float magnitude
                if t_unit != 1:
                    val_in = self.unit_registry.Q_(x, t_unit)
                else:
                    val_in = x
                
                res = func(val_in)
                
                if hasattr(res, 'units'):
                    return res.magnitude
                return res

            # We need to determine the output unit to reconstruct the result
            # Probe at midpoint
            mid = (low_val + up_val) / 2.0
            try:
                if t_unit != 1:
                    probe_in = self.unit_registry.Q_(mid, t_unit)
                else:
                    probe_in = mid
                probe_out = func(probe_in)
                y_unit = probe_out.units if hasattr(probe_out, 'units') else 1
            except Exception:
                y_unit = 1 # Fallback

            val, error = integrate.quad(wrapper, low_val, up_val)
            
            if y_unit != 1 or t_unit != 1:
                return self.unit_registry.Q_(val, y_unit * t_unit)
            return val

        def smart_derivative(func, point, order=1, dx=1e-6):
            # Central difference
            x_val = point
            x_unit = 1
            if hasattr(point, 'units'):
                x_val = point.magnitude
                x_unit = point.units
                
            h = dx
            
            if hasattr(point, 'units'):
                x_plus = self.unit_registry.Q_(x_val + h, x_unit)
                x_minus = self.unit_registry.Q_(x_val - h, x_unit)
                denominator = self.unit_registry.Q_(2 * h, x_unit)
            else:
                x_plus = x_val + h
                x_minus = x_val - h
                denominator = 2 * h
                
            y_plus = func(x_plus)
            y_minus = func(x_minus)
            
            return (y_plus - y_minus) / denominator

        context['math_sum'] = math_sum
        context['math_integral'] = smart_integral
        context['sum'] = math_sum
        context['integral'] = smart_integral
        context['derivative'] = smart_derivative
        context['diff'] = smart_derivative
        
        def prop_wrapper(fluid, out, in1, v1, in2, v2):
             from .thermo import ThermoProps
             
             # Map of standard units for CoolProp inputs
             standard_units = {
                 'T': 'K',
                 'P': 'Pa',
                 'D': 'kg/m**3',
                 'H': 'J/kg',
                 'S': 'J/kg/K',
                 'U': 'J/kg',
                 'Q': '', # Quality is dimensionless
             }
             
             def convert_input(prop_name, val):
                 prop_upper = prop_name.upper() if isinstance(prop_name, str) else str(prop_name)
                 target_unit = standard_units.get(prop_upper)
                 
                 if hasattr(val, 'units'):
                     if target_unit:
                         return val.to(target_unit).magnitude
                     else:
                         return val.to_base_units().magnitude
                 return val

             v1_val = convert_input(in1, v1)
             v2_val = convert_input(in2, v2)
             
             val = ThermoProps().get_prop(fluid, out, in1, v1_val, in2, v2_val)
             
             # Wrap result in units
             out_upper = out.upper() if isinstance(out, str) else str(out)
             unit_str = self.coolprop_units.get(out_upper, '')
             if unit_str:
                 return self.unit_registry.Q_(val, unit_str)
             return val

        context['prop'] = prop_wrapper

        def convert_wrapper(val, from_u, to_u):
            if hasattr(val, 'units'):
                return val.to(to_u).magnitude # Return magnitude as requested by user? Or Quantity?
                # Usually convert(x, 'm', 'ft') returns the value in feet.
                # If we return magnitude, we lose the unit info for further propagation.
                # But if the user writes x = convert(y, 'm', 'ft'), x is likely expected to be just the number if they are doing manual unit management,
                # OR they expect x to be in feet.
                # If we return Quantity(val, 'ft'), then x has unit 'ft'. This is better.
                return val.to(to_u)
            return self.unit_registry.Q_(self.unit_registry.convert(val, from_u, to_u), to_u)
            
        context['convert'] = convert_wrapper
        
        # Helper function to transform EES-style syntax to Python lambda form
        def transform_special_functions(expr):
            """
            Transforms EES-style function calls to Python lambda form:
            - sum(i^2, i, 1, 3) -> sum(lambda i: (i)**2, 1, 3)
            - integral(x^2, x, 0, 1) -> integral(lambda x: (x)**2, 0, 1)
            - derivative(x^2, x, 5) -> derivative(lambda x: (x)**2, 5)
            """
            import re
            result = expr
            
            # Pattern for sum(expr, var, start, end)
            sum_pattern = r'\bsum\s*\(\s*([^,]+)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
            def sum_repl(m):
                func_expr, var_name, start, end = m.groups()
                return f'sum(lambda {var_name}: ({func_expr}), {start}, {end})'
            result = re.sub(sum_pattern, sum_repl, result)
            
            # Pattern for integral(expr, var, lower, upper)
            integral_pattern = r'\bintegral\s*\(\s*([^,]+)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
            def integral_repl(m):
                func_expr, var_name, lower, upper = m.groups()
                return f'integral(lambda {var_name}: ({func_expr}), {lower}, {upper})'
            result = re.sub(integral_pattern, integral_repl, result)
            
            # Pattern for derivative(expr, var, point) or diff(expr, var, point)
            deriv_pattern = r'\b(derivative|diff)\s*\(\s*([^,]+)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*([^)]+)\s*\)'
            def deriv_repl(m):
                func_name, func_expr, var_name, point = m.groups()
                return f'{func_name}(lambda {var_name}: ({func_expr}), {point})'
            result = re.sub(deriv_pattern, deriv_repl, result)
            
            return result
        
        # Parse equations
        variables, normalized_eqs, variable_units = self.parser.parse("\n".join(equations))
        assignments = self.parser.extract_assignments(equations)
        
        # Transform special function syntax in assignments
        assignments = {var: transform_special_functions(expr) for var, expr in assignments.items()}
        
        # Infer units from usage context (trig functions, prop calls)
        inferred_from_usage = self._infer_units_from_usage(equations, variables, variable_units, angle_unit)
        
        # Initialize known values dictionary and unit warnings list
        known_values = {}
        unit_warnings = []
        
        # Handle 'e' as a constant
        if 'e' in variables and 'e' not in assignments:
             known_values['e'] = math.e

        # Validate units before solving (returns warnings, doesn't raise)
        validation_warnings = self._validate_units(equations, variables, variable_units, context)
        unit_warnings.extend(validation_warnings)
        
        # Forward evaluation: iteratively compute all explicit assignments
        max_iterations = len(variables) + 5
        for iteration in range(max_iterations):
            progress = False
            for var, expr in assignments.items():
                if var in known_values:
                    continue
                
                # Build evaluation context
                eval_ctx = {"__builtins__": {}}
                eval_ctx.update(context)
                eval_ctx.update(known_values)
                
                try:
                    value = eval(expr, eval_ctx)
                    
                    # Validate units: if the expression produces units AND the variable has a manual unit annotation
                    if hasattr(value, 'units') and var in variable_units and variable_units[var]:
                        calculated_unit = value.units
                        specified_unit_str = variable_units[var]
                        
                        try:
                            # Create a quantity with the specified unit to check compatibility
                            specified_quantity = self.unit_registry.Q_(1.0, specified_unit_str)
                            
                            # Check if the dimensionalities match
                            if calculated_unit.dimensionality != specified_quantity.units.dimensionality:
                                # Add warning instead of raising error
                                calc_unit_display = self.unit_registry.format_unit_display(f"{calculated_unit:~}")
                                spec_unit_display = self.unit_registry.format_unit_display(specified_unit_str)
                                unit_warnings.append(
                                    f"Variable '{var}': Calculated units ({calc_unit_display}) "
                                    f"do not match specified units ({spec_unit_display}). "
                                    f"Using calculated units."
                                )
                                # Keep the calculated units, don't convert
                            else:
                                # If dimensions match, convert to the specified unit for display
                                # This preserves the user's desired unit format
                                value = value.to(specified_unit_str)
                            
                        except pint.DimensionalityError:
                            # Add warning instead of raising error
                            calc_unit_display = self.unit_registry.format_unit_display(f"{calculated_unit:~}")
                            spec_unit_display = self.unit_registry.format_unit_display(specified_unit_str)
                            unit_warnings.append(
                                f"Variable '{var}': Calculated units ({calc_unit_display}) "
                                f"cannot be converted to specified units ({spec_unit_display}). "
                                f"Using calculated units."
                            )
                    
                    # If the result is a float but we have a known unit for this variable, wrap it
                    elif not hasattr(value, 'units') and var in variable_units and variable_units[var]:
                        specified_unit_str = variable_units[var]
                        
                        # Check if this unit was inferred from usage (trig, prop) vs explicitly specified
                        was_inferred_from_usage = var in inferred_from_usage
                        
                        if was_inferred_from_usage:
                            # Unit was inferred from context (e.g., variable in sin() or prop())
                            # Apply the inferred unit to the value
                            value = self.unit_registry.Q_(value, specified_unit_str)
                        else:
                            # User explicitly specified a unit with [unit] syntax
                            # For explicit units on dimensionless results (e.g., exp(1) [m]),
                            # we should apply the unit - this is EES-style behavior
                            value = self.unit_registry.Q_(value, specified_unit_str)
                    
                    known_values[var] = value
                    progress = True
                except pint.DimensionalityError as e:
                    # Unit mismatch in expression - retry with magnitudes only
                    try:
                        # Build a context with magnitudes stripped from quantities
                        magnitude_ctx = {"__builtins__": {}}
                        magnitude_ctx.update(context)
                        for kv_var, kv_val in known_values.items():
                            if hasattr(kv_val, 'magnitude'):
                                magnitude_ctx[kv_var] = kv_val.magnitude
                            else:
                                magnitude_ctx[kv_var] = kv_val
                        
                        value = eval(expr, magnitude_ctx)
                        known_values[var] = value
                        progress = True
                        
                        # Add warning about the unit issue
                        unit_warnings.append(
                            f"Unit warning for '{var}': {e}. Calculated using numeric values only."
                        )
                    except Exception:
                        # Still failed, skip this variable for now
                        pass
                except Exception as e:
                    # Suppress other errors during forward evaluation
                    pass
            
            if not progress:
                break
        
        
        # Determine which variables still need to be solved numerically
        unknown_vars = [v for v in sorted(variables) if v not in known_values]
        
        # Filter equations to only those involving unknowns
        implicit_eqs = []
        for eq_text in equations:
            # Clean the equation
            clean_eq = re.sub(r'//.*|#.*', '', eq_text)
            clean_eq = re.sub(r'\[.*?\]', '', clean_eq).strip()
            if not clean_eq:
                continue
            
            clean_eq = clean_eq.replace('^', '**')
            
            if '=' in clean_eq:
                lhs, rhs = clean_eq.split('=', 1)
                lhs = lhs.strip()
                rhs = rhs.strip()
                
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', lhs) and lhs in known_values:
                    continue
                
                implicit_eqs.append(f"({lhs}) - ({rhs})")
            else:
                implicit_eqs.append(clean_eq)
        
        if not implicit_eqs or not unknown_vars:
            results = {}
            for var in sorted(variables):
                val = known_values.get(var, 0.0)
                # Determine unit source: explicit (user-defined), inferred (from patterns/usage), or propagated (calculated)
                if var in variable_units and variable_units[var]:
                    if var in inferred_from_usage:
                        unit_source = 'inferred'
                    else:
                        unit_source = 'explicit'
                else:
                    unit_source = 'propagated'
                
                if hasattr(val, 'units'):
                    results[var] = {
                        "value": val.magnitude,
                        "unit": str(val.units),
                        "unit_source": unit_source
                    }
                else:
                    results[var] = {
                        "value": val,
                        "unit": variable_units.get(var, ""),
                        "unit_source": unit_source
                    }
            results, infer_warnings = self._infer_units(results, assignments, variable_units, variables, angle_unit, inferred_from_usage)
            # Merge and deduplicate warnings from forward evaluation with inference warnings
            all_warnings = list(dict.fromkeys(unit_warnings + infer_warnings))  # Preserves order, removes duplicates
            return results, all_warnings if all_warnings else None
        
        # Set up initial guesses for unknowns
        if not initial_guesses:
            initial_guesses = {}
        
        x0 = [initial_guesses.get(v, 1.0) for v in unknown_vars]

        def residuals(vars_values):
            local_vars = dict(zip(unknown_vars, vars_values))
            
            for var in unknown_vars:
                if variable_units.get(var):
                    try:
                        local_vars[var] = self.unit_registry.Q_(local_vars[var], variable_units[var])
                    except Exception:
                        pass

            local_vars.update(known_values)
            local_vars.update(context)
            
            res = []
            for eq in implicit_eqs:
                try:
                    val = eval(eq, {"__builtins__": {}}, local_vars)
                    if hasattr(val, 'units'):
                        try:
                            res.append(val.to_base_units().magnitude)
                        except Exception:
                             res.append(val.magnitude)
                    else:
                        res.append(val)
                except Exception:
                    res.append(1e6) 
            return res

        sol = root(residuals, x0, method='hybr')
        
        if sol.success:
            all_values = known_values.copy()
            for i, var in enumerate(unknown_vars):
                val = sol.x[i]
                if variable_units.get(var):
                     val = self.unit_registry.Q_(val, variable_units[var])
                all_values[var] = val
            
            results = {}
            for var in sorted(variables):
                val = all_values.get(var, 0.0)
                # Determine unit source: explicit (user-defined), inferred (from patterns/usage), or propagated (calculated)
                if var in variable_units and variable_units[var]:
                    if var in inferred_from_usage:
                        unit_source = 'inferred'
                    else:
                        unit_source = 'explicit'
                else:
                    unit_source = 'propagated'
                
                if hasattr(val, 'units'):
                    results[var] = {
                        "value": val.magnitude,
                        "unit": str(val.units),
                        "unit_source": unit_source
                    }
                else:
                    results[var] = {
                        "value": val,
                        "unit": variable_units.get(var, ""),
                        "unit_source": unit_source
                    }
            
            results, infer_warnings = self._infer_units(results, assignments, variable_units, variables, angle_unit, inferred_from_usage)
            # Merge and deduplicate warnings from forward evaluation with inference warnings
            all_warnings = list(dict.fromkeys(unit_warnings + infer_warnings))  # Preserves order, removes duplicates
            return results, all_warnings if all_warnings else None
        else:
            raise RuntimeError(f"Solver failed to converge: {sol.message}")

    def _validate_units(self, equations: List[str], variables: set, variable_units: Dict[str, str], context: Dict) -> List[str]:
        """
        Validates that equations are dimensionally consistent before solving.
        Returns a list of warning messages instead of raising exceptions.
        """
        warnings = []
        
        # Create a dummy context with 1.0 [unit] for all variables
        dummy_ctx = {"__builtins__": {}}
        dummy_ctx.update(context)
        
        # Track which variables have unknown units - we'll skip validation for equations using them
        unknown_unit_vars = set()
        
        for var in variables:
            if var in variable_units and variable_units[var]:
                try:
                    dummy_ctx[var] = self.unit_registry.Q_(1.0, variable_units[var])
                except Exception:
                    dummy_ctx[var] = 1.0
                    unknown_unit_vars.add(var)
            else:
                # If unit is unknown, mark it and use dimensionless placeholder
                dummy_ctx[var] = 1.0
                unknown_unit_vars.add(var)

        # Mock prop function for validation to avoid physical constraints (e.g. T=1K for Water)
        # but still validate input units and return correct output units.
        def mock_prop_validate(fluid, out, in1, v1, in2, v2):
             from .thermo import ThermoProps
             standard_units = {
                 'T': 'K', 'P': 'Pa', 'D': 'kg/m**3', 'H': 'J/kg',
                 'S': 'J/kg/K', 'U': 'J/kg', 'Q': '',
             }
             def check_input(prop_name, val):
                 prop_upper = prop_name.upper() if isinstance(prop_name, str) else str(prop_name)
                 target_unit = standard_units.get(prop_upper)
                 if hasattr(val, 'units') and target_unit:
                     # This will raise DimensionalityError if incompatible
                     val.to(target_unit)

             check_input(in1, v1)
             check_input(in2, v2)

             # Return dummy output with correct units
             out_upper = out.upper() if isinstance(out, str) else str(out)
             unit_str = self.coolprop_units.get(out_upper, '')
             if unit_str:
                 return self.unit_registry.Q_(1.0, unit_str)
             return 1.0

        dummy_ctx['prop'] = mock_prop_validate

        for eq in equations:
            # Preprocess inline units (e.g. 1 [kg] -> Q_(1, "kg"))
            pre_eq = self.parser._preprocess(eq)
            
            clean_eq = re.sub(r'//.*|#.*', '', pre_eq)
            clean_eq = re.sub(r'\[.*?\]', '', clean_eq).strip()
            if not clean_eq:
                continue
            clean_eq = clean_eq.replace('^', '**')
            
            # Check if this equation involves any unknown-unit variables
            # If so, skip strict unit validation (we can't be sure of the result)
            eq_vars = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', clean_eq))
            if eq_vars & unknown_unit_vars:
                # This equation has variables with unknown units - skip validation
                continue
            
            try:
                if '=' in clean_eq:
                    lhs, rhs = clean_eq.split('=', 1)
                    # Check if LHS and RHS have compatible units
                    val_lhs = eval(lhs, dummy_ctx)
                    val_rhs = eval(rhs, dummy_ctx)
                    
                    if hasattr(val_lhs, 'units') and hasattr(val_rhs, 'units'):
                        if val_lhs.dimensionality != val_rhs.dimensionality:
                            lhs_unit_display = self.unit_registry.format_unit_display(f"{val_lhs.units:~}")
                            rhs_unit_display = self.unit_registry.format_unit_display(f"{val_rhs.units:~}")
                            warnings.append(f"Unit warning in equation '{eq}': Dimension mismatch ({lhs_unit_display} vs {rhs_unit_display})")
                    
                    # If one side is dimensionless (float) and the other has units, we usually can't be sure 
                    # if the float is a true dimensionless number or an invalid/unknown variable (like 'z').
                    # So we skip strict comparison for Float vs Quantity to avoid false positives on inferred variables.
                    # Function argument checks (e.g. sin(m)) still work because they raise errors during eval.
                else:
                    # Expression = 0 type
                    eval(clean_eq, dummy_ctx)
            except pint.DimensionalityError as e:
                # Convert to warning instead of raising exception
                warnings.append(f"Unit warning in equation '{eq}': {e}")
            except ValueError as e:
                # Convert to warning instead of raising exception
                warnings.append(f"Unit warning in equation '{eq}': {e}")
            except Exception:
                # If we can't evaluate (e.g. due to unknown variables or math errors), we skip strict validation
                pass
        
        return warnings

    def _infer_units_from_usage(self, equations: List[str], variables: set, variable_units: Dict[str, str], angle_unit: str) -> Dict[str, str]:
        """
        Infers units for variables based on how they are used in equations.
        - Variables passed to sin/cos/tan are inferred to have angle units
        - Variables used in prop() calls are inferred to have CoolProp standard units
        - Variables with common naming patterns (T_, P_, temp, etc.) get inferred units
        
        Returns a dict of variable -> inferred unit
        Updates variable_units in place for variables without explicit units.
        """
        inferred = {}
        
        # Standard units for CoolProp property inputs
        prop_input_units = {
            'T': 'K',
            'P': 'Pa',
            'D': 'kg/m**3',
            'H': 'J/kg',
            'S': 'J/kg/K',
            'U': 'J/kg',
            'Q': '',  # Quality is dimensionless
        }
        
        # Common variable name patterns and their units
        # These are ONLY checked when no explicit unit is given AND no prop() context
        # We're conservative here - only match unambiguous patterns
        name_patterns = {
            # Temperature patterns - variables that look like temperatures
            'temperature': [
                # Don't match single 'T' - too ambiguous (could be tension, period, etc.)
                (r'^T_(?:evap|cond|hot|cold|high|low|in|out|sat|amb|ref|avg|mean|\d+)$', 'K'),
                (r'^T\d+$', 'K'),                  # T1, T2, T3
                (r'^[Tt]emp', 'K'),                # temp, Temp, temperature  
                (r'^dT$', 'K'),                    # Temperature difference
                (r'^delta_?[Tt]', 'K'),            # delta_T, deltaT
            ],
            # Pressure patterns  
            'pressure': [
                # Don't match P_real (power), P_in could be power input
                (r'^P_(?:evap|cond|hot|cold|high|low|sat|atm|\d+)$', 'Pa'),
                (r'^P\d+$', 'Pa'),                 # P1, P2, P3
                (r'^[Pp]ress', 'Pa'),              # press, pressure
                (r'^dP$', 'Pa'),                   # Pressure drop
                (r'^delta_?[Pp]', 'Pa'),           # delta_P, deltaP
            ],
            # Mass flow patterns (more specific than mass)
            'mass_flow': [
                (r'^m_dot$', 'kg/s'),              # m_dot
                (r'^mdot$', 'kg/s'),               # mdot
                (r'^mass_?flow', 'kg/s'),          # mass_flow, massflow
            ],
            # Length patterns - only unambiguous ones
            'length': [
                (r'^length$', 'm'),                # length
                (r'^[Dd]iam', 'm'),                # diameter
                (r'^L_(?:beam|pipe|tube|channel|\d+)$', 'm'),  # L_beam, L_pipe
                (r'^D_(?:pipe|tube|channel|\d+)$', 'm'),       # D_pipe (diameter context)
            ],
            # Velocity patterns - exclude volume-related names
            'velocity': [
                (r'^vel', 'm/s'),                  # velocity
                (r'^V_(?:in|out|x|y|z|avg|mean|max|min|\d+)$', 'm/s'),  # V_1, V_in (velocity)
            ],
            # Time patterns - only unambiguous ones
            'time': [
                (r'^t_(?:flight|start|end|total|\d+)$', 's'),  # t_1, t_flight
                (r'^time$', 's'),                  # time
            ],
            # Stiffness patterns - only with underscore or subscript
            'stiffness': [
                (r'^k_(?:spring|eq|\d+)$', 'N/m'), # k_1, k_spring
                (r'^stiffness', 'N/m'),            # stiffness
            ],
            # Damping patterns - exclude c_critical which is computed
            'damping': [
                (r'^c_(?:damper|damp|eq|\d+)$', 'N*s/m'),  # c_1, c_damper (not c_critical)
                (r'^damping', 'N*s/m'),            # damping
            ],
            # Enthalpy patterns - only match common thermodynamic names
            'enthalpy': [
                (r'^h_(?:in|out|fg|vap|liq|sat|\d+)$', 'J/kg'),  # h_1, h_fg (not h_height, h_beam)
                (r'^enthalpy', 'J/kg'),            # enthalpy
            ],
            # Entropy patterns  
            'entropy': [
                (r'^s_(?:in|out|fg|vap|liq|sat|\d+)$', 'J/kg/K'),  # s_1, s_2
                (r'^entropy', 'J/kg/K'),           # entropy
            ],
        }
        
        # Trig functions that expect angle input
        trig_functions = ['sin', 'cos', 'tan']
        
        # First pass: infer from variable naming conventions
        for var in variables:
            if var in variable_units and variable_units[var]:
                continue  # Already has explicit unit
            
            # Check against naming patterns
            for category, patterns in name_patterns.items():
                matched = False
                for pattern, unit in patterns:
                    if re.match(pattern, var):
                        # Don't override if the variable is used in a specific context later
                        # Just set a tentative inference
                        if var not in inferred:
                            inferred[var] = unit
                            variable_units[var] = unit
                        matched = True
                        break
                if matched:
                    break
        
        for eq in equations:
            # Clean the equation
            clean_eq = re.sub(r'//.*|#.*', '', eq)
            clean_eq = re.sub(r'\[.*?\]', '', clean_eq).strip()
            if not clean_eq:
                continue
            
            # Find trig function calls with variable arguments
            for trig_fn in trig_functions:
                # Pattern: sin(var) or sin(var + ...) etc - find the first variable
                # Use word boundary \b to prevent matching acos, asin, atan (inverse trig takes dimensionless input)
                pattern = rf'(?<![a-zA-Z]){trig_fn}\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)'
                matches = re.findall(pattern, clean_eq)
                for var in matches:
                    if var in variables and var not in variable_units:
                        # Infer angle unit from context
                        angle_unit_str = 'deg' if angle_unit == 'deg' else 'rad'
                        inferred[var] = angle_unit_str
                        variable_units[var] = angle_unit_str
            
            # Find prop() calls and infer units for input variables
            # Pattern: prop('Fluid', 'OutProp', 'InProp1', val1, 'InProp2', val2)
            prop_pattern = r"prop\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*([^,]+)\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*([^)]+)\s*\)"
            prop_matches = re.findall(prop_pattern, clean_eq)
            
            for match in prop_matches:
                # match = (fluid, out_prop, in1_name, in1_val, in2_name, in2_val)
                fluid, out_prop, in1_name, in1_val, in2_name, in2_val = match
                
                # Check if in1_val is a variable
                in1_val = in1_val.strip()
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', in1_val):
                    if in1_val in variables:
                        in1_unit = prop_input_units.get(in1_name.upper(), '')
                        if in1_unit:
                            # Override any previous inference - prop() context is more specific
                            inferred[in1_val] = in1_unit
                            variable_units[in1_val] = in1_unit
                
                # Check if in2_val is a variable
                in2_val = in2_val.strip()
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', in2_val):
                    if in2_val in variables:
                        in2_unit = prop_input_units.get(in2_name.upper(), '')
                        if in2_unit:
                            # Override any previous inference - prop() context is more specific
                            inferred[in2_val] = in2_unit
                            variable_units[in2_val] = in2_unit
        
        return inferred

    def _infer_units(self, results: Dict, assignments: Dict[str, str], variable_units: Dict[str, str], variables: set, angle_unit: str = 'deg', inferred_from_usage: Dict[str, str] = None) -> tuple:
        """
        Infers units for variables that don't have explicit units specified.
        Uses dimensional analysis on assignment expressions.
        """
        var_list = sorted(list(variables))
        final_units = variable_units.copy()
        
        # Initialize inferred_from_usage to empty dict if not provided
        if inferred_from_usage is None:
            inferred_from_usage = {}
        
        for var, data in results.items():
            if data.get('unit'):
                final_units[var] = data['unit']
        
        var_errors = {}
        unit_warnings = []
        
        def mock_func_dimensionless(*args):
            return 1
            
        def mock_inverse_trig(*args):
            return self.unit_registry.ureg(angle_unit)
        
        def mock_prop_for_units(fluid, out_prop, *args):
            out_prop_upper = out_prop.upper() if isinstance(out_prop, str) else str(out_prop)
            unit_str = self.coolprop_units.get(out_prop_upper, '')
            if unit_str:
                return self.unit_registry.ureg(unit_str)
            return 1
        
        for _ in range(len(assignments) + 1):
            changed = False
            
            unit_ctx = {}
            for v_name in var_list:
                if v_name in final_units and final_units[v_name]:
                    try:
                        unit_ctx[v_name] = self.unit_registry.ureg(final_units[v_name])
                    except Exception:
                        unit_ctx[v_name] = 1
                else:
                    # Variable with no unit / dimensionless - include as 1
                    unit_ctx[v_name] = 1
            
            for var,expr in assignments.items():
                # Check if this variable has a manually specified unit (not inferred)
                # A manually specified unit is one that's in variable_units but NOT in inferred_from_usage
                has_manual_unit = var in variable_units and variable_units[var] and var not in inferred_from_usage
                
                # If it has a manually specified unit, we need to validate it
                # If it doesn't have one, we need to infer it
                if var in final_units and final_units[var] and not has_manual_unit:
                    # Already has inferred unit from actual value, skip
                    continue
                    
                try:
                    unit_eval_ctx = {
                        "__builtins__": {},
                        "sin": mock_func_dimensionless,
                        "cos": mock_func_dimensionless,
                        "tan": mock_func_dimensionless,
                        "exp": mock_func_dimensionless,
                        "log": mock_func_dimensionless,
                        "log10": mock_func_dimensionless,
                        "asin": mock_inverse_trig,
                        "acos": mock_inverse_trig,
                        "atan": mock_inverse_trig,
                        "sqrt": lambda x: x**0.5,
                        "abs": lambda x: x,  # abs preserves units
                        "prop": mock_prop_for_units,
                        "pi": 1,
                        "e": 1,
                        "Q_": lambda val, unit: self.unit_registry.ureg(unit)
                    }
                    unit_eval_ctx.update(unit_ctx)
                    
                    val = eval(expr, unit_eval_ctx)
                    
                    if hasattr(val, 'units'):
                        calculated_unit_str = f"{val.units:~}"
                        
                        # If manual unit was specified, validate it matches calculated unit
                        if has_manual_unit:
                            try:
                                # Create a quantity with the specified unit
                                specified_quantity = self.unit_registry.ureg(variable_units[var])
                                
                                # Check dimensionality match
                                if val.units.dimensionality != specified_quantity.dimensionality:
                                    # Add warning instead of raising error
                                    calc_unit_display = self.unit_registry.format_unit_display(calculated_unit_str)
                                    spec_unit_display = self.unit_registry.format_unit_display(variable_units[var])
                                    unit_warnings.append(
                                        f"Variable '{var}': Calculated units ({calc_unit_display}) "
                                        f"do not match specified units ({spec_unit_display}). "
                                        f"Using calculated units."
                                    )
                                    # Use calculated units instead of specified
                                    final_units[var] = self.unit_registry.format_unit_display(calculated_unit_str)
                                else:
                                    # Use the manually specified unit (user preference)
                                    final_units[var] = self.unit_registry.format_unit_display(variable_units[var])
                            except pint.DimensionalityError:
                                # Add warning instead of raising error
                                calc_unit_display = self.unit_registry.format_unit_display(calculated_unit_str)
                                spec_unit_display = self.unit_registry.format_unit_display(variable_units[var])
                                unit_warnings.append(
                                    f"Variable '{var}': Calculated units ({calc_unit_display}) "
                                    f"cannot be converted to specified units ({spec_unit_display}). "
                                    f"Using calculated units."
                                )
                                # Use calculated units
                                final_units[var] = self.unit_registry.format_unit_display(calculated_unit_str)
                        else:
                            # No manual unit, use the calculated one
                            final_units[var] = self.unit_registry.format_unit_display(calculated_unit_str)
                        
                        changed = True
                    elif isinstance(val, (int, float)):
                        # Expression result is dimensionless
                        if has_manual_unit:
                            # User specified a unit for a dimensionless expression
                            # Apply it - this is EES-style behavior (e.g., exp(1) [m])
                            final_units[var] = self.unit_registry.format_unit_display(variable_units[var])
                        else:
                            # No manual unit for dimensionless result
                            if var not in variable_units:
                                final_units[var] = ""
                        changed = True
                    
                    if var in var_errors:
                        del var_errors[var]
                        
                except Exception as e:
                    var_errors[var] = str(e)
            
            if not changed:
                break
        
        # Add any var_errors to warnings only if the variable wasn't computed successfully
        for var, err in var_errors.items():
            # Skip errors for variables that have a computed value (already handled)
            if var in results and results[var].get('value') is not None:
                continue
            unit_warnings.append(f"Unit error for '{var}': {err}")

        # Format all units through format_unit_display for pretty display
        # This simplifies complex units like N**0.5/kg**0.5/m**0.5 to rad/s
        for var in results:
            raw_unit = final_units.get(var, results[var].get('unit', ''))
            if raw_unit:
                results[var]['unit'] = self.unit_registry.format_unit_display(raw_unit)
            else:
                results[var]['unit'] = ''
        
        return results, unit_warnings

