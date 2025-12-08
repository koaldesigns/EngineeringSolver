# Test script for unit formatting
import sys
sys.stdout.reconfigure(encoding='utf-8')

from solver.units import UnitRegistry

u = UnitRegistry()

tests = [
    'm ** 2',
    'm ** 3 / s',
    'kg / m ** 3',
    'kg * m ** 2 / s ** 2',   # Should simplify to J
    'kg * m ** 2 / s ** 3',   # Should simplify to W
    'kg * m / s ** 2',        # Should simplify to N
    'W',
    'J/s',                    # Should simplify to W
    'Pa',
    'm/s',
    'W/m/K',                  # Thermal conductivity
    'J/kg/K',                 # Specific heat
    'm^2',                    # Caret notation
]

print("Unit Formatting Test:")
print("=" * 50)
for t in tests:
    try:
        result = u.format_unit_display(t)
        print(f"  {t:25} -> {result}")
    except Exception as e:
        print(f"  {t:25} -> ERROR: {e}")
