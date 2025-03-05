import { Entity, Relationship, EntityType } from '../types';

interface GraphData {
  nodes: Entity[];
  links: Relationship[];
}

interface VisualizationSettings {
  nodeSize: number;
  forceStrength: number;
  showLabels: boolean;
  darkMode: boolean;
  highlightNeighbors?: boolean;
  showRelationshipLabels?: boolean;
  clusterByType?: boolean;
  maxRelationshipDepth?: number;
  timeBasedLayout?: boolean;
  filterThreshold?: number;
  importanceThreshold?: number;
  levelOfDetail?: boolean;
  [key: string]: any;
}

// NodeFocusInfo moved to export interface below

/**
 * Filters nodes in large graphs based on importance metrics
 * - Always shows selected node and direct connections
 * - Filters distant nodes based on connectivity patterns
 * - Implements logarithmic scaling for better visibility
 * 
 * @param nodes - Complete nodes array
 * @param links - Complete links array
 * @param selectedEntityId - Currently selected entity ID
 * @param settings - Visualization settings
 * @returns Filtered nodes for display
 */
export function getFilteredNodes(
  nodes: Entity[],
  links: Relationship[],
  selectedEntityId: string | null,
  settings: VisualizationSettings
): Entity[] {
  // Default thresholds if not provided
  const filterThreshold = settings.filterThreshold || 100;
  const importanceThreshold = settings.importanceThreshold || 0.5;

  // For smaller graphs, show everything
  if (nodes.length < filterThreshold) {
    return nodes;
  }
  
  // Create node ID lookup for faster filtering
  const directConnectionIds = new Set<string>();
  
  // Find all direct connections to selected node (O(1) lookup)
  if (selectedEntityId) {
    links.forEach(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      
      if (sourceId === selectedEntityId) directConnectionIds.add(targetId);
      if (targetId === selectedEntityId) directConnectionIds.add(sourceId);
    });
  }
  
  // Calculate connection counts for importance filtering
  const connectionCounts: Record<string, number> = {};
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
  });
  
  // Calculate importance threshold based on graph size (logarithmic scaling)
  const importanceThresholdDynamic = Math.max(2, Math.log(nodes.length) / 2);
  
  // Filter nodes based on importance
  return nodes.filter(node => {
    // Always show selected node
    if (node.id === selectedEntityId) return true;
    
    // Always show direct connections to selected node
    if (directConnectionIds.has(node.id)) return true;
    
    // Always show nodes with user-defined importance (if available)
    if (node.importance && node.importance > importanceThreshold) return true;
    
    // For other nodes, filter based on connection count
    const connectionCount = connectionCounts[node.id] || 0;
    
    // Show nodes with significant connections
    return connectionCount >= importanceThresholdDynamic;
  });
}

/**
 * Creates a dynamic node size scale based on connection count
 * 
 * @param nodes - Graph nodes
 * @param links - Graph links
 * @param baseSize - Base node size
 * @returns Function that returns size for each node
 */
export function createNodeSizeScale(
  nodes: Entity[],
  links: Relationship[],
  baseSize: number
): (node: Entity) => number {
  // Calculate connection counts
  const connectionCounts: Record<string, number> = {};
  
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
  });
  
  // Get maximum connection count (or 1 if no connections)
  const maxConnections = Math.max(1, ...Object.values(connectionCounts));
  
  // Return sizing function
  return (node: Entity): number => {
    const connectionCount = connectionCounts[node.id] || 1;
    
    // Use logarithmic scale to avoid extremely large nodes
    const scaleFactor = Math.log(connectionCount + 1) / Math.log(maxConnections + 1);
    
    // Scale from baseSize to 2.5x baseSize
    return baseSize * (1 + scaleFactor * 1.5);
  };
}

/**
 * Count connections for a specific node
 * 
 * @param nodeId - The ID of the node
 * @param links - All graph links
 * @returns The number of connections
 */
export function countNodeConnections(nodeId: string, links: Relationship[]): number {
  return links.filter(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    return sourceId === nodeId || targetId === nodeId;
  }).length;
}

/**
 * Creates optimized force simulation parameters for large graphs
 * 
 * @param nodes - Graph nodes
 * @param settings - Visualization settings
 * @returns Optimized force simulation parameters
 */
export function createOptimizedForceParameters(
  nodes: Entity[],
  settings: VisualizationSettings
): { 
  alphaDecay: number;
  velocityDecay: number;
  forceStrength: number;
  linkDistance: number;
  chargeStrength: number;
  collisionRadius: number;
  alphaMin: number;
  iterations: number;
} {
  // Calculate optimal parameters based on graph size
  const nodeCount = nodes.length;
  const isLargeGraph = nodeCount > 500;
  const isVeryLargeGraph = nodeCount > 1000;
  const isExtremeGraph = nodeCount > 5000;
  
  // Adjust decay and strength based on graph size
  const alphaDecay = isExtremeGraph ? 0.04 : isVeryLargeGraph ? 0.035 : (isLargeGraph ? 0.028 : 0.0228);
  const velocityDecay = isExtremeGraph ? 0.6 : isVeryLargeGraph ? 0.5 : (isLargeGraph ? 0.4 : 0.4);
  const forceStrength = settings.forceStrength || 500;
  const baseForceStrength = isVeryLargeGraph ? forceStrength * 1.5 : forceStrength;
  
  // Calculate link distance - increase distance for larger graphs
  const linkDistance = isExtremeGraph
    ? settings.nodeSize * 20
    : isVeryLargeGraph 
      ? settings.nodeSize * 15
      : isLargeGraph 
        ? settings.nodeSize * 12
        : settings.nodeSize * 10;
  
  // Calculate charge strength (repulsion between nodes)
  // Use stronger scaling for large graphs to prevent clumping
  const chargeStrength = isExtremeGraph 
    ? -baseForceStrength / Math.pow(nodeCount, 0.4)
    : isVeryLargeGraph
      ? -baseForceStrength / Math.pow(nodeCount, 0.33)
      : -baseForceStrength / Math.sqrt(nodeCount);
  
  // Calculate collision radius
  const collisionRadius = settings.nodeSize * (isExtremeGraph ? 2 : 1.5);
  
  // Lower alphaMin for large graphs to stabilize faster
  const alphaMin = isExtremeGraph ? 0.01 : isVeryLargeGraph ? 0.005 : 0.001;
  
  // Number of iterations for static layout
  const iterations = isExtremeGraph 
    ? 10 
    : isVeryLargeGraph 
      ? 30 
      : isLargeGraph 
        ? 50 
        : 100;
  
  return {
    alphaDecay,
    velocityDecay,
    forceStrength: baseForceStrength,
    linkDistance,
    chargeStrength,
    collisionRadius,
    alphaMin,
    iterations
  };
}

/**
 * Generate a test dataset with a specified number of nodes
 * 
 * @param nodeCount - Number of nodes to generate
 * @returns Test graph data
 */
export function generateTestData(nodeCount: number): GraphData {
  const nodes: Entity[] = [];
  const links: Relationship[] = [];
  
  // Entity types for variety
  const entityTypes: EntityType[] = ['MODEL', 'DATASET', 'ALGORITHM', 'PAPER', 'AUTHOR', 'CODE', 'FRAMEWORK'];
  
  // Relationship types for variety
  const relationshipTypes: string[] = ['USES', 'AUTHORED_BY', 'CITES', 'EVALUATED_ON', 'BUILDS_ON', 'TRAINED_ON'];
  
  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    const entityType = entityTypes[Math.floor(Math.random() * entityTypes.length)];
    nodes.push({
      id: `node-${i}`,
      name: `Test Node ${i} (${entityType})`,
      type: entityType,
      importance: Math.random()
    });
  }
  
  // Generate links (ensure connectedness but not too dense)
  // For large graphs, we'll connect about 3-5 links per node on average
  const linksPerNode = Math.min(5, Math.max(3, Math.floor(10000 / nodeCount)));
  
  // First, make sure all nodes are connected in a chain
  for (let i = 0; i < nodes.length - 1; i++) {
    links.push({
      id: `link-chain-${i}`,
      source: nodes[i].id,
      target: nodes[i + 1].id, 
      type: relationshipTypes[Math.floor(Math.random() * relationshipTypes.length)] as any
    });
  }
  
  // Then add some random connections
  for (let i = 0; i < nodes.length; i++) {
    const numLinks = Math.floor(Math.random() * linksPerNode) + 1;
    
    for (let j = 0; j < numLinks; j++) {
      // Find a target node that's not the same as the source
      let targetIndex;
      do {
        targetIndex = Math.floor(Math.random() * nodes.length);
      } while (targetIndex === i);
      
      // Add link
      links.push({
        id: `link-random-${i}-${j}`,
        source: nodes[i].id,
        target: nodes[targetIndex].id,
        type: relationshipTypes[Math.floor(Math.random() * relationshipTypes.length)] as any
      });
    }
  }
  
  // Create a few hub nodes with many connections (preferential attachment)
  const numHubs = Math.min(5, Math.floor(nodeCount / 200));
  
  for (let h = 0; h < numHubs; h++) {
    const hubIndex = Math.floor(Math.random() * nodes.length);
    const hubConnections = Math.floor(nodeCount * 0.1); // Connect to 10% of nodes
    
    for (let c = 0; c < hubConnections; c++) {
      const targetIndex = Math.floor(Math.random() * nodes.length);
      if (targetIndex !== hubIndex) {
        links.push({
          id: `link-hub-${h}-${c}`,
          source: nodes[hubIndex].id,
          target: nodes[targetIndex].id,
          type: relationshipTypes[Math.floor(Math.random() * relationshipTypes.length)] as any
        });
      }
    }
  }
  
  return { nodes, links };
}

/**
 * Calculate level of detail parameters based on zoom level
 * 
 * @param scale - Current zoom scale (from d3.zoom transform)
 * @param nodeCount - Total number of nodes in the graph
 * @returns Object with visibility thresholds for different elements
 */
export function calculateLevelOfDetail(scale: number, nodeCount: number): {
  showLabels: boolean;
  showRelationshipLabels: boolean;
  nodeBorderWidth: number;
  linkOpacity: number;
  labelFontSize: number;
  nodeOpacity: number;
  nodeRadiusMultiplier: number;
} {
  // Base thresholds - adjusted dynamically based on graph size
  const labelThreshold = nodeCount > 1000 ? 1.5 : nodeCount > 500 ? 1.2 : 0.8;
  const relationshipLabelThreshold = nodeCount > 1000 ? 3.0 : nodeCount > 500 ? 2.5 : 2.0;
  
  // Scale border width and opacity based on zoom level
  const baseBorderWidth = 1;
  const nodeBorderWidth = Math.min(3, baseBorderWidth / Math.sqrt(scale));
  
  // Adjust opacity - links become more transparent when zoomed out
  const linkOpacity = scale < 0.5 ? 0.3 : scale < 1 ? 0.5 : 0.7;
  
  // Adjust node opacity for better performance with large graphs
  const nodeOpacity = nodeCount > 2000 
    ? (scale < 0.5 ? 0.7 : 0.9) 
    : nodeCount > 1000 
      ? (scale < 0.7 ? 0.8 : 1.0) 
      : 1.0;
  
  // Adjust font size based on zoom level
  const baseFontSize = 10;
  const labelFontSize = scale > 2 
    ? baseFontSize 
    : baseFontSize * Math.max(0.8, scale);
  
  // Adjust node radius based on zoom (for visual consistency)
  const nodeRadiusMultiplier = 1 / Math.sqrt(Math.max(0.1, scale));
  
  return {
    showLabels: scale > labelThreshold,
    showRelationshipLabels: scale > relationshipLabelThreshold,
    nodeBorderWidth,
    linkOpacity,
    labelFontSize,
    nodeOpacity,
    nodeRadiusMultiplier
  };
}

/**
 * Creates a pre-computed node index map for keyboard navigation
 * 
 * @param nodes - Graph nodes to create index map for
 * @returns Map of node IDs to their index positions
 */
export function createNodeIndexMap(nodes: Entity[]): Map<string, number> {
  const indexMap = new Map<string, number>();
  
  nodes.forEach((node, index) => {
    indexMap.set(node.id, index);
  });
  
  return indexMap;
}

/**
 * Node focus information for keyboard navigation
 */
export interface NodeFocusInfo {
  id: string;
  index: number;
}

/**
 * Get the next or previous navigable node in the graph
 * 
 * @param currentNodeId - Currently focused node ID
 * @param nodes - All graph nodes
 * @param direction - Navigation direction (1 for next, -1 for previous)
 * @returns NodeFocusInfo with ID and index of the next node to focus
 */
export function getNavigableNode(
  currentNodeId: string | null,
  nodes: Entity[],
  direction: 1 | -1
): NodeFocusInfo | null {
  if (!nodes.length) return null;
  
  // If no current node, start with the first or last node
  if (!currentNodeId) {
    const targetIndex = direction === 1 ? 0 : nodes.length - 1;
    return {
      id: nodes[targetIndex].id,
      index: targetIndex
    };
  }
  
  // Find current node index
  const currentIndex = nodes.findIndex(node => node.id === currentNodeId);
  
  // If not found, start at beginning
  if (currentIndex === -1) {
    return {
      id: nodes[0].id,
      index: 0
    };
  }
  
  // Calculate next index with wraparound
  const nextIndex = (currentIndex + direction + nodes.length) % nodes.length;
  
  return {
    id: nodes[nextIndex].id,
    index: nextIndex
  };
}

/**
 * Find related nodes to show when a node is focused
 * 
 * @param nodeId - The ID of the node to find related nodes for
 * @param nodes - All nodes in the graph
 * @param links - All links in the graph
 * @param maxCount - Maximum number of related nodes to return
 * @returns Array of node IDs that are related to the focused node
 */
export function findRelatedNodes(
  nodeId: string,
  nodes: Entity[],
  links: Relationship[],
  maxCount: number = 5
): string[] {
  // Find all directly connected nodes
  const connectedNodeIds = new Set<string>();
  
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    if (sourceId === nodeId) {
      connectedNodeIds.add(targetId);
    } else if (targetId === nodeId) {
      connectedNodeIds.add(sourceId);
    }
  });
  
  // Convert to array and limit to maxCount
  return Array.from(connectedNodeIds).slice(0, maxCount);
}

/**
 * Process and optimize node attributes for large graphs
 * 
 * @param nodes - Graph nodes
 * @param links - Graph links
 * @param selectedNodeId - Currently selected node ID
 * @returns Object with optimized color and node importance maps
 */
export function optimizeNodeAttributes(
  nodes: Entity[], 
  links: Relationship[],
  selectedNodeId: string | null
): {
  colorMap: Map<string, string>;
  sizeMap: Map<string, number>;
  importantNodeIds: Set<string>;
} {
  // Create maps for faster lookups
  const colorMap = new Map<string, string>();
  const sizeMap = new Map<string, number>();
  const importantNodeIds = new Set<string>();
  
  // Calculate node degrees for sizing
  const degreeMap = new Map<string, number>();
  
  // Color mapping for entity types
  const entityColors: Record<string, string> = {
    MODEL: '#4285F4',
    DATASET: '#34A853',
    ALGORITHM: '#EA4335',
    PAPER: '#FBBC05',
    AUTHOR: '#9C27B0',
    CODE: '#00ACC1',
    FRAMEWORK: '#FF9800',
    METRIC: '#795548',
    METHOD: '#607D8B',
    TASK: '#9E9E9E'
  };
  
  // Calculate node degrees
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    degreeMap.set(sourceId, (degreeMap.get(sourceId) || 0) + 1);
    degreeMap.set(targetId, (degreeMap.get(targetId) || 0) + 1);
  });
  
  // Find max degree for sizing
  const maxDegree = Math.max(1, ...Array.from(degreeMap.values()));
  
  // Process each node
  nodes.forEach(node => {
    // Set color based on entity type
    const color = node.color || entityColors[node.type] || '#757575';
    colorMap.set(node.id, color);
    
    // Calculate node size based on degree
    const degree = degreeMap.get(node.id) || 1;
    
    // Use logarithmic scale for size to avoid extremely large nodes
    const sizeFactor = Math.log(degree + 1) / Math.log(maxDegree + 1);
    const size = 5 + sizeFactor * 10;
    sizeMap.set(node.id, size);
    
    // Mark important nodes (selected node, high-degree nodes, or nodes with importance)
    if (
      node.id === selectedNodeId ||
      node.importance && node.importance > 0.7 ||
      degree > maxDegree * 0.7
    ) {
      importantNodeIds.add(node.id);
    }
  });
  
  return {
    colorMap,
    sizeMap,
    importantNodeIds
  };
}