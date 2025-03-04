# Contributing to AI Research Integration Project

Thank you for your interest in contributing to the AI Research Integration Project! This guide provides detailed instructions for contributing to the project and helps you understand our development workflow, coding standards, and review process.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Project Structure](#project-structure)
3. [Development Environment Setup](#development-environment-setup)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation Guidelines](#documentation-guidelines)
8. [Pull Request Process](#pull-request-process)
9. [Commit Message Guidelines](#commit-message-guidelines)
10. [License](#license)
11. [Contact](#contact)

## Code of Conduct

All contributors are expected to adhere to the project's code of conduct. We are committed to providing a welcoming and inclusive environment for all. Please be respectful and professional in all communications and interactions with the community. Any form of harassment, discrimination, or unprofessional behavior will not be tolerated.

## Project Structure

Understanding the project structure is essential for making effective contributions. The AI Research Integration Project follows a modular architecture with clear separation of concerns:

```
src/
├── research_orchestrator/       # Research Orchestration Framework
│   ├── core/                    # Core orchestration functionality
│   ├── external_adapters/       # Adapters for external repositories
│   ├── information_gathering/   # Information gathering components
│   ├── knowledge_extraction/    # Knowledge extraction components
│   ├── knowledge_integration/   # Knowledge integration components
│   └── research_generation/     # Research report generation
│
├── knowledge_graph_system/      # Knowledge Graph System
│   ├── core/                    # Core graph functionality
│   ├── models/                  # Entity and relationship models
│   ├── schema/                  # Graph schema definitions
│   └── utils/                   # Utility functions
│
├── research_implementation/     # Research Implementation System
│   ├── core/                    # Core implementation functionality
│   ├── paper_processing/        # Paper processing components
│   ├── code_generation/         # Code generation components
│   └── verification/            # Implementation verification
│
├── ui/                          # User Interface
│   ├── api/                     # FastAPI backend
│   │   ├── database/            # Database connection modules
│   │   ├── models/              # Pydantic models
│   │   ├── routers/             # API route handlers
│   │   ├── middleware/          # Middleware components
│   │   └── services/            # Business logic services
│   │
│   └── frontend/                # React frontend
│       ├── public/              # Static assets
│       └── src/                 # Frontend source code
│           ├── components/      # React components
│           ├── contexts/        # React contexts
│           ├── pages/           # Page components
│           ├── services/        # API client services
│           └── utils/           # Utility functions
│
└── utils/                       # Shared utility functions
```

When adding new functionality, please ensure it follows this structure and respects the separation of concerns.

## Development Environment Setup

### Prerequisites

- Python 3.9+ for backend development
- Node.js 14+ for frontend development
- Docker and Docker Compose for containerized services
- Git for version control

### Setup Steps

1. **Fork the repository**
   - Visit the [project repository](https://github.com/yourusername/ai-research-integration) and click "Fork"

2. **Clone your fork locally**
   ```bash
   git clone https://github.com/your-username/ai-research-integration.git
   cd ai-research-integration
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   # Install main requirements
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

5. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

6. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit the .env file with your configuration
   ```

7. **Set up the frontend**
   ```bash
   cd src/ui/frontend
   npm install
   ```

8. **Start the database services**
   ```bash
   docker-compose up -d neo4j mongodb
   ```

## Development Workflow

1. **Create a feature branch**
   - Always create a new branch for your work
   ```bash
   git checkout -b feature/descriptive-feature-name
   ```

2. **Make your changes**
   - Follow the [coding standards](#coding-standards)
   - Write [tests](#testing-guidelines)
   - Update [documentation](#documentation-guidelines)

3. **Run tests locally**
   ```bash
   # Run all Python tests
   pytest
   
   # Run with coverage
   pytest --cov=src
   
   # Run specific tests
   pytest tests/specific_test_file.py
   
   # Run frontend tests
   cd src/ui/frontend
   npm test
   ```

4. **Run linting and formatting**
   ```bash
   # Run all pre-commit checks
   pre-commit run --all-files
   
   # Run specific checks
   black src tests
   flake8 src tests
   isort src tests
   mypy src
   ```

5. **Commit your changes**
   - Follow the [commit message guidelines](#commit-message-guidelines)
   ```bash
   git add .
   git commit -m "feat(component): Add new feature"
   ```

6. **Pull and rebase changes from upstream**
   ```bash
   git remote add upstream https://github.com/original-repo/ai-research-integration.git
   git fetch upstream
   git rebase upstream/main
   ```

7. **Push changes to your fork**
   ```bash
   git push origin feature/descriptive-feature-name
   ```

8. **Submit a pull request**
   - See the [pull request process](#pull-request-process)

## Coding Standards

This project enforces high coding standards to ensure code quality, maintainability, and consistency. All contributions must adhere to these standards.

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) code style
- Use [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) docstrings
- Include comprehensive [type hints](https://www.python.org/dev/peps/pep-0484/) for all functions and methods
- Maximum line length: 88 characters (enforced by Black)
- Formatting is enforced using [Black](https://black.readthedocs.io/)
- Import sorting is enforced using [isort](https://pycqa.github.io/isort/)
- Static typing is checked using [mypy](http://mypy-lang.org/)
- Code quality is checked using [flake8](https://flake8.pycqa.org/)

### JavaScript/TypeScript

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use [ESLint](https://eslint.org/) for linting
- Use [Prettier](https://prettier.io/) for formatting
- Prefer functional components with hooks for React development
- Use PropTypes or TypeScript for type checking
- Maximum line length: 100 characters

### Example Python Code

```python
from typing import Dict, List, Optional, Union

import numpy as np

from research_orchestrator.core.base import BaseComponent
from utils.logging import get_logger


class DataProcessor(BaseComponent):
    """Process research data into structured format.
    
    This component handles the transformation of raw research data
    into a structured format suitable for analysis and storage.
    
    Attributes:
        name: A string identifier for the processor.
        logger: Logger instance for this component.
        config: Configuration dictionary for the processor.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, any]] = None) -> None:
        """Initialize the data processor.
        
        Args:
            name: Unique identifier for this processor instance.
            config: Optional configuration parameters. Defaults to None.
        """
        super().__init__(name)
        self.logger = get_logger(f"{self.__class__.__name__}.{name}")
        self.config = config or {}
    
    def process(self, data: List[Dict[str, Union[str, int, float]]]) -> Dict[str, any]:
        """Process the input data into a structured format.
        
        Args:
            data: List of dictionaries containing raw research data.
            
        Returns:
            Processed data in a structured format.
            
        Raises:
            ValueError: If input data is empty or malformed.
        """
        if not data:
            raise ValueError("Input data cannot be empty")
        
        self.logger.info(f"Processing {len(data)} data records")
        
        # Perform data processing
        result = {
            "count": len(data),
            "fields": list(data[0].keys()),
            "numeric_stats": self._calculate_numeric_stats(data),
            "processed_items": [self._process_item(item) for item in data]
        }
        
        self.logger.info("Data processing complete")
        
        return result
    
    def _calculate_numeric_stats(self, data: List[Dict[str, any]]) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for numeric fields in the data.
        
        Args:
            data: List of data dictionaries.
            
        Returns:
            Dictionary with statistics for each numeric field.
        """
        stats = {}
        numeric_fields = self._identify_numeric_fields(data)
        
        for field in numeric_fields:
            values = [item[field] for item in data if field in item]
            if values:
                stats[field] = {
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
        
        return stats
    
    def _identify_numeric_fields(self, data: List[Dict[str, any]]) -> List[str]:
        """Identify numeric fields in the data.
        
        Args:
            data: List of data dictionaries.
            
        Returns:
            List of field names that contain numeric data.
        """
        numeric_fields = []
        sample_item = data[0]
        
        for key, value in sample_item.items():
            if isinstance(value, (int, float)):
                numeric_fields.append(key)
        
        return numeric_fields
    
    def _process_item(self, item: Dict[str, any]) -> Dict[str, any]:
        """Process an individual data item.
        
        Args:
            item: Dictionary containing item data.
            
        Returns:
            Processed item dictionary.
        """
        # Implement item-specific processing here
        processed = item.copy()
        
        # Apply transformations based on configuration
        if "transformations" in self.config:
            for field, transform in self.config["transformations"].items():
                if field in processed and transform == "uppercase" and isinstance(processed[field], str):
                    processed[field] = processed[field].upper()
        
        return processed
```

### Example React Component

```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { CircularProgress, Typography, Box, Alert } from '@mui/material';

import { fetchResearchData } from '../services/researchService';
import DataVisualization from './DataVisualization';
import EmptyState from './EmptyState';

/**
 * Component to display research data with visualization.
 */
const ResearchDataDisplay = ({ researchId, onDataLoaded }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      if (!researchId) return;
      
      try {
        setLoading(true);
        setError(null);
        
        const researchData = await fetchResearchData(researchId);
        setData(researchData);
        
        if (onDataLoaded) {
          onDataLoaded(researchData);
        }
      } catch (err) {
        console.error('Failed to load research data:', err);
        setError('Could not load research data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [researchId, onDataLoaded]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="No research data available" />;
  }

  return (
    <div className="research-data-container">
      <Typography variant="h5" gutterBottom>
        Research Data
      </Typography>
      
      <Box mb={3}>
        <Typography variant="subtitle1">
          Title: {data.title}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Date: {new Date(data.timestamp).toLocaleDateString()}
        </Typography>
      </Box>
      
      {data.visualization_data && (
        <DataVisualization data={data.visualization_data} />
      )}
      
      <Box mt={3}>
        <Typography variant="body1">
          {data.summary}
        </Typography>
      </Box>
    </div>
  );
};

ResearchDataDisplay.propTypes = {
  researchId: PropTypes.string.isRequired,
  onDataLoaded: PropTypes.func,
};

ResearchDataDisplay.defaultProps = {
  onDataLoaded: null,
};

export default ResearchDataDisplay;
```

## Testing Guidelines

Comprehensive testing is essential for maintaining code quality and preventing regressions. All contributions should include appropriate tests.

### Test Requirements

- Maintain at least 80% test coverage for all components
- Write both unit and integration tests
- Mock external dependencies appropriately
- Test both normal and edge cases
- Test failure scenarios

### Test Framework

- **Backend**: Use pytest for Python code
- **Frontend**: Use Jest and React Testing Library for JavaScript/React code

### Example Python Test

```python
import pytest
from unittest.mock import MagicMock, patch

from research_orchestrator.core.data_processor import DataProcessor


class TestDataProcessor:
    """Tests for the DataProcessor class."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return [
            {"id": 1, "name": "Sample 1", "value": 10.5},
            {"id": 2, "name": "Sample 2", "value": 20.0},
            {"id": 3, "name": "Sample 3", "value": 15.2},
        ]
    
    @pytest.fixture
    def processor(self):
        """Create a data processor instance for testing."""
        return DataProcessor("test-processor")
    
    def test_process_with_valid_data(self, processor, sample_data):
        """Test processing with valid input data."""
        result = processor.process(sample_data)
        
        assert result["count"] == 3
        assert set(result["fields"]) == {"id", "name", "value"}
        assert "numeric_stats" in result
        assert "value" in result["numeric_stats"]
        assert result["numeric_stats"]["value"]["mean"] == pytest.approx(15.23, 0.1)
        assert len(result["processed_items"]) == 3
    
    def test_process_with_empty_data(self, processor):
        """Test processing with empty data raises ValueError."""
        with pytest.raises(ValueError, match="Input data cannot be empty"):
            processor.process([])
    
    def test_process_with_transformations(self, processor, sample_data):
        """Test processing with field transformations."""
        processor.config = {
            "transformations": {
                "name": "uppercase"
            }
        }
        
        result = processor.process(sample_data)
        processed_items = result["processed_items"]
        
        assert processed_items[0]["name"] == "SAMPLE 1"
        assert processed_items[1]["name"] == "SAMPLE 2"
        assert processed_items[2]["name"] == "SAMPLE 3"
    
    @patch("research_orchestrator.core.data_processor.np")
    def test_calculate_numeric_stats(self, mock_np, processor, sample_data):
        """Test calculation of numeric statistics."""
        mock_np.mean.return_value = 15.23
        mock_np.median.return_value = 15.2
        mock_np.std.return_value = 4.75
        mock_np.min.return_value = 10.5
        mock_np.max.return_value = 20.0
        
        result = processor._calculate_numeric_stats(sample_data)
        
        assert "value" in result
        assert result["value"]["mean"] == 15.23
        assert result["value"]["median"] == 15.2
        assert result["value"]["std"] == 4.75
        assert result["value"]["min"] == 10.5
        assert result["value"]["max"] == 20.0
```

### Example React Component Test

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResearchDataDisplay from './ResearchDataDisplay';
import { fetchResearchData } from '../services/researchService';

// Mock the service
jest.mock('../services/researchService');

describe('ResearchDataDisplay', () => {
  const mockData = {
    title: 'Research on Vision Transformers',
    timestamp: '2023-04-15T10:30:00Z',
    summary: 'A comprehensive analysis of Vision Transformers in computer vision.',
    visualization_data: { type: 'bar', data: [10, 20, 30] }
  };
  
  const mockDataLoadedFn = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('displays loading state initially', () => {
    fetchResearchData.mockResolvedValue(mockData);
    
    render(<ResearchDataDisplay researchId="123" onDataLoaded={mockDataLoadedFn} />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
  
  test('displays data when loaded successfully', async () => {
    fetchResearchData.mockResolvedValue(mockData);
    
    render(<ResearchDataDisplay researchId="123" onDataLoaded={mockDataLoadedFn} />);
    
    await waitFor(() => {
      expect(screen.getByText('Research on Vision Transformers')).toBeInTheDocument();
    });
    
    expect(screen.getByText('A comprehensive analysis of Vision Transformers in computer vision.')).toBeInTheDocument();
    expect(screen.getByText(/Date:/)).toBeInTheDocument();
    expect(mockDataLoadedFn).toHaveBeenCalledWith(mockData);
  });
  
  test('displays error message when data loading fails', async () => {
    fetchResearchData.mockRejectedValue(new Error('Failed to fetch'));
    
    render(<ResearchDataDisplay researchId="123" onDataLoaded={mockDataLoadedFn} />);
    
    await waitFor(() => {
      expect(screen.getByText(/Could not load research data/)).toBeInTheDocument();
    });
    
    expect(mockDataLoadedFn).not.toHaveBeenCalled();
  });
  
  test('displays empty state when no data is available', async () => {
    fetchResearchData.mockResolvedValue({});
    
    render(<ResearchDataDisplay researchId="123" onDataLoaded={mockDataLoadedFn} />);
    
    await waitFor(() => {
      expect(screen.getByText('No research data available')).toBeInTheDocument();
    });
  });
});
```

## Documentation Guidelines

Good documentation is crucial for project maintainability and usability. All code should be well-documented.

### Code Documentation

- Add docstrings to all modules, classes, and functions
- Use Google-style docstrings for Python code
- Include type information in docstrings
- Document parameters, return values, and exceptions
- Add inline comments for complex logic

### Component Documentation

Each major component should have a dedicated README.md file that explains:

- Purpose and functionality
- Key classes and interfaces
- Usage examples
- Configuration options
- Integration with other components

### API Documentation

- Document all API endpoints using appropriate decorators (FastAPI for backend)
- Include request and response schemas
- Document error responses and status codes
- Provide example requests and responses

## Pull Request Process

1. **Create your pull request**
   - Navigate to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with relevant information

2. **PR Template**
   - Title: Brief, descriptive title of the changes
   - Description: Detailed description of what changes were made and why
   - Related Issues: Link to any related issues
   - Type of Change: (Bug fix, new feature, breaking change, etc.)
   - Checklist: Tests, documentation, style compliance, etc.

3. **Code review**
   - Wait for reviews from maintainers
   - Address any feedback or questions
   - Make necessary changes based on comments
   - Push updates to your branch

4. **Merge requirements**
   - CI checks pass (tests, linting, type checking)
   - At least one approval from a maintainer
   - All discussions resolved
   - No merge conflicts with the target branch

5. **After merge**
   - Delete your branch
   - Verify deployment if applicable
   - Close related issues

## Commit Message Guidelines

Clear, structured commit messages help maintain a readable project history. We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
type(scope): Subject

[optional body]

[optional footer]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semi-colons, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Code changes that improve performance
- **test**: Adding or modifying tests
- **build**: Changes to the build system or dependencies
- **ci**: Changes to CI configuration
- **chore**: Other changes that don't modify src or test files

### Examples

```
feat(knowledge-graph): Add relationship type filtering

Add ability to filter relationships by type in the knowledge graph query system.
This enables more precise graph queries and improves performance by reducing
the amount of data that needs to be processed.

Closes #123
```

```
fix(ui): Resolve authentication token refresh issue

The token refresh logic was not properly handling expired tokens, causing
users to be unexpectedly logged out. This fix implements proper token refresh
before expiration.

Fixes #456
```

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Contact

If you have questions about contributing, please:

- Open an issue on GitHub
- Reach out to project maintainers

Thank you for contributing to the AI Research Integration Project!