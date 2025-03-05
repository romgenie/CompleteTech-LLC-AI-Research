# High Contrast Mode Implementation

This document describes the implementation of high contrast mode in the AI Research Integration Platform, a feature designed to enhance accessibility for users with visual impairments or those who prefer higher contrast interfaces.

## Overview

High contrast mode provides alternative color schemes with significantly higher contrast ratios, clearer element boundaries, and improved visual distinction between different UI elements. We've implemented two high contrast themes:

1. **High Contrast Light** - White background with black text and strong color accents
2. **High Contrast Dark** - Black background with white text and bright color accents

## Implementation Details

### Theme System

The application uses a comprehensive theming system with four distinct themes:

1. Standard Light
2. Standard Dark
3. High Contrast Light
4. High Contrast Dark

Each theme has been carefully designed to meet WCAG 2.1 AA accessibility standards, with contrast ratios of at least 4.5:1 for normal text and 3:1 for large text.

### Key Features

1. **ThemeContext** - A React context that manages theme state and provides toggle functions:
   - `toggleDarkMode()` - Switches between light and dark modes
   - `toggleHighContrast()` - Toggles high contrast within the current light/dark mode
   - `setThemeMode()` - Directly sets a specific theme

2. **Local Storage Persistence** - User preferences are saved in localStorage so they persist between sessions

3. **System Preference Detection** - The app checks for system dark mode preference on initial load

4. **Theme Toggle Component** - Provides an intuitive UI for changing theme settings:
   - Icon button in the app header
   - Expanded menu with direct mode selection
   - Switch controls for dark/light and high contrast toggles

5. **Knowledge Graph Specific Colors** - Special high contrast color schemes for the knowledge graph visualization that maintain semantic meaning while improving contrast

### Color Schemes

#### Standard Themes
- **Light**: Blue primary (#1976d2), Purple secondary (#7B1FA2), Light background (#f5f5f5)
- **Dark**: Light Blue primary (#90caf9), Light Purple secondary (#ce93d8), Dark background (#121212)

#### High Contrast Themes
- **High Contrast Light**: Black primary (#000000), Deep Blue secondary (#000099), White background (#ffffff)
- **High Contrast Dark**: White primary (#ffffff), Yellow secondary (#ffff00), Black background (#000000)

### Visual Enhancements

In high contrast mode, we:

1. **Add Borders** - Clear borders around interactive elements like buttons and cards
2. **Increase Font Weight** - Slightly heavier fonts for better readability
3. **Reduce Border Radius** - More angular corners for clearer boundaries
4. **Underline Links** - Always show underlines for better link identification
5. **Simplify Background Patterns** - Remove subtle patterns/gradients that might reduce contrast

## Knowledge Graph Visualization

The knowledge graph visualization required special attention to ensure accessibility:

1. **Specialized Color Schemes** - Entity types maintain consistent semantic meaning across themes:
   - MODEL: Blue → Deep Blue (HC Light) → Light Blue (HC Dark)
   - DATASET: Green → Dark Green (HC Light) → Light Green (HC Dark)
   - Etc.

2. **Thicker Borders** - Node borders increase in thickness in high contrast mode
3. **Simpler Visual Effects** - Reduced shadows and glows in favor of clearer boundaries
4. **Accessibility Component** - A dedicated component shows the current contrast mode and helps with keyboard navigation

## Testing and Validation

The high contrast themes have been tested for:

1. **Contrast Ratios** - Using the WCAG contrast checker to ensure all text meets AA standards
2. **Color Blindness** - Using color blindness simulators to ensure information is not lost
3. **Screen Reader Compatibility** - Ensuring screen readers correctly announce theme changes

## Usage Guidelines

For users with low vision or who prefer high contrast:

1. Click the theme settings icon in the app header (gear icon)
2. Toggle "High Contrast" on
3. Choose between light and dark variants based on preference

Users can also use operating system settings (like Windows High Contrast Mode or macOS Increase Contrast) alongside our app's high contrast mode for even stronger visual differentiation.

## Future Improvements

1. **Text Size Controls** - Add UI controls to increase text size
2. **Color Customization** - Allow users to customize specific color aspects
3. **Keyboard Shortcut** - Add a keyboard shortcut for toggling high contrast mode
4. **Focus Indicators** - Enhance focus indicators for keyboard navigation