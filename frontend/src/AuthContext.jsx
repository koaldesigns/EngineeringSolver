import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCurrentUser, login as apiLogin, logout as apiLogout, register as apiRegister, refreshSession } from './api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // Check for existing session on mount
    useEffect(() => {
        const checkSession = async () => {
            try {
                const userData = await getCurrentUser();
                if (userData) {
                    setUser(userData);
                    setIsLoggedIn(true);
                }
            } catch (error) {
                console.error('Session check failed:', error);
            } finally {
                setIsLoading(false);
            }
        };
        checkSession();
    }, []);

    // Refresh session periodically (every 30 minutes while active)
    useEffect(() => {
        if (!isLoggedIn) return;

        const refreshInterval = setInterval(async () => {
            try {
                const result = await refreshSession();
                if (!result) {
                    // Session expired
                    setUser(null);
                    setIsLoggedIn(false);
                }
            } catch (error) {
                console.error('Session refresh failed:', error);
            }
        }, 30 * 60 * 1000); // 30 minutes

        return () => clearInterval(refreshInterval);
    }, [isLoggedIn]);

    const login = useCallback(async (username, password) => {
        const result = await apiLogin(username, password);
        setUser(result.user);
        setIsLoggedIn(true);
        return result;
    }, []);

    const register = useCallback(async (username, password, token) => {
        const result = await apiRegister(username, password, token);
        setUser(result.user);
        setIsLoggedIn(true);
        return result;
    }, []);

    const logout = useCallback(async () => {
        await apiLogout();
        setUser(null);
        setIsLoggedIn(false);
    }, []);

    const value = {
        user,
        isLoggedIn,
        isLoading,
        isAdmin: user?.is_admin || false,
        login,
        register,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
