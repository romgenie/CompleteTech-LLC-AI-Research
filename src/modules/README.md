# Module Testing

This directory contains the implementation of UI modules according to the modular component architecture.

## Testing the Modules

To test the modules, follow these steps:

1. Navigate to the modules directory:
   ```
   cd src/modules
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open your browser at [http://localhost:3001](http://localhost:3001)

The test page will allow you to:
- See the Knowledge Graph module in action
- Switch between different display modes (list, detail, form)
- Toggle read-only mode
- Configure various module options

## Available Modules

### Knowledge Graph Module

The Knowledge Graph module displays and manages entities and relationships in a knowledge graph:

- View entities in a list format with filtering by type
- Visualize graph data with interactive controls 
- View statistics about the graph
- Create, update, and delete entities (when not in read-only mode)

#### Usage Example

```jsx
import { KnowledgeGraphModule } from './modules/KnowledgeGraph';

const MyPage = () => {
  return (
    <KnowledgeGraphModule 
      mode="list"
      readOnly={false}
      showActions={true}
      showFilters={true}
      height={600}
      width="100%"
      onItemSelect={(entity) => console.log('Selected entity:', entity)}
    />
  );
};
```

## Implementation Status

- ✅ Knowledge Graph Module: Basic implementation with EntityList
- 🔄 Knowledge Graph Module: Missing components (to be completed)
  - EntityDetail
  - EntityForm
  - GraphVisualization
  - GraphStats
  - PathFinder
- 🔄 Research Orchestration Module: Not started
- 🔄 Implementation Planning Module: Not started
- 🔄 Paper Processing Module: Not started