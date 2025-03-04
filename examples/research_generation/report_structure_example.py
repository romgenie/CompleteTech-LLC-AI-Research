"""
Example demonstrating the usage of the Report Structure Planner.

This example shows how to use the Report Structure Planner to create document structures,
generate section outlines, and adjust structures for different audiences.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add the project root to sys.path for imports
project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))

from src.research_orchestrator.research_generation.report_structure import (
    ReportStructurePlanner,
    DocumentType,
    SectionType,
    Section,
    DocumentStructure
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_research_paper_example():
    """Example of creating a research paper structure."""
    logger.info("===== Creating Research Paper Structure =====")
    
    # Initialize the planner
    planner = ReportStructurePlanner()
    
    # Generate a research paper structure
    paper_structure = planner.generate_structure(
        title="Attention-based Mechanisms for Efficient Natural Language Processing",
        document_type=DocumentType.RESEARCH_PAPER,
        topic="Attention mechanisms in NLP",
        audience="Academic",
        target_length="10-12 pages"
    )
    
    # Print basic structure info
    logger.info(f"Document Type: {paper_structure.document_type.name}")
    logger.info(f"Title: {paper_structure.title}")
    logger.info(f"Audience: {paper_structure.audience}")
    logger.info(f"Target Length: {paper_structure.target_length}")
    logger.info(f"Number of Sections: {len(paper_structure.sections)}")
    
    # Print sections
    logger.info("Sections:")
    for section in paper_structure.sections:
        logger.info(f"  - {section.title} ({section.section_type.name})")
        if section.subsections:
            for subsection in section.subsections:
                logger.info(f"      - {subsection.title} ({subsection.section_type.name})")
    
    # Example of saving the structure to a file
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, "research_paper_structure.json")
    paper_structure.save_to_file(file_path)
    logger.info(f"Saved structure to {file_path}")
    
    return paper_structure


def customize_structure_with_topics():
    """Example of customizing a structure with specific topics."""
    logger.info("===== Customizing Structure with Topics =====")
    
    # Initialize the planner
    planner = ReportStructurePlanner()
    
    # Define topic and subtopics
    topic = "Transformer Architecture Improvements"
    subtopics = [
        "Attention Mechanisms",
        "Positional Encoding",
        "Transformer Pre-training Strategies",
        "Fine-tuning Approaches"
    ]
    
    # Generate an initial structure
    structure = planner.generate_structure(
        title=f"Advances in {topic}",
        document_type=DocumentType.RESEARCH_PAPER,
        topic=topic
    )
    
    # Analyze topics to generate appropriate sections
    suggested_sections = planner.analyze_topics_for_sections(
        topic=topic,
        subtopics=subtopics,
        document_type=DocumentType.RESEARCH_PAPER
    )
    
    # Add the suggested sections to the structure
    for section in suggested_sections:
        structure.add_section(section)
    
    # Print the customized structure
    logger.info(f"Customized Structure for '{topic}':")
    logger.info(f"Number of Sections: {len(structure.sections)}")
    
    logger.info("Sections:")
    for section in structure.sections:
        logger.info(f"  - {section.title} ({section.section_type.name})")
        if section.subsections:
            for subsection in section.subsections:
                logger.info(f"      - {subsection.title} ({subsection.section_type.name})")
    
    return structure


def create_different_document_types():
    """Example of creating different types of documents."""
    logger.info("===== Creating Different Document Types =====")
    
    # Initialize the planner
    planner = ReportStructurePlanner()
    
    # List of document types to demonstrate
    document_types = [
        DocumentType.LITERATURE_REVIEW,
        DocumentType.TECHNICAL_REPORT,
        DocumentType.TUTORIAL,
        DocumentType.SURVEY
    ]
    
    # Generate structures for each document type
    for doc_type in document_types:
        structure = planner.generate_structure(
            title=f"Example {doc_type.name}",
            document_type=doc_type,
            topic="Machine Learning Techniques",
            audience="General"
        )
        
        logger.info(f"\n{doc_type.name} Structure:")
        logger.info(f"Number of Sections: {len(structure.sections)}")
        
        # Print first 3 sections as example
        logger.info("First 3 Sections:")
        for section in structure.sections[:3]:
            logger.info(f"  - {section.title} ({section.section_type.name})")
            if section.subsections and len(section.subsections) > 0:
                logger.info(f"      - {section.subsections[0].title} ({section.subsections[0].section_type.name})")


def adapt_for_different_audiences():
    """Example of adapting a structure for different audiences."""
    logger.info("===== Adapting for Different Audiences =====")
    
    # Initialize the planner
    planner = ReportStructurePlanner()
    
    # Create a base structure
    base_structure = planner.generate_structure(
        title="Deep Learning for Computer Vision",
        document_type=DocumentType.TECHNICAL_REPORT,
        topic="Deep Learning in Computer Vision",
        audience="General"
    )
    
    # List of audiences to demonstrate
    audiences = ["Academic", "Industry", "Beginner"]
    
    # Adapt for each audience
    for audience in audiences:
        adapted_structure = planner.adjust_for_audience(base_structure, audience)
        
        logger.info(f"\nStructure for {audience} Audience:")
        logger.info(f"Number of Sections: {len(adapted_structure.sections)}")
        
        # Print sections
        logger.info("Sections:")
        for section in adapted_structure.sections:
            logger.info(f"  - {section.title} ({section.section_type.name})")
            
            # For demonstration, print content guidance for a key section
            if section.section_type in [SectionType.INTRODUCTION, SectionType.METHODOLOGY]:
                logger.info(f"    Content Guidance: {section.content_guidance}")


def generate_section_outlines():
    """Example of generating detailed section outlines."""
    logger.info("===== Generating Section Outlines =====")
    
    # Initialize the planner
    planner = ReportStructurePlanner()
    
    # Create a structure
    structure = planner.generate_structure(
        title="Reinforcement Learning in Robotics",
        document_type=DocumentType.RESEARCH_PAPER,
        topic="Reinforcement Learning for Robotic Control",
        audience="Academic"
    )
    
    # Define topic for outline generation
    topic = "Reinforcement Learning for Robotic Control"
    
    # Generate outlines for key sections
    key_sections = [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.CONCLUSION
    ]
    
    outlines = {}
    for section_type in key_sections:
        # Find the section with this type
        section = next((s for s in structure.sections if s.section_type == section_type), None)
        
        if section:
            # Generate outline
            outline = planner.generate_section_outline(section, topic)
            outlines[section_type.name] = outline
    
    # Print outlines
    logger.info(f"Section Outlines for '{topic}':")
    
    for section_type, outline in outlines.items():
        logger.info(f"\nOutline for {section_type}:")
        logger.info(f"Title: {outline['section_title']}")
        
        logger.info("Key Points:")
        for point in outline['key_points']:
            logger.info(f"  - {point}")
        
        logger.info("Subsections:")
        for subsection in outline['subsections']:
            logger.info(f"  - {subsection['title']}: {subsection['content']}")
    
    # Save outlines to a file for reference
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, "section_outlines.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(outlines, f, indent=2)
    
    logger.info(f"Saved outlines to {file_path}")


def create_custom_template():
    """Example of creating and saving a custom template."""
    logger.info("===== Creating Custom Template =====")
    
    # Initialize the planner
    planner = ReportStructurePlanner()
    
    # Create custom sections for a case study
    sections = [
        Section(
            section_type=SectionType.TITLE,
            title="Title",
            description="Case study title",
            content_guidance="Should clearly indicate the subject of the case study",
            required=True,
            order=0
        ),
        Section(
            section_type=SectionType.ABSTRACT,
            title="Executive Summary",
            description="Brief summary of the case study",
            content_guidance="Should summarize the context, challenge, solution, and outcomes",
            estimated_length="250-350 words",
            required=True,
            order=1
        ),
        Section(
            section_type=SectionType.INTRODUCTION,
            title="Background and Context",
            description="Introduction to the case study context",
            content_guidance="Should provide necessary background on the organization/situation",
            estimated_length="1-2 pages",
            required=True,
            order=2
        ),
        Section(
            section_type=SectionType.PROBLEM,
            title="Challenge or Problem Statement",
            description="Description of the challenge or problem",
            content_guidance="Should clearly articulate the problem that needed to be solved",
            estimated_length="1-2 pages",
            required=True,
            order=3
        ),
        Section(
            section_type=SectionType.METHODOLOGY,
            title="Approach and Solution",
            description="Description of the approach and solution",
            content_guidance="Should detail the approach taken to address the challenge",
            estimated_length="2-3 pages",
            required=True,
            order=4,
            subsections=[
                Section(
                    section_type=SectionType.METHODOLOGY,
                    title="Solution Design",
                    description="Description of the solution design",
                    content_guidance="Should explain the design of the solution",
                    estimated_length="1 page",
                    required=True
                ),
                Section(
                    section_type=SectionType.IMPLEMENTATION,
                    title="Implementation Process",
                    description="Description of the implementation process",
                    content_guidance="Should detail how the solution was implemented",
                    estimated_length="1 page",
                    required=True
                )
            ]
        ),
        Section(
            section_type=SectionType.RESULTS,
            title="Results and Impact",
            description="Description of the results and impact",
            content_guidance="Should present the outcomes and impact of the solution",
            estimated_length="1-2 pages",
            required=True,
            order=5
        ),
        Section(
            section_type=SectionType.DISCUSSION,
            title="Lessons Learned",
            description="Discussion of lessons learned",
            content_guidance="Should discuss insights and lessons learned from the case",
            estimated_length="1 page",
            required=True,
            order=6
        ),
        Section(
            section_type=SectionType.CONCLUSION,
            title="Conclusion",
            description="Concluding remarks",
            content_guidance="Should summarize key takeaways and potential applications",
            estimated_length="0.5-1 page",
            required=True,
            order=7
        )
    ]
    
    # Create the template structure
    case_study_template = DocumentStructure(
        title="AI Implementation Case Study Template",
        document_type=DocumentType.CASE_STUDY,
        sections=sections,
        audience="Industry practitioners",
        target_length="8-12 pages",
        style_guide="Harvard Business School case study format",
        metadata={
            "template_version": "1.0",
            "description": "Template for a case study on AI implementation in industry"
        }
    )
    
    # Save the template
    planner.save_template(case_study_template, "case_study")
    
    logger.info("Created and saved custom case study template")
    logger.info("Template name: case_study")
    logger.info(f"Sections: {len(case_study_template.sections)}")
    
    # Verify the template was saved
    templates = planner.get_document_templates()
    logger.info(f"Available templates: {', '.join(templates)}")
    
    # Try loading the template to verify it was saved correctly
    loaded_template = planner.load_template("case_study")
    logger.info(f"Loaded template: {loaded_template.title}")
    logger.info(f"Document type: {loaded_template.document_type.name}")
    logger.info(f"Number of sections: {len(loaded_template.sections)}")


def main():
    """Run the Report Structure Planner examples."""
    logger.info("Starting Report Structure Planner examples")
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Run the examples
        create_research_paper_example()
        customize_structure_with_topics()
        create_different_document_types()
        adapt_for_different_audiences()
        generate_section_outlines()
        create_custom_template()
        
        logger.info("All examples completed successfully")
    
    except Exception as e:
        logger.error(f"Error running examples: {e}")


if __name__ == "__main__":
    main()