/**
 * Utilities for performance benchmarking the knowledge graph visualization
 */
import knowledgeGraphService from '../services/knowledgeGraphService';
import { generateTestData } from './graphUtils';

/**
 * Measures the time taken for a function to execute
 * 
 * @param {Function} fn - Function to measure
 * @param {Array} args - Arguments to pass to the function
 * @returns {Object} Object containing the result and execution time
 */
export function measureExecutionTime(fn, args = []) {
  const start = performance.now();
  const result = fn(...args);
  const end = performance.now();
  return {
    result,
    time: end - start
  };
}

/**
 * Measures the time taken for an async function to execute
 * 
 * @param {Function} fn - Async function to measure
 * @param {Array} args - Arguments to pass to the function
 * @returns {Promise<Object>} Promise resolving to object containing the result and execution time
 */
export async function measureAsyncExecutionTime(fn, args = []) {
  const start = performance.now();
  const result = await fn(...args);
  const end = performance.now();
  return {
    result,
    time: end - start
  };
}

/**
 * Runs a performance benchmark for the full graph visualization cycle
 * 
 * @param {number} nodeCount - Number of nodes to use for the benchmark
 * @returns {Object} Object containing benchmark results
 */
export async function runGraphPerformanceBenchmark(nodeCount = 1000) {
  console.log(`Running performance benchmark with ${nodeCount} nodes`);
  
  // Generate test data
  const generateDataResult = measureExecutionTime(generateTestData, [nodeCount]);
  const testData = generateDataResult.result;
  
  // Metrics to return
  const metrics = {
    nodeCount,
    generateDataTime: generateDataResult.time,
    processingTime: 0,
    renderTime: 0,
    totalTime: 0,
    fps: 0
  };
  
  return metrics;
}

/**
 * Builds a real-world knowledge graph from multiple entity starting points
 * 
 * @param {Array<string>} entityIds - Array of entity IDs to start from
 * @param {number} maxDepth - Maximum relationship depth to explore
 * @returns {Promise<Object>} Promise resolving to combined graph data
 */
export async function buildRealWorldGraph(entityIds, maxDepth = 2) {
  // Track unique nodes and links to avoid duplicates
  const uniqueNodes = new Map();
  const uniqueLinks = new Map();
  
  // Process each starting entity
  for (const entityId of entityIds) {
    try {
      // Get related entities data from the service
      const data = await knowledgeGraphService.getRelatedEntities(entityId);
      
      // Add the central entity
      if (data.entities && data.entities.length > 0) {
        const centralEntity = await knowledgeGraphService.getEntityDetails(entityId);
        if (centralEntity) {
          uniqueNodes.set(centralEntity.id, centralEntity);
        }
      }
      
      // Add all entities
      if (data.entities) {
        data.entities.forEach((entity) => {
          uniqueNodes.set(entity.id, entity);
        });
      }
      
      // Add all relationships
      if (data.relationships) {
        data.relationships.forEach((rel) => {
          uniqueLinks.set(rel.id, rel);
        });
      }
    } catch (err) {
      console.error(`Error loading real-world data for entity ${entityId}:`, err);
      // Continue with other entities
    }
  }
  
  return {
    nodes: Array.from(uniqueNodes.values()),
    links: Array.from(uniqueLinks.values())
  };
}

/**
 * Runs a frame rate test by measuring simulation ticks
 * 
 * @param {Object} simulation - D3 force simulation
 * @param {number} durationMs - Duration to run test in milliseconds
 * @returns {Promise<Object>} Promise resolving to frame rate metrics
 */
export function measureFrameRate(simulation, durationMs = 2000) {
  return new Promise((resolve) => {
    let ticks = 0;
    const startTime = performance.now();
    
    // Replace tick handler with counting function
    const originalTick = simulation.on('tick');
    
    simulation.on('tick', () => {
      ticks++;
      if (originalTick) originalTick();
    });
    
    // Stop measuring after duration
    setTimeout(() => {
      const endTime = performance.now();
      const actualDuration = endTime - startTime;
      const fps = (ticks / actualDuration) * 1000;
      
      // Restore original tick handler
      simulation.on('tick', originalTick);
      
      resolve({
        ticks,
        duration: actualDuration,
        fps
      });
    }, durationMs);
  });
}

/**
 * Benchmarks entity search performance
 * 
 * @param {number} searchCount - Number of searches to perform
 * @returns {Promise<Object>} Promise resolving to search performance metrics
 */
export async function benchmarkSearch(searchCount = 10) {
  const searchTerms = [
    'model', 'algorithm', 'transformer', 'bert', 'gpt',
    'dataset', 'neural', 'machine', 'learning', 'paper'
  ];
  
  const results = [];
  
  // Perform multiple searches
  for (let i = 0; i < searchCount; i++) {
    const term = searchTerms[i % searchTerms.length];
    
    try {
      const { time } = await measureAsyncExecutionTime(
        knowledgeGraphService.searchEntities, 
        [term]
      );
      
      results.push({ term, time });
    } catch (err) {
      console.error(`Error benchmarking search for "${term}":`, err);
    }
  }
  
  // Calculate metrics
  const times = results.map(r => r.time);
  const metrics = {
    count: results.length,
    min: Math.min(...times),
    max: Math.max(...times),
    avg: times.reduce((sum, t) => sum + t, 0) / times.length,
    p90: calculatePercentile(times, 90),
    details: results
  };
  
  return metrics;
}

/**
 * Calculate percentile from an array of values
 * 
 * @param {Array<number>} values - Array of numeric values
 * @param {number} percentile - Percentile to calculate (0-100)
 * @returns {number} The specified percentile value
 */
function calculatePercentile(values, percentile) {
  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.ceil((percentile / 100) * sorted.length) - 1;
  return sorted[index];
}