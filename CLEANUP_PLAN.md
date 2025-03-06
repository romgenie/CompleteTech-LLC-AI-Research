# Cleanup Plan

## 1. Remove Debug Files
rm debug_document_processor.py
rm debug_test.py

## 2. Add .gitignore Rules
cat << 'EOF' > .gitignore
# Python cache files
__pycache__/
*.py[cod]
*.class

# Virtual environments
venv/
env/
.env/
.venv/

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log

# Build outputs
dist/
build/
*.egg-info/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Debug files
debug_*.py

# Test cache
.pytest_cache/
.coverage
htmlcov/
coverage.xml

# Frontend build artifacts
ui_backup/
EOF

## 3. Handle Frontend Files
git rm -r --cached src/ui/frontend/
mkdir -p src/ui/frontend-new

## 4. Update Requirements
git add requirements.txt requirements-api.txt

## 5. Add Untracked Test Files
git add tests/research_orchestrator/information_gathering/edge_cases/
git add tests/research_orchestrator/information_gathering/property/test_quality_assessor_properties.py
git add tests/research_orchestrator/information_gathering/property/test_source_manager_properties.py

