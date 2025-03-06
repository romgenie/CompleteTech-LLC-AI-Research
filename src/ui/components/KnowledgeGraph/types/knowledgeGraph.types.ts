/**
 * Knowledge Graph module type definitions
 */
import { BaseEntity, BaseFilter } from '../../_templates/BaseModule/types/base.types';

// Entity Types
export type EntityType = 
  | 'MODEL' 
  | 'ALGORITHM' 
  | 'DATASET' 
  | 'PAPER' 
  | 'AUTHOR' 
  | 'METHOD'
  | 'FINDING'
  | 'METRIC'
  | 'CODE'
  | 'CONCEPT'
  | 'FRAMEWORK';

// Relationship Types
export type RelationshipType =
  | 'CREATED_BY'
  | 'USES'
  | 'IMPLEMENTS'
  | 'TRAINED_ON'
  | 'EVALUATED_ON'
  | 'CITES'
  | 'OUTPERFORMS'
  | 'PART_OF'
  | 'RELATED_TO'
  | 'EXTENDS';

// Entity model
export interface Entity extends BaseEntity {
  name: string;
  type: EntityType;
  description?: string;
  properties: Record<string, any>;
  confidence?: number;
  sourceIds?: string[];
}

// Relationship model
export interface Relationship {
  id: string;
  type: RelationshipType;
  sourceId: string;
  targetId: string;
  properties: Record<string, any>;
  confidence?: number;
  createdAt: string;
  updatedAt: string;
}

// Graph data model
export interface GraphData {
  entities: Entity[];
  relationships: Relationship[];
}

// Entity filter
export interface EntityFilter extends BaseFilter {
  type?: EntityType;
  name?: string;
  description?: string;
  property?: string;
  propertyValue?: string;
  confidence?: number;
  minConfidence?: number;
  sourceId?: string;
}

// Relationship filter
export interface RelationshipFilter extends BaseFilter {
  type?: RelationshipType;
  sourceId?: string;
  targetId?: string;
  property?: string;
  propertyValue?: string;
  confidence?: number;
  minConfidence?: number;
}

// Graph visualization options
export interface GraphVisualizationOptions {
  layout?: 'force' | 'tree' | 'radial' | 'circle';
  showLabels?: boolean;
  nodeSize?: 'fixed' | 'degree' | 'centrality';
  colorBy?: 'type' | 'property' | 'cluster';
  edgeThickness?: 'fixed' | 'weight';
  highlightNeighbors?: boolean;
  showProperties?: boolean;
  enablePhysics?: boolean;
  minNodeSize?: number;
  maxNodeSize?: number;
}

// Path query options
export interface PathQuery {
  sourceId: string;
  targetId: string;
  maxDepth?: number;
  relationshipTypes?: RelationshipType[];
  excludedRelationshipTypes?: RelationshipType[];
  bidirectional?: boolean;
  algorithm?: 'shortestPath' | 'allPaths' | 'weightedPath';
}

// Path result
export interface Path {
  entities: Entity[];
  relationships: Relationship[];
  length: number;
  score?: number;
}

// Graph statistics
export interface GraphStatistics {
  entityCount: number;
  relationshipCount: number;
  entityTypeCounts: Record<EntityType, number>;
  relationshipTypeCounts: Record<RelationshipType, number>;
  density: number;
  averageDegree: number;
  maxDegree: number;
  diameter?: number;
  clusteringCoefficient?: number;
}