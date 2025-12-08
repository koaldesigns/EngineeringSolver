import { useState, useEffect, useCallback } from 'react'
import Sidebar from './Sidebar'
import EquationEditor from './EquationEditor'
import Documentation from './Documentation'
import Instructions from './Instructions'
import StressTests from './StressTests'
import Settings from './Settings'
import { CustomTabView } from './CustomTabs'
import { getCustomTabs, saveCustomTabs, importCustomTab, exportCustomTab } from './api'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('editor')
  const [equations, setEquations] = useState('')
  const [customTabs, setCustomTabs] = useState([])
  const [isSaving, setIsSaving] = useState(false)

  // Load custom tabs on startup
  useEffect(() => {
    const loadTabs = async () => {
      try {
        const data = await getCustomTabs();
        setCustomTabs(data.tabs || []);
      } catch (err) {
        console.error('Failed to load custom tabs:', err);
      }
    };
    loadTabs();
  }, []);

  // Save custom tabs with debouncing
  const saveTabsToBackend = useCallback(async (tabs) => {
    if (isSaving) return;
    setIsSaving(true);
    try {
      await saveCustomTabs({ tabs });
    } catch (err) {
      console.error('Failed to save custom tabs:', err);
    } finally {
      setIsSaving(false);
    }
  }, [isSaving]);

  // Debounce save on customTabs change
  useEffect(() => {
    const timer = setTimeout(() => {
      if (customTabs.length > 0 || localStorage.getItem('customTabsInitialized')) {
        saveTabsToBackend(customTabs);
        localStorage.setItem('customTabsInitialized', 'true');
      }
    }, 1000);
    return () => clearTimeout(timer);
  }, [customTabs, saveTabsToBackend]);

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
    } catch (err) {
      console.error('Failed to export tab:', err);
      alert('Failed to export tab: ' + err.message);
    }
  };

  const handleImportTab = async (tabData) => {
    try {
      const result = await importCustomTab(tabData);
      // Refresh tabs from backend to get the new tab with resolved ID
      const data = await getCustomTabs();
      setCustomTabs(data.tabs || []);
      setActiveTab(`custom_${result.tab.id}`);
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

export default App
