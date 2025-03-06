# Modular Frontend Component Architecture

## Overview

We've designed a comprehensive modular component architecture to standardize our UI development across all API endpoints. This architecture follows these key principles:

### Base Module Template

Each API endpoint will have a dedicated module built on our base template:

```
/src/modules/[ModuleName]/
  ├── components/              # UI components specific to this module
  │   ├── [ModuleName]Card.tsx         # Card view of entity
  │   ├── [ModuleName]List.tsx         # List view of entities
  │   ├── [ModuleName]Detail.tsx       # Detailed view
  │   ├── [ModuleName]Form.tsx         # Create/edit form
  │   └── [ModuleName]Filter.tsx       # Filter component
  ├── hooks/                   # Custom hooks for this module
  │   ├── use[ModuleName].ts           # Main data hook
  │   ├── use[ModuleName]Mutation.ts   # Create/update/delete operations
  │   └── use[ModuleName]Query.ts      # Read operations
  ├── types/                   # TypeScript types
  │   └── [moduleName].types.ts        # Type definitions
  ├── utils/                   # Module-specific utilities
  │   └── [moduleName]Utils.ts         # Helper functions
  ├── [ModuleName]Module.tsx   # Main exportable module component
  └── index.ts                 # Public API for the module
```

### Key Features

1. **Self-contained Modules**: Each module is entirely self-contained with its own state management, UI components, and API integration.

2. **Consistent Patterns**: All modules follow the same structure and patterns, making the codebase more maintainable.

3. **Flexible Configuration**: Modules accept configuration props to customize their behavior and appearance:
   ```tsx
   <KnowledgeGraphModule
     mode="card"
     height={300}
     showFilters={false}
     readOnly={true}
   />
   ```

4. **Multiple Display Modes**: Each module supports multiple display modes (list, card, detail, form) that can be toggled.

5. **React Query Integration**: Modules use React Query for data fetching, caching, and mutations.

6. **Material-UI Components**: Built on Material-UI for consistent styling and accessibility.

## Module Implementations

We've created module definitions for each API category:

1. **Knowledge Graph**: Entity management, graph visualization, path finding
   ```
   /src/modules/KnowledgeGraph/
     ├── components/
     │   ├── EntityCard.tsx
     │   ├── EntityList.tsx
     │   ├── EntityDetail.tsx
     │   ├── EntityForm.tsx
     │   ├── GraphVisualization.tsx
     │   ├── PathFinder.tsx
     │   └── GraphStats.tsx
     ├── hooks/
     │   ├── useKnowledgeGraph.ts
     │   ├── useEntity.ts
     │   ├── useGraphSearch.ts
     │   └── useGraphStats.ts
     ├── KnowledgeGraphModule.tsx
     └── index.ts
   ```

2. **Research Orchestration**: Query management, task tracking, search functionality
   ```
   /src/modules/ResearchOrchestration/
     ├── components/
     │   ├── QueryForm.tsx
     │   ├── TaskList.tsx
     │   ├── TaskDetail.tsx
     │   ├── TaskStatus.tsx
     │   └── SearchResults.tsx
     ├── hooks/
     │   ├── useResearchQuery.ts
     │   ├── useResearchTasks.ts
     │   └── useQuickSearch.ts
     ├── ResearchOrchestrationModule.tsx
     └── index.ts
   ```

3. **Implementation Planning**: Plan management, task editing, implementation status
   ```
   /src/modules/ImplementationPlanning/
     ├── components/
     │   ├── PlanList.tsx
     │   ├── PlanDetail.tsx
     │   ├── PlanForm.tsx
     │   ├── TaskEditor.tsx
     │   └── TaskStatus.tsx
     ├── hooks/
     │   ├── useImplementationPlans.ts
     │   └── useImplementationTasks.ts
     ├── ImplementationPlanningModule.tsx
     └── index.ts
   ```

4. **Paper Processing**: Paper uploads, processing status, batch operations
   ```
   /src/modules/PaperProcessing/
     ├── components/
     │   ├── PaperCard.tsx
     │   ├── PaperList.tsx
     │   ├── PaperUpload.tsx
     │   ├── ProcessingStatus.tsx
     │   ├── BatchProcessor.tsx
     │   └── PaperStats.tsx
     ├── hooks/
     │   ├── usePapers.ts
     │   ├── usePaperProcessing.ts
     │   ├── usePaperWebSocket.ts
     │   └── usePaperStats.ts
     ├── PaperProcessingModule.tsx
     └── index.ts
   ```

## Usage Example

Modules can be easily composed in pages:

```tsx
// Example of a dashboard page
const DashboardPage: React.FC = () => {
  return (
    <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
      <KnowledgeGraphModule 
        mode="card" 
        height={300} 
        showFilters={false} 
      />
      
      <ResearchOrchestrationModule 
        mode="list" 
        height={300} 
        initialFilters={{ status: 'active' }} 
      />
      
      <PaperProcessingModule 
        mode="list" 
        height={300} 
        showActions={true} 
      />
      
      <ImplementationPlanningModule 
        mode="card" 
        height={300} 
        readOnly={true} 
      />
    </Box>
  );
};

// Example of a detailed page focused on one module
const KnowledgeGraphPage: React.FC = () => {
  return (
    <Box sx={{ height: '100%' }}>
      <KnowledgeGraphModule 
        mode="detail" 
        showFilters={true}
        showActions={true}
        customActions={<CustomActionComponent />}
      />
    </Box>
  );
};
```

## Implementation Strategy

1. **Start with a template module** - Create a base template that can be cloned for each endpoint
2. **Implement services first** - Ensure API integration works properly 
3. **Build core components** - Implement the essential UI components
4. **Add routing integration** - Connect components to the application router
5. **Implement progressive enhancements** - Add advanced features like filtering, sorting, and custom visualizations

## Cloning Process for a Specific Endpoint

When creating a new module for a specific endpoint, follow these steps:

1. **Create a new module directory** using the endpoint name (e.g., `KnowledgeGraphEntities`)

2. **Copy the template files** from the BaseModule template

3. **Rename all components** from "Base" to the specific entity name:
   - Rename files (e.g., `BaseList.tsx` → `EntityList.tsx`)
   - Rename component names inside files
   - Update imports to reflect the new names

4. **Customize the data model** to match the API:
   - Update the Entity interface in types
   - Add specific fields and types
   - Customize the Filter interface with endpoint-specific filters

5. **Implement service functions** for the specific endpoint:
   - Create API functions for CRUD operations
   - Map API responses to the entity model
   - Handle errors appropriately

6. **Customize the UI components** to match the entity:
   - Update form fields and validation
   - Customize card and list displays for meaningful data
   - Add endpoint-specific actions

7. **Implement module-specific hooks**:
   - Use the baseHooks as a foundation
   - Add specialized logic for the specific entity

8. **Test the module**:
   - Test with mock data
   - Test with the actual API
   - Verify all CRUD operations

## Next Steps

1. Implement full module templates for all API endpoints
2. Create end-to-end examples for each module type
3. Add comprehensive documentation for each module's props and functionality
4. Set up unit and integration tests for all modules
