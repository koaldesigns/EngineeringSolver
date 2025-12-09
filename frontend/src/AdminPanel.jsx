import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { getAdminUsers, deleteAdminUser, getAdminTokens, getAdminStats } from './api';
import './AdminPanel.css';

const AdminPanel = () => {
    const { isAdmin } = useAuth();
    const [users, setUsers] = useState([]);
    const [tokens, setTokens] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [deleteConfirm, setDeleteConfirm] = useState(null);

    useEffect(() => {
        if (!isAdmin) return;
        loadData();
    }, [isAdmin]);

    const loadData = async () => {
        setLoading(true);
        setError('');
        try {
            const [usersData, tokensData, statsData] = await Promise.all([
                getAdminUsers(),
                getAdminTokens(),
                getAdminStats()
            ]);
            setUsers(usersData);
            setTokens(tokensData);
            setStats(statsData);
        } catch (err) {
            setError(err.message || 'Failed to load admin data');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteUser = async (userId, username) => {
        try {
            await deleteAdminUser(userId);
            setDeleteConfirm(null);
            loadData(); // Refresh
        } catch (err) {
            setError(err.message || 'Failed to delete user');
        }
    };

    if (!isAdmin) {
        return null;
    }

    if (loading) {
        return (
            <div className="admin-panel">
                <h2>👑 Admin Panel</h2>
                <p className="loading-text">Loading admin data...</p>
            </div>
        );
    }

    return (
        <div className="admin-panel">
            <h2>👑 Admin Panel</h2>

            {error && (
                <div className="admin-error">⚠️ {error}</div>
            )}

            {/* Stats Overview */}
            {stats && (
                <div className="admin-stats">
                    <div className="stat-card">
                        <span className="stat-value">{stats.regular_users}</span>
                        <span className="stat-label">/ {stats.max_users} Users</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-value">{stats.available_tokens}</span>
                        <span className="stat-label">Tokens Available</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-value">{stats.total_equation_tabs}</span>
                        <span className="stat-label">Equation Tabs</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-value">{stats.total_equation_sets}</span>
                        <span className="stat-label">Equation Sets</span>
                    </div>
                </div>
            )}

            {/* User List */}
            <h3>👥 Registered Users</h3>
            <div className="admin-table-container">
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Created</th>
                            <th>Last Active</th>
                            <th>Tabs</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td className="username-cell">
                                    {user.username}
                                </td>
                                <td>
                                    {user.is_admin ? (
                                        <span className="role-badge admin">Admin</span>
                                    ) : (
                                        <span className="role-badge user">User</span>
                                    )}
                                </td>
                                <td className="date-cell">
                                    {new Date(user.created_at).toLocaleDateString()}
                                </td>
                                <td className="date-cell">
                                    {new Date(user.last_active).toLocaleDateString()}
                                </td>
                                <td>{user.equation_tab_count}</td>
                                <td>
                                    {!user.is_admin && (
                                        deleteConfirm === user.id ? (
                                            <div className="delete-confirm-inline">
                                                <button
                                                    className="confirm-btn yes"
                                                    onClick={() => handleDeleteUser(user.id, user.username)}
                                                >
                                                    Yes
                                                </button>
                                                <button
                                                    className="confirm-btn no"
                                                    onClick={() => setDeleteConfirm(null)}
                                                >
                                                    No
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                className="delete-user-btn"
                                                onClick={() => setDeleteConfirm(user.id)}
                                            >
                                                🗑️
                                            </button>
                                        )
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Token Status */}
            <h3>🔑 Registration Tokens</h3>
            <div className="token-grid">
                {tokens.map(token => (
                    <div
                        key={token.token}
                        className={`token-card ${token.is_available ? 'available' : 'used'}`}
                    >
                        <code className="token-code">{token.token}</code>
                        {token.is_available ? (
                            <span className="token-status available">Available</span>
                        ) : (
                            <span className="token-status used">
                                Used by {token.used_by_username}
                            </span>
                        )}
                    </div>
                ))}
            </div>

            <button className="refresh-btn" onClick={loadData}>
                🔄 Refresh Data
            </button>
        </div>
    );
};

export default AdminPanel;
