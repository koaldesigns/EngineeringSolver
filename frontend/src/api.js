// Use environment variable for production, fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ============== Auth Token Management ==============

const TOKEN_KEY = 'authToken';

export const getAuthToken = () => localStorage.getItem(TOKEN_KEY);
export const setAuthToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearAuthToken = () => localStorage.removeItem(TOKEN_KEY);

const getAuthHeaders = () => {
    const token = getAuthToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};


// ============== Health Check ==============

export const checkHealth = async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        return await response.json();
    } catch (error) {
        console.error("API Health Check Failed:", error);
        return { status: "error", message: error.message };
    }
};


// ============== Authentication API ==============

export const register = async (username, password, token) => {
    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, token }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }

        // Store the token
        setAuthToken(data.access_token);
        return data;
    } catch (error) {
        console.error("Registration Failed:", error);
        throw error;
    }
};

export const login = async (username, password) => {
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        // Store the token
        setAuthToken(data.access_token);
        return data;
    } catch (error) {
        console.error("Login Failed:", error);
        throw error;
    }
};

export const logout = async () => {
    try {
        await fetch(`${API_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
            },
        });
    } catch (error) {
        console.error("Logout request failed:", error);
    } finally {
        // Always clear the token locally
        clearAuthToken();
    }
};

export const getCurrentUser = async () => {
    const token = getAuthToken();
    if (!token) return null;

    try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            // Token is invalid, clear it
            clearAuthToken();
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error("Get Current User Failed:", error);
        clearAuthToken();
        return null;
    }
};

export const refreshSession = async () => {
    const token = getAuthToken();
    if (!token) return null;

    try {
        const response = await fetch(`${API_URL}/api/auth/refresh`, {
            method: 'POST',
            headers: {
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            return null;
        }

        const data = await response.json();
        setAuthToken(data.access_token);
        return data;
    } catch (error) {
        console.error("Refresh Session Failed:", error);
        return null;
    }
};


// ============== Equations API ==============

export const solveEquations = async (equations, angleUnit = "deg", outputUnits = null, arrayMode = "parallel") => {
    try {
        // Split by newlines and filter empty lines
        const equationList = equations.split('\n').filter(eq => eq.trim() !== '');

        const response = await fetch(`${API_URL}/api/solve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                equations: equationList,
                guesses: null,
                angle_unit: angleUnit,
                output_units: outputUnits,
                array_mode: arrayMode
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to solve equations');
        }

        return await response.json();
    } catch (error) {
        console.error("Solve Request Failed:", error);
        throw error;
    }
};


// ============== Unit Conversion API ==============

/**
 * Convert a value from one unit to another via the backend.
 * Uses Pint for robust compound unit support (e.g., m/s, kg/m^3, J/(kg*K)).
 * 
 * @param {number} value - The value to convert
 * @param {string} fromUnit - Source unit string
 * @param {string} toUnit - Target unit string
 * @returns {Promise<{success: boolean, value?: number, unit?: string, factor?: number, error?: string}>}
 */
export const convertUnitViaBackend = async (value, fromUnit, toUnit) => {
    try {
        const response = await fetch(`${API_URL}/api/convert-unit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                value: value,
                from_unit: fromUnit,
                to_unit: toUnit
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            return { success: false, error: errorData.detail || 'Conversion failed' };
        }

        return await response.json();
    } catch (error) {
        console.error("Unit Conversion Failed:", error);
        return { success: false, error: error.message };
    }
};

/**
 * Get compatible unit suggestions from the backend based on dimensional analysis.
 * Uses Pint to determine the dimensionality and returns common engineering units.
 * 
 * @param {string} unit - The source unit string
 * @returns {Promise<{success: boolean, suggestions: string[], error?: string}>}
 */
export const getUnitSuggestions = async (unit) => {
    try {
        const response = await fetch(`${API_URL}/api/unit-suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ unit }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            return { success: false, suggestions: [], error: errorData.detail || 'Failed to get suggestions' };
        }

        return await response.json();
    } catch (error) {
        console.error("Get Unit Suggestions Failed:", error);
        return { success: false, suggestions: [], error: error.message };
    }
};


// ============== Custom Tabs API ==============

export const getCustomTabs = async () => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs`, {
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            throw new Error('Failed to load custom tabs');
        }
        return await response.json();
    } catch (error) {
        console.error("Load Custom Tabs Failed:", error);
        return { tabs: [], logged_in: false };
    }
};

export const saveCustomTabs = async (tabsData) => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: JSON.stringify(tabsData),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to save custom tabs');
        }
        return await response.json();
    } catch (error) {
        console.error("Save Custom Tabs Failed:", error);
        throw error;
    }
};

export const exportCustomTab = async (tabId) => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs/export/${tabId}`, {
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            throw new Error('Failed to export tab');
        }
        return await response.json();
    } catch (error) {
        console.error("Export Custom Tab Failed:", error);
        throw error;
    }
};

export const importCustomTab = async (tabData) => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs/import`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: JSON.stringify({ tab: tabData }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to import tab');
        }
        return await response.json();
    } catch (error) {
        console.error("Import Custom Tab Failed:", error);
        throw error;
    }
};


// ============== User Preferences API ==============

export const getPreferences = async () => {
    try {
        const response = await fetch(`${API_URL}/api/preferences`, {
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error("Get Preferences Failed:", error);
        return null;
    }
};

export const savePreferences = async (prefs) => {
    try {
        const response = await fetch(`${API_URL}/api/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: JSON.stringify(prefs),
        });
        if (!response.ok) {
            throw new Error('Failed to save preferences');
        }
        return await response.json();
    } catch (error) {
        console.error("Save Preferences Failed:", error);
        throw error;
    }
};


// ============== Admin API ==============

export const getAdminUsers = async () => {
    try {
        const response = await fetch(`${API_URL}/api/admin/users`, {
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            throw new Error('Failed to get users');
        }
        return await response.json();
    } catch (error) {
        console.error("Get Admin Users Failed:", error);
        throw error;
    }
};

export const deleteAdminUser = async (userId) => {
    try {
        const response = await fetch(`${API_URL}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete user');
        }
        return await response.json();
    } catch (error) {
        console.error("Delete Admin User Failed:", error);
        throw error;
    }
};

export const getAdminTokens = async () => {
    try {
        const response = await fetch(`${API_URL}/api/admin/tokens`, {
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            throw new Error('Failed to get tokens');
        }
        return await response.json();
    } catch (error) {
        console.error("Get Admin Tokens Failed:", error);
        throw error;
    }
};

export const getAdminStats = async () => {
    try {
        const response = await fetch(`${API_URL}/api/admin/stats`, {
            headers: {
                ...getAuthHeaders(),
            },
        });
        if (!response.ok) {
            throw new Error('Failed to get stats');
        }
        return await response.json();
    } catch (error) {
        console.error("Get Admin Stats Failed:", error);
        throw error;
    }
};
