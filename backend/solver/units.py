import pint
import re

class UnitRegistry:
    """
    Wrapper around Pint's UnitRegistry to handle unit conversions and consistency checks.
    
    NOTE FOR DEVELOPERS/AGENTS:
    When adding new unit aliases or modifying unit handling:
    1. Update FEATURE_REFERENCE.md in project root (Units System section)
    2. Update frontend/src/Documentation.jsx (UnitsSection component)
    3. Add the unit alias to the unit_map dict below if needed
    """
    def __init__(self):
        self.ureg = pint.UnitRegistry()
        self.ureg.default_format = '~'
        self._raw_Q = self.ureg.Quantity
        self._define_safe_aliases()
        
        # EES to Pint mapping
        self.unit_map = {
            'C': 'degC',
            'F': 'degF',
            'R': 'degR',
            'K': 'kelvin',
            'mu': 'micro', # Prefix handling might be tricky, but if used as unit, map it.
            'psia': 'psi',
            'psig': 'psi',
            'lbm': 'pound',
            'lbf': 'force_pound',
            'Btu': 'Btu', # Case sensitivity check
            'btu': 'Btu',
            'BTU': 'Btu',
            'gal': 'gallon',
            'liter': 'liter',
            'L': 'liter',
            'l': 'liter',
        }
    
    def Q_(self, value, unit_str):
        """
        Create a Quantity with normalized units.
        Ensures EES aliases like 'C' -> 'degC' are applied.
        """
        # Only normalize if unit_str is a string, not already a Unit object
        if isinstance(unit_str, str):
            normalized = self.normalize_unit(unit_str) if unit_str else unit_str
            return self._raw_Q(value, normalized)
        else:
            # Already a Unit object or None
            return self._raw_Q(value, unit_str)

    def _define_safe_aliases(self):
        """
        Defines safe aliases that don't conflict with base units or offsets.
        """
        definitions = [
            "lbm = pound",
            "lbf = force_pound",
            # "psia = psi", # psi is already defined, psia/psig are context dependent. We map them.
        ]
        for definition in definitions:
            try:
                self.ureg.define(definition)
            except Exception:
                pass

    def normalize_unit(self, unit_str: str) -> str:
        """
        Normalizes EES unit strings to Pint-compatible strings.
        """
        if not unit_str:
            return ""
        
        # Simple lookup for whole units
        if unit_str in self.unit_map:
            return self.unit_map[unit_str]
            
        # Handle compound units? e.g. "kJ/kg-C"
        # This is complex. For now, we rely on Pint's parser, 
        # but we might need to replace tokens.
        # A simple token replacement might work.
        
        normalized = unit_str
        # Sort keys by length to replace longest first (e.g. psia before psi if we had both)
        for key in sorted(self.unit_map.keys(), key=len, reverse=True):
            # Use regex to replace whole words only to avoid replacing 'C' in 'mC' (milliCoulomb)
            # But 'C' in EES is Celsius. 'mC' is likely milliCelsius? No.
            # EES is case insensitive usually.
            # We'll assume the user uses the mapped keys as tokens.
            
            # Regex: \b matches word boundary.
            # We escape the key just in case.
            pattern = r'\b' + re.escape(key) + r'\b'
            normalized = re.sub(pattern, self.unit_map[key], normalized)
            
        return normalized

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Converts a value from one unit to another.
        """
        from_unit = self.normalize_unit(from_unit)
        to_unit = self.normalize_unit(to_unit)
        
        try:
            quantity = self.Q_(value, from_unit)
            converted = quantity.to(to_unit)
            return converted.magnitude
        except pint.UndefinedUnitError as e:
            raise ValueError(f"Undefined unit: {e}")
        except pint.DimensionalityError as e:
            raise ValueError(f"Incompatible units: {e}")

    def check_consistency(self, eq_str: str) -> bool:
        """
        Checks if an equation is dimensionally consistent.
        (This is a placeholder for more complex logic where we'd parse units from the equation)
        """
        # TODO: Implement full equation unit analysis
        return True

    def get_base_units(self, unit_str: str) -> str:
        """
        Returns the base units for a given unit string.
        """
        try:
            q = self.Q_(1, unit_str)
            return str(q.to_base_units().units)
        except Exception:
            return "unknown"

    def format_unit_display(self, unit_str: str) -> str:
        """
        Formats a unit string for pretty display:
        1. Simplifies to preferred derived units (W, J, Pa, N, etc.)
        2. Uses Unicode superscripts for exponents (via Pint's pretty format)
        3. Removes spaces from compound units
        4. Fixes multi-slash ambiguity (J/K/kg → J/(kg·K))
        5. Simplifies frequency-like units to rad/s
        6. Simplifies complex compound units to base forms
        """
        if not unit_str:
            return ""
        
        try:
            # Create a quantity from the input
            q = self.Q_(1, unit_str)
            
            # Check if dimensionless
            # Check if dimensionless, but exclude angles (deg, rad) which are dimensionless in Pint but should be displayed
            unit_str_repr = str(q.units)
            is_angle = any(u in unit_str_repr for u in ['radian', 'degree', 'deg', 'rad', 'arcmin', 'arcsec'])
            
            if (q.dimensionless or q.to_base_units().dimensionless) and not is_angle:
                return ""
            
            # First, try to simplify to base units and then to derived units
            base_q = q.to_base_units()
            base_dimensionality = base_q.dimensionality
            
            # Check for special cases that need custom simplification
            
            # Case 1: Angular frequency / frequency (1/s or rad/s)
            # sqrt(k/m) = sqrt(N/m/kg) = sqrt(kg*m/s^2/m/kg) = sqrt(1/s^2) = 1/s = rad/s
            # Dimensionality for 1/s is {time: -1}
            if base_dimensionality == {'[time]': -1}:
                # This is a frequency-like unit (1/s)
                # For angular frequency (from sqrt(k/m)), display as rad/s
                formatted = "rad/s"
                return formatted
            
            # Case 2: Velocity (m/s)
            # sqrt(J/kg) = sqrt(kg*m^2/s^2/kg) = sqrt(m^2/s^2) = m/s
            # Dimensionality for m/s is {length: 1, time: -1}
            if base_dimensionality == {'[length]': 1, '[time]': -1}:
                # Convert magnitude to check if it's 1
                try:
                    vel_converted = q.to('m/s')
                    if abs(vel_converted.magnitude - 1.0) < 1e-6:
                        return "m/s"
                except Exception:
                    pass
            
            # Case 3: Length (m)
            # N/m/Pa = N*m^2/(m*N) = m
            # Dimensionality for m is {length: 1}
            if base_dimensionality == {'[length]': 1}:
                try:
                    len_converted = q.to('m')
                    if abs(len_converted.magnitude - 1.0) < 1e-6:
                        return "m"
                except Exception:
                    pass

            # Common derived units to try simplifying to (in priority order)
            derived_units = [
                ('watt', self.ureg.watt),          # W = J/s
                ('joule', self.ureg.joule),        # J = N·m
                ('newton', self.ureg.newton),      # N = kg·m/s²
                ('pascal', self.ureg.pascal),      # Pa = N/m²
                ('volt', self.ureg.volt),          # V = W/A
                ('ohm', self.ureg.ohm),            # Ω = V/A
                ('hertz', self.ureg.hertz),        # Hz = 1/s
                ('coulomb', self.ureg.coulomb),    # C = A·s
                ('farad', self.ureg.farad),        # F = C/V
                ('weber', self.ureg.weber),        # Wb = V·s
                ('tesla', self.ureg.tesla),        # T = Wb/m²
                ('henry', self.ureg.henry),        # H = Wb/A
            ]
            
            # Try to simplify to a common derived unit
            simplified_q = q
            simplified = False
            for name, derived_unit in derived_units:
                try:
                    # Check if dimensions are compatible
                    converted = q.to(derived_unit)
                    # If conversion succeeds with magnitude 1.0, use this simpler form
                    if abs(converted.magnitude - 1.0) < 1e-10:
                        simplified_q = converted
                        simplified = True
                        break
                except Exception:
                    continue
            
            # If not simplified to a standard derived unit, try compound simplifications
            if not simplified:
                # Try combinations like J/(kg·K) for specific heat
                compound_targets = [
                    ('m/s', self.ureg('m/s')),           # velocity
                    ('m**2', self.ureg('m**2')),         # area
                    ('m**3', self.ureg('m**3')),         # volume
                    ('kg/s', self.ureg('kg/s')),         # mass flow rate
                    ('W/m**2', self.ureg('W/m**2')),     # heat flux
                    ('W/(m*K)', self.ureg('W/(m*K)')),   # thermal conductivity
                    ('J/(kg*K)', self.ureg('J/(kg*K)')), # specific heat
                    ('Pa*s', self.ureg('Pa*s')),         # dynamic viscosity
                    ('m**2/s', self.ureg('m**2/s')),     # kinematic viscosity
                    ('rad/s', self.ureg('rad/s')),       # angular velocity
                ]
                for name, target in compound_targets:
                    try:
                        converted = q.to(target)
                        if abs(converted.magnitude - 1.0) < 1e-10:
                            simplified_q = converted
                            simplified = True
                            break
                    except Exception:
                        continue
            
            # Use Pint's pretty format which includes superscripts
            # ~P = compact (abbreviated) + pretty (superscripts/unicode)
            formatted = f"{simplified_q.units:~P}"
            
        except Exception:
            # If parsing fails, just clean up the string manually
            formatted = unit_str
        
        # Remove any remaining spaces (around / and ·)
        formatted = formatted.replace(' / ', '/')
        formatted = formatted.replace(' · ', '·')
        formatted = formatted.replace(' * ', '·')
        formatted = formatted.replace(' ', '')
        
        # Fix ambiguous multi-slash notation: J/K/kg -> J/(kg·K)
        # This happens when Pint outputs e.g. "J/K/kg" which is confusing
        if formatted.count('/') > 1:
            formatted = self._fix_multi_slash_notation(formatted)
        
        return formatted
    
    def _fix_multi_slash_notation(self, unit_str: str) -> str:
        """
        Converts ambiguous multi-slash notation to grouped denominator format.
        e.g., J/K/kg -> J/(kg·K)
             W/K/m  -> W/(m·K)
        """
        if '/' not in unit_str or unit_str.count('/') <= 1:
            return unit_str
        
        # Split by first slash to get numerator and denominator parts
        parts = unit_str.split('/')
        if len(parts) < 2:
            return unit_str
        
        numerator = parts[0]
        # All remaining parts are in the denominator
        denominator_parts = parts[1:]
        
        # Join denominator parts with · (multiplication)
        denominator = '·'.join(denominator_parts)
        
        # Format as numerator/(denominator)
        return f"{numerator}/({denominator})"

