"""
Direct test of the validation logic
"""
import pint

ureg = pint.UnitRegistry()

# Test: Can we wrap a dimensionless value in meters?
try:
    value = 25  # dimensionless
    specified_unit = 'm'
    
    specified_quantity = ureg.Quantity(1.0, specified_unit)
    print(f"Specified quantity: {specified_quantity}")
    print(f"Is dimensionless: {specified_quantity.dimensionless}")
    print(f"Dimensionality: {specified_quantity.dimensionality}")
    
    if not specified_quantity.dimensionless:
        print("ERROR: Should raise - trying to assign dimensional units to dimensionless value")
    else:
        print("OK: Unit is dimensionless")
        
except Exception as e:
    print(f"Exception: {e}")
