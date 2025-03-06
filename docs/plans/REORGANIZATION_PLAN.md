# Repository Reorganization Plan

This document outlines the plan to reorganize the repository structure for better clarity, consistency, and maintainability.

## Current Issues

1. **Duplicate Module Structures**: Code exists in both root directory and under `src/`
2. **Inconsistent Import Paths**: Different import styles across files
3. **Disorganized UI Components**: Frontend files need clearer organization
4. **Mixed Top-Level Files**: Various documentation files mixed with code

## Reorganization Plan

### 1. Consolidate Modules

Move all code to the `src` directory with a consistent structure:

```
src/
├── api/                        # API server and routes
├── knowledge_graph_system/     # Knowledge graph components
├── paper_processing/           # Paper processing pipeline
├── research_implementation/    # Implementation system
├── research_orchestrator/      # Main orchestration framework
│   ├── information_gathering/  # Search and data collection
│   ├── knowledge_extraction/   # Entity and relationship extraction
│   ├── knowledge_integration/  # Graph integration
│   ├── research_generation/    # Report generation
│   └── research_understanding/ # Paper analysis
└── ui/                         # Frontend 
    ├── components/             # Shared UI components
    ├── pages/                  # Page definitions
    ├── services/               # API client services 
    └── utils/                  # Frontend utilities
```

### 2. Fix Import Paths

Update all imports to consistently use the package structure:

```python
# Change from:
from research_orchestrator.knowledge_extraction import KnowledgeExtractor

# To:
from src.research_orchestrator.knowledge_extraction import KnowledgeExtractor
```

Or set up proper package installation with:

```python
from ai_research_integration.research_orchestrator.knowledge_extraction import KnowledgeExtractor
```

### 3. Move Documentation to Dedicated Directory

Create a `docs` directory for all documentation files:

```
docs/
├── architecture/              # System architecture documents
├── modules/                   # Module-specific documentation
├── implementation_plans/      # Implementation plans
├── testing/                   # Testing documentation
└── user_guides/               # End-user documentation
```

### 4. Clean Up Root Directory

Keep only essential files in the root directory:

- README.md
- LICENSE
- setup.py
- pyproject.toml
- requirements*.txt
- docker-compose.yml
- Dockerfile.*
- .gitignore

### 5. Standardize Test Organization

Ensure all tests follow a consistent organization pattern:

```
tests/
├── knowledge_graph_system/    # Tests for knowledge graph
├── research_implementation/   # Tests for implementation system
├── research_orchestrator/     # Tests for orchestration framework
│   ├── information_gathering/ # Tests for information gathering
│   └── ...                    # Other component tests
└── ui/                        # Frontend tests
```

## Implementation Steps

1. **Create New Directory Structure**: Set up the target directory structure
2. **Move Files**: Relocate files to their new locations
3. **Update Imports**: Fix import statements throughout the codebase
4. **Update Configuration**: Adjust setup.py and other config files
5. **Update Documentation**: Ensure README and other docs reflect new structure
6. **Test**: Verify all modules function correctly with new structure

## Benefits

- **Clarity**: Clear organization makes the codebase easier to navigate
- **Consistency**: Standardized structure improves developer experience
- **Maintainability**: Logical grouping makes future changes easier
- **Reduced Confusion**: Eliminates duplicate modules and import confusion
- **Better Documentation**: Organized docs improve onboarding and reference