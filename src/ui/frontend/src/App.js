import React from 'react';
import { 
  BrowserRouter, 
  Routes, 
  Route,
  Navigate,
  useRoutes
} from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';

// Import theme
import theme from './theme';

// Import routes configuration
import routes from './routes';

/**
 * Main App component that sets up routing and theming
 */
const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ThemeProvider>
  );
};

/**
 * Component to render routes from configuration
 */
const AppRoutes = () => {
  // Use the routes configuration to generate React Router routes
  const routeElements = useRoutes(routes);
  
  return routeElements;
};

export default App;