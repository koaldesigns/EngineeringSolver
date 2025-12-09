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
            'gauss': 'gauss_si', # Force SI-compatible gauss
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
            "gauss_si = 1e-4 * tesla", # Define SI-compatible gauss to avoid CGS dimension issues
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

    def get_compatible_units(self, unit_str: str) -> list:
        """
        Returns a list of compatible units for the given unit, based on dimensional analysis.
        Uses Pint to determine the dimensionality and returns common engineering units.
        
        Args:
            unit_str: The source unit string
            
        Returns:
            List of compatible unit strings (may be empty if unit is unknown)
        """
        if not unit_str:
            return []
        
        # Comprehensive mapping of dimensions to common units
        # Keys are frozensets of (dimension_name, exponent) tuples
        DIMENSION_TO_UNITS = {
            # Length [L]
            frozenset([('[length]', 1)]): ['m', 'cm', 'mm', 'km', 'ft', 'in', 'yd', 'mi'],
            # Area [L^2]
            frozenset([('[length]', 2)]): ['m^2', 'cm^2', 'ft^2', 'in^2', 'km^2'],
            # Volume [L^3]
            frozenset([('[length]', 3)]): ['m^3', 'L', 'mL', 'cm^3', 'ft^3', 'gal', 'in^3'],
            # Mass [M]
            frozenset([('[mass]', 1)]): ['kg', 'g', 'mg', 'lb', 'lbm', 'oz', 'ton'],
            # Time [T]
            frozenset([('[time]', 1)]): ['s', 'ms', 'min', 'h', 'hr', 'day'],
            # Temperature [Θ]
            frozenset([('[temperature]', 1)]): ['K', 'degC', 'degF', 'degR'],
            # Current [I]
            frozenset([('[current]', 1)]): ['A', 'mA', 'μA', 'kA'],
            # Amount [N]  
            frozenset([('[substance]', 1)]): ['mol', 'kmol', 'mmol'],
            
            # Velocity [L/T]
            frozenset([('[length]', 1), ('[time]', -1)]): ['m/s', 'km/h', 'ft/s', 'mph', 'in/s', 'cm/s', 'mi/h'],
            # Acceleration [L/T^2]
            frozenset([('[length]', 1), ('[time]', -2)]): ['m/s^2', 'ft/s^2', 'in/s^2', 'cm/s^2', 'g0'],
            # Force [M*L/T^2]
            frozenset([('[mass]', 1), ('[length]', 1), ('[time]', -2)]): ['N', 'kN', 'MN', 'lbf', 'dyn', 'kgf'],
            # Pressure [M/(L*T^2)]
            frozenset([('[mass]', 1), ('[length]', -1), ('[time]', -2)]): ['Pa', 'kPa', 'MPa', 'bar', 'psi', 'atm', 'mmHg', 'inHg', 'torr'],
            # Energy / Work / Torque [M*L^2/T^2]
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -2)]): [
                'J', 'kJ', 'MJ', 'cal', 'kcal', 'Wh', 'kWh', 'BTU', 'eV', 'ft*lbf',  # Energy
                'N*m', 'kN*m', 'in*lbf', 'kgf*m'                                     # Torque (merged to avoid overwrite)
            ],
            # Power [M*L^2/T^3]
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -3)]): ['W', 'kW', 'MW', 'hp', 'BTU/h', 'BTU/s', 'ft*lbf/s'],
            # Frequency [1/T]
            frozenset([('[time]', -1)]): ['Hz', 'kHz', 'MHz', 'GHz', 'rad/s', '1/s', 'rpm'],
            
            # Density [M/L^3]
            frozenset([('[mass]', 1), ('[length]', -3)]): ['kg/m^3', 'g/cm^3', 'g/mL', 'lbm/ft^3', 'lb/ft^3', 'kg/L'],
            # Mass flow rate [M/T]
            frozenset([('[mass]', 1), ('[time]', -1)]): ['kg/s', 'kg/h', 'kg/min', 'g/s', 'lbm/s', 'lb/s', 'lbm/h', 'g/min'],
            # Volume flow rate [L^3/T]
            frozenset([('[length]', 3), ('[time]', -1)]): ['m^3/s', 'm^3/h', 'L/s', 'L/min', 'L/h', 'ft^3/s', 'ft^3/min', 'gal/min', 'gal/h'],
            
            # Specific energy [L^2/T^2] (J/kg = m^2/s^2)
            frozenset([('[length]', 2), ('[time]', -2)]): ['J/kg', 'kJ/kg', 'MJ/kg', 'BTU/lb', 'BTU/lbm', 'Wh/kg', 'm^2/s^2'],
            # Specific heat capacity [L^2/(T^2*Θ)] (J/(kg*K))
            frozenset([('[length]', 2), ('[temperature]', -1), ('[time]', -2)]): ['J/(kg*K)', 'kJ/(kg*K)', 'BTU/(lb*R)', 'BTU/(lbm*R)', 'cal/(g*K)', 'J/(g*K)'],
            # Thermal conductivity [M*L/(T^3*Θ)] (W/(m*K))
            frozenset([('[mass]', 1), ('[length]', 1), ('[time]', -3), ('[temperature]', -1)]): ['W/(m*K)', 'W/(cm*K)', 'BTU/(h*ft*R)', 'BTU/(hr*ft*R)', 'W/(m*degC)'],
            
            # Dynamic viscosity [M/(L*T)] (Pa*s)
            frozenset([('[mass]', 1), ('[length]', -1), ('[time]', -1)]): ['Pa*s', 'mPa*s', 'cP', 'P', 'lb/(ft*s)', 'kg/(m*s)', 'N*s/m^2'],
            # Kinematic viscosity [L^2/T]
            frozenset([('[length]', 2), ('[time]', -1)]): ['m^2/s', 'cm^2/s', 'ft^2/s', 'cSt', 'St'],
            
            # Momentum [M*L/T] (kg*m/s)
            frozenset([('[mass]', 1), ('[length]', 1), ('[time]', -1)]): ['kg*m/s', 'N*s', 'lbm*ft/s', 'lb*ft/s', 'g*cm/s'],
            # Moment/Torque [M*L^2/T^2] (N*m) - same as energy but different usage
            # Merged with Energy above to avoid map overwrites for same dimension key
            
            # Heat flux [M/T^3] (W/m^2)
            frozenset([('[mass]', 1), ('[time]', -3)]): ['W/m^2', 'kW/m^2', 'BTU/(h*ft^2)', 'W/cm^2'],
            # Entropy [M*L^2/(T^2*Θ)] (J/K)
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -2), ('[temperature]', -1)]): ['J/K', 'kJ/K', 'BTU/R', 'cal/K'],
            
            # Voltage [M*L^2/(T^3*I)]
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -3), ('[current]', -1)]): ['V', 'mV', 'kV', 'MV'],
            # Resistance [M*L^2/(T^3*I^2)]
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -3), ('[current]', -2)]): ['ohm', 'kohm', 'Mohm', 'mOhm'],
            # Capacitance [T^4*I^2/(M*L^2)]
            # Use 'farad' directly because 'F' maps to Fahrenheit in this system
            frozenset([('[time]', 4), ('[current]', 2), ('[mass]', -1), ('[length]', -2)]): ['farad', 'mF', 'μF', 'nF', 'pF'],
            # Inductance [M*L^2/(T^2*I^2)]
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -2), ('[current]', -2)]): ['H', 'mH', 'μH', 'nH'],
            
            # ===== Additional Engineering Dimensions =====
            
            # Specific volume [L^3/M] (m³/kg) - inverse of density
            frozenset([('[length]', 3), ('[mass]', -1)]): ['m^3/kg', 'L/kg', 'cm^3/g', 'ft^3/lb', 'ft^3/lbm'],
            
            # Second moment of area [L^4] (m⁴) - area moment of inertia
            frozenset([('[length]', 4)]): ['m^4', 'cm^4', 'mm^4', 'in^4', 'ft^4'],
            
            # Stiffness / Spring constant / Surface tension [M/T^2] (N/m = kg/s²)
            # Combined with Energy per area in later section (same dimension)
            
            # Heat transfer coefficient [M/(T^3*Θ)] (W/(m²*K))
            frozenset([('[mass]', 1), ('[time]', -3), ('[temperature]', -1)]): ['W/(m^2*K)', 'W/(m^2*degC)', 'BTU/(h*ft^2*R)', 'BTU/(hr*ft^2*R)'],
            
            # Thermal resistance [T^3*Θ/M] (K/W)
            frozenset([('[time]', 3), ('[temperature]', 1), ('[mass]', -1)]): ['K/W', 'degC/W', 'R*h/BTU'],
            
            # Angular acceleration [1/T^2] (rad/s²)
            frozenset([('[time]', -2)]): ['rad/s^2', 'deg/s^2', '1/s^2', 'rpm/s'],
            
            # Linear charge density [I*T/L] (C/m)
            # Use 'coulomb' because 'C' maps to Celsius
            frozenset([('[current]', 1), ('[time]', 1), ('[length]', -1)]): ['coulomb/m', 'coulomb/cm'],
            
            # Electric field [M*L/(T^3*I)] (V/m)
            frozenset([('[mass]', 1), ('[length]', 1), ('[time]', -3), ('[current]', -1)]): ['V/m', 'kV/m', 'V/cm', 'V/mm'],
            
            # Magnetic flux [M*L^2/(T^2*I)] (Wb)
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -2), ('[current]', -1)]): ['Wb', 'mWb', 'μWb'],
            
            # Magnetic flux density [M/(T^2*I)] (T)
            # Use 'gauss' instead of 'G' to avoid confusion with Giga prefix (though mapped via alias)
            frozenset([('[mass]', 1), ('[time]', -2), ('[current]', -1)]): ['T', 'mT', 'μT', 'gauss'],
            
            # Molar mass [M/N] (kg/mol)
            frozenset([('[mass]', 1), ('[substance]', -1)]): ['kg/mol', 'g/mol', 'lb/mol'],
            
            # Molar volume [L^3/N] (m³/mol)
            frozenset([('[length]', 3), ('[substance]', -1)]): ['m^3/mol', 'L/mol', 'cm^3/mol'],
            
            # Concentration [N/L^3] (mol/m³)
            frozenset([('[substance]', 1), ('[length]', -3)]): ['mol/m^3', 'mol/L', 'mmol/L', 'mol/cm^3'],
            
            # Thermal power/temperature [M*L^2/(T^3*Θ)] (W/K)
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -3), ('[temperature]', -1)]): ['W/K', 'kW/K', 'BTU/(h*R)'],
            
            # ===== Comprehensive Additional Engineering Dimensions =====
            
            # --- Mechanical / Structural ---
            
            # Section modulus [L^3] (m³) - used in beam bending calculations
            # Already covered by Volume [L^3]
            
            # Curvature [1/L] (1/m)
            frozenset([('[length]', -1)]): ['1/m', '1/cm', '1/mm', '1/ft', '1/in'],
            
            # Angular momentum [M*L^2/T] (kg·m²/s)
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -1)]): ['kg*m^2/s', 'N*m*s', 'J*s'],
            
            # Moment of inertia (rotational) [M*L^2] (kg·m²)
            frozenset([('[mass]', 1), ('[length]', 2)]): ['kg*m^2', 'kg*cm^2', 'lb*ft^2', 'lb*in^2', 'g*cm^2'],
            
            # Strain energy density [M/(L*T^2)] (J/m³ = Pa)
            # Already covered by Pressure
            
            # Stress intensity factor [M/(L^0.5*T^2)] - Not cleanly representable with integer exponents
            # Skipping - fractional exponents not supported
            
            # --- Fluid Mechanics ---
            
            # Volumetric flow per area [L/T] (m/s) - superficial velocity
            # Already covered by Velocity
            
            # Permeability [L^2] (m² or darcy)
            # Already covered by Area
            
            # Hydraulic conductivity [L/T] 
            # Already covered by Velocity
            
            # --- Heat Transfer ---
            
            # Thermal diffusivity [L^2/T] (m²/s)
            # Already covered by Kinematic viscosity
            
            # Volumetric heat capacity [M/(L*T^2*Θ)] (J/(m³·K))
            frozenset([('[mass]', 1), ('[length]', -1), ('[time]', -2), ('[temperature]', -1)]): ['J/(m^3*K)', 'kJ/(m^3*K)', 'BTU/(ft^3*R)'],
            
            # --- Electrical / Electronics ---
            
            # Conductance [T^3*I^2/(M*L^2)] (S = 1/Ω)
            frozenset([('[time]', 3), ('[current]', 2), ('[mass]', -1), ('[length]', -2)]): ['S', 'mS', 'μS', 'kS'],
            
            # Conductivity [T^3*I^2/(M*L^3)] (S/m)
            frozenset([('[time]', 3), ('[current]', 2), ('[mass]', -1), ('[length]', -3)]): ['S/m', 'mS/cm', 'μS/cm'],
            
            # Resistivity [M*L^3/(T^3*I^2)] (Ω·m)
            frozenset([('[mass]', 1), ('[length]', 3), ('[time]', -3), ('[current]', -2)]): ['ohm*m', 'ohm*cm', 'ohm*mm'],
            
            # Electric charge [I*T] (C = A·s)
            # Use 'coulomb' directly because 'C' maps to Celsius in this system
            frozenset([('[current]', 1), ('[time]', 1)]): ['coulomb', 'mC', 'μC', 'nC', 'pC', 'A*h', 'mA*h'],
            
            # Capacitance per length [T^4*I^2/(M*L^3)] (F/m)
            frozenset([('[time]', 4), ('[current]', 2), ('[mass]', -1), ('[length]', -3)]): ['F/m', 'pF/m', 'nF/m'],
            
            # Inductance per length [M*L/(T^2*I^2)] (H/m)
            frozenset([('[mass]', 1), ('[length]', 1), ('[time]', -2), ('[current]', -2)]): ['H/m', 'mH/m', 'μH/m'],
            
            # Current density [I/L^2] (A/m²)
            frozenset([('[current]', 1), ('[length]', -2)]): ['A/m^2', 'A/cm^2', 'A/mm^2', 'mA/cm^2'],
            
            # Electric potential gradient [M*L/(T^3*I)] (V/m)
            # Already covered by Electric field
            
            # Magnetic field strength [I/L] (A/m)
            frozenset([('[current]', 1), ('[length]', -1)]): ['A/m', 'A/cm', 'kA/m', 'Oe'],
            
            # Permittivity [T^4*I^2/(M*L^3)] (F/m)
            # Same as Capacitance per length
            
            # Permeability [M*L/(T^2*I^2)] (H/m)
            # Same as Inductance per length
            
            # --- Radiation / Optics ---
            
            # Luminous intensity [candela] - base unit, handle separately
            frozenset([('[luminosity]', 1)]): ['cd', 'mcd', 'kcd'],
            
            # Luminous flux [cd*sr] (lumen)
            # Pint may not track solid angle - skip for now
            
            # Illuminance [cd*sr/L^2] (lux = lm/m²)
            # Pint may not track solid angle - skip for now
            
            # Radioactivity [1/T] (Bq = 1/s)
            # Already covered by Frequency
            
            # Absorbed dose [L^2/T^2] (Gy = J/kg = m²/s²)
            # Already covered by Specific energy
            
            # --- Acoustics ---
            
            # Acoustic impedance [M/(L^2*T)] (Pa·s/m = kg/(m²·s))
            frozenset([('[mass]', 1), ('[length]', -2), ('[time]', -1)]): ['Pa*s/m', 'kg/(m^2*s)', 'rayl'],
            
            # --- Chemistry / Chemical Engineering ---
            
            # Molar flow rate [N/T] (mol/s)
            frozenset([('[substance]', 1), ('[time]', -1)]): ['mol/s', 'mol/min', 'mol/h', 'kmol/h', 'kmol/s'],
            
            # Molar flux [N/(L^2*T)] (mol/(m²·s))
            frozenset([('[substance]', 1), ('[length]', -2), ('[time]', -1)]): ['mol/(m^2*s)', 'mol/(cm^2*s)', 'kmol/(m^2*s)'],
            
            # Reaction rate [N/(L^3*T)] (mol/(m³·s))
            frozenset([('[substance]', 1), ('[length]', -3), ('[time]', -1)]): ['mol/(m^3*s)', 'mol/(L*s)', 'mol/(L*min)'],
            
            # Catalytic activity [N/T] (katal = mol/s)
            # Same as Molar flow rate
            
            # Molar energy [M*L^2/(T^2*N)] (J/mol)
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -2), ('[substance]', -1)]): ['J/mol', 'kJ/mol', 'cal/mol', 'kcal/mol', 'eV/mol'],
            
            # Molar entropy/heat capacity [M*L^2/(T^2*N*Θ)] (J/(mol·K))
            frozenset([('[mass]', 1), ('[length]', 2), ('[time]', -2), ('[substance]', -1), ('[temperature]', -1)]): ['J/(mol*K)', 'kJ/(mol*K)', 'cal/(mol*K)'],
            
            # --- Additional Mechanical ---
            
            # Compliance [T^2/M] (m/N = 1/(N/m))
            frozenset([('[time]', 2), ('[mass]', -1)]): ['m/N', 'mm/N', 'in/lbf'],
            
            # Mass per length [M/L] (kg/m) - linear density
            frozenset([('[mass]', 1), ('[length]', -1)]): ['kg/m', 'g/m', 'g/cm', 'lb/ft', 'lb/in'],
            
            # Mass per area [M/L^2] (kg/m²) - areal density
            frozenset([('[mass]', 1), ('[length]', -2)]): ['kg/m^2', 'g/cm^2', 'lb/ft^2', 'oz/yd^2', 'g/m^2'],
            
            # Force per length / Surface tension / Energy per area [M/T^2] (N/m = J/m²)
            # Note: N/m and J/m² have the same dimension but different physical meanings
            frozenset([('[mass]', 1), ('[time]', -2)]): ['N/m', 'kN/m', 'lbf/in', 'lbf/ft', 'N/mm', 'J/m^2', 'mJ/m^2'],
            
            # Pressure gradient [M/(L^2*T^2)] (Pa/m)
            frozenset([('[mass]', 1), ('[length]', -2), ('[time]', -2)]): ['Pa/m', 'kPa/m', 'psi/ft', 'bar/m'],
            
            # Power per length [M*L/T^3] (W/m)
            frozenset([('[mass]', 1), ('[length]', 1), ('[time]', -3)]): ['W/m', 'kW/m', 'BTU/(h*ft)'],
            
            # Power per volume [M/(L*T^3)] (W/m³)
            frozenset([('[mass]', 1), ('[length]', -1), ('[time]', -3)]): ['W/m^3', 'kW/m^3', 'BTU/(h*ft^3)'],
            
            # --- Miscellaneous ---
            
            # Jerk [L/T^3] (m/s³)
            frozenset([('[length]', 1), ('[time]', -3)]): ['m/s^3', 'ft/s^3', 'in/s^3'],
            
            # Fuel efficiency [1/L^2] (1/m² or L/100km as special case)
            frozenset([('[length]', -2)]): ['1/m^2', 'L/(100*km)', 'gal/mi'],  # Note: L/100km not directly compatible
            
            # Specific fuel consumption [T/L^2] (kg/(N·s) for jets, simplified)
            # Complex - skip
            
            # Angle (dimensionless but tracked)
            frozenset(): ['rad', 'deg', 'mrad', 'arcmin', 'arcsec'],
        }
        
        try:
            # Normalize and parse the unit
            normalized = self.normalize_unit(unit_str)
            q = self.Q_(1, normalized)
            
            # Get the dimensionality as a dict
            dim = q.dimensionality
            
            # Convert to frozenset for lookup
            dim_key = frozenset((str(k), int(v)) for k, v in dim.items())
            
            # Look up in our mapping
            if dim_key in DIMENSION_TO_UNITS:
                suggestions = DIMENSION_TO_UNITS[dim_key]
                # Filter out the input unit itself (in various forms)
                input_normalized = normalized.lower().replace(' ', '').replace('*', '').replace('·', '')
                return [u for u in suggestions 
                        if u.lower().replace(' ', '').replace('*', '').replace('·', '') != input_normalized]
            
            # If not found in our dict, return empty (unknown dimension combination)
            return []
            
        except Exception as e:
            # Unit parsing failed
            return []

