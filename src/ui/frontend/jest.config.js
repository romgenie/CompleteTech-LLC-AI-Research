module.exports = {
  // Test environment for React components
  testEnvironment: 'jsdom',
  
  // File extensions to process with Jest
  moduleFileExtensions: ['js', 'jsx'],
  
  // Transform files with Babel for ES6 support
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },
  
  // Mock CSS and image imports
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/__mocks__/styleMock.js',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  
  // Setup files to run before tests
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  
  // Coverage settings
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/**/*.d.ts',
    '!src/**/index.{js,jsx}',
    '!src/serviceWorker.js',
    '!src/setupTests.js',
  ],
  
  // Coverage output directory
  coverageDirectory: 'coverage',
  
  // Minimum code coverage percentages
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  
  // Don't watch for changes in node_modules
  watchPathIgnorePatterns: ['<rootDir>/node_modules/'],
};