# Equation Nomenclature and Syntax Guide

This document outlines the syntax and conventions for writing equations in the Engineering Equation Solver.

## 1. General Syntax
- **Equations**: Enter one equation per line. The order of equations does not matter.
- **Variables**: Variable names must start with a letter and can contain numbers and underscores (e.g., `T_1`, `Vel_in`, `x2`).
- **Comments**: Use `//` or `#` for comments. Text after these characters is ignored.
  ```
  x = 5 // This is a comment
  ```
- **Case Sensitivity**: Variable names are currently **case-sensitive** (e.g., `t` and `T` are different).

## 2. Units
You can define units for variables using square brackets `[]` immediately after the value or variable definition.
- **Input**: `L = 10 [m]`
- **Output**: The solver tracks units for display.
- **EES Compatibility**: The solver supports common EES unit aliases:
  - Temperature: `C`, `degC`, `Celsius` (all treated as Celsius), `F`, `degF`, `Fahrenheit`, `K`, `Kelvin`, `R`, `degR`, `Rankine`.
  - Pressure: `psi`, `psia`, `psig` (all treated as psi), `bar`, `atm`, `kPa`, `MPa`.
  - Energy: `Btu`, `kJ`, `J`.
  - Mass/Force: `lbm` (pound mass), `lbf` (pound force), `kg`, `N`.
  - Volume: `L`, `liter`, `gal` (gallon).
  - Prefix: `mu` can be used for micro (e.g. `mu m` for micrometer is NOT supported directly as a space-separated unit, but `mum` might be if Pint supports it. Best to use standard Pint units or `micro` prefix). *Correction*: Use `micro` prefix or standard abbreviations. `mu` is mapped to `micro` if used as a standalone unit string, but `mum` should be written as `micrometer` or `um`.

## 3. Unit Conversion
You can perform unit conversions within your equations using the `convert` function.
- **Syntax**: `convert(value, 'from_unit', 'to_unit')`
- **Example**: 
  ```
  T_F = convert(100, 'C', 'F') // Converts 100 Celsius to Fahrenheit
  P_psi = convert(1, 'atm', 'psi')
  ```

## 4. Mathematical Functions
Standard mathematical functions are available:
- **Basic**: `abs(x)`, `min(x, y)`, `max(x, y)`, `sqrt(x)`
- **Exponential/Log**: `exp(x)`, `ln(x)` (natural log), `log10(x)`
- **Trigonometry**: `sin(x)`, `cos(x)`, `tan(x)`, `asin(x)`, `acos(x)`, `atan(x)`
  - **Note**: Trigonometric functions automatically handle **Degrees** or **Radians** based on your solver settings. Default is typically Degrees for engineering.

## 5. Advanced Engineering Functions
- **Summation**: `sum(expression_func, start, end)`
  - *Note*: The syntax requires a function or lambda if using the internal solver directly, but for the text parser, `sum` support is currently limited to the python `sum` or requires specific syntax implementation.
  - *Correction*: The current solver exposes a `sum` function that expects `(func, start, end)`. Defining a function inline in the equation text (e.g. `i -> i^2`) is not yet supported by the simple parser. 
  - **Recommendation**: For summations, it is currently recommended to calculate them separately or wait for future syntax updates.
- **Integration**: `integral(func, lower, upper)` (Similar limitation as sum).

## 6. Thermodynamic Properties
Use the `prop` function to call property data (via CoolProp).
- Syntax: `prop('FluidName', 'OutputProp', 'Input1', Value1, 'Input2', Value2)`
- Example: `h = prop('Water', 'H', 'T', 300, 'P', 101325)`

## 7. Example Problem
```
// Inputs
P = 100 [kPa]
T = 25 [C] // EES style unit

// Geometric parameters
L = 2.5 [m]
D = 0.1 [m]
Area = pi * (D/2)^2

// Unit Conversion Example
T_F = convert(T, 'C', 'F')

// Fluid Property (using Kelvin for safety, though prop handles units if configured)
// Note: The prop function currently expects SI units (K, Pa) unless configured otherwise.
rho = prop('Air', 'D', 'T', T + 273.15, 'P', P * 1000)

// Calculation
Mass = rho * Area * L
```
