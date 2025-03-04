# Relationship Extraction System

The Relationship Extraction System is a core component of the Knowledge Extraction Pipeline, responsible for identifying relationships between entities in research documents.

## Overview

This system identifies various types of relationships between entities, including:

- AI model relationships (trained-on, outperforms, based-on, etc.)
- Scientific concept relationships (part-of, is-a, studies, etc.)
- Citation and reference relationships
- Hierarchical and compositional relationships

The system uses pattern matching, entity type analysis, and contextual clues to extract relationships with confidence scoring.

## Components

### Core Components

1. **Relationship Data Model (`relationship.py`)**
   - `Relationship` class representing entity relationships
   - `RelationType` enum defining supported relationship types
   - Serialization and utility methods

2. **Base Relationship Extractor (`base_extractor.py`)**
   - Abstract base class for all extractors
   - Common functionality for relationship handling
   - Entity pair finding and context analysis

3. **Pattern-based Extractor (`pattern_extractor.py`)**
   - Pattern-based relationship extraction
   - Regular expression pattern matching
   - Contextual confidence scoring

4. **AI-specific Extractor (`ai_extractor.py`)**
   - Specialized for AI research relationships
   - Model performance extraction
   - AI model hierarchy and lineage detection

5. **Combined Extractor (`combined_extractor.py`)**
   - Integrates multiple specialized extractors
   - Resolves conflicts between extractors
   - Provides comprehensive relationship coverage

6. **Extractor Factory (`factory.py`)**
   - Creates and configures different extractors
   - Provides default configurations
   - Supports configuration-based creation

### Key Features

- **Comprehensive Relationship Types**: 30+ relationship types for AI and scientific domains
- **Pattern-Based Extraction**: Regular expression patterns for relationship detection
- **Entity Type Association**: Intelligent pairing of entity types with relationship types
- **Context Analysis**: Extraction of surrounding context for relationship verification
- **Confidence Scoring**: Heuristic-based confidence calculation for relationships
- **Conflict Resolution**: Intelligent handling of conflicting relationship types
- **Network Analysis**: Tools for analyzing the entity-relationship network

## Usage Examples

### Basic Usage

```python
from research_orchestrator.knowledge_extraction.entity_recognition import EntityRecognizerFactory
from research_orchestrator.knowledge_extraction.relationship_extraction import RelationshipExtractorFactory

# Extract entities first
entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
entities = entity_recognizer.recognize(text)

# Create a relationship extractor
relationship_extractor = RelationshipExtractorFactory.create_default_extractor()

# Extract relationships
relationships = relationship_extractor.extract_relationships(text, entities)

# Process results
for relationship in relationships:
    print(f"{relationship.source.text} {relationship.relation_type} {relationship.target.text} ({relationship.confidence:.2f})")
```

### Using Specific Extractors

```python
# Create a pattern-based extractor
pattern_extractor = RelationshipExtractorFactory.create_pattern_extractor()

# Create an AI-specific extractor
ai_extractor = RelationshipExtractorFactory.create_ai_extractor()

# Use the extractors
pattern_relationships = pattern_extractor.extract_relationships(text, entities)
ai_relationships = ai_extractor.extract_relationships(text, entities)
```

### Custom Configuration

```python
# Create an extractor with custom configuration
config = {
    "patterns": {
        "trained_on": [r"trained (?:on|with) \{target\}"]
    },
    "max_entity_distance": 200,
    "context_window_size": 120
}

custom_extractor = RelationshipExtractorFactory.create_pattern_extractor(**config)
```

### Advanced Analysis

```python
# Extract relationships
relationships = extractor.extract_relationships(text, entities)

# Get statistics
stats = extractor.get_relationship_statistics()

# Find relationships for specific entity
entity_relationships = extractor.find_relationships_involving_entity(entity)

# Find relationship chains
chains = extractor.find_relationship_chain(start_entity, max_depth=3)
```

## Integration with Other Components

This Relationship Extraction System interfaces with:

1. **Entity Recognition**: Receives entities from entity recognition system
2. **Document Processing**: Processes text from document processing system
3. **Knowledge Graph**: Provides relationships that become edges in the knowledge graph
4. **Research Planning**: Relationships inform research planning decisions

## Extension Points

The system is designed to be extensible:

1. **New Relationship Types**: Add new types to the RelationType enum
2. **Custom Extractors**: Create new specialized extractors by subclassing RelationshipExtractor
3. **Custom Patterns**: Add domain-specific patterns through configuration
4. **Confidence Calculation**: Customize confidence scoring for specific needs

## Running the Example

To run the included example:

```
cd src
python -m research_orchestrator.knowledge_extraction.relationship_extraction.test_example
```