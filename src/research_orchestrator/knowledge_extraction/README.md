# Knowledge Extraction Pipeline

The Knowledge Extraction Pipeline is a comprehensive system for extracting structured knowledge from research documents. It integrates document processing, entity recognition, and relationship extraction into a cohesive workflow that produces a knowledge graph from unstructured text.

> **Note on Paper Processing Status:** While all components of the knowledge extraction pipeline are fully implemented, the automated paper processing workflow is planned for future implementation. Currently, papers can be uploaded but will remain in the "uploaded" status until the processing pipeline is implemented in a future release.

## Overview

The Knowledge Extraction Pipeline consists of three main components:

1. **Document Processing Engine**: Processes various document formats (PDF, HTML, text) to extract raw text content.
2. **Entity Recognition System**: Identifies named entities such as models, datasets, metrics, concepts, etc.
3. **Relationship Extraction Module**: Identifies relationships between entities (e.g., "trained on", "outperforms", etc.).
4. **Knowledge Extraction Coordinator**: Coordinates the extraction process and builds a knowledge graph.

## Components

### Document Processing Engine

- `DocumentProcessor`: Coordinates processing of different document types
- `Document`: Representation of a processed document
- `PDFProcessor`: Processes PDF documents
- `HTMLProcessor`: Processes HTML documents
- `TextProcessor`: Processes plain text documents

The Document Processing Engine handles various document formats, extracting raw text content and metadata. It also segments documents into logical chunks (pages, paragraphs, sections) for easier processing.

### Entity Recognition System

- `EntityRecognizer`: Abstract base class for entity recognizers
- `Entity` and `EntityType`: Data model for entities
- `AIEntityRecognizer`: Recognizes AI-specific entities (models, datasets, metrics)
- `ScientificEntityRecognizer`: Recognizes scientific entities (concepts, theories, methodologies)
- `CombinedEntityRecognizer`: Integrates multiple recognizers
- `EntityRecognizerFactory`: Creates and configures recognizers

The Entity Recognition System identifies named entities in text, categorizes them, and assigns confidence scores. It supports 20+ entity types across AI and scientific domains.

### Relationship Extraction Module

- `RelationshipExtractor`: Abstract base class for relationship extractors
- `Relationship` and `RelationType`: Data model for relationships
- `PatternRelationshipExtractor`: Extracts relationships using patterns
- `AIRelationshipExtractor`: Specialized extractor for AI relationships
- `CombinedRelationshipExtractor`: Integrates multiple extractors
- `RelationshipExtractorFactory`: Creates and configures extractors

The Relationship Extraction Module identifies relationships between entities, using pattern matching, entity proximity, and contextual analysis. It supports 30+ relationship types.

### Knowledge Extraction Coordinator

- `KnowledgeExtractor`: Main coordinator for the extraction pipeline
- Knowledge graph creation and querying
- Extraction results management and serialization
- Statistical analysis and reporting

The Knowledge Extraction Coordinator orchestrates the entire extraction process, from document processing to knowledge graph creation. It provides a unified interface for the extraction pipeline and handles result management.

## Usage Examples

### Basic Usage

```python
from research_orchestrator.knowledge_extraction import KnowledgeExtractor

# Create a knowledge extractor
extractor = KnowledgeExtractor()

# Extract knowledge from a document
results = extractor.extract_from_document('path/to/document.pdf')

# Extract knowledge from text
text_results = extractor.extract_from_text('Some research text about models...')

# Process all documents in a directory
directory_results = extractor.extract_from_directory('path/to/docs')

# Get extraction statistics
stats = extractor.get_extraction_statistics()
```

### Using Custom Extractors

```python
from research_orchestrator.knowledge_extraction import KnowledgeExtractor
from research_orchestrator.knowledge_extraction.entity_recognition import EntityRecognizerFactory
from research_orchestrator.knowledge_extraction.relationship_extraction import RelationshipExtractorFactory

# Create custom extractors
entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
relationship_extractor = RelationshipExtractorFactory.create_default_extractor()

# Create knowledge extractor with custom extractors
extractor = KnowledgeExtractor(
    entity_recognizer=entity_recognizer,
    relationship_extractor=relationship_extractor
)

# Process documents with custom extractors
results = extractor.extract_from_document('path/to/document.pdf')
```

### Querying the Knowledge Graph

```python
# Query for specific entities
entity_query = {
    "type": "entity",
    "entity_type": "model",
    "keywords": ["GPT-4"]
}
entities = extractor.query_knowledge_graph(entity_query)

# Query for relationships
relationship_query = {
    "type": "relationship",
    "relation_type": "outperforms",
    "source_type": "model",
    "target_type": "model"
}
relationships = extractor.query_knowledge_graph(relationship_query)

# Find paths between entities
path_query = {
    "type": "path",
    "start_entity": "GPT-4",
    "end_entity": "BERT",
    "max_length": 3
}
paths = extractor.query_knowledge_graph(path_query)
```

## Saving and Loading Results

```python
# Save extraction results
output_dir = extractor.save_extraction_results('/path/to/output')

# Load extraction results
extractor.load_extraction_results('/path/to/saved/results')
```

## Key Features

- **Comprehensive extraction pipeline**: Document processing, entity recognition, relationship extraction
- **Multi-format support**: Process PDF, HTML, and text documents
- **Rich entity and relationship types**: 20+ entity types and 30+ relationship types
- **Knowledge graph creation**: Convert extracted information into a graph structure
- **Querying capabilities**: Search for entities, relationships, and paths
- **Statistical analysis**: Get insights into extraction results
- **Result management**: Save and load extraction results

## Integration with Other Components

The Knowledge Extraction Pipeline integrates with other components of the Research Orchestration Framework:

- **Information Gathering**: Processes documents retrieved from various sources
- **Research Planning**: Provides knowledge for research planning decisions
- **Knowledge Graph System**: Feeds extracted knowledge into the larger knowledge graph
- **Research Generation**: Supplies information for report generation

## Planned Enhancements

The following enhancements are planned for the Knowledge Extraction Pipeline:

1. **Paper Processing Pipeline**
   - Asynchronous task processing system using Celery and Redis
   - Paper lifecycle state management with detailed status tracking
   - Real-time status updates via WebSockets
   - Manual processing endpoints with batch capability
   - Integration with existing DocumentProcessor components
   - Enhanced metadata extraction and knowledge graph integration
   - Citation network analysis and concept-based paper interconnection

2. **Additional Document Format Support**
   - LaTeX document processing
   - Word document processing
   - Markdown document processing
   - Jupyter notebook processing

## Running the Example

To run the included example:

```
cd src
python -m research_orchestrator.knowledge_extraction.test_knowledge_extractor
```