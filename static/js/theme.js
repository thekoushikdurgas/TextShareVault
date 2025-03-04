// Theme configuration
const themes = {
    light: {
        primary: '#2D3748',
        secondary: '#4A5568',
        background: '#F7FAFC',
        text: '#1A202C',
        accent: '#3182CE'
    },
    dark: {
        primary: '#1A202C',
        secondary: '#2D3748',
        background: '#171923',
        text: '#F7FAFC',
        accent: '#4299E1'
    },
    sepia: {
        primary: '#433422',
        secondary: '#5C4934',
        background: '#FDF5E6',
        text: '#2D2016',
        accent: '#8B5E34'
    },
    ocean: {
        primary: '#1B3A4B',
        secondary: '#2C5282',
        background: '#E6F3F8',
        text: '#1A365D',
        accent: '#2B6CB0'
    }
};

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.setupThemeSelector();
    }

    applyTheme(themeName) {
        const theme = themes[themeName];
        const root = document.documentElement;
        
        Object.entries(theme).forEach(([key, value]) => {
            root.style.setProperty(`--${key}`, value);
        });
        
        localStorage.setItem('theme', themeName);
        this.currentTheme = themeName;
        
        // Update theme selector if it exists
        const themeSelect = document.getElementById('themeSelect');
        if (themeSelect) {
            themeSelect.value = themeName;
        }
    }

    setupThemeSelector() {
        const themeSelect = document.getElementById('themeSelect');
        if (!themeSelect) return;

        themeSelect.addEventListener('change', (e) => {
            this.applyTheme(e.target.value);
        });
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});
