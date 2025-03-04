# Entity Recognition System

The Entity Recognition System is a core component of the Knowledge Extraction Pipeline, responsible for identifying and extracting named entities from research documents.

## Overview

This system identifies various types of entities in research documents, including:

### Core Entity Types
- **Models**: Neural network architectures, language models, etc.
- **Algorithms**: Specific algorithms and methods
- **Datasets**: Benchmark and training datasets
- **Metrics**: Evaluation metrics and measurements
- **Papers**: Research publications and articles
- **Authors**: Researchers and paper authors
- **Institutions**: Research institutions, universities, labs
- **Code**: Implementation repositories or source code
- **Concepts**: AI concepts, methods, techniques

### Additional Entity Types
- **AI-specific entities**: Architecture, parameters, frameworks, techniques, tasks
- **Scientific entities**: Theories, methodologies, findings, hypotheses, experiments
- **Metadata entities**: Fields, domains, problems, solutions, tools

The system uses a combination of pattern matching, dictionary-based recognition, and contextual analysis to identify entities with confidence scoring.

## Components

### Core Components

1. **Entity Data Model (`entity.py`)**
   - `Entity` class representing extracted entities
   - `EntityType` enum defining supported entity types
   - Serialization and utility methods

2. **Base Entity Recognizer (`base_recognizer.py`)**
   - Abstract base class for all recognizers
   - Common functionality for entity handling
   - Filtering, merging, and confidence calculation

3. **AI Entity Recognizer (`ai_recognizer.py`)**
   - Specialized for AI research entities
   - Recognizes models, datasets, metrics, etc.
   - AI-specific pattern matching and context analysis

4. **Scientific Entity Recognizer (`scientific_recognizer.py`)**
   - Specialized for scientific research concepts
   - Identifies theories, methodologies, findings, etc.
   - Scientific citation and reference handling

5. **Combined Entity Recognizer (`combined_recognizer.py`)**
   - Integrates multiple specialized recognizers
   - Resolves conflicts between recognizers
   - Merges overlapping entities

6. **Entity Recognizer Factory (`factory.py`)**
   - Creates and configures different recognizer types
   - Supports creation from configuration files
   - Default recognizer setups

### Key Features

- **Entity Type System**: Comprehensive typing for AI and scientific entities
- **Confidence Scoring**: Heuristic-based confidence for each entity
- **Conflict Resolution**: Intelligent handling of overlapping entities
- **Configurable Patterns**: Customizable recognition patterns
- **Dictionary Support**: Integration with terminology dictionaries
- **Context-Aware Recognition**: Uses document context to improve recognition

## Usage Examples

### Basic Usage

```python
from research_orchestrator.knowledge_extraction.entity_recognition import (
    EntityRecognizerFactory
)

# Create a default combined recognizer
recognizer = EntityRecognizerFactory.create_default_recognizer()

# Analyze text
text = "BERT achieved 84.6% accuracy on the GLUE benchmark."
entities = recognizer.recognize(text)

# Process results
for entity in entities:
    print(f"{entity.text} ({entity.type}): {entity.confidence:.2f}")
```

### Using Specific Recognizers

```python
# Create an AI-specific recognizer
ai_recognizer = EntityRecognizerFactory.create_recognizer("ai")

# Create a scientific recognizer
scientific_recognizer = EntityRecognizerFactory.create_recognizer("scientific")

# Use the recognizers
ai_entities = ai_recognizer.recognize(text)
scientific_entities = scientific_recognizer.recognize(text)
```

### Custom Configuration

```python
# Create a recognizer with custom configuration
config = {
    "patterns": {
        "model": [r"\b(Custom-[A-Z]+)\b"]
    },
    "dictionary_path": "path/to/custom_dictionary.json"
}

custom_recognizer = EntityRecognizerFactory.create_recognizer("ai", config)
```

## Integration with Other Components

This Entity Recognition System interfaces with:

1. **Document Processing**: Works on processed document content
2. **Relationship Extraction**: Entities are used to extract relationships
3. **Knowledge Graph**: Entities become nodes in the knowledge graph
4. **Research Planning**: Entities inform research planning decisions

## Extension Points

The system is designed to be extensible:

1. **New Entity Types**: Add new entity types to the EntityType enum
2. **Custom Recognizers**: Create new specialized recognizers by subclassing EntityRecognizer
3. **Custom Patterns**: Add domain-specific patterns through configuration
4. **Entity Dictionaries**: Integrate with domain-specific terminology

## Running the Example

To run the included example:

```
cd src
python -m research_orchestrator.knowledge_extraction.entity_recognition.test_example
```