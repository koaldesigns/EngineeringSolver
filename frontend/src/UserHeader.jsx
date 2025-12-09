import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './AuthContext';
import LoginModal from './LoginModal';
import './UserHeader.css';

const UserHeader = () => {
    const { user, isLoggedIn, isLoading, isAdmin, logout } = useAuth();
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = async () => {
        setShowDropdown(false);
        await logout();
    };

    if (isLoading) {
        return (
            <div className="user-header">
                <div className="user-header-loading">...</div>
            </div>
        );
    }

    return (
        <>
            <div className="user-header">
                {isLoggedIn ? (
                    <div className="user-menu" ref={dropdownRef}>
                        <button
                            className="user-menu-btn"
                            onClick={() => setShowDropdown(!showDropdown)}
                        >
                            <span className="user-avatar">
                                {isAdmin ? '👑' : '👤'}
                            </span>
                            <span className="user-name">{user?.username}</span>
                            <span className="dropdown-arrow">▼</span>
                        </button>

                        {showDropdown && (
                            <div className="user-dropdown">
                                <div className="dropdown-header">
                                    <span className="dropdown-username">{user?.username}</span>
                                    {isAdmin && <span className="admin-badge">Admin</span>}
                                </div>
                                <div className="dropdown-divider"></div>
                                <button className="dropdown-item logout-btn" onClick={handleLogout}>
                                    🚪 Sign Out
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <button
                        className="sign-in-btn"
                        onClick={() => setShowLoginModal(true)}
                    >
                        <span className="sign-in-icon">🔐</span>
                        <span className="sign-in-text">Sign In</span>
                    </button>
                )}
            </div>

            <LoginModal
                isOpen={showLoginModal}
                onClose={() => setShowLoginModal(false)}
            />
        </>
    );
};

export default UserHeader;
