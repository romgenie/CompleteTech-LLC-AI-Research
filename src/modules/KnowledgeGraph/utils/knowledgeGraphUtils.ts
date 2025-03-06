/**
 * Knowledge Graph utility functions
 */
import { Entity, EntityType, Relationship, RelationshipType, GraphStatistics } from '../types/knowledgeGraph.types';

/**
 * Get entity color based on type
 */
export const getEntityColor = (type: EntityType): string => {
  const colors: Record<EntityType, string> = {
    MODEL: '#4285F4',      // Google Blue
    ALGORITHM: '#EA4335',  // Google Red
    DATASET: '#FBBC05',    // Google Yellow
    PAPER: '#34A853',      // Google Green
    AUTHOR: '#9C27B0',     // Purple
    METHOD: '#FF9800',     // Orange
    FINDING: '#00BCD4',    // Cyan
    METRIC: '#795548',     // Brown
    CODE: '#607D8B',       // Blue Grey
    CONCEPT: '#E91E63',    // Pink
    FRAMEWORK: '#3F51B5',  // Indigo
  };
  
  return colors[type] || '#757575'; // Default to grey
};

/**
 * Get relationship color based on type
 */
export const getRelationshipColor = (type: RelationshipType): string => {
  const colors: Record<RelationshipType, string> = {
    CREATED_BY: '#4285F4',    // Google Blue
    USES: '#EA4335',          // Google Red
    IMPLEMENTS: '#FBBC05',    // Google Yellow
    TRAINED_ON: '#34A853',    // Google Green
    EVALUATED_ON: '#9C27B0',  // Purple
    CITES: '#FF9800',         // Orange
    OUTPERFORMS: '#00BCD4',   // Cyan
    PART_OF: '#795548',       // Brown
    RELATED_TO: '#607D8B',    // Blue Grey
    EXTENDS: '#3F51B5',       // Indigo
  };
  
  return colors[type] || '#757575'; // Default to grey
};

/**
 * Format entity for display
 */
export const formatEntity = (entity: Entity): string => {
  const propertyString = Object.entries(entity.properties || {})
    .filter(([_, value]) => value !== null && value !== undefined)
    .map(([key, value]) => `${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`)
    .join(', ');
  
  return `${entity.name} (${entity.type})${propertyString ? ` - ${propertyString}` : ''}`;
};

/**
 * Format relationship for display
 */
export const formatRelationship = (relationship: Relationship, sourceEntity?: Entity, targetEntity?: Entity): string => {
  const sourceName = sourceEntity?.name || relationship.sourceId;
  const targetName = targetEntity?.name || relationship.targetId;
  
  return `${sourceName} ${relationship.type.replace(/_/g, ' ')} ${targetName}`;
};

/**
 * Calculate graph density
 * Density = actual edges / potential edges
 * For directed graphs: potential edges = n(n-1)
 */
export const calculateGraphDensity = (nodeCount: number, edgeCount: number): number => {
  if (nodeCount <= 1) return 0;
  const potentialEdges = nodeCount * (nodeCount - 1);
  return edgeCount / potentialEdges;
};

/**
 * Generate summary of graph statistics
 */
export const formatGraphStatistics = (stats: GraphStatistics): string[] => {
  const summary = [
    `Entities: ${stats.entityCount}`,
    `Relationships: ${stats.relationshipCount}`,
    `Density: ${(stats.density * 100).toFixed(2)}%`,
    `Average Degree: ${stats.averageDegree.toFixed(2)}`,
    `Max Degree: ${stats.maxDegree}`,
  ];
  
  if (stats.diameter !== undefined) {
    summary.push(`Diameter: ${stats.diameter}`);
  }
  
  if (stats.clusteringCoefficient !== undefined) {
    summary.push(`Clustering: ${stats.clusteringCoefficient.toFixed(2)}`);
  }
  
  return summary;
};

/**
 * Transform entity and relationship data for D3 visualization
 */
export const transformForD3 = (entities: Entity[], relationships: Relationship[]) => {
  const nodes = entities.map(entity => ({
    id: entity.id,
    name: entity.name,
    type: entity.type,
    color: getEntityColor(entity.type),
    properties: entity.properties,
    confidence: entity.confidence,
  }));
  
  const links = relationships.map(rel => ({
    id: rel.id,
    source: rel.sourceId,
    target: rel.targetId,
    type: rel.type,
    color: getRelationshipColor(rel.type),
    properties: rel.properties,
    confidence: rel.confidence,
  }));
  
  return { nodes, links };
};