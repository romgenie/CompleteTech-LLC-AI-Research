// Add fetch polyfill for tests
require('whatwg-fetch');

// Add testing-library jest-dom matchers
require('@testing-library/jest-dom');

// Suppress console errors/warnings in tests
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = (...args) => {
    if (
      /Warning: ReactDOM.render is no longer supported in React 18/.test(args[0]) ||
      /Warning: useLayoutEffect does nothing on the server/.test(args[0])
    ) {
      return;
    }
    originalConsoleError.call(console, ...args);
  };

  console.warn = (...args) => {
    if (
      /Warning: React.createElement: type is invalid/.test(args[0]) ||
      /Warning: Failed prop type/.test(args[0])
    ) {
      return;
    }
    originalConsoleWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});