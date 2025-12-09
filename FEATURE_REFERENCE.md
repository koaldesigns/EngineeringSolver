# Engineering Equation Solver - Complete Feature Reference

> **Last Updated:** December 2024
> 
> **NOTE FOR DEVELOPERS/AGENTS:** When adding new features to the solver, update this document AND the frontend Documentation component (`frontend/src/Documentation.jsx`).

---

## Table of Contents

1. [Basic Syntax](#basic-syntax)
2. [Mathematical Operators](#mathematical-operators)
3. [Mathematical Functions](#mathematical-functions)
4. [Trigonometric Functions](#trigonometric-functions)
5. [Units System](#units-system)
6. [Unit Conversion](#unit-conversion)
7. [Thermodynamic Properties](#thermodynamic-properties)
8. [Advanced Features](#advanced-features)
9. [Array Inputs & Sweeps](#array-inputs--sweeps)
10. [Plotting](#plotting)
11. [Unit Validation & Warnings](#unit-validation--warnings)
12. [Reserved Words](#reserved-words)

---

## Basic Syntax

### Equations
- One equation per line
- Use `=` for equality constraints
- Comments: `//` or `#`

```
x = 5           // Assignment
y = x^2         // Expression
x^2 + y^2 = 25  // Implicit equation
```

### Variables
- Must start with letter or underscore
- Can contain letters, numbers, underscores
- Case-sensitive (`T` ≠ `t`)

```
Valid:   x, velocity, T_1, _internal, speed2
Invalid: 2nd_var, my-var, sin (reserved)
```

### Numbers
- Integer: `42`, `-100`
- Decimal: `3.14159`, `0.001`
- Scientific: `2.5e-10`, `1.38E-23`, `200e9`

---

## Mathematical Operators

| Operator | Description | Example | Unit Behavior |
|----------|-------------|---------|---------------|
| `+` | Addition | `a + b` | Requires compatible units |
| `-` | Subtraction | `a - b` | Requires compatible units |
| `*` | Multiplication | `a * b` | Units multiply |
| `/` | Division | `a / b` | Units divide |
| `^` | Exponentiation | `a^2` | Units raised to power |
| `**` | Exponentiation (alt) | `a**2` | Units raised to power |

### Operator Precedence (highest to lowest)
1. Parentheses `()`
2. Exponentiation `^`, `**`
3. Unary minus `-x`
4. Multiplication/Division `*`, `/`
5. Addition/Subtraction `+`, `-`

---

## Mathematical Functions

### Basic Functions

| Function | Description | Unit Handling |
|----------|-------------|---------------|
| `sqrt(x)` | Square root | Returns √(unit) |
| `abs(x)` | Absolute value | Preserves units |
| `min(x, y)` | Minimum | Requires same units |
| `max(x, y)` | Maximum | Requires same units |
| `pow(x, n)` | Power | Returns unit^n |

### Exponential & Logarithmic

| Function | Description | Unit Handling |
|----------|-------------|---------------|
| `exp(x)` | e^x | Requires dimensionless, returns dimensionless |
| `log(x)` | Natural log (ln) | Requires dimensionless, returns dimensionless |
| `log10(x)` | Base-10 log | Requires dimensionless, returns dimensionless |

### Hyperbolic Functions

| Function | Description |
|----------|-------------|
| `sinh(x)` | Hyperbolic sine |
| `cosh(x)` | Hyperbolic cosine |
| `tanh(x)` | Hyperbolic tangent |

### Mathematical Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `pi` | 3.14159265... | Circle ratio |
| `e` | 2.71828182... | Euler's number |

---

## Trigonometric Functions

### Mode Setting
The solver supports both **Degrees** (default) and **Radians** modes.

### Standard Trig Functions

| Function | Input | Output |
|----------|-------|--------|
| `sin(x)` | Angle (based on mode) | Dimensionless [-1, 1] |
| `cos(x)` | Angle (based on mode) | Dimensionless [-1, 1] |
| `tan(x)` | Angle (based on mode) | Dimensionless |

### Inverse Trig Functions

| Function | Input | Output |
|----------|-------|--------|
| `asin(x)` | Dimensionless [-1, 1] | Angle with unit (deg/rad) |
| `acos(x)` | Dimensionless [-1, 1] | Angle with unit (deg/rad) |
| `atan(x)` | Dimensionless | Angle with unit (deg/rad) |

### Unit Handling
- With angle units: `sin(30 [deg])` - auto-converted
- Without units: `sin(45)` - uses mode setting
- Dimensional input: `sin(5 [m])` - **ERROR**

---

## Units System

### Specifying Units
```
length = 10 [m]           // Value with unit
Area [m^2] = length^2     // LHS unit declaration
velocity = distance / time // Unit propagation
```

### Supported Unit Categories
The system supports over 50 dimensional categories powered by Pint. Selected common units:

#### Base & Common
`m`, `ft`, `in` (Length), `kg`, `lbm` (Mass), `s`, `min`, `hr` (Time), `K`, `degC`, `degF` (Temp)

#### Mechanical
`N`, `lbf` (Force), `Pa`, `psi`, `bar` (Pressure), `J`, `BTU`, `cal` (Energy), `W`, `hp` (Power), `N*m` (Torque)

#### Thermal & Fluid
`J/(kg*K)` (Specific Heat), `W/(m*K)` (Conductivity), `Pa*s` (Viscosity), `kg/s` (Flow Rate)

#### Electrical & Magnetic
`A`, `V`, `ohm` (Basic), `coulomb` (Charge), `farad` (Capacitance), `tesla`, `gauss` (B-Field)

> **Compound Units**: You can use any valid combination, e.g., `[J/(kg*K)]` or `[m/s^2]`.

### EES Compatibility Aliases & Rules

To ensure ambiguity is resolved between EES conventions and standard SI units:

| Symbol | Interpreted As | Use Full Name For |
|--------|----------------|-------------------|
| `C` | `degC` (Celsius) | `[coulomb]` (Charge) |
| `F` | `degF` (Fahrenheit) | `[farad]` (Capacitance) |
| `R` | `degR` (Rankine) | - |
| `G` | Gravitational Constant | `[gauss]` (Magnetic Flux) |
| `gauss`| `1e-4 tesla` (SI) | - |
| `psia`, `psig` | `psi` | - |
| `lbm` | `pound` (mass) | - |
| `lbf` | `force_pound` | - |
| `L` | `liter` | - |

> **Note**: `gauss` is automatically converted to an SI-compatible definition (1 G = 10⁻⁴ T) to ensure consistency.

---

## Unit Conversion

### convert() Function
```
convert(value, 'from_unit', 'to_unit')
```

### Examples
```
T_F = convert(100, 'C', 'F')      // 212
P_psi = convert(1, 'atm', 'psi')  // 14.696
L_ft = convert(10, 'm', 'ft')     // 32.808
```

---

## Thermodynamic Properties

### prop() Function (CoolProp)
```
prop('FluidName', 'OutputProperty', 'Input1', Value1, 'Input2', Value2)
```

### Common Fluids
`Water`, `Air`, `Nitrogen`, `Oxygen`, `CO2`, `Ammonia`, `R134a`, `R410A`, `R22`, `R32`, `Propane`, `Methane`, `Hydrogen`, `Helium`

### Property Codes

| Code | Property | Units |
|------|----------|-------|
| `T` | Temperature | K |
| `P` | Pressure | Pa |
| `D`, `DMASS` | Mass density | kg/m³ |
| `V` | Specific volume | m³/kg |
| `H`, `HMASS` | Specific enthalpy | J/kg |
| `U`, `UMASS` | Specific internal energy | J/kg |
| `S`, `SMASS` | Specific entropy | J/(kg·K) |
| `C`, `CP`, `CPMASS` | Specific heat (const P) | J/(kg·K) |
| `CV`, `CVMASS` | Specific heat (const V) | J/(kg·K) |
| `Q` | Quality (vapor fraction) | dimensionless |
| `A`, `SPEED_OF_SOUND` | Speed of sound | m/s |
| `VISCOSITY`, `MU` | Dynamic viscosity | Pa·s |
| `CONDUCTIVITY`, `K`, `L` | Thermal conductivity | W/(m·K) |
| `M`, `MOLAR_MASS` | Molar mass | kg/mol |

### Examples
```
// Air density
rho = prop('Air', 'D', 'T', 300, 'P', 101325)

// Water saturation
h_fg = prop('Water', 'H', 'P', 101325, 'Q', 1) - prop('Water', 'H', 'P', 101325, 'Q', 0)

// R134a cycle
P_evap = prop('R134a', 'P', 'T', 253.15, 'Q', 1)
```

---

## Advanced Features

### Summation
```
sum(function, start, end)
```

### Integration
```
integral(function, lower, upper)
```
Uses scipy.integrate.quad for numerical integration.

### Differentiation
```
derivative(function, point)
diff(function, point)
```
Uses central difference method (default dx = 1e-6).

### Name-Based Unit Inference
The solver automatically infers units from common variable naming patterns:

| Pattern | Inferred Unit |
|---------|---------------|
| `T_evap`, `T1`, `temp` | K |
| `P_cond`, `P1`, `pressure` | Pa |
| `m_dot`, `mdot` | kg/s |
| `velocity`, `V_in` | m/s |
| `h_fg`, `enthalpy` | J/kg |
| `s_1`, `entropy` | J/(kg·K) |

---

## Array Inputs & Sweeps

Array inputs allow you to sweep a variable across multiple values and see how results change.

### Defining Arrays

```
t = linspace(0, 10, 50)     // 50 points from 0 to 10
t = arange(0, 10, 0.5)      // From 0 to 10 step 0.5
t = [1, 2, 3, 4, 5]         // Explicit array
```

### Arrays with Units

```
t = linspace(0, 10, 50) [s]     // Time sweep in seconds
P = arange(100, 500, 50) [kPa]  // Pressure sweep
```

### Array Combination Modes

When multiple arrays are defined:

- **Parallel** (default): Arrays iterated together
  - `t = [1, 2, 3]`, `P = [100, 200, 300]` → 3 cases
  
- **Grid**: Cartesian product of all arrays
  - `t = [1, 2]`, `P = [100, 200]` → 4 cases

Use directives to specify mode:
```
@parallel
t = linspace(0, 10, 5)

@grid
x = [1, 2, 3]
y = [10, 20]
```

### Array Propagation

When a variable is an array, all downstream calculations become arrays:

```
t = linspace(0, 10, 5) [s]
v = 5 [m/s]
x = v * t        // x becomes [0, 5, 10, 15, 20] m
```

---

## Plotting

Generate plots from array results using the `plot()` or `scatter()` functions.

### Basic Plot Syntax

```
plot(x_variable, y_variable)
plot(x_variable, [y1, y2, y3])    // Multiple Y variables
scatter(x_variable, y_variable)   // Scatter plot
```

### Example - Kinematic Plot

```
t = linspace(0, 5, 50) [s]
v0 = 10 [m/s]
a = -9.81 [m/s^2]
v = v0 + a * t
y = v0 * t + 0.5 * a * t^2
plot(t, [y, v])
```

### Plot Types

| Function | Type |
|----------|------|
| `plot(x, y)` | Line plot |
| `scatter(x, y)` | Scatter plot |
| `plot(x, y, type='scatter')` | Explicit scatter |

### Axis Labels

Axis labels automatically include variable names and units:
- X-axis: `time [s]`
- Y-axis: `velocity [m/s]`

---

## Unit Validation & Warnings

The solver performs dimensional analysis and generates **warnings** (not errors) for:

1. **Addition/Subtraction mismatch**: `5[m] + 3[s]`
2. **Specified vs Calculated mismatch**: `A = L^2 [m]` when A is actually m²
3. **Dimensionless mismatch**: `y = x * 2 [kg]` when x is dimensionless

### Behavior
- Calculations **continue** despite warnings
- Calculated units are **primary**
- Compatible units are **auto-converted**
- Warnings are returned in the API response

---

## Reserved Words

These cannot be used as variable names:

```
// Math functions
sin, cos, tan, asin, acos, atan
exp, log, log10, sqrt, abs
min, max, pow, sinh, cosh, tanh
sum, integral, derivative, diff

// Unit/thermo functions
convert, prop, pi, e, Q_

// Array/plot functions
linspace, arange, plot, scatter
```

---

## API Reference

### Solve Endpoint
```
POST /api/solve
```

#### Request Body
```json
{
  "equations": ["x = 5", "y = x^2"],
  "guesses": {"x": 1.0},
  "angle_unit": "deg",
  "output_units": {"y": "m^2"},
  "array_mode": "parallel"
}
```

**Parameters:**
- `equations`: Array of equation strings
- `guesses`: Optional initial values for implicit solving
- `angle_unit`: `"deg"` or `"rad"` for trig functions
- `output_units`: Optional unit conversions for results
- `array_mode`: `"parallel"` or `"grid"` for array sweeps

#### Response (Scalar)
```json
{
  "results": {
    "x": {"value": 5.0, "unit": ""},
    "y": {"value": 25.0, "unit": ""}
  },
  "status": "converged",
  "unit_warnings": null,
  "is_array_solve": false,
  "plots": null
}
```

#### Response (Array)
```json
{
  "results": {
    "t": {"value": [0, 1, 2, 3, 4], "unit": "s", "is_array": true},
    "x": {"value": [0, 2, 4, 6, 8], "unit": "m", "is_array": true}
  },
  "status": "converged",
  "unit_warnings": null,
  "is_array_solve": true,
  "plots": [{"data": [...], "layout": {...}}]
}
```

---

## File Structure

```
backend/
├── solver/
│   ├── numerical.py    # Main solver logic + array solving
│   ├── parser.py       # Equation parser + array/plot parsing
│   ├── plotting.py     # Plotly chart generation
│   ├── units.py        # Unit handling (Pint wrapper)
│   └── thermo.py       # CoolProp wrapper
├── api/
│   └── routes.py       # API endpoints
└── main.py             # FastAPI app

frontend/src/
├── PlotPanel.jsx       # Plotly chart rendering
├── Documentation.jsx   # This reference (UI version)
├── EditorComponents.jsx # Shared editor components
└── ...
```

---

*This document is the authoritative reference for all solver features. Keep it updated!*
