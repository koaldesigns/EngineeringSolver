import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './AuthContext';
import LoginModal from './LoginModal';
import './Sidebar.css';
import './CustomTabs.css';

const Sidebar = ({ activeTab, setActiveTab, customTabs = [], onAddTab, onImportTab }) => {
    const [showImportModal, setShowImportModal] = useState(false);
    const [importData, setImportData] = useState('');
    const [importError, setImportError] = useState('');
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [showUserDropdown, setShowUserDropdown] = useState(false);
    const fileInputRef = useRef(null);
    const dropdownRef = useRef(null);

    const { user, isLoggedIn, isLoading, isAdmin, logout } = useAuth();

    const builtInTabs = [
        { id: 'editor', label: 'Equation Editor', icon: '📝' },
        { id: 'documentation', label: 'Documentation', icon: '📘' },
        { id: 'instructions', label: 'Guide & Examples', icon: '📚' },
        { id: 'stresstests', label: 'Stress Tests', icon: '🧪' },
        { id: 'settings', label: 'Settings', icon: '⚙️' },
    ];

    const handleAddTab = () => {
        const newTab = {
            id: `custom_${Date.now()}`,
            name: 'My Equations',
            icon: '📐',
            equationSets: []
        };
        onAddTab && onAddTab(newTab);
    };

    const handleImportClick = () => {
        setShowImportModal(true);
        setImportData('');
        setImportError('');
    };

    const handleImportSubmit = () => {
        try {
            const parsed = JSON.parse(importData);
            if (!parsed.id || !parsed.name || !parsed.equationSets) {
                throw new Error('Invalid tab format. Expected: {id, name, icon, equationSets}');
            }
            onImportTab && onImportTab(parsed);
            setShowImportModal(false);
            setImportData('');
            setImportError('');
        } catch (err) {
            setImportError(err.message);
        }
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setImportData(event.target.result);
            };
            reader.readAsText(file);
        }
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowUserDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = async () => {
        setShowUserDropdown(false);
        await logout();
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h2>Engineering Solver</h2>
            </div>

            {/* User Account Section */}
            <div className="sidebar-user-section">
                {isLoading ? (
                    <div className="user-loading">...</div>
                ) : isLoggedIn ? (
                    <div className="user-info" ref={dropdownRef}>
                        <button
                            className="user-info-btn"
                            onClick={() => setShowUserDropdown(!showUserDropdown)}
                        >
                            <span className="user-avatar">{isAdmin ? '👑' : '👤'}</span>
                            <span className="user-name">{user?.username}</span>
                            <span className="dropdown-arrow">▼</span>
                        </button>
                        {showUserDropdown && (
                            <div className="sidebar-user-dropdown">
                                <div className="dropdown-username">
                                    {user?.username}
                                    {isAdmin && <span className="admin-badge">Admin</span>}
                                </div>
                                <button className="dropdown-signout" onClick={handleLogout}>
                                    🚪 Sign Out
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <button
                        className="sidebar-sign-in-btn"
                        onClick={() => setShowLoginModal(true)}
                    >
                        <span className="sign-in-icon">🔐</span>
                        <span>Sign In</span>
                    </button>
                )}
            </div>

            <nav className="sidebar-nav">
                {/* Built-in tabs */}
                {builtInTabs.map((tab) => (
                    <button
                        key={tab.id}
                        className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="icon">{tab.icon}</span>
                        <span className="label">{tab.label}</span>
                    </button>
                ))}

                {/* Custom tabs section */}
                {(customTabs.length > 0 || onAddTab) && (
                    <div className="sidebar-custom-tabs">
                        <div className="sidebar-custom-tabs-header">
                            <span>My Equation Sets</span>
                            {!isLoggedIn && customTabs.length > 0 && (
                                <span
                                    className="unsaved-indicator"
                                    title="Sign in to save your equation sets"
                                >
                                    ⚠️
                                </span>
                            )}
                            <div style={{ display: 'flex', gap: '4px' }}>
                                <button
                                    className="add-tab-btn"
                                    onClick={handleImportClick}
                                    title="Import equation set"
                                >
                                    📥
                                </button>
                                <button
                                    className="add-tab-btn"
                                    onClick={handleAddTab}
                                    title="Create new equation set"
                                >
                                    +
                                </button>
                            </div>
                        </div>
                        {customTabs.map((tab) => (
                            <button
                                key={tab.id}
                                className={`custom-tab-nav-item ${activeTab === `custom_${tab.id}` ? 'active' : ''}`}
                                onClick={() => setActiveTab(`custom_${tab.id}`)}
                            >
                                <span className="tab-icon">{tab.icon || '📐'}</span>
                                <span className="tab-name">{tab.name}</span>
                            </button>
                        ))}
                    </div>
                )}
            </nav>
            <div className="sidebar-footer">
                <p>v0.1.0</p>
            </div>

            {/* Login Modal */}
            <LoginModal
                isOpen={showLoginModal}
                onClose={() => setShowLoginModal(false)}
            />

            {/* Import Modal */}
            {showImportModal && (
                <div className="import-modal-overlay" onClick={() => setShowImportModal(false)}>
                    <div className="import-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>📥 Import Equation Set</h3>
                        <input
                            type="file"
                            ref={fileInputRef}
                            accept=".json"
                            onChange={handleFileUpload}
                            style={{ display: 'none' }}
                        />
                        <button
                            className="action-btn"
                            onClick={() => fileInputRef.current?.click()}
                            style={{ marginBottom: '1rem', width: '100%' }}
                        >
                            📂 Choose JSON File
                        </button>
                        <textarea
                            placeholder="...or paste exported JSON here"
                            value={importData}
                            onChange={(e) => setImportData(e.target.value)}
                        />
                        {importError && (
                            <p style={{ color: '#ef4444', fontSize: '0.85rem', margin: '0.5rem 0' }}>
                                ⚠️ {importError}
                            </p>
                        )}
                        <div className="import-modal-actions">
                            <button className="cancel-btn" onClick={() => setShowImportModal(false)}>
                                Cancel
                            </button>
                            <button className="import-btn" onClick={handleImportSubmit}>
                                Import
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Sidebar;
