---
description: How to maintain feature parity between main editor and mini editors
---

# Editor Feature Parity Workflow

> ⚠️ **CRITICAL RULE**: The mini equation editors MUST ALWAYS have 100% feature parity with the main Equation Editor. If you add a feature to one, you MUST add it to all.

## The Golden Rule

**NEVER add a feature to `EquationEditor.jsx` without also adding it to `MiniEquationEditor` in `EditorComponents.jsx`.**

This is non-negotiable. Both editors serve the same purpose (solving equations) and users expect identical behavior regardless of which page they're on.

## Architecture Overview

All shared editor functionality is centralized in:
```
frontend/src/EditorComponents.jsx
```

This file contains:
1. **Utility Functions**: `getUnitHue()`, `formatNumber()` - for display formatting
2. **Unit Conversion System**: `UNIT_CONVERSIONS`, `convertUnit()`, `getSuggestedUnits()`
3. **Modal Components**: `UnitInputModal` - for changing display units
4. **Context Menu**: `ResultContextMenu` - right-click menu on result cards
5. **Result Rendering**: `ResultCard` - individual result display
6. **Plot Panel**: `MiniPlotPanel` - Plotly chart rendering for mini editors
7. **Custom Hooks**:
   - `useContextMenu()` - manages context menu state
   - `useKeyVariables()` - manages pinned/key variable state
   - `useDisplayUnits()` - manages unit override state
   - `useUnitModal()` - manages unit modal state
   - `useEquationEditorState()` - **THE MAIN HOOK** that encapsulates ALL editor logic
8. **MiniEquationEditor** - The complete mini editor component

## Adding a New Feature - MANDATORY STEPS

When adding ANY new feature to the equation editor:

### Step 1: Check if Feature Exists in Main Editor

Before starting, check `EquationEditor.jsx` for the feature. If it exists there but not in mini editors, you need to port it.

### Step 2: Implement in EditorComponents.jsx FIRST

**Always start here.** Add the feature to `EditorComponents.jsx`:

```javascript
// If it's a hook:
export const useNewFeature = () => {
    const [state, setState] = useState(...);
    // ... implementation
    return { state, ...handlers };
};

// If it's a component:
export const NewFeatureComponent = ({ props }) => {
    // ... implementation
};
```

### Step 3: Update useEquationEditorState Hook

If the feature involves state management, add it to `useEquationEditorState`:

```javascript
export const useEquationEditorState = (initialEquations, onValueChange = null) => {
    // Add your new state here
    const [newFeatureState, setNewFeatureState] = useState(...);
    
    // Add handlers
    const handleNewFeature = () => { ... };
    
    // Return in the state object
    return {
        // ... existing state
        newFeatureState,
        handleNewFeature,
    };
};
```

### Step 4: Update MiniEquationEditor

In `EditorComponents.jsx`, update the `MiniEquationEditor` component to use the new feature:

```javascript
export const MiniEquationEditor = ({ ... }) => {
    const state = useEquationEditorState(initialEquations);
    
    // Use state.newFeatureState and state.handleNewFeature
    // Add JSX for the new feature
};
```

### Step 5: Update Main EquationEditor

Update `EquationEditor.jsx` to use the same feature (may already use shared hook):

```javascript
const EquationEditor = ({ ... }) => {
    const state = useEquationEditorState(initialValue, onValueChange);
    
    // Both editors now automatically have the feature!
};
```

### Step 6: Add Required CSS

Update ALL CSS files with matching styles:
- `EquationEditor.css` - for main editor styles
- `Instructions.css` - for mini editor styles (shared by StressTests, Guide)
- `CustomTabs.css` - for custom equation sets (uses hidden header overlay)

**The styles should be visually consistent!** The custom tabs use `hideHeader={true}` and overlay an editable header, so sizing must match `Instructions.css`.

### Step 7: Update This Documentation

Add the new feature to the Current Shared Features table below.

## Current Shared Features

| Feature | Description | Main Editor | Mini Editors |
|---------|-------------|:-----------:|:------------:|
| Equation Running | Solve equations via API | ✅ | ✅ |
| Angle Unit Selection | deg/rad toggle | ✅ | ✅ |
| Array Mode Selection | parallel/grid toggle | ✅ | ✅ |
| Context Menu | Right-click on results | ✅ | ✅ |
| Key Variables | Pin important variables | ✅ | ✅ |
| Display Unit Override | Convert units on display | ✅ | ✅ |
| Unit Modal | Modal for entering units | ✅ | ✅ |
| Unit Warnings | Display solver warnings | ✅ | ✅ |
| Equation Plotting | Interactive Plotly charts | ✅ | ✅ |
| Array Table Display | Collapsible table view of arrays | ✅ | ✅ |
| Array Solve Indicator | Banner showing array mode | ✅ | ✅ |

## Testing Feature Parity - REQUIRED

After making ANY changes to editor functionality:

// turbo-all
1. Start the development server: `npm run dev` (in frontend directory)
2. Navigate to the main **Equation Editor** tab and test the feature
3. Navigate to the **Guide & Examples** page and test the SAME feature
4. Navigate to the **Stress Tests** page and test the SAME feature
5. **Verify all three locations behave IDENTICALLY**

## File Structure

```
frontend/src/
├── EditorComponents.jsx     # 🔑 SHARED: Components, hooks, utilities, MiniEquationEditor
├── EquationEditor.jsx       # Main equation editor (uses shared hooks)
├── EquationEditor.css       # Main editor styles
├── Instructions.jsx         # Guide page (imports MiniEquationEditor)
├── StressTests.jsx          # Stress tests page (imports MiniEquationEditor)
├── Instructions.css         # Shared mini editor styles
└── PlotPanel.jsx            # Full PlotPanel (main editor uses this)
```

## Quick Checklist for New Features

Before submitting any editor change, verify:

- [ ] Feature is implemented in `EditorComponents.jsx`
- [ ] `useEquationEditorState` hook includes any new state
- [ ] `MiniEquationEditor` component uses the feature
- [ ] `EquationEditor.jsx` uses the same shared logic
- [ ] CSS added to BOTH `EquationEditor.css` AND `Instructions.css`
- [ ] Feature table in this document is updated
- [ ] Tested in ALL THREE locations (main editor, guide, stress tests)

## Key Principles

> **Single Source of Truth**: All editor-related logic should be implemented in `EditorComponents.jsx` first, then consumed by both the main editor and mini editors.

> **No Feature Left Behind**: If a user can do something in the main editor, they MUST be able to do the same thing in mini editors.

> **Consistency is Key**: Visual styles, interaction patterns, and behavior should be identical across all editors.
