# Knowledge Graph System Core

This module provides the core functionality for the Knowledge Graph System, which builds and maintains comprehensive knowledge graphs of AI research.

## Overview

The Knowledge Graph System Core includes three main components:

1. **Database Management**: Connects to and manages the Neo4j graph database
2. **Data Models**: Defines the structure of entities and relationships in the knowledge graph
3. **Knowledge Graph Management**: Provides high-level operations for adding, querying, and managing the knowledge graph

## Key Components

### Database Management

- **Neo4jManager**: Manages connections to Neo4j, handles queries, and provides utility methods for database operations

### Data Models

- **GraphEntity**: Base class for all graph nodes, with common attributes like ID, label, properties, etc.
- **GraphRelationship**: Base class for all graph relationships, with common attributes like ID, type, source/target IDs, etc.
- **AI-specific Models**: Specialized entity and relationship classes for AI research, including:
  - AIModel: Represents AI models like GPT-4, BERT, etc.
  - Dataset: Represents datasets like ImageNet, MNIST, etc.
  - Algorithm: Represents algorithms like transformers, reinforcement learning, etc.
  - Paper: Represents research papers
  - And various relationship types like TRAINED_ON, OUTPERFORMS, etc.

### Knowledge Graph Management

- **KnowledgeGraphManager**: High-level manager for knowledge graph operations, including:
  - Adding/updating entities and relationships
  - Querying and searching the graph
  - Finding paths and relationships between entities
  - Detecting contradictions and inconsistencies
  - Computing graph statistics

### Utilities

- **SchemaDefinition**: Defines and validates the knowledge graph schema
- **Schema Utils**: Utilities for schema management and validation

## Usage Examples

### Connecting to Neo4j

```python
from knowledge_graph_system.core.db.neo4j_manager import Neo4jManager

# Connect using direct parameters
neo4j_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password",
    database="ai_research"
)

# Or connect using config file
neo4j_manager = Neo4jManager.from_config("config/db_config.json")

# Or connect using environment variables
neo4j_manager = Neo4jManager.from_env()
```

### Creating and Adding Entities

```python
from knowledge_graph_system.core.models.ai_models import AIModel
from knowledge_graph_system.core.knowledge_graph_manager import KnowledgeGraphManager

# Create knowledge graph manager
kg_manager = KnowledgeGraphManager(neo4j_manager)

# Create an AI model entity
gpt4 = AIModel(
    name="GPT-4",
    organization="OpenAI",
    release_date="2023-03-14",
    model_type="language model",
    parameters=1500000000000,  # 1.5 trillion
    architecture="Transformer",
    capabilities=["text generation", "reasoning", "translation"],
    limitations=["hallucinations", "knowledge cutoff"],
    confidence=0.95,
    source="openai.com"
)

# Add the entity to the graph
result = kg_manager.add_entity(gpt4)
```

### Creating and Adding Relationships

```python
from knowledge_graph_system.core.models.ai_models import Dataset, TrainedOn

# Create a dataset entity
common_crawl = Dataset(
    name="Common Crawl",
    description="Web archive of billions of pages",
    domain="general",
    size="multi-petabyte",
    confidence=0.9,
    source="commoncrawl.org"
)

# Add the dataset to the graph
kg_manager.add_entity(common_crawl)

# Create a relationship
trained_on = TrainedOn(
    source_id=gpt4.id,
    target_id=common_crawl.id,
    confidence=0.85,
    source="inferred"
)

# Add the relationship to the graph
kg_manager.add_relationship(trained_on)
```

### Querying the Graph

```python
# Get an entity by ID
entity = kg_manager.get_entity_by_id("entity-id")

# Find entities by label
models = kg_manager.get_entities_by_label("AIModel", limit=10)

# Search for entities
search_results = kg_manager.search_entities("transformer", limit=20)

# Find relationships between entities
paths = kg_manager.find_paths("entity-id-1", "entity-id-2", max_depth=3)

# Find related entities
related = kg_manager.find_related_entities("entity-id", 
                                         relationship_types=["TRAINED_ON", "USES_ALGORITHM"],
                                         entity_labels=["Dataset", "Algorithm"])
```

## Configuration

The core module supports configuration through:

1. **Config Files**: JSON files specifying database connection parameters, schema definitions, etc.
2. **Environment Variables**: E.g., NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, etc.
3. **Direct Parameters**: Passed to constructors when creating objects

## Integration

The Knowledge Graph System Core is designed to integrate with:

- **KARMA**: For knowledge extraction and triple generation
- **Research Orchestrator**: For connecting to research planning and information gathering
- **Web APIs**: For fetching additional information about entities
- **Visualization Tools**: For visualizing the knowledge graph