# Research Planning Module

This module is responsible for processing research queries, generating structured research plans, and allocating resources for research tasks.

## Components

- **query_analyzer.py**: Processes and analyzes research queries to understand intent and scope
- **research_plan_generator.py**: Creates detailed research plans with sections and objectives
- **feedback_integrator.py**: Incorporates user feedback to refine research plans
- **resource_allocator.py**: Determines computational resources needed for research tasks

## Functionality

The Research Planning module provides the following key functionality:

1. Query analysis to extract research topics, constraints, and objectives
2. Generation of structured research plans with logical organization
3. Integration of user feedback to improve plans
4. Resource allocation and scheduling for research tasks

## Usage

```python
from research_orchestrator.research_planning.query_analyzer import QueryAnalyzer
from research_orchestrator.research_planning.research_plan_generator import ResearchPlanGenerator

# Analyze a research query
analyzer = QueryAnalyzer()
query_analysis = analyzer.analyze("What are the recent advances in transformers for computer vision?")

# Generate a research plan
generator = ResearchPlanGenerator()
research_plan = generator.generate_plan(
    query_analysis=query_analysis,
    depth="comprehensive",
    focus_areas=["architectures", "applications", "performance"]
)

# Print the plan structure
for section in research_plan.sections:
    print(f"Section: {section.title}")
    for subsection in section.subsections:
        print(f"  - {subsection.title}")
```

## Integration Points

- Receives research queries from the **Core** module
- Interacts with **Information Gathering** to perform preliminary searches
- Passes completed research plans to other modules for execution
- Interfaces with **TDAG** adapter for task decomposition