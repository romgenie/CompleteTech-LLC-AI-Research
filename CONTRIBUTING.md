# Contributing to AI Research Integration Project

Thank you for your interest in contributing to the AI Research Integration Project! This document provides guidelines for contributing to the project.

## Code of Conduct

All contributors are expected to adhere to the project's code of conduct. Be respectful and professional in all communications and interactions with the community.

## Getting Started

1. Fork the repository
2. Clone your fork locally: `git clone https://github.com/your-username/ai-research-integration.git`
3. Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature-name`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Set up pre-commit hooks: `pre-commit install`

## Development Workflow

1. Make sure to follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation as necessary
4. Run tests to ensure your changes don't break existing functionality: `pytest`
5. Run linting checks: `pre-commit run --all-files`

## Pull Request Process

1. Update the README.md or relevant documentation with details of changes if appropriate
2. Update the CHANGELOG.md file with details of your changes
3. Make sure all tests pass and the code follows the project's style guidelines
4. Submit a pull request with a clear description of the changes and the problem they solve
5. The pull request will be reviewed by the maintainers

## Coding Standards

This project follows the standards defined in:

- **PEP 8** for code style
- **Google Style** for docstrings
- **Type hints** for all function definitions
- **Comprehensive tests** for all functionality

## Commit Message Format

Please use clear and descriptive commit messages. Structure them as follows:

```
type(scope): Subject

Body

Footer
```

Where `type` can be:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code style changes (formatting, missing semi-colons, etc)
- refactor: Code changes that neither fix bugs nor add features
- test: Adding or modifying tests
- chore: Changes to the build process or auxiliary tools

## License

By contributing your code, you agree to license your contribution under the project's MIT license.

## Questions?

If you have any questions, please open an issue or reach out to the project maintainers.