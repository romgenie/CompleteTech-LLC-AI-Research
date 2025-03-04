# AI Research Orchestration Framework

A comprehensive system that orchestrates the entire AI research process from query to report generation.

## Overview

The Research Orchestration Framework combines capabilities from multiple agent-based AI systems to create an end-to-end research assistant. It leverages task decomposition, information gathering, knowledge extraction, graph-based integration, and content generation to automate and enhance the AI research discovery process.

## Key Features

- **Intelligent Research Planning**: Processes research queries and creates structured research plans
- **Multi-source Information Gathering**: Collects data from academic databases, code repositories, and web sources
- **Knowledge Extraction and Integration**: Extracts structured knowledge and organizes it into a cohesive form
- **Comprehensive Report Generation**: Creates detailed research reports with proper citations and visualizations
- **Human-in-the-loop Feedback**: Incorporates researcher feedback throughout the process

## Architecture

The system is organized into five core modules:

1. **Research Planning Coordinator**: Creates structured research plans based on user queries
2. **Information Gathering System**: Collects data from multiple sources with specialized retrieval techniques
3. **Knowledge Extraction Pipeline**: Processes collected information into structured knowledge
4. **Graph-based Knowledge Integration**: Organizes discovered knowledge into interconnected graphs
5. **Research Generation System**: Produces comprehensive reports, papers, or code implementations

Each module is designed with clear interfaces, allowing them to operate independently or as part of the integrated system.

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/research_orchestrator.git
cd research_orchestrator

# Install dependencies
pip install -r requirements.txt

# Configure API credentials
cp config/api_credentials.yaml.example config/api_credentials.yaml
# Edit the file to add your credentials
```

## Usage

```python
from research_orchestrator.core.orchestrator import ResearchOrchestrator

# Initialize the orchestrator
orchestrator = ResearchOrchestrator()

# Start a new research project
project = orchestrator.create_project(
    query="What are the recent advances in reinforcement learning for robotic manipulation?",
    depth="comprehensive",  # Options: quick, standard, comprehensive
    focus_areas=["algorithms", "applications", "benchmarks"]
)

# Get the research plan and review it
plan = project.get_research_plan()
print(plan)

# Approve the plan and start research
project.approve_plan()
project.execute()

# Get the final report
report = project.get_report(format="markdown")  # Also supports PDF, HTML
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This framework integrates technology from the following projects:
- TDAG (Task Decomposition Agent Generation)
- GDesigner
- KARMA
- open_deep_research
- AutoCodeAgent2.0