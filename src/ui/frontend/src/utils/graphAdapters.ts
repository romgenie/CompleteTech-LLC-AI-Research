/**
 * Adapters for making our Entity and Relationship types compatible with D3's force simulation
 */
import * as d3 from 'd3';
import { Entity, Relationship } from '../types';

/**
 * Type assertion function to treat Entity as SimulationNodeDatum
 * @param entity Entity to cast
 * @returns Entity as SimulationNodeDatum
 */
export function asSimulationNode(entity: Entity): d3.SimulationNodeDatum {
  return entity as unknown as d3.SimulationNodeDatum;
}

/**
 * Type assertion function to treat Relationship as SimulationLinkDatum
 * @param relationship Relationship to cast
 * @returns Relationship as SimulationLinkDatum
 */
export function asSimulationLink(relationship: Relationship): d3.SimulationLinkDatum<d3.SimulationNodeDatum> {
  return relationship as unknown as d3.SimulationLinkDatum<d3.SimulationNodeDatum>;
}

/**
 * Creates D3-compatible nodes from our entity objects
 * @param entities Array of entity objects
 * @returns Array of SimulationNodeDatum compatible objects
 */
export function createSimulationNodes(entities: Entity[]): d3.SimulationNodeDatum[] {
  return entities.map(asSimulationNode);
}

/**
 * Creates D3-compatible links from our relationship objects
 * @param relationships Array of relationship objects
 * @returns Array of SimulationLinkDatum compatible objects
 */
export function createSimulationLinks(relationships: Relationship[]): d3.SimulationLinkDatum<d3.SimulationNodeDatum>[] {
  return relationships.map(asSimulationLink);
}

/**
 * Type guard to check if a given object is an Entity
 * @param obj Object to check
 * @returns True if object is an Entity
 */
export function isEntity(obj: any): obj is Entity {
  return obj && typeof obj === 'object' && 'id' in obj && 'name' in obj && 'type' in obj;
}

/**
 * Get source/target ID from a relationship object with safe type handling
 * @param link Relationship object
 * @param key 'source' or 'target'
 * @returns ID string
 */
export function getLinkEntityId(link: Relationship, key: 'source' | 'target'): string {
  const value = link[key];
  if (typeof value === 'string') {
    return value;
  } else if (isEntity(value)) {
    return value.id;
  }
  throw new Error(`Invalid ${key} value in relationship`);
}