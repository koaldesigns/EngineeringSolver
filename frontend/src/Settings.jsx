import React, { useState, useEffect } from 'react';
import './Settings.css';

const Settings = () => {
    const [activeSection, setActiveSection] = useState('appearance');

    // Theme mode (light/dark) with localStorage persistence
    const [themeMode, setThemeMode] = useState(() => {
        const saved = localStorage.getItem('themeMode');
        return saved || 'dark';
    });

    // Accent color customization
    const [hue, setHue] = useState(() => {
        const saved = localStorage.getItem('accentHue');
        return saved ? Number(saved) : 25;
    });
    const [brightness, setBrightness] = useState(() => {
        const saved = localStorage.getItem('accentBrightness');
        return saved ? Number(saved) : 40;  // Burnt orange #CC5500
    });

    const sections = [
        { id: 'appearance', title: 'Appearance', icon: '🎨' },
        { id: 'general', title: 'General', icon: '⚙️' },
        { id: 'editor', title: 'Editor', icon: '✏️' },
        { id: 'about', title: 'About', icon: 'ℹ️' },
    ];

    // Helper to convert HSL to Hex
    const hslToHex = (h, s, l) => {
        l /= 100;
        const a = s * Math.min(l, 1 - l) / 100;
        const f = n => {
            const k = (n + h / 30) % 12;
            const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
            return Math.round(255 * color).toString(16).padStart(2, '0');
        };
        return `#${f(0)}${f(8)}${f(4)}`;
    };

    // Helper to convert HSL to RGB numbers
    const hslToRgbValues = (h, s, l) => {
        l /= 100;
        const a = s * Math.min(l, 1 - l) / 100;
        const f = n => {
            const k = (n + h / 30) % 12;
            const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
            return Math.round(255 * color);
        };
        return [f(0), f(8), f(4)];
    };


    const updateAccentColor = (h, b) => {
        // Assume Saturation is constant for vibrant colors, e.g., 90%
        const s = 90;

        // Primary Accent
        const hex = hslToHex(h, s, b);

        // Hover variant (slightly lighter or different saturation)
        const hoverHex = hslToHex(h, s, Math.min(b + 10, 100));

        // Glow (rgba)
        const [r, g, br] = hslToRgbValues(h, s, b);
        const glow = `rgba(${r}, ${g}, ${br}, 0.15)`;
        const subtle = `rgba(${r}, ${g}, ${br}, 0.08)`;

        document.documentElement.style.setProperty('--accent-primary', hex);
        document.documentElement.style.setProperty('--accent-hover', hoverHex);
        document.documentElement.style.setProperty('--accent-glow', glow);
        document.documentElement.style.setProperty('--accent-subtle', subtle);

        // Persist to localStorage
        localStorage.setItem('accentHue', h.toString());
        localStorage.setItem('accentBrightness', b.toString());
    };

    // Apply theme mode to document
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', themeMode);
        localStorage.setItem('themeMode', themeMode);
    }, [themeMode]);

    useEffect(() => {
        updateAccentColor(hue, brightness);
    }, [hue, brightness]);

    const handleReset = () => {
        setHue(25);
        setBrightness(50);
    };

    const renderSection = () => {
        switch (activeSection) {
            case 'appearance':
                return (
                    <AppearanceSection
                        themeMode={themeMode}
                        setThemeMode={setThemeMode}
                        hue={hue}
                        setHue={setHue}
                        brightness={brightness}
                        setBrightness={setBrightness}
                        handleReset={handleReset}
                    />
                );
            case 'general':
                return <GeneralSection />;
            case 'editor':
                return <EditorSection />;
            case 'about':
                return <AboutSection />;
            default:
                return (
                    <AppearanceSection
                        themeMode={themeMode}
                        setThemeMode={setThemeMode}
                        hue={hue}
                        setHue={setHue}
                        brightness={brightness}
                        setBrightness={setBrightness}
                        handleReset={handleReset}
                    />
                );
        }
    };

    return (
        <div className="settings-container">
            <div className="settings-header">
                <h1>⚙️ Settings</h1>
                <p>Configure your solver preferences and appearance</p>
            </div>

            <div className="settings-layout">
                <nav className="settings-nav">
                    {sections.map((section) => (
                        <button
                            key={section.id}
                            className={`settings-nav-item ${activeSection === section.id ? 'active' : ''}`}
                            onClick={() => setActiveSection(section.id)}
                        >
                            <span className="nav-icon">{section.icon}</span>
                            <span className="nav-label">{section.title}</span>
                        </button>
                    ))}
                </nav>

                <div className="settings-content">
                    {renderSection()}
                </div>
            </div>
        </div>
    );
};

// ============================================================================
// SECTION COMPONENTS
// ============================================================================

const AppearanceSection = ({ themeMode, setThemeMode, hue, setHue, brightness, setBrightness, handleReset }) => (
    <div className="settings-section-content">
        <h2>🎨 Appearance Settings</h2>

        <div className="settings-info-card highlight">
            <h3>Theme Customization</h3>
            <p>
                Personalize the look of your equation solver by adjusting the theme and accent color.
                Changes are applied in real-time across the entire application.
            </p>
        </div>

        <h3>Theme Mode</h3>
        <div className="settings-group">
            <div className="control-group">
                <label>Color Theme</label>
                <p className="control-description">Switch between light and dark interface themes</p>
                <div className="theme-toggle-container">
                    <button
                        className={`theme-toggle-btn ${themeMode === 'dark' ? 'active' : ''}`}
                        onClick={() => setThemeMode('dark')}
                    >
                        <span className="theme-icon">🌙</span>
                        <span className="theme-label">Dark</span>
                    </button>
                    <button
                        className={`theme-toggle-btn ${themeMode === 'light' ? 'active' : ''}`}
                        onClick={() => setThemeMode('light')}
                    >
                        <span className="theme-icon">☀️</span>
                        <span className="theme-label">Light</span>
                    </button>
                </div>
            </div>
        </div>

        <h3>Accent Color</h3>
        <div className="settings-group">
            <div className="control-group">
                <label>Color Hue</label>
                <p className="control-description">Select the primary color for buttons, indicators, and highlights</p>
                <div className="slider-container">
                    <input
                        type="range"
                        min="0"
                        max="360"
                        value={hue}
                        onChange={(e) => setHue(Number(e.target.value))}
                        className="hue-slider"
                    />
                    <span className="slider-value">{hue}°</span>
                </div>
            </div>

            <div className="control-group">
                <label>Brightness</label>
                <p className="control-description">Adjust the lightness/darkness of the accent color</p>
                <div className="slider-container">
                    <input
                        type="range"
                        min="20"
                        max="80"
                        value={brightness}
                        onChange={(e) => setBrightness(Number(e.target.value))}
                        className="brightness-slider"
                    />
                    <span className="slider-value">{brightness}%</span>
                </div>
            </div>
        </div>

        <h3>Preview</h3>
        <div className="preview-box">
            <button className="preview-button">
                Preview Button
            </button>
            <p className="preview-text">
                This is how accent elements will appear throughout the application.
            </p>
        </div>

        <div className="action-row">
            <button onClick={handleReset} className="reset-button">
                ↺ Reset to Default
            </button>
        </div>
    </div>
);

const GeneralSection = () => (
    <div className="settings-section-content">
        <h2>⚙️ General Settings</h2>

        <div className="settings-info-card">
            <h3>Coming Soon</h3>
            <p>
                General configuration options will be available in a future update.
                This will include preferences for default units, number formatting, and more.
            </p>
        </div>

        <h3>Planned Features</h3>
        <div className="feature-list">
            <div className="feature-item disabled">
                <span className="feature-icon">📏</span>
                <div className="feature-info">
                    <h4>Default Unit System</h4>
                    <p>Choose between SI, Imperial, or custom unit defaults</p>
                </div>
            </div>
            <div className="feature-item disabled">
                <span className="feature-icon">🔢</span>
                <div className="feature-info">
                    <h4>Number Precision</h4>
                    <p>Set default decimal places for result display</p>
                </div>
            </div>
            <div className="feature-item disabled">
                <span className="feature-icon">💾</span>
                <div className="feature-info">
                    <h4>Auto-save</h4>
                    <p>Automatically save your work at regular intervals</p>
                </div>
            </div>
        </div>
    </div>
);

const EditorSection = () => (
    <div className="settings-section-content">
        <h2>✏️ Editor Settings</h2>

        <div className="settings-info-card">
            <h3>Coming Soon</h3>
            <p>
                Editor customization options will be available in a future update.
                Configure font sizes, key bindings, and auto-completion behavior.
            </p>
        </div>

        <h3>Planned Features</h3>
        <div className="feature-list">
            <div className="feature-item disabled">
                <span className="feature-icon">🔤</span>
                <div className="feature-info">
                    <h4>Font Size</h4>
                    <p>Adjust the editor font size for comfortable viewing</p>
                </div>
            </div>
            <div className="feature-item disabled">
                <span className="feature-icon">⌨️</span>
                <div className="feature-info">
                    <h4>Key Bindings</h4>
                    <p>Customize keyboard shortcuts for common actions</p>
                </div>
            </div>
            <div className="feature-item disabled">
                <span className="feature-icon">💡</span>
                <div className="feature-info">
                    <h4>Auto-completion</h4>
                    <p>Configure intelligent code completion settings</p>
                </div>
            </div>
        </div>
    </div>
);

const AboutSection = () => (
    <div className="settings-section-content">
        <h2>ℹ️ About</h2>

        <div className="settings-info-card highlight">
            <h3>Engineering Equation Solver</h3>
            <p>
                A powerful numerical solver designed for engineering calculations.
                Combining equation solving with automatic unit tracking, thermodynamic
                property lookups, and dimensional analysis.
            </p>
        </div>

        <h3>Features</h3>
        <div className="about-features">
            <div className="about-feature">
                <span className="about-icon">🔢</span>
                <span>Multi-equation solving</span>
            </div>
            <div className="about-feature">
                <span className="about-icon">📏</span>
                <span>Automatic unit tracking</span>
            </div>
            <div className="about-feature">
                <span className="about-icon">🌡️</span>
                <span>CoolProp integration</span>
            </div>
            <div className="about-feature">
                <span className="about-icon">⚠️</span>
                <span>Unit validation warnings</span>
            </div>
        </div>

        <h3>Technologies</h3>
        <div className="tech-list">
            <span className="tech-badge">React</span>
            <span className="tech-badge">Python</span>
            <span className="tech-badge">Flask</span>
            <span className="tech-badge">Pint</span>
            <span className="tech-badge">CoolProp</span>
            <span className="tech-badge">SciPy</span>
        </div>

        <div className="settings-info-card">
            <h4>Version</h4>
            <p style={{ fontFamily: 'monospace' }}>1.0.0</p>
        </div>
    </div>
);

export default Settings;
