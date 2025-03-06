"""
Tests for the Report Structure Planner in the Research Generation System.

This module contains tests for the Report Structure Planner, which is responsible for
planning the structure of research reports, determining appropriate sections, and
organizing content in a logical flow.
"""

import os
import unittest
import tempfile
import json
from pathlib import Path

from src.research_orchestrator.research_generation.report_structure import (
    ReportStructurePlanner,
    DocumentStructure,
    Section,
    DocumentType,
    SectionType
)


class TestReportStructurePlanner(unittest.TestCase):
    """Tests for the ReportStructurePlanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for templates
        self.temp_dir = tempfile.TemporaryDirectory()
        self.planner = ReportStructurePlanner(template_dir=self.temp_dir.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_create_default_templates(self):
        """Test that default templates are created correctly."""
        # Templates should have been created in setUp
        templates = self.planner.get_document_templates()
        
        # Check that we have the expected templates
        expected_templates = ["research_paper", "literature_review", "technical_report", "tutorial", "survey"]
        for template in expected_templates:
            self.assertIn(template, templates)
        
        # Check that template files exist
        for template in expected_templates:
            template_path = os.path.join(self.temp_dir.name, f"{template}.json")
            self.assertTrue(os.path.exists(template_path))
    
    def test_load_template(self):
        """Test loading a template."""
        template = self.planner.load_template("research_paper")
        
        self.assertEqual(template.document_type, DocumentType.RESEARCH_PAPER)
        self.assertGreater(len(template.sections), 0)
        
        section_types = [section.section_type for section in template.sections]
        self.assertIn(SectionType.INTRODUCTION, section_types)
        self.assertIn(SectionType.METHODOLOGY, section_types)
        self.assertIn(SectionType.CONCLUSION, section_types)
    
    def test_save_template(self):
        """Test saving a template."""
        # Create template
        sections = [
            Section(
                section_type=SectionType.TITLE,
                title="Test Title",
                description="Test description",
                required=True,
                order=0
            ),
            Section(
                section_type=SectionType.INTRODUCTION,
                title="Test Introduction",
                description="Test introduction description",
                required=True,
                order=1
            )
        ]
        
        template = DocumentStructure(
            title="Test Template",
            document_type=DocumentType.RESEARCH_PAPER,
            sections=sections
        )
        
        # Save and reload template
        self.planner.save_template(template, "test_template")
        
        template_path = os.path.join(self.temp_dir.name, "test_template.json")
        self.assertTrue(os.path.exists(template_path))
        
        loaded_template = self.planner.load_template("test_template")
        self.assertEqual(loaded_template.title, "Test Template")
        self.assertEqual(loaded_template.document_type, DocumentType.RESEARCH_PAPER)
        self.assertEqual(len(loaded_template.sections), 2)
    
    def test_generate_structure(self):
        """Test generating a document structure."""
        structure = self.planner.generate_structure(
            title="Test Document",
            document_type=DocumentType.RESEARCH_PAPER,
            topic="Test Topic",
            audience="Academic",
            target_length="10 pages"
        )
        
        self.assertEqual(structure.title, "Test Document")
        self.assertEqual(structure.document_type, DocumentType.RESEARCH_PAPER)
        self.assertEqual(structure.audience, "Academic")
        self.assertEqual(structure.target_length, "10 pages")
        self.assertEqual(structure.metadata["generated_for"], "Test Topic")
    
    def test_generate_structure_with_string_document_type(self):
        """Test generating a document structure with a string document type."""
        structure = self.planner.generate_structure(
            title="Test Document",
            document_type="LITERATURE_REVIEW",
            topic="Test Topic"
        )
        
        self.assertEqual(structure.document_type, DocumentType.LITERATURE_REVIEW)
    
    def test_analyze_topics_for_sections(self):
        """Test analyzing topics for sections."""
        topic = "Machine Learning Algorithms"
        subtopics = ["Decision Trees", "Neural Networks", "Support Vector Machines"]
        
        # Test research paper structure
        paper_sections = self.planner.analyze_topics_for_sections(
            topic=topic,
            subtopics=subtopics,
            document_type=DocumentType.RESEARCH_PAPER
        )
        
        self.assertGreater(len(paper_sections), 0)
        section_types = [section.section_type for section in paper_sections]
        self.assertIn(SectionType.METHODOLOGY, section_types)
        self.assertIn(SectionType.RESULTS, section_types)
        
        # Test literature review structure
        review_sections = self.planner.analyze_topics_for_sections(
            topic=topic,
            subtopics=subtopics,
            document_type=DocumentType.LITERATURE_REVIEW
        )
        
        self.assertEqual(len(review_sections), len(subtopics))
    
    def test_adjust_for_audience(self):
        """Test adjusting a document structure for different audiences."""
        # Create a basic structure
        sections = [
            Section(
                section_type=SectionType.TITLE,
                title="Test Title",
                description="Test description",
                required=True,
                order=0
            ),
            Section(
                section_type=SectionType.INTRODUCTION,
                title="Test Introduction",
                description="Test introduction description",
                content_guidance="Basic guidance",
                required=True,
                order=1
            ),
            Section(
                section_type=SectionType.METHODOLOGY,
                title="Test Methodology",
                description="Test methodology description",
                content_guidance="Basic guidance",
                required=True,
                order=2
            )
        ]
        
        structure = DocumentStructure(
            title="Test Document",
            document_type=DocumentType.RESEARCH_PAPER,
            sections=sections,
            audience="General"
        )
        
        # Adjust for academic audience
        academic_structure = self.planner.adjust_for_audience(structure, "Academic")
        
        # Check that the audience was updated
        self.assertEqual(academic_structure.audience, "Academic")
        
        # Check that content guidance was updated for methodology section
        methodology_section = next(s for s in academic_structure.sections if s.section_type == SectionType.METHODOLOGY)
        self.assertIn("theoretical foundations", methodology_section.content_guidance)
        
        # Adjust for industry audience
        industry_structure = self.planner.adjust_for_audience(structure, "Industry")
        
        # Check that the audience was updated
        self.assertEqual(industry_structure.audience, "Industry")
        
        # Check that introduction guidance was updated
        intro_section = next(s for s in industry_structure.sections if s.section_type == SectionType.INTRODUCTION)
        self.assertIn("business value", intro_section.content_guidance)
        
        # Check for added business section
        business_sections = [s for s in industry_structure.sections if s.title == "Business Implications"]
        self.assertEqual(len(business_sections), 1)
        
        # Adjust for beginner audience
        beginner_structure = self.planner.adjust_for_audience(structure, "Beginner")
        
        # Check for added glossary section
        glossary_sections = [s for s in beginner_structure.sections if s.title == "Glossary of Terms"]
        self.assertEqual(len(glossary_sections), 1)
        
        # Check for added further reading section
        reading_sections = [s for s in beginner_structure.sections if s.title == "Further Reading"]
        self.assertEqual(len(reading_sections), 1)
    
    def test_generate_section_outline(self):
        """Test generating a section outline."""
        # Create a section
        section = Section(
            section_type=SectionType.INTRODUCTION,
            title="Introduction",
            description="Introduction to the topic",
            required=True
        )
        
        # Generate an outline
        outline = self.planner.generate_section_outline(section, "Machine Learning")
        
        # Check that the outline has the expected structure
        self.assertIn("section_title", outline)
        self.assertIn("section_type", outline)
        self.assertIn("key_points", outline)
        self.assertIn("subsections", outline)
        
        # Check that the outline contains key points
        self.assertGreater(len(outline["key_points"]), 0)
        
        # Check that the outline contains subsections
        self.assertGreater(len(outline["subsections"]), 0)
    
    def test_section_to_dict_and_from_dict(self):
        """Test converting sections to and from dictionaries."""
        # Create a section with subsections
        subsection = Section(
            section_type=SectionType.ALGORITHM_DESCRIPTION,
            title="Algorithm Description",
            description="Description of the algorithm",
            content_guidance="Detailed algorithm description",
            estimated_length="1-2 pages",
            required=True
        )
        
        section = Section(
            section_type=SectionType.METHODOLOGY,
            title="Methodology",
            description="Research methodology",
            content_guidance="Detailed methodology description",
            estimated_length="2-3 pages",
            required=True,
            order=1,
            subsections=[subsection]
        )
        
        # Convert to dictionary
        section_dict = section.to_dict()
        
        # Check dictionary structure
        self.assertEqual(section_dict["section_type"], "METHODOLOGY")
        self.assertEqual(section_dict["title"], "Methodology")
        self.assertEqual(len(section_dict["subsections"]), 1)
        
        # Convert back to section
        new_section = Section.from_dict(section_dict)
        
        # Check section properties
        self.assertEqual(new_section.section_type, SectionType.METHODOLOGY)
        self.assertEqual(new_section.title, "Methodology")
        self.assertEqual(len(new_section.subsections), 1)
        
        # Check subsection properties
        subsection = new_section.subsections[0]
        self.assertEqual(subsection.section_type, SectionType.ALGORITHM_DESCRIPTION)
        self.assertEqual(subsection.title, "Algorithm Description")
    
    def test_document_structure_to_dict_and_from_dict(self):
        """Test converting document structures to and from dictionaries."""
        # Create a document structure
        sections = [
            Section(
                section_type=SectionType.TITLE,
                title="Title",
                description="Document title",
                required=True,
                order=0
            ),
            Section(
                section_type=SectionType.INTRODUCTION,
                title="Introduction",
                description="Introduction to the topic",
                required=True,
                order=1
            )
        ]
        
        structure = DocumentStructure(
            title="Test Document",
            document_type=DocumentType.RESEARCH_PAPER,
            sections=sections,
            audience="Academic",
            target_length="10 pages",
            style_guide="IEEE",
            metadata={"key": "value"}
        )
        
        # Convert to dictionary
        structure_dict = structure.to_dict()
        
        # Check dictionary structure
        self.assertEqual(structure_dict["title"], "Test Document")
        self.assertEqual(structure_dict["document_type"], "RESEARCH_PAPER")
        self.assertEqual(structure_dict["audience"], "Academic")
        self.assertEqual(len(structure_dict["sections"]), 2)
        
        # Convert back to document structure
        new_structure = DocumentStructure.from_dict(structure_dict)
        
        # Check structure properties
        self.assertEqual(new_structure.title, "Test Document")
        self.assertEqual(new_structure.document_type, DocumentType.RESEARCH_PAPER)
        self.assertEqual(new_structure.audience, "Academic")
        self.assertEqual(len(new_structure.sections), 2)
    
    def test_document_structure_save_and_load(self):
        """Test saving and loading document structures."""
        # Create a document structure
        sections = [
            Section(
                section_type=SectionType.TITLE,
                title="Title",
                description="Document title",
                required=True,
                order=0
            ),
            Section(
                section_type=SectionType.INTRODUCTION,
                title="Introduction",
                description="Introduction to the topic",
                required=True,
                order=1
            )
        ]
        
        structure = DocumentStructure(
            title="Test Document",
            document_type=DocumentType.RESEARCH_PAPER,
            sections=sections,
            audience="Academic",
            target_length="10 pages"
        )
        
        # Save to a temporary file
        file_path = os.path.join(self.temp_dir.name, "test_structure.json")
        structure.save_to_file(file_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Load the structure
        loaded_structure = DocumentStructure.load_from_file(file_path)
        
        # Check structure properties
        self.assertEqual(loaded_structure.title, "Test Document")
        self.assertEqual(loaded_structure.document_type, DocumentType.RESEARCH_PAPER)
        self.assertEqual(loaded_structure.audience, "Academic")
        self.assertEqual(len(loaded_structure.sections), 2)


if __name__ == "__main__":
    unittest.main()