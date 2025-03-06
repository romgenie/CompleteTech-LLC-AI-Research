/**
 * Knowledge Graph Module exports
 */

// Main module component
export { KnowledgeGraphModule } from './KnowledgeGraphModule';

// Component exports
export { EntityList } from './components/EntityList';
export { EntityCard } from './components/EntityCard';
export { EntityDetail } from './components/EntityDetail';
export { EntityForm } from './components/EntityForm';
export { GraphVisualization } from './components/GraphVisualization';
export { PathFinder } from './components/PathFinder';
export { GraphStats } from './components/GraphStats';

// Hook exports
export { useKnowledgeGraph } from './hooks/useKnowledgeGraph';
export { useEntity } from './hooks/useEntity';
// export { useGraphSearch } from './hooks/useGraphSearch';
// export { useGraphStats } from './hooks/useGraphStats';

// Type exports
export type { 
  Entity,
  EntityType,
  EntityFilter,
  Relationship,
  RelationshipType,
  RelationshipFilter,
  GraphData,
  GraphVisualizationOptions,
  GraphStatistics,
  Path,
  PathQuery
} from './types/knowledgeGraph.types';

// Utility exports
export {
  getEntityColor,
  getRelationshipColor,
  formatEntity,
  formatRelationship,
  calculateGraphDensity,
  formatGraphStatistics,
  transformForD3
} from './utils/knowledgeGraphUtils';