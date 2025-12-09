/**
 * ConfirmedUnitsContext - Global state for unit confirmations with persistence
 * 
 * This context provides:
 * - Confirmed units state management
 * - Persistence to localStorage for all users
 * - Sync to server preferences when logged in
 */
import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from './AuthContext';
import { getPreferences, savePreferences } from './api';

const ConfirmedUnitsContext = createContext(null);

const STORAGE_KEY = 'confirmedUnits';

export const ConfirmedUnitsProvider = ({ children }) => {
    const [confirmedUnits, setConfirmedUnits] = useState(() => {
        // Load from localStorage on init
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : {};
        } catch {
            return {};
        }
    });

    const [serverLoaded, setServerLoaded] = useState(false);
    const saveTimeoutRef = useRef(null);
    const { isLoggedIn, isLoading: authLoading } = useAuth();

    // Persist to localStorage whenever confirmedUnits changes
    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(confirmedUnits));
        } catch (err) {
            console.error('Failed to save confirmed units to localStorage:', err);
        }
    }, [confirmedUnits]);

    // Load from server when logged in
    useEffect(() => {
        const loadFromServer = async () => {
            if (!isLoggedIn || authLoading) return;

            try {
                const prefs = await getPreferences();
                if (prefs?.extra_settings?.confirmed_units) {
                    // Merge server data with local data (local takes precedence for conflicts)
                    setConfirmedUnits(prev => ({
                        ...prefs.extra_settings.confirmed_units,
                        ...prev
                    }));
                }
                setServerLoaded(true);
            } catch (err) {
                console.error('Failed to load confirmed units from server:', err);
                setServerLoaded(true);
            }
        };
        loadFromServer();
    }, [isLoggedIn, authLoading]);

    // Save to server when confirmed units change (debounced)
    useEffect(() => {
        if (!isLoggedIn || !serverLoaded) return;

        // Clear pending save
        if (saveTimeoutRef.current) {
            clearTimeout(saveTimeoutRef.current);
        }

        // Debounce save to server
        saveTimeoutRef.current = setTimeout(async () => {
            try {
                await savePreferences({
                    extra_settings: {
                        confirmed_units: confirmedUnits
                    }
                });
            } catch (err) {
                console.error('Failed to save confirmed units to server:', err);
            }
        }, 2000); // 2 second debounce

        return () => {
            if (saveTimeoutRef.current) {
                clearTimeout(saveTimeoutRef.current);
            }
        };
    }, [confirmedUnits, isLoggedIn, serverLoaded]);

    const confirmUnit = useCallback((variable, unit) => {
        if (!variable || !unit) return;
        setConfirmedUnits(prev => ({ ...prev, [variable]: unit }));
    }, []);

    const unconfirmUnit = useCallback((variable) => {
        setConfirmedUnits(prev => {
            const next = { ...prev };
            delete next[variable];
            return next;
        });
    }, []);

    const isUnitConfirmed = useCallback((variable, unitSource, currentUnit) => {
        // Explicit units (defined in equation with [unit]) are always confirmed
        if (unitSource === 'explicit') return true;

        // Check if user confirmed THIS specific unit
        return confirmedUnits[variable] === currentUnit;
    }, [confirmedUnits]);

    // Prune variables that no longer exist (called by editors after solve)
    const pruneConfirmations = useCallback((existingVariables) => {
        const varSet = new Set(existingVariables);
        setConfirmedUnits(prev => {
            const next = { ...prev };
            let changed = false;
            Object.keys(next).forEach(variable => {
                if (!varSet.has(variable)) {
                    delete next[variable];
                    changed = true;
                }
            });
            return changed ? next : prev;
        });
    }, []);

    return (
        <ConfirmedUnitsContext.Provider value={{
            confirmedUnits,
            confirmUnit,
            unconfirmUnit,
            isUnitConfirmed,
            pruneConfirmations,
            setConfirmedUnits
        }}>
            {children}
        </ConfirmedUnitsContext.Provider>
    );
};

export const useConfirmedUnitsContext = () => {
    const context = useContext(ConfirmedUnitsContext);
    if (!context) {
        // If used outside provider, return a no-op version
        return {
            confirmedUnits: {},
            confirmUnit: () => { },
            unconfirmUnit: () => { },
            isUnitConfirmed: () => false,
            pruneConfirmations: () => { },
            setConfirmedUnits: () => { }
        };
    }
    return context;
};

export default ConfirmedUnitsContext;
