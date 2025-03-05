import { createTheme } from '@mui/material/styles';

// Standard light theme
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',  // Blue
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#7B1FA2',  // Purple
      light: '#9c27b0',
      dark: '#6a1b9a',
      contrastText: '#fff',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
    divider: 'rgba(0, 0, 0, 0.12)',
  },
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },
});

// Dark mode theme
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',  // Lighter blue for dark mode
      light: '#e3f2fd',
      dark: '#42a5f5',
      contrastText: '#000',
    },
    secondary: {
      main: '#ce93d8',  // Lighter purple for dark mode
      light: '#f3e5f5',
      dark: '#ab47bc',
      contrastText: '#000',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b0b0',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
  },
  // Same typography, shape, etc. as light theme
  ...lightTheme,
  components: {
    ...lightTheme.components,
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        },
      },
    },
  },
});

// High contrast light theme (for accessibility)
export const highContrastLightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#000000',  // Black
      light: '#333333',
      dark: '#000000',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#000099',  // Deep Blue
      light: '#0000cc',
      dark: '#000066',
      contrastText: '#ffffff',
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#000000',
      secondary: '#000000',
    },
    divider: '#000000',
    action: {
      active: '#000000',
      hover: 'rgba(0, 0, 0, 0.1)',
      selected: 'rgba(0, 0, 0, 0.2)',
      disabled: 'rgba(0, 0, 0, 0.3)',
      disabledBackground: 'rgba(0, 0, 0, 0.05)',
    },
  },
  typography: {
    ...lightTheme.typography,
    // Increase font weight for better visibility
    body1: {
      fontWeight: 500,
    },
    body2: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 4, // Reduced for better visual clarity
  },
  components: {
    ...lightTheme.components,
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 4,
          border: '2px solid black',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          boxShadow: '0 0 0 2px black',
          border: '1px solid black',
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        thumb: {
          border: '1px solid black',
        },
        track: {
          backgroundColor: '#cccccc', 
          border: '1px solid black',
        },
      },
    },
    MuiLink: {
      styleOverrides: {
        root: {
          textDecoration: 'underline',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          border: '1px solid black',
        },
      },
    },
  },
});

// High contrast dark theme (for accessibility)
export const highContrastDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ffffff',  // White
      light: '#ffffff',
      dark: '#cccccc',
      contrastText: '#000000',
    },
    secondary: {
      main: '#ffff00',  // Yellow
      light: '#ffff99',
      dark: '#cccc00',
      contrastText: '#000000',
    },
    background: {
      default: '#000000',
      paper: '#000000',
    },
    text: {
      primary: '#ffffff',
      secondary: '#ffffff',
    },
    divider: '#ffffff',
    action: {
      active: '#ffffff',
      hover: 'rgba(255, 255, 255, 0.2)',
      selected: 'rgba(255, 255, 255, 0.3)',
      disabled: 'rgba(255, 255, 255, 0.5)',
      disabledBackground: 'rgba(255, 255, 255, 0.1)',
    },
  },
  typography: {
    ...darkTheme.typography,
    // Increase font weight for better visibility
    body1: {
      fontWeight: 500,
    },
    body2: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 4, // Reduced for better visual clarity
  },
  components: {
    ...darkTheme.components,
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 4,
          border: '2px solid white',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          boxShadow: '0 0 0 2px white',
          border: '1px solid white',
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        thumb: {
          border: '1px solid white',
        },
        track: {
          backgroundColor: '#333333',
          border: '1px solid white',
        },
      },
    },
    MuiLink: {
      styleOverrides: {
        root: {
          textDecoration: 'underline',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          border: '1px solid white',
        },
      },
    },
  },
});

// Knowledge Graph specific color schemes for high contrast
export const knowledgeGraphColorSchemes = {
  standard: {
    MODEL: '#4285F4',      // Google Blue
    DATASET: '#34A853',    // Google Green
    ALGORITHM: '#EA4335',  // Google Red
    PAPER: '#FBBC05',      // Google Yellow
    AUTHOR: '#9C27B0',     // Purple
    CODE: '#00ACC1',       // Cyan
    default: '#757575'     // Gray
  },
  highContrastLight: {
    MODEL: '#000099',      // Deep Blue
    DATASET: '#006600',    // Dark Green
    ALGORITHM: '#990000',  // Dark Red
    PAPER: '#996600',      // Dark Yellow/Brown
    AUTHOR: '#660066',     // Dark Purple
    CODE: '#006666',       // Dark Teal
    default: '#000000'     // Black
  },
  highContrastDark: {
    MODEL: '#99ccff',      // Light Blue
    DATASET: '#99ff99',    // Light Green
    ALGORITHM: '#ff9999',  // Light Red
    PAPER: '#ffff99',      // Light Yellow
    AUTHOR: '#ff99ff',     // Light Magenta
    CODE: '#99ffff',       // Light Cyan
    default: '#ffffff'     // White
  }
});

// Custom theme configuration for the application
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButtonBase: {
      defaultProps: {
        disableRipple: true, // Disable ripple effect in tests
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

export default theme;