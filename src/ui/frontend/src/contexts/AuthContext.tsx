import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';
import authService from '../services/authService';
import { User, AuthState, JWTPayload } from '../types';

// Define interface for the AuthContext
interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
}

// Create context with default values
const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

// Auth provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    currentUser: null,
    token: localStorage.getItem('token'),
    loading: true,
    error: null,
    isAuthenticated: false
  });

  // Check if token is valid and not expired
  const isTokenValid = (token: string): boolean => {
    if (!token) return false;

    try {
      const decoded = jwtDecode<JWTPayload>(token);
      const currentTime = Date.now() / 1000;
      
      return decoded.exp > currentTime;
    } catch (err) {
      console.error('Error decoding token:', err);
      return false;
    }
  };

  // Initialize auth state
  useEffect(() => {
    const initAuth = async (): Promise<void> => {
      const storedToken = localStorage.getItem('token');
      
      if (storedToken && isTokenValid(storedToken)) {
        try {
          // Get user information
          const user = await authService.getUserInfo(storedToken);
          setState(prev => ({
            ...prev,
            currentUser: user,
            token: storedToken,
            isAuthenticated: true,
            loading: false
          }));
        } catch (err) {
          console.error('Failed to get user info:', err);
          logout();
          setState(prev => ({ ...prev, loading: false }));
        }
      } else if (storedToken) {
        // Token exists but is invalid
        logout();
        setState(prev => ({ ...prev, loading: false }));
      } else {
        setState(prev => ({ ...prev, loading: false }));
      }
    };

    initAuth();
  }, []);

  // Login function
  const login = async (username: string, password: string): Promise<User> => {
    try {
      setState(prev => ({ ...prev, error: null, loading: true }));
      const { token, user } = await authService.login(username, password);
      
      localStorage.setItem('token', token);
      setState({
        token,
        currentUser: user,
        loading: false,
        error: null,
        isAuthenticated: true
      });
      
      return user;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to login');
      setState(prev => ({ 
        ...prev, 
        error,
        loading: false,
        isAuthenticated: false
      }));
      throw error;
    }
  };

  // Logout function
  const logout = (): void => {
    localStorage.removeItem('token');
    setState({
      token: null,
      currentUser: null,
      loading: false,
      error: null,
      isAuthenticated: false
    });
  };

  // Value object to be provided
  const value: AuthContextType = {
    ...state,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for using auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;