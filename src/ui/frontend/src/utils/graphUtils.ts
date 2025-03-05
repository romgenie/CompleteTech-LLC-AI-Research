import { Entity, Relationship } from '../types';

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
  [key: string]: any;
}

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
} {
  // Calculate optimal parameters based on graph size
  const nodeCount = nodes.length;
  const isLargeGraph = nodeCount > 500;
  const isVeryLargeGraph = nodeCount > 1000;
  
  // Adjust decay and strength based on graph size
  const alphaDecay = isVeryLargeGraph ? 0.035 : (isLargeGraph ? 0.028 : 0.0228);
  const velocityDecay = isVeryLargeGraph ? 0.5 : (isLargeGraph ? 0.4 : 0.4);
  const forceStrength = settings.forceStrength || 500;
  const baseForceStrength = isVeryLargeGraph ? forceStrength * 1.5 : forceStrength;
  
  // Calculate link distance
  const linkDistance = isVeryLargeGraph 
    ? settings.nodeSize * 15
    : isLargeGraph 
      ? settings.nodeSize * 12
      : settings.nodeSize * 10;
  
  // Calculate charge strength (repulsion between nodes)
  const chargeStrength = -baseForceStrength / Math.sqrt(nodeCount);
  
  // Calculate collision radius
  const collisionRadius = settings.nodeSize * 1.5;
  
  return {
    alphaDecay,
    velocityDecay,
    forceStrength: baseForceStrength,
    linkDistance,
    chargeStrength,
    collisionRadius
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
  const entityTypes: string[] = ['MODEL', 'DATASET', 'ALGORITHM', 'PAPER', 'AUTHOR', 'CODE', 'FRAMEWORK'];
  
  // Relationship types for variety
  const relationshipTypes: string[] = ['USES', 'AUTHORED_BY', 'CITES', 'EVALUATED_ON', 'BUILDS_ON', 'TRAINED_ON'];
  
  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    const entityType = entityTypes[Math.floor(Math.random() * entityTypes.length)];
    nodes.push({
      id: `node-${i}`,
      name: `Test Node ${i} (${entityType})`,
      type: entityType as any,
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