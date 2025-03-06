#!/usr/bin/env python3
"""
Repository Reorganization Script

This script helps reorganize the repository structure according to the plan
outlined in REORGANIZATION_PLAN.md.

Usage:
    python reorganize_repo.py
"""

import os
import shutil
import re
import sys
from pathlib import Path
import subprocess


def create_directory_structure():
    """Create the target directory structure."""
    print("Creating directory structure...")
    
    # Define the directories to create
    directories = [
        # Main module directories
        "src/api",
        "src/knowledge_graph_system",
        "src/paper_processing",
        "src/research_implementation",
        "src/research_orchestrator",
        "src/ui/components",
        "src/ui/pages",
        "src/ui/services",
        "src/ui/utils",
        
        # Documentation directories
        "docs/architecture",
        "docs/modules",
        "docs/implementation_plans",
        "docs/testing",
        "docs/user_guides",
        
        # Test directories
        "tests/knowledge_graph_system",
        "tests/research_implementation",
        "tests/research_orchestrator",
        "tests/ui",
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py in Python module directories
        if directory.startswith("src/") and not directory.endswith("ui"):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write("# Module initialization\n")
    
    print("Directory structure created successfully.")


def move_files():
    """Move files to their new locations."""
    print("Moving files to new locations...")
    
    # Define file movement mapping (source -> target)
    moves = [
        # Move modules from root to src
        ("research_implementation", "src/research_implementation"),
        ("knowledge_graph_system", "src/knowledge_graph_system"),
        ("research_orchestrator", "src/research_orchestrator"),
        
        # Move documentation files to docs directory
        ("*_PLAN.md", "docs/implementation_plans"),
        ("*_SPEC.md", "docs/architecture"),
        ("*_TESTING.md", "docs/testing"),
        
        # Move UI files
        ("src/ui/frontend-new", "src/ui"),
    ]
    
    # Execute moves using rsync for better control and error handling
    for source, target in moves:
        if os.path.exists(source):
            print(f"Moving {source} to {target}...")
            if "*" in source:
                # Handle glob patterns
                for file in Path('.').glob(source):
                    if file.is_file():
                        shutil.copy2(file, os.path.join(target, file.name))
                        print(f"  Copied {file} to {target}")
            else:
                # Use rsync for recursive copy
                rsync_cmd = ["rsync", "-av", source + "/", target + "/"]
                subprocess.run(rsync_cmd, check=True)
    
    print("Files moved successfully.")


def update_imports():
    """Update import statements throughout the codebase."""
    print("Updating import statements...")
    
    patterns = [
        # Match absolute imports from root modules
        (r'from (research_orchestrator|knowledge_graph_system|research_implementation)\.', 
         r'from src.\1.'),
        
        # Match relative imports that need fixing based on new structure
        (r'from \.\.([^\.])', 
         r'from ..\1'),
    ]
    
    # Find all Python files
    python_files = list(Path('src').rglob("*.py"))
    
    # Process each file
    for file_path in python_files:
        update_file_imports(file_path, patterns)
    
    print("Import statements updated successfully.")


def update_file_imports(file_path, patterns):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Apply all patterns
        modified = False
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                modified = True
        
        # Write back if modified
        if modified:
            with open(file_path, 'w') as file:
                file.write(content)
            print(f"  Updated imports in {file_path}")
    except Exception as e:
        print(f"  Error updating {file_path}: {e}")


def update_configuration():
    """Update setup.py and other configuration files."""
    print("Updating configuration files...")
    
    # Update setup.py
    if os.path.exists("setup.py"):
        with open("setup.py", 'r') as file:
            content = file.read()
        
        # Update package paths
        new_content = re.sub(
            r'packages=find_packages\(\)',
            r'packages=find_packages(where="src")\n    package_dir={"": "src"}',
            content
        )
        
        # Write back if modified
        if new_content != content:
            with open("setup.py", 'w') as file:
                file.write(new_content)
            print("  Updated setup.py")
    
    print("Configuration files updated successfully.")


def create_readme_updates():
    """Create a document with suggested README updates."""
    print("Creating README update suggestions...")
    
    with open("README_UPDATES.md", 'w') as file:
        file.write("""# README Update Suggestions

The repository structure has been reorganized. Consider updating the README.md with the following information:

## Updated Project Structure

```
repository/
├── docs/                      # Project documentation
│   ├── architecture/          # System architecture documents
│   ├── implementation_plans/  # Implementation plans
│   ├── modules/               # Module-specific documentation
│   ├── testing/               # Testing documentation
│   └── user_guides/           # End-user documentation
├── src/                       # Source code
│   ├── api/                   # API server and routes
│   ├── knowledge_graph_system/# Knowledge graph components
│   ├── paper_processing/      # Paper processing pipeline
│   ├── research_implementation/# Implementation system
│   ├── research_orchestrator/ # Main orchestration framework
│   └── ui/                    # Frontend components
├── tests/                     # Test suite
│   ├── knowledge_graph_system/# Knowledge graph tests
│   ├── research_implementation/# Implementation system tests
│   ├── research_orchestrator/ # Orchestration framework tests
│   └── ui/                    # Frontend tests
├── README.md                  # Project overview
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # Project license
├── setup.py                   # Package setup script
├── requirements.txt           # Project dependencies
└── docker-compose.yml         # Docker configuration
```

## Development and Testing

With the reorganized structure, imports should follow this pattern:

```python
# For internal imports
from src.research_orchestrator.knowledge_extraction import KnowledgeExtractor

# After package installation
from ai_research_integration.research_orchestrator.knowledge_extraction import KnowledgeExtractor
```

Running tests:

```bash
# Install package in development mode
pip install -e .

# Run all tests
python -m pytest tests/

# Run specific module tests
python -m pytest tests/research_orchestrator/
```
""")
    
    print("README update suggestions created successfully.")


def main():
    """Main function to execute the reorganization."""
    print("Starting repository reorganization...")
    
    # Skip confirmation in non-interactive environments
    if sys.stdin.isatty():
        response = input("This will reorganize the repository structure. Continue? (y/n): ")
        if response.lower() != 'y':
            print("Reorganization cancelled.")
            sys.exit(0)
    else:
        print("Running in non-interactive mode. Proceeding with reorganization...")
    
    try:
        # Execute steps
        create_directory_structure()
        move_files()
        update_imports()
        update_configuration()
        create_readme_updates()
        
        print("\nReorganization completed successfully!")
        print("Please review the changes and check for any issues.")
        print("See README_UPDATES.md for suggested README updates.")
    except Exception as e:
        print(f"Error during reorganization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()