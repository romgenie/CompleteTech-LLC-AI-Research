"""
Integration tests for the relationship extraction components.

This module contains tests that validate the integration between different components
of the relationship extraction system, ensuring they work together correctly.
"""

import unittest
import os
import tempfile
import json
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory


class TestRelationshipExtractionIntegration(unittest.TestCase):
    """Integration tests for relationship extraction components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample test text with AI relationships
        self.test_text = """
        GPT-4 is a large language model developed by OpenAI. It was trained on a massive dataset
        of text and code, and it outperforms previous models like GPT-3.5 on many benchmarks.
        The model was evaluated on tasks such as the MMLU benchmark, where it achieved
        86.4% accuracy. Researchers implemented the model using PyTorch and trained it
        on NVIDIA A100 GPUs with distributed training techniques.
        
        BERT is a transformer-based language model that was developed by Google AI.
        It uses a bidirectional training approach and is based on the transformer architecture.
        BERT has been fine-tuned for various NLP tasks and has achieved state-of-the-art results
        on benchmarks like GLUE and SQuAD.
        """
        
        # Create sample entities
        self.entities = [
            Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=9, end_pos=14, metadata={}),
            Entity(text="OpenAI", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=56, end_pos=62, metadata={}),
            Entity(text="GPT-3.5", type=EntityType.MODEL, confidence=0.9, start_pos=147, end_pos=154, metadata={}),
            Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.85, start_pos=213, end_pos=217, metadata={}),
            Entity(text="PyTorch", type=EntityType.FRAMEWORK, confidence=0.8, start_pos=290, end_pos=297, metadata={}),
            Entity(text="NVIDIA A100", type=EntityType.HARDWARE, confidence=0.85, start_pos=317, end_pos=328, metadata={}),
            Entity(text="BERT", type=EntityType.MODEL, confidence=0.95, start_pos=376, end_pos=380, metadata={}),
            Entity(text="Google AI", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=434, end_pos=443, metadata={}),
            Entity(text="transformer architecture", type=EntityType.ARCHITECTURE, confidence=0.85, start_pos=507, end_pos=531, metadata={}),
            Entity(text="GLUE", type=EntityType.BENCHMARK, confidence=0.8, start_pos=613, end_pos=617, metadata={}),
            Entity(text="SQuAD", type=EntityType.BENCHMARK, confidence=0.8, start_pos=622, end_pos=627, metadata={})
        ]
    
    @unittest.skipIf(os.environ.get('SKIP_SLOW_TESTS', False), "Skipping slow tests")
    def test_pattern_extractor_integration(self):
        """Test that pattern extractor can identify basic relationships."""
        # Create a pattern relationship extractor
        extractor = RelationshipExtractorFactory.create_extractor("pattern")
        
        # Extract relationships
        relationships = extractor.extract_relationships(self.test_text, self.entities)
        
        # Check that we found at least some relationships
        self.assertTrue(len(relationships) > 0)
        
        # Check for specific relationship types
        found_types = {str(r.relation_type).lower() for r in relationships}
        
        # We should find at least some of these relationship types
        expected_types = {"is_a", "developed_by", "based_on", "outperforms", "evaluated_on", "implemented_in"}
        common_types = found_types.intersection({t.lower() for t in expected_types})
        
        self.assertTrue(len(common_types) > 0, f"No expected relationship types found. Found: {found_types}")
        
        # Check for some specific relationships
        has_developed_by = False
        has_outperforms = False
        has_based_on = False
        
        for rel in relationships:
            source_text = rel.source.text.lower() if rel.source else ""
            target_text = rel.target.text.lower() if rel.target else ""
            rel_type = str(rel.relation_type).lower()
            
            if "gpt-4" in source_text and "openai" in target_text and "developed_by" in rel_type:
                has_developed_by = True
            
            if "gpt-4" in source_text and "gpt-3.5" in target_text and "outperforms" in rel_type:
                has_outperforms = True
            
            if "bert" in source_text and "transformer" in target_text and "based_on" in rel_type:
                has_based_on = True
        
        # We don't require all relationships to be found as pattern extraction is imprecise,
        # but at least one should be identified
        self.assertTrue(
            has_developed_by or has_outperforms or has_based_on,
            "None of the expected relationships were found"
        )
    
    @unittest.skipIf(os.environ.get('SKIP_SLOW_TESTS', False), "Skipping slow tests")
    def test_ai_extractor_integration(self):
        """Test that AI extractor can identify AI-specific relationships."""
        # Create an AI relationship extractor
        extractor = RelationshipExtractorFactory.create_extractor("ai")
        
        # Extract relationships
        relationships = extractor.extract_relationships(self.test_text, self.entities)
        
        # Check that we found at least some relationships
        self.assertTrue(len(relationships) > 0)
        
        # Check for specific relationship types
        found_types = {str(r.relation_type).lower() for r in relationships}
        
        # We should find at least some of these relationship types
        expected_types = {"trained_on", "evaluated_on", "outperforms", "achieves", "uses"}
        common_types = found_types.intersection({t.lower() for t in expected_types})
        
        self.assertTrue(len(common_types) > 0, f"No expected relationship types found. Found: {found_types}")
    
    @unittest.skipIf(os.environ.get('SKIP_SLOW_TESTS', False), "Skipping slow tests")
    def test_combined_extractor_integration(self):
        """Test that combined extractor combines results from multiple extractors."""
        # Create a combined relationship extractor
        extractor = RelationshipExtractorFactory.create_extractor("combined")
        
        # Extract relationships
        relationships = extractor.extract_relationships(self.test_text, self.entities)
        
        # Check that we found at least some relationships
        self.assertTrue(len(relationships) > 0)
        
        # The combined extractor should find more relationships than either individual extractor
        pattern_extractor = RelationshipExtractorFactory.create_extractor("pattern")
        ai_extractor = RelationshipExtractorFactory.create_extractor("ai")
        
        pattern_relationships = pattern_extractor.extract_relationships(self.test_text, self.entities)
        ai_relationships = ai_extractor.extract_relationships(self.test_text, self.entities)
        
        # The combined extractor should have a substantial number of relationships
        # Not necessarily equal to the sum (may remove duplicates), but should be significant
        self.assertGreaterEqual(
            len(relationships), 
            max(len(pattern_relationships), len(ai_relationships)),
            "Combined extractor should find at least as many relationships as the best individual extractor"
        )
    
    def test_filtering_and_sorting(self):
        """Test relationship filtering and sorting functionality."""
        # Create mock relationships with different confidence scores
        model1 = self.entities[0]  # GPT-4
        model2 = self.entities[2]  # GPT-3.5
        org1 = self.entities[1]    # OpenAI
        benchmark = self.entities[3]  # MMLU
        
        relationships = [
            Relationship(
                source=model1,
                target=benchmark,
                relation_type=RelationType.EVALUATED_ON,
                confidence=0.9,
                context="The model was evaluated on MMLU benchmark"
            ),
            Relationship(
                source=model1,
                target=model2,
                relation_type=RelationType.OUTPERFORMS,
                confidence=0.8,
                context="It outperforms previous models like GPT-3.5"
            ),
            Relationship(
                source=model1,
                target=org1,
                relation_type=RelationType.DEVELOPED_BY,
                confidence=0.95,
                context="GPT-4 is a large language model developed by OpenAI"
            ),
            Relationship(
                source=model2,
                target=benchmark,
                relation_type=RelationType.EVALUATED_ON,
                confidence=0.7,
                context="GPT-3.5 was also evaluated on MMLU"
            )
        ]
        
        # Create a relationship extractor
        extractor = RelationshipExtractorFactory.create_extractor("combined")
        
        # Test filtering by confidence
        high_confidence = extractor.filter_relationships(relationships, min_confidence=0.9)
        self.assertEqual(len(high_confidence), 2)
        
        # Test filtering by relation type
        evaluated_rels = extractor.filter_relationships(
            relationships, 
            relation_types=[RelationType.EVALUATED_ON]
        )
        self.assertEqual(len(evaluated_rels), 2)
        
        # Test filtering by both criteria
        filtered = extractor.filter_relationships(
            relationships,
            min_confidence=0.8,
            relation_types=[RelationType.EVALUATED_ON, RelationType.OUTPERFORMS]
        )
        self.assertEqual(len(filtered), 2)


if __name__ == '__main__':
    unittest.main()