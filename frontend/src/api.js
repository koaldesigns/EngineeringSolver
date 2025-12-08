const API_URL = "http://localhost:8000";

export const checkHealth = async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        return await response.json();
    } catch (error) {
        console.error("API Health Check Failed:", error);
        return { status: "error", message: error.message };
    }
};

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


// ============== Custom Tabs API ==============

export const getCustomTabs = async () => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs`);
        if (!response.ok) {
            throw new Error('Failed to load custom tabs');
        }
        return await response.json();
    } catch (error) {
        console.error("Load Custom Tabs Failed:", error);
        return { tabs: [] };
    }
};

export const saveCustomTabs = async (tabsData) => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tabsData),
        });
        if (!response.ok) {
            throw new Error('Failed to save custom tabs');
        }
        return await response.json();
    } catch (error) {
        console.error("Save Custom Tabs Failed:", error);
        throw error;
    }
};

export const exportCustomTab = async (tabId) => {
    try {
        const response = await fetch(`${API_URL}/api/custom-tabs/export/${tabId}`);
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
            },
            body: JSON.stringify({ tab: tabData }),
        });
        if (!response.ok) {
            throw new Error('Failed to import tab');
        }
        return await response.json();
    } catch (error) {
        console.error("Import Custom Tab Failed:", error);
        throw error;
    }
};
