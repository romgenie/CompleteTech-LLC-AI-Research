"""
Unit tests for the Evolution Predictor module.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from knowledge_graph_system.temporal_evolution.prediction.evolution_predictor import (
    EvolutionPredictor, EvolutionTrajectory, KnowledgeGap
)
from knowledge_graph_system.temporal_evolution.analyzer.evolution_analyzer import (
    EvolutionAnalyzer, ResearchField, TrendDirection, EntityEvolutionPattern
)
from knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)


class TestEvolutionPredictor(unittest.TestCase):
    """Tests for the EvolutionPredictor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects
        self.mock_query_engine = MagicMock()
        self.mock_analyzer = MagicMock()
        
        # Create the predictor
        self.predictor = EvolutionPredictor(self.mock_query_engine, self.mock_analyzer)
        
        # Create a sample research field
        self.field = ResearchField("AI Research")
        self.mock_analyzer.research_fields = {"AI Research": self.field}
        
        # Add sample entities to the field
        now = datetime.now()
        
        # Create entities with different creation dates
        entity1 = TemporalEntityBase(
            id="1",
            name="GPT-3",
            entity_type="AIModel",
            created_at=now - timedelta(days=500),
            updated_at=now - timedelta(days=100)
        )
        entity2 = TemporalEntityBase(
            id="2",
            name="GPT-4",
            entity_type="AIModel",
            created_at=now - timedelta(days=200),
            updated_at=now - timedelta(days=50)
        )
        
        # Add entities to the field
        self.field.entities = [entity1, entity2]
        
        # Add activity history data
        self.field.activity_history = {
            now - timedelta(days=360): 5,
            now - timedelta(days=270): 8,
            now - timedelta(days=180): 12,
            now - timedelta(days=90): 15,
            now - timedelta(days=30): 20
        }
    
    def test_predict_field_trajectory_linear(self):
        """Test predicting field trajectory with linear model."""
        # Define prediction window
        now = datetime.now()
        start_date = now + timedelta(days=30)
        end_date = now + timedelta(days=180)
        prediction_window = (start_date, end_date)
        
        # Call predict_field_trajectory
        trajectory = self.predictor.predict_field_trajectory(
            field_name="AI Research",
            prediction_window=prediction_window,
            model_type="linear"
        )
        
        # Check the result
        self.assertIsInstance(trajectory, EvolutionTrajectory)
        self.assertEqual(trajectory.name, "AI Research")
        self.assertEqual(trajectory.start_date, start_date)
        self.assertEqual(trajectory.end_date, end_date)
        self.assertEqual(len(trajectory.prediction_points), 10)  # Default num_points
    
    def test_identify_knowledge_gaps(self):
        """Test identifying knowledge gaps."""
        # Mock entity graph methods
        with patch('networkx.DiGraph'), \
             patch.object(self.predictor, '_identify_missing_connections', return_value=[]), \
             patch.object(self.predictor, '_identify_isolated_clusters', return_value=[]), \
             patch.object(self.predictor, '_identify_stagnant_trending_entities', return_value=[]), \
             patch.object(self.predictor, '_identify_diverging_areas', return_value=[]):
            
            # Create a sample gap to return
            gap = KnowledgeGap(
                name="Test Gap",
                description="A test gap",
                related_entities=["Entity1", "Entity2"],
                gap_score=0.8,
                potential_score=0.7,
                confidence=0.6
            )
            
            # Mock the first method to return this gap
            self.predictor._identify_missing_connections = MagicMock(return_value=[gap])
            
            # Call identify_knowledge_gaps
            gaps = self.predictor.identify_knowledge_gaps(
                field_name="AI Research",
                min_gap_score=0.5,
                max_gaps=5
            )
            
            # Check the result
            self.assertEqual(len(gaps), 1)
            self.assertEqual(gaps[0].name, "Test Gap")
            self.assertEqual(gaps[0].gap_score, 0.8)
    
    def test_predict_entity_evolution_simple(self):
        """Test predicting entity evolution with simple approach."""
        # Mock get_entity_by_id to return an entity
        now = datetime.now()
        entity = TemporalEntityBase(
            id="1",
            name="GPT-3",
            entity_type="AIModel",
            created_at=now - timedelta(days=500),
            updated_at=now - timedelta(days=100)
        )
        self.mock_query_engine.get_entity_by_id.return_value = entity
        
        # Mock trace_concept_evolution to return empty (no evolution history)
        self.mock_query_engine.trace_concept_evolution.return_value = {}
        
        # Define prediction window
        start_date = now + timedelta(days=30)
        end_date = now + timedelta(days=180)
        prediction_window = (start_date, end_date)
        
        # Mock _predict_simple_evolution
        self.predictor._predict_simple_evolution = MagicMock(return_value={
            "entity_name": "GPT-3",
            "entity_id": "1",
            "branches": [
                {
                    "name": "GPT-3 Next",
                    "direction": "incremental",
                    "confidence": 0.7,
                    "estimated_date": start_date + timedelta(days=90)
                }
            ]
        })
        
        # Call predict_entity_evolution
        prediction = self.predictor.predict_entity_evolution(
            entity_id="1",
            prediction_window=prediction_window,
            max_branches=3
        )
        
        # Check the result
        self.assertEqual(prediction["entity_name"], "GPT-3")
        self.assertEqual(len(prediction["branches"]), 1)
        self.assertEqual(prediction["branches"][0]["name"], "GPT-3 Next")
    
    def test_predict_entity_evolution_with_history(self):
        """Test predicting entity evolution with evolution history."""
        # Mock get_entity_by_id to return an entity
        now = datetime.now()
        entity = TemporalEntityBase(
            id="1",
            name="GPT-3",
            entity_type="AIModel",
            created_at=now - timedelta(days=500),
            updated_at=now - timedelta(days=100)
        )
        self.mock_query_engine.get_entity_by_id.return_value = entity
        
        # Mock trace_concept_evolution to return a history
        self.mock_query_engine.trace_concept_evolution.return_value = {
            "1": ["2"],  # Entity 1 evolved into Entity 2
            "2": []      # Entity 2 has no descendants yet
        }
        
        # Mock identify_evolution_patterns
        self.mock_analyzer.identify_evolution_patterns.return_value = EntityEvolutionPattern.LINEAR
        
        # Define prediction window
        start_date = now + timedelta(days=30)
        end_date = now + timedelta(days=180)
        prediction_window = (start_date, end_date)
        
        # Mock _predict_multi_branch_evolution
        self.predictor._predict_multi_branch_evolution = MagicMock(return_value={
            "entity_name": "GPT-3",
            "entity_id": "1",
            "pattern": "linear",
            "branches": [
                {
                    "name": "GPT-3 Next",
                    "direction": "incremental",
                    "confidence": 0.8,
                    "estimated_date": start_date + timedelta(days=90)
                }
            ]
        })
        
        # Call predict_entity_evolution
        prediction = self.predictor.predict_entity_evolution(
            entity_id="1",
            prediction_window=prediction_window,
            max_branches=3
        )
        
        # Check the result
        self.assertEqual(prediction["entity_name"], "GPT-3")
        self.assertEqual(prediction["pattern"], "linear")
        self.assertEqual(len(prediction["branches"]), 1)
        self.assertEqual(prediction["branches"][0]["name"], "GPT-3 Next")
    
    def test_evolution_trajectory_methods(self):
        """Test EvolutionTrajectory class methods."""
        # Create a trajectory with a clear trend
        now = datetime.now()
        start_date = now
        end_date = now + timedelta(days=100)
        
        # Create points with a clear increasing trend
        points = [
            (now + timedelta(days=0), 10),
            (now + timedelta(days=25), 15),
            (now + timedelta(days=50), 25),
            (now + timedelta(days=75), 40),
            (now + timedelta(days=100), 60)
        ]
        
        trajectory = EvolutionTrajectory(
            name="Test Trajectory",
            start_date=start_date,
            end_date=end_date,
            prediction_points=points,
            confidence=0.8
        )
        
        # Test get_average_trend
        trend = trajectory.get_average_trend()
        self.assertGreater(trend, 0)  # Should be positive for increasing trend
        
        # Test get_trend_direction
        direction = trajectory.get_trend_direction()
        self.assertEqual(direction, TrendDirection.ACCELERATING)
        
        # Check peaks and valleys
        self.assertEqual(len(trajectory.peaks), 0)  # No internal peaks in a monotonic function
        self.assertEqual(len(trajectory.valleys), 0)  # No internal valleys in a monotonic function


if __name__ == '__main__':
    unittest.main()