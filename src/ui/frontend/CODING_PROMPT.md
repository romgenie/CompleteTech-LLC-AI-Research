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
   - Create text-based alternatives for complex visualizations
   - Implement high contrast mode for accessibility

2. **TypeScript Migration** (Weeks 1-2)
   - Convert core contexts (AuthContext, WebSocketContext) to TypeScript
   - Transform essential hooks (useD3, useFetch, useWebSocket) to TypeScript
   - Create comprehensive interface definitions for all API models
   - Implement proper typing for WebSocket message handling

3. **Research Enhancement** (Weeks 3-4)
   - Complete citation management with multiple export formats
   - Implement reference organization system with filtering
   - Add research history tracking with localStorage
   - Create favorites and saved queries functionality
   - Apply consistent UX patterns across research interface

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

### Knowledge Graph Performance Optimization (Priority)

#### Week 1: D3 Force Simulation Optimization
```javascript
/**
 * Optimizes D3 force simulation parameters for large graphs (1000+ nodes)
 * - Adjusts simulation parameters based on node count
 * - Scales forces proportionally for stability
 * - Implements performance boundaries for large datasets
 * 
 * @param {Array} nodes - Graph nodes array
 * @param {Array} links - Graph links array
 * @param {Object} settings - Visualization settings object
 * @returns {d3.forceSimulation} - Configured force simulation
 */
function createOptimizedForceSimulation(nodes, links, settings) {
  // Calculate optimal parameters based on graph size
  const nodeCount = nodes.length;
  const isLargeGraph = nodeCount > 500;
  const isVeryLargeGraph = nodeCount > 1000;
  
  // Adjust decay and strength based on graph size
  const alphaDecay = isVeryLargeGraph ? 0.035 : (isLargeGraph ? 0.028 : 0.0228);
  const velocityDecay = isVeryLargeGraph ? 0.5 : (isLargeGraph ? 0.4 : 0.4);
  const baseStrength = isVeryLargeGraph ? 
    settings.forceStrength * 1.5 : 
    settings.forceStrength;
  
  // Create simulation with optimized parameters
  const simulation = d3.forceSimulation(nodes)
    // Adjust cooling rate (higher = faster stabilization but potentially worse layout)
    .alphaDecay(alphaDecay)
    // Control "friction" - higher values = less bouncy movement
    .velocityDecay(velocityDecay);
    
  // Configure optimized link forces
  simulation.force("link", d3.forceLink(links)
    .id(d => d.id)
    // Increase distance proportionally for large graphs
    .distance(d => {
      const baseDistance = settings.nodeSize * 10;
      return isVeryLargeGraph ? baseDistance * 1.5 : baseDistance;
    })
    // Scale strength inversely to connection count for better stability
    .strength(d => {
      const source = typeof d.source === 'object' ? d.source.id : d.source;
      const target = typeof d.target === 'object' ? d.target.id : d.target;
      
      const sourceConnections = countConnections(source, links);
      const targetConnections = countConnections(target, links);
      
      return 1 / Math.min(Math.sqrt(sourceConnections), Math.sqrt(targetConnections));
    }));
  
  // Configure charge force (repulsion between nodes)
  simulation.force("charge", d3.forceManyBody()
    // Scale strength based on node count for better distribution
    .strength(d => -baseStrength / Math.sqrt(nodeCount))
    // Limit the maximum effect distance for better performance
    .distanceMax(isVeryLargeGraph ? 200 : 300)
    // Improve performance by limiting tree-based calculations
    .theta(0.8));
  
  // Keep visualization centered
  simulation.force("center", d3.forceCenter(width / 2, height / 2));
  
  // Add collision detection to prevent node overlap
  simulation.force("collision", d3.forceCollide()
    .radius(d => settings.nodeSize * (d.isSelected ? 1.75 : 1.5)));
    
  // For very large graphs, limit iterations for performance
  if (isVeryLargeGraph) {
    simulation.stop();
    for (let i = 0; i < 100; ++i) simulation.tick();
  }
  
  return simulation;
}

// Helper function to count node connections
function countConnections(nodeId, links) {
  return links.filter(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    return sourceId === nodeId || targetId === nodeId;
  }).length;
}
```

#### Week 1: Smart Node Filtering for Large Graphs
```javascript
/**
 * Filters nodes in large graphs based on importance metrics
 * - Always shows selected node and direct connections
 * - Filters distant nodes based on connectivity patterns
 * - Implements logarithmic scaling for better visibility
 * 
 * @param {Array} nodes - Complete nodes array
 * @param {Array} links - Complete links array
 * @param {Object} selected - Currently selected entity
 * @param {Object} settings - Visualization settings
 * @returns {Array} - Filtered nodes for display
 */
function getFilteredNodes(nodes, links, selected, settings) {
  // For smaller graphs, show everything
  if (nodes.length < settings.filterThreshold) {
    return nodes;
  }
  
  // Create node ID lookup for faster filtering
  const selectedId = selected?.id;
  const directConnectionIds = new Set();
  
  // Find all direct connections to selected node (fast lookup)
  if (selectedId) {
    links.forEach(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      
      if (sourceId === selectedId) directConnectionIds.add(targetId);
      if (targetId === selectedId) directConnectionIds.add(sourceId);
    });
  }
  
  // Calculate connection counts for importance filtering
  const connectionCounts = {};
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
  });
  
  // Calculate importance threshold based on graph size (logarithmic scaling)
  const importanceThreshold = Math.max(2, Math.log(nodes.length) / 2);
  
  // Filter nodes based on importance
  return nodes.filter(node => {
    // Always show selected node
    if (node.id === selectedId) return true;
    
    // Always show direct connections to selected node
    if (directConnectionIds.has(node.id)) return true;
    
    // Always show nodes with user-defined importance (if available)
    if (node.importance && node.importance > settings.importanceThreshold) return true;
    
    // For other nodes, filter based on connection count
    const connectionCount = connectionCounts[node.id] || 0;
    
    // Show nodes with significant connections
    return connectionCount >= importanceThreshold;
  });
}
```

#### Week 1: Dynamic Node Sizing and Visual Importance
```javascript
/**
 * Implements dynamic node sizing based on graph metrics
 * - Scales nodes based on connection count and importance
 * - Highlights selected nodes and their connections
 * - Adjusts sizing based on viewport and zoom level
 * 
 * @param {d3.Selection} nodeSelection - D3 selection of nodes
 * @param {Array} nodes - Complete nodes array
 * @param {Array} links - Complete links array
 * @param {Object} selected - Currently selected entity
 * @param {Object} settings - Visualization settings
 * @param {Number} scale - Current zoom scale
 */
function applyDynamicNodeSizing(nodeSelection, nodes, links, selected, settings, scale = 1) {
  // Calculate node importance based on connections
  const connectionCounts = {};
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
  });
  
  // Find maximum connection count for scaling
  const maxConnections = Math.max(
    1, 
    d3.max(Object.values(connectionCounts))
  );
  
  // Create scale function for node size based on connections
  const nodeSizeScale = d3.scaleLog()
    .domain([1, maxConnections])
    .range([settings.nodeSize, settings.nodeSize * 2.5])
    .clamp(true);
  
  // Find nodes connected to selected node
  const connectedToSelected = new Set();
  if (selected?.id) {
    links.forEach(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      
      if (sourceId === selected.id) connectedToSelected.add(targetId);
      if (targetId === selected.id) connectedToSelected.add(sourceId);
    });
  }
  
  // Apply dynamic sizing to nodes
  nodeSelection.attr("r", d => {
    // Calculate base node size based on connections
    const connectionCount = connectionCounts[d.id] || 1;
    let nodeSize = nodeSizeScale(connectionCount);
    
    // Adjust size for selected node
    if (d.id === selected?.id) {
      nodeSize = settings.nodeSize * 2;
    } 
    // Adjust size for nodes connected to selected node
    else if (connectedToSelected.has(d.id)) {
      nodeSize = settings.nodeSize * 1.5;
    }
    
    // If user-defined importance is available, factor it in
    if (d.importance) {
      nodeSize *= 0.8 + (d.importance * 0.4);
    }
    
    // Adjust size based on zoom level for consistent visual appearance
    return nodeSize / Math.sqrt(scale);
  });
  
  // Update node styling based on selection state
  nodeSelection
    .attr("stroke", d => {
      if (d.id === selected?.id) return "#000";
      if (connectedToSelected.has(d.id)) return "#555";
      return "#999";
    })
    .attr("stroke-width", d => {
      if (d.id === selected?.id) return 2.5 / Math.sqrt(scale);
      if (connectedToSelected.has(d.id)) return 1.5 / Math.sqrt(scale);
      return 1 / Math.sqrt(scale);
    });
}
```
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

#### Week 2: Comprehensive Accessibility Implementation

```javascript
/**
 * Implements full accessibility support for Knowledge Graph visualization
 * 
 * This module provides:
 * 1. Keyboard navigation for graph exploration
 * 2. Screen reader support with ARIA attributes
 * 3. Text-based alternative view of graph data
 * 4. High contrast mode for visual accessibility
 * 5. Focus management and indicators
 */

// 1. Keyboard Navigation System
/**
 * Sets up keyboard navigation and focus management for graph visualization
 * 
 * @param {d3.Selection} svg - The SVG container element
 * @param {d3.Selection} nodes - D3 selection of node elements
 * @param {Array} graphData - The complete graph data object
 * @param {Function} selectNode - Callback for node selection
 * @param {Object} zoomBehavior - D3 zoom behavior object
 */
function setupKeyboardNavigation(svg, nodes, graphData, selectNode, zoomBehavior) {
  // Make main SVG focusable with proper ARIA attributes
  svg
    .attr("tabindex", 0)
    .attr("role", "application")
    .attr("aria-label", "Knowledge Graph Visualization")
    .attr("aria-description", `Interactive visualization of ${graphData.nodes.length} entities and their relationships`)
    .on("focus", announceGraphSummary)
    .on("keydown", handleSvgKeydown);
  
  // Make individual nodes focusable and interactive
  nodes
    .attr("tabindex", 0)
    .attr("role", "button")
    .attr("aria-label", d => getNodeAriaLabel(d))
    .attr("data-entity-id", d => d.id)
    .attr("data-entity-type", d => d.type)
    .on("focus", handleNodeFocus)
    .on("blur", handleNodeBlur)
    .on("keydown", handleNodeKeydown);
  
  // Create global keyboard handler for SVG container
  function handleSvgKeydown(event) {
    // Prevent default browser scrolling with arrow keys when in graph
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
      event.preventDefault();
    }
    
    switch (event.key) {
      // Pan controls
      case "ArrowUp":
        zoomBehavior.translateBy(svg.transition().duration(100), 0, -50);
        announceToScreenReader("Panned up");
        break;
      case "ArrowDown":
        zoomBehavior.translateBy(svg.transition().duration(100), 0, 50);
        announceToScreenReader("Panned down");
        break;
      case "ArrowLeft":
        zoomBehavior.translateBy(svg.transition().duration(100), -50, 0);
        announceToScreenReader("Panned left");
        break;
      case "ArrowRight":
        zoomBehavior.translateBy(svg.transition().duration(100), 50, 0);
        announceToScreenReader("Panned right");
        break;
      
      // Zoom controls
      case "+":
      case "=":
        zoomBehavior.scaleBy(svg.transition().duration(200), 1.2);
        announceToScreenReader("Zoomed in");
        break;
      case "-":
        zoomBehavior.scaleBy(svg.transition().duration(200), 0.8);
        announceToScreenReader("Zoomed out");
        break;
      case "0": 
        zoomBehavior.transform(svg.transition().duration(500), d3.zoomIdentity);
        announceToScreenReader("Reset zoom level");
        break;
      
      // Tab to start/end of nodes
      case "Tab":
        if (!event.shiftKey) {
          // Find first visible node and focus it
          const firstNode = nodes.filter(":visible").nodes()[0];
          if (firstNode && document.activeElement === svg.node()) {
            event.preventDefault();
            firstNode.focus();
          }
        }
        break;
        
      // Help shortcut  
      case "?":
      case "h":
        showKeyboardShortcutsHelp();
        break;
        
      // Text view toggle  
      case "t":
        toggleTextAlternativeView();
        break;
    }
  }
  
  // Handle keyboard events on individual nodes
  function handleNodeKeydown(event, d) {
    switch (event.key) {
      // Selection controls
      case "Enter":
      case " ":
        event.preventDefault();
        selectNode(d);
        announceToScreenReader(`Selected ${d.type}: ${d.name}`);
        break;
      
      // Explore connected nodes
      case "ArrowLeft":
      case "ArrowRight":
        navigateToAdjacentNode(d, event.key === "ArrowRight" ? 1 : -1);
        break;
      case "ArrowUp":
      case "ArrowDown":
        navigateToConnectedNode(d, event.key === "ArrowUp" ? "source" : "target");
        break;
    }
  }
  
  // Apply visual focus indicator when node receives keyboard focus
  function handleNodeFocus(event, d) {
    const nodeElement = d3.select(this);
    
    // Store original appearance for restoration on blur
    this._originalFill = nodeElement.attr("fill");
    this._originalStroke = nodeElement.attr("stroke");
    this._originalStrokeWidth = nodeElement.attr("stroke-width");
    
    // Apply focus styling
    nodeElement
      .attr("stroke", "#000000")
      .attr("stroke-width", 3)
      .attr("stroke-dasharray", "5,5");
    
    // Announce focused node information
    announceToScreenReader(`Focused on ${d.type}: ${d.name}`);
    
    // Show node details in side panel if available
    if (typeof showNodeDetailsInPanel === 'function') {
      showNodeDetailsInPanel(d);
    }
  }
  
  // Remove focus styling when losing focus
  function handleNodeBlur(event) {
    const nodeElement = d3.select(this);
    
    // Restore original appearance
    if (this._originalFill) nodeElement.attr("fill", this._originalFill);
    if (this._originalStroke) nodeElement.attr("stroke", this._originalStroke);
    if (this._originalStrokeWidth) nodeElement.attr("stroke-width", this._originalStrokeWidth);
    
    // Remove dashed focus indicator
    nodeElement.attr("stroke-dasharray", null);
  }
  
  // Navigate from current node to next/previous node
  function navigateToAdjacentNode(currentNode, direction) {
    const visibleNodes = nodes.filter(":visible").nodes();
    const currentIndex = visibleNodes.findIndex(
      node => d3.select(node).datum().id === currentNode.id
    );
    
    if (currentIndex === -1) return;
    
    // Calculate target index with wraparound
    const targetIndex = (currentIndex + direction + visibleNodes.length) % visibleNodes.length;
    
    // Focus the target node
    visibleNodes[targetIndex].focus();
  }
  
  // Navigate to nodes connected to current node
  function navigateToConnectedNode(currentNode, direction) {
    // Find connected nodes
    const connections = graphData.links.filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      
      return direction === "source" 
        ? targetId === currentNode.id  // Find incoming links
        : sourceId === currentNode.id; // Find outgoing links
    });
    
    if (connections.length === 0) {
      announceToScreenReader(`No ${direction === "source" ? "incoming" : "outgoing"} connections found`);
      return;
    }
    
    // Get first connected node
    const connection = connections[0];
    const connectedNodeId = direction === "source"
      ? (typeof connection.source === 'object' ? connection.source.id : connection.source)
      : (typeof connection.target === 'object' ? connection.target.id : connection.target);
    
    // Find and focus the connected node element
    const connectedNodeElement = nodes.nodes()
      .find(node => d3.select(node).datum().id === connectedNodeId);
    
    if (connectedNodeElement) {
      connectedNodeElement.focus();
      
      // If there are multiple connections, announce count
      if (connections.length > 1) {
        announceToScreenReader(`Navigated to 1 of ${connections.length} ${direction === "source" ? "incoming" : "outgoing"} connections`);
      }
    }
  }
  
  // Generate accessible label for node
  function getNodeAriaLabel(node) {
    let label = `${node.type || 'entity'}: ${node.name}`;
    
    // Add connection count if available
    const connectionCount = graphData.links.filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      return sourceId === node.id || targetId === node.id;
    }).length;
    
    if (connectionCount > 0) {
      label += `, with ${connectionCount} connections`;
    }
    
    // Add properties if available
    if (node.properties && Object.keys(node.properties).length > 0) {
      const propertyCount = Object.keys(node.properties).length;
      label += `, containing ${propertyCount} properties`;
    }
    
    return label;
  }
  
  // Announce graph summary to screen readers
  function announceGraphSummary() {
    const summary = `Knowledge graph with ${graphData.nodes.length} entities and ${graphData.links.length} relationships. Use arrow keys to navigate, plus and minus to zoom, Enter to select, and T for text view.`;
    announceToScreenReader(summary);
  }
  
  // Display keyboard shortcut help dialog
  function showKeyboardShortcutsHelp() {
    // Implementation depends on UI framework (Material UI, etc.)
    // This could open a modal or popover with shortcuts list
    if (typeof showHelpDialog === 'function') {
      showHelpDialog('keyboard-shortcuts');
    } else {
      // Fallback announcement
      announceToScreenReader(`
        Keyboard shortcuts: 
        Arrow keys to navigate between nodes or pan the graph.
        Enter or Space to select a node.
        Plus or Minus to zoom.
        0 to reset zoom.
        T to toggle text view.
        H or question mark for this help.
      `);
    }
  }
}

// 2. Screen Reader Support
/**
 * Sets up screen reader support with ARIA live regions and announcements
 * 
 * @returns {Function} Announcement function to use throughout the application
 */
function setupScreenReaderSupport() {
  // Create ARIA live region for announcements
  const liveRegion = d3.select("body")
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
  
  // Create function to make announcements
  return function announceToScreenReader(message) {
    // First clear the region (needed for some screen readers to announce repeated content)
    liveRegion.text("");
    
    // Use setTimeout to ensure screen readers register the new content
    setTimeout(() => {
      liveRegion.text(message);
    }, 50);
  };
}

// 3. Text-Based Alternative View
/**
 * Creates a comprehensive text-based alternative of the graph visualization
 * 
 * @param {Object} graphData - The complete graph data object
 * @param {Object} selectedEntity - Currently selected entity
 * @param {Function} selectEntity - Callback for entity selection
 * @param {String} containerId - ID of container for text alternative
 */
function createTextAlternative(graphData, selectedEntity, selectEntity, containerId = "graph-text-alternative") {
  const container = d3.select(`#${containerId}`);
  
  // Clear existing content
  container.html("");
  
  // 1. Add summary information section
  const summarySection = container.append("section")
    .attr("class", "text-alternative-summary")
    .attr("aria-labelledby", "graph-summary-heading");
    
  summarySection.append("h2")
    .attr("id", "graph-summary-heading")
    .text("Knowledge Graph Summary");
    
  summarySection.append("p")
    .html(`This knowledge graph contains <strong>${graphData.nodes.length}</strong> entities and <strong>${graphData.links.length}</strong> relationships.`);
  
  if (selectedEntity?.id) {
    summarySection.append("p")
      .html(`The central entity is <strong>${selectedEntity.type}: ${selectedEntity.name}</strong>`);
  }
  
  // 2. Create filtering and navigation controls
  const controlsSection = container.append("section")
    .attr("class", "text-alternative-controls");
    
  // Filters for entity types
  const entityTypes = [...new Set(graphData.nodes.map(n => n.type))];
  
  controlsSection.append("h3")
    .text("Filter Entities");
    
  // Add filter buttons/checkboxes by type
  const filterForm = controlsSection.append("form")
    .attr("class", "entity-type-filters")
    .attr("aria-label", "Entity type filters");
    
  entityTypes.forEach(type => {
    const typeCount = graphData.nodes.filter(n => n.type === type).length;
    const filterId = `filter-${type.toLowerCase()}`;
    
    const filterItem = filterForm.append("div")
      .attr("class", "filter-item");
      
    filterItem.append("input")
      .attr("type", "checkbox")
      .attr("id", filterId)
      .attr("name", "entity-type")
      .attr("value", type)
      .attr("checked", true)
      .on("change", function() {
        // Toggle visibility of corresponding entity sections
        const typeSection = container.select(`#entity-type-${type.toLowerCase()}`);
        typeSection.style("display", this.checked ? "block" : "none");
      });
      
    filterItem.append("label")
      .attr("for", filterId)
      .text(`${type} (${typeCount})`);
  });
  
  // 3. Create entity listings organized by type
  const entitiesSection = container.append("section")
    .attr("class", "text-alternative-entities")
    .attr("aria-labelledby", "entities-heading");
    
  entitiesSection.append("h2")
    .attr("id", "entities-heading")
    .text("Entities by Type");
  
  // Create a subsection for each entity type
  entityTypes.forEach(type => {
    const typeNodes = graphData.nodes.filter(n => n.type === type);
    const typeSectionId = `entity-type-${type.toLowerCase()}`;
    
    const typeSection = entitiesSection.append("section")
      .attr("id", typeSectionId)
      .attr("class", "entity-type-section")
      .attr("aria-labelledby", `${typeSectionId}-heading`);
      
    typeSection.append("h3")
      .attr("id", `${typeSectionId}-heading`)
      .text(`${type} (${typeNodes.length})`);
    
    // Create a table for better screen reader navigation
    const table = typeSection.append("table")
      .attr("class", "entity-table")
      .attr("aria-label", `${type} entities`);
      
    // Add table header
    table.append("thead").append("tr")
      .html(`
        <th scope="col">Name</th>
        <th scope="col">Connections</th>
        <th scope="col">Actions</th>
      `);
    
    // Add table body with entity rows
    const tbody = table.append("tbody");
    
    typeNodes.forEach(node => {
      // Count connections for this node
      const connectionCount = graphData.links.filter(link => {
        const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
        const targetId = typeof link.target === 'object' ? link.target.id : link.target;
        return sourceId === node.id || targetId === node.id;
      }).length;
      
      // Create table row
      const row = tbody.append("tr")
        .attr("class", node.id === selectedEntity?.id ? "selected-entity" : "");
      
      // Entity name cell  
      row.append("td")
        .html(`
          <span class="entity-name" ${node.id === selectedEntity?.id ? 'aria-current="true"' : ''}>
            ${node.name}
            ${node.id === selectedEntity?.id ? ' <span class="visually-hidden">(Selected)</span>' : ''}
          </span>
        `);
      
      // Connection count cell  
      row.append("td")
        .text(connectionCount);
      
      // Actions cell with select button  
      row.append("td")
        .html(`
          <button 
            type="button" 
            class="entity-select-btn" 
            data-entity-id="${node.id}"
            aria-label="Select ${node.type}: ${node.name}"
          >
            Select
          </button>
        `);
    });
  });
  
  // 4. Create relationships section organized by type
  const relationshipsSection = container.append("section")
    .attr("class", "text-alternative-relationships")
    .attr("aria-labelledby", "relationships-heading");
    
  relationshipsSection.append("h2")
    .attr("id", "relationships-heading")
    .text("Relationships");
  
  // Group relationships by type
  const relationshipsByType = {};
  graphData.links.forEach(link => {
    const type = link.type || "default";
    if (!relationshipsByType[type]) {
      relationshipsByType[type] = [];
    }
    
    // Find source and target node objects
    const source = graphData.nodes.find(n => n.id === (typeof link.source === 'object' ? link.source.id : link.source));
    const target = graphData.nodes.find(n => n.id === (typeof link.target === 'object' ? link.target.id : link.target));
    
    if (source && target) {
      relationshipsByType[type].push({ source, target, type });
    }
  });
  
  // Create a subsection for each relationship type
  Object.entries(relationshipsByType).forEach(([type, relationships]) => {
    const typeSectionId = `relationship-type-${type.toLowerCase().replace(/\s+/g, '-')}`;
    
    const typeSection = relationshipsSection.append("section")
      .attr("id", typeSectionId)
      .attr("class", "relationship-type-section")
      .attr("aria-labelledby", `${typeSectionId}-heading`);
      
    typeSection.append("h3")
      .attr("id", `${typeSectionId}-heading`)
      .text(`${type} (${relationships.length})`);
    
    // Create a table for better screen reader navigation
    const table = typeSection.append("table")
      .attr("class", "relationship-table")
      .attr("aria-label", `${type} relationships`);
      
    // Add table header
    table.append("thead").append("tr")
      .html(`
        <th scope="col">Source</th>
        <th scope="col">Relationship</th>
        <th scope="col">Target</th>
      `);
    
    // Add table body with relationship rows
    const tbody = table.append("tbody");
    
    relationships.forEach(rel => {
      tbody.append("tr")
        .html(`
          <td>
            <button 
              type="button" 
              class="entity-select-btn" 
              data-entity-id="${rel.source.id}"
              aria-label="Select source: ${rel.source.name}"
            >
              ${rel.source.name}
            </button>
          </td>
          <td><strong>${type}</strong></td>
          <td>
            <button 
              type="button" 
              class="entity-select-btn" 
              data-entity-id="${rel.target.id}"
              aria-label="Select target: ${rel.target.name}"
            >
              ${rel.target.name}
            </button>
          </td>
        `);
    });
  });
  
  // 5. Add selected entity details section if entity is selected
  if (selectedEntity?.id) {
    const detailsSection = container.append("section")
      .attr("class", "text-alternative-details")
      .attr("aria-labelledby", "entity-details-heading");
      
    detailsSection.append("h2")
      .attr("id", "entity-details-heading")
      .text("Selected Entity Details");
    
    // Create definition list for entity properties
    const dl = detailsSection.append("dl")
      .attr("class", "entity-properties");
      
    // Add basic entity information
    dl.append("dt").text("Name");
    dl.append("dd").text(selectedEntity.name);
    
    dl.append("dt").text("Type");
    dl.append("dd").text(selectedEntity.type);
    
    // Add any additional properties
    if (selectedEntity.properties) {
      Object.entries(selectedEntity.properties).forEach(([key, value]) => {
        dl.append("dt").text(key);
        dl.append("dd").text(value);
      });
    }
  }
  
  // 6. Add event listeners for entity selection buttons
  container.selectAll(".entity-select-btn").on("click", function() {
    const entityId = this.getAttribute("data-entity-id");
    const entity = graphData.nodes.find(n => n.id === entityId);
    
    if (entity && typeof selectEntity === 'function') {
      selectEntity(entity);
      
      // Announce selection to screen readers
      const announcer = d3.select("#graph-announcer");
      if (announcer.size() > 0) {
        announcer.text(`Selected ${entity.type}: ${entity.name}`);
      }
    }
  });
  
  // Add CSS for visually hidden elements (for screen readers only)
  if (!document.getElementById("a11y-styles")) {
    const style = document.createElement("style");
    style.id = "a11y-styles";
    style.textContent = `
      .visually-hidden {
        position: absolute;
        width: 1px;
        height: 1px;
        margin: -1px;
        padding: 0;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
      }
      
      .selected-entity {
        background-color: #f0f7ff;
      }
      
      .text-alternative-controls {
        margin-bottom: 1.5rem;
      }
      
      .entity-type-filters {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      
      .filter-item {
        display: flex;
        align-items: center;
        margin-right: 1rem;
      }
      
      .entity-table,
      .relationship-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1.5rem;
      }
      
      .entity-table th,
      .entity-table td,
      .relationship-table th,
      .relationship-table td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid #eee;
      }
    `;
    document.head.appendChild(style);
  }
  
  // Return the container for potential further customization
  return container;
}

// 4. High Contrast Mode
/**
 * Applies high contrast mode for better visibility
 * 
 * @param {Boolean} enabled - Whether to enable high contrast mode
 * @param {d3.Selection} svg - The SVG container element
 * @param {d3.Selection} nodes - D3 selection of node elements
 * @param {d3.Selection} links - D3 selection of link elements
 * @param {d3.Selection} labels - D3 selection of label elements
 */
function applyHighContrastMode(enabled, svg, nodes, links, labels) {
  // Toggle high-contrast class on SVG for CSS targeting
  svg.classed("high-contrast", enabled);
  
  if (enabled) {
    // High contrast color palette (WCAG AA compliant)
    const highContrastColors = {
      MODEL: '#0000FF',      // Blue
      DATASET: '#008000',    // Green
      ALGORITHM: '#FF0000',  // Red
      PAPER: '#000000',      // Black
      AUTHOR: '#800080',     // Purple
      CODE: '#FF8000',       // Orange
      // Add additional entity types with distinct colors
      default: '#000000'     // Default black
    };
    
    // Apply high contrast colors to nodes
    nodes.attr("fill", d => highContrastColors[d.type] || highContrastColors.default)
      .attr("stroke", "#FFFFFF")
      .attr("stroke-width", d => d.isSelected ? 4 : 2);
    
    // Increase contrast for links
    links.attr("stroke", "#000000")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 1);
    
    // Add background to labels for better readability
    labels.each(function() {
      const label = d3.select(this);
      const bbox = this.getBBox();
      
      // Create background rect if it doesn't exist
      let bgRect = svg.select(`rect.label-bg-${label.attr("data-id")}`);
      
      if (bgRect.empty()) {
        bgRect = svg.insert("rect", () => this)
          .attr("class", `label-bg label-bg-${label.attr("data-id")}`)
          .attr("rx", 3)
          .attr("ry", 3);
      }
      
      // Position background
      bgRect
        .attr("x", bbox.x - 2)
        .attr("y", bbox.y - 2)
        .attr("width", bbox.width + 4)
        .attr("height", bbox.height + 4)
        .attr("fill", "#FFFFFF")
        .attr("stroke", "#000000")
        .attr("stroke-width", 1);
      
      // Ensure text is on top and high contrast
      label
        .attr("fill", "#000000")
        .attr("font-weight", "bold");
    });
  } else {
    // Restore default appearance
    nodes.attr("fill", d => d.color || "#1976d2")
      .attr("stroke", "#ffffff")
      .attr("stroke-width", d => d.isSelected ? 2 : 1);
    
    links.attr("stroke", "#999")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.6);
    
    // Remove label backgrounds
    svg.selectAll("rect.label-bg").remove();
    
    // Restore label styling
    labels.attr("fill", d => d.isSelected ? "#000000" : "#333333")
      .attr("font-weight", d => d.isSelected ? "bold" : "normal");
  }
}
```
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

1. **TypeScript Migration** (In Progress - Weeks 1-2)
   - ✅ Create JSDoc type definitions as preparation (Completed with typeDefs.js)
   - ✅ Add TypeScript and tsconfig.json configuration (Completed)
   
   **Core System Migration (Week 1 - Active):**
   - 🔄 Convert AuthContext to TypeScript with proper JWT typing
     ```typescript
     interface User {
       id: string;
       username: string;
       roles: string[];
       email?: string;
     }

     interface AuthState {
       currentUser: User | null;
       token: string | null;
       loading: boolean;
       error: Error | null;
       isAuthenticated: boolean;
     }

     interface AuthContextType extends AuthState {
       login: (username: string, password: string) => Promise<User>;
       logout: () => void;
     }
     ```
   - 🔄 Convert WebSocketContext with message and subscription typing
     ```typescript
     interface WebSocketMessage {
       type: string;
       [key: string]: any;
     }

     interface NotificationMessage extends WebSocketMessage {
       type: 'notification';
       id: string;
       title: string;
       message: string;
       category: 'info' | 'success' | 'warning' | 'error' | 'paper_status';
       timestamp: string;
     }

     interface SubscriptionMessage extends WebSocketMessage {
       type: 'subscribe' | 'unsubscribe';
       channel: string;
     }

     interface WebSocketContextType {
       isConnected: boolean;
       connect: () => void;
       disconnect: () => void;
       sendMessage: (data: WebSocketMessage) => boolean;
       lastMessage: WebSocketMessage | null;
       error: Event | null;
       notifications: NotificationMessage[];
       clearNotifications: () => void;
       removeNotification: (id: string) => void;
       subscribeToPaperUpdates: (paperId: string) => boolean;
       unsubscribeFromPaperUpdates: (paperId: string) => boolean;
     }
     ```
   - 🔄 Add comprehensive interface definitions for context values
   - 🔄 Create reusable type utilities for common patterns
   
   **Hook Migration (Week 2 - Planned):**
   - 🔄 Convert useD3 hook with D3 selection typing
     ```typescript
     function useD3<GElement extends d3.BaseType, PDatum, PGroup extends d3.BaseType>(
       renderFn: (selection: d3.Selection<GElement, PDatum, PGroup, unknown>) => void,
       dependencies: React.DependencyList = []
     ): React.RefObject<GElement> {
       const ref = useRef<GElement>(null);
       
       useEffect(() => {
         if (ref.current) {
           renderFn(d3.select(ref.current));
         }
         // Cleanup function
         return () => {
           if (ref.current) {
             d3.select(ref.current).selectAll('*').interrupt();
           }
         };
       }, dependencies);
       
       return ref;
     }
     ```
   - 🔄 Implement generics for useFetch request/response types
     ```typescript
     interface UseFetchOptions<TRequestData = any> extends Omit<AxiosRequestConfig, 'url'> {
       data?: TRequestData;
     }

     interface UseFetchResult<TData = any> {
       data: TData | null;
       loading: boolean;
       error: Error | null;
       refetch: () => Promise<void>;
     }

     function useFetch<TData = any, TRequestData = any>(
       url: string, 
       options?: UseFetchOptions<TRequestData>,
       immediate: boolean = true,
       mockDataFn?: () => TData
     ): UseFetchResult<TData> {
       // Implementation...
     }
     ```
   - 🔄 Add proper typing for useWebSocket messages and events
   - 🔄 Convert useLocalStorage with generic value typing
     ```typescript
     function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void] {
       // Implementation...
     }
     ```
   
   **Future Phases:**
   - Convert UI components incrementally (starting with shared components)
   - Add comprehensive API model interfaces
   - Implement runtime type validation

2. **Knowledge Graph Performance & Accessibility** (Highest Priority - Weeks 1-2)
   - 🔄 **Performance for Large Graphs** (Week 1)
     - Optimize D3 force simulation parameters
       ```javascript
       const simulation = d3.forceSimulation(graphData.nodes)
         // Reduce alpha decay for more stable layout with large graphs
         .alphaDecay(0.028)  // default is 0.0228
         // Configure forces for better performance
         .force("link", d3.forceLink(graphData.links)
           .id(d => d.id)
           .distance(d => visualizationSettings.nodeSize * 10)
           .strength(d => 1 / Math.min(count(d.source), count(d.target))))
         // Scale charge force based on node count
         .force("charge", d3.forceManyBody()
           .strength(d => -visualizationSettings.forceStrength / Math.sqrt(graphData.nodes.length))
           .distanceMax(300))
         .force("center", d3.forceCenter(width / 2, height / 2))
         // Optional collision detection for large graphs
         .force("collision", d3.forceCollide().radius(d => visualizationSettings.nodeSize * 1.5));
       ```
     - Implement node filtering based on importance metrics
       ```javascript
       // Filter nodes based on importance or connectivity
       const filteredNodes = graphData.nodes.filter(node => {
         // Always show selected node and neighbors
         if (node.id === selectedEntity.id || isDirectlyConnected(node)) {
           return true;
         }
         
         // For other nodes, filter based on importance
         const connectionCount = countConnections(node);
         return connectionCount > Math.log(graphData.nodes.length);
       });
       ```
     - Add dynamic node sizing based on connectivity
   
   - 🔄 **Accessibility Enhancements** (Week 1-2)
     - Implement keyboard navigation for graph interaction
       ```javascript
       // Add keyboard navigation to graph
       svg.attr("tabindex", 0)
         .on("keydown", handleGraphKeydown);
       
       node.attr("tabindex", 0)
         .attr("role", "button")
         .attr("aria-label", d => `${d.type} node: ${d.name}`)
         .on("keydown", handleNodeKeydown)
         .on("focus", handleNodeFocus);
       ```
     - Add ARIA attributes with screen reader support
       ```javascript
       // Add live region for announcements
       const announcer = d3.select("body")
         .append("div")
         .attr("id", "graph-announcer")
         .attr("role", "status")
         .attr("aria-live", "polite")
         .style("position", "absolute")
         .style("clip", "rect(0,0,0,0)");
       ```
     - Create text-based alternatives for visualization data
     - Add high-contrast mode support
       ```javascript
       function applyHighContrastMode(enabled) {
         if (enabled) {
           // High contrast colors for different entity types
           const highContrastColors = {
             MODEL: '#0000FF',      // Blue
             DATASET: '#008000',    // Green
             ALGORITHM: '#FF0000',  // Red
             PAPER: '#000000',      // Black
             AUTHOR: '#800080',     // Purple
             CODE: '#FF8000',       // Orange
           };
           
           // Apply to nodes and ensure strong borders
           node.attr("fill", d => highContrastColors[d.type] || '#000000')
             .attr("stroke", "#FFFFFF")
             .attr("stroke-width", 2);
           
           // Increase contrast for links and labels
           link.attr("stroke", "#000000")
             .attr("stroke-width", 2)
             .attr("stroke-opacity", 1);
           
           label.attr("fill", "#000000")
             .attr("stroke", "#FFFFFF")
             .attr("stroke-width", 0.5);
         }
       }
       ```
   
   - 🔄 **Level-of-Detail Rendering** (Week 2)
     - Implement zoom-dependent detail
       ```javascript
       // Add zoom behavior
       const zoom = d3.zoom()
         .scaleExtent([0.1, 8])
         .on("zoom", (event) => {
           svg.select("g.visualization").attr("transform", event.transform);
           
           // Level of detail based on zoom level
           const scale = event.transform.k;
           
           // Show labels based on zoom level
           svg.selectAll("text.node-label")
             .style("display", scale > 1.2 ? "block" : "none");
             
           // Show relationship labels only at higher zoom levels
           svg.selectAll("text.relationship-label")
             .style("display", scale > 2.5 ? "block" : "none");
             
           // Adjust node size inversely to zoom
           svg.selectAll("circle.node")
             .attr("r", d => baseNodeSize(d) / Math.sqrt(scale));
         });
       ```
     - Add node aggregation for dense clusters
     - Create progressive loading mechanism for large graphs
   
   **Future Enhancements:**
   - WebGL rendering for very large graphs (5000+ nodes)
   - URL state encoding for sharing specific views
   - Additional layout options (hierarchical and radial)

3. **Research Enhancement** (Planned - Weeks 3-4)
   - 🔄 **Citation Management** (Week 3)
     - Implement citation export in multiple formats (BibTeX, APA, Chicago)
     - Create reference management interface
     - Add DOI lookup and citation validation
   
   - 🔄 **Research Organization** (Week 4)
     - Add research history with local storage
     - Implement favorites and saved queries
     - Create history viewer with filtering
   
   - 🔄 **Research UI Improvements** (Weeks 3-4)
     - Apply Knowledge Graph UX patterns (progressive disclosure, contextual help)
     - Create step-by-step guided research process
     - Add visual feedback for search relevance
   
   **Future Enhancements:**
   - Add collaborative research features
   - Implement PDF and markdown export
   - Create advanced query builder interface

4. **Developer Experience & Technical Debt** (Ongoing)
   - Set up comprehensive testing with React Testing Library
   - Implement accessibility testing with axe-core
   - Add Storybook for component documentation
   - Set up CI/CD with GitHub Actions
   - Add detailed JSDoc comments for all components
   - Implement Prettier for consistent code formatting