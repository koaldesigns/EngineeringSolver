import React, { useState, useEffect, useRef } from 'react';
import { solveEquations, saveCustomTabs, exportCustomTab } from './api';
import './Instructions.css';
import './CustomTabs.css';
import {
    MiniEquationEditor
} from './EditorComponents';

/**
 * CustomTabView - Displays a single custom tab's equation sets
 * Similar to StressTests but with full edit capabilities
 */
const CustomTabView = ({ tab, onUpdateTab, onDeleteTab, onExportTab }) => {
    const [isEditingName, setIsEditingName] = useState(false);
    const [editedName, setEditedName] = useState(tab.name);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const nameInputRef = useRef(null);

    useEffect(() => {
        if (isEditingName && nameInputRef.current) {
            nameInputRef.current.focus();
            nameInputRef.current.select();
        }
    }, [isEditingName]);

    const handleNameSubmit = () => {
        if (editedName.trim()) {
            onUpdateTab({ ...tab, name: editedName.trim() });
        } else {
            setEditedName(tab.name);
        }
        setIsEditingName(false);
    };

    const handleAddEquationSet = () => {
        const newSet = {
            id: `eq_${Date.now()}`,
            title: 'New Equation Set',
            description: 'Add your equations here',
            equations: '// Enter your equations\nx = 5\ny = x * 2'
        };
        onUpdateTab({
            ...tab,
            equationSets: [...tab.equationSets, newSet]
        });
    };

    const handleUpdateEquationSet = (setId, newEquations) => {
        onUpdateTab({
            ...tab,
            equationSets: tab.equationSets.map(set =>
                set.id === setId ? { ...set, equations: newEquations } : set
            )
        });
    };

    const handleUpdateEquationSetMeta = (setId, field, value) => {
        onUpdateTab({
            ...tab,
            equationSets: tab.equationSets.map(set =>
                set.id === setId ? { ...set, [field]: value } : set
            )
        });
    };

    const handleDeleteEquationSet = (setId) => {
        onUpdateTab({
            ...tab,
            equationSets: tab.equationSets.filter(set => set.id !== setId)
        });
    };

    const handleMoveEquationSet = (setId, direction) => {
        const idx = tab.equationSets.findIndex(s => s.id === setId);
        if ((direction === -1 && idx === 0) ||
            (direction === 1 && idx === tab.equationSets.length - 1)) {
            return;
        }
        const newSets = [...tab.equationSets];
        const temp = newSets[idx];
        newSets[idx] = newSets[idx + direction];
        newSets[idx + direction] = temp;
        onUpdateTab({ ...tab, equationSets: newSets });
    };

    return (
        <div className="instructions-container">
            <div className="instructions-header custom-tab-header">
                <div className="custom-tab-title-row">
                    <span className="tab-icon">{tab.icon}</span>
                    {isEditingName ? (
                        <input
                            ref={nameInputRef}
                            type="text"
                            value={editedName}
                            onChange={(e) => setEditedName(e.target.value)}
                            onBlur={handleNameSubmit}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleNameSubmit();
                                if (e.key === 'Escape') {
                                    setEditedName(tab.name);
                                    setIsEditingName(false);
                                }
                            }}
                            className="tab-name-input"
                        />
                    ) : (
                        <h1 onClick={() => setIsEditingName(true)} className="editable-title">
                            {tab.name}
                            <span className="edit-hint">✏️</span>
                        </h1>
                    )}
                </div>
                <div className="custom-tab-actions">
                    <button className="action-btn add-btn" onClick={handleAddEquationSet}>
                        ➕ Add Equation Set
                    </button>
                    <button className="action-btn export-btn" onClick={() => onExportTab(tab.id)}>
                        📤 Export
                    </button>
                    {showDeleteConfirm ? (
                        <div className="delete-confirm">
                            <span>Delete this tab?</span>
                            <button className="confirm-yes" onClick={() => onDeleteTab(tab.id)}>Yes</button>
                            <button className="confirm-no" onClick={() => setShowDeleteConfirm(false)}>No</button>
                        </div>
                    ) : (
                        <button className="action-btn delete-btn" onClick={() => setShowDeleteConfirm(true)}>
                            🗑️ Delete Tab
                        </button>
                    )}
                </div>
            </div>

            <div className="instructions-content">
                {tab.equationSets.length === 0 ? (
                    <div className="empty-tab-message">
                        <p>This tab is empty. Click <strong>+ Add Equation Set</strong> to create your first equation set.</p>
                    </div>
                ) : (
                    tab.equationSets.map((eqSet, index) => (
                        <EditableMiniEditor
                            key={eqSet.id}
                            eqSet={eqSet}
                            onUpdateEquations={(newEq) => handleUpdateEquationSet(eqSet.id, newEq)}
                            onUpdateMeta={(field, value) => handleUpdateEquationSetMeta(eqSet.id, field, value)}
                            onDelete={() => handleDeleteEquationSet(eqSet.id)}
                            onMoveUp={() => handleMoveEquationSet(eqSet.id, -1)}
                            onMoveDown={() => handleMoveEquationSet(eqSet.id, 1)}
                            canMoveUp={index > 0}
                            canMoveDown={index < tab.equationSets.length - 1}
                        />
                    ))
                )}
            </div>
        </div>
    );
};

/**
 * EditableMiniEditor - Wraps MiniEquationEditor with edit/delete controls
 */
const EditableMiniEditor = ({
    eqSet,
    onUpdateEquations,
    onUpdateMeta,
    onDelete,
    onMoveUp,
    onMoveDown,
    canMoveUp,
    canMoveDown
}) => {
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [isEditingDesc, setIsEditingDesc] = useState(false);
    const [editedTitle, setEditedTitle] = useState(eqSet.title);
    const [editedDesc, setEditedDesc] = useState(eqSet.description);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const handleTitleSubmit = () => {
        onUpdateMeta('title', editedTitle.trim() || 'Untitled');
        setIsEditingTitle(false);
    };

    const handleDescSubmit = () => {
        onUpdateMeta('description', editedDesc.trim());
        setIsEditingDesc(false);
    };

    return (
        <div className="editable-mini-editor">
            <div className="editor-controls">
                <div className="move-controls">
                    <button
                        className="move-btn"
                        onClick={onMoveUp}
                        disabled={!canMoveUp}
                        title="Move up"
                    >▲</button>
                    <button
                        className="move-btn"
                        onClick={onMoveDown}
                        disabled={!canMoveDown}
                        title="Move down"
                    >▼</button>
                </div>
                {showDeleteConfirm ? (
                    <div className="delete-confirm-inline">
                        <button className="confirm-yes-sm" onClick={onDelete}>✓</button>
                        <button className="confirm-no-sm" onClick={() => setShowDeleteConfirm(false)}>✗</button>
                    </div>
                ) : (
                    <button
                        className="delete-set-btn"
                        onClick={() => setShowDeleteConfirm(true)}
                        title="Delete equation set"
                    >×</button>
                )}
            </div>

            {/* Editable title and description overlay */}
            <div className="editable-header-overlay">
                {isEditingTitle ? (
                    <input
                        type="text"
                        value={editedTitle}
                        onChange={(e) => setEditedTitle(e.target.value)}
                        onBlur={handleTitleSubmit}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') handleTitleSubmit();
                            if (e.key === 'Escape') {
                                setEditedTitle(eqSet.title);
                                setIsEditingTitle(false);
                            }
                        }}
                        className="title-input-overlay"
                        autoFocus
                    />
                ) : (
                    <span
                        className="editable-title-text"
                        onClick={() => setIsEditingTitle(true)}
                        title="Click to edit title"
                    >
                        {eqSet.title}
                    </span>
                )}

                {isEditingDesc ? (
                    <input
                        type="text"
                        value={editedDesc}
                        onChange={(e) => setEditedDesc(e.target.value)}
                        onBlur={handleDescSubmit}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') handleDescSubmit();
                            if (e.key === 'Escape') {
                                setEditedDesc(eqSet.description);
                                setIsEditingDesc(false);
                            }
                        }}
                        className="desc-input-overlay"
                        autoFocus
                    />
                ) : (
                    <span
                        className="editable-desc-text"
                        onClick={() => setIsEditingDesc(true)}
                        title="Click to edit description"
                    >
                        {eqSet.description || 'Click to add description'}
                    </span>
                )}
            </div>

            <MiniEquationEditor
                title={eqSet.title}
                description={eqSet.description}
                initialEquations={eqSet.equations}
                onEquationsChange={onUpdateEquations}
                hideHeader={true}
            />
        </div>
    );
};

export { CustomTabView };
export default CustomTabView;
