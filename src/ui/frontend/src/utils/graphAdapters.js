/**
 * Adapters for making our Entity and Relationship types compatible with D3's force simulation
 */
import * as d3 from 'd3';
import { Entity, Relationship } from '../types';

/**
 * Type assertion function to treat Entity as SimulationNodeDatum
 * @param {Entity} entity Entity to cast
 * @returns {object} Entity as SimulationNodeDatum
 */
export function asSimulationNode(entity) {
  return entity;
}

/**
 * Type assertion function to treat Relationship as SimulationLinkDatum
 * @param {Relationship} relationship Relationship to cast
 * @returns {object} Relationship as SimulationLinkDatum
 */
export function asSimulationLink(relationship) {
  return relationship;
}

/**
 * Creates D3-compatible nodes from our entity objects
 * @param {Entity[]} entities Array of entity objects
 * @returns {object[]} Array of SimulationNodeDatum compatible objects
 */
export function createSimulationNodes(entities) {
  return entities.map(asSimulationNode);
}

/**
 * Creates D3-compatible links from our relationship objects
 * @param {Relationship[]} relationships Array of relationship objects
 * @returns {object[]} Array of SimulationLinkDatum compatible objects
 */
export function createSimulationLinks(relationships) {
  return relationships.map(asSimulationLink);
}

/**
 * Type guard to check if a given object is an Entity
 * @param {any} obj Object to check
 * @returns {boolean} True if object is an Entity
 */
export function isEntity(obj) {
  return obj && typeof obj === 'object' && 'id' in obj && 'name' in obj && 'type' in obj;
}

/**
 * Get source/target ID from a relationship object with safe type handling
 * @param {Relationship} link Relationship object
 * @param {'source' | 'target'} key 'source' or 'target'
 * @returns {string} ID string
 */
export function getLinkEntityId(link, key) {
  const value = link[key];
  if (typeof value === 'string') {
    return value;
  } else if (isEntity(value)) {
    return value.id;
  }
  throw new Error(`Invalid ${key} value in relationship`);
}