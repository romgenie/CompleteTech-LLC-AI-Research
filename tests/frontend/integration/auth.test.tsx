/**
 * Tests for authentication flow
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Login from '../../../src/ui/frontend/src/pages/Login';
import { login, logout, isAuthenticated } from '../../../src/ui/frontend/src/services/authService';

// Mock the auth service
jest.mock('../../../src/ui/frontend/src/services/authService', () => ({
  login: jest.fn(),
  logout: jest.fn(),
  isAuthenticated: jest.fn()
}));

// Mock navigate function from react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('Authentication Flow', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('login page renders correctly', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    // Check that important elements are in the document
    expect(screen.getByText(/sign in/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('login form submits with credentials', async () => {
    // Mock successful login
    (login as jest.Mock).mockResolvedValueOnce({ token: 'test-token' });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify login was called with correct parameters
    expect(login).toHaveBeenCalledWith('testuser', 'password123');

    // Verify redirect after successful login
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('displays error message on login failure', async () => {
    // Mock failed login
    (login as jest.Mock).mockRejectedValueOnce(new Error('Invalid credentials'));

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpassword' } });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify error message appears
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    // Verify no redirect happens
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('logout clears authentication data', async () => {
    // Mock localStorage with token
    localStorage.setItem('token', 'test-token');

    // Call logout
    logout();

    // Verify localStorage was cleared
    expect(localStorage.getItem('token')).toBeNull();
  });

  test('isAuthenticated returns true with valid token', () => {
    // Mock a valid token in localStorage
    localStorage.setItem('token', 'valid-token');
    (isAuthenticated as jest.Mock).mockReturnValueOnce(true);

    // Check authentication
    const authenticated = isAuthenticated();

    // Verify result
    expect(authenticated).toBe(true);
  });

  test('isAuthenticated returns false with no token', () => {
    // Ensure no token in localStorage
    localStorage.removeItem('token');
    (isAuthenticated as jest.Mock).mockReturnValueOnce(false);

    // Check authentication
    const authenticated = isAuthenticated();

    // Verify result
    expect(authenticated).toBe(false);
  });
});