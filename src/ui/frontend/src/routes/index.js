import React from 'react';
import { Navigate } from 'react-router-dom';

// Import route configurations
import collaborationRoutes from './collaborationRoutes';

// Import layout components
import MainLayout from '../layouts/MainLayout';

// Import page components
import Dashboard from '../pages/Dashboard';
import NotFound from '../pages/NotFound';

/**
 * Main application routes configuration
 */
const routes = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { path: '/', element: <Navigate to="/dashboard" /> },
      { path: 'dashboard', element: <Dashboard /> },
      
      // Include collaboration routes
      ...collaborationRoutes,
      
      // Add other route groups here
      
      // 404 Not Found route
      { path: '*', element: <NotFound /> }
    ]
  }
];

export default routes;