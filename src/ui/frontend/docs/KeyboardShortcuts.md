# Keyboard Shortcuts and Navigation

This document outlines all keyboard shortcuts and navigation features in the AI Research Integration Platform, with special focus on the Knowledge Graph visualization.

## Global Navigation

| Shortcut | Action |
|----------|--------|
| `Tab` | Move focus to next interactive element |
| `Shift+Tab` | Move focus to previous interactive element |
| `Enter` or `Space` | Activate the focused element (button, link, etc.) |
| `Esc` | Close modal dialogs, menus, or panels |
| `Alt+1` through `Alt+5` | Jump to main navigation items |
| `Alt+H` | Return to Home/Dashboard |
| `Alt+S` | Focus search field |
| `Alt+M` | Open main menu (mobile view) |
| `/` | Focus on global search field |

## Knowledge Graph Visualization

### Navigation

| Shortcut | Action |
|----------|--------|
| `←` `→` `↑` `↓` | Navigate between nodes in the graph |
| `Tab` | Move to next interactive element in the visualization |
| `Shift+Tab` | Move to previous interactive element in the visualization |
| `Home` | Jump to first node in the graph |
| `End` | Jump to last node in the graph |
| `Ctrl+Home` | Return to the central/selected node |

### Selection and Interaction

| Shortcut | Action |
|----------|--------|
| `Enter` or `Space` | Select the currently focused node |
| `S` | Select the currently focused node |
| `I` | Show information about the focused node |
| `E` | Expand connections from the selected node |
| `C` | Collapse connections from the selected node |
| `F` | Find related nodes for the current selection |

### Visualization Controls

| Shortcut | Action |
|----------|--------|
| `+` or `=` | Zoom in |
| `-` | Zoom out |
| `0` | Reset zoom level |
| `R` | Reset the entire visualization |
| `V` | Toggle between graph view and table view |
| `L` | Toggle node labels |
| `P` | Toggle relationship labels |
| `D` | Toggle dark mode |
| `H` | Toggle high contrast mode |

## Table View Navigation

| Shortcut | Action |
|----------|--------|
| `Tab`/`Shift+Tab` | Navigate through table cells |
| `Space` | Select a row in the entity table |
| `Enter` | View details of the selected entity |
| `Home` | Jump to first cell in row |
| `End` | Jump to last cell in row |
| `Page Up` | Previous page of results |
| `Page Down` | Next page of results |
| `Ctrl+Home` | Jump to first row of table |
| `Ctrl+End` | Jump to last row of table |
| `/` | Focus the search/filter field |

## Search and Filtering

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Focus on search/filter field |
| `Enter` (while in search field) | Execute search |
| `Esc` (while in search field) | Clear search field |
| `Alt+C` | Clear all filters and search terms |

## Dialog and Modal Controls

| Shortcut | Action |
|----------|--------|
| `Esc` | Close the current dialog or modal |
| `Tab` | Navigate through controls in dialog |
| `Enter` | Activate the primary action |
| `Ctrl+Enter` | Submit form in current dialog |

## Accessibility Features

| Shortcut | Action |
|----------|--------|
| `Alt+A` | Toggle accessibility panel |
| `Alt+H` | Toggle high contrast mode |
| `Alt+Z` | Toggle screen reader optimizations |
| `Alt+T` | Toggle text-only mode for all visualizations |
| `Alt+F` | Increase font size |
| `Alt+G` | Decrease font size |
| `Alt+R` | Reset all accessibility settings |

## Keyboard Navigation Tips

- Press `Tab` repeatedly to navigate through all interactive elements on the page
- Use `Shift+Tab` to move backwards through elements
- The current focus is indicated by a visible outline around the element
- Press `Enter` or `Space` to activate buttons, links, and other controls
- In the Knowledge Graph visualization, arrow keys allow direct navigation between nodes
- Use `/` to quickly access search functionality from anywhere
- Press `?` from any screen to see keyboard shortcuts for the current page

## Screen Reader Support

The platform has been optimized for screen reader access with the following features:

1. **ARIA Landmarks**: Main sections are marked with appropriate landmarks to aid navigation
2. **Semantic HTML**: Properly structured headings, lists, and tables for logical navigation
3. **ARIA Live Regions**: Dynamic content updates are announced appropriately
4. **Text Alternatives**: All visualizations have text-based alternatives
5. **Focus Management**: Focus is properly managed when content changes

For optimal screen reader experience, use the table view mode for the Knowledge Graph by pressing `V` while the visualization is focused.