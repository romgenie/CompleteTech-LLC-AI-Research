# Test Data Directory

This directory contains test data for the knowledge extraction tests.

## Directory Structure

- `documents/` - Test documents for document processing
  - `text/` - Text documents (plain text, markdown, etc.)
  - `html/` - HTML documents
  - `pdf/` - PDF documents
- `entities/` - Entity data for testing
- `relationships/` - Relationship data for testing
- `graphs/` - Knowledge graph data for testing

## Sample Documents

### Text Documents

- `sample_ai_paper.txt` - A sample research paper about AI language models
  - Contains entities: GPT-4, PaLM, Claude, MMLU, HumanEval, GSM8K
  - Contains organizations: OpenAI, Google, Anthropic
  - Contains relationships: developed_by, outperforms, evaluated_on

### HTML Documents

- `sample_ai_blog.html` - A sample blog post about vision models
  - Contains entities: ViT, CLIP, DALL-E 2, Stable Diffusion, Midjourney
  - Contains organizations: Google Research, OpenAI, Stability AI
  - Contains frameworks: PyTorch, TensorFlow
  - Contains relationships: developed_by, based_on, trained_on

## Usage

These test files are used by the integration and end-to-end tests to verify the knowledge extraction pipeline. The files contain known entities and relationships that should be detected by the extraction components.

To add new test data:

1. Add the document to the appropriate subdirectory in `documents/`
2. If needed, add corresponding entity or relationship data to `entities/` or `relationships/`
3. Update this README.md to list the new test data and its contents