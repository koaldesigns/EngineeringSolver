/**
 * Documentation.jsx
 * 
 * Comprehensive documentation for the Engineering Equation Solver.
 * This file documents ALL supported mathematical operators, function calls, and unit analysis features.
 * 
 * ============================================================================
 * IMPORTANT NOTE FOR DEVELOPERS/AGENTS:
 * ============================================================================
 * When adding new features to the solver (numerical.py, parser.py, units.py):
 * 1. Update this documentation file to include the new feature
 * 2. Add examples showing how to use the new feature
 * 3. Include any unit handling behavior
 * 4. Update the FEATURE_REFERENCE.md file in the project root
 * ============================================================================
 */

import React, { useState } from 'react';
import './Documentation.css';

const Documentation = () => {
    const [activeSection, setActiveSection] = useState('overview');

    const sections = [
        { id: 'overview', title: 'Overview', icon: '📋' },
        { id: 'syntax', title: 'Basic Syntax', icon: '✏️' },
        { id: 'operators', title: 'Operators', icon: '➕' },
        { id: 'functions', title: 'Math Functions', icon: '📐' },
        { id: 'trig', title: 'Trigonometry', icon: '🔺' },
        { id: 'units', title: 'Units System', icon: '📏' },
        { id: 'thermo', title: 'Thermodynamics', icon: '🌡️' },
        { id: 'arrays', title: 'Arrays & Plotting', icon: '📊' },
        { id: 'advanced', title: 'Advanced', icon: '🚀' },
        { id: 'reference', title: 'Quick Reference', icon: '📖' },
    ];

    const renderSection = () => {
        switch (activeSection) {
            case 'overview':
                return <OverviewSection />;
            case 'syntax':
                return <SyntaxSection />;
            case 'operators':
                return <OperatorsSection />;
            case 'functions':
                return <FunctionsSection />;
            case 'trig':
                return <TrigSection />;
            case 'units':
                return <UnitsSection />;
            case 'thermo':
                return <ThermoSection />;
            case 'arrays':
                return <ArraysPlottingSection />;
            case 'advanced':
                return <AdvancedSection />;
            case 'reference':
                return <ReferenceSection />;
            default:
                return <OverviewSection />;
        }
    };

    return (
        <div className="documentation-container">
            <div className="doc-header">
                <h1>📘 Complete Feature Reference</h1>
                <p>Comprehensive documentation for all solver capabilities</p>
            </div>

            <div className="doc-layout">
                <nav className="doc-nav">
                    {sections.map((section) => (
                        <button
                            key={section.id}
                            className={`doc-nav-item ${activeSection === section.id ? 'active' : ''}`}
                            onClick={() => setActiveSection(section.id)}
                        >
                            <span className="nav-icon">{section.icon}</span>
                            <span className="nav-label">{section.title}</span>
                        </button>
                    ))}
                </nav>

                <div className="doc-content">
                    {renderSection()}
                </div>
            </div>
        </div>
    );
};

// ============================================================================
// SECTION COMPONENTS
// ============================================================================

const OverviewSection = () => (
    <div className="doc-section">
        <h2>🎯 Engineering Equation Solver Overview</h2>

        <div className="info-card highlight">
            <h3>What is this solver?</h3>
            <p>
                The Engineering Equation Solver (EES) is a powerful numerical solver designed for
                engineering calculations. It combines equation solving with automatic unit tracking,
                thermodynamic property lookups, and dimensional analysis.
            </p>
        </div>

        <h3>Key Capabilities</h3>
        <div className="feature-grid">
            <div className="feature-card">
                <span className="feature-icon">🔢</span>
                <h4>Equation Solving</h4>
                <p>Solve systems of linear and nonlinear equations simultaneously</p>
            </div>
            <div className="feature-card">
                <span className="feature-icon">📏</span>
                <h4>Unit Tracking</h4>
                <p>Automatic unit propagation and dimensional analysis</p>
            </div>
            <div className="feature-card">
                <span className="feature-icon">🌡️</span>
                <h4>Thermodynamics</h4>
                <p>Access fluid properties via CoolProp database</p>
            </div>
            <div className="feature-card">
                <span className="feature-icon">⚠️</span>
                <h4>Validation</h4>
                <p>Unit consistency warnings to catch errors early</p>
            </div>
        </div>

        <h3>Workflow</h3>
        <ol className="workflow-list">
            <li><strong>Enter equations</strong> - One per line in the editor</li>
            <li><strong>Add units</strong> - Use square brackets: <code>x = 10 [m]</code></li>
            <li><strong>Click Run</strong> - The solver finds all variable values</li>
            <li><strong>Review results</strong> - Values with inferred/propagated units</li>
        </ol>
    </div>
);

const SyntaxSection = () => (
    <div className="doc-section">
        <h2>✏️ Basic Syntax</h2>

        <h3>Equation Format</h3>
        <div className="syntax-block">
            <p>Enter one equation per line. The solver automatically normalizes equations for solving.</p>
            <div className="code-example">
                <code>variable = expression</code>
                <code>expression1 = expression2</code>
                <code>expression = 0   // Implicit form</code>
            </div>
        </div>

        <h3>Variable Names</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Rule</th><th>Example</th><th>Valid?</th></tr>
            </thead>
            <tbody>
                <tr><td>Must start with letter or underscore</td><td><code>velocity</code>, <code>_temp</code></td><td>✅</td></tr>
                <tr><td>Can contain numbers after first char</td><td><code>T1</code>, <code>P_2</code></td><td>✅</td></tr>
                <tr><td>Case-sensitive</td><td><code>T</code> ≠ <code>t</code></td><td>✅</td></tr>
                <tr><td>Cannot start with number</td><td><code>2nd_value</code></td><td>❌</td></tr>
                <tr><td>No reserved words</td><td><code>sin</code>, <code>cos</code>, <code>exp</code></td><td>❌</td></tr>
            </tbody>
        </table>

        <h3>Reserved Words</h3>
        <p>The following are reserved and cannot be used as variable names:</p>
        <div className="code-inline-list">
            <code>sin</code> <code>cos</code> <code>tan</code> <code>asin</code> <code>acos</code> <code>atan</code>
            <code>exp</code> <code>log</code> <code>log10</code> <code>sqrt</code> <code>abs</code>
            <code>min</code> <code>max</code> <code>pow</code> <code>sinh</code> <code>cosh</code> <code>tanh</code>
            <code>sum</code> <code>integral</code> <code>derivative</code> <code>diff</code>
            <code>convert</code> <code>prop</code> <code>pi</code> <code>e</code>
            <code>linspace</code> <code>arange</code> <code>plot</code> <code>scatter</code>
        </div>

        <h3>Comments</h3>
        <div className="code-example">
            <code>x = 5 // This is a comment (C-style)</code>
            <code>y = 10 # This is also a comment (Python-style)</code>
        </div>

        <h3>Numbers</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Format</th><th>Example</th></tr>
            </thead>
            <tbody>
                <tr><td>Integer</td><td><code>42</code>, <code>-100</code></td></tr>
                <tr><td>Decimal</td><td><code>3.14159</code>, <code>0.001</code></td></tr>
                <tr><td>Scientific notation</td><td><code>2.5e-10</code>, <code>1.38E-23</code>, <code>200e9</code></td></tr>
            </tbody>
        </table>
    </div>
);

const OperatorsSection = () => (
    <div className="doc-section">
        <h2>➕ Mathematical Operators</h2>

        <h3>Arithmetic Operators</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Operator</th><th>Description</th><th>Example</th><th>Result</th></tr>
            </thead>
            <tbody>
                <tr><td><code>+</code></td><td>Addition</td><td><code>3 + 5</code></td><td><code>8</code></td></tr>
                <tr><td><code>-</code></td><td>Subtraction</td><td><code>10 - 4</code></td><td><code>6</code></td></tr>
                <tr><td><code>*</code></td><td>Multiplication</td><td><code>6 * 7</code></td><td><code>42</code></td></tr>
                <tr><td><code>/</code></td><td>Division</td><td><code>15 / 3</code></td><td><code>5</code></td></tr>
                <tr><td><code>^</code></td><td>Exponentiation</td><td><code>2^3</code></td><td><code>8</code></td></tr>
                <tr><td><code>**</code></td><td>Exponentiation (alt)</td><td><code>2**3</code></td><td><code>8</code></td></tr>
            </tbody>
        </table>

        <h3>Unit Behavior with Operators</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Operation</th><th>Example</th><th>Result Unit</th></tr>
            </thead>
            <tbody>
                <tr><td>Addition</td><td><code>10[m] + 5[m]</code></td><td><code>15 m</code></td></tr>
                <tr><td>Multiplication</td><td><code>10[m] * 5[m]</code></td><td><code>50 m²</code></td></tr>
                <tr><td>Division</td><td><code>100[m] / 10[s]</code></td><td><code>10 m/s</code></td></tr>
                <tr><td>Exponentiation</td><td><code>(5[m])^2</code></td><td><code>25 m²</code></td></tr>
                <tr><td>Square root</td><td><code>sqrt(25[m^2])</code></td><td><code>5 m</code></td></tr>
            </tbody>
        </table>

        <div className="warning-box">
            <h4>⚠️ Important: Unit Compatibility</h4>
            <p>Addition and subtraction require compatible units. Adding <code>5[m] + 3[s]</code> will generate a unit mismatch warning.</p>
        </div>

        <h3>Comparison Operators (in equations)</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Operator</th><th>Description</th><th>Example</th></tr>
            </thead>
            <tbody>
                <tr><td><code>=</code></td><td>Equality constraint</td><td><code>x^2 + y^2 = 25</code></td></tr>
            </tbody>
        </table>

        <h3>Operator Precedence</h3>
        <ol>
            <li><strong>Parentheses</strong> <code>()</code> - Highest</li>
            <li><strong>Exponentiation</strong> <code>^</code>, <code>**</code></li>
            <li><strong>Unary minus</strong> <code>-x</code></li>
            <li><strong>Multiplication/Division</strong> <code>*</code>, <code>/</code></li>
            <li><strong>Addition/Subtraction</strong> <code>+</code>, <code>-</code> - Lowest</li>
        </ol>
    </div>
);

const FunctionsSection = () => (
    <div className="doc-section">
        <h2>📐 Mathematical Functions</h2>

        <h3>Basic Functions</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Function</th><th>Description</th><th>Example</th><th>Unit Handling</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>sqrt(x)</code></td>
                    <td>Square root</td>
                    <td><code>sqrt(16) = 4</code></td>
                    <td>Returns √(unit)</td>
                </tr>
                <tr>
                    <td><code>abs(x)</code></td>
                    <td>Absolute value</td>
                    <td><code>abs(-5) = 5</code></td>
                    <td>Preserves units</td>
                </tr>
                <tr>
                    <td><code>min(x, y)</code></td>
                    <td>Minimum value</td>
                    <td><code>min(3, 7) = 3</code></td>
                    <td>Requires same units</td>
                </tr>
                <tr>
                    <td><code>max(x, y)</code></td>
                    <td>Maximum value</td>
                    <td><code>max(3, 7) = 7</code></td>
                    <td>Requires same units</td>
                </tr>
                <tr>
                    <td><code>pow(x, n)</code></td>
                    <td>Power function</td>
                    <td><code>pow(2, 3) = 8</code></td>
                    <td>Returns unit^n</td>
                </tr>
            </tbody>
        </table>

        <h3>Exponential & Logarithmic Functions</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Function</th><th>Description</th><th>Example</th><th>Unit Handling</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>exp(x)</code></td>
                    <td>e raised to power x</td>
                    <td><code>exp(1) ≈ 2.718</code></td>
                    <td>Requires dimensionless input, returns dimensionless</td>
                </tr>
                <tr>
                    <td><code>log(x)</code></td>
                    <td>Natural logarithm (ln)</td>
                    <td><code>log(e) = 1</code></td>
                    <td>Requires dimensionless input, returns dimensionless</td>
                </tr>
                <tr>
                    <td><code>log10(x)</code></td>
                    <td>Base-10 logarithm</td>
                    <td><code>log10(100) = 2</code></td>
                    <td>Requires dimensionless input, returns dimensionless</td>
                </tr>
            </tbody>
        </table>

        <div className="info-card">
            <h4>💡 Tip: Dimensionless Ratios</h4>
            <p>To use log/exp with quantities that have units, create a dimensionless ratio first:</p>
            <code>log(pressure / P_ref)  // Both in same units = dimensionless</code>
        </div>

        <h3>Hyperbolic Functions</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Function</th><th>Description</th></tr>
            </thead>
            <tbody>
                <tr><td><code>sinh(x)</code></td><td>Hyperbolic sine</td></tr>
                <tr><td><code>cosh(x)</code></td><td>Hyperbolic cosine</td></tr>
                <tr><td><code>tanh(x)</code></td><td>Hyperbolic tangent</td></tr>
            </tbody>
        </table>

        <h3>Mathematical Constants</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Constant</th><th>Value</th><th>Description</th></tr>
            </thead>
            <tbody>
                <tr><td><code>pi</code></td><td>3.14159265...</td><td>Ratio of circumference to diameter</td></tr>
                <tr><td><code>e</code></td><td>2.71828182...</td><td>Euler's number (base of natural log)</td></tr>
            </tbody>
        </table>
    </div>
);

const TrigSection = () => (
    <div className="doc-section">
        <h2>🔺 Trigonometric Functions</h2>

        <div className="info-card highlight">
            <h4>🔄 Angle Mode</h4>
            <p>
                The solver supports both <strong>Degrees</strong> and <strong>Radians</strong> modes.
                Use the angle unit selector in the toolbar to switch between them.
                Default is <strong>Degrees</strong> for engineering convenience.
            </p>
        </div>

        <h3>Standard Trigonometric Functions</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Function</th><th>Description</th><th>Input</th><th>Output</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>sin(x)</code></td>
                    <td>Sine</td>
                    <td>Angle (deg or rad based on mode)</td>
                    <td>Dimensionless [-1, 1]</td>
                </tr>
                <tr>
                    <td><code>cos(x)</code></td>
                    <td>Cosine</td>
                    <td>Angle (deg or rad based on mode)</td>
                    <td>Dimensionless [-1, 1]</td>
                </tr>
                <tr>
                    <td><code>tan(x)</code></td>
                    <td>Tangent</td>
                    <td>Angle (deg or rad based on mode)</td>
                    <td>Dimensionless</td>
                </tr>
            </tbody>
        </table>

        <h3>Inverse Trigonometric Functions</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Function</th><th>Description</th><th>Input</th><th>Output</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>asin(x)</code></td>
                    <td>Arc sine (inverse sine)</td>
                    <td>Dimensionless [-1, 1]</td>
                    <td>Angle with unit (deg or rad)</td>
                </tr>
                <tr>
                    <td><code>acos(x)</code></td>
                    <td>Arc cosine (inverse cosine)</td>
                    <td>Dimensionless [-1, 1]</td>
                    <td>Angle with unit (deg or rad)</td>
                </tr>
                <tr>
                    <td><code>atan(x)</code></td>
                    <td>Arc tangent (inverse tangent)</td>
                    <td>Dimensionless</td>
                    <td>Angle with unit (deg or rad)</td>
                </tr>
            </tbody>
        </table>

        <h3>Examples</h3>
        <div className="code-example">
            <p>// In Degrees mode:</p>
            <code>angle = 45</code>
            <code>s = sin(angle)         // s = 0.707</code>
            <code>c = cos(angle)         // c = 0.707</code>
            <code>check = s^2 + c^2      // check = 1</code>
            <br />
            <code>x = 0.5</code>
            <code>theta = asin(x)        // theta = 30 deg</code>
        </div>

        <h3>Unit Handling</h3>
        <div className="feature-grid">
            <div className="feature-card">
                <h4>With Angle Units</h4>
                <p><code>sin(30 [deg])</code> automatically converts to radians internally</p>
            </div>
            <div className="feature-card">
                <h4>Without Units</h4>
                <p><code>sin(45)</code> uses the current angle mode setting</p>
            </div>
            <div className="feature-card">
                <h4>Auto-Inference</h4>
                <p>Variables in trig functions are automatically inferred to have angle units</p>
            </div>
        </div>

        <div className="warning-box">
            <h4>⚠️ Invalid Input</h4>
            <p>Passing dimensional quantities (like length or time) to trig functions will raise an error:</p>
            <code>sin(5 [m])  // Error: sin expects angle or dimensionless</code>
        </div>
    </div>
);

const UnitsSection = () => (
    <div className="doc-section">
        <h2>📏 Units System</h2>

        <div className="info-card highlight">
            <h4>Powered by Pint</h4>
            <p>
                The solver uses the Pint library for unit handling, supporting hundreds of physical units
                with automatic conversion and dimensional analysis.
            </p>
        </div>

        <h3>Specifying Units</h3>
        <div className="code-example">
            <p>// Units in square brackets after values:</p>
            <code>length = 10 [m]</code>
            <code>time = 5 [s]</code>
            <code>velocity = length / time  // Automatically: 2 m/s</code>
            <br />
            <p>// LHS unit declaration:</p>
            <code>Area [m^2] = length^2</code>
        </div>

        <h3>Supported Unit Categories</h3>

        <h4>Length</h4>
        <div className="code-inline-list">
            <code>m</code> <code>cm</code> <code>mm</code> <code>km</code>
            <code>in</code> <code>ft</code> <code>yd</code> <code>mi</code>
            <code>um</code> <code>nm</code>
        </div>

        <h4>Mass</h4>
        <div className="code-inline-list">
            <code>kg</code> <code>g</code> <code>mg</code>
            <code>lb</code> <code>lbm</code> <code>oz</code> <code>ton</code>
        </div>

        <h4>Time</h4>
        <div className="code-inline-list">
            <code>s</code> <code>ms</code> <code>min</code> <code>hr</code> <code>day</code>
        </div>

        <h4>Temperature</h4>
        <div className="code-inline-list">
            <code>K</code> <code>degC</code> <code>C</code>
            <code>degF</code> <code>F</code> <code>degR</code> <code>R</code>
        </div>

        <h4>Pressure</h4>
        <div className="code-inline-list">
            <code>Pa</code> <code>kPa</code> <code>MPa</code> <code>bar</code>
            <code>atm</code> <code>psi</code> <code>psia</code>
        </div>

        <h4>Energy</h4>
        <div className="code-inline-list">
            <code>J</code> <code>kJ</code> <code>MJ</code>
            <code>Btu</code> <code>cal</code> <code>kcal</code> <code>Wh</code> <code>kWh</code>
        </div>

        <h4>Power</h4>
        <div className="code-inline-list">
            <code>W</code> <code>kW</code> <code>MW</code> <code>hp</code>
        </div>

        <h4>Force</h4>
        <div className="code-inline-list">
            <code>N</code> <code>kN</code> <code>lbf</code>
        </div>

        <h4>Angle</h4>
        <div className="code-inline-list">
            <code>deg</code> <code>rad</code>
        </div>

        <h3>Unit Conversion Function</h3>
        <div className="code-example">
            <code>convert(value, 'from_unit', 'to_unit')</code>
            <br />
            <p>// Examples:</p>
            <code>T_F = convert(100, 'C', 'F')  // 212</code>
            <code>P_psi = convert(1, 'atm', 'psi')  // 14.696</code>
            <code>L_ft = convert(10, 'm', 'ft')  // 32.808</code>
        </div>

        <h3>EES Unit Aliases</h3>
        <p>For compatibility with EES notation, these aliases are supported:</p>
        <table className="doc-table">
            <thead>
                <tr><th>EES Style</th><th>Interpreted As</th></tr>
            </thead>
            <tbody>
                <tr><td><code>C</code></td><td><code>degC</code> (Celsius)</td></tr>
                <tr><td><code>F</code></td><td><code>degF</code> (Fahrenheit)</td></tr>
                <tr><td><code>R</code></td><td><code>degR</code> (Rankine)</td></tr>
                <tr><td><code>psia</code>, <code>psig</code></td><td><code>psi</code></td></tr>
                <tr><td><code>lbm</code></td><td><code>pound</code> (mass)</td></tr>
                <tr><td><code>lbf</code></td><td><code>force_pound</code></td></tr>
                <tr><td><code>L</code>, <code>liter</code></td><td><code>liter</code></td></tr>
                <tr><td><code>gal</code></td><td><code>gallon</code></td></tr>
            </tbody>
        </table>

        <h3>Unit Validation & Warnings</h3>
        <p>The solver performs dimensional analysis and generates warnings for:</p>
        <ul>
            <li>Adding/subtracting incompatible units</li>
            <li>Specified units not matching calculated units</li>
            <li>Passing dimensional values to functions expecting dimensionless</li>
        </ul>

        <div className="info-card">
            <h4>💡 Warning System</h4>
            <p>
                The solver uses <strong>warnings</strong> instead of errors for unit mismatches.
                This allows calculations to continue while alerting you to potential issues.
            </p>
        </div>

        <h3>Unit Display Indicators</h3>
        <p>The results panel uses visual cues to show unit status:</p>

        <table className="doc-table">
            <thead>
                <tr><th>Indicator</th><th>Meaning</th><th>Action</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Solid border</strong></td>
                    <td>User-defined / Confirmed unit</td>
                    <td>No action needed - unit is explicitly set</td>
                </tr>
                <tr>
                    <td><strong>Dashed border with dot (•)</strong></td>
                    <td>Auto-propagated / Unconfirmed unit</td>
                    <td>Right-click to verify and confirm the unit</td>
                </tr>
            </tbody>
        </table>

        <div className="warning-box">
            <h4>⚠️ Why Confirm Units?</h4>
            <p>
                Auto-propagated units are calculated automatically from your equations but may not
                match your intended output format. Confirming units helps catch input errors and
                ensures your results are in the expected format.
            </p>
        </div>

        <h4>How to Confirm a Unit</h4>
        <ol>
            <li>Right-click on any variable result card</li>
            <li>Enter or select the desired display unit</li>
            <li>The unit badge changes from dashed to solid border</li>
        </ol>
    </div>
);

const ThermoSection = () => (
    <div className="doc-section">
        <h2>🌡️ Thermodynamic Properties</h2>

        <div className="info-card highlight">
            <h4>Powered by CoolProp</h4>
            <p>
                Access thermodynamic properties for over 120 fluids using the <code>prop()</code> function.
                Properties are returned with appropriate SI units automatically.
            </p>
        </div>

        <h3>prop() Function Syntax</h3>
        <div className="code-example">
            <code>prop('FluidName', 'OutputProperty', 'Input1', Value1, 'Input2', Value2)</code>
        </div>

        <h3>Common Fluids</h3>
        <div className="code-inline-list">
            <code>Water</code> <code>Air</code> <code>Nitrogen</code> <code>Oxygen</code>
            <code>CO2</code> <code>Ammonia</code> <code>R134a</code> <code>R410A</code>
            <code>R22</code> <code>R32</code> <code>Propane</code> <code>Methane</code>
            <code>Hydrogen</code> <code>Helium</code>
        </div>

        <h3>Property Codes</h3>
        <table className="doc-table">
            <thead>
                <tr><th>Code</th><th>Property</th><th>Units</th></tr>
            </thead>
            <tbody>
                <tr><td><code>T</code></td><td>Temperature</td><td>K</td></tr>
                <tr><td><code>P</code></td><td>Pressure</td><td>Pa</td></tr>
                <tr><td><code>D</code>, <code>DMASS</code></td><td>Mass density</td><td>kg/m³</td></tr>
                <tr><td><code>V</code></td><td>Specific volume</td><td>m³/kg</td></tr>
                <tr><td><code>H</code>, <code>HMASS</code></td><td>Specific enthalpy</td><td>J/kg</td></tr>
                <tr><td><code>U</code>, <code>UMASS</code></td><td>Specific internal energy</td><td>J/kg</td></tr>
                <tr><td><code>S</code>, <code>SMASS</code></td><td>Specific entropy</td><td>J/(kg·K)</td></tr>
                <tr><td><code>C</code>, <code>CP</code>, <code>CPMASS</code></td><td>Specific heat (const P)</td><td>J/(kg·K)</td></tr>
                <tr><td><code>CV</code>, <code>CVMASS</code></td><td>Specific heat (const V)</td><td>J/(kg·K)</td></tr>
                <tr><td><code>Q</code></td><td>Quality (vapor fraction)</td><td>dimensionless</td></tr>
                <tr><td><code>A</code>, <code>SPEED_OF_SOUND</code></td><td>Speed of sound</td><td>m/s</td></tr>
                <tr><td><code>VISCOSITY</code>, <code>MU</code></td><td>Dynamic viscosity</td><td>Pa·s</td></tr>
                <tr><td><code>CONDUCTIVITY</code>, <code>K</code>, <code>L</code></td><td>Thermal conductivity</td><td>W/(m·K)</td></tr>
                <tr><td><code>M</code>, <code>MOLAR_MASS</code></td><td>Molar mass</td><td>kg/mol</td></tr>
            </tbody>
        </table>

        <h3>Examples</h3>
        <div className="code-example">
            <p>// Air density at standard conditions:</p>
            <code>T = 300  // K</code>
            <code>P = 101325  // Pa</code>
            <code>rho = prop('Air', 'D', 'T', T, 'P', P)  // kg/m³</code>
            <br />
            <p>// Water enthalpy at saturation:</p>
            <code>h_vapor = prop('Water', 'H', 'P', 101325, 'Q', 1)</code>
            <code>h_liquid = prop('Water', 'H', 'P', 101325, 'Q', 0)</code>
            <code>h_fg = h_vapor - h_liquid  // Latent heat</code>
            <br />
            <p>// R134a refrigeration cycle:</p>
            <code>T_evap = 253.15  // -20°C in K</code>
            <code>P_evap = prop('R134a', 'P', 'T', T_evap, 'Q', 1)</code>
        </div>

        <h3>Input Unit Inference</h3>
        <p>Variables used as inputs to <code>prop()</code> automatically get inferred units:</p>
        <ul>
            <li><code>T</code> inputs → K (Kelvin)</li>
            <li><code>P</code> inputs → Pa (Pascal)</li>
            <li><code>D</code> inputs → kg/m³</li>
            <li><code>H</code>, <code>U</code> inputs → J/kg</li>
            <li><code>S</code> inputs → J/(kg·K)</li>
            <li><code>Q</code> inputs → dimensionless</li>
        </ul>

        <div className="warning-box">
            <h4>⚠️ Standard Units Required</h4>
            <p>
                CoolProp expects SI units. If you provide values with units, they will be
                automatically converted. If you provide raw numbers, they are assumed to be
                in standard SI units (K, Pa, etc.).
            </p>
        </div>
    </div>
);

const ArraysPlottingSection = () => (
    <div className="doc-section">
        <h2>📊 Arrays & Plotting</h2>

        <div className="info-card highlight">
            <h4>Parameter Sweeps</h4>
            <p>
                Arrays allow you to solve equations for multiple values of a parameter at once.
                Results are computed for each value in the array, making it easy to explore how
                outputs change across a range of inputs.
            </p>
        </div>

        <h3>Defining Arrays</h3>

        <h4>linspace - Evenly Spaced Values</h4>
        <div className="code-example">
            <code>linspace(start, end, count)</code>
            <br />
            <p>// Creates 'count' evenly spaced values from 'start' to 'end':</p>
            <code>t = linspace(0, 10, 50)     // 50 points from 0 to 10</code>
            <code>t = linspace(0, 5, 6) [s]   // With units: [0, 1, 2, 3, 4, 5] s</code>
        </div>

        <h4>arange - Values with Step</h4>
        <div className="code-example">
            <code>arange(start, end, step)</code>
            <br />
            <p>// Creates values from 'start' to 'end' (exclusive) with given 'step':</p>
            <code>P = arange(100, 500, 50) [kPa]  // [100, 150, 200, 250, 300, 350, 400, 450] kPa</code>
        </div>

        <h4>Explicit Arrays</h4>
        <div className="code-example">
            <p>// List specific values in square brackets:</p>
            <code>T = [300, 350, 400, 450] [K]</code>
            <code>x = [1, 2, 3, 4, 5]</code>
        </div>

        <h3>Array Combination Modes</h3>
        <p>When you define multiple arrays, you can control how they are combined:</p>

        <table className="doc-table">
            <thead>
                <tr><th>Mode</th><th>Directive</th><th>Behavior</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Parallel</strong> (default)</td>
                    <td><code>@parallel</code></td>
                    <td>Arrays iterated together (element-wise)</td>
                </tr>
                <tr>
                    <td><strong>Grid</strong></td>
                    <td><code>@grid</code></td>
                    <td>Cartesian product (all combinations)</td>
                </tr>
            </tbody>
        </table>

        <div className="code-example">
            <p>// Parallel mode (default): x=[1,2], y=[10,20] → 2 cases: (1,10), (2,20)</p>
            <code>@parallel</code>
            <code>x = [1, 2]</code>
            <code>y = [10, 20]</code>
            <br />
            <p>// Grid mode: x=[1,2], y=[10,20] → 4 cases: (1,10), (1,20), (2,10), (2,20)</p>
            <code>@grid</code>
            <code>x = [1, 2]</code>
            <code>y = [10, 20]</code>
        </div>

        <h3>Array Propagation</h3>
        <p>When any input is an array, all dependent calculations become arrays:</p>
        <div className="code-example">
            <code>t = linspace(0, 5, 6) [s]   // Array: [0, 1, 2, 3, 4, 5]</code>
            <code>v = 10 [m/s]                // Scalar</code>
            <code>x = v * t                   // Becomes array: [0, 10, 20, 30, 40, 50] m</code>
        </div>

        <h3>Plotting</h3>
        <p>Generate interactive Plotly charts from array results:</p>

        <h4>Basic Plot Syntax</h4>
        <div className="code-example">
            <code>plot(x_variable, y_variable)</code>
            <code>plot(x_variable, [y1, y2, y3])   // Multiple Y on same plot</code>
            <code>scatter(x_variable, y_variable)  // Scatter plot</code>
        </div>

        <h4>Complete Example - Projectile Motion</h4>
        <div className="code-example">
            <p>// Define time array</p>
            <code>t = linspace(0, 5, 50) [s]</code>
            <br />
            <p>// Initial conditions</p>
            <code>v0 = 30 [m/s]</code>
            <code>theta = 45                    // Launch angle (degrees)</code>
            <code>g = 9.81 [m/s^2]</code>
            <br />
            <p>// Calculate trajectory</p>
            <code>x = v0 * cos(theta) * t</code>
            <code>y = v0 * sin(theta) * t - 0.5 * g * t^2</code>
            <br />
            <p>// Generate plot</p>
            <code>plot(x, y)</code>
        </div>

        <div className="info-card">
            <h4>💡 Plot Features</h4>
            <ul>
                <li>Axis labels automatically include variable names and units</li>
                <li>Multiple Y variables shown with different colors</li>
                <li>Interactive: hover for values, zoom, and pan</li>
                <li>Click the expand button to view plots larger</li>
            </ul>
        </div>
    </div>
);

const AdvancedSection = () => (
    <div className="doc-section">
        <h2>🚀 Advanced Features</h2>

        <h3>Summation</h3>
        <div className="code-example">
            <code>sum(function, start, end)</code>
            <br />
            <p>// Example: Sum of i² from 1 to 5</p>
            <code>result = sum(lambda i: i^2, 1, 5)  // 1+4+9+16+25 = 55</code>
        </div>
        <div className="info-card">
            <p><strong>Note:</strong> The sum function requires a lambda or function as the first argument.
                Inline function definition in equation text is limited.</p>
        </div>

        <h3>Integration</h3>
        <div className="code-example">
            <code>integral(function, lower, upper)</code>
            <br />
            <p>// Numerical integration using scipy.integrate.quad</p>
        </div>

        <h3>Numerical Differentiation</h3>
        <div className="code-example">
            <code>derivative(function, point)</code>
            <code>diff(function, point)</code>
            <br />
            <p>// Uses central difference method (default dx = 1e-6)</p>
        </div>

        <h3>Implicit Equations</h3>
        <p>The solver can handle implicit equations where the variable appears on both sides:</p>
        <div className="code-example">
            <code>x^2 + y^2 = 25  // Circle equation</code>
            <code>y = x + 1       // Line equation</code>
            <code>// Solver finds intersection points</code>
        </div>

        <h3>Coupled Systems</h3>
        <p>Variables can depend on each other across multiple equations:</p>
        <div className="code-example">
            <code>m = 10 [kg]</code>
            <code>v = 5 [m/s]</code>
            <code>KE = 0.5 * m * v^2  // Kinetic energy</code>
            <code>h = 10 [m]</code>
            <code>g = 9.81 [m/s^2]</code>
            <code>PE = m * g * h      // Potential energy</code>
            <code>E_total = KE + PE   // Total energy</code>
        </div>

        <h3>Name-Based Unit Inference</h3>
        <p>The solver can automatically infer units based on common variable naming patterns:</p>
        <table className="doc-table">
            <thead>
                <tr><th>Pattern</th><th>Inferred Unit</th></tr>
            </thead>
            <tbody>
                <tr><td><code>T_evap</code>, <code>T1</code>, <code>temp</code></td><td>K</td></tr>
                <tr><td><code>P_cond</code>, <code>P1</code>, <code>pressure</code></td><td>Pa</td></tr>
                <tr><td><code>m_dot</code>, <code>mdot</code></td><td>kg/s</td></tr>
                <tr><td><code>velocity</code>, <code>V_in</code></td><td>m/s</td></tr>
                <tr><td><code>h_fg</code>, <code>enthalpy</code></td><td>J/kg</td></tr>
                <tr><td><code>s_1</code>, <code>entropy</code></td><td>J/(kg·K)</td></tr>
            </tbody>
        </table>

        <h3>Initial Guesses</h3>
        <p>For nonlinear systems, you can provide initial guesses to help convergence:</p>
        <div className="code-example">
            <p>// Via API (not yet exposed in UI):</p>
            <code>initial_guesses = {'{'}x: 2, y: 3{'}'}</code>
        </div>
    </div>
);

const ReferenceSection = () => (
    <div className="doc-section">
        <h2>📖 Quick Reference Card</h2>

        <div className="reference-grid">
            <div className="reference-card">
                <h3>Arithmetic</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td><code>+</code></td><td>Add</td></tr>
                        <tr><td><code>-</code></td><td>Subtract</td></tr>
                        <tr><td><code>*</code></td><td>Multiply</td></tr>
                        <tr><td><code>/</code></td><td>Divide</td></tr>
                        <tr><td><code>^</code></td><td>Power</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="reference-card">
                <h3>Basic Functions</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td><code>sqrt(x)</code></td><td>√x</td></tr>
                        <tr><td><code>abs(x)</code></td><td>|x|</td></tr>
                        <tr><td><code>exp(x)</code></td><td>eˣ</td></tr>
                        <tr><td><code>log(x)</code></td><td>ln(x)</td></tr>
                        <tr><td><code>log10(x)</code></td><td>log₁₀(x)</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="reference-card">
                <h3>Trigonometry</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td><code>sin(x)</code></td><td>Sine</td></tr>
                        <tr><td><code>cos(x)</code></td><td>Cosine</td></tr>
                        <tr><td><code>tan(x)</code></td><td>Tangent</td></tr>
                        <tr><td><code>asin(x)</code></td><td>Arc sine</td></tr>
                        <tr><td><code>acos(x)</code></td><td>Arc cosine</td></tr>
                        <tr><td><code>atan(x)</code></td><td>Arc tangent</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="reference-card">
                <h3>Units</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td><code>x = 5 [m]</code></td><td>Assign with unit</td></tr>
                        <tr><td><code>x [m] = ...</code></td><td>Declare unit</td></tr>
                        <tr><td><code>convert(v, 'a', 'b')</code></td><td>Convert units</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="reference-card">
                <h3>Thermodynamics</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td colSpan="2"><code>prop('Fluid', 'Out', 'In1', v1, 'In2', v2)</code></td></tr>
                        <tr><td><code>T, P</code></td><td>Temp, Pressure</td></tr>
                        <tr><td><code>H, S</code></td><td>Enthalpy, Entropy</td></tr>
                        <tr><td><code>D, V</code></td><td>Density, Sp. Vol</td></tr>
                        <tr><td><code>Q</code></td><td>Quality</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="reference-card">
                <h3>Constants</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td><code>pi</code></td><td>3.14159...</td></tr>
                        <tr><td><code>e</code></td><td>2.71828...</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="reference-card">
                <h3>Arrays & Plots</h3>
                <table className="mini-table">
                    <tbody>
                        <tr><td><code>linspace(a,b,n)</code></td><td>n points a→b</td></tr>
                        <tr><td><code>arange(a,b,s)</code></td><td>a→b step s</td></tr>
                        <tr><td><code>[1, 2, 3]</code></td><td>Explicit array</td></tr>
                        <tr><td><code>plot(x, y)</code></td><td>Line plot</td></tr>
                        <tr><td><code>scatter(x, y)</code></td><td>Scatter plot</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <h3>Common Unit Symbols</h3>
        <div className="reference-units">
            <div><strong>Length:</strong> m, cm, mm, km, in, ft</div>
            <div><strong>Mass:</strong> kg, g, lb, lbm</div>
            <div><strong>Time:</strong> s, min, hr</div>
            <div><strong>Temperature:</strong> K, degC, C, degF, F</div>
            <div><strong>Pressure:</strong> Pa, kPa, MPa, bar, atm, psi</div>
            <div><strong>Energy:</strong> J, kJ, Btu, cal</div>
            <div><strong>Power:</strong> W, kW, hp</div>
            <div><strong>Force:</strong> N, kN, lbf</div>
        </div>
    </div>
);

export default Documentation;
