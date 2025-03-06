# Collaborative Tagging System

## Overview

The collaborative tagging system extends our hierarchical tag functionality to enable sharing, collaboration, and community-based tag organization. This feature allows users to:

- Share tags with specific users or groups with different permission levels
- Discover popular and community-created tags
- Use suggested tags based on content and community patterns
- Resolve conflicts in competing taxonomies
- View analytics on tag usage and trends
- Create and manage shared taxonomies (organized collections of tags)

The system is designed to balance individual customization with organizational consistency, allowing for both personal and standardized taxonomies to coexist.

## Key Components

### Data Layer

1. **Enhanced Tag Model** (`/src/types/research.ts`)
   - Added visibility and sharing properties
   - Added ownership and usage metrics
   - Added taxonomy relationships

2. **Taxonomy Model** (`/src/types/research.ts`)
   - Created model for organizing collections of tags
   - Implemented visibility and sharing controls
   - Added versioning support

3. **Services** 
   - **Tag Service** (`/src/services/tagsService.ts`): Enhanced with sharing, suggestion, and analytics capabilities
   - **Taxonomy Service** (`/src/services/taxonomyService.ts`): New service for taxonomy management

### UI Components

1. **Tag Discovery** (`/src/components/Tags/TagDiscovery.tsx`)
   - Interface for discovering shared, popular, and suggested tags
   - Multi-tab display for different tag sources (popular, global, shared)
   - Search and filtering capabilities

2. **Tag Sharing Dialog** (`/src/components/Tags/TagSharingDialog.tsx`)
   - Interface for setting tag visibility (private, shared, public)
   - User/group selection with permission settings
   - Management of sharing permissions

3. **Tag Conflict Resolution** (`/src/components/Tags/TagConflictResolution.tsx`)
   - Interface for resolving taxonomy conflicts
   - Multiple resolution options (merge, move, rename, split)
   - Visual explanations of conflict consequences

4. **Tag Analytics** (`/src/components/Tags/TagAnalytics.tsx`)
   - Usage statistics visualization
   - Trend analysis
   - Co-occurrence relationships display

5. **Tag Management Page** (`/src/pages/TagManagementPage.tsx`)
   - Integrated interface combining all tag management features
   - Tab-based navigation between different tag functions
   - Context-sensitive tools based on selected tag

## Data Structure

### Enhanced Tag Model

```typescript
interface Tag {
  // Core properties
  id: string;
  name: string;
  color?: string;
  description?: string;
  
  // Hierarchy properties
  parentId?: string | null;
  children?: string[];
  level?: number;
  path?: string;
  inheritedFrom?: string[];
  
  // Collaboration properties
  owner?: string;
  visibility: 'private' | 'shared' | 'public';
  sharedWith?: SharedWith[];
  isGlobal?: boolean;
  taxonomyId?: string;
  
  // Analytics properties
  usageCount?: number;
  popularity?: number;
  suggestedBy?: string;
  lastUsed?: string;
}
```

### Taxonomy Model

```typescript
interface Taxonomy {
  id: string;
  name: string;
  description?: string;
  owner: string;
  visibility: 'private' | 'shared' | 'public';
  sharedWith?: SharedWith[];
  rootTags: string[];
  isOfficial?: boolean;
  domain?: string;
  createdAt: string;
  updatedAt?: string;
  version?: string;
}
```

### Sharing Permissions

```typescript
interface SharedWith {
  id: string; // User or group ID
  type: 'user' | 'group' | 'team';
  permission: 'view' | 'use' | 'edit' | 'admin';
}
```

## Key Features

### 1. Tag Visibility and Sharing

Tags can have three visibility levels:
- **Private**: Only visible to the creator
- **Shared**: Visible to specific users or groups with assigned permissions
- **Public**: Visible to all users in the system

Sharing permissions:
- **View**: Can see the tag but not apply it
- **Use**: Can apply the tag to research items
- **Edit**: Can modify tag properties and hierarchy
- **Admin**: Full control including sharing with others

### 2. Tag Discovery

The tag discovery interface presents tags from different sources:
- **Popular Tags**: Most frequently used tags across all users
- **Suggestions**: AI and community-generated tag suggestions for current context
- **Global Tags**: System-wide standardized tags (often created by administrators)
- **Shared Tags**: Tags explicitly shared with the current user
- **Taxonomies**: Formal tag organizations (often domain-specific)

### 3. Tag Conflict Resolution

The system detects potential conflicts including:
- **Hierarchy Conflicts**: Same tag exists in multiple incompatible hierarchies
- **Name Conflicts**: Similar names for different concepts
- **Classification Conflicts**: Same concept classified differently
- **Duplicate Conflicts**: Identical tags maintained separately

Resolution options include:
- **Merge**: Combine conflicting tags
- **Move**: Relocate tag in hierarchy
- **Rename**: Change tag name for clarity
- **Split**: Separate tag into distinct concepts
- **Keep**: Maintain separate tags

### 4. Analytics and Suggestions

Analytics features include:
- **Usage Trends**: Visualization of tag usage over time
- **User Adoption**: Tracking how many users employ each tag
- **Co-Occurrence**: Analysis of which tags are used together
- **Popularity Trends**: Rising, stable, or falling usage patterns

Suggestion system uses:
- Content analysis for contextual suggestions
- Usage patterns for popularity-based suggestions
- Co-occurrence analysis for relationship-based suggestions
- User behavior for personalized suggestions

## Integration with Existing Systems

The collaborative tagging system integrates with:

1. **Authentication System**: Uses the existing auth context for user permissions
2. **Research Query System**: Enhances search with shared tags
3. **Knowledge Graph**: Relates tags to entities for improved navigation
4. **User Preferences**: Stores tag favorites and usage history

## Backend API Requirements

The implementation requires several new API endpoints:

1. **Tag Sharing**: 
   - `POST /api/tags/:id/share` - Share a tag with users/groups
   - `GET /api/tags/shared` - Get tags shared with current user

2. **Tag Discovery**:
   - `GET /api/tags/popular` - Get popular tags
   - `GET /api/tags/global` - Get global tags
   - `GET /api/tags/suggestions` - Get tag suggestions

3. **Tag Taxonomies**:
   - `GET /api/taxonomies` - Get accessible taxonomies
   - `POST /api/taxonomies` - Create a taxonomy
   - `PATCH /api/taxonomies/:id` - Update a taxonomy
   - `POST /api/taxonomies/:id/share` - Share a taxonomy

4. **Conflict Management**:
   - `GET /api/tags/conflicts` - Get tag conflicts
   - `POST /api/tags/conflicts/:id/resolve` - Resolve a conflict

5. **Analytics**:
   - `GET /api/tags/:id/stats` - Get usage statistics for a tag

## Performance Considerations

1. **Caching**: Tag discovery data is cached with appropriate TTLs using React Query
2. **Lazy Loading**: Taxonomy data is loaded only when needed
3. **Optimistic Updates**: UI updates immediately for sharing and visibility changes
4. **Batch Operations**: Multiple changes can be made before submitting to server

## Future Enhancements

1. **Machine Learning Integration**: Improved tag suggestions based on content analysis
2. **Tag Reputation System**: Quality scores for tags based on usage patterns
3. **Advanced Conflict Resolution**: Automated merge recommendations
4. **Tag Deprecation Workflow**: Process for retiring outdated tags
5. **Version Control**: Full history of taxonomy changes