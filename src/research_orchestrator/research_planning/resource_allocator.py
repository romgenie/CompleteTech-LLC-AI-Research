"""
Resource allocation module for the Research Orchestration Framework.

This module determines computational resources needed for research tasks
and schedules them appropriately.
"""

from typing import Any, Dict, List, Optional

from loguru import logger


class ResourceRequirements:
    """
    Represents resource requirements for a research task.
    
    Attributes:
        cpu_count: Number of CPU cores
        memory_mb: Memory in megabytes
        gpu_count: Number of GPUs
        storage_mb: Storage in megabytes
        max_tokens: Maximum tokens for LLM requests
        api_calls: Estimated number of API calls
    """
    
    def __init__(
        self,
        cpu_count: int = 1,
        memory_mb: int = 1024,
        gpu_count: int = 0,
        storage_mb: int = 1024,
        max_tokens: int = 4000,
        api_calls: int = 10,
    ):
        """
        Initialize resource requirements.
        
        Args:
            cpu_count: Number of CPU cores
            memory_mb: Memory in megabytes
            gpu_count: Number of GPUs
            storage_mb: Storage in megabytes
            max_tokens: Maximum tokens for LLM requests
            api_calls: Estimated number of API calls
        """
        self.cpu_count = cpu_count
        self.memory_mb = memory_mb
        self.gpu_count = gpu_count
        self.storage_mb = storage_mb
        self.max_tokens = max_tokens
        self.api_calls = api_calls
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of resource requirements
        """
        return {
            "cpu_count": self.cpu_count,
            "memory_mb": self.memory_mb,
            "gpu_count": self.gpu_count,
            "storage_mb": self.storage_mb,
            "max_tokens": self.max_tokens,
            "api_calls": self.api_calls,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceRequirements":
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation of resource requirements
            
        Returns:
            ResourceRequirements instance
        """
        return cls(
            cpu_count=data.get("cpu_count", 1),
            memory_mb=data.get("memory_mb", 1024),
            gpu_count=data.get("gpu_count", 0),
            storage_mb=data.get("storage_mb", 1024),
            max_tokens=data.get("max_tokens", 4000),
            api_calls=data.get("api_calls", 10),
        )


class ResourceAllocator:
    """
    Determines and allocates computational resources for research tasks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the resource allocator.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        
        # Set default resource limits
        self.resource_limits = {
            "cpu_count": self.config.get("max_cpu_count", 8),
            "memory_mb": self.config.get("max_memory_mb", 16384),
            "gpu_count": self.config.get("max_gpu_count", 1),
            "storage_mb": self.config.get("max_storage_mb", 102400),
            "max_tokens": self.config.get("max_tokens_per_request", 16000),
            "max_api_calls": self.config.get("max_api_calls_per_hour", 100),
        }
        
        logger.debug("Initialized ResourceAllocator")
    
    def estimate_requirements(
        self, plan: Dict[str, Any], section_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate resource requirements for a research plan or section.
        
        Args:
            plan: Research plan dictionary
            section_id: Section ID (optional, if None then estimate for the whole plan)
            
        Returns:
            Resource requirements as a dictionary
        """
        if section_id:
            # Estimate for a specific section
            section = plan.get("sections", {}).get(section_id)
            if not section:
                raise ValueError(f"Section {section_id} not found in the plan")
            
            requirements = self._estimate_section_requirements(section)
        else:
            # Estimate for the whole plan
            requirements = self._estimate_plan_requirements(plan)
        
        # Apply resource limits
        requirements = self._apply_resource_limits(requirements)
        
        return requirements.to_dict()
    
    def _estimate_section_requirements(self, section: Dict[str, Any]) -> ResourceRequirements:
        """
        Estimate resource requirements for a section.
        
        Args:
            section: Section dictionary
            
        Returns:
            ResourceRequirements object
        """
        # Extract section properties
        scope = section.get("scope", {})
        depth = scope.get("depth", "detailed")
        focus = scope.get("focus", "general")
        subsections_count = len(section.get("subsections", []))
        
        # Base requirements
        base_requirements = {
            "basic": ResourceRequirements(
                cpu_count=1,
                memory_mb=1024,
                gpu_count=0,
                storage_mb=1024,
                max_tokens=4000,
                api_calls=5,
            ),
            "detailed": ResourceRequirements(
                cpu_count=2,
                memory_mb=2048,
                gpu_count=0,
                storage_mb=2048,
                max_tokens=8000,
                api_calls=10,
            ),
            "comprehensive": ResourceRequirements(
                cpu_count=4,
                memory_mb=4096,
                gpu_count=1,
                storage_mb=4096,
                max_tokens=16000,
                api_calls=20,
            ),
        }
        
        # Get base requirements for depth
        requirements = base_requirements.get(depth, base_requirements["detailed"])
        
        # Adjust for number of subsections
        requirements.memory_mb += subsections_count * 256
        requirements.storage_mb += subsections_count * 256
        requirements.api_calls += subsections_count * 2
        
        # Adjust for special focus areas
        if focus in ["models", "architectures"]:
            requirements.gpu_count = max(requirements.gpu_count, 1)
            requirements.memory_mb *= 1.5
        
        return requirements
    
    def _estimate_plan_requirements(self, plan: Dict[str, Any]) -> ResourceRequirements:
        """
        Estimate resource requirements for a whole plan.
        
        Args:
            plan: Research plan dictionary
            
        Returns:
            ResourceRequirements object
        """
        # Start with minimal requirements
        total_requirements = ResourceRequirements()
        
        # Sum requirements for each section
        for section_id, section in plan.get("sections", {}).items():
            section_requirements = self._estimate_section_requirements(section)
            
            # Aggregate CPU, memory, and storage
            total_requirements.cpu_count = max(
                total_requirements.cpu_count, section_requirements.cpu_count
            )
            total_requirements.memory_mb += section_requirements.memory_mb
            total_requirements.storage_mb += section_requirements.storage_mb
            
            # Take maximum GPU requirement
            total_requirements.gpu_count = max(
                total_requirements.gpu_count, section_requirements.gpu_count
            )
            
            # Sum tokens and API calls
            total_requirements.max_tokens = max(
                total_requirements.max_tokens, section_requirements.max_tokens
            )
            total_requirements.api_calls += section_requirements.api_calls
        
        return total_requirements
    
    def _apply_resource_limits(self, requirements: ResourceRequirements) -> ResourceRequirements:
        """
        Apply resource limits to requirements.
        
        Args:
            requirements: Resource requirements
            
        Returns:
            Resource requirements with limits applied
        """
        requirements.cpu_count = min(requirements.cpu_count, self.resource_limits["cpu_count"])
        requirements.memory_mb = min(requirements.memory_mb, self.resource_limits["memory_mb"])
        requirements.gpu_count = min(requirements.gpu_count, self.resource_limits["gpu_count"])
        requirements.storage_mb = min(requirements.storage_mb, self.resource_limits["storage_mb"])
        requirements.max_tokens = min(requirements.max_tokens, self.resource_limits["max_tokens"])
        requirements.api_calls = min(requirements.api_calls, self.resource_limits["max_api_calls"])
        
        return requirements
    
    def schedule_tasks(
        self, plan: Dict[str, Any], max_parallel_tasks: Optional[int] = None
    ) -> Dict[str, List[str]]:
        """
        Schedule research tasks for execution.
        
        Args:
            plan: Research plan dictionary
            max_parallel_tasks: Maximum number of parallel tasks (optional)
            
        Returns:
            Dictionary mapping task groups to section IDs
        """
        # Default max parallel tasks
        if max_parallel_tasks is None:
            max_parallel_tasks = self.config.get("max_parallel_tasks", 4)
        
        # Get sections
        sections = plan.get("sections", {})
        
        # Simple scheduling strategy: group sections by depth
        task_groups = {"high_priority": [], "medium_priority": [], "low_priority": []}
        
        for section_id, section in sections.items():
            # Get section depth
            depth = section.get("scope", {}).get("depth", "detailed")
            
            # Assign to task group based on depth
            if depth == "comprehensive":
                task_groups["high_priority"].append(section_id)
            elif depth == "detailed":
                task_groups["medium_priority"].append(section_id)
            else:
                task_groups["low_priority"].append(section_id)
        
        # Always have introduction in high priority
        if "introduction" in sections:
            if "introduction" in task_groups["medium_priority"]:
                task_groups["medium_priority"].remove("introduction")
            elif "introduction" in task_groups["low_priority"]:
                task_groups["low_priority"].remove("introduction")
            
            if "introduction" not in task_groups["high_priority"]:
                task_groups["high_priority"].insert(0, "introduction")
        
        # Always have conclusion in low priority
        if "conclusion" in sections:
            for group in ["high_priority", "medium_priority"]:
                if "conclusion" in task_groups[group]:
                    task_groups[group].remove("conclusion")
            
            if "conclusion" not in task_groups["low_priority"]:
                task_groups["low_priority"].append("conclusion")
        
        return task_groups