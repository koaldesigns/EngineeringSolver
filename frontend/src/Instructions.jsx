import React, { useState } from 'react';
import { solveEquations } from './api';
import './Instructions.css';
import {
    MiniEquationEditor
} from './EditorComponents';

// Instructions component uses the shared MiniEquationEditor

const Instructions = () => {
    const sections = [
        {
            title: "1. General Syntax",
            description: "Enter one equation per line. Variables start with a letter, and you can use comments with // or #.",
            equations: `x = 5
y = x^2 + 2
z = y * 3`
        },
        {
            title: "2. Units",
            description: "Define units in square brackets []. Common aliases are supported (e.g., degC, psi, lbm).",
            equations: `L = 10 [m]
T = 25 [degC]
P = 100 [kPa]
// Calculate area
A = L^2 [m^2]`
        },
        {
            title: "3. Unit Conversion",
            description: "Use the convert(value, 'from', 'to') function to convert between units.",
            equations: `// Temperature conversion
T_F = convert(100, 'C', 'F')

// Pressure conversion
P_psi = convert(1, 'atm', 'psi')

// Length conversion
L_ft = convert(10, 'm', 'ft')`
        },
        {
            title: "4. Math Functions",
            description: "Standard functions: sin, cos, tan, exp, log, sqrt, etc. Trig functions use degrees by default.",
            equations: `// Trigonometry (in degrees)
angle = 30
y = sin(angle)

// Other math functions
z = sqrt(100) + exp(2)
w = log(10)`
        },
        {
            title: "5. Thermodynamic Properties",
            description: "Use prop('Fluid', 'Out', 'In1', Val1, 'In2', Val2) to get fluid properties from CoolProp.",
            equations: `// Density of Air at 300K, 101325 Pa
rho = prop('Air', 'D', 'T', 300, 'P', 101325)

// Note: This requires backend support
// Common outputs: D (density), H (enthalpy), S (entropy)`
        },
        {
            title: "6. Complex Example",
            description: "Combine multiple concepts to solve engineering problems.",
            equations: `// Pipe flow calculation
D = 0.1 [m]              // Diameter
L = 50 [m]               // Length
V = 2 [m/s]              // Velocity

// Calculate area and volume
A = 3.14159 * (D/2)^2 [m^2]
Vol = A * L [m^3]

// Flow rate
Q = A * V [m^3/s]`
        }
    ];

    return (
        <div className="instructions-container">
            <div className="instructions-header">
                <h1>Interactive Guide & Examples</h1>
                <p>Learn by doing! Each section below has a mini equation editor you can modify and run independently. <strong>Right-click on results</strong> to access key variables and unit conversion features!</p>
            </div>

            <div className="instructions-content">
                {sections.map((section, index) => (
                    <MiniEquationEditor
                        key={index}
                        title={section.title}
                        description={section.description}
                        initialEquations={section.equations}
                    />
                ))}
            </div>
        </div>
    );
};

export default Instructions;
