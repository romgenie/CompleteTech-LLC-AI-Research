# Accessibility Statement

The AI Research Integration Platform is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone and applying the relevant accessibility standards.

## Conformance Status

The AI Research Integration Platform aims to conform to the Web Content Accessibility Guidelines (WCAG) 2.1 level AA. We have implemented numerous features to ensure that our platform is usable by everyone, regardless of ability or technology.

## Accessibility Features

### Visual Accommodations

1. **High Contrast Mode**
   - Four theme variants: Light, Dark, High Contrast Light, and High Contrast Dark
   - All text meets WCAG 2.1 AA contrast requirements (4.5:1 for normal text, 3:1 for large text)
   - Clear visual boundaries between UI elements
   - Persistent preferences saved in localStorage

2. **Text Options**
   - Responsive text sizing that respects browser zoom
   - Maintains readability when zoomed up to 400%
   - No horizontal scrolling required at 200% zoom

3. **Color Independence**
   - Information is never conveyed by color alone
   - Visual elements include patterns, labels, or icons
   - Knowledge Graph entities use distinct shapes and labels in addition to colors

### Navigation and Input

1. **Keyboard Navigation**
   - Full keyboard accessibility throughout the application
   - Visible focus indicators on all interactive elements
   - Skip links for bypassing navigation
   - Custom keyboard shortcuts for common actions
   - See [Keyboard Shortcuts](KeyboardShortcuts.md) for complete documentation

2. **Input Methods**
   - Support for keyboard, mouse, touch, and voice input
   - No time limits on form submission
   - Error identification and suggestions for form fields
   - Form labels properly associated with inputs

### Screen Reader Support

1. **Semantic Structure**
   - Meaningful heading hierarchy
   - ARIA landmarks for easy navigation
   - ARIA labels on all interactive elements
   - Live regions for dynamic content

2. **Alternative Content**
   - Text alternatives for all non-text content
   - Table view as alternative to graph visualizations
   - Long descriptions for complex visuals
   - Captions and transcripts for media content

### Specific Component Accommodations

1. **Knowledge Graph Visualization**
   - Interactive D3.js visualization with keyboard navigation
   - Alternative table view with full filtering and sorting
   - Screen reader announcements for graph interactions
   - Customizable display options (node size, labels, etc.)

2. **Research Reports**
   - Structured content with proper heading hierarchy
   - Citation information available in screen reader friendly format
   - Data tables with proper headers and scope attributes
   - Code examples with syntax highlighting and screen reader support

3. **Forms and Controls**
   - Clear instructions and labels
   - Error prevention and correction
   - Auto-completion where appropriate
   - Sufficient time to complete actions

## Technologies Used for Accessibility

- React for structured, semantic UI components
- Material-UI components with built-in accessibility features
- Custom theme provider with high contrast options
- ARIA attributes for enhanced screen reader support
- Focus traps for modals and dialogs
- Keyboard event handlers for custom controls

## Testing Methods

Our accessibility features are tested using:

1. **Automated Testing**
   - Axe Core and ESLint-plugin-jsx-a11y for static analysis
   - Lighthouse audits for performance and accessibility

2. **Manual Testing**
   - Keyboard navigation testing
   - Screen reader testing with NVDA and VoiceOver
   - High contrast mode verification
   - Color blindness simulation

3. **User Testing**
   - Feedback from users with various disabilities
   - Testing with assistive technology users

## Known Limitations

While we strive for full accessibility, there are some current limitations:

1. The interactive Knowledge Graph visualization may be challenging to use with some screen readers due to the complex nature of the visualization. We recommend using the alternative table view for screen reader users.

2. Some advanced features related to complex data analysis may have limited screen reader support. We are actively working to improve these areas.

## Feedback and Contact Information

We welcome your feedback on the accessibility of the AI Research Integration Platform. Please let us know if you encounter accessibility barriers:

- Email: accessibility@example.com
- Phone: (123) 456-7890

We will do our best to address any issues as quickly as possible.

## Continuous Improvement

This accessibility statement was last updated on March 5, 2025. We regularly review and update our accessibility features as we continue to improve the platform.