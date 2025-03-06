# Hierarchical Tags System

## Overview

The hierarchical tags system extends the existing tagging functionality to support parent-child relationships between tags. This allows for more organized and structured categorization of research items, enabling users to:

- Create multi-level tag hierarchies with unlimited depth
- Inherit properties and filtering capabilities from parent tags
- Visualize relationships between tags in a tree structure
- Reorganize tag hierarchies through drag-and-drop
- Merge tags while preserving hierarchical structure

## Key Components

### Data Layer

1. **Types** (`/src/types/research.ts`)
   - Enhanced `Tag` interface with hierarchy-related fields
   - Type definitions for tag operations and API responses

2. **Services** (`/src/services/tagsService.ts`)
   - API methods for managing hierarchical tags
   - Custom hooks for React components

### UI Layer

1. **TagHierarchy** (`/src/components/Tags/TagHierarchy.tsx`)
   - Tree visualization component with drag-and-drop support
   - Node expansion/collapse functionality
   - Context menu for tag operations

2. **TagManagementPage** (`/src/pages/TagManagementPage.tsx`)
   - Top-level page for managing tags
   - Multiple view options (list, hierarchy, usage stats)
   - Enhanced dialog components for tag operations

3. **TagSelector** (`/src/components/Tags/TagSelector.tsx`)
   - Multi-select component with hierarchy awareness
   - Support for inherited tag selection

## Data Structure

The hierarchical tag system extends the base `Tag` interface:

```typescript
interface Tag {
  id: string;
  name: string;
  color: string;
  description?: string;
  count?: number;
  
  // Hierarchy-specific fields
  parentId?: string;        // Reference to parent tag
  children?: Tag[];         // Array of child tags
  level: number;            // Depth in hierarchy (0 for root)
  path: string[];           // Array of IDs from root to current tag
  inheritedFrom?: string[]; // IDs of tags this tag inherits from
}
```

### Key Fields

- **parentId**: References the immediate parent tag
- **children**: Contains all direct child tags
- **level**: Indicates depth in hierarchy (0 for root tags)
- **path**: Array of tag IDs from root to current tag, useful for ancestry checks
- **inheritedFrom**: Tracks inherited properties for merged tags

## UI Implementation

### Tree Visualization

The tree visualization is implemented using a recursive component pattern:

```typescript
// Simplified component structure
const TagHierarchyNode = ({ tag, level, onDrop, onSelect, ... }) => {
  const [expanded, setExpanded] = useState(true);
  
  return (
    <div className="tag-node">
      <div className="tag-node-content">
        {tag.children?.length > 0 && (
          <ExpandButton expanded={expanded} onClick={() => setExpanded(!expanded)} />
        )}
        <div className="tag-label" style={{ marginLeft: level * 20 }}>
          {tag.name}
        </div>
      </div>
      
      {expanded && tag.children?.length > 0 && (
        <div className="tag-children">
          {tag.children.map(child => (
            <TagHierarchyNode 
              key={child.id}
              tag={child}
              level={level + 1}
              onDrop={onDrop}
              onSelect={onSelect}
              {...otherProps}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

### Drag and Drop

Drag and drop functionality is implemented using the React DnD library:

1. **Draggable Tag**: Each tag node is wrapped in a draggable container
2. **Drop Targets**: Tag nodes also serve as drop targets
3. **Validation**: Drop operations validate to prevent circular references
4. **State Updates**: Successful drops trigger API calls to update tag relationships

## Tag Inheritance Rules

Tags inherit properties based on the following rules:

1. **Color Inheritance**: Child tags inherit color from parent by default unless explicitly set
2. **Filter Inheritance**: When filtering by a parent tag, all children are included by default
3. **Merge Inheritance**: When merging tags, hierarchical position is preserved when possible
4. **Path Calculation**: When a tag's parent changes, its path and level are automatically recalculated
5. **Circular Reference Prevention**: The system prevents circular references through path validation

### Inheritance Implementation

```typescript
// Color inheritance example
const getEffectiveColor = (tag: Tag, allTags: Record<string, Tag>): string => {
  if (tag.color) {
    return tag.color; // Tag has explicit color
  }
  
  if (tag.parentId && allTags[tag.parentId]) {
    return getEffectiveColor(allTags[tag.parentId], allTags); // Recursive inheritance
  }
  
  return defaultColors[tag.id.charCodeAt(0) % defaultColors.length]; // Fallback
};
```

## Usage Examples

### Creating a Hierarchical Structure

```typescript
// Creating a parent-child relationship
const createHierarchy = async () => {
  // First, create parent tag
  const parentTag = await createTag({
    name: "Machine Learning",
    color: "#3498db"
  });
  
  // Create child tags with parentId reference
  const childTag1 = await createTag({
    name: "Neural Networks",
    parentId: parentTag.id
  });
  
  const childTag2 = await createTag({
    name: "Reinforcement Learning",
    parentId: parentTag.id
  });
  
  // Create a deeper level
  const grandchildTag = await createTag({
    name: "Transformers",
    parentId: childTag1.id
  });
};
```

### Filtering with Hierarchical Tags

```typescript
// Get all research items including those with child tags
const getResearchWithHierarchicalFilter = async (tagId: string) => {
  const tagsService = new TagsService();
  const tag = await tagsService.getTag(tagId);
  
  // Get all descendant tag IDs
  const allDescendantIds = await tagsService.getAllDescendantIds(tagId);
  
  // Include all descendant tags in filter
  const filterTags = [tagId, ...allDescendantIds];
  
  // Use in research filter
  return researchService.getResearchItems({
    tags: filterTags,
    operator: 'OR'
  });
};
```

### Moving Tags in Hierarchy

```typescript
// Moving a tag to a new parent
const moveTag = async (tagId: string, newParentId: string | null) => {
  const tagsService = new TagsService();
  
  // Validate move to prevent circular references
  const canMove = await tagsService.validateMove(tagId, newParentId);
  
  if (!canMove) {
    throw new Error("Invalid move: would create a circular reference");
  }
  
  // Perform move operation
  const updatedTag = await tagsService.moveTag(tagId, newParentId);
  
  // Update local state
  setTags(prevTags => ({
    ...prevTags,
    [tagId]: updatedTag
  }));
};
```

## Best Practices

1. **Path Validation**: Always validate paths when moving tags to prevent circular references
2. **Batch Updates**: Use batch operations for multiple hierarchy changes to maintain consistency
3. **Optimistic UI**: Implement optimistic updates for drag-and-drop operations to improve UX
4. **Error Recovery**: Provide rollback mechanisms for failed hierarchy operations
5. **Performance**: Avoid deep recursion when working with large hierarchies; use memoization when possible

## Technical Limitations

1. The current implementation supports theoretical unlimited depth, but UI testing has focused on hierarchies up to 5 levels deep
2. Large hierarchies (>1000 tags) may experience performance issues in the tree visualization
3. Path array size grows with hierarchy depth, which may impact database storage for very deep hierarchies