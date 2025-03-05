import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';

import { ErrorBoundary, LoadingFallback } from './components';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';
import { queryClient } from './utils/queryClient';

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Login = lazy(() => import('./pages/Login'));
const ResearchPage = lazy(() => import('./pages/ResearchPage'));
const ResearchPageOptimized = lazy(() => import('./pages/ResearchPageOptimized'));
const KnowledgeGraphPage = lazy(() => import('./pages/KnowledgeGraphPage'));
const ImplementationPage = lazy(() => import('./pages/ImplementationPage'));
const NotFound = lazy(() => import('./pages/NotFound'));

const App: React.FC = () => {
  const { loading } = useAuth();

  if (loading) {
    return <LoadingFallback fullPage message="Loading application..." />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app-container">
        <ErrorBoundary errorTitle="Application Error">
          <Suspense fallback={<LoadingFallback fullPage />}>
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
                  path="/research-optimized" 
                  element={
                    <ProtectedRoute>
                      <ResearchPageOptimized />
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
        </ErrorBoundary>
      </div>
    </QueryClientProvider>
  );
}

export default App;