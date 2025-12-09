import React, { useState, useEffect, Suspense, lazy } from 'react';
import './EquationEditor.css';
import {
    getUnitHue,
    convertUnit,
    formatNumber,
    formatUnitDisplay,
    UnitInputModal,
    ResultContextMenu,
    ResultCard,
    ArrayResultsTable,
    useEquationEditorState
} from './EditorComponents';

// Lazy load PlotPanel to gracefully handle missing plotly dependency
const PlotPanel = lazy(() =>
    import('./PlotPanel').then(module => ({ default: module.PlotPanel })).catch(() => ({
        default: () => (
            <div className="plot-panel-missing">
                <p>📊 Plotting requires additional dependencies.</p>
                <p>Run: <code>npm install</code> in the frontend folder</p>
            </div>
        )
    }))
);

/**
 * EquationEditor - The main equation editor component
 * 
 * ============================================================================
 * ⚠️  CRITICAL: FEATURE PARITY REQUIREMENT  ⚠️
 * ============================================================================
 * 
 * If you add ANY feature to this component, you MUST also add it to:
 * - MiniEquationEditor in EditorComponents.jsx
 * 
 * The preferred approach is:
 * 1. Add the feature to useEquationEditorState hook in EditorComponents.jsx
 * 2. Both EquationEditor and MiniEquationEditor will automatically get it
 * 
 * See: .agent/workflows/editor-feature-parity.md for full documentation
 * ============================================================================
 * 
 * This is the primary editor for the application. Features include:
 * - Equation editing with syntax highlighting placeholder
 * - Equation solving via backend API (supports arrays!)
 * - Angle unit selection (degrees/radians)
 * - Array mode selection (parallel/grid)
 * - Right-click context menu on results
 * - Key variables management (pin important variables)
 * - Display unit conversion with modal
 * - Unit warnings display
 * - Plotly charts for array results
 * 
 * IMPORTANT: Uses shared useEquationEditorState hook from EditorComponents.jsx
 * to ensure feature parity with MiniEquationEditors.
 */
const EquationEditor = ({ initialValue, onValueChange }) => {
    // Use the shared state hook for feature parity
    const state = useEquationEditorState(initialValue, onValueChange);

    // State for collapsed array tables
    const [arrayTablesCollapsed, setArrayTablesCollapsed] = React.useState({
        key: true,      // key variables table starts collapsed
        results: true   // main results table starts collapsed
    });

    const toggleKeyTableCollapse = () => {
        setArrayTablesCollapsed(prev => ({ ...prev, key: !prev.key }));
    };

    const toggleResultsTableCollapse = () => {
        setArrayTablesCollapsed(prev => ({ ...prev, results: !prev.results }));
    };

    const getDisplayData = (variable, originalData) => {
        const targetUnit = state.displayUnits[variable];
        if (!targetUnit) {
            return originalData;
        }

        const converted = convertUnit(originalData.value, originalData.unit, targetUnit);
        let warning = null;

        // Check for mismatches
        if (!originalData.unit && targetUnit) {
            warning = `Mismatch: Calculated (Dimensionless) vs Display (${targetUnit})`;
        } else if (!converted.success) {
            warning = `Mismatch: Calculated (${originalData.unit}) vs Display (${targetUnit})`;
        }

        return {
            value: converted.value,
            unit: targetUnit,
            warning
        };
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

    const renderResultCard = (variable, originalData, isKey = false) => {
        // Only handle scalar results - arrays are handled by ArrayResultsTable
        if (originalData.is_array) {
            return null; // Arrays are handled separately
        }

        const displayData = getDisplayData(variable, originalData);
        const hasOverride = state.displayUnits[variable];

        // Unit confirmation status
        const unitSource = originalData?.unit_source || 'propagated';
        const isConfirmed = state.isUnitConfirmed(variable, unitSource);
        const showUnconfirmed = displayData.unit && !isConfirmed;

        return (
            <ResultCard
                key={variable}
                variable={variable}
                originalData={originalData}
                displayUnits={state.displayUnits}
                isKey={isKey}
                onContextMenu={state.handleContextMenu}
                isUnitConfirmed={state.isUnitConfirmed}
            />
        );
    };

    return (
        <div className="editor-container">
            <div className="editor-header">
                <h1>Equation Editor</h1>
                <p className="editor-header-subtitle">Enter equations to solve and visualize</p>
            </div>

            <div className="editor-main">
                {/* Controls Row */}
                <div className="equation-editor-controls">
                    <select
                        className="unit-selector"
                        value={state.angleUnit}
                        onChange={(e) => state.setAngleUnit(e.target.value)}
                        disabled={state.isRunning}
                        title="Angle units for trig functions"
                    >
                        <option value="deg">Degrees</option>
                        <option value="rad">Radians</option>
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
                        className="run-button"
                        onClick={state.handleRun}
                        disabled={state.isRunning}
                    >
                        {state.isRunning ? 'Running...' : 'Run Equations'}
                    </button>
                </div>

                <div className="input-section">
                    <textarea
                        className="equation-input"
                        value={state.equations}
                        onChange={(e) => state.handleTextChange(e.target.value)}
                        placeholder={`Enter your equations here...

Example (scalar):
x = 5 [m]
y = x^2 + 10 [m^2]

Example (array sweep):
t = linspace(0, 10, 50)
v = 5 [m/s]
x = v * t
plot(t, x)`}
                        spellCheck="false"
                    />
                </div>

                {(state.results || state.error) && (
                    <div className="output-section">
                        {/* Array solve indicator */}
                        {state.isArraySolve && (
                            <div className="array-solve-indicator">
                                📊 Array solve mode - Results contain arrays
                            </div>
                        )}

                        {/* Key Variables Section */}
                        {state.keyVariables.length > 0 && state.results && (() => {
                            const keyArrayResults = getArrayResults(state.results, state.keyVariables);
                            const keyScalarResults = getScalarResults(state.results, state.keyVariables);
                            const hasKeyArrays = Object.keys(keyArrayResults).length > 0;
                            const hasKeyScalars = Object.keys(keyScalarResults).length > 0;

                            return (
                                <div className="key-variables-section">
                                    <div className="output-header">
                                        <h3>Key Variables</h3>
                                    </div>
                                    {/* Key scalar variables */}
                                    {hasKeyScalars && (
                                        <div className="results-grid">
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

                        <div className="output-header">
                            <h3>Results</h3>
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
                            <pre className="output-error">{state.error}</pre>
                        ) : (() => {
                            const arrayResults = getArrayResults(state.results);
                            const scalarResults = getScalarResults(state.results);
                            const hasArrays = Object.keys(arrayResults).length > 0;
                            const hasScalars = Object.keys(scalarResults).length > 0;

                            return (
                                <>
                                    {/* Scalar results grid */}
                                    {hasScalars && (
                                        <div className="results-grid">
                                            {Object.entries(scalarResults).map(([variable, data]) => (
                                                <ResultCard
                                                    key={variable}
                                                    variable={variable}
                                                    originalData={data}
                                                    displayUnits={state.displayUnits}
                                                    onContextMenu={state.handleContextMenu}
                                                    onConfirmUnit={state.handleConfirmUnit}
                                                    isUnitConfirmed={state.isUnitConfirmed}
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
                                        <Suspense fallback={<div className="plot-loading">Loading plots...</div>}>
                                            <PlotPanel plotConfigs={state.plots} />
                                        </Suspense>
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

export default EquationEditor;

