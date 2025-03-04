"""
Tests for the query analyzer module.
"""

import pytest

from research_orchestrator.research_planning.query_analyzer import QueryAnalysis, QueryAnalyzer


def test_query_analysis_init():
    """Test QueryAnalysis initialization."""
    analysis = QueryAnalysis(
        query="What are recent advances in transformers?",
        topics=["transformers", "natural language processing"],
        constraints={"time": "recent"},
        objectives=["Understand recent transformer developments"],
        complexity="standard",
        domain="nlp",
    )
    
    assert analysis.query == "What are recent advances in transformers?"
    assert "transformers" in analysis.topics
    assert "natural language processing" in analysis.topics
    assert analysis.constraints == {"time": "recent"}
    assert analysis.objectives == ["Understand recent transformer developments"]
    assert analysis.complexity == "standard"
    assert analysis.domain == "nlp"


def test_query_analysis_to_dict():
    """Test conversion of QueryAnalysis to dictionary."""
    analysis = QueryAnalysis(
        query="What are recent advances in transformers?",
        topics=["transformers", "natural language processing"],
        constraints={"time": "recent"},
        objectives=["Understand recent transformer developments"],
        complexity="standard",
        domain="nlp",
    )
    
    data = analysis.to_dict()
    
    assert data["query"] == "What are recent advances in transformers?"
    assert "transformers" in data["topics"]
    assert "natural language processing" in data["topics"]
    assert data["constraints"] == {"time": "recent"}
    assert data["objectives"] == ["Understand recent transformer developments"]
    assert data["complexity"] == "standard"
    assert data["domain"] == "nlp"


def test_query_analysis_from_dict():
    """Test creation of QueryAnalysis from dictionary."""
    data = {
        "query": "What are recent advances in transformers?",
        "topics": ["transformers", "natural language processing"],
        "constraints": {"time": "recent"},
        "objectives": ["Understand recent transformer developments"],
        "complexity": "standard",
        "domain": "nlp",
    }
    
    analysis = QueryAnalysis.from_dict(data)
    
    assert analysis.query == "What are recent advances in transformers?"
    assert "transformers" in analysis.topics
    assert "natural language processing" in analysis.topics
    assert analysis.constraints == {"time": "recent"}
    assert analysis.objectives == ["Understand recent transformer developments"]
    assert analysis.complexity == "standard"
    assert analysis.domain == "nlp"


def test_query_analyzer_init():
    """Test QueryAnalyzer initialization."""
    analyzer = QueryAnalyzer()
    assert analyzer.config == {}
    
    analyzer = QueryAnalyzer({"test": "value"})
    assert analyzer.config == {"test": "value"}


def test_query_analyzer_analyze():
    """Test QueryAnalyzer analyze method."""
    analyzer = QueryAnalyzer()
    
    # Test NLP domain query
    analysis = analyzer.analyze("What are recent advances in natural language processing and transformers?")
    assert "natural language processing" in analysis.topics
    assert "transformer" in analysis.topics or "transformers" in analysis.topics
    assert analysis.domain == "nlp"
    
    # Test CV domain query
    analysis = analyzer.analyze("What are the latest computer vision models for object detection?")
    assert "computer vision" in analysis.topics
    assert analysis.domain == "cv"
    
    # Test RL domain query
    analysis = analyzer.analyze("How are reinforcement learning algorithms used in robotics?")
    assert "reinforcement learning" in analysis.topics
    assert analysis.domain == "rl"
    
    # Test general AI query
    analysis = analyzer.analyze("What is artificial intelligence?")
    assert "artificial intelligence" in analysis.topics
    assert analysis.domain == "ai"


def test_query_analyzer_complexity():
    """Test QueryAnalyzer complexity determination."""
    analyzer = QueryAnalyzer()
    
    # Test basic query
    analysis = analyzer.analyze("What is ML?")
    assert analysis.complexity == "basic"
    
    # Test standard query
    analysis = analyzer.analyze("What are the key concepts in machine learning?")
    assert analysis.complexity == "standard"
    
    # Test advanced query
    analysis = analyzer.analyze(
        "What are the recent advances in transformer architectures for natural language processing, "
        "computer vision, and multimodal learning, and how do they compare in terms of performance, "
        "computational efficiency, and scalability?"
    )
    assert analysis.complexity == "advanced"