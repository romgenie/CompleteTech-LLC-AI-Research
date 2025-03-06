# Knowledge Graph Module Test

This repository includes a standalone HTML page to test the Knowledge Graph module without needing to set up a development environment.

## How to Test the Knowledge Graph Module

1. Open the standalone test page:
   ```
   open standalone-test.html
   ```
   
   This will open the test page in your default browser.

2. The test page provides a fully functional demonstration of the Knowledge Graph module with:
   - Mock data for entities and relationships
   - Interactive controls to change display modes and module options
   - Full CRUD functionality for entities (Create, Read, Update, Delete)

## Available Features

The test page demonstrates these features of the Knowledge Graph module:

### Entity List View
- View entities in a list format
- Filter entities by type using color-coded tags
- Click on an entity to view its details
- Access edit and delete operations via action buttons

### Entity Detail View
- See all information about a specific entity
- View properties in a structured format
- Edit or delete the entity
- Navigate back to the list view

### Entity Creation/Edit Form
- Create new entities or edit existing ones
- Change entity type from a dropdown of options
- Add, edit or remove entity properties
- Submit form to create/update or cancel to return to previous view

### Module Configuration Controls
- Change display mode (List, Detail, Form)
- Adjust module height
- Toggle read-only mode to disable edit operations
- Toggle action bar visibility

### Tab Navigation
- Entities tab: Shows the entity list
- Graph tab: Placeholder for graph visualization
- Statistics tab: Shows basic entity statistics

## Implementation Details

This test page is a simplified HTML/JavaScript implementation that mimics the functionality of the React-based Knowledge Graph module. It demonstrates the UI components and interactions without requiring any backend services or build tools.

The mock implementation includes:
- In-memory entity and relationship data
- Client-side filtering and state management
- Form validation and data handling
- All UI components rendered with vanilla JavaScript and CSS