"""
Evolution Analyzer for the Temporal Evolution Layer.

This module provides analysis capabilities for detecting patterns in how entities evolve over time,
identifying trends, stagnation, recurring patterns, and convergence/divergence in research fields.
"""

from typing import Dict, List, Optional, Tuple, Set, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict

from knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)
from knowledge_graph_system.temporal_evolution.query_engine.temporal_query_engine import (
    TemporalQueryEngine
)


class TrendDirection(Enum):
    """Enumeration of possible trend directions."""
    ACCELERATING = "accelerating"
    DECELERATING = "decelerating"
    STEADY = "steady"
    STAGNANT = "stagnant"
    REVIVING = "reviving"
    DECLINING = "declining"


class ResearchActivity(Enum):
    """Enumeration of research activity levels."""
    VERY_ACTIVE = "very_active"
    ACTIVE = "active"
    MODERATE = "moderate"
    LOW = "low"
    DORMANT = "dormant"


class EntityEvolutionPattern(Enum):
    """Enumeration of entity evolution patterns."""
    LINEAR = "linear"                   # Straight path evolution (A → B → C)
    BRANCHING = "branching"             # Multiple variants emerge (A → B, A → C)
    MERGING = "merging"                 # Multiple entities combine (A, B → C)
    CYCLICAL = "cyclical"               # Returning to previous approaches
    SPIRAL = "spiral"                   # Similar to cyclical but progressing
    DISRUPTIVE = "disruptive"           # Sudden major changes
    INCREMENTAL = "incremental"         # Small iterative improvements
    CONVERGENT = "convergent"           # Different approaches becoming similar
    DIVERGENT = "divergent"             # Approaches becoming more different


class ResearchField:
    """Represents a research field with its entities and relationships."""

    def __init__(self, 
                 name: str, 
                 entities: List[TemporalEntityBase] = None,
                 relationships: List[TemporalRelationshipBase] = None):
        """
        Initialize a research field.

        Args:
            name: The name of the research field
            entities: List of entities in this field
            relationships: List of relationships in this field
        """
        self.name = name
        self.entities = entities or []
        self.relationships = relationships or []
        self.activity_history: Dict[datetime, int] = {}
        self.citation_history: Dict[datetime, int] = {}
        self.evolution_patterns: Dict[str, EntityEvolutionPattern] = {}
        
    def add_entity(self, entity: TemporalEntityBase) -> None:
        """Add an entity to the research field."""
        self.entities.append(entity)
        
    def add_relationship(self, relationship: TemporalRelationshipBase) -> None:
        """Add a relationship to the research field."""
        self.relationships.append(relationship)
        
    def update_activity_metrics(self, 
                               time_windows: List[Tuple[datetime, datetime]]) -> None:
        """
        Update activity metrics for the specified time windows.
        
        Args:
            time_windows: List of (start_time, end_time) tuples
        """
        for start_time, end_time in time_windows:
            # Count entities created or updated in this window
            activity_count = sum(1 for entity in self.entities 
                               if (entity.created_at >= start_time and entity.created_at <= end_time) or 
                                  (entity.updated_at and entity.updated_at >= start_time and 
                                   entity.updated_at <= end_time))
            
            # Count relationships created in this window
            activity_count += sum(1 for rel in self.relationships 
                                if rel.created_at >= start_time and rel.created_at <= end_time)
            
            # Use the middle of the time window as the key
            mid_point = start_time + (end_time - start_time) / 2
            self.activity_history[mid_point] = activity_count


class EvolutionAnalyzer:
    """
    Analyzer for detecting patterns in how entities and research fields evolve over time.
    """

    def __init__(self, query_engine: TemporalQueryEngine):
        """
        Initialize the Evolution Analyzer.
        
        Args:
            query_engine: The temporal query engine for retrieving data
        """
        self.query_engine = query_engine
        self.research_fields: Dict[str, ResearchField] = {}
        self.trend_cache: Dict[str, Dict[str, Any]] = {}
        
    def define_research_field(self, 
                             name: str, 
                             entity_types: List[str] = None,
                             relationship_types: List[str] = None,
                             keywords: List[str] = None) -> ResearchField:
        """
        Define a research field based on entity types, relationship types, and keywords.
        
        Args:
            name: The name of the research field
            entity_types: List of entity types to include
            relationship_types: List of relationship types to include
            keywords: List of keywords to search for
            
        Returns:
            The created ResearchField object
        """
        # Query for entities and relationships matching the criteria
        entities = self.query_engine.query_entities(
            entity_types=entity_types,
            keywords=keywords,
            time_window=None  # Get all time periods
        )
        
        relationships = self.query_engine.query_relationships(
            relationship_types=relationship_types,
            keywords=keywords,
            time_window=None  # Get all time periods
        )
        
        # Create and store the research field
        field = ResearchField(name, entities, relationships)
        self.research_fields[name] = field
        return field
    
    def analyze_activity_trend(self, 
                              field_name: str, 
                              time_period: int = 90,
                              num_periods: int = 8) -> Tuple[TrendDirection, Dict[datetime, int]]:
        """
        Analyze the activity trend for a research field.
        
        Args:
            field_name: The name of the research field
            time_period: Time period length in days
            num_periods: Number of time periods to analyze
            
        Returns:
            Tuple containing the trend direction and activity data
        """
        if field_name not in self.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
            
        field = self.research_fields[field_name]
        
        # Generate time windows for analysis
        end_time = datetime.now()
        time_windows = []
        for i in range(num_periods):
            window_end = end_time - timedelta(days=i * time_period)
            window_start = window_end - timedelta(days=time_period)
            time_windows.append((window_start, window_end))
            
        # Update activity metrics for these windows
        field.update_activity_metrics(time_windows)
        
        # Sort the activity history by time
        sorted_activities = sorted(field.activity_history.items())
        if len(sorted_activities) < 3:
            return TrendDirection.STEADY, dict(sorted_activities)
            
        # Analyze the trend using the last few data points
        recent_activities = [count for _, count in sorted_activities[-3:]]
        
        if all(count == 0 for count in recent_activities):
            return TrendDirection.STAGNANT, dict(sorted_activities)
            
        # Calculate first and second derivatives to determine acceleration
        first_derivative = [recent_activities[i+1] - recent_activities[i] 
                           for i in range(len(recent_activities)-1)]
        
        if len(first_derivative) >= 2:
            second_derivative = first_derivative[1] - first_derivative[0]
            
            if all(d > 0 for d in first_derivative):
                # Consistently increasing
                return (TrendDirection.ACCELERATING if second_derivative > 0 
                       else TrendDirection.STEADY, dict(sorted_activities))
            elif all(d < 0 for d in first_derivative):
                # Consistently decreasing
                return (TrendDirection.DECELERATING if second_derivative < 0 
                       else TrendDirection.DECLINING, dict(sorted_activities))
            elif first_derivative[-1] > 0 and first_derivative[0] <= 0:
                return TrendDirection.REVIVING, dict(sorted_activities)
            else:
                return TrendDirection.STEADY, dict(sorted_activities)
        else:
            # Not enough data points for second derivative
            if first_derivative[0] > 0:
                return TrendDirection.STEADY, dict(sorted_activities)
            elif first_derivative[0] < 0:
                return TrendDirection.DECLINING, dict(sorted_activities)
            else:
                return TrendDirection.STEADY, dict(sorted_activities)
    
    def detect_stagnant_areas(self, 
                             threshold_days: int = 365, 
                             activity_threshold: int = 5) -> List[str]:
        """
        Detect research areas that have been stagnant for a certain period.
        
        Args:
            threshold_days: Number of days to consider for stagnation
            activity_threshold: Minimum activity to avoid stagnation classification
            
        Returns:
            List of stagnant research field names
        """
        stagnant_fields = []
        
        for name, field in self.research_fields.items():
            # Check if there's been any activity in the specified time window
            threshold_date = datetime.now() - timedelta(days=threshold_days)
            
            # Count recent entity and relationship activity
            recent_entity_activity = sum(1 for entity in field.entities 
                                      if (entity.created_at >= threshold_date) or 
                                         (entity.updated_at and entity.updated_at >= threshold_date))
            
            recent_relationship_activity = sum(1 for rel in field.relationships 
                                           if rel.created_at >= threshold_date)
            
            total_activity = recent_entity_activity + recent_relationship_activity
            
            if total_activity < activity_threshold:
                stagnant_fields.append(name)
                
        return stagnant_fields
    
    def identify_cyclical_patterns(self, 
                                 field_name: str, 
                                 time_period: int = 90,
                                 num_periods: int = 24,
                                 similarity_threshold: float = 0.7) -> List[Tuple[datetime, datetime]]:
        """
        Identify cyclical patterns in research activity.
        
        Args:
            field_name: The name of the research field
            time_period: Time period length in days
            num_periods: Number of time periods to analyze
            similarity_threshold: Threshold for determining similarity between periods
            
        Returns:
            List of time period pairs that show cyclical patterns
        """
        if field_name not in self.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
            
        field = self.research_fields[field_name]
        
        # Generate time windows for analysis
        end_time = datetime.now()
        time_windows = []
        for i in range(num_periods):
            window_end = end_time - timedelta(days=i * time_period)
            window_start = window_end - timedelta(days=time_period)
            time_windows.append((window_start, window_end))
            
        # Get entities and relationships for each window
        period_entities = []
        period_relationships = []
        period_midpoints = []
        
        for start_time, end_time in time_windows:
            # Get entities active in this window
            window_entities = [e for e in field.entities 
                            if (e.created_at >= start_time and e.created_at <= end_time) or 
                               (e.updated_at and e.updated_at >= start_time and e.updated_at <= end_time)]
            
            # Get relationships active in this window
            window_relationships = [r for r in field.relationships 
                                 if r.created_at >= start_time and r.created_at <= end_time]
            
            period_entities.append(set(e.name for e in window_entities))
            period_relationships.append(set(f"{r.source_id}_{r.target_id}_{r.type}" 
                                      for r in window_relationships))
            period_midpoints.append(start_time + (end_time - start_time) / 2)
        
        # Find periods with similar patterns
        cyclical_patterns = []
        
        for i in range(len(period_entities)):
            for j in range(i + 3, len(period_entities)):  # Look at least 3 periods apart
                # Calculate Jaccard similarity for entities
                if not period_entities[i] or not period_entities[j]:
                    continue
                    
                entity_intersection = period_entities[i].intersection(period_entities[j])
                entity_union = period_entities[i].union(period_entities[j])
                entity_similarity = len(entity_intersection) / len(entity_union) if entity_union else 0
                
                # Calculate similarity for relationships
                relationship_similarity = 0
                if period_relationships[i] and period_relationships[j]:
                    rel_intersection = period_relationships[i].intersection(period_relationships[j])
                    rel_union = period_relationships[i].union(period_relationships[j])
                    relationship_similarity = len(rel_intersection) / len(rel_union) if rel_union else 0
                
                # Combined similarity
                combined_similarity = (entity_similarity + relationship_similarity) / 2
                
                if combined_similarity >= similarity_threshold:
                    cyclical_patterns.append((period_midpoints[i], period_midpoints[j]))
        
        return cyclical_patterns
    
    def analyze_convergence_divergence(self, 
                                      field_names: List[str],
                                      time_period: int = 90,
                                      num_periods: int = 8) -> Dict[str, Dict[str, float]]:
        """
        Analyze whether research fields are converging or diverging over time.
        
        Args:
            field_names: List of research field names to compare
            time_period: Time period length in days
            num_periods: Number of time periods to analyze
            
        Returns:
            Dictionary mapping time periods to similarity matrices between fields
        """
        # Check if all fields exist
        for name in field_names:
            if name not in self.research_fields:
                raise ValueError(f"Research field '{name}' not found")
        
        # Generate time windows for analysis
        end_time = datetime.now()
        time_windows = []
        for i in range(num_periods):
            window_end = end_time - timedelta(days=i * time_period)
            window_start = window_end - timedelta(days=time_period)
            time_windows.append((window_start, window_end))
        
        # Calculate similarity between fields for each time window
        results = {}
        
        for start_time, end_time in time_windows:
            window_key = start_time.strftime("%Y-%m-%d")
            results[window_key] = {}
            
            for i, field1_name in enumerate(field_names):
                field1 = self.research_fields[field1_name]
                
                # Get entities and relationships active in this window for field1
                field1_entities = set(e.name for e in field1.entities 
                                  if (e.created_at >= start_time and e.created_at <= end_time) or 
                                     (e.updated_at and e.updated_at >= start_time and 
                                      e.updated_at <= end_time))
                
                field1_relationships = set(f"{r.source_id}_{r.target_id}_{r.type}" 
                                       for r in field1.relationships 
                                       if r.created_at >= start_time and r.created_at <= end_time)
                
                for j, field2_name in enumerate(field_names[i+1:], i+1):
                    field2 = self.research_fields[field2_name]
                    
                    # Get entities and relationships for field2
                    field2_entities = set(e.name for e in field2.entities 
                                      if (e.created_at >= start_time and e.created_at <= end_time) or 
                                         (e.updated_at and e.updated_at >= start_time and 
                                          e.updated_at <= end_time))
                    
                    field2_relationships = set(f"{r.source_id}_{r.target_id}_{r.type}" 
                                          for r in field2.relationships 
                                          if r.created_at >= start_time and r.created_at <= end_time)
                    
                    # Calculate similarities
                    entity_similarity = 0
                    if field1_entities and field2_entities:
                        entity_intersection = field1_entities.intersection(field2_entities)
                        entity_union = field1_entities.union(field2_entities)
                        entity_similarity = len(entity_intersection) / len(entity_union)
                    
                    relationship_similarity = 0
                    if field1_relationships and field2_relationships:
                        rel_intersection = field1_relationships.intersection(field2_relationships)
                        rel_union = field1_relationships.union(field2_relationships)
                        relationship_similarity = len(rel_intersection) / len(rel_union)
                    
                    # Combined similarity
                    combined_similarity = (entity_similarity + relationship_similarity) / 2
                    field_pair = f"{field1_name}_{field2_name}"
                    results[window_key][field_pair] = combined_similarity
        
        return results
    
    def identify_evolution_patterns(self, entity_id: str) -> EntityEvolutionPattern:
        """
        Identify the evolution pattern for a specific entity and its descendants.
        
        Args:
            entity_id: The ID of the entity to analyze
            
        Returns:
            The identified evolution pattern
        """
        # Get the entity's evolution tree
        evolution_tree = self.query_engine.trace_concept_evolution(entity_id)
        
        if not evolution_tree:
            return None
        
        # Count incoming and outgoing evolution relationships for each node
        incoming_edges = defaultdict(int)
        outgoing_edges = defaultdict(int)
        
        for parent_id, children in evolution_tree.items():
            outgoing_edges[parent_id] = len(children)
            for child_id in children:
                incoming_edges[child_id] += 1
        
        # Count root nodes (no incoming edges) and leaf nodes (no outgoing edges)
        root_nodes = [node for node in evolution_tree if incoming_edges[node] == 0]
        leaf_nodes = [node for node in evolution_tree if outgoing_edges[node] == 0]
        
        # Identify branching nodes (multiple outgoing edges)
        branching_nodes = [node for node, count in outgoing_edges.items() if count > 1]
        
        # Identify merging nodes (multiple incoming edges)
        merging_nodes = [node for node, count in incoming_edges.items() if count > 1]
        
        # Check for cycles in the evolution graph
        has_cycle = self._has_cycle(evolution_tree)
        
        # Check for spiral pattern (cycle with progressive improvement)
        # This would require additional metadata about performance metrics
        
        # Determine the pattern based on graph structure
        if has_cycle:
            # Further analysis could distinguish between cyclical and spiral
            return EntityEvolutionPattern.CYCLICAL
        elif len(branching_nodes) > 0 and len(merging_nodes) > 0:
            # Complex pattern with both branching and merging
            # Could further analyze which is more dominant
            return EntityEvolutionPattern.CONVERGENT if len(merging_nodes) > len(branching_nodes) else EntityEvolutionPattern.DIVERGENT
        elif len(branching_nodes) > 0:
            return EntityEvolutionPattern.BRANCHING
        elif len(merging_nodes) > 0:
            return EntityEvolutionPattern.MERGING
        elif len(root_nodes) == 1 and len(leaf_nodes) == 1:
            # Simple linear evolution
            return EntityEvolutionPattern.LINEAR
        else:
            # Default case
            return EntityEvolutionPattern.INCREMENTAL
    
    def _has_cycle(self, graph: Dict[str, List[str]]) -> bool:
        """
        Check if a directed graph contains a cycle.
        
        Args:
            graph: Dictionary representing the graph (node_id -> list of children)
            
        Returns:
            True if the graph has a cycle, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def identify_research_waves(self, 
                               field_name: str,
                               min_wave_length: int = 180,
                               max_wave_length: int = 1095,
                               num_samples: int = 20) -> List[Dict[str, Any]]:
        """
        Identify research waves (periods of increased activity followed by decreased activity).
        
        Args:
            field_name: The name of the research field
            min_wave_length: Minimum wave length in days
            max_wave_length: Maximum wave length in days
            num_samples: Number of sampling points for analysis
            
        Returns:
            List of identified research waves with their properties
        """
        if field_name not in self.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
            
        field = self.research_fields[field_name]
        
        # Generate time windows for analysis
        end_time = datetime.now()
        start_time = end_time - timedelta(days=max_wave_length * 2)  # Look back twice max wave length
        
        step_size = (end_time - start_time) / num_samples
        time_windows = []
        
        for i in range(num_samples - 1):
            window_start = start_time + i * step_size
            window_end = start_time + (i + 1) * step_size
            time_windows.append((window_start, window_end))
            
        # Update activity metrics
        field.update_activity_metrics(time_windows)
        
        # Sort activity by time
        activity_data = sorted(field.activity_history.items())
        if len(activity_data) < 5:  # Need enough data points
            return []
            
        # Convert to numpy arrays for analysis
        times = np.array([t.timestamp() for t, _ in activity_data])
        activities = np.array([a for _, a in activity_data])
        
        # Find local maxima and minima
        peak_indices = []
        valley_indices = []
        
        for i in range(1, len(activities) - 1):
            if activities[i] > activities[i-1] and activities[i] > activities[i+1]:
                peak_indices.append(i)
            elif activities[i] < activities[i-1] and activities[i] < activities[i+1]:
                valley_indices.append(i)
        
        # Identify waves (peak to peak)
        waves = []
        
        for i in range(len(peak_indices) - 1):
            start_peak = peak_indices[i]
            end_peak = peak_indices[i + 1]
            
            # Calculate wave duration
            wave_duration_seconds = times[end_peak] - times[start_peak]
            wave_duration_days = wave_duration_seconds / (24 * 3600)
            
            # Only consider waves within the specified length range
            if min_wave_length <= wave_duration_days <= max_wave_length:
                # Find the valley between these peaks
                valley_index = None
                for v in valley_indices:
                    if start_peak < v < end_peak:
                        if valley_index is None or activities[v] < activities[valley_index]:
                            valley_index = v
                
                if valley_index is not None:
                    # Calculate wave amplitude
                    start_amplitude = activities[start_peak] - activities[valley_index]
                    end_amplitude = activities[end_peak] - activities[valley_index]
                    avg_amplitude = (start_amplitude + end_amplitude) / 2
                    
                    # Only consider significant waves
                    if avg_amplitude > 0:
                        waves.append({
                            'start_date': datetime.fromtimestamp(times[start_peak]),
                            'valley_date': datetime.fromtimestamp(times[valley_index]),
                            'end_date': datetime.fromtimestamp(times[end_peak]),
                            'duration_days': wave_duration_days,
                            'amplitude': avg_amplitude,
                            'start_activity': activities[start_peak],
                            'valley_activity': activities[valley_index],
                            'end_activity': activities[end_peak]
                        })
        
        # Sort waves by duration
        waves.sort(key=lambda x: x['duration_days'])
        return waves