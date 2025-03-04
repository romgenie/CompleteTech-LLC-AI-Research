# Coding Prompt for AI Research Integration Project

## Project Overview

This project aims to integrate capabilities from several advanced AI research repositories to create a comprehensive system for AI research discovery, knowledge extraction, and implementation. The project consists of three main systems:

1. **Research Orchestration Framework**: An end-to-end research assistant that coordinates the entire research process from query to report generation
2. **Dynamic Knowledge Graph System**: A system for building and maintaining knowledge graphs of AI research to identify patterns, trends, and gaps
3. **AI Research Implementation System**: A system that automatically implements, tests, and validates AI research concepts from papers

## Repository Structure and Documentation

### Core Documentation
- **CLAUDE.md**: Contains detailed repository information and integration plans
- **plan/**: Contains structural plans at high, mid, and low levels
  - **plan/structural/**: Detailed architectural plans for each system
  - **plan/file_structures/**: Comprehensive file structure designs for implementation

### System-specific Documentation
Each system has:
- **README.md**: Overview, features, architecture, usage examples
- **DEVELOPER_PLAN.md**: Detailed development roadmap and technical decisions
- Module-level README.md and DEVELOPER_PLAN.md files with component details

## Key Integration Points

The project integrates these existing repositories:
1. **TDAG** (Task Decomposition Agent Generation): For task decomposition and planning
2. **GDesigner**: For graph-based agent communication
3. **KARMA**: For knowledge extraction and graph construction
4. **open_deep_research**: For information gathering and research
5. **AutoCodeAgent2.0**: For code generation and implementation

## Development Guidelines

1. **Modular Architecture**: Each system should maintain clear separation of concerns with well-defined interfaces between modules.

2. **Adapter Pattern**: Use adapters for all external repository integrations to ensure loose coupling.

3. **Progressive Implementation**:
   - Phase 1: Core framework and foundational modules
   - Phase 2: Knowledge extraction and integration
   - Phase 3: Advanced features and inter-system connections
   - Phase 4: Testing, optimization, and user interfaces

4. **Technology Stack**:
   - Python 3.9+ for core development
   - Neo4j for knowledge graph storage
   - FastAPI for API development
   - Docker and Docker Compose for containerization

5. **Code Style and Practices**:
   - PEP 8 compliant Python code
   - Comprehensive type hints
   - Thorough docstrings (Google style)
   - Unit tests for all components (80%+ coverage)

## Getting Started

1. **Explore the documentation in this order**:
   - CLAUDE.md for project overview
   - plan/structural/ for architectural understanding
   - plan/file_structures/ for implementation details
   - Each system's README.md and DEVELOPER_PLAN.md

2. **Start with core modules**:
   - research_orchestrator/core/
   - knowledge_graph_system/core/
   - research_implementation/core/

3. **Implement adapter interfaces** for external repositories

4. **Follow the phased implementation approach** outlined in each system's DEVELOPER_PLAN.md

## Implementation Priorities

1. **First priority**: Research Orchestration Framework core and Research Planning
2. **Second priority**: Knowledge Graph System core and Knowledge Extractor
3. **Third priority**: Research Implementation core and Research Understanding

## Testing and Validation

- Implement comprehensive unit tests for each component
- Create integration tests for module interactions
- Develop end-to-end tests for key workflows
- Use benchmark datasets and papers to validate system performance

## Additional Resources

- External repositories can be found in ./external_repo/
- Each system's documentation contains detailed API specifications and data models
- Development plans include risk assessments and mitigation strategies

## Project Relationships

The three systems are designed to work both independently and as an integrated whole:

- **Research Orchestrator** coordinates the research process and can leverage both Knowledge Graph and Research Implementation
- **Knowledge Graph System** provides knowledge extraction and insights that can feed into both other systems
- **Research Implementation System** can implement concepts discovered by the other systems

When implementing, focus on creating clean interfaces that allow both independent operation and seamless integration.