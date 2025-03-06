"""
Unit tests for the relationship extraction component.

This module contains tests for the Relationship class, RelationshipExtractor,
PatternRelationshipExtractor, AIRelationshipExtractor, CombinedRelationshipExtractor,
and RelationshipExtractorFactory classes, focusing on testing relationship creation,
extraction, filtering, and factory functionality.
"""

import pytest

# Mark all tests in this module as unit tests and relationship related tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.relationship,
    pytest.mark.fast
]
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.pattern_extractor import PatternRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.ai_extractor import AIRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.combined_extractor import CombinedRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory


class TestRelationship:
    """Tests for the Relationship class."""
    
    def test_relationship_creation(self):
        """Test creating a Relationship with proper attributes."""
        source = Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1")
        target = Entity(text="Google", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=30, end_pos=36, id="e2")
        
        relationship = Relationship(
            source=source,
            target=target,
            relation_type=RelationType.DEVELOPED_BY,
            confidence=0.85,
            context="BERT was developed by Google",
            metadata={"source": "test"},
            id="r1"
        )
        
        assert relationship.id == "r1"
        assert relationship.source == source
        assert relationship.target == target
        assert relationship.relation_type == RelationType.DEVELOPED_BY
        assert relationship.confidence == 0.85
        assert relationship.context == "BERT was developed by Google"
        assert relationship.metadata == {"source": "test"}
    
    def test_relationship_to_dict(self):
        """Test conversion of Relationship to dictionary."""
        source = Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1")
        target = Entity(text="Google", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=30, end_pos=36, id="e2")
        
        relationship = Relationship(
            source=source,
            target=target,
            relation_type=RelationType.DEVELOPED_BY,
            confidence=0.85,
            context="BERT was developed by Google",
            metadata={"source": "test"},
            id="r1"
        )
        
        relationship_dict = relationship.to_dict()
        
        assert relationship_dict["id"] == "r1"
        assert relationship_dict["relation_type"] == "developed_by"
        assert relationship_dict["confidence"] == 0.85
        assert relationship_dict["context"] == "BERT was developed by Google"
        assert relationship_dict["source"]["text"] == "BERT"
        assert relationship_dict["target"]["text"] == "Google"
        assert relationship_dict["metadata"] == {"source": "test"}
    
    def test_relationship_from_dict(self):
        """Test creation of Relationship from dictionary."""
        relationship_dict = {
            "id": "r1",
            "source": {
                "id": "e1",
                "text": "BERT",
                "type": "model",
                "confidence": 0.95,
                "start_pos": 10,
                "end_pos": 14,
                "metadata": {}
            },
            "target": {
                "id": "e2",
                "text": "Google",
                "type": "organization",
                "confidence": 0.9,
                "start_pos": 30,
                "end_pos": 36,
                "metadata": {}
            },
            "relation_type": "developed_by",
            "confidence": 0.85,
            "context": "BERT was developed by Google",
            "metadata": {"source": "test"}
        }
        
        relationship = Relationship.from_dict(relationship_dict)
        
        assert relationship.id == "r1"
        assert relationship.source.text == "BERT"
        assert relationship.target.text == "Google"
        assert relationship.relation_type == RelationType.DEVELOPED_BY
        assert relationship.confidence == 0.85
        assert relationship.context == "BERT was developed by Google"
        assert relationship.metadata == {"source": "test"}
    
    def test_relationship_str_representation(self):
        """Test string representation of Relationship."""
        source = Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1")
        target = Entity(text="Google", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=30, end_pos=36, id="e2")
        
        relationship = Relationship(
            source=source,
            target=target,
            relation_type=RelationType.DEVELOPED_BY,
            confidence=0.85,
            context="BERT was developed by Google",
            id="r1"
        )
        
        relationship_str = str(relationship)
        
        assert "BERT" in relationship_str
        assert "Google" in relationship_str
        assert "developed_by" in relationship_str
        assert "0.85" in relationship_str


class TestRelationshipExtractor:
    """Tests for the RelationshipExtractor base class."""
    
    def test_base_extractor_creation(self):
        """Test creating a base RelationshipExtractor."""
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        assert extractor is not None
    
    def test_get_entity_pair_context(self):
        """Test getting context for an entity pair."""
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Create test entities
        source = Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1")
        target = Entity(text="Google", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=30, end_pos=36, id="e2")
        
        # Create test text
        text = "The BERT model was developed by Google AI researchers."
        
        # Get context
        context = extractor.get_entity_pair_context(text, source, target)
        
        # Verify context contains both entities
        assert "BERT" in context
        assert "Google" in context
        
        # Verify context includes text between entities
        assert "was developed by" in context
    
    def test_find_entity_pairs(self):
        """Test finding entity pairs based on proximity."""
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Create test entities
        entities = [
            Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1"),
            Entity(text="Google", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=30, end_pos=36, id="e2"),
            Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.95, start_pos=100, end_pos=105, id="e3"),
            Entity(text="OpenAI", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=200, end_pos=206, id="e4")
        ]
        
        # Find pairs with max distance of 50
        pairs = extractor.find_entity_pairs(entities, max_distance=50)
        
        # Should only find BERT-Google pair
        assert len(pairs) == 2  # Both directions (BERT→Google and Google→BERT)
        
        # Check that BERT-Google pair was found in both directions
        bert_google_found = False
        google_bert_found = False
        
        for source, target in pairs:
            if source.text == "BERT" and target.text == "Google":
                bert_google_found = True
            elif source.text == "Google" and target.text == "BERT":
                google_bert_found = True
        
        assert bert_google_found
        assert google_bert_found
        
        # Find pairs with max distance of 150
        pairs = extractor.find_entity_pairs(entities, max_distance=150)
        
        # Should find both BERT-Google and GPT-3-OpenAI pairs (4 pairs total with both directions)
        assert len(pairs) >= 4
    
    def test_filter_relationships(self):
        """Test filtering relationships by confidence and type."""
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Create test entities
        source1 = Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1")
        target1 = Entity(text="Google", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=30, end_pos=36, id="e2")
        source2 = Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.95, start_pos=100, end_pos=105, id="e3")
        target2 = Entity(text="OpenAI", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=200, end_pos=206, id="e4")
        
        # Create test relationships
        relationships = [
            Relationship(
                source=source1, 
                target=target1, 
                relation_type=RelationType.DEVELOPED_BY, 
                confidence=0.9, 
                context="BERT was developed by Google", 
                id="r1"
            ),
            Relationship(
                source=source2, 
                target=target2, 
                relation_type=RelationType.DEVELOPED_BY, 
                confidence=0.7, 
                context="GPT-3 was developed by OpenAI", 
                id="r2"
            ),
            Relationship(
                source=source1, 
                target=source2, 
                relation_type=RelationType.OUTPERFORMS, 
                confidence=0.8, 
                context="GPT-3 outperforms BERT", 
                id="r3"
            )
        ]
        
        # Filter by confidence
        high_confidence = extractor.filter_relationships(relationships, min_confidence=0.8)
        assert len(high_confidence) == 2
        assert all(r.confidence >= 0.8 for r in high_confidence)
        
        # Filter by type
        developed_by = extractor.filter_relationships(
            relationships, 
            relation_types=[RelationType.DEVELOPED_BY]
        )
        assert len(developed_by) == 2
        assert all(r.relation_type == RelationType.DEVELOPED_BY for r in developed_by)
        
        # Filter by both
        high_confidence_developed_by = extractor.filter_relationships(
            relationships, 
            min_confidence=0.8, 
            relation_types=[RelationType.DEVELOPED_BY]
        )
        assert len(high_confidence_developed_by) == 1
        assert high_confidence_developed_by[0].id == "r1"


class TestPatternRelationshipExtractor:
    """Tests for the PatternRelationshipExtractor class."""
    
    def test_pattern_extractor_creation(self):
        """Test creating a PatternRelationshipExtractor."""
        extractor = PatternRelationshipExtractor()
        assert extractor is not None
        assert hasattr(extractor, "patterns")
    
    def test_add_pattern(self):
        """Test adding a custom pattern."""
        extractor = PatternRelationshipExtractor()
        
        # Add a custom pattern
        pattern = r"(\w+) is based on (\w+)"
        extractor.add_pattern(RelationType.BASED_ON, pattern)
        
        # Verify pattern was added
        assert RelationType.BASED_ON in extractor.patterns
        
        # Count patterns for this relation type
        relation_patterns = extractor.patterns[RelationType.BASED_ON]
        assert len(relation_patterns) > 0
    
    @patch.object(PatternRelationshipExtractor, "extract_relationships")
    def test_extract_with_patterns(self, mock_extract):
        """Test extracting relationships with patterns."""
        # Set up mock
        source = Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=14, id="e1")
        target = Entity(text="Transformer", type=EntityType.ARCHITECTURE, confidence=0.9, start_pos=40, end_pos=51, id="e2")
        
        mock_extract.return_value = [
            Relationship(
                source=source,
                target=target,
                relation_type=RelationType.BASED_ON,
                confidence=0.85,
                context="BERT is based on the Transformer architecture",
                id="r1"
            )
        ]
        
        # Create extractor and extract relationships
        extractor = PatternRelationshipExtractor()
        text = "BERT is based on the Transformer architecture"
        entities = [source, target]
        relationships = extractor.extract_relationships(text, entities)
        
        # Verify results
        mock_extract.assert_called_once_with(text, entities)
        assert len(relationships) == 1
        assert relationships[0].source.text == "BERT"
        assert relationships[0].target.text == "Transformer"
        assert relationships[0].relation_type == RelationType.BASED_ON


class TestAIRelationshipExtractor:
    """Tests for the AIRelationshipExtractor class."""
    
    def test_ai_extractor_creation(self):
        """Test creating an AIRelationshipExtractor."""
        extractor = AIRelationshipExtractor()
        assert extractor is not None
    
    @patch.object(AIRelationshipExtractor, "extract_relationships")
    def test_ai_relationship_extraction(self, mock_extract):
        """Test extracting AI-specific relationships."""
        # Set up mock
        source = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, id="e1")
        target1 = Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.9, start_pos=30, end_pos=34, id="e2")
        target2 = Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.9, start_pos=60, end_pos=65, id="e3")
        
        mock_extract.return_value = [
            Relationship(
                source=source,
                target=target1,
                relation_type=RelationType.EVALUATED_ON,
                confidence=0.8,
                context="GPT-4 was evaluated on the MMLU benchmark",
                id="r1"
            ),
            Relationship(
                source=source,
                target=target2,
                relation_type=RelationType.OUTPERFORMS,
                confidence=0.85,
                context="GPT-4 outperforms GPT-3 on most tasks",
                id="r2"
            )
        ]
        
        # Create extractor and extract relationships
        extractor = AIRelationshipExtractor()
        text = "GPT-4 was evaluated on the MMLU benchmark and outperforms GPT-3 on most tasks."
        entities = [source, target1, target2]
        relationships = extractor.extract_relationships(text, entities)
        
        # Verify results
        mock_extract.assert_called_once_with(text, entities)
        assert len(relationships) == 2
        
        # Check relationship types
        relationship_types = [r.relation_type for r in relationships]
        assert RelationType.EVALUATED_ON in relationship_types
        assert RelationType.OUTPERFORMS in relationship_types


class TestCombinedRelationshipExtractor:
    """Tests for the CombinedRelationshipExtractor class."""
    
    def test_combined_extractor_creation(self):
        """Test creating a CombinedRelationshipExtractor."""
        pattern_extractor = PatternRelationshipExtractor()
        ai_extractor = AIRelationshipExtractor()
        
        combined_extractor = CombinedRelationshipExtractor(extractors=[pattern_extractor, ai_extractor])
        assert combined_extractor is not None
        assert len(combined_extractor.extractors) == 2
    
    def test_combined_extraction(self):
        """Test extracting relationships with a combined extractor."""
        # Create mock extractors
        pattern_extractor = MagicMock()
        ai_extractor = MagicMock()
        
        source = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, id="e1")
        target1 = Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.9, start_pos=30, end_pos=34, id="e2")
        target2 = Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.9, start_pos=60, end_pos=65, id="e3")
        
        # Set up mock returns
        pattern_extractor.extract_relationships.return_value = [
            Relationship(
                source=source,
                target=target2,
                relation_type=RelationType.OUTPERFORMS,
                confidence=0.8,
                context="GPT-4 outperforms GPT-3",
                id="r1"
            )
        ]
        
        ai_extractor.extract_relationships.return_value = [
            Relationship(
                source=source,
                target=target1,
                relation_type=RelationType.EVALUATED_ON,
                confidence=0.85,
                context="GPT-4 evaluated on MMLU",
                id="r2"
            ),
            Relationship(
                source=source,
                target=target2,
                relation_type=RelationType.OUTPERFORMS,
                confidence=0.9,
                context="GPT-4 outperforms GPT-3",
                id="r3"
            )
        ]
        
        # Create combined extractor
        combined_extractor = CombinedRelationshipExtractor(extractors=[pattern_extractor, ai_extractor])
        
        # Mock _resolve_conflicts to return all relationships
        combined_extractor._resolve_conflicts = MagicMock(side_effect=lambda x: x)
        
        # Extract relationships
        text = "GPT-4 was evaluated on MMLU and outperforms GPT-3."
        entities = [source, target1, target2]
        relationships = combined_extractor.extract_relationships(text, entities)
        
        # Verify extractors were called
        pattern_extractor.extract_relationships.assert_called_once_with(text, entities)
        ai_extractor.extract_relationships.assert_called_once_with(text, entities)
        
        # Verify relationships were combined
        assert len(relationships) == 3
        combined_extractor._resolve_conflicts.assert_called_once()
    
    def test_resolve_conflicts(self):
        """Test resolving conflicting relationships."""
        # Create a combined extractor
        combined_extractor = CombinedRelationshipExtractor(extractors=[])
        
        # Create test entities
        source = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, id="e1")
        target = Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.9, start_pos=60, end_pos=65, id="e3")
        
        # Create conflicting relationships (same entities, same relation type, different confidence)
        relationships = [
            Relationship(
                source=source,
                target=target,
                relation_type=RelationType.OUTPERFORMS,
                confidence=0.8,
                context="GPT-4 outperforms GPT-3",
                id="r1"
            ),
            Relationship(
                source=source,
                target=target,
                relation_type=RelationType.OUTPERFORMS,
                confidence=0.9,
                context="GPT-4 outperforms GPT-3 on most tasks",
                id="r2"
            )
        ]
        
        # Resolve conflicts
        resolved = combined_extractor._resolve_conflicts(relationships)
        
        # Should keep the one with higher confidence
        assert len(resolved) == 1
        assert resolved[0].id == "r2"
        assert resolved[0].confidence == 0.9


class TestRelationshipExtractorFactory:
    """Tests for the RelationshipExtractorFactory class."""
    
    def test_create_pattern_extractor(self):
        """Test creating a pattern relationship extractor."""
        extractor = RelationshipExtractorFactory.create_extractor("pattern")
        assert isinstance(extractor, PatternRelationshipExtractor)
    
    def test_create_ai_extractor(self):
        """Test creating an AI relationship extractor."""
        extractor = RelationshipExtractorFactory.create_extractor("ai")
        assert isinstance(extractor, AIRelationshipExtractor)
    
    def test_create_combined_extractor(self):
        """Test creating a combined relationship extractor."""
        config = {
            "extractors": [
                {"type": "pattern"},
                {"type": "ai"}
            ]
        }
        
        extractor = RelationshipExtractorFactory.create_extractor("combined", config)
        assert isinstance(extractor, CombinedRelationshipExtractor)
        assert len(extractor.extractors) == 2
        assert isinstance(extractor.extractors[0], PatternRelationshipExtractor)
        assert isinstance(extractor.extractors[1], AIRelationshipExtractor)
    
    def test_create_with_config(self):
        """Test creating a relationship extractor with configuration."""
        config = {
            "patterns": {
                "DEVELOPED_BY": [r"(\w+) developed by (\w+)"]
            }
        }
        
        extractor = RelationshipExtractorFactory.create_extractor("pattern", config)
        assert isinstance(extractor, PatternRelationshipExtractor)
        
        # Check if the custom patterns were loaded
        if hasattr(extractor, "custom_patterns"):
            assert "DEVELOPED_BY" in extractor.custom_patterns
    
    def test_create_invalid_extractor(self):
        """Test creating an invalid relationship extractor."""
        with pytest.raises(ValueError):
            RelationshipExtractorFactory.create_extractor("invalid_type")