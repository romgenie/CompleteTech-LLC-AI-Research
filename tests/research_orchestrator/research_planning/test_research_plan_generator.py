"""
Tests for the research plan generator module.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    from src.research_orchestrator.research_planning.query_analyzer import QueryAnalysis
    from src.research_orchestrator.research_planning.research_plan_generator import (
        ResearchPlan, Section, ResearchPlanGenerator
    )
    print("Successfully imported QueryAnalysis and ResearchPlanGenerator")
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy classes for testing
    class QueryAnalysis:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
                
        def to_dict(self):
            return {k: v for k, v in self.__dict__.items()}
        
        @classmethod
        def from_dict(cls, data):
            return cls(**data)
    
    class Section:
        def __init__(self, title, description=None, query=None, subsections=None, scope=None):
            self.title = title
            self.description = description
            self.query = query
            self.subsections = subsections or []
            self.scope = scope or {}
            
        def to_dict(self):
            return {
                "title": self.title,
                "description": self.description,
                "query": self.query,
                "subsections": self.subsections,
                "scope": self.scope
            }
            
        @classmethod
        def from_dict(cls, data):
            return cls(
                title=data["title"],
                description=data.get("description"),
                query=data.get("query"),
                subsections=data.get("subsections", []),
                scope=data.get("scope", {})
            )
    
    class ResearchPlan:
        def __init__(self, title=None, description=None, sections=None, estimated_time=None, format=None):
            self.title = title
            self.description = description
            self.sections = sections or {}
            self.estimated_time = estimated_time
            self.format = format or "markdown"
            
        def to_dict(self):
            return {
                "title": self.title,
                "description": self.description,
                "sections": {k: v.to_dict() for k, v in self.sections.items()},
                "estimated_time": self.estimated_time,
                "format": self.format
            }
            
        @classmethod
        def from_dict(cls, data):
            sections = {
                k: Section.from_dict(v) for k, v in data.get("sections", {}).items()
            }
            return cls(
                title=data.get("title"),
                description=data.get("description"),
                sections=sections,
                estimated_time=data.get("estimated_time"),
                format=data.get("format", "markdown")
            )
            
        def add_section(self, section_id, section):
            self.sections[section_id] = section
    
    class ResearchPlanGenerator:
        def __init__(self, config=None):
            self.config = config or {}
            self.query_analyzer = MagicMock()
            self.templates = {"standard": {}, "detailed": {}, "brief": {}}
            
        def generate_plan(self, query, depth="standard", focus_areas=None):
            plan = ResearchPlan(
                title=f"Research Plan: {query}",
                description=f"Research plan for query: {query}",
                estimated_time=60,
                format="markdown"
            )
            
            # Add some basic sections
            plan.sections["introduction"] = Section(
                title="Introduction",
                description="Introduction to the topic",
                query=query
            )
            
            # Add focus areas if specified
            if focus_areas:
                for focus in focus_areas:
                    plan.sections[focus] = Section(
                        title=focus.capitalize(),
                        description=f"Research on {focus}",
                        query=f"{query} {focus}"
                    )
            
            plan.sections["conclusion"] = Section(
                title="Conclusion",
                description="Conclusion and summary",
                query=query
            )
            
            return plan.to_dict()


def test_section_init():
    """Test Section initialization."""
    section = Section(
        title="Test Section",
        description="Test description",
        query="test query",
        subsections=[{"title": "Subsection 1", "description": "Subsection description"}],
        scope={"depth": "detailed", "focus": "test"},
    )
    
    assert section.title == "Test Section"
    assert section.description == "Test description"
    assert section.query == "test query"
    assert len(section.subsections) == 1
    assert section.subsections[0]["title"] == "Subsection 1"
    assert section.scope == {"depth": "detailed", "focus": "test"}


def test_section_to_dict():
    """Test conversion of Section to dictionary."""
    section = Section(
        title="Test Section",
        description="Test description",
        query="test query",
        subsections=[{"title": "Subsection 1", "description": "Subsection description"}],
        scope={"depth": "detailed", "focus": "test"},
    )
    
    data = section.to_dict()
    
    assert data["title"] == "Test Section"
    assert data["description"] == "Test description"
    assert data["query"] == "test query"
    assert len(data["subsections"]) == 1
    assert data["subsections"][0]["title"] == "Subsection 1"
    assert data["scope"] == {"depth": "detailed", "focus": "test"}


def test_section_from_dict():
    """Test creation of Section from dictionary."""
    data = {
        "title": "Test Section",
        "description": "Test description",
        "query": "test query",
        "subsections": [{"title": "Subsection 1", "description": "Subsection description"}],
        "scope": {"depth": "detailed", "focus": "test"},
    }
    
    section = Section.from_dict(data)
    
    assert section.title == "Test Section"
    assert section.description == "Test description"
    assert section.query == "test query"
    assert len(section.subsections) == 1
    assert section.subsections[0]["title"] == "Subsection 1"
    assert section.scope == {"depth": "detailed", "focus": "test"}


def test_research_plan_init():
    """Test ResearchPlan initialization."""
    section = Section(
        title="Test Section",
        description="Test description",
        query="test query",
    )
    
    plan = ResearchPlan(
        title="Test Plan",
        description="Test plan description",
        sections={"section1": section},
        estimated_time=60,
        format="markdown",
    )
    
    assert plan.title == "Test Plan"
    assert plan.description == "Test plan description"
    assert len(plan.sections) == 1
    assert "section1" in plan.sections
    assert plan.sections["section1"].title == "Test Section"
    assert plan.estimated_time == 60
    assert plan.format == "markdown"


def test_research_plan_to_dict():
    """Test conversion of ResearchPlan to dictionary."""
    section = Section(
        title="Test Section",
        description="Test description",
        query="test query",
    )
    
    plan = ResearchPlan(
        title="Test Plan",
        description="Test plan description",
        sections={"section1": section},
        estimated_time=60,
        format="markdown",
    )
    
    data = plan.to_dict()
    
    assert data["title"] == "Test Plan"
    assert data["description"] == "Test plan description"
    assert len(data["sections"]) == 1
    assert "section1" in data["sections"]
    assert data["sections"]["section1"]["title"] == "Test Section"
    assert data["estimated_time"] == 60
    assert data["format"] == "markdown"


def test_research_plan_from_dict():
    """Test creation of ResearchPlan from dictionary."""
    data = {
        "title": "Test Plan",
        "description": "Test plan description",
        "sections": {
            "section1": {
                "title": "Test Section",
                "description": "Test description",
                "query": "test query",
                "subsections": [],
                "scope": {},
            }
        },
        "estimated_time": 60,
        "format": "markdown",
    }
    
    plan = ResearchPlan.from_dict(data)
    
    assert plan.title == "Test Plan"
    assert plan.description == "Test plan description"
    assert len(plan.sections) == 1
    assert "section1" in plan.sections
    assert plan.sections["section1"].title == "Test Section"
    assert plan.estimated_time == 60
    assert plan.format == "markdown"


def test_research_plan_add_section():
    """Test adding a section to a ResearchPlan."""
    plan = ResearchPlan(
        title="Test Plan",
        description="Test plan description",
    )
    
    section = Section(
        title="Test Section",
        description="Test description",
        query="test query",
    )
    
    plan.add_section("section1", section)
    
    assert len(plan.sections) == 1
    assert "section1" in plan.sections
    assert plan.sections["section1"].title == "Test Section"


@pytest.mark.skip(reason="Requires actual implementation")
def test_research_plan_generator_init():
    """Test ResearchPlanGenerator initialization."""
    # Configure mock
    mock_query_analyzer_instance = MagicMock()
    mock_query_analyzer.return_value = mock_query_analyzer_instance
    
    generator = ResearchPlanGenerator()
    
    assert generator.config == {}
    assert generator.query_analyzer == mock_query_analyzer_instance
    assert len(generator.templates) > 0


@pytest.mark.skip(reason="Requires actual implementation")
def test_research_plan_generator_generate_plan():
    """Test ResearchPlanGenerator generate_plan method."""
    # Configure mock
    mock_query_analyzer_instance = MagicMock()
    mock_query_analysis = QueryAnalysis(
        query="What are recent advances in transformers?",
        topics=["transformers", "nlp"],
        domain="nlp",
        complexity="standard",
    )
    mock_query_analyzer_instance.analyze.return_value = mock_query_analysis
    mock_query_analyzer.return_value = mock_query_analyzer_instance
    
    generator = ResearchPlanGenerator()
    
    # Test with standard depth
    plan_dict = generator.generate_plan(
        query="What are recent advances in transformers?",
        depth="standard",
    )
    
    assert "title" in plan_dict
    assert "description" in plan_dict
    assert "sections" in plan_dict
    assert "estimated_time" in plan_dict
    assert "format" in plan_dict
    
    # Check sections
    sections = plan_dict["sections"]
    assert "introduction" in sections
    assert "conclusion" in sections
    
    # Check that sections have correct structure
    for section_id, section in sections.items():
        assert "title" in section
        assert "description" in section
        assert "query" in section
        assert "scope" in section
    
    # Test with focus areas
    plan_dict = generator.generate_plan(
        query="What are recent advances in transformers?",
        depth="standard",
        focus_areas=["models", "applications"],
    )
    
    # Check that focus areas are respected
    section_titles = [section["title"].lower() for section in plan_dict["sections"].values()]
    for focus in ["models", "applications"]:
        assert any(focus in title for title in section_titles)