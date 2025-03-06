# TypeScript/JavaScript Compatibility Guide

This document describes how we maintain compatibility between TypeScript and JavaScript files in our codebase during the migration process.

## Key Challenges and Solutions

### 1. Type Assertions in JavaScript Files

**Problem**: TypeScript uses type assertions (e.g., `as Entity`, `as number`) which aren't valid JavaScript syntax.

**Solution**: Remove type assertions from JavaScript files. Instead:
- Use type-safe techniques that work in both environments
- For number conversions, use JavaScript Number() or parseInt() instead of "as number"
- For object typing, rely on runtime validation rather than compile-time assertions

### 2. TypeScript Interfaces in JavaScript Files

**Problem**: TypeScript interfaces defined inline in JavaScript files cause syntax errors.

**Solution**:
- Define interfaces in separate TypeScript files (usually in /src/types)
- Import the types in TypeScript files where needed
- JavaScript files should avoid declaring interfaces
- Use JSDoc comments in JavaScript files to document expected types

### 3. Generic Type Parameters

**Problem**: TypeScript generic syntax like `useState<string>()` isn't valid JavaScript.

**Solution**:
- Remove generic type parameters from JavaScript files
- Use plain JavaScript syntax: `useState()`
- Add JSDoc comments to document expected types

### 4. Error Boundary Components

**Problem**: React.cloneElement has different type checking between TypeScript and JavaScript.

**Solution**:
- Use defensive checking to avoid passing properties that may not exist
- Minimize props passed to fallback components
- Make fallback components adaptable to different props structures

### 5. D3.js Integration

**Problem**: D3.js has complex types that need special handling.

**Solution**:
- Created custom d3.d.ts with comprehensive type definitions
- Added simulation node types and selection types
- Used more generic parameters in JavaScript D3 code
- Removed specific type casts from D3 selections and simulations

## Best Practices for Mixed TypeScript/JavaScript Codebase

1. **Avoid TypeScript-specific syntax in .js files**
   - No interfaces, type aliases, generics, or type assertions

2. **Use JSDoc in JavaScript files for type documentation**
   - Document parameters, return types, and function descriptions

3. **Prefer functional patterns that work in both languages**
   - Object destructuring, default parameters, etc.

4. **Progressive migration approach**
   - Convert utilities and hooks first
   - Then convert components that depend on them
   - Finally convert pages that use those components

5. **Common type definitions**
   - Keep all type definitions in /src/types
   - Export types for use in TypeScript files
   - Document same types with JSDoc in JavaScript files

## Testing Compatibility

Before committing changes:
1. Run `npm run build` to check for TypeScript/JavaScript compatibility issues
2. Test functionality in development mode to ensure runtime behavior matches expectations
3. Verify that error boundaries and component hierarchies work correctly