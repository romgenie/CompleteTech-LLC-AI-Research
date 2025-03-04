import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container, Box, CircularProgress } from '@mui/material';

import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Login = lazy(() => import('./pages/Login'));
const ResearchPage = lazy(() => import('./pages/ResearchPage'));
const KnowledgeGraphPage = lazy(() => import('./pages/KnowledgeGraphPage'));
const ImplementationPage = lazy(() => import('./pages/ImplementationPage'));
const NotFound = lazy(() => import('./pages/NotFound'));

function App() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <div className="app-container">
      <Suspense 
        fallback={
          <Box 
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            minHeight="90vh"
          >
            <CircularProgress />
          </Box>
        }
      >
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes */}
          <Route element={<Layout />}>
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/research" 
              element={
                <ProtectedRoute>
                  <ResearchPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/knowledge-graph" 
              element={
                <ProtectedRoute>
                  <KnowledgeGraphPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/implementation" 
              element={
                <ProtectedRoute>
                  <ImplementationPage />
                </ProtectedRoute>
              } 
            />
          </Route>

          {/* Not Found and Redirect */}
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </Suspense>
    </div>
  );
}

export default App;