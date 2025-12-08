# Unit Testing Rules and Importance

## Importance of Unit Correctness
Unit analysis is a critical tool for validating mathematical models. In engineering and physics, every physical quantity has dimensions. Ensuring that equations are dimensionally consistent helps:
1.  **Detect Errors**: A dimensional mismatch often indicates a wrong formula or a missing variable.
2.  **Ensure Reliability**: Correct unit propagation guarantees that the results are meaningful and safe to use in real-world applications.
3.  **Facilitate Communication**: Explicit units make the code and equations self-documenting and easier for others to understand.

## Rules for Creating Unit Tests

When creating unit tests for the parser and solver, follow these rules to ensure robust unit handling:

### 1. Test Basic Arithmetic
*   **Addition/Subtraction**: Ensure that adding/subtracting quantities with the same units works (e.g., `1[m] + 2[m] = 3[m]`).
*   **Incompatible Addition**: Ensure that adding incompatible units raises an error (e.g., `1[m] + 1[s]` should fail).
*   **Multiplication/Division**: Verify that units combine correctly (e.g., `1[m] * 2[s] = 2[m*s]`, `4[m] / 2[s] = 2[m/s]`).

### 2. Test Transcendental Functions
*   **Trigonometry**: Functions like `sin`, `cos`, `tan` should accept:
    *   Angles (degrees or radians).
    *   Dimensionless values (treated as radians or degrees based on settings).
    *   They should **reject** dimensions like length or time (e.g., `sin(5[m])` is invalid).
*   **Exponentials/Logarithms**: `exp`, `log`, `log10` generally expect dimensionless arguments. Verify that passing dimensions raises an error or that the solver handles it if the argument is dimensionless (e.g. `log(10[m]/2[m])` is valid).

### 3. Test Property Calls
*   **Thermo Props**: Verify that `prop()` calls return values with the correct units (e.g., Enthalpy in `J/kg`).
*   **Inputs**: Ensure `prop()` accepts inputs with units and converts them correctly (e.g., `T=300[K]` vs `T=26.85[C]`).

### 4. Test Unit Conversion
*   **Explicit Conversion**: Test the `convert()` function (e.g., `convert(1, 'm', 'ft')`).
*   **Automatic Consistency**: Ensure that `x [m] = 5 [ft]` results in `x` being stored as meters (or feet, depending on implementation choice, but magnitude must be correct).

### 5. Test Equation Sets
*   **Coupled Equations**: Test systems where units propagate through multiple variables.
*   **Implicit Equations**: Ensure the solver can handle units in implicit equations (e.g., `x^2 = 4[m^2]`).

### 6. Test Edge Cases
*   **Dimensionless Variables**: Ensure variables without units interact correctly with variables with units.
*   **Zero Values**: Ensure `0[unit]` behaves correctly.

## Example Test Case Structure

```python
def test_unit_mismatch():
    solver = NumericalSolver()
    equations = [
        "x = 1 [m]",
        "y = 1 [s]",
        "z = x + y" # Should fail
    ]
    try:
        solver.solve(equations)
        assert False, "Should have raised dimensionality error"
    except ValueError as e:
        assert "Dimension mismatch" in str(e)
```
