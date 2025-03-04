# CLAUDE.md - Repository Reference

This file contains key information about the repositories in this workspace and their functionalities.

> **Development Statistics:**  
> Total cost: $11.08  
> Total duration (API): 58m 57.5s  
> Total duration (wall): 1h 57m 43.4s  

## Project Implementation Status

### Current Implementation Progress

We have implemented the following components for the AI Research Integration Project:

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

### Next Implementation Steps

1. **Knowledge Extraction Pipeline**
   - Document processing engine
   - Entity recognition system
   - Relationship extraction module
   - Performance result aggregator
   - Concept definition builder

2. **Graph-based Knowledge Integration**
   - Knowledge graph construction
   - Contradiction resolution system
   - Connection discovery engine
   - Temporal evolution tracker
   - Knowledge gap identification

3. **Research Generation System**
   - Report structure planning
   - Content synthesis engine
   - Citation management system
   - Visualization generation tools
   - Code example generation

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