/**
 * Utilities for measuring and evaluating performance of the knowledge graph visualization
 */

import { Entity, Relationship } from '../types';
import { generateTestData } from './graphUtils';

export interface BenchmarkResults {
  renderTime: number;
  frameRate: number;
  nodeCount: number;
  linkCount: number;
  memoryUsage?: number;
  interactionLatency?: number;
}

export interface BenchmarkSuite {
  small: BenchmarkResults | null;
  medium: BenchmarkResults | null;
  large: BenchmarkResults | null;
  veryLarge: BenchmarkResults | null;
}

/**
 * Generate benchmark reports for different dataset sizes
 * 
 * @param results Results from benchmark runs
 * @returns Formatted benchmark report
 */
export function generateBenchmarkReport(suite: BenchmarkSuite): string {
  let report = `# Knowledge Graph Performance Benchmark\n\n`;
  
  report += `## Summary\n\n`;
  report += `| Dataset Size | Node Count | Link Count | Render Time (ms) | Frame Rate (fps) |\n`;
  report += `|--------------|------------|-----------|-----------------|------------------|\n`;
  
  if (suite.small) {
    report += `| Small | ${suite.small.nodeCount} | ${suite.small.linkCount} | ${suite.small.renderTime.toFixed(2)} | ${suite.small.frameRate.toFixed(2)} |\n`;
  }
  
  if (suite.medium) {
    report += `| Medium | ${suite.medium.nodeCount} | ${suite.medium.linkCount} | ${suite.medium.renderTime.toFixed(2)} | ${suite.medium.frameRate.toFixed(2)} |\n`;
  }
  
  if (suite.large) {
    report += `| Large | ${suite.large.nodeCount} | ${suite.large.linkCount} | ${suite.large.renderTime.toFixed(2)} | ${suite.large.frameRate.toFixed(2)} |\n`;
  }
  
  if (suite.veryLarge) {
    report += `| Very Large | ${suite.veryLarge.nodeCount} | ${suite.veryLarge.linkCount} | ${suite.veryLarge.renderTime.toFixed(2)} | ${suite.veryLarge.frameRate.toFixed(2)} |\n`;
  }
  
  report += `\n## Analysis\n\n`;
  
  // Calculate rendering efficiency (nodes per ms)
  const efficiencies: Record<string, number> = {};
  
  if (suite.small) {
    efficiencies.small = suite.small.nodeCount / suite.small.renderTime;
  }
  
  if (suite.medium) {
    efficiencies.medium = suite.medium.nodeCount / suite.medium.renderTime;
  }
  
  if (suite.large) {
    efficiencies.large = suite.large.nodeCount / suite.large.renderTime;
  }
  
  if (suite.veryLarge) {
    efficiencies.veryLarge = suite.veryLarge.nodeCount / suite.veryLarge.renderTime;
  }
  
  // Compare small vs large efficiency
  if (efficiencies.small && efficiencies.large) {
    const ratio = efficiencies.large / efficiencies.small;
    report += `Efficiency ratio (large/small): ${ratio.toFixed(2)}x\n\n`;
    
    if (ratio > 0.8) {
      report += `✅ The visualization scales well with larger datasets\n`;
    } else if (ratio > 0.5) {
      report += `⚠️ The visualization scales adequately with larger datasets\n`;
    } else {
      report += `❌ The visualization shows significant performance degradation with larger datasets\n`;
    }
  }
  
  // Frame rate analysis
  let frameRateAnalysis = '### Frame Rate Analysis\n\n';
  let allFrameRatesGood = true;
  
  if (suite.small && suite.small.frameRate < 30) {
    frameRateAnalysis += `❌ Small dataset frame rate (${suite.small.frameRate.toFixed(2)} fps) is below 30 fps\n`;
    allFrameRatesGood = false;
  }
  
  if (suite.medium && suite.medium.frameRate < 30) {
    frameRateAnalysis += `❌ Medium dataset frame rate (${suite.medium.frameRate.toFixed(2)} fps) is below 30 fps\n`;
    allFrameRatesGood = false;
  }
  
  if (suite.large && suite.large.frameRate < 20) {
    frameRateAnalysis += `❌ Large dataset frame rate (${suite.large.frameRate.toFixed(2)} fps) is below 20 fps\n`;
    allFrameRatesGood = false;
  }
  
  if (suite.veryLarge && suite.veryLarge.frameRate < 15) {
    frameRateAnalysis += `❌ Very large dataset frame rate (${suite.veryLarge.frameRate.toFixed(2)} fps) is below 15 fps\n`;
    allFrameRatesGood = false;
  }
  
  if (allFrameRatesGood) {
    frameRateAnalysis += `✅ All frame rates are within acceptable ranges for their dataset sizes\n`;
  }
  
  report += frameRateAnalysis;
  
  // Render time analysis
  let renderTimeAnalysis = '\n### Render Time Analysis\n\n';
  
  const acceptableRenderTime = (nodeCount: number) => {
    // Heuristic: render time should be less than nodeCount/10 ms
    // (e.g., 1000 nodes should render in less than 100ms)
    return nodeCount / 10;
  };
  
  if (suite.small && suite.small.renderTime > acceptableRenderTime(suite.small.nodeCount)) {
    renderTimeAnalysis += `❌ Small dataset render time (${suite.small.renderTime.toFixed(2)} ms) is higher than expected\n`;
  }
  
  if (suite.medium && suite.medium.renderTime > acceptableRenderTime(suite.medium.nodeCount)) {
    renderTimeAnalysis += `❌ Medium dataset render time (${suite.medium.renderTime.toFixed(2)} ms) is higher than expected\n`;
  }
  
  if (suite.large && suite.large.renderTime > acceptableRenderTime(suite.large.nodeCount)) {
    renderTimeAnalysis += `❌ Large dataset render time (${suite.large.renderTime.toFixed(2)} ms) is higher than expected\n`;
  }
  
  if (suite.veryLarge && suite.veryLarge.renderTime > acceptableRenderTime(suite.veryLarge.nodeCount)) {
    renderTimeAnalysis += `❌ Very large dataset render time (${suite.veryLarge.renderTime.toFixed(2)} ms) is higher than expected\n`;
  }
  
  report += renderTimeAnalysis;
  
  return report;
}

/**
 * Get pre-defined benchmark dataset sizes
 * 
 * @returns Object with test datasets of different sizes
 */
export function getBenchmarkDatasets(): {
  small: { nodes: Entity[], links: Relationship[] };
  medium: { nodes: Entity[], links: Relationship[] };
  large: { nodes: Entity[], links: Relationship[] };
  veryLarge: { nodes: Entity[], links: Relationship[] };
} {
  return {
    small: generateTestData(100),
    medium: generateTestData(500),
    large: generateTestData(1000),
    veryLarge: generateTestData(2000)
  };
}

/**
 * Run a simple benchmark to get current memory usage
 * 
 * @returns Current memory usage statistics if available, or null
 */
export function getMemoryUsage(): { used: number, total: number } | null {
  if (typeof window !== 'undefined' && 
      // @ts-ignore
      window.performance && 
      // @ts-ignore
      window.performance.memory) {
    // @ts-ignore
    const memoryInfo = window.performance.memory;
    return {
      // Values in MB
      used: Math.round(memoryInfo.usedJSHeapSize / (1024 * 1024)),
      total: Math.round(memoryInfo.totalJSHeapSize / (1024 * 1024))
    };
  }
  return null;
}

/**
 * Formats a benchmark result for console output
 */
export function formatBenchmarkResult(result: BenchmarkResults): string {
  return `
Performance Benchmark:
---------------------
Graph Size: ${result.nodeCount} nodes, ${result.linkCount} links
Render Time: ${result.renderTime.toFixed(2)} ms
Frame Rate: ${result.frameRate.toFixed(2)} fps
${result.memoryUsage ? `Memory Usage: ${result.memoryUsage} MB` : ''}
${result.interactionLatency ? `Interaction Latency: ${result.interactionLatency.toFixed(2)} ms` : ''}
`;
}