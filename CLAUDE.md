# CLAUDE.md - Repository Reference

This file contains key information about the repositories in this workspace and their functionalities.

> **Initial Development Statistics (Outdated):**  
> Total cost: $31.94  
> Total duration (API): 2h 37m 27.9s  
> Total duration (wall): 9h 17m 7.9s  

## Project Implementation Status

> **Updated Implementation Statistics:**  
> Total cost: $57.17  
> Total duration (API): 4h 25m 53.3s  
> Total duration (wall): 12h 25m 19.1s  

### Current Implementation Progress

We have implemented the following components for the AI Research Integration Project (all core components are now complete):

1. **TDAG Adapter**
   - Created adapter interface for the TDAG framework
   - Implemented task decomposition functionality
   - Integrated planning capabilities with the Research Orchestration Framework

2. **Information Gathering Module**
   - Implemented SearchManager to coordinate search operations across multiple sources
   - Created SourceManager for registering and managing different information sources
   - Developed QualityAssessor for evaluating search result quality
   - Implemented source adapters for different types of information:
     - AcademicSource: For scholarly articles and papers from ArXiv, PubMed, Semantic Scholar
     - WebSource: For web search through Serper, SerpAPI, Tavily, Perplexity
     - CodeSource: For code repositories like GitHub, GitLab, Hugging Face, PyPI
     - AISource: For LLM-generated information via OpenAI, Anthropic, Cohere, local models

3. **Knowledge Extraction Pipeline**
   - **Document Processing Engine**:
     - Implemented DocumentProcessor with support for different document types
     - Created specialized processors for PDF, HTML, and plain text documents
     - Added content extraction and preprocessing capabilities
   - **Entity Recognition System** ✅:
     - Implemented base EntityRecognizer with core functionality
     - Created AIEntityRecognizer for AI-specific concepts (models, datasets, metrics)
     - Created ScientificEntityRecognizer for research concepts (methodologies, findings)
     - Implemented EntityRecognizerFactory for easy creation and configuration
     - Added CombinedEntityRecognizer for integrating multiple recognizers
     - Created comprehensive entity type system with 35+ entity types organized in categories
     - Implemented core entity types (MODEL, ALGORITHM, DATASET, PAPER, AUTHOR, CODE)
     - Added specialized AI entity types (ARCHITECTURE, PARAMETER, FRAMEWORK)
     - Added scientific entity types (THEORY, METHODOLOGY, FINDING, HYPOTHESIS)
     - Implemented confidence scoring and conflict resolution
     - Added serialization and statistics generation capabilities
   - **Relationship Extraction Module** ✅:
     - Implemented base RelationshipExtractor with core functionality
     - Created PatternRelationshipExtractor using regex patterns
     - Developed AIRelationshipExtractor for AI research relationships
     - Implemented CombinedRelationshipExtractor with conflict resolution
     - Created RelationshipExtractorFactory for extractor creation and configuration
     - Developed comprehensive relationship type system with 50+ types organized in categories
     - Implemented core relationship types (IS_A, PART_OF, BUILDS_ON, OUTPERFORMS)
     - Added AI research relationships (TRAINED_ON, EVALUATED_ON, HAS_CODE)
     - Added scientific relationships (CITES, HYPOTHESIZES, PROVES, CONFIRMS, REPLICATES)
     - Added academic relationships (AUTHORED_BY, AFFILIATED_WITH, COLLABORATES_WITH)
     - Added derivation relationships (DERIVED_FROM, BASIS_FOR)
     - Implemented bidirectional relationship mapping and inverse relationships
     - Added entity type-based relationship mapping
     - Added confidence scoring, context analysis, and network analysis utilities
   - **Knowledge Extractor** ✅:
     - Created KnowledgeExtractor to coordinate the extraction process
     - Implemented document processing integration for text, HTML, and PDF
     - Built knowledge graph creation from entities and relationships
     - Added querying capabilities for entities, relationships, and paths
     - Created extraction results management and serialization
     - Implemented statistical analysis and filtering capabilities
     - Added comprehensive examples and documentation

4. **Knowledge Graph System Core**
   - **Graph Database Management**:
     - Created Neo4jManager for Neo4j connection and query management
     - Implemented configuration through files, environment variables, and direct parameters
     - Added utilities for managing constraints and indexes
   - **Knowledge Graph Models**:
     - Developed base GraphEntity and GraphRelationship models
     - Created AI-specific entity models (AIModel, Dataset, Paper, Algorithm, etc.)
     - Implemented specialized relationship models (TrainedOn, Outperforms, etc.)
   - **Knowledge Graph Manager**:
     - Created high-level KnowledgeGraphManager for graph operations
     - Implemented methods for adding, querying, and updating entities and relationships
     - Added utilities for finding paths, detecting contradictions, and computing stats
   - **Schema Management**:
     - Developed comprehensive schema definition for AI research entities and relationships
     - Created validation utilities to ensure data integrity
     - Implemented schema visualization and generation tools
   - **Integration with Research Orchestrator** ✅:
     - Created KnowledgeGraphAdapter for Research Orchestration Framework
     - Implemented entity and relationship conversion utilities
     - Added methods for knowledge enrichment and querying
     - Implemented local storage fallback for disconnected operation

5. **Research Implementation System Core**
   - **Implementation Manager**:
     - Created ImplementationManager to coordinate the implementation process
     - Developed workflow for paper understanding, planning, and implementation
     - Built lifecycle management from paper to verified implementation
   - **Data Models and Utilities**:
     - Implemented paper and implementation data models
     - Created utilities for code evaluation and verification
     - Built configuration and state management systems

6. **Technical Infrastructure** ✅
   - **API Framework**:
     - Implemented FastAPI application with comprehensive endpoints
     - Created authentication system with JWT tokens
     - Built request validation with Pydantic models
     - Implemented error handling and logging middleware
   - **Database Integration**:
     - Created database connection modules for Neo4j and MongoDB
     - Implemented dependency injection for database connections
     - Added database health checks and monitoring
   - **API Endpoints**:
     - Implemented knowledge graph endpoints for entities and relationships
     - Created research orchestration endpoints for managing research tasks
     - Built research implementation endpoints for paper processing
   - **Containerization**:
     - Configured Docker Compose for Neo4j, MongoDB, and API services
     - Created Dockerfile for API application
     - Implemented environment variable configuration
     - Successfully tested deployment with working services

### Implementation Achievements

1. **Knowledge Extraction Pipeline (Completed)** ✅
   - ✅ Entity Recognition System for identifying AI and scientific entities
   - ✅ Relationship Extraction Module for identifying connections between entities
   - ✅ Knowledge Extraction Coordinator for integrating extraction components
   - ✅ Document Processing Engine for different document formats
   - ✅ Knowledge graph creation and querying capabilities
   - ✅ Enhanced entity type system with 35+ entity types in organized categories
   - ✅ Enhanced relationship type system with 50+ relationship types in organized categories

2. **Knowledge Graph Integration (Completed)** ✅
   - ✅ Connection discovery engine for finding relationships between entities
   - ✅ Contradiction resolution system for handling conflicting information
   - ✅ Knowledge Graph Adapter for coordinating integration with Research Orchestrator
   - ✅ Entity and relationship conversion between extraction and graph formats
   - ✅ Local storage fallback for offline operation
   - ✅ Temporal evolution tracker for tracking changes over time
   - ✅ Knowledge gap identification for research opportunities

3. **Research Understanding Engine (Completed)** ✅
   - ✅ Paper parsing and processing systems for extracting structured information
     - ✅ Created specialized processors for different document formats (PDF, HTML, text)
     - ✅ Implemented comprehensive document structure extraction
     - ✅ Built section, figure, table, and reference extraction utilities
   - ✅ Algorithm and architecture extraction for implementation details
     - ✅ Implemented pattern-based and semantic algorithm extraction
     - ✅ Created pseudocode parser and analyzers for complexity assessment
     - ✅ Added support for extracting algorithm parameters and subroutines
   - ✅ Implementation detail collection for code generation
     - ✅ Built comprehensive code snippet extraction system
     - ✅ Implemented hyperparameter, dataset, and evaluation metric extraction
     - ✅ Created library usage detection and environment analysis
     - ✅ Added implementation reference detection from papers
   - ✅ Cross-paper analysis and knowledge integration
     - ✅ Implemented paper comparison and relationship analysis
     - ✅ Created knowledge graph export functionality
     - ✅ Added support for ArXiv paper retrieval and processing

4. **External Repository Adapters (Completed)** ✅
   - ✅ GDesigner adapter for graph-based agent communication
   - ✅ open_deep_research adapter for information gathering and research
   - ✅ AutoCodeAgent2.0 adapter for code generation and implementation

5. **Research Generation System (Completed)** ✅
   - ✅ Report structure planning for organized output
     - Implemented ReportStructurePlanner with document type classification
     - Created templates for 10+ document types (research papers, white papers, book chapters, etc.)
     - Added section organization and audience adaptation capabilities
     - Implemented section outlining and structure customization features
     - Added 50+ section types with specialized categorization for different document types
     - Incorporated ethics, funding, security, and performance evaluation sections
     - Enhanced templates with more comprehensive section categories
   - ✅ Content synthesis engine for coherent text
     - Implemented ContentSynthesisEngine for AI-powered content generation
     - Created flexible template system with support for different document types and section styles
     - Added LLM integration with ChatOpenAI and ChatAnthropic models
     - Implemented sophisticated prompt engineering for high-quality content generation
     - Added knowledge graph integration for context-aware content
     - Created both template-based and full LLM-based generation modes
     - Added comprehensive template directory structure with default templates
     - Implemented section-specific and document-level generation capabilities
     - Added graceful fallbacks and error handling for all generation modes
   - ✅ Citation management system for proper attribution
     - Implemented CitationManager for handling citations and references
     - Created CitationFormatter with support for 7 citation styles (APA, MLA, Chicago, IEEE, Harvard, Vancouver, Nature)
     - Added in-text citation processing with placeholder replacement
     - Implemented comprehensive reference list generation
     - Added bibliography import/export in multiple formats (JSON, BibTeX, CSV)
     - Created citation validation system to ensure proper formatting
     - Added DOI resolution and metadata retrieval functionality
     - Implemented integration with knowledge graph for enhanced paper information
     - Added citation lookup by keywords, DOI, and other identifiers
     - Created local caching system for citation information
   - ✅ Visualization generation tools for data representation
     - Implemented VisualizationGenerator for charts, graphs, and diagrams
     - Created comprehensive visualization type system with 35+ chart and diagram types
     - Added support for custom styling, layouts, and configurations
     - Implemented data transformation utilities for different visualization formats
     - Created intelligent defaults and fallbacks for various data structures
     - Added integration with Knowledge Graph for data-driven visualizations
     - Implemented multiple output formats (PNG, SVG, PDF, HTML, Markdown, Base64)
     - Created highly customizable visualization configuration system
     - Added specialized visualizations for network data and relationships
     - Integrated visualization capabilities into the Content Synthesis Engine
   - ✅ Code example generation
     - Implemented CodeExampleGenerator with support for multiple programming languages
     - Created comprehensive language adapters for Python, JavaScript, Java, C++, and R
     - Added template-based code generation system with customizable parameters
     - Implemented programming language-specific formatters and documentation styles
     - Added support for generating classes, functions, and algorithms
     - Created template manager with library of code templates for common use cases
     - Added integration with visualization and citation systems
     - Implemented code structure generation for research algorithms and models
     - Created documentation generation following language-specific standards
     - Added automatic imports management and dependency resolution
   - ✅ Integration with Research Orchestrator for end-to-end research workflow
     - Implemented ContentGenerator to coordinate the end-to-end generation process
     - Added robust error handling and recovery mechanisms for resilient processing
     - Created fallback implementations for all components to ensure graceful degradation
     - Implemented knowledge storage and retrieval for report generation
     - Enhanced orchestrator to manage the full research workflow with proper state management
     - Added document and section-specific generation capabilities
     - Created comprehensive interfaces between knowledge extraction and content generation
     - Implemented efficient knowledge combination from multiple sections
     - Added support for various output formats (markdown, HTML) with consistent styling

## External Repositories

### 1. AutoCodeAgent2.0
- **Dual-mode AI agent (IntelliChain and Deep Search)**: The system implements two distinct operational modes managed through app.py. IntelliChain executes via the CodeAgent class, employing a task decomposition strategy centered on generating executable Python code. Deep Search operates through DeepSearchAgentPlanner, which coordinates a multi-agent collaborative chain for autonomous web research.
- **IntelliChain: Task decomposition, code generation, and execution**: IntelliChain breaks complex tasks into subtasks using PlanGenerator to create structured JSON plans. Each subtask's code is validated for security and functionality by FunctionValidator before execution. SubtaskExecutor runs the validated code and handles failures through a regeneration system that can reattempt execution up to three times.
- **Deep Search: Autonomous web research and knowledge synthesis**: Deep Search enables autonomous web research through a planner system that creates a chain of specialized agents. The DeepSearchAgentPlanner coordinates agents that each tackle specific aspects of research queries. WebSearchAgent fetches and processes real-time information from search engines, and outputs are combined into comprehensive HTML reports.
- **Multiple RAG techniques for information retrieval**: The system implements five distinct RAG techniques: Simple RAG uses basic vector retrieval with ChromaDB, Hybrid Vector Graph RAG combines vector embeddings with Neo4j graph relationships, LlamaIndex RAG handles complex documents, HyDE RAG generates hypothetical documents to improve retrieval relevance, and Adaptive RAG adjusts retrieval based on query characteristics.
- **SurfAI integration for web navigation and interaction**: SurfAI provides web automation capabilities through a state machine architecture. BrowserManager creates and manages Playwright browser contexts, CommandExecutor translates natural language into browser interactions, and ScreenshotManager captures visual data, enabling complex web interactions including form filling, data extraction, and navigation.
- **Docker-based deployment with Neo4j and Redis**: The system uses Docker Compose to orchestrate three services: a Flask web application, Neo4j graph database for storing the Evolving Graph of Thought (EGOT), and Redis for maintaining persistent user sessions. Docker volumes ensure data persistence across container restarts, with health checks to verify database availability.

### 2. TDAG (Task Decomposition Agent Generation)
- **Multi-agent framework for complex problem-solving**: The TDAG framework implements a hierarchical multi-agent system where specialized agents collaborate to solve complex tasks. The system is built around a central MainAgent that coordinates the workflow, supported by specialized agents like SubAgent, VerifyAgent, and AgentGenerator. These agents communicate through a structured message-passing interface using standardized prompt templates and a shared state management system.
- **Dynamic task decomposition and agent generation**: TDAG dynamically breaks down complex tasks through the AgentGenerator class, which analyzes tasks and generates appropriate sub-agents. The framework maintains a skill library in JSON format that stores previously solved subtasks, allowing it to reuse solutions for similar tasks. When encountering new tasks, the system dynamically evaluates similarity with existing skills, either creating new agents or updating existing ones.
- **Multiple agent types (main, react, plan and execute, verify, etc.)**: The system implements specialized agent types forming a comprehensive problem-solving ecosystem: MainAgent coordinates the overall workflow, ReactAgent implements reasoning and acting loops, PlanAndExecute Agent separates planning from execution, VerifyAgent validates solutions against requirements, and AgentGenerator dynamically creates custom agents.
- **External API integrations (Bing, WolframAlpha, Gmail, Calendar)**: The system integrates multiple external services with dedicated modules in the API directory. Bing API provides web search functionality, WolframAlpha integration enables computational knowledge queries, and Gmail/Google Calendar integrations use Google's API client libraries with OAuth2 authentication for email and calendar management.
- **Web service architecture with FastAPI**: TDAG uses FastAPI to create a modular API-driven architecture defined in serve.py. The system dynamically registers multiple service routers based on configuration settings, with custom middleware for request/response logging and error handling. Each service is implemented as a standalone router module registered with the main FastAPI application.
- **Travel planning demonstration scenarios**: The travel planning system demonstrates complex task planning through a simulator that models multi-city travel itineraries. The TravelSimulator class implements a state machine tracking traveler location, budget, and time constraints, with sophisticated error detection and scoring mechanisms evaluating plans against efficiency metrics.

### 3. GDesigner
- **Graph-based multi-agent system for complex task solving**: GDesigner implements a graph-based multi-agent system through its Graph class which manages a collection of agent nodes that collaborate on complex tasks. Agents are instantiated from a registry and connected according to configurable graph topologies. Execution follows a topological sort where nodes with zero in-degree execute first, then activate their successors.
- **Dynamic graph topology for agent communication**: The system implements dynamic graph topologies through configurable adjacency matrices represented as spatial and temporal masks. In optimized mode, edge connections are determined probabilistically using logits that can be trained. Edges can be dynamically pruned based on importance scores, removing less useful connections over time.
- **Support for different graph structures**: GDesigner offers multiple pre-defined graph topologies including FullConnected (all-to-all connections), Chain (sequential processing), Star (central node connected to all others), Mesh (upper triangular connections), Random (randomly generated connections), and Layered (nodes organized in sequential layers). Each topology is implemented by generating appropriate adjacency matrices.
- **Evaluation on benchmark datasets (MMLU, HumanEval, GSM8K)**: The system is evaluated on multiple benchmark datasets through dedicated experiment runners that load appropriate datasets, instantiate graphs with the specified topology, and execute the agent network. Each experiment captures detailed results including individual answers, overall accuracy, and execution metrics like token usage and runtime.
- **GNN-based agent coordination**: GDesigner employs a Graph Neural Network (GCN) to enhance agent coordination by learning optimal communication patterns. The GCN processes agent profile embeddings along with query embeddings to compute edge importance scores that determine which agents should communicate. The architecture consists of GCN layers that propagate information along the role-based adjacency matrix.

### 4. KARMA
- **Framework for automated knowledge graph enrichment**: KARMA uses a natural language processing framework that coordinates specialized LLM agents to extract scientific knowledge. The system processes documents, extracts knowledge triples (subject-relation-object), and integrates them into knowledge graphs with quality metrics.
- **Multi-agent system for scientific knowledge extraction**: The system employs multiple specialized LLM agents working together to extract knowledge from scientific literature. These agents have different roles in the pipeline including document processing, entity recognition, and relationship identification.
- **Quality validation with scoring (confidence, clarity, relevance)**: KARMA implements a multi-dimensional scoring system that evaluates extracted knowledge triples on confidence, clarity, and relevance metrics. The output format shows these scores attached to each knowledge triple, enabling filtering based on quality thresholds.
- **Document processing for PDF and text formats**: The system includes capabilities for parsing PDFs and text documents, with context-aware content segmentation and summarization functionalities. It uses tools like PyPDF2 for PDF processing.
- **Entity recognition and relationship identification**: KARMA extracts entities and their relationships from scientific text to form semantic triples. The system leverages both LLMs and traditional NLP tools to identify meaningful entities and the relationships between them.
- **Knowledge graph integration and conflict resolution**: The system incorporates extracted knowledge into graphs while maintaining semantic consistency. It includes conflict resolution as part of the knowledge extraction process and uses networkx for knowledge graph operations.

### 5. AgentLaboratory
- Empty or incomplete repository

### 6. open_deep_research
- **AI-powered research assistant generating comprehensive reports**: The system implements an orchestrated workflow using a LangGraph-based state machine that handles the full research process. It begins by generating a report plan, developing structured section outlines after performing initial web searches. The system then creates targeted search queries for each section, retrieves information, and transforms search results into coherent, formatted report sections.
- **Multi-model flexibility for planning and writing phases**: The framework implements a flexible configuration system that allows separate LLM selection for planning and writing phases. This design enables optimal model selection, with planning models focusing on overall structure and reasoning while writing models handle content generation, providing cost optimization by using more powerful models only for complex planning tasks.
- **Integration with multiple search APIs**: The system implements a pluggable search framework with dedicated functions for Tavily, Perplexity, Exa, ArXiv, PubMed, and Linkup. Each function handles API-specific parameters, rate limiting, error handling, and response formatting to a standardized structure, allowing seamless switching between general web search and specialized academic sources.
- **Human-in-the-loop feedback for report plan approval**: The system implements an interactive human feedback mechanism through the LangGraph interrupt API in the human_feedback node. After generating the initial report plan, the workflow pauses execution and presents the user with the planned sections, awaiting explicit approval or revision feedback, creating a collaborative process where humans guide the system's direction.
- **Built on LangGraph for workflow visualization and management**: The architecture is structured as a directed graph using LangGraph's StateGraph, with an outer graph for overall report flow and a nested subgraph for section research. LangGraph's parallelization capabilities are leveraged to process multiple sections concurrently, and the entire workflow is visualized through LangGraph's Mermaid diagram export.

## Common Commands

- To be added as needed

## Code Style Preferences

- **PEP 8 compliant Python code**: Follow standard Python style guidelines
- **Comprehensive type hints**: Use typing module for all function parameters and return values
- **Google style docstrings**: Include detailed documentation for all classes, methods, and functions
- **Modular architecture**: Maintain clear separation of concerns with well-defined interfaces
- **Adapter pattern**: Use adapters for all external repository integrations
- **Unit tests**: Aim for 80%+ test coverage for all components

## Integration Plans

The `/plan/structural` directory contains detailed architectural plans for integrating the repositories in this workspace for AI research and knowledge discovery:

### Plan 1: AI Research Orchestration Framework
- High-level framework that combines capabilities from all repositories
- Focuses on orchestrating the full research process from planning to report generation
- Key components: Research Planning Coordinator, Information Gathering System, Knowledge Extraction Pipeline, Graph-based Knowledge Integration, and Research Generation System
- Leverages TDAG for planning, open_deep_research for information gathering, GDesigner for agent communication, KARMA for knowledge extraction, and AutoCodeAgent2.0 for code generation

### Plan 2: Dynamic Knowledge Graph System for AI Research
- System focused on building and maintaining comprehensive knowledge graphs of AI research
- Emphasizes patterns, trends, and knowledge gap discovery
- Key components: Multi-source Knowledge Extractor, Evolving Knowledge Graph, Graph-based Agent Network, Insight Generation System, and Research Guidance Interface
- Combines KARMA's knowledge extraction with GDesigner's graph-based coordination and open_deep_research's information gathering

### Plan 3: AI Research Implementation System
- System for automatically implementing and testing AI techniques from research papers
- Bridges the gap between theoretical AI research and practical implementation
- Key components: Research Understanding Engine, Implementation Planning System, Code Generation Pipeline, Experiment Management Framework, and Research Verification System
- Utilizes AutoCodeAgent2.0's code generation with TDAG's task decomposition and knowledge from research papers

Each plan includes detailed breakdowns at high, mid, and low levels of abstraction to guide implementation.