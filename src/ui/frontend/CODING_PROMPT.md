# Frontend Development Guide

## Recent Achievements & Current Focus
- ✅ Enhanced Knowledge Graph Explorer with advanced visualization settings
- ✅ Implemented comprehensive UX improvements for better information hierarchy
- ✅ Added research-focused analysis tools for AI scientists
- ✅ Created intuitive onboarding experience with step-by-step guidance
- ✅ Improved export capabilities with multiple format options

## Implementation Priorities (Next 4 Weeks)
1. **Knowledge Graph Performance & Accessibility** (Weeks 1-2)
   - Optimize rendering for large graphs (1000+ nodes)
   - Implement keyboard navigation for visualization
   - Add screen reader support for data visualization

2. **TypeScript Migration** (Weeks 1-2)
   - Convert core contexts and hooks to TypeScript
   - Create comprehensive interface definitions
   - Implement type validation for API interactions

3. **Research Enhancement** (Weeks 3-4)
   - Complete citation and reference management
   - Implement research history and favorites
   - Apply Knowledge Graph UX standards to research interface

## Project Overview
The AI Research Integration frontend provides a UI for interacting with our knowledge graph, research, and paper implementation systems. It's built with React, MUI, and integrates with our FastAPI backend.

## Technology Stack
- React 18
- Material UI 5
- React Router 6
- Axios
- D3.js for visualizations
- JWT authentication

## Architecture
- `/components` - Reusable UI components
- `/contexts` - React context providers
- `/hooks` - Custom React hooks
- `/pages` - Main application pages
- `/services` - API client services
- `/utils` - Utility functions

## Development Standards
1. **Component Structure**
   - Use functional components with hooks
   - Follow atomic design principles
   - Extract complex logic to custom hooks
   - Implement proper prop validation with TypeScript or PropTypes
   - Use lazy loading for routes and heavy components
   - Follow established UX patterns from Knowledge Graph Explorer

2. **State Management**
   - Use React Context for global state
   - React Query for server state (future implementation)
   - Local component state for UI-specific state
   - Keep state management consistent across components

3. **API Interaction**
   - All API calls through service modules
   - Include error handling and loading states
   - Implement graceful fallbacks to mock data
   - Use the useFetch hook for consistent API access
   - Add proper TypeScript interfaces for request/response types
   - Include retry logic for transient failures

4. **Code Style**
   - Follow ESLint configuration
   - Document with JSDoc comments
   - Use descriptive variable/function names
   - Keep components focused and small (<200 lines)
   - Follow the principle of single responsibility

5. **Performance**
   - Memoize expensive calculations with useMemo
   - Use React.memo for pure components
   - Implement virtualization for lists with 100+ items
   - Optimize D3 rendering with useCallback and useD3 hook
   - Avoid unnecessary re-renders (React DevTools profiler)
   - Implement progressive loading for large datasets
   - Use level-of-detail techniques for complex visualizations
   - Add client-side caching where appropriate

## Testing Strategy
- Unit tests for utilities and hooks (minimum 80% coverage)
- Component tests with React Testing Library
- Mock API responses using Mock Service Worker
- Visual regression tests for UI components
- Focus on critical user flows
- Add E2E tests for main user journeys
- Include accessibility testing in component tests
- Test keyboard navigation for all interactive elements
- Verify screen reader compatibility for critical components

## Docker Development
- Use Docker for consistent development environments
- Development mode: `docker-compose -f docker/docker-compose.dev.yml up`
- Mock API mode: `docker-compose -f docker/docker-compose.mock.yml up`
- Production build: Build with `docker/Dockerfile`
- Full stack: Use root `docker-compose.yml`

## Error Handling
- Use the ErrorBoundary component for critical UI sections
- Provide user-friendly error messages with ErrorFallback
- Log errors to console in development mode only
- Use useFetch hook with built-in retry mechanism 
- Implement graceful degradation with mock data fallbacks
- Add descriptive error states for different error types
- Keep error messaging consistent across the application

## Accessibility
- Use semantic HTML elements
- Maintain proper heading hierarchy
- Ensure keyboard navigation works
- Add ARIA attributes where needed
- Maintain sufficient color contrast (WCAG 2.1 AA)
- Test with screen readers

## Paper Processing Integration
- Use WebSocketContext for real-time status updates
- Show processing stages with StatusIndicator component
- Implement useWebSocket hook for WebSocket connection management
- Handle reconnection automatically with exponential backoff
- Display paper status transitions with meaningful visual cues
- Cache paper status locally for quick loading and offline display
- Subscribe to specific paper updates using the WebSocket API
- Implement notification system for status changes

## Common Development Tasks
- **Adding a new page**:
  1. Create component in `/pages` directory
  2. Add route in App.js
  3. Update navigation in Layout component
  4. Implement lazy loading

- **Creating a new component**:
  1. Create component file in `/components` directory
  2. Export component in appropriate index file
  3. Implement prop validation
  4. Add JSDoc comments
  5. Consider memoization for expensive components

- **Adding an API service**:
  1. Create service file in `/services` directory
  2. Implement API methods with error handling
  3. Add mock data fallback
  4. Update relevant context providers
  5. Add appropriate retry mechanisms

## Backend Integration
- API base URL: http://localhost:8000
- Authentication: JWT tokens stored in localStorage
- Endpoints:
  - `/auth/login` - User authentication
  - `/api/research` - Research query endpoints
  - `/api/knowledge-graph` - Knowledge graph operations
  - `/api/implementation` - Paper implementation endpoints
- Error handling:
  - Network errors: Retry with exponential backoff
  - Authentication errors: Redirect to login
  - Server errors: Display appropriate UI message
  - Default to mock data when backend unavailable

## Knowledge Graph Visualization 
### Core Principles
- Use the useD3 hook for all D3 integrations
- Follow established UX patterns from the existing implementation
- Implement progressive disclosure for advanced features
- Always provide meaningful empty states with clear user guidance

### Performance Optimization (Priority)

#### Week 1: D3 Force Simulation Optimization
```javascript
// Optimize D3 force simulation parameters
const simulation = d3.forceSimulation(graphData.nodes)
  // Reduce alpha decay to make the simulation more stable
  .alphaDecay(0.028)  // default is 0.0228
  // Adjust velocity decay to control the "friction"
  .velocityDecay(0.4)  // default is 0.4
  // Configure forces
  .force("link", d3.forceLink(graphData.links)
    .id(d => d.id)
    // Increase distance for better visibility in large graphs
    .distance(d => visualizationSettings.nodeSize * 10)  
    // Increase strength for stability with many nodes
    .strength(d => 1 / Math.min(count(d.source), count(d.target))))  
  // Adjust charge force for many nodes
  .force("charge", d3.forceManyBody()
    // Scale strength based on node count
    .strength(d => -visualizationSettings.forceStrength / Math.sqrt(graphData.nodes.length))
    // Limit the maximum distance of effect for better performance
    .distanceMax(300))
  .force("center", d3.forceCenter(width / 2, height / 2))
  // Optional collision force to prevent overlap with large node counts
  .force("collision", d3.forceCollide().radius(d => visualizationSettings.nodeSize * 1.5));
```

#### Week 1: Node Filtering and Dynamic Sizing
```javascript
// Filter nodes based on importance metrics
const filteredNodes = graphData.nodes.filter(node => {
  // Show selected node and its immediate neighbors always
  if (node.id === selectedEntity.id || 
      graphData.links.some(link => 
        (link.source.id === selectedEntity.id && link.target.id === node.id) ||
        (link.target.id === selectedEntity.id && link.source.id === node.id))) {
    return true;
  }
  
  // For other nodes, filter based on importance or relationship count
  const relationshipCount = graphData.links.filter(link => 
    link.source.id === node.id || link.target.id === node.id
  ).length;
  
  // Show nodes with more connections and hide less connected nodes when graph is large
  return graphData.nodes.length < 100 || 
         relationshipCount > Math.log(graphData.nodes.length);
});

// Dynamic node sizing based on graph density
const nodeSizeScale = d3.scaleLinear()
  .domain([0, d3.max(graphData.nodes, d => {
    // Count relationships for each node
    return graphData.links.filter(link => 
      link.source.id === d.id || link.target.id === d.id
    ).length;
  })])
  .range([visualizationSettings.nodeSize, visualizationSettings.nodeSize * 2.5]);

// Apply dynamic sizing to nodes
node.attr("r", d => {
  // Selected node is always largest
  if (d.id === selectedEntity.id) {
    return visualizationSettings.nodeSize * 1.5;
  }
  
  // Otherwise size by number of connections
  const connectionCount = graphData.links.filter(link => 
    link.source.id === d.id || link.target.id === d.id
  ).length;
  
  return nodeSizeScale(connectionCount);
});
```

#### Week 2: Level-of-Detail Rendering
```javascript
// Implement zoom behavior
const zoom = d3.zoom()
  .scaleExtent([0.1, 8])
  .on("zoom", (event) => {
    // Update the transform of the main visualization group
    svg.select("g.visualization").attr("transform", event.transform);
    
    // Level of detail adjustments based on zoom level
    const scale = event.transform.k;
    
    // Show/hide labels based on zoom level
    svg.selectAll("text.node-label")
      .style("display", scale > 1.2 || d.id === selectedEntity.id ? "block" : "none")
      .style("font-size", `${Math.min(12, 10 * scale)}px`);
    
    // Show relationship labels only at higher zoom levels
    svg.selectAll("text.relationship-label")
      .style("display", scale > 2.5 ? "block" : "none");
      
    // Adjust node size based on zoom
    svg.selectAll("circle.node")
      .attr("r", d => {
        const baseSize = d.id === selectedEntity.id ? 
          visualizationSettings.nodeSize * 1.5 : 
          nodeSizeScale(connectionCount(d));
        // Adjust size inversely to zoom to maintain visual size
        return baseSize / Math.sqrt(scale);
      });
  });

// Apply zoom to SVG
svg.call(zoom);
```

#### Week 2: Node Aggregation and Progressive Loading
```javascript
// Node Aggregation Function for Dense Clusters
function aggregateNodes(nodes, links, threshold) {
  // Create a map of nodes by type
  const nodesByType = {};
  nodes.forEach(node => {
    if (!nodesByType[node.type]) {
      nodesByType[node.type] = [];
    }
    nodesByType[node.type].push(node);
  });
  
  // Aggregate nodes if count exceeds threshold
  const aggregatedNodes = [];
  const nodeMap = new Map(); // Original to aggregated mapping
  
  Object.entries(nodesByType).forEach(([type, typeNodes]) => {
    if (typeNodes.length > threshold) {
      // Create one aggregated node
      const aggregateNode = {
        id: `aggregate-${type}`,
        name: `${typeNodes.length} ${type} entities`,
        type: type,
        isAggregate: true,
        count: typeNodes.length,
        childNodes: typeNodes
      };
      aggregatedNodes.push(aggregateNode);
      
      // Map original nodes to this aggregate
      typeNodes.forEach(node => {
        nodeMap.set(node.id, aggregateNode.id);
      });
    } else {
      // Keep original nodes
      aggregatedNodes.push(...typeNodes);
      typeNodes.forEach(node => {
        nodeMap.set(node.id, node.id); // Map to self
      });
    }
  });
  
  // Remap links to use aggregated nodes
  const aggregatedLinks = [];
  links.forEach(link => {
    const sourceId = nodeMap.get(link.source.id || link.source);
    const targetId = nodeMap.get(link.target.id || link.target);
    
    // Avoid self-links in aggregates
    if (sourceId !== targetId) {
      // Check if this link already exists
      const existingLink = aggregatedLinks.find(l => 
        (l.source === sourceId && l.target === targetId) ||
        (l.source === targetId && l.target === sourceId)
      );
      
      if (existingLink) {
        // Increment weight if link exists
        existingLink.weight = (existingLink.weight || 1) + 1;
      } else {
        // Create new link
        aggregatedLinks.push({
          source: sourceId,
          target: targetId,
          type: link.type,
          weight: 1
        });
      }
    }
  });
  
  return { nodes: aggregatedNodes, links: aggregatedLinks };
}

// Progressive Loading Implementation
let allNodes = [...originalNodes]; // Store all nodes
let visibleNodes = allNodes.slice(0, 100); // Start with first 100
let isLoadingMore = false;

// Function to add more nodes progressively
function loadMoreNodes() {
  if (isLoadingMore || visibleNodes.length >= allNodes.length) return;
  
  isLoadingMore = true;
  
  // Add 50 more nodes
  const newBatch = allNodes.slice(visibleNodes.length, visibleNodes.length + 50);
  visibleNodes = [...visibleNodes, ...newBatch];
  
  // Update visualization with new nodes
  updateVisualization(visibleNodes);
  
  isLoadingMore = false;
}

// Add scroll or button-triggered loading
d3.select("#load-more-button").on("click", loadMoreNodes);

### Accessibility Requirements (Priority)

#### Week 1: Keyboard Navigation & Focus Management
```javascript
// Add keyboard navigation to graph
function setupKeyboardNavigation() {
  // Create tabindex for SVG elements
  svg.attr("tabindex", 0)
    .on("keydown", handleSvgKeydown);
  
  // Make nodes focusable
  node.attr("tabindex", 0)
    .attr("role", "button")
    .attr("aria-label", d => `${d.type} node: ${d.name}`)
    .on("keydown", handleNodeKeydown)
    .on("focus", handleNodeFocus);
  
  // SVG container keydown handler
  function handleSvgKeydown(event) {
    // Implement keyboard shortcuts for zooming/panning
    switch (event.key) {
      case "+":
        // Zoom in
        zoom.scaleBy(svg.transition().duration(300), 1.2);
        break;
      case "-":
        // Zoom out
        zoom.scaleBy(svg.transition().duration(300), 0.8);
        break;
      case "ArrowUp":
        // Pan up
        zoom.translateBy(svg.transition().duration(100), 0, -50);
        break;
      case "ArrowDown":
        // Pan down
        zoom.translateBy(svg.transition().duration(100), 0, 50);
        break;
      case "ArrowLeft":
        // Pan left
        zoom.translateBy(svg.transition().duration(100), -50, 0);
        break;
      case "ArrowRight":
        // Pan right
        zoom.translateBy(svg.transition().duration(100), 50, 0);
        break;
      case "0":
        // Reset zoom
        zoom.transform(svg.transition().duration(500), d3.zoomIdentity);
        break;
      case "Tab":
        // Focus first node on Tab
        if (!event.shiftKey && !document.activeElement.classList.contains("node")) {
          event.preventDefault();
          node.nodes()[0].focus();
        }
        break;
    }
  }
  
  // Node keydown handler
  function handleNodeKeydown(event, d) {
    switch (event.key) {
      case "Enter":
      case " ":
        // Select node on Enter or Space
        selectNode(d);
        break;
      case "ArrowRight":
        // Navigate to next node
        navigateToAdjacentNode(d, "next");
        break;
      case "ArrowLeft":
        // Navigate to previous node
        navigateToAdjacentNode(d, "prev");
        break;
      case "ArrowUp":
      case "ArrowDown":
        // Navigate to connected nodes
        navigateToConnectedNode(d, event.key === "ArrowUp" ? "source" : "target");
        break;
    }
  }
  
  // Node focus handler
  function handleNodeFocus(event, d) {
    // Highlight focused node
    d3.select(this).attr("stroke", "#000")
      .attr("stroke-width", 3)
      .attr("stroke-dasharray", "5,5");
    
    // Announce node to screen readers
    announceToScreenReader(`Focused on ${d.type} node: ${d.name}`);
  }
  
  // Helper functions for keyboard navigation
  function navigateToAdjacentNode(currentNode, direction) {
    const currentIndex = graphData.nodes.findIndex(n => n.id === currentNode.id);
    const nodeElements = node.nodes();
    
    let targetIndex;
    if (direction === "next") {
      targetIndex = (currentIndex + 1) % graphData.nodes.length;
    } else {
      targetIndex = (currentIndex - 1 + graphData.nodes.length) % graphData.nodes.length;
    }
    
    // Focus the target node
    nodeElements[targetIndex].focus();
  }
  
  function navigateToConnectedNode(currentNode, connectionType) {
    // Find connected nodes
    const connectedLinks = graphData.links.filter(link => {
      if (connectionType === "source") {
        return link.target.id === currentNode.id || link.target === currentNode.id;
      } else {
        return link.source.id === currentNode.id || link.source === currentNode.id;
      }
    });
    
    if (connectedLinks.length > 0) {
      // Get first connected node
      const link = connectedLinks[0];
      const connectedNodeId = connectionType === "source" 
        ? (link.source.id || link.source) 
        : (link.target.id || link.target);
        
      // Find node element and focus it
      const nodeElement = node.nodes()
        .find(el => d3.select(el).datum().id === connectedNodeId);
        
      if (nodeElement) {
        nodeElement.focus();
      }
    }
  }
  
  // Function to select a node programmatically
  function selectNode(d) {
    setSelectedEntity(d);
    fetchEntityDetails(d.id);
    fetchRelatedEntities(d.id);
    
    // Announce to screen readers
    announceToScreenReader(`Selected ${d.type}: ${d.name}`);
  }
}
```

#### Week 1: ARIA Enhancements
```javascript
// Add ARIA live region for announcements
function setupAccessibilityAnnouncements() {
  // Add a visually hidden announcement area
  const announcer = d3.select("body")
    .append("div")
    .attr("id", "graph-announcer")
    .attr("role", "status")
    .attr("aria-live", "polite")
    .style("position", "absolute")
    .style("width", "1px")
    .style("height", "1px")
    .style("margin", "-1px")
    .style("padding", "0")
    .style("overflow", "hidden")
    .style("clip", "rect(0, 0, 0, 0)")
    .style("white-space", "nowrap")
    .style("border", "0");
  
  // Function to make announcements
  window.announceToScreenReader = (message) => {
    announcer.text(message);
  };
  
  // Add landmark role to the main visualization
  svg.attr("role", "application")
    .attr("aria-label", "Knowledge Graph Visualization");
    
  // Add description
  svg.append("desc")
    .text("Interactive visualization of AI research entities and their relationships");
    
  // Add ARIA attributes to all controls
  d3.selectAll(".visualization-control")
    .attr("aria-controls", "knowledge-graph-visualization");
    
  // Add role and state to visualization settings
  d3.selectAll(".visualization-setting")
    .attr("role", "switch")
    .attr("aria-checked", d => d.active ? "true" : "false");
}
```

#### Week 2: Text Alternatives and Screen Reader Support
```javascript
// Create text-based alternative view of graph data
function createTextAlternative() {
  const container = d3.select("#graph-text-alternative");
  
  // Clear existing content
  container.html("");
  
  // Add summary information
  container.append("div")
    .attr("class", "text-alternative-summary")
    .html(`
      <h3>Knowledge Graph Summary</h3>
      <p>This graph contains ${graphData.nodes.length} entities and ${graphData.links.length} relationships.</p>
      <p>The central entity is ${selectedEntity.type}: <strong>${selectedEntity.name}</strong></p>
    `);
  
  // Create a list of entities grouped by type
  const entityTypes = [...new Set(graphData.nodes.map(n => n.type))];
  
  const entityList = container.append("div")
    .attr("class", "text-alternative-entities");
    
  entityList.append("h3").text("Entities by Type");
  
  entityTypes.forEach(type => {
    const typeNodes = graphData.nodes.filter(n => n.type === type);
    
    entityList.append("h4")
      .text(`${type} (${typeNodes.length})`);
      
    const list = entityList.append("ul");
    
    typeNodes.forEach(node => {
      list.append("li")
        .html(`
          <button class="entity-link" data-entity-id="${node.id}">
            ${node.name}
          </button>
          ${node.id === selectedEntity.id ? ' (Selected)' : ''}
        `);
    });
  });
  
  // Create a list of relationships
  const relationshipList = container.append("div")
    .attr("class", "text-alternative-relationships");
    
  relationshipList.append("h3")
    .text("Relationships");
    
  const relationshipsByType = {};
  graphData.links.forEach(link => {
    if (!relationshipsByType[link.type]) {
      relationshipsByType[link.type] = [];
    }
    
    const source = graphData.nodes.find(n => n.id === (link.source.id || link.source));
    const target = graphData.nodes.find(n => n.id === (link.target.id || link.target));
    
    if (source && target) {
      relationshipsByType[link.type].push({
        source,
        target,
        type: link.type
      });
    }
  });
  
  Object.entries(relationshipsByType).forEach(([type, relationships]) => {
    relationshipList.append("h4")
      .text(`${type} (${relationships.length})`);
      
    const list = relationshipList.append("ul");
    
    relationships.forEach(rel => {
      list.append("li")
        .html(`
          <button class="entity-link" data-entity-id="${rel.source.id}">
            ${rel.source.name}
          </button>
          <strong>${type}</strong>
          <button class="entity-link" data-entity-id="${rel.target.id}">
            ${rel.target.name}
          </button>
        `);
    });
  });
  
  // Add event listeners for entity links
  d3.selectAll(".entity-link").on("click", function() {
    const entityId = this.getAttribute("data-entity-id");
    const entity = graphData.nodes.find(n => n.id === entityId);
    
    if (entity) {
      setSelectedEntity(entity);
    }
  });
}
```

#### Week 2: High Contrast Mode
```javascript
// Implement high contrast mode
function applyHighContrastMode(enabled) {
  if (enabled) {
    // Apply high contrast colors
    svg.classed("high-contrast", true);
    
    // Modify entity colors to high contrast alternatives
    const highContrastColors = {
      MODEL: '#0000FF',      // Blue
      DATASET: '#008000',    // Green
      ALGORITHM: '#FF0000',  // Red
      PAPER: '#000000',      // Black
      AUTHOR: '#800080',     // Purple
      CODE: '#FF8000',       // Orange
      default: '#000000'     // Black
    };
    
    // Apply high contrast colors to nodes
    node.attr("fill", d => highContrastColors[d.type] || highContrastColors.default);
    
    // Increase contrast for links
    link.attr("stroke", "#000000")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 1);
    
    // Increase contrast for text
    label.attr("fill", "#000000")
      .attr("stroke", "#FFFFFF")
      .attr("stroke-width", 0.5);
    
    // Add stronger focus indicators
    node.attr("data-focus-visible-added", null)
      .attr("stroke-width", d => d.id === selectedEntity.id ? 4 : 0);
      
    // Add stronger backgrounds to labels for readability
    label.each(function() {
      const textElement = d3.select(this);
      const textBBox = this.getBBox();
      
      const textBackground = svg.insert("rect", () => this)
        .attr("x", textBBox.x - 2)
        .attr("y", textBBox.y - 2)
        .attr("width", textBBox.width + 4)
        .attr("height", textBBox.height + 4)
        .attr("fill", "#FFFFFF")
        .attr("stroke", "#000000")
        .attr("stroke-width", 1)
        .attr("rx", 3)
        .attr("ry", 3);
    });
  } else {
    // Restore default colors
    svg.classed("high-contrast", false);
    
    // Restore entity colors
    node.attr("fill", d => entityColors[d.type] || entityColors.default);
    
    // Restore default link style
    link.attr("stroke", "#999")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.6);
      
    // Restore default text style
    label.attr("fill", visualizationSettings.darkMode ? "#fff" : "#000")
      .attr("stroke", visualizationSettings.darkMode ? "#000" : "#fff")
      .attr("stroke-width", 0.3);
      
    // Remove text backgrounds
    svg.selectAll("rect.text-background").remove();
  }
}

### UI/UX Standards
- Use color coding for entity and relationship types
- Add zooming and panning controls with clear affordances
- Implement selection and focus mechanisms
- Use tooltips to explain visualization features 
- Ensure visualization controls have clear visual feedback
- Follow consistent visual hierarchy
- Include contextual help for complex features
- Consider visual information density for different screen sizes

## Research Query Interface

### Core Requirements (Weeks 3-4 Priority)
- Apply the same UX patterns established in the Knowledge Graph Explorer
- Implement step-by-step guided research process
- Use progressive disclosure for advanced query options
- Create meaningful empty states with clear guidance
- Add visual feedback for search relevance and quality

### Citation Management
- Implement citation export in multiple formats (BibTeX, APA, Chicago, MLA)
- Create reference management interface with filtering and sorting
- Add validation for required citation fields
- Implement DOI lookup for citation enrichment
- Support persistent citation storage

### Research Organization
- Implement history tracking for all research queries
- Create favorites and saved queries functionality
- Add tagging and collection organization
- Build history viewer with filtering capabilities
- Support re-running historical queries

### Query Experience
- Show loading indicators during queries
- Implement typeahead suggestions 
- Support structured and natural language queries
- Format results with proper citations
- Add filtering and sorting of results

## Implemented Features (Phases 1 & 2)

1. **Enhanced Error Handling**
   - ErrorBoundary component for critical UI sections
   - ErrorFallback for consistent error display
   - LoadingFallback for standardized loading states
   - Retry mechanisms with exponential backoff

2. **WebSocket Integration**
   - useWebSocket hook for WebSocket connections
   - WebSocketContext for application-wide real-time updates
   - NotificationCenter for displaying system notifications
   - Paper status subscriptions and updates

3. **Paper Status Visualization**
   - StatusIndicator component for visual status display
   - PaperStatusCard component with real-time updates
   - Progress visualization for paper processing stages
   - Detailed status history view

4. **Knowledge Graph Enhancement**
   - KnowledgeGraphFilter component with comprehensive filtering
   - Entity and relationship type filtering
   - Search capabilities for graph nodes
   - Year and confidence filtering options

5. **Paper Management**
   - PaperUploadDialog with multi-file support
   - Paper metadata editing capabilities
   - Upload progress visualization
   - Status tracking and error handling

## New UX Standards

Following our Knowledge Graph Explorer redesign, all components should follow these standards:

1. **Empty States**
   - Every component should have a meaningful empty state
   - Include step-by-step guidance for first-time users
   - Provide examples and suggested actions
   - Use visual elements to increase clarity

2. **Progressive Disclosure**
   - Start with simplified interface, reveal complexity progressively
   - Use accordions for grouping related settings
   - Organize options from most common to most advanced
   - Employ visual hierarchy to guide users

3. **Contextual Help**
   - Add tooltips to explain functionality
   - Include help icons for advanced features
   - Provide meaningful labels for all controls
   - Use inline illustrations for complex concepts

4. **Visual Feedback**
   - Every user action should receive immediate visual feedback
   - Highlight active states and selections
   - Show progress indicators for asynchronous operations
   - Use animations sparingly to guide attention

5. **Information Architecture**
   - Group related information in cards or panels
   - Use consistent layouts across similar components
   - Employ typography to create clear hierarchies
   - Balance information density with readability

6. **Accessibility**
   - Ensure keyboard navigation for all interactive elements
   - Include ARIA labels and roles for screen readers
   - Maintain sufficient color contrast ratios (WCAG AA compliance)
   - Provide alternative text for visualizations
   - Create text-based alternatives for graphical information
   - Support different viewport sizes with responsive design

## Current Development Priorities

1. **TypeScript Migration** (Priority: High - Weeks 1-2)
   - Create JSDoc type definitions as preparation (✅ Completed with typeDefs.js)
   - Add TypeScript and tsconfig.json configuration (✅ Completed)
   
   **Core System Migration (Week 1):**
   - Convert AuthContext to TypeScript with proper JWT typing
   - Convert WebSocketContext with message and subscription typing
   - Add comprehensive interface definitions for context values
   - Create reusable type utilities for common patterns
   
   **Hook Migration (Week 2):**
   - Convert useD3 hook with D3 selection typing
   - Implement generics for useFetch request/response types
   - Add proper typing for useWebSocket messages and events
   - Convert useLocalStorage with generic value typing
   
   **Future Phases:**
   - Convert UI components incrementally (starting with shared components)
   - Add comprehensive API model interfaces
   - Implement runtime type validation

2. **Performance Optimization** (Priority: Medium)
   - Implement React Query for data fetching and caching
   - Add virtualization for lists with many items
   - Optimize D3 rendering for large knowledge graphs
   - Add proper memoization for expensive computations
   - Implement lazy loading for less critical components

3. **Knowledge Graph Enhancements** (Priority: High) ✅ Phase 1 Completed ✅ Phase 2 Started
   - ✅ Implement dynamic rendering options and visualization settings
   - ✅ Create specialized visualization modes (clustering, relationship focus)
   - ✅ Add node clustering for complex graphs
   - ✅ Implement export capabilities (JSON, CSV, Neo4j, SVG, PNG)
   - ✅ Add research-focused analysis tools (metrics, frontiers)
   - ✅ Enhance user experience with tooltips and contextual guidance
   - ✅ Improve information hierarchy with collapsible sections
   - ✅ Add intuitive empty state with step-by-step guidance
   
   **Phase 2 (Next 2 Weeks - Highest Priority):**
   - Optimize performance for graphs with 1000+ nodes
     - Implement level-of-detail rendering based on zoom level
     - Add node aggregation for dense clusters
     - Optimize D3 force simulation parameters
     - Implement node filtering based on importance metrics
   
   - Add accessibility features for visualization
     - Implement keyboard navigation for graph interaction
     - Add screen reader support with ARIA attributes
     - Create text-based alternatives for visualization data
     - Add high-contrast mode support
     
   **Future Enhancements:**
   - Add WebGL rendering for very large graphs (1000+ nodes)
   - Implement URL state encoding for sharing specific views
   - Create additional layout options (hierarchical and radial)

4. **Paper Dashboard** (Priority: High) ✅ Completed
   - Create comprehensive paper management dashboard with PaperDashboard component
   - Implement advanced sorting options by date, title, status, and year
   - Add filtering capabilities by status, year and search term
   - Provide paper statistics and analytics
   - Create tabs for different paper status groups

5. **Developer Experience** (Priority: Medium)
   - Add Storybook for component documentation
   - Implement comprehensive Jest test suites
   - Set up GitHub Actions for CI/CD
   - Create component templates to ensure consistency
   - Add detailed JSDoc comments for all components
   - Implement Prettier for consistent code formatting
   - Create visual regression testing for UI components
   - Add accessibility testing with axe-core
   - Create comprehensive API documentation
   - Add JSDoc for all components and functions