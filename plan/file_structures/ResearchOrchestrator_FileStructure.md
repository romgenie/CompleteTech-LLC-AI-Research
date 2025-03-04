# File Structure: AI Research Orchestration Framework

```
research_orchestrator/
│
├── README.md                      # Project overview and documentation
├── setup.py                       # Package installation configuration
├── requirements.txt               # Python dependencies
├── config/
│   ├── default_config.yaml        # Default configuration settings
│   ├── model_registry.yaml        # Available AI models configuration
│   └── api_credentials.yaml       # Template for API credentials
│
├── core/
│   ├── __init__.py
│   ├── orchestrator.py            # Main orchestration controller
│   ├── state_manager.py           # System state management
│   └── utils.py                   # Common utilities
│
├── research_planning/
│   ├── __init__.py
│   ├── query_analyzer.py          # Process research queries
│   ├── research_plan_generator.py # Generate structured research plans
│   ├── feedback_integrator.py     # Process user feedback on plans
│   └── resource_allocator.py      # Computational resource allocation
│
├── information_gathering/
│   ├── __init__.py
│   ├── academic_connector.py      # Interface with academic databases
│   ├── code_analyzer.py           # Analyze code repositories
│   ├── web_retriever.py           # Web information retrieval
│   ├── specialized_sources.py     # AI-specific source handling
│   └── quality_assessor.py        # Information quality evaluation
│
├── knowledge_extraction/
│   ├── __init__.py
│   ├── document_processor.py      # Process documents (PDF, HTML, etc.)
│   ├── entity_recognizer.py       # Extract AI concepts and entities
│   ├── relationship_extractor.py  # Extract relationships between entities
│   ├── performance_aggregator.py  # Collect and normalize performance metrics
│   └── concept_builder.py         # Formalize concept definitions
│
├── knowledge_integration/
│   ├── __init__.py
│   ├── graph_constructor.py       # Build knowledge graph from extracted info
│   ├── contradiction_resolver.py  # Resolve conflicting information
│   ├── connection_discoverer.py   # Find non-obvious connections
│   ├── evolution_tracker.py       # Track concept evolution over time
│   └── gap_identifier.py          # Identify knowledge gaps
│
├── research_generation/
│   ├── __init__.py
│   ├── structure_planner.py       # Plan document structure
│   ├── content_synthesizer.py     # Generate coherent content
│   ├── citation_manager.py        # Handle citations and references
│   ├── visualization_generator.py # Create visualizations
│   └── code_implementer.py        # Generate example implementations
│
├── api/
│   ├── __init__.py
│   ├── routes.py                  # API endpoints
│   ├── middleware.py              # API middleware
│   └── validators.py              # Input validation
│
├── adapters/
│   ├── __init__.py
│   ├── tdag_adapter.py            # Integration with TDAG
│   ├── gdesigner_adapter.py       # Integration with GDesigner
│   ├── karma_adapter.py           # Integration with KARMA
│   ├── open_deep_research_adapter.py # Integration with open_deep_research
│   └── autocodeagent_adapter.py   # Integration with AutoCodeAgent2.0
│
├── ui/
│   ├── templates/                 # Web UI templates
│   ├── static/                    # Static assets
│   ├── components/                # UI components
│   └── pages/                     # Page definitions
│
├── db/
│   ├── models.py                  # Database models
│   ├── migrations/                # Database migrations
│   └── repositories/              # Data access patterns
│
└── tests/
    ├── unit/                      # Unit tests
    ├── integration/               # Integration tests
    ├── fixtures/                  # Test fixtures
    └── mocks/                     # Mock objects
```

## Key Design Decisions

1. **Modular Structure**: Each core component from the plan is represented as a top-level module.

2. **Adapters Pattern**: External systems are integrated through adapters, allowing for loose coupling.

3. **Configuration Management**: Separate configuration files for different aspects (defaults, models, credentials).

4. **API-First Design**: Robust API layer enables both UI and programmatic access.

5. **Dependency Injection**: Core components receive their dependencies from the orchestrator.

## Integration Approach

The `adapters/` directory contains adapter classes that serve as bridges to the external repositories:

- `tdag_adapter.py`: Integrates TDAG's task decomposition and planning capabilities
- `gdesigner_adapter.py`: Leverages GDesigner's graph-based agent communication
- `karma_adapter.py`: Uses KARMA's knowledge extraction and graph construction
- `open_deep_research_adapter.py`: Incorporates open_deep_research's information gathering
- `autocodeagent_adapter.py`: Utilizes AutoCodeAgent2.0's code generation

Each adapter implements a common interface defined in the core module, allowing the system to interact with external components in a standardized way.