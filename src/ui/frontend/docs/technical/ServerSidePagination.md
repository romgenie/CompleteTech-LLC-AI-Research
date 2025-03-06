# Server-Side Pagination Implementation

This document provides technical details on the server-side pagination implementation for the AI Research Integration Platform.

## Overview

Server-side pagination is a technique for handling large datasets by fetching only a specific subset (page) of data from the server at a time. This approach improves performance by:

1. Reducing initial load times
2. Minimizing network payload sizes
3. Decreasing memory usage on the client
4. Optimizing rendering performance

Our implementation offers a comprehensive solution with React Query integration, reusable hooks, and a consistent UI experience.

## Architecture

The server-side pagination implementation consists of four main components:

1. **Data Fetching Hooks**: Enhanced React Query hooks for paginated data
2. **Pagination Service**: Domain-specific methods for accessing paginated endpoints
3. **UI Components**: Standardized pagination controls
4. **Integration Examples**: Implementation examples in page components

### Technical Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Pagination  │     │  Pagination   │     │  React Query  │
│   Component   │────▶│   Service     │────▶│     Hooks     │
└───────────────┘     └───────────────┘     └───────────────┘
        ▲                                           │
        │                                           ▼
┌───────────────┐                          ┌───────────────┐
│     Page      │◀─────────────────────────│   API Client  │
│   Component   │                          │               │
└───────────────┘                          └───────────────┘
```

## Implementation Details

### 1. The `usePaginatedQuery` Hook

This hook extends React Query's `useQuery` with pagination-specific functionality:

```typescript
export function usePaginatedQuery<TData = unknown>(
  options: QueryFetchOptions<TData> & {
    initialPage?: number;
    initialPageSize?: number;
  }
) {
  const [page, setPage] = React.useState(options.initialPage || 1);
  const [pageSize, setPageSize] = React.useState(options.initialPageSize || 10);
  
  // Query with pagination parameters included
  const query = useQuery([url, { ...config, page, pageSize }], fetchFn, {
    keepPreviousData: true, // Important for UX - shows previous data while loading
    ...queryOptions
  });
  
  // Prefetch next page for smoother navigation
  React.useEffect(() => {
    if (query.data) {
      queryClient.prefetchQuery([url, { ...config, page: page + 1, pageSize }], fetchFn);
    }
  }, [query.data, page, pageSize]);
  
  // Pagination control functions
  const goToPage = React.useCallback((newPage) => { setPage(newPage); }, []);
  const nextPage = React.useCallback(() => { setPage(old => old + 1); }, []);
  const previousPage = React.useCallback(() => { setPage(old => Math.max(old - 1, 1)); }, []);
  const setPageSizeAndReset = React.useCallback((newPageSize) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to first page when changing page size
  }, []);
  
  // Return combined query result and pagination controls
  return {
    ...query,
    pagination: {
      page, pageSize, goToPage, nextPage, previousPage, setPageSize: setPageSizeAndReset
    }
  };
}
```

### 2. The Pagination Service

The pagination service provides domain-specific implementations:

```typescript
export const paginationService = {
  // Generate pagination parameters
  getPaginationParams(page, pageSize, sortField, sortDirection) {
    return {
      page,
      pageSize,
      sortField,
      sortDirection
    };
  },
  
  // Domain-specific methods with proper typing
  useResearchData(options = {}) {
    const config = {
      ...requestConfig,
      params: {
        ...this.getPaginationParams(options.initialPage, options.initialPageSize, 
                                  options.sortField, options.sortDirection)
      }
    };
    
    return usePaginatedQuery<PaginatedResponse<ResearchData>>({
      url: '/research/history',
      config,
      initialPage: options.initialPage,
      initialPageSize: options.initialPageSize,
      mockData: () => generateMockData(options.initialPage, options.initialPageSize)
    });
  },
  
  // Factory method for custom paginated queries
  createPaginatedQuery<TData = any>(url, options, mockDataGenerator) {
    // Implementation details...
  }
};
```

### 3. The Pagination Component

The pagination component provides a standardized UI for navigating paginated data:

```jsx
function Pagination({
  page, 
  pageSize, 
  total, 
  totalPages,
  onPageChange,
  onPageSizeChange,
  loading,
  hidePageSizeSelector = false,
  pageSizeOptions = [5, 10, 25, 50, 100],
  showFirstLastButtons = true,
  compact = false,
  siblingCount = 1
}) {
  // Logic for generating page range, handling page changes, etc.
  
  return (
    <Box display="flex" alignItems="center" justifyContent="space-between">
      {/* Page size selector */}
      {!hidePageSizeSelector && (
        <Select value={pageSize} onChange={handlePageSizeChange}>
          {pageSizeOptions.map(option => (
            <MenuItem key={option} value={option}>{option}</MenuItem>
          ))}
        </Select>
      )}
      
      {/* Pagination controls */}
      <Box display="flex" alignItems="center">
        {showFirstLastButtons && <FirstPageButton />}
        <PreviousPageButton />
        {!compact && <PageButtons />}
        {compact && <PageIndicator />}
        <NextPageButton />
        {showFirstLastButtons && <LastPageButton />}
      </Box>
      
      {/* Page info */}
      <Typography variant="body2">
        Showing {start}-{end} of {total} items
      </Typography>
    </Box>
  );
}
```

### 4. Backend API Requirements

For server-side pagination to work, the backend API must support:

1. **Page-based Parameters**: 
   - `page`: The requested page number (1-indexed)
   - `pageSize` or `limit`: Number of items per page

2. **Standardized Response Format**:
   ```json
   {
     "items": [...],       // Array of items for the current page
     "total": 100,         // Total number of items across all pages
     "page": 1,            // Current page number
     "pageSize": 10,       // Number of items per page
     "totalPages": 10      // Total number of pages
   }
   ```

3. **Optional Sorting Parameters**:
   - `sortField`: Field to sort by
   - `sortDirection`: Sort direction (asc/desc)

## Usage Example

```tsx
function ResearchHistory() {
  // Use the paginated query hook via the service
  const {
    data,
    isLoading,
    error,
    pagination: { page, pageSize, goToPage, nextPage, previousPage, setPageSize }
  } = paginationService.useResearchData({
    initialPage: 1,
    initialPageSize: 10,
    sortField: 'timestamp',
    sortDirection: 'desc'
  });
  
  return (
    <div>
      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage error={error} />
      ) : (
        <>
          {/* Display the current page of data */}
          <DataTable data={data.items} />
          
          {/* Pagination controls */}
          <Pagination
            page={page}
            pageSize={pageSize}
            total={data.total}
            totalPages={data.totalPages}
            onPageChange={goToPage}
            onPageSizeChange={setPageSize}
            loading={isLoading}
          />
        </>
      )}
    </div>
  );
}
```

## Performance Considerations

1. **Query Key Design**: Include pagination parameters in the query key to ensure proper cache handling.
2. **Keep Previous Data**: Set `keepPreviousData: true` to show the previous page while loading new data.
3. **Prefetching**: Prefetch the next page after loading the current page for smoother navigation.
4. **Debouncing**: Consider debouncing page size changes to avoid excessive API calls.
5. **Optimistic UI**: Update the UI optimistically when possible for immediate feedback.

## Accessibility

The pagination implementation follows WCAG guidelines:

1. **Keyboard Navigation**: All controls are keyboard accessible
2. **Screen Reader Support**: Proper ARIA attributes and announcements
3. **Focus Management**: Maintains focus appropriately during page transitions
4. **Clear Visual Indicators**: Loading states, disabled controls, and current page indication

## Edge Cases and Error Handling

1. **Empty Data**: If no data is available, display appropriate empty state
2. **Last Page**: Disable next/last page buttons when on the last page
3. **First Page**: Disable previous/first page buttons when on the first page
4. **Loading State**: Show loading indicators during page transitions
5. **Error State**: Display error messages if API requests fail
6. **Fallback**: Provide mock data when API is unavailable

## Backend Mock Implementation

During development or when the backend is unavailable, the system falls back to mock data:

```typescript
function generateMockData(page, pageSize) {
  // Calculate total items and pages for realistic pagination
  const totalItems = 100;
  const totalPages = Math.ceil(totalItems / pageSize);
  
  // Generate items for the current page
  const items = Array.from({ length: Math.min(pageSize, totalItems - (page - 1) * pageSize) }, 
    (_, index) => ({
      id: `item-${(page - 1) * pageSize + index + 1}`,
      title: `Item ${(page - 1) * pageSize + index + 1}`,
      // Additional mock properties...
    })
  );
  
  // Return in the standard paginated response format
  return {
    items,
    total: totalItems,
    page,
    pageSize,
    totalPages
  };
}
```