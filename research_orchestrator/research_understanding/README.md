# Research Understanding Engine

The Research Understanding Engine is a comprehensive framework for analyzing research papers, extracting structured information, and preparing for implementation. It provides tools for processing papers, extracting algorithms, and generating code implementations.

## Features

- **Paper Processing**: Convert research papers in various formats (PDF, HTML, ArXiv) into structured representations
- **Algorithm Extraction**: Identify algorithms and their implementation details from papers
- **Implementation Generation**: Generate code implementations from algorithm descriptions

## Architecture

The Research Understanding Engine is organized into several components:

### Paper Processing Module

The Paper Processing module processes research papers and extracts structured information. It includes:

- `PaperProcessor`: Main class for processing papers and extracting structured information
- `PDFPaperProcessor`, `HTMLPaperProcessor`, `ArXivPaperProcessor`: Format-specific processors
- Data models: `PaperSection`, `PaperReference`, `PaperFigure`, `PaperTable`, `PaperAlgorithm`

### Algorithm Extraction Module

The Algorithm Extraction module identifies and extracts algorithms and their implementation details. It includes:

- `AlgorithmExtractor`: Main class for extracting algorithms from papers
- `PseudocodeParser`: Parser for extracting structured information from pseudocode
- `AlgorithmImplementationGenerator`: Generator for creating code implementations
- Data models: `ExtractedAlgorithm`, `AlgorithmParameter`, `AlgorithmVariable`, `AlgorithmSubroutine`

### Understanding Engine

The `ResearchUnderstandingEngine` class provides high-level functionality that coordinates the paper processing, algorithm extraction, and implementation generation stages.

## Usage

### Basic Usage

```python
from research_orchestrator.research_understanding import ResearchUnderstandingEngine
from research_orchestrator.research_understanding.paper_processing import PaperFormat

# Initialize the engine
engine = ResearchUnderstandingEngine(cache_dir='/path/to/cache')

# Process a paper
result = engine.process_paper(
    paper_path='/path/to/paper.pdf',
    paper_format=PaperFormat.PDF,
    extract_algorithms=True
)

# Access the processed data
paper = result['paper']
algorithms = result['algorithms']

# Generate implementations
implementations = engine.generate_implementations(
    algorithms=algorithms,
    language='python',
    include_comments=True
)

# Extract detailed implementation information
enriched_algo = engine.extract_implementation_details(
    paper=paper,
    algorithm_id=algorithms[0].algorithm_id
)
```

### Advanced Usage

For more advanced use cases, you can directly use the individual components:

```python
from research_orchestrator.research_understanding.paper_processing import PaperProcessor
from research_orchestrator.research_understanding.algorithm_extraction import AlgorithmExtractor

# Initialize components
paper_processor = PaperProcessor(cache_dir='/path/to/cache/papers')
algorithm_extractor = AlgorithmExtractor(cache_dir='/path/to/cache/algorithms')

# Process a paper
paper = paper_processor.process_paper(paper_path='/path/to/paper.pdf')

# Extract algorithms
algorithms = algorithm_extractor.extract_algorithms(paper=paper)
```

## Example Scripts

The `examples/research_understanding` directory contains example scripts that demonstrate the usage of the Research Understanding Engine:

- `paper_processing_example.py`: Demonstrates paper processing and algorithm extraction
- `engine_example.py`: Demonstrates the high-level Research Understanding Engine