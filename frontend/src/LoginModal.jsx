import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from './AuthContext';
import './LoginModal.css';

const LoginModal = ({ isOpen, onClose }) => {
    const [mode, setMode] = useState('login'); // 'login' or 'register'
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [token, setToken] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { login, register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            if (mode === 'login') {
                await login(username, password);
            } else {
                if (!token.trim()) {
                    setError('Registration token is required');
                    setIsSubmitting(false);
                    return;
                }
                await register(username, password, token);
            }
            // Success - close modal
            onClose();
            // Reset form
            setUsername('');
            setPassword('');
            setToken('');
        } catch (err) {
            setError(err.message || 'An error occurred');
        } finally {
            setIsSubmitting(false);
        }
    };

    const switchMode = () => {
        setMode(mode === 'login' ? 'register' : 'login');
        setError('');
    };

    if (!isOpen) return null;

    // Use portal to render at document body level for proper centering
    return createPortal(
        <div className="login-modal-overlay" onClick={onClose}>
            <div className="login-modal" onClick={(e) => e.stopPropagation()}>
                <button className="login-modal-close" onClick={onClose}>×</button>

                <div className="login-modal-header">
                    <h2>{mode === 'login' ? '🔐 Sign In' : '📝 Create Account'}</h2>
                    <p className="login-modal-subtitle">
                        {mode === 'login'
                            ? 'Sign in to save your custom equation sets'
                            : 'Register with your invite token'
                        }
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                            minLength={3}
                            maxLength={50}
                            autoComplete="username"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                            required
                            minLength={4}
                            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                        />
                    </div>

                    {mode === 'register' && (
                        <div className="form-group">
                            <label htmlFor="token">Registration Token</label>
                            <input
                                type="text"
                                id="token"
                                value={token}
                                onChange={(e) => setToken(e.target.value.toUpperCase())}
                                placeholder="e.g., ENG-XXXXX-XXXXX"
                                required
                            />
                            <p className="form-hint">
                                Contact the administrator to receive an invite token
                            </p>
                        </div>
                    )}

                    {error && (
                        <div className="login-error">
                            ⚠️ {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="login-submit-btn"
                        disabled={isSubmitting}
                    >
                        {isSubmitting
                            ? 'Please wait...'
                            : (mode === 'login' ? 'Sign In' : 'Create Account')
                        }
                    </button>
                </form>

                <div className="login-modal-footer">
                    <p>
                        {mode === 'login'
                            ? "Don't have an account? "
                            : "Already have an account? "
                        }
                        <button type="button" className="switch-mode-btn" onClick={switchMode}>
                            {mode === 'login' ? 'Register' : 'Sign In'}
                        </button>
                    </p>
                </div>
            </div>
        </div>,
        document.body
    );
};

export default LoginModal;
