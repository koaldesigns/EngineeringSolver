import { useState, useEffect, useCallback } from 'react'
import { AuthProvider, useAuth } from './AuthContext'
import { ConfirmedUnitsProvider } from './ConfirmedUnitsContext'
import Sidebar from './Sidebar'
import EquationEditor from './EquationEditor'
import Documentation from './Documentation'
import Instructions from './Instructions'
import StressTests from './StressTests'
import Settings from './Settings'
import { CustomTabView } from './CustomTabs'
import { getCustomTabs, saveCustomTabs, importCustomTab, exportCustomTab } from './api'
import './App.css'

function AppContent() {
  const [activeTab, setActiveTab] = useState('editor')
  const [equations, setEquations] = useState('')
  const [customTabs, setCustomTabs] = useState([])
  const [isSaving, setIsSaving] = useState(false)
  const [isLoggedInForTabs, setIsLoggedInForTabs] = useState(false)

  const { isLoggedIn, isLoading } = useAuth()

  // Load custom tabs when login status changes
  useEffect(() => {
    const loadTabs = async () => {
      if (isLoading) return;

      try {
        const data = await getCustomTabs();
        setCustomTabs(data.tabs || []);
        setIsLoggedInForTabs(data.logged_in || false);
      } catch (err) {
        console.error('Failed to load custom tabs:', err);
      }
    };
    loadTabs();
  }, [isLoggedIn, isLoading]);

  // Save custom tabs with debouncing (only when logged in)
  const saveTabsToBackend = useCallback(async (tabs) => {
    if (isSaving || !isLoggedIn) return;
    setIsSaving(true);
    try {
      await saveCustomTabs({ tabs });
    } catch (err) {
      console.error('Failed to save custom tabs:', err);
    } finally {
      setIsSaving(false);
    }
  }, [isSaving, isLoggedIn]);

  // Debounce save on customTabs change (only when logged in)
  useEffect(() => {
    if (!isLoggedIn) return;

    const timer = setTimeout(() => {
      if (customTabs.length > 0) {
        saveTabsToBackend(customTabs);
      }
    }, 1000);
    return () => clearTimeout(timer);
  }, [customTabs, saveTabsToBackend, isLoggedIn]);

  const handleAddTab = (newTab) => {
    setCustomTabs(prev => [...prev, newTab]);
    setActiveTab(`custom_${newTab.id}`);
  };

  const handleUpdateTab = (updatedTab) => {
    setCustomTabs(prev => prev.map(tab =>
      tab.id === updatedTab.id ? updatedTab : tab
    ));
  };

  const handleDeleteTab = (tabId) => {
    setCustomTabs(prev => prev.filter(tab => tab.id !== tabId));
    setActiveTab('editor');
  };

  const handleExportTab = async (tabId) => {
    try {
      // For logged-in users, export from backend
      if (isLoggedIn) {
        const data = await exportCustomTab(tabId);
        const jsonStr = JSON.stringify(data.tab, null, 2);

        // Create and trigger download
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${data.tab.name.replace(/[^a-z0-9]/gi, '_')}_equations.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // For guests, export from local state
        const tab = customTabs.find(t => t.id === tabId);
        if (tab) {
          const jsonStr = JSON.stringify(tab, null, 2);
          const blob = new Blob([jsonStr], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${tab.name.replace(/[^a-z0-9]/gi, '_')}_equations.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }
      }
    } catch (err) {
      console.error('Failed to export tab:', err);
      alert('Failed to export tab: ' + err.message);
    }
  };

  const handleImportTab = async (tabData) => {
    try {
      if (isLoggedIn) {
        // For logged-in users, import via backend
        const result = await importCustomTab(tabData);
        // Refresh tabs from backend
        const data = await getCustomTabs();
        setCustomTabs(data.tabs || []);
        setActiveTab(`custom_${result.tab.id}`);
      } else {
        // For guests, import locally
        const newTab = { ...tabData, id: `${tabData.id}_${Date.now()}` };
        setCustomTabs(prev => [...prev, newTab]);
        setActiveTab(`custom_${newTab.id}`);
      }
    } catch (err) {
      console.error('Failed to import tab:', err);
      alert('Failed to import tab: ' + err.message);
    }
  };

  // Find active custom tab if viewing one
  const activeCustomTabId = activeTab.startsWith('custom_')
    ? activeTab.replace('custom_', '')
    : null;
  const activeCustomTab = activeCustomTabId
    ? customTabs.find(t => t.id === activeCustomTabId)
    : null;

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        customTabs={customTabs}
        onAddTab={handleAddTab}
        onImportTab={handleImportTab}
      />
      <main className="main-content">
        {activeTab === 'editor' && (
          <EquationEditor
            initialValue={equations}
            onValueChange={setEquations}
          />
        )}
        {activeTab === 'documentation' && (
          <Documentation />
        )}
        {activeTab === 'instructions' && (
          <Instructions />
        )}
        {activeTab === 'stresstests' && (
          <StressTests />
        )}
        {activeTab === 'settings' && (
          <Settings />
        )}

        {/* Custom tab views */}
        {activeCustomTab && (
          <CustomTabView
            tab={activeCustomTab}
            onUpdateTab={handleUpdateTab}
            onDeleteTab={handleDeleteTab}
            onExportTab={handleExportTab}
          />
        )}

        {/* Placeholder for unknown tabs */}
        {!activeCustomTab &&
          activeTab !== 'editor' &&
          activeTab !== 'documentation' &&
          activeTab !== 'instructions' &&
          activeTab !== 'stresstests' &&
          activeTab !== 'settings' && (
            <div className="placeholder-content">
              <h2>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h2>
              <p>This module is coming soon.</p>
            </div>
          )}
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <ConfirmedUnitsProvider>
        <AppContent />
      </ConfirmedUnitsProvider>
    </AuthProvider>
  )
}

export default App
