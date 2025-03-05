# Knowledge Graph Accessibility Guide

This guide describes the accessibility features of the Knowledge Graph visualization component and how to use them.

## Keyboard Navigation

The Knowledge Graph visualization can be fully navigated using the keyboard:

- **Arrow Keys** (←, →, ↑, ↓): Navigate between graph nodes
- **Home/End**: Jump to first/last node in the graph
- **Enter/Space**: Select the currently focused node
- **+/-**: Zoom in/out of the graph
- **0**: Reset zoom to default level
- **Escape**: Clear the current node focus

## Screen Reader Support

The Knowledge Graph visualization is optimized for screen readers with the following features:

- Proper ARIA attributes on all interactive elements
- Descriptive node labels with entity type information
- Relationship descriptions for understanding connections
- Configurable announcement verbosity levels
- Text-based alternative view for non-visual exploration

### Verbosity Settings

Three levels of screen reader verbosity are available:

1. **Minimal**: Only essential information about nodes and actions
2. **Detailed**: Adds context about node types and direct connections
3. **Verbose**: Complete information including detailed connectivity

## Visual Accommodations

Several visual accommodations are available:

### High Contrast Mode

Enables a high-contrast color scheme optimized for users with low vision:
- Stronger color contrast between nodes and background
- Bold outlines to distinguish nodes
- Enhanced text contrast for better readability

### Color Blind Modes

Three color blind modes address different types of color vision deficiency:
- **Deuteranopia**: Adjusts colors for red-green color blindness (most common)
- **Protanopia**: Alternative adjustments for red-green color blindness
- **Tritanopia**: Adjusts colors for blue-yellow color blindness

### Motion Reduction

Reduces or eliminates animations in the graph visualization:
- Disables transition animations between states
- Eliminates node movement during force simulation
- Provides static layout for users with motion sensitivity

### Text Size Controls

Customize the size of text labels in the visualization:
- Minimum font size setting ensures text is always readable
- Label visibility toggle for reducing visual complexity
- Enhanced label backgrounds for better contrast

## Text-Based Alternative View

For users who cannot use the visual graph, a text-based alternative is available:

- Lists all entities and their types
- Shows relationships between entities
- Provides filtering and searching capabilities
- Fully keyboard navigable

## Accessing Accessibility Settings

1. Click the **Accessibility** button (wheelchair icon) in the top-right of the graph interface
2. Use the dialog to configure accessibility settings
3. Apply changes to immediately update the visualization

## Feedback and Improvements

We are committed to continually improving accessibility. If you encounter any issues or have suggestions for improvements, please submit feedback through our issue tracking system.