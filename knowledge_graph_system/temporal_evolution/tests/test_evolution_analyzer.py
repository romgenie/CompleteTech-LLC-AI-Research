"""
Unit tests for the Evolution Analyzer module.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from knowledge_graph_system.temporal_evolution.analyzer.evolution_analyzer import (
    EvolutionAnalyzer, ResearchField, TrendDirection, EntityEvolutionPattern
)
from knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)


class TestEvolutionAnalyzer(unittest.TestCase):
    """Tests for the EvolutionAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock query engine
        self.mock_query_engine = MagicMock()
        
        # Create the analyzer
        self.analyzer = EvolutionAnalyzer(self.mock_query_engine)
        
        # Create a sample research field
        self.field = ResearchField("AI Research")
        self.analyzer.research_fields["AI Research"] = self.field
        
        # Add sample entities to the field
        now = datetime.now()
        
        # Create entities with different creation dates
        entity1 = TemporalEntityBase(
            name="GPT-3",
            entity_type="AIModel",
            created_at=now - timedelta(days=500),
            updated_at=now - timedelta(days=100)
        )
        entity2 = TemporalEntityBase(
            name="GPT-4",
            entity_type="AIModel",
            created_at=now - timedelta(days=200),
            updated_at=now - timedelta(days=50)
        )
        entity3 = TemporalEntityBase(
            name="DALL-E",
            entity_type="AIModel",
            created_at=now - timedelta(days=300),
            updated_at=None
        )
        
        # Add entities to the field
        self.field.entities = [entity1, entity2, entity3]
        
        # Create relationships between entities
        rel1 = TemporalRelationshipBase(
            source_id="1",
            target_id="2",
            type="EVOLVED_INTO",
            created_at=now - timedelta(days=200)
        )
        rel2 = TemporalRelationshipBase(
            source_id="1",
            target_id="3",
            type="INSPIRED",
            created_at=now - timedelta(days=300)
        )
        
        # Add relationships to the field
        self.field.relationships = [rel1, rel2]
        
        # Add activity history data
        self.field.activity_history = {
            now - timedelta(days=360): 5,
            now - timedelta(days=270): 8,
            now - timedelta(days=180): 12,
            now - timedelta(days=90): 15,
            now - timedelta(days=30): 20
        }
    
    def test_define_research_field(self):
        """Test defining a research field."""
        # Mock the query methods
        self.mock_query_engine.query_entities.return_value = [
            TemporalEntityBase(name="Test Entity", entity_type="Test")
        ]
        self.mock_query_engine.query_relationships.return_value = [
            TemporalRelationshipBase(source_id="1", target_id="2", type="TEST")
        ]
        
        # Define a new research field
        field = self.analyzer.define_research_field(
            name="Test Field",
            entity_types=["Test"],
            relationship_types=["TEST"],
            keywords=["test"]
        )
        
        # Check if the field was created correctly
        self.assertEqual(field.name, "Test Field")
        self.assertEqual(len(field.entities), 1)
        self.assertEqual(len(field.relationships), 1)
        self.assertEqual(field.entities[0].name, "Test Entity")
    
    def test_analyze_activity_trend_accelerating(self):
        """Test analyzing activity trend with accelerating pattern."""
        # Replace activity history with accelerating pattern
        now = datetime.now()
        self.field.activity_history = {
            now - timedelta(days=270): 5,
            now - timedelta(days=180): 8,
            now - timedelta(days=90): 12,
            now - timedelta(days=30): 18
        }
        
        # Analyze trend
        trend, data = self.analyzer.analyze_activity_trend("AI Research")
        
        # Check the result
        self.assertEqual(trend, TrendDirection.ACCELERATING)
        self.assertEqual(len(data), 4)
    
    def test_analyze_activity_trend_declining(self):
        """Test analyzing activity trend with declining pattern."""
        # Replace activity history with declining pattern
        now = datetime.now()
        self.field.activity_history = {
            now - timedelta(days=270): 20,
            now - timedelta(days=180): 15,
            now - timedelta(days=90): 10,
            now - timedelta(days=30): 5
        }
        
        # Analyze trend
        trend, data = self.analyzer.analyze_activity_trend("AI Research")
        
        # Check the result
        self.assertEqual(trend, TrendDirection.DECLINING)
        self.assertEqual(len(data), 4)
    
    def test_detect_stagnant_areas(self):
        """Test detecting stagnant research areas."""
        # Create a stagnant field
        stagnant_field = ResearchField("Stagnant Field")
        
        # Add old entities with no recent updates
        now = datetime.now()
        entity = TemporalEntityBase(
            name="Old Entity",
            entity_type="Test",
            created_at=now - timedelta(days=500),
            updated_at=None
        )
        stagnant_field.entities = [entity]
        
        # Add old relationships
        rel = TemporalRelationshipBase(
            source_id="1",
            target_id="2",
            type="TEST",
            created_at=now - timedelta(days=500)
        )
        stagnant_field.relationships = [rel]
        
        # Add to analyzer
        self.analyzer.research_fields["Stagnant Field"] = stagnant_field
        
        # Detect stagnant areas
        stagnant_fields = self.analyzer.detect_stagnant_areas(threshold_days=365, activity_threshold=2)
        
        # Check the result
        self.assertIn("Stagnant Field", stagnant_fields)
        self.assertNotIn("AI Research", stagnant_fields)  # Should not be stagnant
    
    def test_identify_cyclical_patterns(self):
        """Test identifying cyclical patterns in research activity."""
        # Mock the query methods and entity objects for more complex testing
        # This is just a basic test of method functionality
        
        with patch('knowledge_graph_system.temporal_evolution.analyzer.evolution_analyzer.ResearchField.update_activity_metrics'):
            # Test method call
            patterns = self.analyzer.identify_cyclical_patterns(
                field_name="AI Research",
                time_period=90,
                num_periods=8,
                similarity_threshold=0.5
            )
            
            # Basic check that method runs
            self.assertIsInstance(patterns, list)
    
    def test_field_not_found(self):
        """Test error handling when a field is not found."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_activity_trend("NonexistentField")
    
    def test_identify_evolution_patterns(self):
        """Test identifying evolution patterns for an entity."""
        # Mock trace_concept_evolution to return a simple tree
        self.mock_query_engine.trace_concept_evolution.return_value = {
            "1": ["2", "3"],  # Node 1 has two children
            "2": ["4"],       # Node 2 has one child
            "3": [],          # Node 3 has no children
            "4": []           # Node 4 has no children
        }
        
        # Test with a branching pattern
        pattern = self.analyzer.identify_evolution_patterns("1")
        self.assertEqual(pattern, EntityEvolutionPattern.BRANCHING)
        
        # Test with a linear pattern
        self.mock_query_engine.trace_concept_evolution.return_value = {
            "1": ["2"],
            "2": ["3"],
            "3": []
        }
        
        pattern = self.analyzer.identify_evolution_patterns("1")
        self.assertEqual(pattern, EntityEvolutionPattern.LINEAR)
        
        # Test with an empty tree
        self.mock_query_engine.trace_concept_evolution.return_value = {}
        pattern = self.analyzer.identify_evolution_patterns("1")
        self.assertIsNone(pattern)


if __name__ == '__main__':
    unittest.main()