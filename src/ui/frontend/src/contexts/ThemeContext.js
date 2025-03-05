import React, { createContext, useContext, useState, useEffect } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { lightTheme, darkTheme, highContrastLightTheme, highContrastDarkTheme } from '../theme';
import useLocalStorage from '../hooks/useLocalStorage';

// Define theme modes
export const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  HIGH_CONTRAST_LIGHT: 'highContrastLight',
  HIGH_CONTRAST_DARK: 'highContrastDark',
};

// Create the context
const ThemeContext = createContext({
  themeMode: THEME_MODES.LIGHT,
  setThemeMode: () => {},
  isHighContrast: false,
  toggleHighContrast: () => {},
  isDarkMode: false,
  toggleDarkMode: () => {},
});

/**
 * Theme Provider Component
 * Manages theme state and provides theme toggle functions
 */
export const ThemeProvider = ({ children }) => {
  // Use localStorage to persist theme preference
  const [themeMode, setThemeMode] = useLocalStorage('themeMode', THEME_MODES.LIGHT);
  
  // Compute current theme based on mode
  const currentTheme = (() => {
    switch (themeMode) {
      case THEME_MODES.DARK:
        return darkTheme;
      case THEME_MODES.HIGH_CONTRAST_LIGHT:
        return highContrastLightTheme;
      case THEME_MODES.HIGH_CONTRAST_DARK:
        return highContrastDarkTheme;
      default:
        return lightTheme;
    }
  })();

  // Derived state
  const isDarkMode = themeMode === THEME_MODES.DARK || themeMode === THEME_MODES.HIGH_CONTRAST_DARK;
  const isHighContrast = themeMode === THEME_MODES.HIGH_CONTRAST_LIGHT || themeMode === THEME_MODES.HIGH_CONTRAST_DARK;

  // Toggle functions
  const toggleDarkMode = () => {
    if (isHighContrast) {
      setThemeMode(isDarkMode ? THEME_MODES.HIGH_CONTRAST_LIGHT : THEME_MODES.HIGH_CONTRAST_DARK);
    } else {
      setThemeMode(isDarkMode ? THEME_MODES.LIGHT : THEME_MODES.DARK);
    }
  };

  const toggleHighContrast = () => {
    if (isDarkMode) {
      setThemeMode(isHighContrast ? THEME_MODES.DARK : THEME_MODES.HIGH_CONTRAST_DARK);
    } else {
      setThemeMode(isHighContrast ? THEME_MODES.LIGHT : THEME_MODES.HIGH_CONTRAST_LIGHT);
    }
  };

  // Check for system preference on mount
  useEffect(() => {
    // Only apply if user hasn't set a preference yet
    if (!localStorage.getItem('themeMode') && window.matchMedia) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        setThemeMode(THEME_MODES.DARK);
      }
    }
  }, [setThemeMode]);

  return (
    <ThemeContext.Provider
      value={{
        themeMode,
        setThemeMode,
        isHighContrast,
        toggleHighContrast,
        isDarkMode,
        toggleDarkMode,
      }}
    >
      <MuiThemeProvider theme={currentTheme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

/**
 * Custom hook to use the theme context
 */
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;