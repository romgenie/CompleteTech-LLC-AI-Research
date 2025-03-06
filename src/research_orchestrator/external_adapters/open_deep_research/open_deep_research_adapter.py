"""
Open Deep Research adapter for information gathering and research capabilities.

This module provides an adapter for the open_deep_research repository, allowing the research
orchestrator to utilize its capabilities for comprehensive research and report generation.
"""

import os
import sys
import logging
import importlib.util
import json
from typing import Any, Dict, List, Optional, Union, Tuple

from ..base_adapter import BaseAdapter


# Configure logging
logger = logging.getLogger(__name__)


class OpenDeepResearchAdapter(BaseAdapter):
    """
    Adapter for the open_deep_research repository.
    
    This adapter provides integration with the open_deep_research repository, allowing
    the research orchestrator to utilize its capabilities for information gathering,
    research, and report generation.
    """
    
    # Define the capabilities provided by this adapter
    CAPABILITIES = [
        "report_generation",      # Generate comprehensive research reports
        "information_search",     # Search for information from various sources
        "search_api_integration", # Integrate with multiple search APIs
        "multi_model_planning",   # Use multiple models for planning and writing
        "interactive_feedback",   # Interactive human feedback for report approval
        "langraph_workflow"       # LangGraph-based workflow for research
    ]
    
    def __init__(self, 
                repository_path: Optional[str] = None,
                log_level: int = logging.INFO):
        """
        Initialize the Open Deep Research adapter.
        
        Args:
            repository_path: Path to the open_deep_research repository (if None, will look in standard locations)
            log_level: Logging level
        """
        self.repository_path = repository_path
        self.initialized = False
        self.odr_module = None
        self.research_engine = None
        self.search_manager = None
        
        # Configure logging
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
        
        # Try to determine repository path if not provided
        if self.repository_path is None:
            self._find_repository()
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the adapter with the provided configuration.
        
        Args:
            config: Configuration dictionary containing settings for Open Deep Research
            
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self.logger.info("Initializing Open Deep Research adapter")
            
            # Import Open Deep Research modules
            if not self._import_odr():
                return False
            
            # Configure Open Deep Research based on provided config
            default_config = {
                "planning_model": "gpt-4",
                "writing_model": "claude-3-opus",
                "use_academic_sources": True,
                "use_web_sources": True,
                "max_sources": 20,
                "max_search_results": 10,
                "log_level": "info"
            }
            
            # Merge default and provided config
            merged_config = {**default_config, **config}
            
            # Initialize components
            self._initialize_research_engine(merged_config)
            self._initialize_search_manager(merged_config)
            
            self.initialized = True
            self.logger.info("Open Deep Research adapter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Open Deep Research adapter: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """
        Check if the Open Deep Research repository is available.
        
        Returns:
            True if the repository is available, False otherwise
        """
        return self.initialized and self.odr_module is not None
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities provided by this adapter.
        
        Returns:
            List of capability strings
        """
        return self.CAPABILITIES
    
    def execute(self, 
               action: str, 
               params: Dict[str, Any], 
               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an action using the Open Deep Research repository.
        
        Args:
            action: The action to execute
            params: Parameters for the action
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        if not self.initialized:
            raise RuntimeError("Open Deep Research adapter is not initialized")
        
        self.logger.info(f"Executing action: {action}")
        
        # Map actions to corresponding methods
        action_map = {
            "generate_report": self._generate_report,
            "search_information": self._search_information,
            "get_search_apis": self._get_search_apis,
            "configure_search": self._configure_search,
            "get_report_plan": self._get_report_plan,
            "generate_section": self._generate_section,
            "provide_feedback": self._provide_feedback
        }
        
        # Check if the action is supported
        if action not in action_map:
            raise ValueError(f"Unsupported action: {action}")
        
        # Execute the action
        return action_map[action](params, context)
    
    def shutdown(self) -> bool:
        """
        Shutdown the adapter and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            self.logger.info("Shutting down Open Deep Research adapter")
            
            # Clean up any resources
            self.research_engine = None
            self.search_manager = None
            self.odr_module = None
            self.initialized = False
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to shutdown Open Deep Research adapter: {str(e)}")
            return False
    
    def _find_repository(self) -> None:
        """
        Find the Open Deep Research repository path.
        
        This method tries to find the repository in standard locations.
        """
        # List of standard locations to check
        standard_locations = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../external_repo/open_deep_research"),
            os.path.join(os.path.expanduser("~"), "open_deep_research"),
            "/opt/open_deep_research",
            os.getenv("OPEN_DEEP_RESEARCH_PATH")
        ]
        
        # Check each location
        for location in standard_locations:
            if location and os.path.exists(location) and os.path.isdir(location):
                self.repository_path = location
                self.logger.info(f"Found Open Deep Research repository at: {location}")
                return
        
        self.logger.warning("Could not find Open Deep Research repository")
    
    def _import_odr(self) -> bool:
        """
        Import the Open Deep Research modules.
        
        Returns:
            True if imports were successful, False otherwise
        """
        if not self.repository_path:
            self.logger.error("Open Deep Research repository path is not set")
            return False
        
        try:
            # Add repository path to sys.path
            if self.repository_path not in sys.path:
                sys.path.append(self.repository_path)
            
            # Try to import the main module
            spec = importlib.util.find_spec("open_deep_research")
            if spec is None:
                # If not found directly, try subdirectory
                odr_path = os.path.join(self.repository_path, "src")
                if odr_path not in sys.path:
                    sys.path.append(odr_path)
                spec = importlib.util.find_spec("open_deep_research")
            
            if spec is None:
                self.logger.error("Could not find Open Deep Research module")
                return False
            
            # Import module
            self.odr_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.odr_module)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to import Open Deep Research modules: {str(e)}")
            return False
    
    def _initialize_research_engine(self, config: Dict[str, Any]) -> None:
        """
        Initialize the research engine.
        
        Args:
            config: Configuration dictionary
        """
        # For now, this is a stub as we don't have direct access to the codebase
        self.research_engine = {
            "planning_model": config["planning_model"],
            "writing_model": config["writing_model"],
            "max_sources": config["max_sources"],
            "use_academic_sources": config["use_academic_sources"],
            "use_web_sources": config["use_web_sources"],
            "active_searches": [],
            "generated_reports": []
        }
        
        # In a real implementation, this would initialize the research engine from the repository
        # For example:
        # self.research_engine = self.odr_module.ResearchEngine(
        #     planning_model=config["planning_model"],
        #     writing_model=config["writing_model"],
        #     use_academic_sources=config["use_academic_sources"],
        #     use_web_sources=config["use_web_sources"]
        # )
    
    def _initialize_search_manager(self, config: Dict[str, Any]) -> None:
        """
        Initialize the search manager.
        
        Args:
            config: Configuration dictionary
        """
        # For now, this is a stub as we don't have direct access to the codebase
        self.search_manager = {
            "max_search_results": config["max_search_results"],
            "api_status": {
                "tavily": {"enabled": True, "quota_remaining": 100},
                "perplexity": {"enabled": True, "quota_remaining": 100},
                "exa": {"enabled": True, "quota_remaining": 100},
                "arxiv": {"enabled": config["use_academic_sources"], "quota_remaining": None},
                "pubmed": {"enabled": config["use_academic_sources"], "quota_remaining": None},
                "linkup": {"enabled": config["use_web_sources"], "quota_remaining": 100}
            },
            "default_apis": ["tavily", "perplexity"]
        }
        
        # In a real implementation, this would initialize the search manager from the repository
        # For example:
        # self.search_manager = self.odr_module.SearchManager(
        #     max_results=config["max_search_results"]
        # )
    
    def _generate_report(self, 
                        params: Dict[str, Any], 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive research report.
        
        Args:
            params: Parameters for report generation
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract parameters
        query = params.get("query", "")
        depth = params.get("depth", "comprehensive")
        format = params.get("format", "markdown")
        max_length = params.get("max_length", 5000)
        search_apis = params.get("search_apis", self.search_manager["default_apis"])
        
        # For now, this is a stub as we don't have direct access to the codebase
        
        # Mock report generation
        import random
        import time
        from datetime import datetime
        
        # Simulate processing time
        processing_time = random.uniform(5, 15)
        time.sleep(min(0.5, processing_time / 10))  # Simulate a fraction of the processing time
        
        # Calculate word count based on max_length
        word_count = min(random.randint(2000, 10000), max_length)
        
        # Generate mock report
        report_id = f"report_{int(time.time())}"
        report_title = f"Research Report: {query}"
        
        # Generate mock sections
        sections = []
        section_titles = [
            "Introduction",
            "Background and Context",
            "Current State of Research",
            "Key Developments and Findings",
            "Analysis and Implications",
            "Future Directions",
            "Conclusion"
        ]
        
        for i, title in enumerate(section_titles):
            section_length = word_count // len(section_titles)
            sections.append({
                "title": title,
                "content": f"Content for section {i+1}: {title}. This section contains approximately {section_length} words.",
                "word_count": section_length,
                "sources": random.randint(3, 8)
            })
        
        # Generate mock source citations
        sources = []
        for i in range(random.randint(10, 20)):
            source_type = random.choice(["academic", "web", "book", "paper"])
            sources.append({
                "id": f"source_{i+1}",
                "title": f"Source {i+1} for {query}",
                "type": source_type,
                "url": f"https://example.com/source_{i+1}" if source_type == "web" else None,
                "author": f"Author {i+1}",
                "date": f"202{random.randint(0, 3)}"
            })
        
        # Add report to research engine
        self.research_engine["generated_reports"].append({
            "id": report_id,
            "title": report_title,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sections": [s["title"] for s in sections],
            "sources": len(sources)
        })
        
        result = {
            "success": True,
            "report_id": report_id,
            "title": report_title,
            "query": query,
            "word_count": word_count,
            "processing_time": processing_time,
            "format": format,
            "sections": sections,
            "sources": sources,
            "search_apis_used": search_apis
        }
        
        return result
    
    def _search_information(self, 
                           params: Dict[str, Any], 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for information from various sources.
        
        Args:
            params: Parameters for information search
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract parameters
        query = params.get("query", "")
        search_apis = params.get("search_apis", self.search_manager["default_apis"])
        max_results = params.get("max_results", self.search_manager["max_search_results"])
        include_academic = params.get("include_academic", self.research_engine["use_academic_sources"])
        filters = params.get("filters", {})
        
        # For now, this is a stub as we don't have direct access to the codebase
        
        # Mock search results
        import random
        import time
        from datetime import datetime, timedelta
        
        # Generate a search ID
        search_id = f"search_{int(time.time())}"
        
        # Determine which APIs to use
        apis_used = []
        for api in search_apis:
            if api in self.search_manager["api_status"] and self.search_manager["api_status"][api]["enabled"]:
                apis_used.append(api)
        
        # If academic sources are requested, add them
        if include_academic:
            for api in ["arxiv", "pubmed"]:
                if api in self.search_manager["api_status"] and self.search_manager["api_status"][api]["enabled"]:
                    apis_used.append(api)
        
        # Generate results per API
        results = []
        for api in apis_used:
            # Number of results from this API
            num_results = random.randint(3, max_results)
            
            for i in range(num_results):
                # Generate a random date within the last 5 years
                date = datetime.now() - timedelta(days=random.randint(0, 365 * 5))
                
                # Create result based on API type
                if api in ["arxiv", "pubmed"]:
                    # Academic source
                    result = {
                        "id": f"{api}_{i+1}",
                        "title": f"{api.capitalize()} result {i+1} for: {query}",
                        "source": api,
                        "url": f"https://{api}.org/article/{random.randint(1000, 9999)}.{random.randint(1000, 9999)}",
                        "authors": [f"Author {j+1}" for j in range(random.randint(1, 4))],
                        "published_date": date.strftime("%Y-%m-%d"),
                        "abstract": f"Abstract for result {i+1} from {api} about {query}",
                        "relevance_score": random.uniform(0.7, 0.95)
                    }
                else:
                    # Web source
                    result = {
                        "id": f"{api}_{i+1}",
                        "title": f"{api.capitalize()} result {i+1} for: {query}",
                        "source": api,
                        "url": f"https://example.com/{api}/{random.randint(1000, 9999)}",
                        "snippet": f"Snippet from {api} search result about {query}...",
                        "published_date": date.strftime("%Y-%m-%d"),
                        "relevance_score": random.uniform(0.7, 0.95)
                    }
                
                results.append(result)
        
        # Sort results by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Limit results to max_results
        results = results[:max_results]
        
        # Add search to active searches
        self.research_engine["active_searches"].append({
            "id": search_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "apis_used": apis_used,
            "num_results": len(results)
        })
        
        # Prepare metadata
        metadata = {
            "apis_used": apis_used,
            "num_results": len(results),
            "max_results": max_results,
            "filters_applied": filters,
            "processing_time": random.uniform(0.5, 3.0)
        }
        
        return {
            "success": True,
            "search_id": search_id,
            "query": query,
            "results": results,
            "metadata": metadata
        }
    
    def _get_search_apis(self, 
                        params: Dict[str, Any], 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get information about available search APIs.
        
        Args:
            params: Parameters (not used)
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract relevant information about APIs
        apis = []
        for api_name, api_info in self.search_manager["api_status"].items():
            apis.append({
                "name": api_name,
                "enabled": api_info["enabled"],
                "quota_remaining": api_info["quota_remaining"],
                "type": "academic" if api_name in ["arxiv", "pubmed"] else "web"
            })
        
        return {
            "success": True,
            "apis": apis,
            "default_apis": self.search_manager["default_apis"]
        }
    
    def _configure_search(self, 
                         params: Dict[str, Any], 
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Configure search settings.
        
        Args:
            params: Parameters for search configuration
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract parameters
        max_results = params.get("max_results")
        default_apis = params.get("default_apis")
        enabled_apis = params.get("enabled_apis")
        
        # Update configuration
        if max_results is not None:
            self.search_manager["max_search_results"] = max_results
        
        if default_apis is not None:
            # Validate that all default APIs exist
            valid_apis = [api for api in default_apis if api in self.search_manager["api_status"]]
            self.search_manager["default_apis"] = valid_apis
        
        if enabled_apis is not None:
            # Update enabled status for each API
            for api_name, enabled in enabled_apis.items():
                if api_name in self.search_manager["api_status"]:
                    self.search_manager["api_status"][api_name]["enabled"] = enabled
        
        return {
            "success": True,
            "max_results": self.search_manager["max_search_results"],
            "default_apis": self.search_manager["default_apis"],
            "api_status": self.search_manager["api_status"]
        }
    
    def _get_report_plan(self, 
                        params: Dict[str, Any], 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a plan for a research report.
        
        Args:
            params: Parameters for report planning
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract parameters
        query = params.get("query", "")
        depth = params.get("depth", "comprehensive")
        
        # For now, this is a stub as we don't have direct access to the codebase
        
        # Generate a mock report plan
        import random
        
        # Create a report ID
        report_id = f"report_plan_{int(time.time())}"
        
        # Generate section outlines based on depth
        if depth == "brief":
            num_sections = random.randint(3, 5)
        elif depth == "comprehensive":
            num_sections = random.randint(5, 8)
        else:  # depth == "detailed"
            num_sections = random.randint(7, 12)
        
        # Create section templates
        section_templates = [
            {"title": "Introduction", "content": "Introduction to the topic, including background and context."},
            {"title": "Background", "content": "Historical context and foundational concepts."},
            {"title": "Current Research", "content": "Overview of current research and recent developments."},
            {"title": "Key Technologies", "content": "Description of key technologies and methodologies."},
            {"title": "Applications", "content": "Real-world applications and use cases."},
            {"title": "Challenges", "content": "Current challenges and limitations."},
            {"title": "Future Directions", "content": "Potential future developments and research directions."},
            {"title": "Ethical Considerations", "content": "Ethical implications and considerations."},
            {"title": "Comparative Analysis", "content": "Comparison of different approaches and methodologies."},
            {"title": "Case Studies", "content": "Detailed case studies and examples."},
            {"title": "Industry Impact", "content": "Impact on industry and economic considerations."},
            {"title": "Conclusion", "content": "Summary and concluding thoughts."}
        ]
        
        # Select a subset of sections based on the desired depth
        selected_sections = random.sample(section_templates, min(num_sections, len(section_templates)))
        
        # Ensure Introduction and Conclusion are included
        intro_included = any(s["title"] == "Introduction" for s in selected_sections)
        conclusion_included = any(s["title"] == "Conclusion" for s in selected_sections)
        
        if not intro_included:
            intro = next(s for s in section_templates if s["title"] == "Introduction")
            selected_sections.insert(0, intro)
        
        if not conclusion_included:
            conclusion = next(s for s in section_templates if s["title"] == "Conclusion")
            selected_sections.append(conclusion)
        
        # Generate search queries for each section
        for section in selected_sections:
            section["search_queries"] = [
                f"{query} {section['title'].lower()}",
                f"{section['title'].lower()} in {query}",
                f"recent developments in {query} {section['title'].lower()}"
            ]
        
        return {
            "success": True,
            "report_id": report_id,
            "query": query,
            "depth": depth,
            "sections": selected_sections,
            "estimated_length": num_sections * 500,  # words
            "estimated_sources": num_sections * 3,   # sources
            "requires_feedback": True
        }
    
    def _generate_section(self, 
                         params: Dict[str, Any], 
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a section for a research report.
        
        Args:
            params: Parameters for section generation
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract parameters
        report_id = params.get("report_id", "")
        section_title = params.get("section_title", "")
        search_queries = params.get("search_queries", [])
        max_length = params.get("max_length", 1000)
        
        # For now, this is a stub as we don't have direct access to the codebase
        
        # Generate a mock section
        import random
        import time
        
        # Simulate processing time
        processing_time = random.uniform(2, 8)
        time.sleep(min(0.5, processing_time / 10))  # Simulate a fraction of the processing time
        
        # Generate mock sources
        sources = []
        for i in range(random.randint(3, 6)):
            source_type = random.choice(["academic", "web", "book", "paper"])
            sources.append({
                "id": f"source_{i+1}",
                "title": f"Source {i+1} for {section_title}",
                "type": source_type,
                "url": f"https://example.com/source_{i+1}" if source_type == "web" else None,
                "author": f"Author {i+1}",
                "date": f"202{random.randint(0, 3)}"
            })
        
        # Generate mock content
        content = f"""
        # {section_title}
        
        This is the content for the {section_title} section. It provides detailed information
        related to the topic based on multiple sources.
        
        ## Key Points
        
        - First key point about {section_title}
        - Second key point with additional details
        - Third key point with reference to recent research
        
        ## Detailed Analysis
        
        The analysis shows that there are several important factors to consider.
        According to [Source {random.randint(1, len(sources))}], the primary considerations are...
        
        ## Summary
        
        In summary, the {section_title} demonstrates the importance of...
        """
        
        # Calculate word count
        word_count = min(len(content.split()), max_length)
        
        return {
            "success": True,
            "report_id": report_id,
            "section_title": section_title,
            "content": content,
            "word_count": word_count,
            "processing_time": processing_time,
            "sources": sources,
            "search_queries_used": search_queries
        }
    
    def _provide_feedback(self, 
                         params: Dict[str, Any], 
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide feedback on a report plan or section.
        
        Args:
            params: Parameters for feedback
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        # Extract parameters
        report_id = params.get("report_id", "")
        feedback_type = params.get("feedback_type", "plan")  # "plan" or "section"
        section_title = params.get("section_title", "")
        approved = params.get("approved", True)
        feedback = params.get("feedback", "")
        
        # For now, this is a stub as we don't have direct access to the codebase
        
        if feedback_type == "plan":
            response = {
                "success": True,
                "report_id": report_id,
                "feedback_type": feedback_type,
                "approved": approved,
                "action_taken": "proceed" if approved else "revise_plan",
                "next_steps": "Generating sections" if approved else "Revising plan based on feedback"
            }
        else:  # section feedback
            response = {
                "success": True,
                "report_id": report_id,
                "feedback_type": feedback_type,
                "section_title": section_title,
                "approved": approved,
                "action_taken": "proceed" if approved else "revise_section",
                "next_steps": "Moving to next section" if approved else "Revising section based on feedback"
            }
        
        return response