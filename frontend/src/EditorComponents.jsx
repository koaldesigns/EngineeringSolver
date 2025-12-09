/**
 * EditorComponents.jsx
 * 
 * ============================================================================
 * ⚠️  CRITICAL: FEATURE PARITY REQUIREMENT  ⚠️
 * ============================================================================
 * 
 * This file is the SINGLE SOURCE OF TRUTH for all equation editor functionality.
 * 
 * RULES:
 * 1. ALL editor features MUST be implemented here first
 * 2. The MiniEquationEditor in this file MUST have 100% feature parity with EquationEditor.jsx
 * 3. If you add something to EquationEditor.jsx, you MUST add it here too
 * 4. The useEquationEditorState hook encapsulates ALL shared state logic
 * 
 * See: .agent/workflows/editor-feature-parity.md for full documentation
 * 
 * Shared components and utilities for equation editors.
 * This file ensures feature parity between the main EquationEditor and MiniEquationEditors.
 * 
 * IMPORTANT: Any new feature added to EquationEditor should be implemented here first,
 * then consumed by both the main editor and mini editors to maintain consistency.
 */

import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useConfirmedUnitsContext } from './ConfirmedUnitsContext';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
import { solveEquations, convertUnitViaBackend } from './api';



/**
 * Generates a unique hue value for a given unit string for color-coding badges
 */
export const getUnitHue = (unit) => {
    if (!unit) return 0;
    let hash = 0;
    for (let i = 0; i < unit.length; i++) {
        hash = Math.imul(31, hash) + unit.charCodeAt(i) | 0;
    }
    return Math.abs((hash * 137) % 360);
};

/**
 * Formats a number for display with appropriate precision.
 * Removes trailing zeros only when there's a decimal point to avoid
 * incorrectly truncating integer values (e.g., 500000 -> 5).
 */
export const formatNumber = (value, precision = 6) => {
    if (typeof value !== 'number') return value;

    const absVal = Math.abs(value);
    let str;

    // Use scientific notation for:
    // 1. Large numbers >= 1e6
    // 2. Small non-zero numbers < 1e-4
    if (absVal >= 1e6 || (absVal > 0 && absVal < 1e-4)) {
        str = value.toExponential(precision - 2);
    } else {
        str = value.toPrecision(precision);
    }

    // Clean up trailing zeros in mantissa
    if (str.includes('e') || str.includes('E')) {
        str = str.replace(/(\.\d*?[1-9])0+e/i, '$1e') // 1.2300e -> 1.23e
            .replace(/\.0+e/i, 'e')               // 1.0000e -> 1e
            .replace(/\+0+(?=\d)/, '+')           // e+05 -> e+5
            .replace(/-0+(?=\d)/, '-');           // e-05 -> e-5
    } else {
        if (str.includes('.')) {
            str = str.replace(/\.?0+$/, "");
        }
    }

    return str;
};

/**
 * Formats a unit string for display with Unicode superscripts.
 * Converts ^N and **N syntax to proper Unicode superscript characters,
 * and wraps ALL superscript characters in spans for CSS styling.
 * Also detects existing Unicode superscripts (², ³, etc.) from the backend.
 * 
 * Returns a React fragment with styled superscripts.
 */
export const formatUnitDisplay = (unit) => {
    if (!unit) return '';

    // Map of digits/chars to their superscript Unicode equivalents
    const superscriptMap = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '-': '⁻', '+': '⁺', '.': '·'
    };

    // Set of Unicode superscript characters to detect
    const superscriptChars = new Set(['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '⁻', '⁺']);

    // Convert exponent to superscript string
    const toSuperscript = (exp) => exp.split('').map(c => superscriptMap[c] || c).join('');

    // First, convert ^N and **N patterns to Unicode superscripts
    let processed = unit
        .replace(/\*\*(-?\d+\.?\d*)/g, (_, exp) => toSuperscript(exp))
        .replace(/\^(-?\d+\.?\d*)/g, (_, exp) => toSuperscript(exp));

    // Now split the processed string into parts: regular text and superscripts
    const parts = [];
    let currentText = '';
    let currentSuperscript = '';

    for (const char of processed) {
        if (superscriptChars.has(char)) {
            // Save any accumulated regular text
            if (currentText) {
                parts.push({ type: 'text', value: currentText });
                currentText = '';
            }
            currentSuperscript += char;
        } else {
            // Save any accumulated superscript
            if (currentSuperscript) {
                parts.push({ type: 'exp', value: currentSuperscript });
                currentSuperscript = '';
            }
            currentText += char;
        }
    }

    // Don't forget any remaining text or superscript
    if (currentText) {
        parts.push({ type: 'text', value: currentText });
    }
    if (currentSuperscript) {
        parts.push({ type: 'exp', value: currentSuperscript });
    }

    // If no parts or just one text part, return plain string
    if (parts.length === 0) {
        return processed;
    }
    if (parts.length === 1 && parts[0].type === 'text') {
        return parts[0].value;
    }

    // Return React elements
    return parts.map((part, i) =>
        part.type === 'exp'
            ? <span key={i} className="unit-exponent">{part.value}</span>
            : <span key={i}>{part.value}</span>
    );
};

// ============================================================================
// UNIT CONVERSION SYSTEM
// ============================================================================

/**
 * Unit conversion factors for frontend display unit changes.
 * Add new unit conversions here to support them across all editors.
 */
export const UNIT_CONVERSIONS = {
    'm': { 'cm': 100, 'mm': 1000, 'km': 0.001, 'in': 39.3701, 'ft': 3.28084, 'yd': 1.09361, 'mi': 0.000621371 },
    'cm': { 'm': 0.01, 'mm': 10, 'in': 0.393701, 'ft': 0.0328084 },
    'mm': { 'm': 0.001, 'cm': 0.1, 'in': 0.0393701 },
    'km': { 'm': 1000, 'mi': 0.621371 },
    'in': { 'm': 0.0254, 'cm': 2.54, 'mm': 25.4, 'ft': 0.0833333 },
    'ft': { 'm': 0.3048, 'cm': 30.48, 'in': 12, 'yd': 0.333333 },
    'kg': { 'g': 1000, 'mg': 1e6, 'lb': 2.20462, 'oz': 35.274 },
    'g': { 'kg': 0.001, 'mg': 1000, 'lb': 0.00220462 },
    'lb': { 'kg': 0.453592, 'g': 453.592, 'oz': 16 },
    's': { 'ms': 1000, 'min': 1 / 60, 'hr': 1 / 3600, 'h': 1 / 3600 },
    'min': { 's': 60, 'hr': 1 / 60, 'h': 1 / 60 },
    'hr': { 's': 3600, 'min': 60 },
    'h': { 's': 3600, 'min': 60 },
    'm/s': { 'km/h': 3.6, 'km/hr': 3.6, 'mph': 2.23694, 'ft/s': 3.28084 },
    'km/h': { 'm/s': 0.277778, 'mph': 0.621371 },
    'mph': { 'm/s': 0.44704, 'km/h': 1.60934 },
    'N': { 'kN': 0.001, 'lbf': 0.224809 },
    'kN': { 'N': 1000, 'lbf': 224.809 },
    'Pa': { 'kPa': 0.001, 'MPa': 1e-6, 'bar': 1e-5, 'psi': 0.000145038, 'atm': 9.86923e-6 },
    'kPa': { 'Pa': 1000, 'MPa': 0.001, 'bar': 0.01, 'psi': 0.145038 },
    'MPa': { 'Pa': 1e6, 'kPa': 1000, 'bar': 10, 'psi': 145.038 },
    'bar': { 'Pa': 1e5, 'kPa': 100, 'psi': 14.5038, 'atm': 0.986923 },
    'psi': { 'Pa': 6894.76, 'kPa': 6.89476, 'bar': 0.0689476 },
    'J': { 'kJ': 0.001, 'MJ': 1e-6, 'cal': 0.239006, 'kcal': 0.000239006, 'Wh': 0.000277778, 'kWh': 2.77778e-7, 'BTU': 0.000947817 },
    'kJ': { 'J': 1000, 'MJ': 0.001, 'kcal': 0.239006, 'kWh': 0.000277778 },
    'W': { 'kW': 0.001, 'MW': 1e-6, 'hp': 0.00134102 },
    'kW': { 'W': 1000, 'MW': 0.001, 'hp': 1.34102 },
    'm²': { 'cm²': 10000, 'mm²': 1e6, 'km²': 1e-6, 'ft²': 10.7639, 'in²': 1550 },
    'm^2': { 'cm^2': 10000, 'mm^2': 1e6, 'km^2': 1e-6, 'ft^2': 10.7639, 'in^2': 1550 },
    'm³': { 'L': 1000, 'mL': 1e6, 'cm³': 1e6, 'gal': 264.172, 'ft³': 35.3147 },
    'm^3': { 'L': 1000, 'mL': 1e6, 'cm^3': 1e6, 'gal': 264.172, 'ft^3': 35.3147 },
    'L': { 'm³': 0.001, 'mL': 1000, 'gal': 0.264172 },
    'rad': { 'deg': 57.2958, '°': 57.2958 },
    'deg': { 'rad': 0.0174533 },
    '°': { 'rad': 0.0174533 },
};

/**
 * Conversion cache for backend-fetched conversion factors.
 * Keys are `${fromUnit}->${toUnit}`, values are:
 *   - Success: { factor, displayUnit, timestamp, failed: false }
 *   - Failure: { failed: true, error, timestamp }
 * This cache persists across re-renders and is shared globally.
 */
const conversionCache = new Map();

/**
 * Get a cached conversion if available.
 * @param {string} fromUnit - Source unit
 * @param {string} toUnit - Target unit
 * @returns {object|null} - { factor, displayUnit, failed, error } if cached, null otherwise
 */
export const getCachedConversion = (fromUnit, toUnit) => {
    const key = `${fromUnit}->${toUnit}`;
    const cached = conversionCache.get(key);
    if (cached) {
        // Cache entries expire after 1 hour (optional, can be removed for permanent cache)
        if (Date.now() - cached.timestamp < 3600000) {
            return cached;
        }
        conversionCache.delete(key);
    }
    return null;
};

/**
 * Store a successful conversion factor in the cache.
 * @param {string} fromUnit - Source unit  
 * @param {string} toUnit - Target unit
 * @param {number} factor - Conversion factor
 * @param {string} displayUnit - Formatted display unit from backend
 */
export const setCachedConversion = (fromUnit, toUnit, factor, displayUnit) => {
    const key = `${fromUnit}->${toUnit}`;
    conversionCache.set(key, { factor, displayUnit, timestamp: Date.now(), failed: false });
};

/**
 * Store a failed conversion in the cache (incompatible dimensions).
 * @param {string} fromUnit - Source unit  
 * @param {string} toUnit - Target unit
 * @param {string} error - Error message from backend
 */
export const setCachedFailure = (fromUnit, toUnit, error) => {
    const key = `${fromUnit}->${toUnit}`;
    conversionCache.set(key, { failed: true, error, timestamp: Date.now() });
};

/**
 * Normalize a unit string for comparison and caching.
 * Converts Unicode superscripts to caret notation.
 */
const normalizeUnit = (u) => {
    if (!u) return '';
    return u.replace(/\s+/g, '')
        .replace(/²/g, '^2')
        .replace(/³/g, '^3')
        .replace(/⁰/g, '^0')
        .replace(/¹/g, '^1')
        .replace(/⁴/g, '^4')
        .replace(/⁵/g, '^5')
        .replace(/⁶/g, '^6')
        .replace(/⁷/g, '^7')
        .replace(/⁸/g, '^8')
        .replace(/⁹/g, '^9')
        .replace(/⁻/g, '-');
};

/**
 * Pre-fetch a unit conversion from the backend and cache it.
 * This should be called when a user sets a display unit.
 * Caches both successful conversions and failures for faster subsequent lookups.
 * @param {number} value - A sample value to convert (used to get factor)
 * @param {string} fromUnit - Source unit
 * @param {string} toUnit - Target unit
 * @param {function} onComplete - Callback when conversion is complete (triggers re-render)
 * @returns {Promise<{success: boolean, factor?: number, displayUnit?: string, error?: string, failed?: boolean}>}
 */
export const prefetchConversion = async (value, fromUnit, toUnit, onComplete = null) => {
    // Normalize units for consistent caching
    const from = normalizeUnit(fromUnit);
    const to = normalizeUnit(toUnit);

    // Check cache first (includes both successful and failed conversions)
    const cached = getCachedConversion(from, to);
    if (cached) {
        if (onComplete) onComplete();
        if (cached.failed) {
            return { success: false, failed: true, error: cached.error };
        }
        return { success: true, factor: cached.factor, displayUnit: cached.displayUnit };
    }

    // Try local conversion first
    const localResult = convertUnitLocal(value, fromUnit, toUnit);
    if (localResult.success) {
        const factor = value !== 0 ? localResult.value / value : 1;
        setCachedConversion(from, to, factor, toUnit);
        if (onComplete) onComplete();
        return { success: true, factor, displayUnit: toUnit };
    }

    // Fall back to backend - send normalized units
    const backendResult = await convertUnitViaBackend(value, from, to);
    if (backendResult.success) {
        setCachedConversion(from, to, backendResult.factor, backendResult.unit || toUnit);
        if (onComplete) onComplete();
        return { success: true, factor: backendResult.factor, displayUnit: backendResult.unit || toUnit };
    }

    // Cache the failure so we don't keep trying
    setCachedFailure(from, to, backendResult.error || 'Incompatible units');
    if (onComplete) onComplete();
    return { success: false, failed: true, error: backendResult.error };
};

/**
 * Convert a value using only local (synchronous) lookup table.
 */
const convertUnitLocal = (value, fromUnit, toUnit) => {
    if (!fromUnit || !toUnit || fromUnit === toUnit) {
        return { value, unit: toUnit || fromUnit, success: true };
    }

    // Use the shared normalizeUnit function
    const from = normalizeUnit(fromUnit);
    const to = normalizeUnit(toUnit);

    if (from === to) {
        return { value, unit: toUnit, success: true };
    }

    if (UNIT_CONVERSIONS[from] && UNIT_CONVERSIONS[from][to] !== undefined) {
        return { value: value * UNIT_CONVERSIONS[from][to], unit: toUnit, success: true };
    }

    if (UNIT_CONVERSIONS[to] && UNIT_CONVERSIONS[to][from] !== undefined) {
        return { value: value / UNIT_CONVERSIONS[to][from], unit: toUnit, success: true };
    }

    return { value, unit: fromUnit, success: false, error: `Cannot convert ${fromUnit} to ${toUnit}` };
};

/**
 * Convert a value from one unit to another.
 * First tries local lookup, then checks cache for backend conversions.
 * If conversion is not available, returns failure (caller should prefetch first).
 */
export const convertUnit = (value, fromUnit, toUnit) => {
    if (!fromUnit || !toUnit || fromUnit === toUnit) {
        return { value, unit: toUnit || fromUnit, success: true };
    }

    // Use the shared normalizeUnit function
    const from = normalizeUnit(fromUnit);
    const to = normalizeUnit(toUnit);

    if (from === to) {
        return { value, unit: toUnit, success: true };
    }

    // Try local lookup first
    if (UNIT_CONVERSIONS[from] && UNIT_CONVERSIONS[from][to] !== undefined) {
        return { value: value * UNIT_CONVERSIONS[from][to], unit: toUnit, success: true };
    }

    if (UNIT_CONVERSIONS[to] && UNIT_CONVERSIONS[to][from] !== undefined) {
        return { value: value / UNIT_CONVERSIONS[to][from], unit: toUnit, success: true };
    }

    // Check cache for backend conversions (includes both success and failure)
    const cached = getCachedConversion(from, to);
    if (cached) {
        if (cached.failed) {
            // Cached failure - this is a real dimension mismatch
            return { value, unit: fromUnit, success: false, failed: true, error: cached.error };
        }
        return { value: value * cached.factor, unit: cached.displayUnit || toUnit, success: true };
    }

    // Also check reverse direction in cache
    const cachedReverse = getCachedConversion(to, from);
    if (cachedReverse) {
        if (cachedReverse.failed) {
            return { value, unit: fromUnit, success: false, failed: true, error: cachedReverse.error };
        }
        return { value: value / cachedReverse.factor, unit: toUnit, success: true };
    }

    // Conversion not in cache yet - prefetch is in progress
    // Return needsPrefetch: true so caller knows this is NOT a confirmed mismatch
    return { value, unit: fromUnit, success: false, needsPrefetch: true };
};

/**
 * Compound unit suggestions by dimension family.
 * Each key is a pattern that matches units of that type.
 * Values are common alternative units in SI and Imperial.
 */
const COMPOUND_UNIT_SUGGESTIONS = {
    // Velocity: m/s, km/h, ft/s, mph, etc.
    velocity: {
        patterns: ['m/s', 'm/sec', 'km/h', 'km/hr', 'ft/s', 'ft/sec', 'mph', 'mi/h', 'in/s', 'cm/s'],
        suggestions: ['m/s', 'km/h', 'ft/s', 'mph', 'in/s']
    },
    // Density: kg/m^3, g/cm^3, lb/ft^3, etc.
    density: {
        patterns: ['kg/m^3', 'kg/m³', 'g/cm^3', 'g/cm³', 'g/mL', 'lb/ft^3', 'lb/ft³', 'lbm/ft^3', 'slug/ft^3'],
        suggestions: ['kg/m^3', 'g/cm^3', 'lbm/ft^3', 'g/mL']
    },
    // Mass flow: kg/s, lb/s, g/min, etc.
    massFlow: {
        patterns: ['kg/s', 'kg/min', 'kg/h', 'kg/hr', 'g/s', 'g/min', 'lb/s', 'lbm/s', 'lb/min', 'lb/h', 'lb/hr'],
        suggestions: ['kg/s', 'kg/h', 'lbm/s', 'g/min']
    },
    // Volume flow: m^3/s, L/min, gal/min, etc.
    volumeFlow: {
        patterns: ['m^3/s', 'm³/s', 'L/s', 'L/min', 'mL/s', 'ft^3/s', 'ft³/s', 'gal/min', 'gpm', 'cfm'],
        suggestions: ['m^3/s', 'L/min', 'gal/min', 'ft^3/s']
    },
    // Specific heat: J/(kg·K), kJ/(kg·K), BTU/(lb·R), etc.
    specificHeat: {
        patterns: ['J/(kg*K)', 'J/(kg·K)', 'kJ/(kg*K)', 'kJ/(kg·K)', 'BTU/(lb*R)', 'BTU/(lbm*R)', 'cal/(g*K)'],
        suggestions: ['J/(kg*K)', 'kJ/(kg*K)', 'BTU/(lbm*R)']
    },
    // Thermal conductivity: W/(m·K), BTU/(h·ft·R), etc.
    thermalConductivity: {
        patterns: ['W/(m*K)', 'W/(m·K)', 'W/m/K', 'BTU/(h*ft*R)', 'BTU/(hr*ft*R)'],
        suggestions: ['W/(m*K)', 'BTU/(hr*ft*R)']
    },
    // Dynamic viscosity: Pa·s, kg/(m·s), lb/(ft·s), etc.
    dynamicViscosity: {
        patterns: ['Pa*s', 'Pa·s', 'kg/(m*s)', 'N*s/m^2', 'lb/(ft*s)', 'lbf*s/ft^2', 'poise', 'cP', 'centipoise'],
        suggestions: ['Pa*s', 'cP', 'lb/(ft*s)']
    },
    // Kinematic viscosity: m^2/s, ft^2/s, etc.
    kinematicViscosity: {
        patterns: ['m^2/s', 'm²/s', 'ft^2/s', 'ft²/s', 'stokes', 'cSt', 'centistokes'],
        suggestions: ['m^2/s', 'cSt', 'ft^2/s']
    },
    // Pressure (already in lookup but add variations)
    pressure: {
        patterns: ['N/m^2', 'N/m²', 'kN/m^2', 'lbf/in^2', 'lbf/ft^2'],
        suggestions: ['Pa', 'kPa', 'bar', 'psi', 'atm']
    },
    // Energy per volume: J/m^3, etc.
    energyDensity: {
        patterns: ['J/m^3', 'J/m³', 'kJ/m^3', 'BTU/ft^3'],
        suggestions: ['J/m^3', 'kJ/m^3', 'BTU/ft^3']
    },
    // Acceleration: m/s^2, ft/s^2, g, etc.
    acceleration: {
        patterns: ['m/s^2', 'm/s²', 'ft/s^2', 'ft/s²', 'in/s^2', 'cm/s^2'],
        suggestions: ['m/s^2', 'ft/s^2', 'in/s^2']
    }
};

/**
 * Get suggested units for a given unit (for quick select in modal).
 * Includes both simple unit conversions from lookup table and 
 * compound unit suggestions based on dimension families.
 */
export const getSuggestedUnits = (currentUnit) => {
    if (!currentUnit) return [];
    const normalized = normalizeUnit(currentUnit);

    // First try exact match in local conversion table
    const suggestions = UNIT_CONVERSIONS[normalized];
    if (suggestions) {
        return Object.keys(suggestions);
    }

    // Check if this unit is a target of any conversion
    for (const [baseUnit, targets] of Object.entries(UNIT_CONVERSIONS)) {
        if (targets[normalized] !== undefined) {
            return [baseUnit, ...Object.keys(targets).filter(u => u !== normalized)];
        }
    }

    // Try compound unit suggestions based on pattern matching
    for (const [, config] of Object.entries(COMPOUND_UNIT_SUGGESTIONS)) {
        const matches = config.patterns.some(pattern => {
            const normalizedPattern = normalizeUnit(pattern);
            return normalized === normalizedPattern;
        });
        if (matches) {
            // Return suggestions excluding the current unit
            return config.suggestions.filter(u => normalizeUnit(u) !== normalized);
        }
    }

    return [];
};

// ============================================================================
// MODAL COMPONENTS
// ============================================================================

/**
 * Unit Input Modal Component
 * Used for changing display units on result cards.
 * Fetches compatible unit suggestions from backend via dimensional analysis.
 * 
 * Props:
 * - unitSource: Optional 'explicit', 'propagated', or 'inferred' - if propagated/inferred, shows confirm checkbox
 * - onConfirm: Called with (newUnit, shouldConfirm) - second arg indicates if user checked confirm box
 */
export const UnitInputModal = ({ isOpen, variable, currentUnit, originalUnit, unitSource, onConfirm, onCancel }) => {
    const [inputValue, setInputValue] = useState('');
    const [confirmChecked, setConfirmChecked] = useState(false);
    const [suggestedUnits, setSuggestedUnits] = useState([]);
    const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
    const inputRef = useRef(null);

    // Show confirm checkbox for non-explicit units
    const showConfirmCheckbox = unitSource && unitSource !== 'explicit';

    useEffect(() => {
        if (isOpen) {
            setInputValue(currentUnit || '');
            setConfirmChecked(false);  // Reset checkbox each time modal opens

            // Fetch suggestions from backend
            const fetchSuggestions = async () => {
                if (!originalUnit) {
                    setSuggestedUnits([]);
                    return;
                }

                setIsLoadingSuggestions(true);
                try {
                    // Import dynamically to avoid circular dependencies
                    const { getUnitSuggestions } = await import('./api');
                    const result = await getUnitSuggestions(originalUnit);
                    if (result.success && result.suggestions) {
                        setSuggestedUnits(result.suggestions);
                    } else {
                        // Fallback to local suggestions
                        setSuggestedUnits(getSuggestedUnits(originalUnit));
                    }
                } catch (error) {
                    // Fallback to local suggestions
                    setSuggestedUnits(getSuggestedUnits(originalUnit));
                } finally {
                    setIsLoadingSuggestions(false);
                }
            };

            fetchSuggestions();

            setTimeout(() => {
                if (inputRef.current) {
                    inputRef.current.focus();
                    inputRef.current.select();
                }
            }, 50);
        }
    }, [isOpen, currentUnit, originalUnit]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onConfirm(inputValue.trim(), confirmChecked);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
            onCancel();
        }
    };

    if (!isOpen) return null;

    return createPortal(
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Set Display Unit</h3>
                    <button className="modal-close" onClick={onCancel}>×</button>
                </div>
                <div className="modal-body">
                    <p className="modal-description">
                        Enter the display unit for <strong>{variable}</strong>
                    </p>
                    <p className="modal-current">
                        Current: <span className="unit-badge-inline" style={{ '--unit-hue': getUnitHue(originalUnit) }}>{formatUnitDisplay(originalUnit || 'dimensionless')}</span>
                        {showConfirmCheckbox && <span className="unit-source-badge">{unitSource}</span>}
                    </p>
                    <form onSubmit={handleSubmit}>
                        <input
                            ref={inputRef}
                            type="text"
                            className="modal-input"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="e.g., cm, ft, kPa..."
                        />
                    </form>
                    {suggestedUnits.length > 0 && (
                        <div className="modal-suggestions">
                            <span className="suggestions-label">Quick select:</span>
                            <div className="suggestions-list">
                                {suggestedUnits.slice(0, 6).map((unit) => (
                                    <button
                                        key={unit}
                                        type="button"
                                        className="suggestion-chip"
                                        onClick={() => {
                                            setInputValue(unit);
                                            onConfirm(unit, true);  // Quick select implies confirmation
                                        }}
                                    >
                                        {unit}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                    {showConfirmCheckbox && (
                        <label className="modal-confirm-checkbox">
                            <input
                                type="checkbox"
                                checked={confirmChecked}
                                onChange={(e) => setConfirmChecked(e.target.checked)}
                            />
                            <span>Confirm propagated units match expected dimensions</span>
                        </label>
                    )}
                </div>
                <div className="modal-footer">
                    <button className="modal-btn modal-btn-secondary" onClick={onCancel}>
                        Cancel
                    </button>
                    <button className="modal-btn modal-btn-primary" onClick={() => onConfirm(inputValue.trim(), confirmChecked)}>
                        Apply
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
};

// ============================================================================
// CONTEXT MENU COMPONENT
// ============================================================================

/**
 * Context Menu Component for result cards
 * Provides right-click options for key variables and unit display
 */
export const ResultContextMenu = ({
    contextMenu,
    contextMenuRef,
    keyVariables,
    displayUnits,
    results,
    isUnitConfirmed,
    onToggleKeyVariable,
    onOpenUnitModal,
    onResetUnit,
    onConfirmUnit,
    onClose
}) => {
    if (!contextMenu) return null;

    // Check if this variable's unit needs confirmation
    const variableData = results?.[contextMenu.variable];
    const unitSource = variableData?.unit_source || 'propagated';
    const hasUnit = !!variableData?.unit;
    // Pass currentUnit to isUnitConfirmed
    const needsConfirmation = hasUnit && !isUnitConfirmed?.(contextMenu.variable, unitSource, contextMenu.currentUnit);

    return createPortal(
        <div
            ref={contextMenuRef}
            className="context-menu"
            style={{
                position: 'fixed',
                top: contextMenu.y,
                left: contextMenu.x,
                zIndex: 9999
            }}
        >
            <div
                className="context-menu-item"
                onClick={() => onToggleKeyVariable(contextMenu.variable)}
            >
                <span className="menu-icon">{keyVariables.includes(contextMenu.variable) ? '−' : '+'}</span>
                {keyVariables.includes(contextMenu.variable) ? 'Remove from Key Variables' : 'Add to Key Variables'}
            </div>
            {needsConfirmation && (
                <div
                    className="context-menu-item confirm-unit-item"
                    onClick={() => onConfirmUnit(contextMenu.variable, contextMenu.currentUnit)}
                >
                    <span className="menu-icon">✓</span>
                    Confirm Unit
                </div>
            )}
            <div
                className="context-menu-item"
                onClick={() => onOpenUnitModal(contextMenu.variable)}
            >
                <span className="menu-icon">⇄</span>
                Set Display Unit...
            </div>
            {displayUnits[contextMenu.variable] && (
                <div
                    className="context-menu-item"
                    onClick={() => onResetUnit(contextMenu.variable)}
                >
                    <span className="menu-icon">↺</span>
                    Reset to Original Unit
                </div>
            )}
        </div>,
        document.body
    );
};

// ============================================================================
// RESULT CARD COMPONENT
// ============================================================================

/**
 * Result Card Component
 * Renders a single variable result with optional unit badge and context menu support
 */
export const ResultCard = ({
    variable,
    originalData,
    displayUnits = {},
    isKey = false,
    onContextMenu,
    onConfirmUnit, // NEW: Handler for clicking unconfirmed badge
    isUnitConfirmed,
    className = ''
}) => {
    const getDisplayData = () => {
        const targetUnit = displayUnits[variable];
        if (!targetUnit) {
            return originalData;
        }

        const converted = convertUnit(originalData.value, originalData.unit, targetUnit);
        let warning = null;
        let isPending = false;

        // Check for mismatches - but only show warning for confirmed failures
        if (!originalData.unit && targetUnit) {
            // Trying to apply unit to dimensionless result
            warning = `Mismatch: Calculated (Dimensionless) vs Display (${targetUnit})`;
        } else if (!converted.success) {
            if (converted.failed) {
                // Confirmed failure from cache - this is a real dimension mismatch
                warning = `Mismatch: Calculated (${originalData.unit}) vs Display (${targetUnit})`;
            } else if (converted.needsPrefetch) {
                // Conversion is pending - don't show warning yet
                // The prefetch will complete and trigger a re-render
                isPending = true;
            }
        }

        return {
            value: converted.success ? converted.value : originalData.value,
            unit: converted.success ? converted.unit : targetUnit,
            warning,
            isPending
        };
    };

    const displayData = getDisplayData();
    const hasOverride = displayUnits[variable] && displayUnits[variable] !== originalData.unit;

    // Determine if unit is confirmed
    const unitSource = originalData?.unit_source || 'propagated';
    const hasUnit = !!displayData.unit;
    // Check confirmation against the displayed unit
    const confirmed = hasUnit && isUnitConfirmed?.(variable, unitSource, displayData.unit);
    const showUnconfirmed = hasUnit && !confirmed;

    return (
        <div
            className={`result-card ${isKey ? 'key-variable-card' : ''} ${hasOverride ? 'unit-override' : ''} ${displayData.warning ? 'unit-mismatch' : ''} ${className}`}
            onContextMenu={(e) => onContextMenu && onContextMenu(e, variable, originalData.unit)}
        >
            <span className="var-name">{variable}</span>
            <span className="equals">=</span>
            <span className="var-value">
                {typeof displayData.value === 'number'
                    ? formatNumber(displayData.value)
                    : displayData.value}
            </span>
            {displayData.unit && (
                <span
                    className={`unit-badge ${showUnconfirmed ? 'unit-unconfirmed' : 'unit-confirmed'}`}
                    style={{ '--unit-hue': getUnitHue(displayData.unit) }}
                    title={displayData.warning || (showUnconfirmed ? 'Unconfirmed: Right-click or Click to confirm unit' : (hasOverride ? `Original: ${originalData.value.toPrecision(4)} ${originalData.unit || 'dimensionless'}` : displayData.unit))}
                    onContextMenu={(e) => onContextMenu(e, variable, displayData.unit)}
                    onClick={(e) => {
                        if (showUnconfirmed && onConfirmUnit) {
                            e.stopPropagation();
                            onConfirmUnit(variable, displayData.unit);
                        }
                    }}
                >
                    {displayData.warning && <span className="mismatch-icon">⚠️ </span>}
                    {showUnconfirmed && <span className="unconfirmed-icon"></span>}
                    {formatUnitDisplay(displayData.unit)}
                </span>
            )}
        </div>
    );
};

// ============================================================================
// HOOKS FOR EDITOR FUNCTIONALITY
// ============================================================================

/**
 * Custom hook for managing context menu state
 */
export const useContextMenu = () => {
    const [contextMenu, setContextMenu] = useState(null);
    const contextMenuRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (contextMenuRef.current && !contextMenuRef.current.contains(event.target)) {
                setContextMenu(null);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const openContextMenu = (e, variable, currentUnit) => {
        e.preventDefault();
        e.stopPropagation();
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            variable,
            currentUnit
        });
    };

    const closeContextMenu = () => setContextMenu(null);

    return { contextMenu, contextMenuRef, openContextMenu, closeContextMenu };
};

/**
 * Custom hook for managing key variables
 */
export const useKeyVariables = () => {
    const [keyVariables, setKeyVariables] = useState([]);

    const toggleKeyVariable = (variable) => {
        setKeyVariables(prev =>
            prev.includes(variable)
                ? prev.filter(v => v !== variable)
                : [...prev, variable]
        );
    };

    return { keyVariables, toggleKeyVariable };
};

/**
 * Custom hook for managing display unit overrides with backend prefetch support.
 * When a display unit is set, it triggers a prefetch to cache the conversion factor.
 */
export const useDisplayUnits = () => {
    const [displayUnits, setDisplayUnits] = useState({});
    // Counter to trigger re-renders when conversions complete
    const [conversionReady, setConversionReady] = useState(0);

    /**
     * Set a display unit for a variable.
     * Triggers async prefetch of conversion factor if needed.
     * @param {string} variable - The variable name
     * @param {string} newUnit - The new display unit
     * @param {string} originalUnit - The original calculated unit
     * @param {number} sampleValue - Optional sample value to use for prefetch (default 1)
     */
    const setDisplayUnit = (variable, newUnit, originalUnit, sampleValue = 1) => {
        if (newUnit === '' || newUnit === originalUnit) {
            // Clear override
            setDisplayUnits(prev => {
                const next = { ...prev };
                delete next[variable];
                return next;
            });
        } else {
            // Set the display unit immediately
            setDisplayUnits(prev => ({
                ...prev,
                [variable]: newUnit
            }));

            // Prefetch the conversion factor from backend if needed
            // This will cache the factor for instant use on subsequent renders
            if (originalUnit && newUnit !== originalUnit) {
                prefetchConversion(sampleValue, originalUnit, newUnit, () => {
                    // Trigger a re-render when conversion is ready
                    setConversionReady(prev => prev + 1);
                });
            }
        }
    };

    const resetDisplayUnit = (variable) => {
        setDisplayUnits(prev => {
            const next = { ...prev };
            delete next[variable];
            return next;
        });
    };

    return { displayUnits, setDisplayUnit, resetDisplayUnit, conversionReady };
};

/**
 * Custom hook for managing unit confirmation state.
 * Units must be confirmed by the user to be considered "validated".
 * 
 * Confirmation happens when:
 * - Unit source is 'explicit' (defined in equation with [unit])
 * - User manually confirms via context menu or checkbox in modal
 * - User sets a display unit (which implicitly confirms they reviewed the unit)
 * 
 * Confirmation persists as long as the variable name and the unit string remain the same.
 * It does NOT reset automatically when equations change, unless the unit itself changes.
 * 
 * NEW: Supports optional persistence via initialConfirmedUnits and onConfirmedUnitsChange.
 * When logged in, confirmed units can be saved to the user's preferences on the server.
 */
export const useConfirmedUnits = (results, initialConfirmedUnits = {}, onConfirmedUnitsChange = null) => {
    // Store confirmed units as { variableName: "unitString" }
    // We confirm a specific UNIT string for a variable.
    const [confirmedUnits, setConfirmedUnits] = useState(initialConfirmedUnits);

    // Track if we've initialized from server data
    const [initialized, setInitialized] = useState(false);

    // Update from initial data when it changes (e.g., user logs in)
    useEffect(() => {
        if (Object.keys(initialConfirmedUnits).length > 0 && !initialized) {
            setConfirmedUnits(prev => ({ ...initialConfirmedUnits, ...prev }));
            setInitialized(true);
        }
    }, [initialConfirmedUnits, initialized]);

    // Prune confirmations for variables that no longer exist in successful results
    useEffect(() => {
        if (results && typeof results === 'object') {
            const currentVars = new Set(Object.keys(results));
            setConfirmedUnits(prev => {
                const next = { ...prev };
                let changed = false;
                Object.keys(next).forEach(variable => {
                    if (!currentVars.has(variable)) {
                        delete next[variable];
                        changed = true;
                    }
                });
                return changed ? next : prev;
            });
        }
    }, [results]);

    // Notify parent when confirmed units change (for server persistence)
    useEffect(() => {
        if (onConfirmedUnitsChange && initialized) {
            onConfirmedUnitsChange(confirmedUnits);
        }
    }, [confirmedUnits, onConfirmedUnitsChange, initialized]);

    const confirmUnit = (variable, unit) => {
        if (!variable || !unit) return;
        setConfirmedUnits(prev => ({ ...prev, [variable]: unit }));
    };

    const unconfirmUnit = (variable) => {
        setConfirmedUnits(prev => {
            const next = { ...prev };
            delete next[variable];
            return next;
        });
    };

    /**
     * Check if a unit is confirmed.
     * @param {string} variable - The variable name
     * @param {string} unitSource - The unit source from backend ('explicit', 'inferred', 'propagated')
     * @param {string} currentUnit - The logical unit being displayed/calculated (e.g. "kg*m/s^2")
     * @returns {boolean} True if the unit is considered confirmed
     */
    const isUnitConfirmed = (variable, unitSource, currentUnit) => {
        // Explicit units (user-defined in equation) are always confirmed
        if (unitSource === 'explicit') return true;

        // Otherwise, check if user manually confirmed THIS specific unit
        // If the calculated unit changes (e.g. from 'm' to 'm^2'), 
        // the previous confirmation for 'm' will implicitly be invalid.
        return confirmedUnits[variable] === currentUnit;
    };

    return { confirmedUnits, confirmUnit, unconfirmUnit, isUnitConfirmed, setConfirmedUnits };
};

/**
 * Custom hook for managing unit input modal state
 */
export const useUnitModal = (results, displayUnits, onUnitChange) => {
    const [unitModal, setUnitModal] = useState({
        isOpen: false,
        variable: null,
        currentUnit: '',
        originalUnit: '',
        unitSource: 'propagated'
    });

    const openUnitModal = (variable) => {
        const varData = results?.[variable];
        const originalUnit = varData?.unit || '';
        const unitSource = varData?.unit_source || 'propagated';
        const currentDisplayUnit = displayUnits[variable] || originalUnit || '';
        setUnitModal({
            isOpen: true,
            variable,
            currentUnit: currentDisplayUnit,
            originalUnit,
            unitSource
        });
    };

    const handleConfirm = (newUnit, shouldConfirm = false) => {
        const { variable, originalUnit } = unitModal;
        onUnitChange(variable, newUnit, originalUnit, shouldConfirm);
        setUnitModal({ isOpen: false, variable: null, currentUnit: '', originalUnit: '', unitSource: 'propagated' });
    };

    const handleCancel = () => {
        setUnitModal({ isOpen: false, variable: null, currentUnit: '', originalUnit: '', unitSource: 'propagated' });
    };

    return { unitModal, openUnitModal, handleConfirm, handleCancel };
};

/**
 * Custom hook that encapsulates ALL equation editor logic.
 * Used by both the main EquationEditor and MiniEquationEditor to ensure 100% feature parity.
 */
export const useEquationEditorState = (initialEquations, onValueChange = null) => {
    const [equations, setEquations] = useState(initialEquations || '');
    const [results, setResults] = useState(null);
    const [isRunning, setIsRunning] = useState(false);
    const [error, setError] = useState(null);
    const [unitWarnings, setUnitWarnings] = useState([]);
    const [angleUnit, setAngleUnit] = useState('deg');
    const [arrayMode, setArrayMode] = useState('parallel');  // NEW: 'parallel' or 'grid'
    const [isArraySolve, setIsArraySolve] = useState(false);  // NEW: flag for array results
    const [plots, setPlots] = useState(null);  // NEW: Plotly configurations

    // Shared sub-hooks
    const { contextMenu, contextMenuRef, openContextMenu, closeContextMenu } = useContextMenu();
    const { keyVariables, toggleKeyVariable } = useKeyVariables();
    const { displayUnits, setDisplayUnit, resetDisplayUnit } = useDisplayUnits();

    // Use global confirmed units context for persistence
    const globalConfirmedUnits = useConfirmedUnitsContext();
    const { confirmedUnits, confirmUnit, unconfirmUnit, isUnitConfirmed, pruneConfirmations } = globalConfirmedUnits;

    // Prune confirmations when results change (remove variables that no longer exist)
    useEffect(() => {
        if (results && typeof results === 'object' && pruneConfirmations) {
            pruneConfirmations(Object.keys(results));
        }
    }, [results, pruneConfirmations]);

    // Wire up modal confirm to updated persistence logic
    const { unitModal, openUnitModal, handleConfirm: handleUnitModalConfirm, handleCancel: handleUnitModalCancel } = useUnitModal(results, displayUnits, (variable, newUnit, originalUnit, shouldConfirm) => {
        setDisplayUnit(variable, newUnit, originalUnit);

        // Confirm unit logic:
        // 1. If user sets a NEW display unit, that new unit is implicitly confirmed.
        // 2. If user checks "Confirm" box (shouldConfirm=true), we confirm the ORIGINAL unit (since they are confirming the propagated one).
        if (newUnit) {
            confirmUnit(variable, newUnit);
        } else if (shouldConfirm) {
            confirmUnit(variable, originalUnit);
        }
    });

    const handleTextChange = (newVal) => {
        setEquations(newVal);
        if (onValueChange) onValueChange(newVal);
    };

    const handleRun = async () => {
        setIsRunning(true);
        setError(null);
        setResults(null);
        setPlots(null);  // NEW: Clear plots
        setUnitWarnings([]);

        try {
            const data = await solveEquations(equations, angleUnit, null, arrayMode);

            if (data.results) {
                setResults(data.results);
                setIsArraySolve(data.is_array_solve || false);  // NEW
                setPlots(data.plots || null);  // NEW: Store plot configs

                if (data.unit_warnings && data.unit_warnings.length > 0) {
                    setUnitWarnings(data.unit_warnings);
                } else {
                    setUnitWarnings([]); // Clear if no warnings
                }
            } else if (data.error) {
                setError(data.error);
                setResults(null);
                setIsArraySolve(false);
                setPlots(null);
            } else {
                // Fallback for unexpected response structure
                setError(JSON.stringify(data, null, 2));
                setResults(null);
                setIsArraySolve(false);
                setPlots(null);
            }
        } catch (err) {
            setError(err.message);
            setResults(null);
            setIsArraySolve(false);
            setPlots(null);
        } finally {
            setIsRunning(false);
        }
    };

    // Context menu handlers
    const handleContextMenu = (e, variable, currentUnit) => {
        openContextMenu(e, variable, currentUnit);
    };

    const handleToggleKeyVariable = (variable) => {
        toggleKeyVariable(variable);
        closeContextMenu();
    };

    const handleOpenUnitModal = (variable) => {
        openUnitModal(variable);
        closeContextMenu();
    };

    const handleResetUnit = (variable) => {
        resetDisplayUnit(variable);
        closeContextMenu();
    };

    // Handler for confirming a unit via context menu
    const handleConfirmUnit = (variable, unit) => {
        confirmUnit(variable, unit);
        closeContextMenu();
    };

    return {
        equations,
        setEquations,
        handleTextChange,
        results,
        isRunning,
        error,
        unitWarnings,
        angleUnit,
        setAngleUnit,
        arrayMode,      // NEW
        setArrayMode,   // NEW
        isArraySolve,   // NEW
        plots,          // NEW
        handleRun,
        // Context menu & Unit state
        contextMenu,
        contextMenuRef,
        keyVariables,
        displayUnits,
        unitModal,
        // Handlers
        handleContextMenu,
        handleToggleKeyVariable,
        handleOpenUnitModal,
        handleResetUnit,
        handleConfirmUnit,  // NEW: for confirming units via context menu
        handleUnitModalConfirm,
        handleUnitModalCancel,
        closeContextMenu,
        // Unit confirmation state
        confirmedUnits,
        confirmUnit,
        isUnitConfirmed
    };
};


// ============================================================================
// ARRAY RESULTS TABLE COMPONENT
// ============================================================================

/**
 * ArrayResultsTable - Display array results in a collapsible table format
 * 
 * Groups all array variables into a single table with:
 * - "Index" column + one column per array variable
 * - Column headers: "variable [unit]" format, center-justified
 * - Each row = one array index with values across all variables
 * - Collapsible with expand/collapse toggle
 * - Right-click on any cell opens context menu for that variable
 * 
 * Props:
 * - arrayResults: { varName: { value: [...], unit: "m", is_array: true, ... }, ... }
 * - displayUnits: { varName: "cm", ... } - unit overrides
 * - handleContextMenu: (e, variable, originalUnit) => void
 * - isUnitConfirmed: (variable, unitSource) => boolean
 * - isCollapsed: boolean
 * - onToggleCollapse: () => void
 * - title: string - section title (e.g., "Key Variables" or "Array Results")
 * - isKeySection: boolean - if true, uses key variable styling
 */
export const ArrayResultsTable = ({
    arrayResults,
    displayUnits = {},
    handleContextMenu,
    onConfirmUnit, // NEW
    isUnitConfirmed,
    isCollapsed = false,
    onToggleCollapse,
    title = "Array Results",
    isKeySection = false
}) => {
    // Get all variable names from the results
    const variables = Object.keys(arrayResults);
    if (variables.length === 0) return null;

    // Get array length from first variable
    const firstVar = variables[0];
    const arrayLength = Array.isArray(arrayResults[firstVar]?.value)
        ? arrayResults[firstVar].value.length
        : 0;

    if (arrayLength === 0) return null;

    // Helper to get display value and unit for a variable
    const getDisplayData = (variable, originalData) => {
        const targetUnit = displayUnits[variable];
        if (!targetUnit) {
            return { value: originalData.value, unit: originalData.unit };
        }

        const converted = convertUnit(originalData.value, originalData.unit, targetUnit);
        return {
            value: converted.value,
            unit: targetUnit
        };
    };

    // Get header info for each variable
    const headerInfo = variables.map(varName => {
        const data = arrayResults[varName];
        const displayData = getDisplayData(varName, data);
        const unitSource = data?.unit_source || 'propagated';
        // Check confirmation against the displayed unit, NOT just variable name
        const confirmed = displayData.unit && isUnitConfirmed?.(varName, unitSource, displayData.unit);
        const showUnconfirmed = displayData.unit && !confirmed;

        return {
            varName,
            unit: displayData.unit,
            showUnconfirmed,
            unitSource,
            originalUnit: data.unit
        };
    });

    return (
        <div className={`array-table-container ${isKeySection ? 'key-section' : ''}`}>
            <div
                className="array-table-header"
                onClick={onToggleCollapse}
            >
                <span className="array-table-title">
                    {isKeySection ? '⭐ ' : '📊 '}{title}
                    <span className="array-count-badge">{arrayLength} values</span>
                </span>
                <button
                    className="array-table-toggle"
                    onClick={(e) => { e.stopPropagation(); onToggleCollapse(); }}
                >
                    {isCollapsed ? '▶ Show' : '▼ Hide'}
                </button>
            </div>

            {!isCollapsed && (
                <div className="array-table-wrapper">
                    <table className="array-results-table">
                        <thead>
                            <tr>
                                <th className="index-column">Index</th>
                                {headerInfo.map(({ varName, unit, showUnconfirmed }) => (
                                    <th
                                        key={varName}
                                        className="variable-column"
                                        onContextMenu={(e) => handleContextMenu(e, varName, arrayResults[varName]?.unit)}
                                    >
                                        <span className="var-header-name">{varName}</span>
                                        {unit && (
                                            <span
                                                className={`unit-badge ${showUnconfirmed ? 'unit-unconfirmed' : 'unit-confirmed'}`}
                                                style={{ '--unit-hue': getUnitHue(unit) }}
                                                title={showUnconfirmed ? 'Unconfirmed: Right-click or Click to confirm unit' : unit}
                                                onClick={(e) => {
                                                    if (showUnconfirmed && onConfirmUnit) {
                                                        e.stopPropagation();
                                                        onConfirmUnit(varName, unit);
                                                    }
                                                }}
                                            >
                                                {showUnconfirmed && <span className="unconfirmed-icon"></span>}
                                                {formatUnitDisplay(unit)}
                                            </span>
                                        )}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {Array.from({ length: arrayLength }, (_, rowIdx) => (
                                <tr key={rowIdx}>
                                    <td className="index-cell">{rowIdx}</td>
                                    {variables.map(varName => {
                                        const data = arrayResults[varName];
                                        const values = data?.value;
                                        const rawValue = Array.isArray(values) ? values[rowIdx] : values;

                                        // Apply unit conversion if display unit is set
                                        let displayValue = rawValue;
                                        const targetUnit = displayUnits[varName];
                                        if (targetUnit && data.unit) {
                                            const converted = convertUnit(rawValue, data.unit, targetUnit);
                                            if (converted.success) {
                                                displayValue = converted.value;
                                            }
                                        }

                                        return (
                                            <td
                                                key={varName}
                                                className="value-cell"
                                                onContextMenu={(e) => handleContextMenu(e, varName, data?.unit)}
                                            >
                                                {typeof displayValue === 'number'
                                                    ? formatNumber(displayValue, 5)
                                                    : displayValue}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

// ============================================================================
// MINI EDITOR COMPONENT
// ============================================================================


/**
 * MiniPlotPanel - Full plot rendering for mini editors
 * 
 * Uses dynamic import to load react-plotly.js, matching the main editor's PlotPanel behavior.
 * This ensures feature parity between main and mini editors for equation plotting.
 */
const MiniPlotPanel = ({ plots }) => {
    const [Plot, setPlot] = useState(null);
    const [loadError, setLoadError] = useState(null);
    const [expandedPlot, setExpandedPlot] = useState(null);

    // Dynamically load plotly
    useEffect(() => {
        import('react-plotly.js')
            .then(module => {
                setPlot(() => module.default);
            })
            .catch(err => {
                console.error('Failed to load react-plotly.js:', err);
                setLoadError('Plotly not installed. Run: npm install');
            });
    }, []);

    if (!plots || plots.length === 0) return null;

    // Show error state if Plotly failed to load
    if (loadError) {
        return (
            <div className="mini-plot-panel">
                <div className="mini-plot-header">
                    <h4>📊 Plots</h4>
                </div>
                <div className="mini-plot-error">
                    <p>📊 Plotting requires additional dependencies.</p>
                    <p>Run: <code>cd frontend && npm install</code></p>
                </div>
            </div>
        );
    }

    // Show loading state while Plotly loads
    if (!Plot) {
        return (
            <div className="mini-plot-panel">
                <div className="mini-plot-header">
                    <h4>📊 Plots</h4>
                </div>
                <div className="mini-plot-loading">
                    <p>Loading plot library...</p>
                </div>
            </div>
        );
    }

    const handlePlotClick = (idx) => {
        setExpandedPlot(expandedPlot === idx ? null : idx);
    };

    // Detect current theme and create deep merge function for proper axis title preservation
    const isDarkMode = document.documentElement.getAttribute('data-theme') !== 'light';

    const mergeLayouts = (baseLayout, isDark) => {
        const colors = isDark ? {
            paper: 'rgba(30, 30, 30, 0.95)', plot: 'rgba(30, 30, 30, 0.95)',
            text: '#e4e4e7', grid: 'rgba(255,255,255,0.1)', zero: 'rgba(255,255,255,0.2)',
            tick: '#a1a1aa', legendBg: 'rgba(45, 45, 48, 0.9)'
        } : {
            paper: 'rgba(255, 255, 255, 0.98)', plot: 'rgba(255, 255, 255, 0.98)',
            text: '#000000', grid: 'rgba(0,0,0,0.1)', zero: 'rgba(0,0,0,0.2)',
            tick: '#18181b', legendBg: 'rgba(255, 255, 255, 0.95)'
        };
        const result = { ...baseLayout };
        result.paper_bgcolor = colors.paper;
        result.plot_bgcolor = colors.plot;
        result.font = { ...(baseLayout.font || {}), color: colors.text, size: 12 };
        if (baseLayout.title) {
            const titleText = typeof baseLayout.title === 'string' ? baseLayout.title : baseLayout.title?.text;
            result.title = { text: titleText, font: { color: colors.text, size: 14 } };
        }
        result.legend = { ...(baseLayout.legend || {}), bgcolor: colors.legendBg, font: { color: colors.text } };
        if (baseLayout.xaxis) {
            const xTitle = typeof baseLayout.xaxis.title === 'string' ? baseLayout.xaxis.title : baseLayout.xaxis.title?.text;
            result.xaxis = {
                ...baseLayout.xaxis, gridcolor: colors.grid, zerolinecolor: colors.zero,
                tickfont: { ...(baseLayout.xaxis.tickfont || {}), color: colors.tick },
                title: xTitle ? { text: xTitle, font: { color: colors.text } } : undefined
            };
        }
        if (baseLayout.yaxis) {
            const yTitle = typeof baseLayout.yaxis.title === 'string' ? baseLayout.yaxis.title : baseLayout.yaxis.title?.text;
            result.yaxis = {
                ...baseLayout.yaxis, gridcolor: colors.grid, zerolinecolor: colors.zero,
                tickfont: { ...(baseLayout.yaxis.tickfont || {}), color: colors.tick },
                title: yTitle ? { text: yTitle, font: { color: colors.text } } : undefined
            };
        }
        result.autosize = true;
        result.margin = { t: 70, r: 20, b: 70, l: 60 };
        return result;
    };

    // Render the actual plots using Plotly
    return (
        <div className="mini-plot-panel">
            <div className="mini-plot-header">
                <h4>📊 Plots</h4>
                <span className="plot-count">{plots.length} plot{plots.length > 1 ? 's' : ''}</span>
            </div>
            <div className="mini-plots-container">
                {plots.map((config, idx) => (
                    <div
                        key={idx}
                        className={`mini-plot-wrapper ${expandedPlot === idx ? 'expanded' : ''}`}
                        onClick={() => handlePlotClick(idx)}
                    >
                        <Plot
                            data={config.data}
                            layout={mergeLayouts(config.layout, isDarkMode)}
                            config={{
                                responsive: true,
                                displayModeBar: true,
                                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                                displaylogo: false
                            }}
                            style={{ width: '100%', height: expandedPlot === idx ? '500px' : '380px' }}
                            useResizeHandler={true}
                        />
                    </div>
                ))}
            </div>
        </div>
    );
};

/**
 * MiniEquationEditor - A compact equation editor 
 * 
 * Uses useEquationEditorState to guarantee logic parity with main editor.
 * 
 * Props:
 * - title: The title displayed in the header
 * - description: Optional description text
 * - initialEquations: Initial equation text
 * - category: Optional category badge
 * - onEquationsChange: Optional callback when equations change (for save functionality)
 * - hideHeader: If true, hides the built-in header (for custom tab editors)
 */
export const MiniEquationEditor = ({
    title,
    description,
    initialEquations,
    category,
    onEquationsChange,
    hideHeader = false
}) => {
    const state = useEquationEditorState(initialEquations);
    const textareaRef = useRef(null);

    // State for collapsed array tables
    const [arrayTablesCollapsed, setArrayTablesCollapsed] = useState({
        key: true,      // key variables table starts collapsed
        results: true   // main results table starts collapsed
    });

    const toggleKeyTableCollapse = () => {
        setArrayTablesCollapsed(prev => ({ ...prev, key: !prev.key }));
    };

    const toggleResultsTableCollapse = () => {
        setArrayTablesCollapsed(prev => ({ ...prev, results: !prev.results }));
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [state.equations]);

    // Callback when equations change
    const handleTextChange = (newValue) => {
        state.handleTextChange(newValue);
        if (onEquationsChange) {
            onEquationsChange(newValue);
        }
    };


    // Helper to separate array and scalar results
    const getArrayResults = (results, filterKeys = null) => {
        if (!results) return {};
        return Object.fromEntries(
            Object.entries(results).filter(([key, data]) => {
                if (filterKeys && !filterKeys.includes(key)) return false;
                return data.is_array;
            })
        );
    };

    const getScalarResults = (results, filterKeys = null) => {
        if (!results) return {};
        return Object.fromEntries(
            Object.entries(results).filter(([key, data]) => {
                if (filterKeys && !filterKeys.includes(key)) return false;
                return !data.is_array;
            })
        );
    };

    return (
        <div className={`mini-editor-card ${hideHeader ? 'no-header' : ''}`}>
            {!hideHeader && (
                <div className="mini-editor-header">
                    <div className="mini-editor-title">
                        <h2>{title}</h2>
                        {category && <span className="category-badge">{category}</span>}
                        {description && <p className="mini-editor-description">{description}</p>}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <select
                            className="unit-selector"
                            value={state.angleUnit}
                            onChange={(e) => state.setAngleUnit(e.target.value)}
                            disabled={state.isRunning}
                        >
                            <option value="deg">Deg</option>
                            <option value="rad">Rad</option>
                        </select>
                        <select
                            className="unit-selector"
                            value={state.arrayMode}
                            onChange={(e) => state.setArrayMode(e.target.value)}
                            disabled={state.isRunning}
                            title="Array combination mode"
                        >
                            <option value="parallel">Parallel</option>
                            <option value="grid">Grid</option>
                        </select>
                        <button
                            className="mini-run-button"
                            onClick={state.handleRun}
                            disabled={state.isRunning}
                        >
                            {state.isRunning ? '⏳ Running...' : '▶ Run'}
                        </button>
                    </div>
                </div>
            )}

            <div className="mini-editor-body">
                {/* Show controls when header is hidden */}
                {hideHeader && (
                    <div className="mini-editor-inline-controls">
                        <select
                            className="unit-selector"
                            value={state.angleUnit}
                            onChange={(e) => state.setAngleUnit(e.target.value)}
                            disabled={state.isRunning}
                        >
                            <option value="deg">Deg</option>
                            <option value="rad">Rad</option>
                        </select>
                        <select
                            className="unit-selector"
                            value={state.arrayMode}
                            onChange={(e) => state.setArrayMode(e.target.value)}
                            disabled={state.isRunning}
                            title="Array combination mode"
                        >
                            <option value="parallel">Parallel</option>
                            <option value="grid">Grid</option>
                        </select>
                        <button
                            className="mini-run-button"
                            onClick={state.handleRun}
                            disabled={state.isRunning}
                        >
                            {state.isRunning ? '⏳ Running...' : '▶ Run'}
                        </button>
                    </div>
                )}
                <div className="mini-input-section">
                    <textarea
                        ref={textareaRef}
                        className="mini-equation-input"
                        value={state.equations}
                        onChange={(e) => handleTextChange(e.target.value)}
                        spellCheck="false"
                    />
                </div>

                {(state.results || state.error || state.unitWarnings.length > 0) && (
                    <div className="mini-output-section">
                        {/* Array solve indicator */}
                        {state.isArraySolve && (
                            <div className="array-solve-indicator">
                                📊 Array solve mode - Click on array results to expand
                            </div>
                        )}

                        {/* Key Variables Section */}
                        {state.keyVariables.length > 0 && state.results && (() => {
                            const keyArrayResults = getArrayResults(state.results, state.keyVariables);
                            const keyScalarResults = getScalarResults(state.results, state.keyVariables);
                            const hasKeyArrays = Object.keys(keyArrayResults).length > 0;
                            const hasKeyScalars = Object.keys(keyScalarResults).length > 0;

                            return (
                                <div className="mini-key-variables-section">
                                    <div className="mini-output-header">
                                        <h4>⭐ Key Variables</h4>
                                    </div>
                                    {/* Key scalar variables */}
                                    {hasKeyScalars && (
                                        <div className="mini-results-grid">
                                            {state.keyVariables.map(v =>
                                                state.results[v] && !state.results[v].is_array ? (
                                                    <ResultCard
                                                        key={v}
                                                        variable={v}
                                                        originalData={state.results[v]}
                                                        displayUnits={state.displayUnits}
                                                        isKey={true}
                                                        onContextMenu={state.handleContextMenu}
                                                        onConfirmUnit={state.handleConfirmUnit}
                                                        isUnitConfirmed={state.isUnitConfirmed}
                                                        className="mini-result-card"
                                                    />
                                                ) : null
                                            )}
                                        </div>
                                    )}
                                    {/* Key array variables table */}
                                    {hasKeyArrays && (
                                        <ArrayResultsTable
                                            arrayResults={keyArrayResults}
                                            displayUnits={state.displayUnits}
                                            handleContextMenu={state.handleContextMenu}
                                            onConfirmUnit={state.handleConfirmUnit}
                                            isUnitConfirmed={state.isUnitConfirmed}
                                            isCollapsed={arrayTablesCollapsed.key}
                                            onToggleCollapse={toggleKeyTableCollapse}
                                            title="Key Array Variables"
                                            isKeySection={true}
                                        />
                                    )}
                                </div>
                            );
                        })()}

                        <div className="mini-output-header">
                            <h4>Results</h4>
                        </div>

                        {state.unitWarnings.length > 0 && (
                            <div className="unit-warnings">
                                <div className="warning-header">⚠️ Unit Analysis Warnings</div>
                                {state.unitWarnings.map((warning, idx) => (
                                    <div key={idx} className="warning-item">{warning}</div>
                                ))}
                            </div>
                        )}

                        {state.error ? (
                            <pre className="mini-output-error">{state.error}</pre>
                        ) : state.results && (() => {
                            const arrayResults = getArrayResults(state.results);
                            const scalarResults = getScalarResults(state.results);
                            const hasArrays = Object.keys(arrayResults).length > 0;
                            const hasScalars = Object.keys(scalarResults).length > 0;

                            return (
                                <>
                                    {/* Scalar results grid */}
                                    {hasScalars && (
                                        <div className="mini-results-grid">
                                            {Object.entries(scalarResults).map(([variable, data]) => (
                                                <ResultCard
                                                    key={variable}
                                                    variable={variable}
                                                    originalData={data}
                                                    displayUnits={state.displayUnits}
                                                    onContextMenu={state.handleContextMenu}
                                                    onConfirmUnit={state.handleConfirmUnit}
                                                    isUnitConfirmed={state.isUnitConfirmed}
                                                    className="mini-result-card"
                                                />
                                            ))}
                                        </div>
                                    )}

                                    {/* Array results table */}
                                    {hasArrays && (
                                        <ArrayResultsTable
                                            arrayResults={arrayResults}
                                            displayUnits={state.displayUnits}
                                            handleContextMenu={state.handleContextMenu}
                                            onConfirmUnit={state.handleConfirmUnit}
                                            isUnitConfirmed={state.isUnitConfirmed}
                                            isCollapsed={arrayTablesCollapsed.results}
                                            onToggleCollapse={toggleResultsTableCollapse}
                                            title="Array Results"
                                            isKeySection={false}
                                        />
                                    )}

                                    {/* Render Plots */}
                                    {state.plots && state.plots.length > 0 && (
                                        <MiniPlotPanel plots={state.plots} />
                                    )}
                                </>
                            );
                        })()}
                    </div>
                )}
            </div>

            {/* Context Menu */}
            <ResultContextMenu
                contextMenu={state.contextMenu}
                contextMenuRef={state.contextMenuRef}
                keyVariables={state.keyVariables}
                displayUnits={state.displayUnits}
                results={state.results}
                isUnitConfirmed={state.isUnitConfirmed}
                onToggleKeyVariable={state.handleToggleKeyVariable}
                onOpenUnitModal={state.handleOpenUnitModal}
                onResetUnit={state.handleResetUnit}
                onConfirmUnit={state.handleConfirmUnit}
                onClose={state.closeContextMenu}
            />

            {/* Unit Input Modal */}
            <UnitInputModal
                isOpen={state.unitModal.isOpen}
                variable={state.unitModal.variable}
                currentUnit={state.unitModal.currentUnit}
                originalUnit={state.unitModal.originalUnit}
                unitSource={state.unitModal.unitSource}
                onConfirm={state.handleUnitModalConfirm}
                onCancel={state.handleUnitModalCancel}
            />
        </div>
    );
};



