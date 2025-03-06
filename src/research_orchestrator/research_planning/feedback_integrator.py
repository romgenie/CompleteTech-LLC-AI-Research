"""
Feedback integration module for the Research Orchestration Framework.

This module processes user feedback on research plans and integrates it
into improved plans.
"""

from typing import Any, Dict, List, Optional, Union

from loguru import logger

from src.research_orchestrator.research_planning.research_plan_generator import ResearchPlan, Section


class FeedbackIntegrator:
    """
    Integrates user feedback into research plans.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the feedback integrator.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        logger.debug("Initialized FeedbackIntegrator")
    
    def integrate_feedback(
        self, plan: Dict[str, Any], feedback: str
    ) -> Dict[str, Any]:
        """
        Integrate feedback into a research plan.
        
        Args:
            plan: Research plan dictionary
            feedback: User feedback text
            
        Returns:
            Updated research plan dictionary
        """
        logger.info(f"Integrating feedback into plan: {plan.get('title')}")
        
        # Parse the original plan
        research_plan = ResearchPlan.from_dict(plan)
        
        # Parse the feedback
        feedback_items = self._parse_feedback(feedback)
        
        # Apply the feedback
        updated_plan = self._apply_feedback(research_plan, feedback_items)
        
        # Return updated plan
        return updated_plan.to_dict()
    
    def _parse_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Parse feedback into structured items.
        
        Args:
            feedback: User feedback text
            
        Returns:
            Dictionary of structured feedback items
        """
        # TODO: Implement more sophisticated feedback parsing
        # For now, use a simple approach based on keywords
        
        feedback_items = {
            "add_sections": [],
            "remove_sections": [],
            "modify_sections": {},
            "general_comments": "",
        }
        
        # Process feedback line by line
        lines = feedback.strip().split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section-specific feedback
            if line.lower().startswith("add section:") or line.lower().startswith("add:"):
                section_desc = line.split(":", 1)[1].strip()
                feedback_items["add_sections"].append(section_desc)
            
            elif line.lower().startswith("remove section:") or line.lower().startswith("remove:"):
                section_title = line.split(":", 1)[1].strip()
                feedback_items["remove_sections"].append(section_title)
            
            elif line.lower().startswith("modify section:") or line.lower().startswith("modify:"):
                section_title = line.split(":", 1)[1].strip()
                current_section = section_title
                feedback_items["modify_sections"][current_section] = ""
            
            # If we're currently collecting feedback for a section, add to it
            elif current_section:
                feedback_items["modify_sections"][current_section] += line + "\n"
            
            # Otherwise, add to general comments
            else:
                feedback_items["general_comments"] += line + "\n"
        
        return feedback_items
    
    def _apply_feedback(
        self, plan: ResearchPlan, feedback_items: Dict[str, Any]
    ) -> ResearchPlan:
        """
        Apply feedback items to the research plan.
        
        Args:
            plan: Research plan
            feedback_items: Structured feedback items
            
        Returns:
            Updated research plan
        """
        # Create a copy of the plan
        updated_plan = ResearchPlan(
            title=plan.title,
            description=plan.description,
            sections=dict(plan.sections),
            estimated_time=plan.estimated_time,
            format=plan.format,
        )
        
        # Apply general feedback to plan description
        if feedback_items["general_comments"]:
            updated_plan.description += f"\n\nFeedback notes: {feedback_items['general_comments'].strip()}"
        
        # Remove sections
        for section_title in feedback_items["remove_sections"]:
            # Find the section ID by title
            for section_id, section in list(updated_plan.sections.items()):
                if section.title.lower() == section_title.lower():
                    del updated_plan.sections[section_id]
                    logger.debug(f"Removed section: {section_title}")
                    break
        
        # Modify sections
        for section_title, modification in feedback_items["modify_sections"].items():
            # Find the section by title
            for section_id, section in updated_plan.sections.items():
                if section.title.lower() == section_title.lower():
                    # Append modification notes to section description
                    section.description += f"\n\nFeedback notes: {modification.strip()}"
                    updated_plan.sections[section_id] = section
                    logger.debug(f"Modified section: {section_title}")
                    break
        
        # Add new sections
        # For now, just add them as basic sections at the end
        for i, section_desc in enumerate(feedback_items["add_sections"]):
            # Extract title and description if possible
            parts = section_desc.split(":", 1)
            if len(parts) > 1:
                title = parts[0].strip()
                description = parts[1].strip()
            else:
                title = f"New Section {i+1}"
                description = section_desc
            
            # Create new section
            section_id = f"new_section_{i+1}"
            new_section = Section(
                title=title,
                description=description,
                query=f"{plan.title} {title}",
                scope={"depth": "detailed", "focus": "custom"},
            )
            
            updated_plan.sections[section_id] = new_section
            logger.debug(f"Added new section: {title}")
        
        # Update estimated time
        # Simple heuristic: 30 minutes per section
        updated_plan.estimated_time = len(updated_plan.sections) * 30
        
        return updated_plan