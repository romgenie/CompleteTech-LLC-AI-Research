# AI Research Idea Generation and Evaluation

Implementation of the research paper "Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers" (Si et al., 2024).

## Project Overview

This project aims to evaluate the capability of Large Language Models (LLMs) in generating novel, expert-level research ideas in the field of NLP. The system includes:

1. An LLM ideation agent that generates and ranks research ideas
2. A style normalization module for standardizing AI and human-written ideas
3. A comprehensive evaluation framework with human expert reviews
4. Statistical analysis tools for comparing idea quality across conditions

## Key Findings

The paper's central finding is that AI-generated ideas are rated as significantly more novel than human expert ideas, while being comparable or slightly weaker on feasibility metrics. This system allows for:

- Generating diverse research ideas across multiple NLP topics
- Evaluating idea quality through expert review
- Analyzing various dimensions of idea quality (novelty, excitement, feasibility, effectiveness)

## Our Implementation

We've implemented a full-featured research idea generation system in the `ai_research_agent/` directory. Key components include:

1. **Paper Retriever**: Fetches relevant papers from Semantic Scholar API for context
2. **Idea Generator**: Creates novel research ideas based on retrieved papers
3. **Idea Ranker**: Uses pairwise comparisons to rank ideas by quality 
4. **Style Normalizer**: Standardizes writing style to eliminate AI vs. human cues
5. **Evaluation Framework**: Analyzes idea quality with statistical rigor

The implementation is fully modular and configurable via YAML configuration files.

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ai-research-agent.git
cd ai-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables for API keys
echo "OPENAI_API_KEY=your_openai_key" > .env
echo "ANTHROPIC_API_KEY=your_anthropic_key" >> .env
echo "SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key" >> .env
```

## Configuration

Edit `config.yaml` to configure:
- API settings for LLM access
- Research topics and their descriptions
- Paper retrieval parameters
- Idea generation and ranking settings
- Evaluation metrics and statistical tests

## Usage

### Using the New Implementation

```bash
# Run the full agent pipeline with default config
python ai_research_agent/scripts/run_agent.py --config config.yaml

# Run with custom output directory
python ai_research_agent/scripts/run_agent.py --config config.yaml --output-dir custom_outputs

# Run with specific topics
python ai_research_agent/scripts/run_agent.py --config config.yaml --topics topic1 topic2

# Evaluate results
python ai_research_agent/scripts/run_evaluation.py --ratings outputs/ratings.json
```

### Original Scripts (Legacy)

```bash
# Generate research ideas for all topics
python scripts/generate_ideas.py

# Generate for a specific topic
python scripts/generate_ideas.py --topic factuality

# Normalize style of generated ideas
python scripts/normalize_style.py

# Run evaluation on generated ideas
python scripts/run_evaluation.py

# Analyze evaluation results
python scripts/analyze_results.py
```

## Repository Structure

```
research/
├── ai_research_agent/       # Main implementation
│   ├── agent/               # Core agent components
│   ├── data/                # Data storage
│   ├── evaluation/          # Evaluation system
│   ├── experiments/         # Experiment tracking
│   ├── scripts/             # Utility scripts
│   ├── utils/               # Utility functions
│   └── README.md            # Detailed implementation README
├── config.yaml              # Configuration file
├── data/                    # Data directory
│   └── raw/                 # Raw data and templates
├── CLAUDE.md                # Project guidelines and commands
├── paper.txt                # Original research paper
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

## Citation

This project is an implementation of the methodology described in the paper:

> **"Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers"**  
> Chenglei Si, Diyi Yang, Tatsunori Hashimoto  
> Stanford University  
> arXiv:2409.04109 (2024)

If you use this code, please cite the original paper:

```
@article{si2024canllms,
  title={Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers},
  author={Si, Chenglei and Yang, Diyi and Hashimoto, Tatsunori},
  journal={arXiv preprint arXiv:2409.04109},
  year={2024}
}
```

The paper is available at: [https://arxiv.org/abs/2409.04109](https://arxiv.org/abs/2409.04109)

## License

MIT License

## Acknowledgements

This project is based on research by Stanford University. We thank all the participants who contributed to the original study.