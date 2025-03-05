"""
Evolution Predictor for the Temporal Evolution Layer.

This module provides predictive modeling capabilities for forecasting research trends,
identifying knowledge gaps, and projecting future evolution paths for entities.
"""

from typing import Dict, List, Optional, Tuple, Set, Any, Union
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import networkx as nx
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

from knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)
from knowledge_graph_system.temporal_evolution.query_engine.temporal_query_engine import (
    TemporalQueryEngine
)
from knowledge_graph_system.temporal_evolution.analyzer.evolution_analyzer import (
    EvolutionAnalyzer, ResearchField, TrendDirection, EntityEvolutionPattern
)


class PredictionWindow(Tuple[datetime, datetime]):
    """A time window for predictions with start and end times."""
    pass


class EvolutionTrajectory:
    """
    Represents a predicted evolution trajectory for a research entity or field.
    """
    
    def __init__(self, 
                name: str, 
                start_date: datetime,
                end_date: datetime,
                prediction_points: List[Tuple[datetime, float]],
                confidence: float = 0.0,
                related_entities: List[str] = None):
        """
        Initialize an evolution trajectory.
        
        Args:
            name: Name of the entity or field
            start_date: Start date of the prediction
            end_date: End date of the prediction
            prediction_points: List of (date, value) points representing the predicted trajectory
            confidence: Confidence score for this prediction (0-1)
            related_entities: List of related entity names or IDs
        """
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.prediction_points = prediction_points
        self.confidence = confidence
        self.related_entities = related_entities or []
        self.peaks = []  # Will hold peak points in the trajectory
        self.valleys = []  # Will hold valley points in the trajectory
        
        # Extract dates and values for easier access
        self.dates = [point[0] for point in prediction_points]
        self.values = [point[1] for point in prediction_points]
        
        # Identify peaks and valleys if there are enough points
        if len(prediction_points) >= 3:
            self._identify_peaks_valleys()
    
    def _identify_peaks_valleys(self):
        """Identify peaks and valleys in the prediction trajectory."""
        for i in range(1, len(self.prediction_points) - 1):
            current_val = self.values[i]
            prev_val = self.values[i - 1]
            next_val = self.values[i + 1]
            
            # Identify peaks (local maxima)
            if current_val > prev_val and current_val > next_val:
                self.peaks.append((self.dates[i], current_val))
                
            # Identify valleys (local minima)
            if current_val < prev_val and current_val < next_val:
                self.valleys.append((self.dates[i], current_val))
    
    def get_average_trend(self) -> float:
        """
        Calculate the average trend value (slope) for the trajectory.
        
        Returns:
            The average slope of the trajectory
        """
        if len(self.prediction_points) < 2:
            return 0.0
            
        # Create arrays of x (days since start) and y (values)
        x = [(date - self.start_date).days for date in self.dates]
        y = self.values
        
        # Fit a line and return the slope
        if len(x) > 1:
            try:
                model = LinearRegression()
                model.fit(np.array(x).reshape(-1, 1), y)
                return model.coef_[0]
            except:
                # Fallback to simple delta calculation
                return (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
        return 0.0
    
    def get_trend_direction(self) -> TrendDirection:
        """
        Determine the overall trend direction based on the trajectory.
        
        Returns:
            TrendDirection indicating the trajectory trend
        """
        avg_trend = self.get_average_trend()
        
        # Check for stagnation
        if abs(avg_trend) < 0.01 and max(self.values) - min(self.values) < 0.1:
            return TrendDirection.STAGNANT
            
        # Look for acceleration/deceleration by analyzing the curve
        if len(self.prediction_points) >= 4:
            # Divide the trajectory into two halves and compare trends
            mid_point = len(self.prediction_points) // 2
            
            first_half_x = [(date - self.start_date).days for date in self.dates[:mid_point]]
            first_half_y = self.values[:mid_point]
            
            second_half_x = [(date - self.start_date).days for date in self.dates[mid_point:]]
            second_half_y = self.values[mid_point:]
            
            # Calculate trends for each half
            if len(first_half_x) > 1 and len(second_half_x) > 1:
                try:
                    model1 = LinearRegression()
                    model1.fit(np.array(first_half_x).reshape(-1, 1), first_half_y)
                    first_half_trend = model1.coef_[0]
                    
                    model2 = LinearRegression()
                    model2.fit(np.array(second_half_x).reshape(-1, 1), second_half_y)
                    second_half_trend = model2.coef_[0]
                    
                    # Compare trends
                    if first_half_trend > 0 and second_half_trend > first_half_trend:
                        return TrendDirection.ACCELERATING
                    elif first_half_trend > 0 and second_half_trend < first_half_trend:
                        return TrendDirection.DECELERATING
                    elif first_half_trend < 0 and second_half_trend > 0:
                        return TrendDirection.REVIVING
                    elif first_half_trend < 0 and second_half_trend < 0:
                        return TrendDirection.DECLINING
                except:
                    pass
        
        # Fallback to simple trend analysis
        if avg_trend > 0.05:
            return TrendDirection.STEADY
        elif avg_trend < -0.05:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STEADY


class KnowledgeGap:
    """
    Represents an identified gap in the knowledge graph that could be promising for research.
    """
    
    def __init__(self, 
                name: str, 
                description: str,
                related_entities: List[str],
                gap_score: float,
                potential_score: float,
                confidence: float):
        """
        Initialize a knowledge gap.
        
        Args:
            name: Short name for the gap
            description: Detailed description of the gap
            related_entities: List of entity IDs or names related to this gap
            gap_score: Score indicating the size of the gap (0-1)
            potential_score: Score indicating the potential value of filling the gap (0-1)
            confidence: Confidence in this gap identification (0-1)
        """
        self.name = name
        self.description = description
        self.related_entities = related_entities
        self.gap_score = gap_score
        self.potential_score = potential_score
        self.confidence = confidence
        
        # Calculate an overall priority score
        self.priority_score = (gap_score * 0.3 + potential_score * 0.5 + confidence * 0.2)


class EvolutionPredictor:
    """
    Predictor for forecasting research evolution trends and identifying knowledge gaps.
    """
    
    def __init__(self, 
                query_engine: TemporalQueryEngine,
                analyzer: EvolutionAnalyzer):
        """
        Initialize the Evolution Predictor.
        
        Args:
            query_engine: The temporal query engine for retrieving data
            analyzer: The evolution analyzer for trend analysis
        """
        self.query_engine = query_engine
        self.analyzer = analyzer
        self.trajectory_cache: Dict[str, EvolutionTrajectory] = {}
        self.gap_cache: Dict[str, KnowledgeGap] = {}
        self.model_cache: Dict[str, Any] = {}
    
    def predict_field_trajectory(self, 
                               field_name: str,
                               prediction_window: Tuple[datetime, datetime],
                               num_points: int = 10,
                               model_type: str = 'linear') -> EvolutionTrajectory:
        """
        Predict the activity trajectory for a research field.
        
        Args:
            field_name: Name of the research field
            prediction_window: (start_date, end_date) for the prediction
            num_points: Number of prediction points to generate
            model_type: Type of prediction model ('linear', 'forest', 'arima')
            
        Returns:
            EvolutionTrajectory for the predicted activity
        """
        if field_name not in self.analyzer.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
            
        field = self.analyzer.research_fields[field_name]
        
        # Get historical activity data
        if not field.activity_history:
            # Generate historical data if not already present
            self._generate_historical_data(field)
            
        # Sort historical data by date
        historical_data = sorted(field.activity_history.items())
        
        if len(historical_data) < 3:
            raise ValueError(f"Not enough historical data for field '{field_name}'")
        
        # Prepare data for modeling
        hist_dates = [date for date, _ in historical_data]
        hist_values = [value for _, value in historical_data]
        
        # Convert dates to numeric (days since first date)
        first_date = hist_dates[0]
        hist_days = [(date - first_date).days for date in hist_dates]
        
        # Fit the prediction model
        if model_type == 'linear':
            model = self._fit_linear_model(hist_days, hist_values)
        elif model_type == 'forest':
            model = self._fit_random_forest_model(hist_days, hist_values)
        else:  # Default to linear
            model = self._fit_linear_model(hist_days, hist_values)
        
        # Generate prediction dates
        start_date, end_date = prediction_window
        date_range = (end_date - start_date).days
        prediction_days = np.linspace(
            (start_date - first_date).days,
            (end_date - first_date).days,
            num_points
        )
        
        # Make predictions
        predicted_values = self._predict_with_model(model, prediction_days, model_type)
        
        # Convert days back to dates
        prediction_dates = [first_date + timedelta(days=int(days)) for days in prediction_days]
        
        # Create trajectory
        prediction_points = list(zip(prediction_dates, predicted_values))
        
        # Calculate confidence based on historical data quality
        confidence = self._calculate_prediction_confidence(field, model, hist_days, hist_values)
        
        # Get related entities
        related_entities = [entity.name for entity in field.entities[:10]]  # Top 10 entities
        
        trajectory = EvolutionTrajectory(
            name=field_name,
            start_date=start_date,
            end_date=end_date,
            prediction_points=prediction_points,
            confidence=confidence,
            related_entities=related_entities
        )
        
        # Cache the trajectory
        cache_key = f"{field_name}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        self.trajectory_cache[cache_key] = trajectory
        
        return trajectory
    
    def _generate_historical_data(self, field: ResearchField):
        """
        Generate historical activity data for a field.
        
        Args:
            field: The research field to generate data for
        """
        # Find the oldest and newest entity/relationship dates
        entity_dates = [entity.created_at for entity in field.entities]
        if field.relationships:
            rel_dates = [rel.created_at for rel in field.relationships]
            all_dates = entity_dates + rel_dates
        else:
            all_dates = entity_dates
            
        if not all_dates:
            raise ValueError(f"No temporal data found for field '{field.name}'")
            
        start_date = min(all_dates)
        end_date = max(all_dates)
        
        # Generate quarterly windows
        time_windows = []
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + timedelta(days=90)  # Approximately one quarter
            time_windows.append((current_date, next_date))
            current_date = next_date
            
        # Update activity metrics for these windows
        field.update_activity_metrics(time_windows)
    
    def _fit_linear_model(self, x_data, y_data):
        """Fit a linear regression model to the data."""
        model = LinearRegression()
        model.fit(np.array(x_data).reshape(-1, 1), y_data)
        return model
    
    def _fit_random_forest_model(self, x_data, y_data):
        """Fit a random forest regression model to the data."""
        # Convert x_data to features (e.g., day of year, month, etc.)
        features = []
        for days in x_data:
            # Simple example: use the day value and its square as features
            features.append([days, days**2])
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(features, y_data)
        return model
    
    def _predict_with_model(self, model, prediction_days, model_type):
        """Make predictions using the fitted model."""
        if model_type == 'linear':
            return model.predict(prediction_days.reshape(-1, 1))
        elif model_type == 'forest':
            # Convert prediction_days to features
            features = []
            for days in prediction_days:
                features.append([days, days**2])
            return model.predict(features)
        else:
            return model.predict(prediction_days.reshape(-1, 1))
    
    def _calculate_prediction_confidence(self, field, model, hist_days, hist_values):
        """Calculate confidence score for the prediction based on model quality."""
        # For linear model, use R² as a base for confidence
        if hasattr(model, 'score'):
            r2_score = model.score(np.array(hist_days).reshape(-1, 1), hist_values)
            base_confidence = max(0, min(r2_score, 1))  # Ensure between 0 and 1
        else:
            base_confidence = 0.5  # Default
        
        # Adjust based on amount of historical data
        data_factor = min(len(hist_days) / 10, 1)  # Scales up to 1 with 10+ data points
        
        # Adjust based on data consistency
        if len(hist_values) > 2:
            # Calculate variance normalized by the mean
            mean_value = np.mean(hist_values)
            if mean_value > 0:
                normalized_variance = np.var(hist_values) / (mean_value ** 2)
                consistency_factor = 1 / (1 + normalized_variance * 10)  # Lower variance = higher confidence
            else:
                consistency_factor = 0.5
        else:
            consistency_factor = 0.5
            
        # Combine factors
        return base_confidence * 0.5 + data_factor * 0.3 + consistency_factor * 0.2
    
    def identify_knowledge_gaps(self, 
                              field_name: str,
                              min_gap_score: float = 0.5,
                              max_gaps: int = 5) -> List[KnowledgeGap]:
        """
        Identify potential knowledge gaps in a research field.
        
        Args:
            field_name: Name of the research field
            min_gap_score: Minimum gap score to include
            max_gaps: Maximum number of gaps to return
            
        Returns:
            List of KnowledgeGap objects representing identified gaps
        """
        if field_name not in self.analyzer.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
            
        field = self.analyzer.research_fields[field_name]
        
        # Get entities and relationships
        entities = field.entities
        relationships = field.relationships
        
        # Create a graph representation of the field
        G = nx.DiGraph()
        
        # Add nodes for entities
        for entity in entities:
            G.add_node(entity.id, name=entity.name, type=entity.entity_type)
        
        # Add edges for relationships
        for rel in relationships:
            G.add_edge(rel.source_id, rel.target_id, type=rel.type)
        
        # Identify potential gaps through various methods
        gaps = []
        
        # Method 1: Find entity groups with missing connections
        gaps.extend(self._identify_missing_connections(G, field))
        
        # Method 2: Find isolated entity clusters
        gaps.extend(self._identify_isolated_clusters(G, field))
        
        # Method 3: Find trending entities without recent developments
        gaps.extend(self._identify_stagnant_trending_entities(field))
        
        # Method 4: Find research areas with diverging patterns
        gaps.extend(self._identify_diverging_areas(field))
        
        # Filter by minimum gap score
        gaps = [gap for gap in gaps if gap.gap_score >= min_gap_score]
        
        # Sort by priority score and limit to max_gaps
        gaps.sort(key=lambda x: x.priority_score, reverse=True)
        gaps = gaps[:max_gaps]
        
        # Cache results
        for gap in gaps:
            self.gap_cache[gap.name] = gap
            
        return gaps
    
    def _identify_missing_connections(self, graph, field):
        """
        Identify potential missing connections between entities.
        
        Args:
            graph: NetworkX graph of the field
            field: ResearchField object
            
        Returns:
            List of KnowledgeGap objects for missing connections
        """
        gaps = []
        
        # Look for triangles with missing edges (A→B, B→C, but no A→C)
        for node_a in graph.nodes():
            for node_b in graph.successors(node_a):
                for node_c in graph.successors(node_b):
                    if node_c != node_a and not graph.has_edge(node_a, node_c):
                        # Found a potential missing connection
                        entity_a = next((e for e in field.entities if e.id == node_a), None)
                        entity_b = next((e for e in field.entities if e.id == node_b), None)
                        entity_c = next((e for e in field.entities if e.id == node_c), None)
                        
                        if entity_a and entity_c:
                            # Calculate scores
                            gap_score = 0.7  # High gap score for missing triangular connections
                            
                            # Higher potential if the entities are recently active
                            recency_a = self._calculate_entity_recency(entity_a)
                            recency_c = self._calculate_entity_recency(entity_c)
                            potential_score = 0.5 + 0.25 * (recency_a + recency_c)
                            
                            # Higher confidence if there are multiple intermediaries
                            other_paths = list(nx.all_simple_paths(graph, node_a, node_c, cutoff=2))
                            confidence = 0.5 + min(0.5, 0.1 * len(other_paths))
                            
                            # Create gap
                            gap = KnowledgeGap(
                                name=f"Missing link: {entity_a.name} → {entity_c.name}",
                                description=f"Potential direct relationship between {entity_a.name} and "
                                           f"{entity_c.name}, currently connected through {entity_b.name}",
                                related_entities=[entity_a.name, entity_b.name, entity_c.name],
                                gap_score=gap_score,
                                potential_score=potential_score,
                                confidence=confidence
                            )
                            gaps.append(gap)
        
        return gaps
    
    def _identify_isolated_clusters(self, graph, field):
        """
        Identify isolated clusters that could be connected.
        
        Args:
            graph: NetworkX graph of the field
            field: ResearchField object
            
        Returns:
            List of KnowledgeGap objects for isolated clusters
        """
        gaps = []
        
        # Find weakly connected components
        components = list(nx.weakly_connected_components(graph))
        if len(components) <= 1:
            return gaps  # Only one component, no isolation
            
        # For each pair of components, evaluate potential connections
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                # Find the most "central" nodes in each component
                subgraph1 = graph.subgraph(comp1)
                subgraph2 = graph.subgraph(comp2)
                
                try:
                    central_node1 = max(subgraph1.nodes(), 
                                      key=lambda n: nx.closeness_centrality(subgraph1)[n])
                    central_node2 = max(subgraph2.nodes(), 
                                      key=lambda n: nx.closeness_centrality(subgraph2)[n])
                    
                    # Get corresponding entities
                    entity1 = next((e for e in field.entities if e.id == central_node1), None)
                    entity2 = next((e for e in field.entities if e.id == central_node2), None)
                    
                    if entity1 and entity2:
                        # Calculate scores
                        # Gap score based on component sizes (larger components = larger gap)
                        gap_score = 0.5 + 0.1 * min(5, len(comp1) + len(comp2)) / 10
                        
                        # Potential score based on component activity levels
                        comp1_entities = [e for e in field.entities if e.id in comp1]
                        comp2_entities = [e for e in field.entities if e.id in comp2]
                        comp1_activity = sum(self._calculate_entity_recency(e) for e in comp1_entities) / len(comp1_entities)
                        comp2_activity = sum(self._calculate_entity_recency(e) for e in comp2_entities) / len(comp2_entities)
                        potential_score = 0.5 * (comp1_activity + comp2_activity)
                        
                        # Confidence based on similarity between the central entities
                        # This is a placeholder - in a real system, you would use entity embeddings or attribute similarity
                        confidence = 0.6  # Default confidence for isolated clusters
                        
                        # Create gap
                        gap = KnowledgeGap(
                            name=f"Isolated clusters: {entity1.name} and {entity2.name}",
                            description=f"Potential connection between isolated research clusters "
                                       f"centered around {entity1.name} and {entity2.name}",
                            related_entities=[entity1.name, entity2.name],
                            gap_score=gap_score,
                            potential_score=potential_score,
                            confidence=confidence
                        )
                        gaps.append(gap)
                except Exception as e:
                    # Skip this pair if there's an error in centrality calculation
                    continue
        
        return gaps
    
    def _identify_stagnant_trending_entities(self, field):
        """
        Identify entities that were trending but have become stagnant.
        
        Args:
            field: ResearchField object
            
        Returns:
            List of KnowledgeGap objects for stagnant trending entities
        """
        gaps = []
        
        # Get recent activity trend
        trend, _ = self.analyzer.analyze_activity_trend(field.name)
        
        # Only look for stagnant trending entities if the field was active previously
        if trend in [TrendDirection.DECLINING, TrendDirection.STAGNANT, TrendDirection.DECELERATING]:
            # Find entities that haven't been updated recently
            stagnant_entities = []
            threshold_date = datetime.now() - timedelta(days=365)  # 1 year threshold
            
            for entity in field.entities:
                # Check if entity was active previously but is now stagnant
                if entity.created_at < threshold_date and (
                    not entity.updated_at or entity.updated_at < threshold_date):
                    # Calculate a "previous activity" score based on relationships
                    rel_count = sum(1 for rel in field.relationships 
                                 if (rel.source_id == entity.id or rel.target_id == entity.id) and
                                    rel.created_at < threshold_date)
                    
                    if rel_count > 0:  # Only consider previously active entities
                        stagnant_entities.append((entity, rel_count))
            
            # Sort by previous activity (higher first)
            stagnant_entities.sort(key=lambda x: x[1], reverse=True)
            
            # Create gaps for top stagnant entities
            for entity, rel_count in stagnant_entities[:5]:  # Top 5
                # Calculate scores
                gap_score = 0.5 + min(0.5, rel_count / 20)  # Higher score for more previous relationships
                
                # Higher potential for entities that were very active
                potential_score = 0.6 + min(0.4, rel_count / 30)
                
                # Confidence based on field declining trend strength
                confidence = 0.7 if trend == TrendDirection.DECLINING else 0.6
                
                # Get related entities through relationships
                related_entity_ids = set()
                for rel in field.relationships:
                    if rel.source_id == entity.id:
                        related_entity_ids.add(rel.target_id)
                    elif rel.target_id == entity.id:
                        related_entity_ids.add(rel.source_id)
                
                related_entities = [entity.name]
                for entity_id in related_entity_ids:
                    related_entity = next((e for e in field.entities if e.id == entity_id), None)
                    if related_entity:
                        related_entities.append(related_entity.name)
                
                # Create gap
                gap = KnowledgeGap(
                    name=f"Stagnant research: {entity.name}",
                    description=f"Previously active research area around {entity.name} "
                               f"has become stagnant with no updates in over a year",
                    related_entities=related_entities[:5],  # Top 5 related entities
                    gap_score=gap_score,
                    potential_score=potential_score,
                    confidence=confidence
                )
                gaps.append(gap)
        
        return gaps
    
    def _identify_diverging_areas(self, field):
        """
        Identify areas that are diverging from the main research direction.
        
        Args:
            field: ResearchField object
            
        Returns:
            List of KnowledgeGap objects for diverging areas
        """
        gaps = []
        
        # Create a graph of entity relationships
        G = nx.Graph()
        
        # Add nodes and edges from field data
        for entity in field.entities:
            G.add_node(entity.id, name=entity.name, created_at=entity.created_at)
        
        for rel in field.relationships:
            G.add_edge(rel.source_id, rel.target_id, created_at=rel.created_at)
        
        # Try to identify diverging areas using community detection
        try:
            # Use Louvain method for community detection
            import community as community_louvain
            partition = community_louvain.best_partition(G)
            
            # Group nodes by community
            communities = defaultdict(list)
            for node, community_id in partition.items():
                communities[community_id].append(node)
            
            # Calculate centroids and evolution rates for communities
            community_stats = {}
            for comm_id, nodes in communities.items():
                if len(nodes) < 3:  # Skip very small communities
                    continue
                    
                # Get entities in this community
                comm_entities = [e for e in field.entities if e.id in nodes]
                
                # Skip if no entities found
                if not comm_entities:
                    continue
                
                # Calculate average creation date
                avg_created = sum((e.created_at - datetime(2020, 1, 1)).days 
                                 for e in comm_entities) / len(comm_entities)
                
                # Calculate recent activity (entities updated in last 180 days)
                recent_threshold = datetime.now() - timedelta(days=180)
                recent_activity = sum(1 for e in comm_entities 
                                    if e.updated_at and e.updated_at >= recent_threshold) / len(comm_entities)
                
                # Store community stats
                community_stats[comm_id] = {
                    'size': len(nodes),
                    'avg_created': avg_created,
                    'recent_activity': recent_activity,
                    'entities': comm_entities
                }
            
            # Identify diverging communities (recent, active, but isolated)
            all_communities = list(community_stats.items())
            all_communities.sort(key=lambda x: x[1]['size'], reverse=True)
            
            # Use the largest community as the reference
            if not all_communities:
                return gaps
                
            reference_comm = all_communities[0][1]
            
            for comm_id, stats in all_communities[1:]:  # Skip the largest (reference) community
                # Check if community is recent and active
                if stats['recent_activity'] > 0.3:  # At least 30% of entities recently active
                    # Calculate isolation from reference community
                    comm_nodes = set(communities[comm_id])
                    ref_nodes = set(communities[all_communities[0][0]])
                    
                    # Count edges between this community and reference
                    cross_edges = sum(1 for u, v in G.edges() 
                                   if (u in comm_nodes and v in ref_nodes) or 
                                      (u in ref_nodes and v in comm_nodes))
                    
                    # Calculate isolation score (lower value = more isolated)
                    isolation = cross_edges / (len(comm_nodes) * len(ref_nodes))
                    isolation_score = 1 - min(1, isolation * 1000)  # Convert to 0-1 scale
                    
                    if isolation_score > 0.7:  # Considerably isolated
                        # Find the most central entity in this community
                        subgraph = G.subgraph(comm_nodes)
                        try:
                            central_node = max(subgraph.nodes(), 
                                            key=lambda n: nx.degree_centrality(subgraph)[n])
                            central_entity = next((e for e in field.entities if e.id == central_node), None)
                            
                            if central_entity:
                                # Calculate scores
                                gap_score = isolation_score * 0.7 + stats['recent_activity'] * 0.3
                                potential_score = 0.5 + 0.5 * min(1, stats['size'] / 10)
                                confidence = 0.6  # Default for diverging communities
                                
                                # Get top entities from this community
                                related_entities = [e.name for e in stats['entities'][:5]]
                                
                                # Create gap
                                gap = KnowledgeGap(
                                    name=f"Diverging research: {central_entity.name}",
                                    description=f"Active research area around {central_entity.name} "
                                               f"is diverging from the main field with limited integration",
                                    related_entities=related_entities,
                                    gap_score=gap_score,
                                    potential_score=potential_score,
                                    confidence=confidence
                                )
                                gaps.append(gap)
                        except:
                            continue
        except ImportError:
            # Fall back to a simpler approach if community detection is not available
            pass
        
        return gaps
    
    def _calculate_entity_recency(self, entity):
        """Calculate a recency score for an entity (0-1, higher = more recent)."""
        days_since_creation = (datetime.now() - entity.created_at).days
        if entity.updated_at:
            days_since_update = (datetime.now() - entity.updated_at).days
            days_since_activity = min(days_since_creation, days_since_update)
        else:
            days_since_activity = days_since_creation
            
        # Convert to a score between 0 and 1 (exponential decay)
        recency_score = np.exp(-days_since_activity / 365)  # 1 year half-life
        return recency_score
    
    def predict_entity_evolution(self, 
                               entity_id: str,
                               prediction_window: Tuple[datetime, datetime],
                               max_branches: int = 3) -> Dict[str, Any]:
        """
        Predict potential evolution paths for a specific entity.
        
        Args:
            entity_id: ID of the entity to predict evolution for
            prediction_window: (start_date, end_date) for the prediction
            max_branches: Maximum number of evolution branches to predict
            
        Returns:
            Dictionary with prediction results
        """
        # Get the entity
        entity = self.query_engine.get_entity_by_id(entity_id)
        if not entity:
            raise ValueError(f"Entity with ID {entity_id} not found")
            
        # Get evolution history
        evolution_tree = self.query_engine.trace_concept_evolution(entity_id)
        if not evolution_tree:
            # No evolution history, use a single-branch approach
            return self._predict_simple_evolution(entity, prediction_window, max_branches)
            
        # With evolution history, use a more sophisticated approach
        return self._predict_multi_branch_evolution(entity, evolution_tree, prediction_window, max_branches)
    
    def _predict_simple_evolution(self, entity, prediction_window, max_branches):
        """Predict evolution for an entity without existing evolution history."""
        start_date, end_date = prediction_window
        
        # Create a basic prediction with potential branches
        prediction = {
            "entity_name": entity.name,
            "entity_id": entity.id,
            "start_date": start_date,
            "end_date": end_date,
            "branches": []
        }
        
        # Determine possible evolution directions based on entity type
        possible_directions = self._determine_evolution_directions(entity)
        
        # Create predictions for top directions (up to max_branches)
        for direction in possible_directions[:max_branches]:
            branch = {
                "name": f"{entity.name} {direction['suffix']}",
                "direction": direction["type"],
                "confidence": direction["confidence"],
                "estimated_date": start_date + timedelta(days=int(direction["time_estimate"])),
                "description": direction["description"].format(entity_name=entity.name)
            }
            prediction["branches"].append(branch)
            
        # Sort branches by confidence
        prediction["branches"].sort(key=lambda x: x["confidence"], reverse=True)
        
        return prediction
    
    def _predict_multi_branch_evolution(self, entity, evolution_tree, prediction_window, max_branches):
        """Predict evolution for an entity with existing evolution history."""
        start_date, end_date = prediction_window
        
        # Create prediction structure
        prediction = {
            "entity_name": entity.name,
            "entity_id": entity.id,
            "start_date": start_date,
            "end_date": end_date,
            "branches": []
        }
        
        # Analyze the evolution pattern
        pattern = self.analyzer.identify_evolution_patterns(entity.id)
        prediction["pattern"] = pattern.value if pattern else "unknown"
        
        # Determine branch count based on historical pattern
        if pattern in [EntityEvolutionPattern.LINEAR, EntityEvolutionPattern.INCREMENTAL]:
            target_branches = 1
        elif pattern in [EntityEvolutionPattern.BRANCHING, EntityEvolutionPattern.DIVERGENT]:
            target_branches = min(max_branches, 3)  # Up to 3 branches for branching patterns
        else:
            target_branches = min(max_branches, 2)  # Default to 2 branches
            
        # Create evolution branches
        directions = self._determine_evolution_directions(entity)
        
        # Adjust directions based on historical pattern
        adjusted_directions = self._adjust_directions_by_pattern(directions, pattern)
        
        # Create prediction branches
        for direction in adjusted_directions[:target_branches]:
            # Estimate date based on historical timing
            avg_time_between_versions = self._calculate_avg_evolution_time(evolution_tree)
            if avg_time_between_versions:
                time_estimate = avg_time_between_versions
            else:
                time_estimate = direction["time_estimate"]
                
            estimated_date = start_date + timedelta(days=int(time_estimate))
            
            # Adjust name based on naming patterns in the evolution tree
            name_pattern = self._identify_naming_pattern(evolution_tree)
            if name_pattern:
                new_name = self._generate_name_from_pattern(entity.name, name_pattern, direction)
            else:
                new_name = f"{entity.name} {direction['suffix']}"
                
            branch = {
                "name": new_name,
                "direction": direction["type"],
                "confidence": direction["confidence"],
                "estimated_date": estimated_date,
                "description": direction["description"].format(entity_name=entity.name)
            }
            prediction["branches"].append(branch)
            
        return prediction
    
    def _determine_evolution_directions(self, entity):
        """
        Determine possible evolution directions based on entity type.
        
        Returns a list of possible directions with their properties.
        """
        # Start with some generic directions
        directions = [
            {
                "type": "incremental",
                "suffix": "Next",
                "confidence": 0.7,
                "time_estimate": 365,  # days
                "description": "Incremental improvement of {entity_name} with minor enhancements"
            },
            {
                "type": "major_update",
                "suffix": "2.0",
                "confidence": 0.5,
                "time_estimate": 730,  # days
                "description": "Major update to {entity_name} with significant new capabilities"
            }
        ]
        
        # Add type-specific directions
        if hasattr(entity, 'entity_type'):
            if entity.entity_type == 'AIModel':
                directions.extend([
                    {
                        "type": "scaling",
                        "suffix": "Large",
                        "confidence": 0.6,
                        "time_estimate": 365,
                        "description": "Scaled-up version of {entity_name} with more parameters"
                    },
                    {
                        "type": "efficiency",
                        "suffix": "Efficient",
                        "confidence": 0.5,
                        "time_estimate": 456,
                        "description": "More efficient version of {entity_name} requiring less compute"
                    },
                    {
                        "type": "multimodal",
                        "suffix": "Multimodal",
                        "confidence": 0.4,
                        "time_estimate": 548,
                        "description": "Multimodal extension of {entity_name} supporting additional input types"
                    }
                ])
            elif entity.entity_type == 'Algorithm':
                directions.extend([
                    {
                        "type": "parallelization",
                        "suffix": "Parallel",
                        "confidence": 0.6,
                        "time_estimate": 274,
                        "description": "Parallelized version of {entity_name} for distributed computation"
                    },
                    {
                        "type": "approximation",
                        "suffix": "Approximate",
                        "confidence": 0.4,
                        "time_estimate": 365,
                        "description": "Approximate version of {entity_name} trading accuracy for speed"
                    }
                ])
            elif entity.entity_type == 'Dataset':
                directions.extend([
                    {
                        "type": "expansion",
                        "suffix": "Extended",
                        "confidence": 0.7,
                        "time_estimate": 183,
                        "description": "Expanded version of {entity_name} with more samples"
                    },
                    {
                        "type": "cleaning",
                        "suffix": "Clean",
                        "confidence": 0.5,
                        "time_estimate": 274,
                        "description": "Cleaned version of {entity_name} with improved data quality"
                    }
                ])
        
        # Adjust confidence based on entity attributes if available
        if hasattr(entity, 'attributes'):
            if 'popularity' in entity.attributes:
                # More popular entities are more likely to evolve
                popularity = float(entity.attributes['popularity'])
                for direction in directions:
                    direction['confidence'] = min(0.9, direction['confidence'] * (1 + popularity / 10))
        
        return directions
    
    def _adjust_directions_by_pattern(self, directions, pattern):
        """Adjust evolution direction probabilities based on historical pattern."""
        if not pattern:
            return directions
            
        adjusted = directions.copy()
        
        # Adjust confidences based on pattern
        if pattern == EntityEvolutionPattern.LINEAR:
            # Favor incremental updates
            for direction in adjusted:
                if direction["type"] == "incremental":
                    direction["confidence"] = min(0.9, direction["confidence"] * 1.3)
                else:
                    direction["confidence"] *= 0.8
                    
        elif pattern == EntityEvolutionPattern.BRANCHING:
            # Boost confidence for multiple directions
            for direction in adjusted:
                direction["confidence"] = min(0.9, direction["confidence"] * 1.1)
                
        elif pattern == EntityEvolutionPattern.DISRUPTIVE:
            # Favor major updates
            for direction in adjusted:
                if direction["type"] == "major_update":
                    direction["confidence"] = min(0.9, direction["confidence"] * 1.5)
                    
        elif pattern == EntityEvolutionPattern.INCREMENTAL:
            # Strong favor for incremental updates
            for direction in adjusted:
                if direction["type"] == "incremental":
                    direction["confidence"] = min(0.9, direction["confidence"] * 1.5)
                else:
                    direction["confidence"] *= 0.7
        
        # Sort by adjusted confidence
        adjusted.sort(key=lambda x: x["confidence"], reverse=True)
        return adjusted
    
    def _calculate_avg_evolution_time(self, evolution_tree):
        """Calculate average time between evolution steps."""
        # This requires temporal data for all entities in the tree
        # In a real system, you would retrieve this from the database
        
        # Placeholder for demonstration
        return 365  # Default to 1 year
    
    def _identify_naming_pattern(self, evolution_tree):
        """Identify naming patterns in an evolution tree."""
        # Placeholder - in a real system, you would analyze actual entity names
        return None
    
    def _generate_name_from_pattern(self, base_name, pattern, direction):
        """Generate a new name based on identified pattern and direction."""
        # Placeholder - in a real system this would use the pattern
        return f"{base_name} {direction['suffix']}"