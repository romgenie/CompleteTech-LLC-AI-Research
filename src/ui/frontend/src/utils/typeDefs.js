/**
 * Type definitions to be used throughout the application
 * This provides a foundation for future TypeScript migration
 * 
 * @module typeDefs
 */

/**
 * @typedef {Object} Entity
 * @property {string} id - Unique identifier
 * @property {string} name - Entity name
 * @property {string} type - Entity type (MODEL, DATASET, PAPER, etc.)
 * @property {Object} properties - Additional properties
 * @property {string} [properties.description] - Optional description
 * @property {number|string} [properties.year] - Optional year
 * @property {number|string} [properties.confidence] - Optional confidence score
 */

/**
 * @typedef {Object} Relationship
 * @property {string} id - Unique identifier
 * @property {string} source - Source entity id
 * @property {string} target - Target entity id
 * @property {string} type - Relationship type (TRAINED_ON, CITES, etc.)
 * @property {Object} properties - Additional properties
 * @property {number|string} [properties.confidence] - Optional confidence score
 * @property {number|string} [properties.year] - Optional year
 */

/**
 * @typedef {Object} Graph
 * @property {Entity[]} entities - Array of entities
 * @property {Relationship[]} relationships - Array of relationships
 */

/**
 * @typedef {Object} Paper
 * @property {string} id - Unique identifier
 * @property {string} title - Paper title
 * @property {string[]} authors - Array of author names
 * @property {string|number} year - Publication year
 * @property {string} [abstract] - Paper abstract
 * @property {string} status - Processing status
 * @property {string} [url] - URL to paper
 * @property {string} uploaded_at - Upload timestamp
 * @property {string} [updated_at] - Last update timestamp
 */

/**
 * @typedef {Object} PaperDetails
 * @property {string} title - Paper title
 * @property {string} authors - Comma-separated author names
 * @property {string|number} year - Publication year
 * @property {string} [abstract] - Paper abstract
 */

/**
 * @typedef {Object} UploadResult
 * @property {boolean} success - Whether upload was successful
 * @property {Object} [data] - Result data if successful
 * @property {string} [error] - Error message if unsuccessful
 */

/**
 * @typedef {Object} User
 * @property {number|string} id - User ID
 * @property {string} username - Username
 * @property {string} [email] - Email address
 * @property {string} [full_name] - Full name
 * @property {string} [role] - User role
 * @property {string[]} [permissions] - User permissions
 */

/**
 * @typedef {Object} ResearchQuery
 * @property {string} query - Research query text
 * @property {string[]} [sources] - Optional sources to include
 * @property {Object} [options] - Additional options
 */

/**
 * @typedef {Object} ResearchResult
 * @property {string} query - Original query
 * @property {string} summary - Result summary
 * @property {Object[]} sources - Source information
 * @property {Object[]} sections - Content sections
 * @property {string[]} relatedTopics - Related topics
 * @property {Graph} entityGraph - Related entity graph
 */

/**
 * @typedef {Object} Implementation
 * @property {Paper} paper - The paper being implemented
 * @property {Object} implementation - Implementation details
 * @property {string} implementation.language - Programming language
 * @property {string} implementation.framework - Framework used
 * @property {Object[]} implementation.files - Files in implementation
 * @property {Object} implementation.stats - Implementation statistics
 * @property {string} implementation.sampleCode - Sample code
 */

/**
 * @typedef {Object} NotificationMessage
 * @property {string} id - Unique notification ID
 * @property {string} type - Message type
 * @property {string} category - Message category
 * @property {string} title - Notification title
 * @property {string} message - Notification message
 * @property {string} timestamp - Creation timestamp
 * @property {Object} [action] - Optional action to take on notification click
 * @property {string} action.type - Action type
 * @property {string} [action.path] - Navigation path if action is 'navigate'
 */

/**
 * @typedef {Object} WebSocketMessage
 * @property {string} type - Message type
 * @property {string} [channel] - Optional channel name
 * @property {Object} [data] - Message data
 */

/**
 * @typedef {Object} PaperStatusUpdate
 * @property {string} type - Message type ('paper_status_update')
 * @property {string} paper_id - Paper ID
 * @property {string} status - New status
 * @property {string} timestamp - Update timestamp
 */

export const PAPER_STATUSES = {
  UPLOADED: 'uploaded',
  QUEUED: 'queued',
  PROCESSING: 'processing',
  EXTRACTING_ENTITIES: 'extracting_entities',
  EXTRACTING_RELATIONSHIPS: 'extracting_relationships',
  BUILDING_KNOWLEDGE_GRAPH: 'building_knowledge_graph',
  ANALYZED: 'analyzed',
  IMPLEMENTATION_READY: 'implementation_ready',
  IMPLEMENTED: 'implemented',
  FAILED: 'failed',
  ERROR: 'error'
};

export const ENTITY_TYPES = {
  MODEL: 'MODEL',
  DATASET: 'DATASET',
  PAPER: 'PAPER',
  AUTHOR: 'AUTHOR',
  ALGORITHM: 'ALGORITHM',
  FRAMEWORK: 'FRAMEWORK',
  METRIC: 'METRIC'
};

export const RELATIONSHIP_TYPES = {
  TRAINED_ON: 'TRAINED_ON',
  CITES: 'CITES',
  AUTHORED_BY: 'AUTHORED_BY',
  IMPLEMENTS: 'IMPLEMENTS',
  BASED_ON: 'BASED_ON',
  OUTPERFORMS: 'OUTPERFORMS',
  USES: 'USES',
  EVALUATED_ON: 'EVALUATED_ON',
  PART_OF: 'PART_OF',
  DEVELOPED_BY: 'DEVELOPED_BY'
};

export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
  PAPER_STATUS: 'paper_status'
};

/**
 * Validate an entity object
 * @param {Entity} entity - Entity to validate
 * @returns {boolean} Whether entity is valid
 */
export const isValidEntity = (entity) => {
  return (
    entity &&
    typeof entity.id === 'string' &&
    typeof entity.name === 'string' &&
    typeof entity.type === 'string'
  );
};

/**
 * Validate a relationship object
 * @param {Relationship} relationship - Relationship to validate
 * @returns {boolean} Whether relationship is valid
 */
export const isValidRelationship = (relationship) => {
  return (
    relationship &&
    typeof relationship.id === 'string' &&
    typeof relationship.source === 'string' &&
    typeof relationship.target === 'string' &&
    typeof relationship.type === 'string'
  );
};

/**
 * Validate a paper object
 * @param {Paper} paper - Paper to validate
 * @returns {boolean} Whether paper is valid
 */
export const isValidPaper = (paper) => {
  return (
    paper &&
    typeof paper.id === 'string' &&
    typeof paper.title === 'string' &&
    Array.isArray(paper.authors) &&
    typeof paper.status === 'string'
  );
};

/**
 * Validate a graph object
 * @param {Graph} graph - Graph to validate
 * @returns {boolean} Whether graph is valid
 */
export const isValidGraph = (graph) => {
  return (
    graph &&
    Array.isArray(graph.entities) &&
    Array.isArray(graph.relationships) &&
    graph.entities.every(isValidEntity) &&
    graph.relationships.every(isValidRelationship)
  );
};