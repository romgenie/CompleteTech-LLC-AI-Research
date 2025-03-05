/**
 * Utilities for graph visualization and data handling
 */

/**
 * Filters nodes in large graphs based on importance metrics
 * - Always shows selected node and direct connections
 * - Filters distant nodes based on connectivity patterns
 * - Implements logarithmic scaling for better visibility
 * 
 * @param {Array} nodes - Complete nodes array
 * @param {Array} links - Complete links array
 * @param {string|null} selectedEntityId - Currently selected entity ID
 * @param {Object} settings - Visualization settings
 * @returns {Array} Filtered nodes for display
 */
export function getFilteredNodes(nodes, links, selectedEntityId, settings) {
  // Default thresholds if not provided
  const filterThreshold = settings.filterThreshold || 100;
  const importanceThreshold = settings.importanceThreshold || 0.5;

  // For smaller graphs, show everything
  if (nodes.length < filterThreshold) {
    return nodes;
  }
  
  // Create node ID lookup for faster filtering
  const directConnectionIds = new Set();
  
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
  const connectionCounts = {};
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
 * @param {Array} nodes - Graph nodes
 * @param {Array} links - Graph links
 * @param {number} baseSize - Base node size
 * @returns {Function} Function that returns size for each node
 */
export function createNodeSizeScale(nodes, links, baseSize) {
  // Calculate connection counts
  const connectionCounts = {};
  
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
  });
  
  // Get maximum connection count (or 1 if no connections)
  const maxConnections = Math.max(1, ...Object.values(connectionCounts));
  
  // Return sizing function
  return (node) => {
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
 * @param {string} nodeId - The ID of the node
 * @param {Array} links - All graph links
 * @returns {number} The number of connections
 */
export function countNodeConnections(nodeId, links) {
  return links.filter(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    return sourceId === nodeId || targetId === nodeId;
  }).length;
}

/**
 * Creates optimized force simulation parameters for large graphs
 * 
 * @param {Array} nodes - Graph nodes
 * @param {Object} settings - Visualization settings
 * @returns {Object} Optimized force simulation parameters
 */
export function createOptimizedForceParameters(nodes, settings) {
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
 * Calculate level of detail settings based on zoom scale and node count
 * 
 * @param {number} scale - Current zoom scale
 * @param {number} nodeCount - Number of visible nodes
 * @returns {Object} Level of detail settings
 */
export function calculateLevelOfDetail(scale, nodeCount) {
  // Default settings
  const settings = {
    showLabels: false,
    showRelationshipLabels: false,
    nodeOpacity: 1,
    linkOpacity: 0.6,
    labelFontSize: 12,
    linkLabelFontSize: 10,
    nodeDetailLevel: 'low'
  };
  
  // Very zoomed out (overview)
  if (scale < 0.5) {
    settings.showLabels = false;
    settings.showRelationshipLabels = false;
    settings.nodeOpacity = 0.7;
    settings.linkOpacity = 0.3;
    settings.nodeDetailLevel = 'low';
  } 
  // Medium zoom
  else if (scale < 1.5) {
    settings.showLabels = nodeCount < 200;
    settings.showRelationshipLabels = false;
    settings.nodeOpacity = 0.9;
    settings.linkOpacity = 0.6;
    settings.labelFontSize = 11;
    settings.nodeDetailLevel = 'medium';
  } 
  // Zoomed in
  else if (scale < 3) {
    settings.showLabels = nodeCount < 500;
    settings.showRelationshipLabels = nodeCount < 100;
    settings.nodeOpacity = 1;
    settings.linkOpacity = 0.8;
    settings.labelFontSize = 12;
    settings.linkLabelFontSize = 10;
    settings.nodeDetailLevel = 'high';
  } 
  // Very zoomed in (detail view)
  else {
    settings.showLabels = true;
    settings.showRelationshipLabels = nodeCount < 200;
    settings.nodeOpacity = 1;
    settings.linkOpacity = 1;
    settings.labelFontSize = 14;
    settings.linkLabelFontSize = 12;
    settings.nodeDetailLevel = 'very-high';
  }
  
  return settings;
}

/**
 * Find the closest navigable node in a given direction
 * 
 * @param {string} currentNodeId - Current node ID
 * @param {string} direction - Direction to navigate (up, down, left, right)
 * @param {Array} nodes - All graph nodes
 * @param {Array} links - All graph links
 * @returns {string|null} ID of the navigable node or null if none found
 */
export function getNavigableNode(currentNodeId, direction, nodes, links) {
  // Get current node position
  const currentNode = nodes.find(n => n.id === currentNodeId);
  if (!currentNode || !currentNode.x || !currentNode.y) return null;
  
  // Get connected nodes
  const connectedNodeIds = links
    .filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      return sourceId === currentNodeId || targetId === currentNodeId;
    })
    .map(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      return sourceId === currentNodeId ? targetId : sourceId;
    });
  
  // Get connected node positions
  const connectedNodes = nodes.filter(n => connectedNodeIds.includes(n.id));
  if (!connectedNodes.length) return null;
  
  // Find the node in the desired direction
  let bestNode = null;
  let bestScore = Infinity;
  
  for (const node of connectedNodes) {
    if (!node.x || !node.y) continue;
    
    const dx = node.x - currentNode.x;
    const dy = node.y - currentNode.y;
    let score;
    
    switch (direction) {
      case 'up':
        // Prefer nodes above (negative y is up)
        score = dy > 0 ? Infinity : Math.abs(dx) + Math.abs(dy);
        break;
      case 'down':
        // Prefer nodes below (positive y is down)
        score = dy < 0 ? Infinity : Math.abs(dx) + Math.abs(dy);
        break;
      case 'left':
        // Prefer nodes to the left (negative x is left)
        score = dx > 0 ? Infinity : Math.abs(dx) + Math.abs(dy);
        break;
      case 'right':
        // Prefer nodes to the right (positive x is right)
        score = dx < 0 ? Infinity : Math.abs(dx) + Math.abs(dy);
        break;
      default:
        score = Infinity;
    }
    
    if (score < bestScore) {
      bestScore = score;
      bestNode = node;
    }
  }
  
  return bestNode ? bestNode.id : null;
}

/**
 * Generate a test dataset with a specified number of nodes
 * 
 * @param {number} nodeCount - Number of nodes to generate
 * @returns {Object} Test graph data
 */
export function generateTestData(nodeCount) {
  const nodes = [];
  const links = [];
  
  // Entity types for variety
  const entityTypes = ['MODEL', 'DATASET', 'ALGORITHM', 'PAPER', 'AUTHOR', 'CODE', 'FRAMEWORK'];
  
  // Relationship types for variety
  const relationshipTypes = ['USES', 'AUTHORED_BY', 'CITES', 'EVALUATED_ON', 'BUILDS_ON', 'TRAINED_ON'];
  
  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    const type = entityTypes[Math.floor(Math.random() * entityTypes.length)];
    nodes.push({
      id: `node-${i}`,
      name: `${type} ${i}`,
      type: type,
      importance: Math.random(),
      properties: {
        year: 2010 + Math.floor(Math.random() * 15),
        citations: Math.floor(Math.random() * 1000)
      }
    });
  }
  
  // Create links (approximately 2x nodes)
  const linkCount = Math.min(nodeCount * 2, nodeCount * (nodeCount - 1) / 2);
  
  for (let i = 0; i < linkCount; i++) {
    const source = Math.floor(Math.random() * nodeCount);
    let target;
    do {
      target = Math.floor(Math.random() * nodeCount);
    } while (target === source);
    
    links.push({
      id: `link-${i}`,
      source: `node-${source}`,
      target: `node-${target}`,
      type: relationshipTypes[Math.floor(Math.random() * relationshipTypes.length)],
      properties: {
        weight: Math.random(),
        year: 2010 + Math.floor(Math.random() * 15)
      }
    });
  }
  
  return { nodes, links };
}