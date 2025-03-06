"""
End-to-end test fixtures for knowledge extraction.

This module provides pytest fixtures specifically for end-to-end testing
the entire knowledge extraction pipeline, including real components
and test data representative of real-world scenarios.
"""

import pytest
import tempfile
import os
import shutil
import json

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory


@pytest.fixture
def e2e_document_directory():
    """Create a directory with test documents for end-to-end testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a research paper text file (simplified version)
    with open(os.path.join(temp_dir, "paper.txt"), "w") as f:
        f.write("Title: Advances in Large Language Models\n\n")
        f.write("Abstract: This paper discusses recent advances in large language models like GPT-4, PaLM,\n")
        f.write("and Claude. We analyze their performance on various benchmarks and discuss implications.\n\n")
        f.write("1. Introduction\n\n")
        f.write("Large language models (LLMs) have revolutionized natural language processing. Models like\n")
        f.write("GPT-4 developed by OpenAI, PaLM developed by Google, and Claude developed by Anthropic\n")
        f.write("have shown impressive capabilities on various tasks.\n\n")
        f.write("2. Methodology\n\n")
        f.write("We evaluated these models on benchmarks including MMLU, HumanEval, GSM8K, and BIG-Bench.\n")
        f.write("The evaluation was conducted using standard methodologies described by previous researchers.\n\n")
        f.write("3. Results\n\n")
        f.write("GPT-4 achieved 86.4% accuracy on MMLU, outperforming PaLM (76.2%) and Claude (75.5%).\n")
        f.write("On HumanEval, GPT-4 achieved 67.0% pass@1, compared to 58.4% for PaLM.\n")
        f.write("All models were implemented using PyTorch and trained on NVIDIA A100 GPUs.\n\n")
        f.write("4. Conclusion\n\n")
        f.write("Our analysis shows that GPT-4 currently leads performance across most benchmarks,\n")
        f.write("though all models show strengths in different areas. Future work will explore\n")
        f.write("specialized training techniques to improve performance on specific tasks.\n")
    
    # Create a web article HTML file
    with open(os.path.join(temp_dir, "article.html"), "w") as f:
        f.write("<html><head><title>AI Research Overview</title></head><body>\n")
        f.write("<h1>The State of AI Research in 2023</h1>\n")
        f.write("<p>The field of artificial intelligence has seen tremendous progress in recent years.</p>\n")
        f.write("<h2>Large Language Models</h2>\n")
        f.write("<p>BERT, developed by Google AI in 2018, revolutionized NLP by introducing bidirectional training.</p>\n")
        f.write("<p>GPT-3 by OpenAI, with 175 billion parameters, demonstrated impressive few-shot learning capabilities.</p>\n")
        f.write("<p>More recently, models like Llama by Meta and Falcon have emerged as powerful open-source alternatives.</p>\n")
        f.write("<h2>Training Infrastructure</h2>\n")
        f.write("<p>Modern AI models are typically trained using PyTorch or TensorFlow on NVIDIA GPUs.</p>\n")
        f.write("<p>Training GPT-4 reportedly required thousands of NVIDIA A100 GPUs.</p>\n")
        f.write("</body></html>")
    
    # Create a blog post text file
    with open(os.path.join(temp_dir, "blog.txt"), "w") as f:
        f.write("# Comparing Modern Vision Models\n\n")
        f.write("In this post, we'll compare several modern vision models including:\n\n")
        f.write("- ViT (Vision Transformer) by Google Research\n")
        f.write("- CLIP by OpenAI\n")
        f.write("- DALL-E 2 by OpenAI\n")
        f.write("- Stable Diffusion by Stability AI\n\n")
        f.write("## Performance Comparisons\n\n")
        f.write("CLIP has shown impressive zero-shot capabilities across various vision tasks.\n")
        f.write("Stable Diffusion, based on the latent diffusion model architecture, has been widely\n")
        f.write("adopted due to its open nature and lower computational requirements compared to DALL-E 2.\n")
        f.write("Both models use the transformer architecture pioneered by the original ViT model.\n")
    
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def e2e_output_directory():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def real_knowledge_extractor():
    """Return a knowledge extractor with real components for end-to-end testing."""
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    relationship_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    return KnowledgeExtractor(
        document_processor=document_processor,
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )


@pytest.fixture
def advanced_knowledge_extractor():
    """Return an advanced knowledge extractor with combined components for end-to-end testing."""
    document_processor = DocumentProcessor()
    
    # Create a combined entity recognizer with both AI and scientific entities
    entity_recognizer = EntityRecognizerFactory.create_recognizer(
        "combined",
        config={
            "recognizers": [
                {"type": "ai"},
                {"type": "scientific"}
            ]
        }
    )
    
    # Create a combined relationship extractor with both pattern and AI extractors
    relationship_extractor = RelationshipExtractorFactory.create_extractor(
        "combined",
        config={
            "extractors": [
                {"type": "pattern"},
                {"type": "ai"}
            ]
        }
    )
    
    return KnowledgeExtractor(
        document_processor=document_processor,
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )