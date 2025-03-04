# AI Research Integration Project

This project integrates capabilities from multiple advanced AI systems to create a comprehensive framework for AI research, knowledge discovery, and implementation.

## Project Components

The project consists of three main systems:

1. **Research Orchestration Framework**: An end-to-end research assistant that coordinates the entire research process from query to report generation.

2. **Dynamic Knowledge Graph System**: A system for building and maintaining knowledge graphs of AI research to identify patterns, trends, and knowledge gaps.

3. **AI Research Implementation System**: A system that bridges the gap between theoretical AI research and practical implementation by automatically implementing, testing, and validating AI concepts from papers.

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Neo4j (for Knowledge Graph System)
- Access to external repositories (in `./external_repo/`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-research-integration.git
cd ai-research-integration

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

## Architecture

Each system follows a modular architecture with clear separation of concerns:

### Research Orchestration Framework
- **Core**: System initialization and coordination
- **Research Planning**: Query analysis and plan generation
- **Information Gathering**: Multi-source information collection
- **Knowledge Extraction**: Entity and relationship extraction
- **Knowledge Integration**: Organizing knowledge in graphs
- **Research Generation**: Creating reports and implementations

### Dynamic Knowledge Graph System
- **Core**: System initialization and coordination
- **Knowledge Extractor**: Multi-source knowledge extraction
- **Knowledge Graph**: Dynamic graph management
- **Agent Network**: Graph-based agent coordination
- **Insight Generation**: Pattern and gap discovery
- **Research Guidance**: Query handling and recommendations

### AI Research Implementation System
- **Core**: System initialization and coordination
- **Research Understanding**: Paper analysis and extraction
- **Implementation Planning**: Structured implementation planning
- **Code Generation**: Multi-framework code generation
- **Experiment Management**: Testing and validation
- **Research Verification**: Result comparison and analysis

## Development

This project follows a phased development approach:

1. **Phase 1**: Core framework and foundational modules
2. **Phase 2**: Knowledge extraction and integration
3. **Phase 3**: Advanced features and inter-system connections
4. **Phase 4**: Testing, optimization, and user interfaces

See `DEVELOPER_PLAN.md` in each system directory for detailed development roadmaps.

## Documentation

- **CLAUDE.md**: Detailed repository information and integration plans
- **plan/**: Architectural plans and file structures
- **CODING_PROMPT.md**: Guide for implementing the project
- **README.md** files in each directory with component-specific documentation

## Integration Points

The project integrates these existing repositories:

1. **TDAG**: Task decomposition and planning
2. **GDesigner**: Graph-based agent communication
3. **KARMA**: Knowledge extraction and graph construction
4. **open_deep_research**: Information gathering and research
5. **AutoCodeAgent2.0**: Code generation and implementation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project builds on the work of multiple open-source AI research projects.
See `CLAUDE.md` for detailed information about each integrated repository.