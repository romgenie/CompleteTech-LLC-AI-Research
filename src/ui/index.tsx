/**
 * Module Testing Entry Point
 */
import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import KnowledgeGraphTest from './KnowledgeGraphTest';

// Create a theme instance
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Find the root element
const container = document.getElementById('root');

// Make sure container exists
if (!container) {
  throw new Error('Root element not found');
}

// Create a root
const root = createRoot(container);

// Render the app
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <KnowledgeGraphTest />
    </ThemeProvider>
  </React.StrictMode>
);