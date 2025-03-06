// Jest configuration for frontend tests
module.exports = {
  // Root directory to search for tests
  rootDir: '../../',

  // Test files pattern
  testMatch: [
    '<rootDir>/tests/frontend/**/*.test.{js,jsx,ts,tsx}',
    '<rootDir>/src/ui/frontend/src/**/*.test.{js,jsx,ts,tsx}'
  ],

  // File extensions for modules
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json', 'node'],

  // Module name mapper for non-JS modules and aliases
  moduleNameMapper: {
    // Handle CSS imports
    '\\.css$': '<rootDir>/tests/frontend/mocks/styleMock.js',
    // Handle image imports
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/tests/frontend/mocks/fileMock.js',
    // Handle module aliases
    '^@/(.*)$': '<rootDir>/src/ui/frontend/src/$1'
  },

  // Setup files to run before tests
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setupTests.js'],

  // Test environment
  testEnvironment: 'jsdom',

  // Code coverage configuration
  coverageDirectory: '<rootDir>/coverage/frontend',
  collectCoverageFrom: [
    '<rootDir>/src/ui/frontend/src/**/*.{js,jsx,ts,tsx}',
    '!<rootDir>/src/ui/frontend/src/**/*.d.ts',
    '!<rootDir>/src/ui/frontend/src/**/index.{js,ts}',
    '!<rootDir>/src/ui/frontend/src/serviceWorker.{js,ts}',
    '!<rootDir>/src/ui/frontend/src/setupTests.{js,ts}'
  ],

  // Transform files
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { configFile: './tests/frontend/babel.config.js' }]
  },

  // Ignore transformations
  transformIgnorePatterns: [
    '/node_modules/(?!(@mui|d3|react-beautiful-dnd|dayjs|react-transition-group)/)'
  ],

  // Verbose output
  verbose: true
};