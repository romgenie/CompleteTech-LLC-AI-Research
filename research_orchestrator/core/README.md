# Core Module - Research Orchestrator

This module contains the core components of the Research Orchestration Framework. It handles system initialization, orchestration, state management, and common utilities.

## Components

- **orchestrator.py**: Main controller that coordinates all modules and manages workflow
- **state_manager.py**: Handles project state persistence and retrieval
- **utils.py**: Common utility functions used across the system

## Responsibilities

The core module is responsible for:

1. System initialization and configuration loading
2. Coordinating workflows between different modules
3. Managing project state throughout the research process
4. Providing common utilities and helper functions
5. Handling error conditions and recovery

## Usage

```python
from research_orchestrator.core.orchestrator import ResearchOrchestrator

# Initialize the orchestrator
orchestrator = ResearchOrchestrator(config_path="path/to/config.yaml")

# Create a new research project
project = orchestrator.create_project(
    query="What are the recent advances in transformer architectures?",
    depth="comprehensive"
)

# Execute the full research workflow
orchestrator.execute_workflow(project_id=project.id)
```

## Development Guidelines

1. Keep the core module focused on orchestration and coordination
2. Avoid putting domain-specific logic here - that belongs in the respective modules
3. Ensure proper error handling and logging
4. Maintain backward compatibility for the public API
5. Include comprehensive unit tests for all functionality