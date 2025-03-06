/**
 * Test utilities for React components
 */
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import theme from '../../../src/ui/frontend/src/theme';

// Define interface for custom render options
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
  initialState?: Record<string, any>;
}

/**
 * Custom render function that wraps the component with necessary providers
 * 
 * @param ui - The React element to render
 * @param options - Custom render options
 * @returns The rendered component with testing utilities
 */
const customRender = (
  ui: ReactElement,
  { 
    route = '/', 
    initialState = {}, 
    ...renderOptions 
  }: CustomRenderOptions = {}
) => {
  // Create wrapper with providers
  const AllProviders = ({ children }: { children: React.ReactNode }) => (
    <ThemeProvider theme={theme}>
      <MemoryRouter initialEntries={[route]}>
        {children}
      </MemoryRouter>
    </ThemeProvider>
  );

  return render(ui, { wrapper: AllProviders, ...renderOptions });
};

// Mock for localStorage
const mockLocalStorage = () => {
  const store: Record<string, string> = {};
  
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach(key => {
        delete store[key];
      });
    })
  };
};

// Mock for API responses
const mockApiResponse = (status: number, data: any, headers = {}) => {
  return new Response(JSON.stringify(data), {
    status,
    headers: new Headers(headers),
  });
};

/**
 * Creates a mock user event
 * 
 * @param type - The event type (e.g., 'click', 'change')
 * @param payload - The event payload
 * @returns The mock event object
 */
const createUserEvent = (type: string, payload: any = {}) => {
  return {
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
    target: payload,
    type,
    ...payload
  };
};

export {
  customRender as render,
  mockLocalStorage,
  mockApiResponse,
  createUserEvent
};