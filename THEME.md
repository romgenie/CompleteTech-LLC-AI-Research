# AI Research Integration Platform Theme Guide

This document outlines the design system and theme used throughout the AI Research Integration Platform to ensure a consistent visual identity and user experience.

## Color Palette

Our color palette is designed to convey trust, intelligence, and innovation while maintaining accessibility and readability.

### Primary Colors

- **Primary Blue (`#4a6fa5`)**: Used for primary buttons, links, and key UI elements
- **Secondary Green (`#5c946e`)**: Used for success indicators, progress elements, and secondary actions
- **Accent Purple (`#ad5b82`)**: Used for highlighting important features, calls to action, and accent elements

### Neutral Colors

- **Dark Background (`#212529`)**: Used for headers, footers, and dark mode backgrounds
- **Light Background (`#f8f9fa`)**: Used for content areas, cards, and light mode backgrounds
- **Text Color (`#333333`)**: Main text color for body content
- **Light Text (`#f8f9fa`)**: Text color for dark backgrounds

## Typography

- **Primary Font**: 'Inter', with system font fallbacks
- **Headings**: Bold weight (700-800) with slightly reduced letter spacing
- **Body Text**: Regular weight (400) with line height of 1.6
- **Code Snippets**: Monospace font for API endpoints and code examples

## UI Elements

### Buttons

- **Primary Button**: Blue background with white text
- **Secondary Button**: Outlined with primary color
- **Accent Button**: Purple background with white text

### Cards

- Light background with subtle shadow
- Rounded corners (0.375rem / 6px)
- Subtle hover effect with elevation increase

### Icons

- Clean, minimal line icons
- 24px standard size for navigation
- 32px size for feature highlights
- Icons should have consistent stroke width

## Gradients

- **Primary Gradient**: Linear gradient from primary blue to secondary green (`linear-gradient(135deg, #4a6fa5, #5c946e)`)
- **Secondary Gradient**: Linear gradient from primary blue to darker blue (`linear-gradient(135deg, #4a6fa5, #3a5a8f)`)
- **Accent Gradient**: Linear gradient from accent purple to darker purple (`linear-gradient(135deg, #ad5b82, #96466d)`)

## Layout

- Consistent spacing system using Bootstrap's spacing utilities
- Responsive design with mobile-first approach
- Maximum content width of 1200px with centered alignment
- Section padding: 3rem (desktop), 2rem (mobile)

## Component Styling

### Navigation

- Dark background with light text
- Active state indicated by underline or subtle highlight
- Clear visual hierarchy between main and secondary navigation items

### Feature Sections

- Alternating background colors for visual separation
- Icons with gradient backgrounds in feature cards
- Consistent vertical spacing between features

### API Documentation

- Code snippets in monospace with syntax highlighting
- Clear endpoint labeling with HTTP method indicators
- Request/response examples in collapsible sections

## Accessibility Considerations

- Minimum contrast ratio of 4.5:1 for text
- Focus states clearly visible for keyboard navigation
- Alt text for all images and icons
- Color is not the only means of conveying information

## Implementation Notes

The theme is implemented using CSS variables for easy customization and consistency. The primary variables are defined in the `:root` selector:

```css
:root {
  --primary-color: #4a6fa5;
  --secondary-color: #5c946e;
  --accent-color: #ad5b82;
  --light-bg: #f8f9fa;
  --dark-bg: #212529;
  --text-color: #333;
  --light-text: #f8f9fa;
}
```

When implementing new components or pages, refer to this style guide to ensure visual consistency throughout the platform.