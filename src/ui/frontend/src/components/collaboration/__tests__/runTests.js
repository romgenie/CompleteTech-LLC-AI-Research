/**
 * Test runner script for collaboration components
 */
const { execSync } = require('child_process');

console.log('Running collaboration component tests...\n');

try {
  // Run Jest tests for all files in this directory
  execSync('npx jest --config=jest.config.js ./src/components/collaboration/__tests__', 
    { stdio: 'inherit' }
  );
  
  console.log('\nAll collaboration tests completed successfully!');
} catch (error) {
  console.error('\nError running collaboration tests:', error.message);
  process.exit(1);
}