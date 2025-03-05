# API Integration Architecture

This document describes the architecture of the API integration layer in the AI Research Integration Platform frontend. The system is designed to provide efficient, reliable, and real-time data exchange with the backend services.

## Core Components

### 1. API Client

The `apiClient` is a centralized service that handles all HTTP requests to the backend API. It is built on top of Axios and provides:

- **Unified error handling**: Centralizes error management across all API calls
- **Authentication management**: Automatically adds auth tokens to requests
- **Response data extraction**: Standardizes response formatting
- **WebSocket integration**: Provides real-time data synchronization capabilities
- **Reconnection logic**: Handles network interruptions with exponential backoff

```typescript
// Example usage of apiClient
import apiClient from './services/apiClient';

// Making a GET request
const data = await apiClient.get<MyDataType>('/endpoint');

// Making a POST request
const result = await apiClient.post<ResultType, PayloadType>('/endpoint', payload);

// WebSocket usage
apiClient.connectWebSocket('ws://api.example.com/ws');
const unsubscribe = apiClient.subscribeToWebSocket<UpdateType>('update_type', (data) => {
  // Handle real-time updates
});
```

### 2. React Query Integration

The system uses React Query for efficient data fetching, caching, and state management:

- **Enhanced hooks**: Custom hooks built on React Query for API interactions
- **Automatic caching**: Smart caching strategies to minimize network requests
- **Background refetching**: Keeps data fresh while maintaining UI responsiveness
- **Optimistic updates**: Immediate UI updates with server confirmation
- **Prefetching**: Anticipatory data loading for improved UX
- **Pagination**: Efficient handling of large datasets
- **WebSocket integration**: Real-time updates to cached data

```typescript
// Example of React Query hook
export function useResearchStats(dateRange?: DateRangeParams) {
  return useFetchQuery<ResearchStats>({
    url: STATS_BASE_URL,
    config: { params: dateRange },
    queryOptions: {
      staleTime: 1000 * 60 * 15, // 15 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: generateMockStats,
    enableWebSocket: true,
    wsMessageType: 'stats_update'
  });
}
```

### 3. Service Layer

Domain-specific services abstract the API functionality into logical modules:

- **tagsService**: Manages research tag operations
- **statsService**: Handles research statistics and analytics
- **recommendationsService**: Provides personalized recommendations and insights
- **researchService**: Manages research queries and results
- **citationService**: Handles citation formatting and management

Each service provides both direct API methods and React Query hooks:

```typescript
// Direct API method
const tags = await tagsService.getTags();

// React Query hook
const { data, isLoading, error } = useTags();
```

## Key Features

### Server-Side Pagination

The system implements efficient server-side pagination for handling large datasets:

1. **Paginated API Requests**: Fetches only the required subset of data from the server
2. **Customizable Page Sizes**: Adjustable number of items per page
3. **Intelligent Prefetching**: Loads the next page in advance for smoother navigation
4. **Consistent UI Components**: Standardized pagination controls with accessibility support
5. **Sorting Integration**: Combines pagination with server-side sorting
6. **Mock Data Support**: Falls back to simulated pagination when API is unavailable

For detailed implementation information, see [Server-Side Pagination Implementation](/docs/technical/ServerSidePagination.md).

### Real-time Updates via WebSockets

The system supports real-time data updates through WebSockets:

1. **Connection Management**: Automatic connection establishment and reconnection
2. **Subscription Model**: Component-based subscription to specific message types
3. **React Query Integration**: Updates query cache with real-time data
4. **Cleanup**: Automatic resource cleanup when components unmount

### Optimistic Updates

For improved user experience, the system implements optimistic updates:

1. **Immediate UI Updates**: Changes appear instantly before server confirmation
2. **Rollback Mechanism**: Reverts changes if server requests fail
3. **Server Confirmation**: Validates changes once server responds
4. **Conflict Resolution**: Handles conflicts between optimistic and actual data

### Error Handling

Comprehensive error handling ensures a robust user experience:

1. **Centralized Error Processing**: Common error handling logic in one place
2. **Graceful Degradation**: Fallback to cached or mock data when needed
3. **Retry Logic**: Automatic retries with exponential backoff for transient failures
4. **User Feedback**: Clear error messages for actionable user responses
5. **Authentication Errors**: Automatic redirection to login for authentication issues

### Mock Data Fallbacks

The system seamlessly falls back to mock data when API endpoints are unavailable:

1. **Mock Data Generation**: Realistic mock data that mimics API responses
2. **Transparent Fallback**: Services automatically switch to mock data on API failure
3. **Development Mode**: Easy testing without backend dependencies
4. **Consistency**: Mock data structures match real API responses

## WebSocket Message Types

The system uses the following WebSocket message types for real-time updates:

| Message Type | Description | Affected Components |
|--------------|-------------|---------------------|
| `recommendations_update` | New or updated recommendations | ResearchRecommendationList |
| `insights_update` | New research insights | ResearchInsightList |
| `tag_update` | Tag creation or modification | TagList, TagFilter |
| `stats_update` | Updated research statistics | ResearchStats |
| `query_status` | Research query status changes | ResearchTaskList |

## API Endpoints

The frontend interacts with the following API endpoints:

### Tags API

- `GET /api/tags` - Get all tags
- `GET /api/tags/:id` - Get a specific tag
- `POST /api/tags` - Create a new tag
- `PATCH /api/tags/:id` - Update a tag
- `DELETE /api/tags/:id` - Delete a tag
- `POST /api/tags/merge` - Merge two tags
- `GET /api/tags/:id/items` - Get items with a specific tag
- `POST /api/tags/:id/items` - Add a tag to an item
- `DELETE /api/tags/:id/items/:itemId` - Remove a tag from an item

### Statistics API

- `GET /api/research/stats` - Get overall research statistics
- `GET /api/research/stats/tags` - Get tag usage statistics
- `GET /api/research/stats/terms` - Get top search terms
- `GET /api/research/stats/activity` - Get historical activity data
- `GET /api/research/stats/export` - Export statistics in various formats

### Recommendations API

- `GET /api/research/recommendations` - Get personalized recommendations
- `POST /api/research/recommendations/save` - Save a recommendation
- `DELETE /api/research/recommendations/save/:id` - Remove a saved recommendation
- `GET /api/research/recommendations/saved` - Get saved recommendations
- `POST /api/research/recommendations/generate` - Generate custom recommendations
- `GET /api/research/insights` - Get research insights
- `POST /api/research/insights/:id/read` - Mark an insight as read
- `POST /api/research/insights/:id/dismiss` - Dismiss an insight

## Implementation Notes

### Performance Considerations

The implementation prioritizes performance through:

- **Efficient caching**: Minimizes unnecessary network requests
- **Pagination**: Handles large datasets without loading everything at once
- **Lazy loading**: Defers loading of non-critical data
- **Optimistic updates**: Eliminates waiting for server responses
- **Background fetching**: Updates data without blocking the UI
- **WebSockets**: Uses efficient real-time updates instead of polling

### Security Considerations

The implementation includes several security measures:

- **Token management**: Secure handling of authentication tokens
- **HTTPS**: All API communication over encrypted connections
- **Input validation**: Validating data before sending to API
- **Error obscuring**: Not exposing sensitive information in error messages
- **Session timeout**: Handling expired sessions gracefully

## Future Enhancements

Planned enhancements to the API integration layer include:

1. **Offline support**: Continue operation when disconnected from the server
2. **Request batching**: Group multiple requests to reduce network overhead
3. **Request prioritization**: Critical requests take precedence
4. **Enhanced analytics**: More detailed performance monitoring
5. **Expanded WebSocket usage**: More real-time features