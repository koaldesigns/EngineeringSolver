# Unit Validation Fix - Summary

## Issue Description
When running equations like:
```
L = 10 [m]
A = L^2 [m^2]
```

The system was incorrectly handling unit validation. The expression `L^2` naturally produces units of `m^2` (since L has units of `m`), and the user also specified `[m^2]`. The system was double-counting or not properly validating that these match.

## Root Cause
The solver had two issues:

1. **Forward Evaluation**: When evaluating expressions in the forward pass, the system would calculate the result (e.g., `L^2 = 100 m^2`) but wasn't validating that this matched the manually specified unit `[m^2]`.

2. **Unit Inference**: The `_infer_units` method would skip variables that already had manually specified units, never checking if those units matched the calculated units from the expression.

## Solution Implemented
The fix adds comprehensive unit validation at two stages:

### 1. Forward Evaluation (lines 293-334 in numerical.py)
When evaluating assignments like `A = L^2`:
- If the expression produces units (e.g., `m^2` from `L^2`), check if a manual unit was specified
- If yes, validate that the dimensionalities match
- If they match, convert to the user-specified unit format for display
- If they don't match, raise a `ValueError` with a clear message

Example validation:
```python
# Expression 'L**2' produces units 'm ** 2'
# Manual unit specified: 'm^2'
# Check: m**2 dimensionality == m^2 dimensionality? YES
# Result: Use 'm²' for display (user's preferred format)
```

### 2. Unit Inference (lines 592-672 in numerical.py)
When inferring units for variables:
- Don't skip variables with manual units - validate them instead
- Calculate what the expression would produce
- Compare calculated units with manually specified units
- Raise errors for mismatches

## Test Results

### ✓ Test 1: Matching Units (PASSED)
```
L = 10 [m]
A = L^2 [m^2]
```
Result: `A = 100 m²` (correctly uses user-specified format)

### ✓ Test 3: Dimensionless with Dimensional Unit (PASSED)
```
x = 5
y = x^2 [m]
```
Error: `Unit mismatch for variable 'y': Expression 'x**2' produces a dimensionless result but dimensional unit 'm' was specified.`

### ✓ Test 4: Different Unit Formats, Same Dimensionality (PASSED)
```
L = 10 [m]
A = L^2 [ft^2]
```
Result: `A = 1076.39 ft²` (automatically converts from m² to ft²)

### ✓ Test 6: Units with Exponents (PASSED)
```
r = 5 [m]
V = (4/3) * 3.14159 * r^3 [m^3]
```
Result: `V = 523.60 m³`

### ✓ Test 7: Complex Unit Calculation (PASSED)
```
m = 10 [kg]
v = 5 [m/s]
KE = 0.5 * m * v^2 [J]
```
Result: `KE = 125.0 J` (kg·m²/s² correctly simplified to J)

## Key Behaviors

1. **Calculated units are primary**: The expression `L^2` determines the true units (`m^2`)
2. **Manual units are validated**: The specified `[m^2]` is checked against calculated units
3. **Display preference**: If units match, the user' specified format is used for display
4. **Clear error messages**: If units don't match, a descriptive error is thrown:
   - Different dimensionalities (e.g., `m` vs `m^2`)
   - Dimensionless vs dimensional mismatch
   - Invalid unit specifications

## Error Examples

### Incompatible Units
```
L = 10 [m]
A = L^2 [m]  # ERROR: m^2 ≠ m
```
Error: `Unit mismatch for variable 'A': Expression 'L**2' calculates to units 'm ** 2' but 'm' was specified. These have different dimensionalities.`

### Dimensionless Mismatch
```
x = 5
y = x * 2 [kg]  # ERROR: dimensionless ≠ kg
```
Error: `Unit mismatch for variable 'y': Expression 'x * 2' produces a dimensionless result but dimensional unit 'kg' was specified.`

## Files Modified

1. **backend/solver/numerical.py**
   - Lines 293-334: Forward evaluation unit validation
   - Lines 592-672: Unit inference validation
   - Added comprehensive dimensionality checking
   - Improved error messages

## Backward Compatibility

The changes are backward compatible:
- Existing equations without manual unit specifications work unchanged
- Unit inference still works for variables without specified units
- Only adds validation - doesn't change core solving logic
