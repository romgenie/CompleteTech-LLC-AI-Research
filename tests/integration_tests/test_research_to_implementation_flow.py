"""
Integration test for the full research workflow: 
from research query to knowledge extraction to implementation.

This test validates the flow of information through all three major systems:
1. Research Orchestration Framework processes a query and gathers information
2. Knowledge Graph System extracts and stores entities and relationships
3. Implementation System generates code based on the knowledge graph

The test creates a controlled research scenario, follows it through the entire process,
and validates that each system correctly processes and passes the information.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

class TestResearchToImplementationFlow(unittest.TestCase):
    """Test the end-to-end flow from research query to code implementation."""

    def setUp(self):
        """Set up test environment with mocked external services."""
        # Create patchers for external services to avoid real API calls during testing
        self.web_search_patcher = patch('research_orchestrator.information_gathering.web_source.search')
        self.academic_search_patcher = patch('research_orchestrator.information_gathering.academic_source.search')
        self.llm_generate_patcher = patch('research_orchestrator.research_generation.content_synthesis.generate_content')
        self.neo4j_patcher = patch('knowledge_graph_system.core.neo4j_manager.Neo4jManager')
        
        # Start the patchers
        self.mock_web_search = self.web_search_patcher.start()
        self.mock_academic_search = self.academic_search_patcher.start()
        self.mock_llm_generate = self.llm_generate_patcher.start()
        self.mock_neo4j = self.neo4j_patcher.start()
        
        # Configure mocks to return test data
        self.mock_web_search.return_value = self._get_test_web_results()
        self.mock_academic_search.return_value = self._get_test_academic_results()
        self.mock_llm_generate.return_value = self._get_test_generated_content()
        
        # Configure Neo4j mock to return mock graph data
        self.mock_neo4j_instance = self.mock_neo4j.return_value
        self.mock_neo4j_instance.run_query.return_value = self._get_test_graph_results()
        
        # Import actual components (after patching their dependencies)
        from research_orchestrator.core import ResearchOrchestrator
        from knowledge_graph_system.core import KnowledgeGraphManager
        from research_implementation.core import ImplementationManager
        
        # Initialize the components with test configuration
        self.research_orchestrator = ResearchOrchestrator(config={'test_mode': True})
        self.knowledge_graph_manager = KnowledgeGraphManager(graph_connection=self.mock_neo4j_instance)
        self.implementation_manager = ImplementationManager(config={'test_mode': True})
    
    def tearDown(self):
        """Clean up test environment."""
        # Stop all patchers
        self.web_search_patcher.stop()
        self.academic_search_patcher.stop()
        self.llm_generate_patcher.stop()
        self.neo4j_patcher.stop()
    
    def _get_test_web_results(self):
        """Return mock web search results about a transformer model."""
        return [
            {
                "title": "Introduction to Vision Transformers (ViT)",
                "url": "https://example.com/vision-transformers",
                "snippet": "Vision Transformers (ViT) apply the transformer architecture to image classification by splitting images into patches and processing them as tokens."
            },
            {
                "title": "ViT: Vision Transformer Implementation Guide",
                "url": "https://example.com/vit-implementation",
                "snippet": "This guide shows how to implement Vision Transformers using PyTorch, including the patch embedding, transformer encoder, and classification head."
            }
        ]
    
    def _get_test_academic_results(self):
        """Return mock academic search results about ViT."""
        return [
            {
                "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
                "authors": ["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov"],
                "publication": "ICLR 2021",
                "url": "https://arxiv.org/abs/2010.11929",
                "abstract": "We show that a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks."
            }
        ]
    
    def _get_test_generated_content(self):
        """Return mock LLM-generated content about ViT."""
        return {
            "title": "Vision Transformers: Architecture and Implementation",
            "content": "Vision Transformers (ViT) represent a paradigm shift in computer vision...",
            "code_examples": {
                "python": "import torch\nfrom torch import nn\n\nclass PatchEmbedding(nn.Module):\n    def __init__(self, img_size=224, patch_size=16, in_channels=3, embed_dim=768):\n        super().__init__()\n        self.patch_size = patch_size\n        self.projection = nn.Conv2d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)\n        \n    def forward(self, x):\n        x = self.projection(x)\n        x = x.flatten(2)\n        x = x.transpose(1, 2)\n        return x"
            }
        }
    
    def _get_test_graph_results(self):
        """Return mock Neo4j graph results."""
        mock_result = MagicMock()
        mock_result.data.return_value = [
            {
                "paper": {"title": "An Image is Worth 16x16 Words", "year": 2021},
                "model": {"name": "Vision Transformer", "type": "Transformer"},
                "relationship": "INTRODUCES"
            },
            {
                "model": {"name": "Vision Transformer", "type": "Transformer"},
                "dataset": {"name": "ImageNet", "type": "Image Classification"},
                "relationship": "EVALUATED_ON"
            }
        ]
        return mock_result
    
    def test_end_to_end_research_flow(self):
        """Test the full research to implementation flow."""
        # Step 1: Create a research query
        research_query = "How do Vision Transformers work and how can I implement one?"
        
        # Step 2: Research Orchestrator processes the query
        research_result = self.research_orchestrator.process_query(research_query)
        
        # Validate research result structure
        self.assertIn('title', research_result)
        self.assertIn('content', research_result)
        self.assertIn('entities', research_result)
        self.assertIn('relationships', research_result)
        
        # Step 3: Extract entities and relationships for knowledge graph
        entities = research_result['entities']
        relationships = research_result['relationships']
        
        # Step 4: Add to knowledge graph
        for entity in entities:
            entity_id = self.knowledge_graph_manager.add_entity(entity)
            self.assertIsNotNone(entity_id)
        
        for rel in relationships:
            rel_id = self.knowledge_graph_manager.add_relationship(
                rel['source'], rel['target'], rel['type'], rel['properties']
            )
            self.assertIsNotNone(rel_id)
        
        # Step 5: Query knowledge graph for implementation details
        implementation_context = self.knowledge_graph_manager.get_implementation_context("Vision Transformer")
        
        # Validate implementation context
        self.assertIn('model', implementation_context)
        self.assertIn('papers', implementation_context)
        self.assertIn('components', implementation_context)
        
        # Step 6: Generate implementation
        implementation = self.implementation_manager.create_implementation(
            topic="Vision Transformer",
            context=implementation_context
        )
        
        # Validate implementation
        self.assertIn('code', implementation)
        self.assertIn('documentation', implementation)
        self.assertIn('requirements', implementation)
        
        # Validate code contains key components
        self.assertIn('PatchEmbedding', implementation['code'])
        self.assertIn('transformer', implementation['code'].lower())

if __name__ == '__main__':
    unittest.main()