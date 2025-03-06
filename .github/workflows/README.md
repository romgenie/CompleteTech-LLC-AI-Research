# CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration and delivery.

## Knowledge Extraction Test Workflows

The following workflows are implemented for the Knowledge Extraction component:

### 1. Knowledge Extraction Tests (`knowledge_extraction_tests.yml`)

This workflow runs tests for the Knowledge Extraction component when changes are made to the relevant code.

Features:
- Matrix testing across Python 3.9 and 3.10
- Separate jobs for different test types (unit, integration, e2e, property, edge)
- Artifact upload for test reports
- Dedicated benchmark job
- Code coverage reporting

Triggers:
- Push to main branch (affecting Knowledge Extraction files)
- Pull requests to main branch (affecting Knowledge Extraction files)

### 2. Generate Test Status Badges (`generate_test_badges.yml`)

This workflow generates status badges for Knowledge Extraction tests.

Features:
- Automatically updates badges based on test results
- Adds badge section to README if not present
- Supports different badge status for each test type and Python version

Triggers:
- Completion of Knowledge Extraction Tests workflow

### 3. Dependency Review (`dependency_review.yml`)

This workflow checks for security vulnerabilities in dependencies.

Features:
- Automatically scans dependencies in pull requests
- Fails on high severity vulnerabilities
- Provides detailed reports

Triggers:
- Pull requests to main branch

## Usage

These workflows run automatically based on their triggers. No manual action is required.

For local testing before committing changes, you can run:

```bash
cd tests/research_orchestrator/knowledge_extraction
./run_tests.sh -t all
```

## Badge Status

Badges are automatically generated and updated in the README of the knowledge extraction component.