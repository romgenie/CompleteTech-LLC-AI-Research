# Core Module - Knowledge Graph System

This module contains the core components of the Dynamic Knowledge Graph System for AI Research. It handles system initialization, coordination, global settings, and common utilities.

## Components

- **system.py**: Main controller that initializes and coordinates system components
- **settings.py**: Global settings management and configuration handling
- **utils.py**: Common utility functions used throughout the system

## Responsibilities

The core module is responsible for:

1. System initialization and component registration
2. Configuration loading and management
3. Coordinating interaction between system components
4. Providing common utilities and helpers
5. Error handling and recovery mechanisms

## Usage

```python
from knowledge_graph_system.core.system import KnowledgeGraphSystem

# Initialize the system with configuration
system = KnowledgeGraphSystem(config_path="config/default_config.yaml")

# Start system components
system.start()

# Get references to major subsystems
extractor = system.get_component("knowledge_extractor")
graph = system.get_component("knowledge_graph")
agent_network = system.get_component("agent_network")

# Shutdown the system
system.shutdown()
```

## Configuration

The system uses YAML configuration files with the following structure:

```yaml
system:
  name: "Knowledge Graph System"
  version: "1.0.0"
  log_level: "INFO"

components:
  knowledge_extractor:
    enabled: true
    # Component-specific configuration...
  
  knowledge_graph:
    enabled: true
    database:
      type: "neo4j"
      uri: "bolt://localhost:7687"
      # Database-specific configuration...
  
  # Other component configurations...
```

## Development Guidelines

1. Keep the core module focused on system coordination
2. Use dependency injection for component coupling
3. Maintain clean separation of concerns
4. Implement proper error handling and logging
5. Write comprehensive tests for all functionality