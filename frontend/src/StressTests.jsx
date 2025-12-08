import React, { useState } from 'react';
import { solveEquations } from './api';
import './Instructions.css';
import {
    MiniEquationEditor
} from './EditorComponents';

// StressTests component uses the shared MiniEquationEditor

const StressTests = () => {
    const sections = [
        // Complex Math Operators
        {
            title: "Nested Exponentiation",
            category: "Math Operators",
            description: "Test power operations with various exponent patterns.",
            equations: `x = 2
y = x^3
z = (x^2)^2
w = x^(1/2)
// Expected: y=8, z=16, w≈1.414`
        },
        {
            title: "Complex Arithmetic",
            category: "Math Operators",
            description: "Test arithmetic with nested parentheses.",
            equations: `a = 10
b = 3
c = (a + b) * (a - b)
d = a / b + b / a
e = ((a + b) / 2)^2 - (a * b)
// Expected: c=91, d≈3.63, e=12.25`
        },
        {
            title: "Trigonometric Functions",
            category: "Math Operators",
            description: "Test trig functions in degree mode.",
            equations: `angle = 45 [deg]
s = sin(angle)
c = cos(angle)
t = tan(angle)
check = s^2 + c^2
// Expected: s≈0.707, c≈0.707, t=1, check=1`
        },
        {
            title: "Logarithms & Exponentials",
            category: "Math Operators",
            description: "Test log, exp, and related functions.",
            equations: `a = exp(1)
b = log(a)
c = log10(100)
d = exp(log(5))
// Expected: a≈2.718, b=1, c=2, d=5`
        },
        // Unit Propagation
        {
            title: "Area & Volume Units",
            category: "Unit Propagation",
            description: "Test unit propagation through multiplication.",
            equations: `length = 10 [m]
width = 5 [m]
height = 2 [m]
area = length * width
volume = area * height
perimeter = 2 * (length + width)
// Expected: area→m², volume→m³, perimeter→m`
        },
        {
            title: "Velocity & Acceleration",
            category: "Unit Propagation",
            description: "Test division of units.",
            equations: `distance = 100 [m]
time = 10 [s]
velocity = distance / time
acceleration = velocity / time
// Expected: velocity→m/s, acceleration→m/s²`
        },
        {
            title: "Force & Energy",
            category: "Unit Propagation",
            description: "Test compound unit formation (Newton, Joule).",
            equations: `mass = 10 [kg]
accel = 9.81 [m/s^2]
force = mass * accel
distance = 5 [m]
work = force * distance
// Expected: force→kg·m/s², work→kg·m²/s²`
        },
        {
            title: "Power & Energy",
            category: "Unit Propagation",
            description: "Test electrical unit propagation.",
            equations: `voltage = 220 [V]
current = 10 [A]
power = voltage * current
time = 3600 [s]
energy = power * time
// Expected: power→V·A, energy→V·A·s`
        },
        // Thermodynamic Properties
        {
            title: "Air Density (CoolProp)",
            category: "Thermo Properties",
            description: "Test property retrieval with unit propagation.",
            equations: `T = 300 [K]
P = 101325 [Pa]
rho = prop('Air', 'D', 'T', 300, 'P', 101325)
// Expected: rho≈1.177 [kg/m³]`
        },
        {
            title: "Mass Flow Rate",
            category: "Thermo Properties",
            description: "Combine prop() with geometry calculations.",
            equations: `D = 0.1 [m]
V = 2 [m/s]
rho = prop('Air', 'D', 'T', 300, 'P', 101325)
A = 3.14159 * (D/2)^2
mdot = rho * A * V
// Expected: mdot→kg/s`
        },
        {
            title: "Water Properties",
            category: "Thermo Properties",
            description: "Test multiple property calls for water.",
            equations: `T = 373.15
P = 101325
rho = prop('Water', 'D', 'T', T, 'P', P)
h = prop('Water', 'H', 'T', T, 'P', P)
s = prop('Water', 'S', 'T', T, 'P', P)
// Boiling point: rho≈958 kg/m³`
        },
        // Nonlinear Systems
        {
            title: "Circle-Line Intersection",
            category: "Nonlinear Systems",
            description: "Solve a quadratic system: circle and line.",
            equations: `x^2 + y^2 = 25
y = x + 1
// Solutions: (3,4) or (-4,-3)`
        },
        {
            title: "Exponential System",
            category: "Nonlinear Systems",
            description: "Solve system with exp and log.",
            equations: `exp(x) + y = 10
x + log(y) = 2
// Find x and y satisfying both`
        },
        {
            title: "Trigonometric System",
            category: "Nonlinear Systems",
            description: "Solve system with sin and cos.",
            equations: `sin(x) + cos(y) = 1.5
cos(x) + sin(y) = 1.0
// Angles in degrees`
        },
        // Engineering Calculations
        {
            title: "Projectile Motion",
            category: "Engineering",
            description: "Calculate projectile trajectory parameters.",
            equations: `v0 = 50 [m/s]
angle = 45
g = 9.81 [m/s^2]
vx = v0 * cos(angle)
vy = v0 * sin(angle)
t_flight = 2 * vy / g
h_max = vy^2 / (2 * g)
range_val = vx * t_flight`
        },
        {
            title: "Heat Transfer",
            category: "Engineering",
            description: "Calculate heat transfer for a given mass.",
            equations: `mass = 10 [kg]
cp = 4180 [J/kg/K]
dT = 20 [K]
Q = mass * cp * dT
// Expected: Q=836000 J`
        },
        {
            title: "Reynolds Number",
            category: "Engineering",
            description: "Calculate dimensionless Reynolds number.",
            equations: `D = 0.1 [m]
rho = 1000 [kg/m^3]
mu = 0.001 [Pa*s]
V = 2 [m/s]
Re = rho * V * D / mu
// Expected: Re=200000 (dimensionless)`
        },
        {
            title: "Fourier's Law",
            category: "Engineering",
            description: "Calculate heat conduction through a wall.",
            equations: `k = 0.5 [W/m/K]
A = 2 [m^2]
dT = 30 [K]
dx = 0.1 [m]
Q = k * A * dT / dx
// Expected: Q=300 W`
        },
        // Edge Cases
        {
            title: "Small Numbers",
            category: "Edge Cases",
            description: "Test handling of small values.",
            equations: `a = 0.001
b = a^2
c = sqrt(a)
// Expected: b=1e-6, c≈0.0316`
        },
        {
            title: "Large Numbers",
            category: "Edge Cases",
            description: "Test handling of large values.",
            equations: `a = 1000
b = a^2
c = sqrt(a)
// Expected: b=1e6, c≈31.6`
        },
        {
            title: "Mathematical Constants",
            category: "Edge Cases",
            description: "Test pi and e constants.",
            equations: `p = pi
euler = e
check = cos(0) + sin(90)
// Expected: p≈3.14159, euler≈2.718, check=2`
        },
        {
            title: "Nested Expressions",
            category: "Edge Cases",
            description: "Test deeply nested parentheses.",
            equations: `x = 2
y = ((x + 1) * 2 - 3) / 2
z = sqrt(x^2 + 3*x + 1)
// Expected: y=1.5, z≈3.32`
        },
        // Mixed Unit Expressions
        {
            title: "Efficiency (Dimensionless)",
            category: "Mixed Units",
            description: "Test unit cancellation for ratios.",
            equations: `P_in = 1000 [W]
P_out = 850 [W]
efficiency = P_out / P_in
// Expected: efficiency=0.85 (dimensionless)`
        },
        {
            title: "Pressure Drop",
            category: "Mixed Units",
            description: "Combine dimensionless coefficient with units.",
            equations: `rho = 1000 [kg/m^3]
V = 5 [m/s]
K = 2.5
dP = K * rho * V^2 / 2
// Expected: dP=31250 Pa`
        },
        // Extreme Calculus (Unit Aware)
        {
            title: "Integral with Units",
            category: "Extreme Calculus",
            description: "Integration of velocity to get distance.",
            equations: `// Distance = integral of velocity
dist = integral(lambda t: 5 [m/s], 0 [s], 10 [s])
// Expected: 50 m`
        },
        {
            title: "Derivative with Units",
            category: "Extreme Calculus",
            description: "Differentiation of position to get velocity.",
            equations: `// Velocity = derivative of position
// x(t) = 0.5 * a * t^2
a = 9.8 [m/s^2]
v_at_2 = derivative(lambda t: 0.5 * a * t^2, 2 [s])
// Expected: 19.6 m/s`
        },
        {
            title: "Summation with Units",
            category: "Extreme Calculus",
            description: "Summation of quantities with units.",
            equations: `// Total mass
total = sum(lambda i: i * 10 [kg], 1, 5)
// Expected: 150 kg`
        },
        {
            title: "Complex Impulse",
            category: "Extreme Calculus",
            description: "Integral of Force (mass * accel) over time.",
            equations: `mass = 10 [kg]
// Impulse = integral of Force dt
// Force = mass * jerk * t
impulse = integral(lambda t: mass * 2 [m/s^3] * t, 0 [s], 5 [s])
// Expected: 250 kg m/s`
        },
        // Refrigeration Cycle Tests (R134a)
        {
            title: "R134a Basic Properties",
            category: "Refrigeration Cycle",
            description: "Test R134a properties at evaporator and condenser conditions.",
            equations: `T_evap = 253.15  // -20°C in K
T_cond = 313.15  // 40°C in K
P_evap = prop('R134a', 'P', 'T', T_evap, 'Q', 1)
P_cond = prop('R134a', 'P', 'T', T_cond, 'Q', 0)
// Expected: P_evap≈132kPa, P_cond≈1016kPa`
        },
        {
            title: "R134a Enthalpy States",
            category: "Refrigeration Cycle",
            description: "Calculate R134a enthalpy at key cycle states.",
            equations: `T_evap = 263.15  // -10°C
T_cond = 318.15  // 45°C
h1 = prop('R134a', 'H', 'T', T_evap, 'Q', 1)
h3 = prop('R134a', 'H', 'T', T_cond, 'Q', 0)
s1 = prop('R134a', 'S', 'T', T_evap, 'Q', 1)
q_evap = h1 - h3
// h1≈395kJ/kg, h3≈260kJ/kg`
        },
        {
            title: "Refrigeration COP (Carnot)",
            category: "Refrigeration Cycle",
            description: "Calculate Carnot COP for refrigeration cycle.",
            equations: `T_L = 253.15  // -20°C cold reservoir
T_H = 313.15  // 40°C hot reservoir
COP_carnot = T_L / (T_H - T_L)
// Expected: COP≈4.22`
        },
        {
            title: "R134a Full Cycle Analysis",
            category: "Refrigeration Cycle",
            description: "Complete vapor-compression cycle with R134a.",
            equations: `// Evaporator and condenser temperatures
T_e = 268.15  // -5°C evaporator
T_c = 308.15  // 35°C condenser

// State 1: Evaporator outlet (saturated vapor)
h1 = prop('R134a', 'H', 'T', T_e, 'Q', 1)
s1 = prop('R134a', 'S', 'T', T_e, 'Q', 1)
P_low = prop('R134a', 'P', 'T', T_e, 'Q', 1)

// State 3: Condenser outlet (saturated liquid)
h3 = prop('R134a', 'H', 'T', T_c, 'Q', 0)
P_high = prop('R134a', 'P', 'T', T_c, 'Q', 0)

// State 4: After expansion valve (h4 = h3)
h4 = h3

// Cooling effect and mass flow for 1 kW capacity
Q_evap = h1 - h4
Q_capacity = 1000 [W]  // 1 kW cooling
m_dot = Q_capacity / Q_evap`
        },
        // Rankine Cycle Tests
        {
            title: "Rankine Boiler Conditions",
            category: "Rankine Cycle",
            description: "Steam properties at boiler/turbine inlet.",
            equations: `P_high = 8000000  // 8 MPa boiler pressure
T_superheat = 773.15  // 500°C superheat
h3 = prop('Water', 'H', 'T', T_superheat, 'P', P_high)
s3 = prop('Water', 'S', 'T', T_superheat, 'P', P_high)
// h3≈3400 kJ/kg for superheated steam`
        },
        {
            title: "Rankine Condenser",
            category: "Rankine Cycle",
            description: "Water properties at condenser (low pressure).",
            equations: `P_low = 10000  // 10 kPa condenser
h1 = prop('Water', 'H', 'P', P_low, 'Q', 0)
v1 = prop('Water', 'V', 'P', P_low, 'Q', 0)
h2_sat = prop('Water', 'H', 'P', P_low, 'Q', 1)
h_fg = h2_sat - h1
// h1≈192kJ/kg, v1≈0.001m³/kg`
        },
        {
            title: "Rankine Pump Work",
            category: "Rankine Cycle",
            description: "Calculate ideal pump work in Rankine cycle.",
            equations: `P_low = 10000 [Pa]
P_high = 8000000 [Pa]
v1 = 0.00101 [m^3/kg]
W_pump = v1 * (P_high - P_low)
// Expected: W_pump≈8 kJ/kg`
        },
        {
            title: "Rankine Thermal Efficiency",
            category: "Rankine Cycle",
            description: "Compare actual vs Carnot efficiency.",
            equations: `T_H = 773.15  // 500°C (K)
T_L = 318.97  // Sat temp at 10kPa
eta_carnot = 1 - T_L / T_H
// Carnot efficiency≈58.7%`
        },
        // Modal Analysis Tests
        {
            title: "Single Mass-Spring",
            category: "Modal Analysis",
            description: "Natural frequency of single DOF system.",
            equations: `m = 10 [kg]
k = 1000 [N/m]
omega_n = sqrt(k / m)
f_n = omega_n / (2 * pi)
// omega_n=10 rad/s, f_n≈1.59 Hz`
        },
        {
            title: "2-DOF Symmetric System",
            category: "Modal Analysis",
            description: "Natural frequencies of symmetric 2-mass system.",
            equations: `// For symmetric system: m1=m2=m, k1=k2=k3=k
m = 1 [kg]
k = 100 [N/m]
omega1_sq = k / m
omega1 = sqrt(omega1_sq)
omega2_sq = 3 * k / m
omega2 = sqrt(omega2_sq)
// omega1=10, omega2≈17.32 rad/s`
        },
        {
            title: "Reduced Mass Analysis",
            category: "Modal Analysis",
            description: "Effect of mass ratio on system dynamics.",
            equations: `m1 = 1 [kg]
m2 = 2 [kg]
k = 500 [N/m]
mu = m2 / m1
equiv_mass = (m1 * m2) / (m1 + m2)
omega_reduced = sqrt(k / equiv_mass)
// mu=2, equiv≈0.667kg, omega≈27.4`
        },
        {
            title: "Damped Oscillation",
            category: "Modal Analysis",
            description: "Damping ratio and damped natural frequency.",
            equations: `m = 5 [kg]
c = 20 [N*s/m]
k = 500 [N/m]
omega_n = sqrt(k / m)
c_critical = 2 * m * omega_n
zeta = c / c_critical
omega_d = omega_n * sqrt(1 - zeta^2)
// zeta=0.2, omega_d≈9.8 rad/s`
        },
        // Advanced Thermodynamics
        {
            title: "Nitrogen at Cryogenic",
            category: "Advanced Thermo",
            description: "Nitrogen properties at cryogenic conditions.",
            equations: `T = 100  // 100 K (cryogenic)
P = 500000  // 5 bar
rho = prop('Nitrogen', 'D', 'T', T, 'P', P)
cp = prop('Nitrogen', 'C', 'T', T, 'P', P)
// High density at low temp`
        },
        {
            title: "Supercritical CO2",
            category: "Advanced Thermo",
            description: "CO2 properties near/above critical point.",
            equations: `T_crit = 304.13  // CO2 critical temp
P = 10000000  // 10 MPa (supercritical)
T = 320  // Above critical
rho = prop('CO2', 'D', 'T', T, 'P', P)
// Supercritical density ~200-800 kg/m³`
        },
        {
            title: "Ammonia Refrigerant",
            category: "Advanced Thermo",
            description: "Ammonia as industrial refrigerant.",
            equations: `T_evap = 248.15  // -25°C
h_vapor = prop('Ammonia', 'H', 'T', T_evap, 'Q', 1)
h_liquid = prop('Ammonia', 'H', 'T', T_evap, 'Q', 0)
h_fg = h_vapor - h_liquid
// Ammonia latent heat ~1200 kJ/kg`
        },
        // Complex Coupled Equations
        {
            title: "Heat Exchanger NTU",
            category: "Coupled Equations",
            description: "NTU-effectiveness calculation.",
            equations: `m_dot_h = 0.5 [kg/s]
m_dot_c = 0.8 [kg/s]
cp_h = 4180 [J/kg/K]
cp_c = 1005 [J/kg/K]
C_h = m_dot_h * cp_h
C_c = m_dot_c * cp_c
C_r = C_c / C_h
U = 50 [W/m^2/K]
A = 10 [m^2]
NTU = U * A / C_c
// NTU≈0.62`
        },
        {
            title: "Pipe Pressure Drop",
            category: "Coupled Equations",
            description: "Darcy-Weisbach pressure drop calculation.",
            equations: `D = 0.05 [m]
L = 100 [m]
rho = 1000 [kg/m^3]
mu = 0.001 [Pa*s]
V = 2 [m/s]
Re = rho * V * D / mu
f = 64 / Re
dP = f * (L / D) * rho * V^2 / 2
// Re=100000, f=0.00064`
        },
        {
            title: "Mach Number Calc",
            category: "Coupled Equations",
            description: "Compressible flow speed calculation.",
            equations: `V = 340 [m/s]
T = 288.15 [K]
gamma = 1.4
R = 287 [J/kg/K]
a = sqrt(gamma * R * T)
M = V / a
// M≈1.0 (sonic), a≈340 m/s`
        },
        // Multi-Physics Problems
        {
            title: "Thermoelectric Cooling",
            category: "Multi-Physics",
            description: "Peltier device cooling calculations.",
            equations: `I = 3 [A]
R = 2 [ohm]
alpha = 0.05 [V/K]
T_h = 320 [K]
T_c = 280 [K]
Q_joule = I^2 * R
Q_peltier = alpha * I * T_c
COP = Q_peltier / Q_joule
// Q_joule=18W, Q_peltier=42W`
        },
        {
            title: "Cantilever Deflection",
            category: "Multi-Physics",
            description: "Beam maximum deflection under point load.",
            equations: `// Beam deflection with proper units
P = 1000 [N]  // Point load
L_beam = 2 [m]  // Length
E_mod = 200e9 [Pa]  // Young's modulus
b_width = 0.05 [m]  // Width
h_beam = 0.1 [m]  // Height
I_moment = b_width * h_beam^3 / 12
delta_max = P * L_beam^3 / (3 * E_mod * I_moment)
// I≈4.17e-6 m⁴, delta≈3.2mm`
        },
        {
            title: "AC Power Factor",
            category: "Multi-Physics",
            description: "Electrical power factor and phase angle.",
            equations: `V_rms = 120 [V]
I_rms = 10 [A]
P_real = 1000 [W]
S_apparent = V_rms * I_rms
PF = P_real / S_apparent
phi = acos(PF)
// PF=0.833, phi≈33.6°`
        },
        // Extreme Unit Edge Cases
        {
            title: "Microscale Geometry",
            category: "Extreme Units",
            description: "Very small unit handling (micrometer scale).",
            equations: `d = 0.000001 [m]
A_circle = pi * (d/2)^2
Vol_sphere = (4/3) * pi * (d/2)^3
// A≈7.85e-13 m², Vol≈5.24e-19 m³`
        },
        {
            title: "Astronomical Scale",
            category: "Extreme Units",
            description: "Very large values (speed of light).",
            equations: `c = 299792458 [m/s]
year = 31557600 [s]
light_year = c * year
// light_year≈9.46e15 m`
        },
        {
            title: "Temperature Difference",
            category: "Extreme Units",
            description: "Temperature differences and thermal resistance.",
            equations: `T1 = 373.15 [K]
T2 = 293.15 [K]
dT = T1 - T2
Q = 1000 [W]
R_thermal = dT / Q
// dT=80 K`
        },
        {
            title: "Near-Zero Values",
            category: "Extreme Units",
            description: "Handling zero and near-zero calculations.",
            equations: `x = 0.0001
y = x^2
z = 1 / (x + 0.01)
// y=1e-8, z≈99.01`
        },
        // Array Sweeps and Plotting
        {
            title: "Linspace Array",
            category: "Array Sweeps",
            description: "Test linspace array generation and propagation.",
            equations: `t = linspace(0, 10, 5) [s]
v = 5 [m/s]
x = v * t
// x should be array: [0, 12.5, 25, 37.5, 50] m`
        },
        {
            title: "Arange Array",
            category: "Array Sweeps",
            description: "Test arange array generation with step.",
            equations: `x = arange(0, 5, 1) [m]
y = x^2
// y should be: [0, 1, 4, 9, 16] m²`
        },
        {
            title: "Explicit Array",
            category: "Array Sweeps",
            description: "Test explicit array definition.",
            equations: `P = [100, 200, 300, 400, 500] [kPa]
A = 0.01 [m^2]
F = P * A
// F should be array of forces in N`
        },
        {
            title: "Scientific Notation Array",
            category: "Array Sweeps",
            description: "Arrays with scientific notation values.",
            equations: `E = [1e9, 2e9, 3e9] [Pa]
A = 0.001 [m^2]
F = E * A
// F should be [1e6, 2e6, 3e6] N`
        },
        {
            title: "Simple Line Plot",
            category: "Plotting",
            description: "Generate a basic line plot from array data.",
            equations: `t = linspace(0, 5, 20) [s]
v = 10 [m/s]
x = v * t
plot(t, x)`
        },
        {
            title: "Multi-Variable Plot",
            category: "Plotting",
            description: "Plot multiple Y variables against same X.",
            equations: `t = linspace(0, 2, 20) [s]
v0 = 20 [m/s]
a = -9.81 [m/s^2]
v = v0 + a * t
y = v0 * t + 0.5 * a * t^2
plot(t, [y, v])`
        },
        {
            title: "Scatter Plot",
            category: "Plotting",
            description: "Generate a scatter plot instead of line.",
            equations: `x = [1, 2, 3, 4, 5]
y = [2.1, 3.9, 6.2, 7.8, 10.1]
scatter(x, y)
// Best fit would be y ≈ 2x`
        },
        {
            title: "Parametric Sweep",
            category: "Plotting",
            description: "Sweep a parameter and plot results.",
            equations: `T = linspace(250, 350, 10) [K]
P = 101325 [Pa]
rho = prop('Air', 'D', 'T', 300, 'P', 101325)
// TODO: rho for each T
plot(T, T)`
        },
    ];

    // Group sections by category
    const categories = [...new Set(sections.map(s => s.category))];

    return (
        <div className="instructions-container">
            <div className="instructions-header">
                <h1>🧪 Stress Tests</h1>
                <p>Comprehensive test cases for equation parsing, unit propagation, and solver capabilities. Each test is editable and runnable. <strong>Right-click on results</strong> to access key variables and unit conversion features!</p>
            </div>

            <div className="instructions-content">
                {categories.map(category => (
                    <div key={category} className="category-section">
                        <h2 className="category-title">{category}</h2>
                        {sections
                            .filter(s => s.category === category)
                            .map((section, index) => (
                                <MiniEquationEditor
                                    key={`${category}-${index}`}
                                    title={section.title}
                                    description={section.description}
                                    category={section.category}
                                    initialEquations={section.equations}
                                />
                            ))
                        }
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StressTests;
