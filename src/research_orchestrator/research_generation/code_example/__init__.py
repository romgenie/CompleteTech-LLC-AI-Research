"""
Code Example Generation module for the Research Generation System.

This module provides functionality for generating code examples, algorithm
implementations, and practical demonstrations based on research concepts.
"""

from .code_example_generator import (
    CodeExampleGenerator,
    ProgrammingLanguage,
    CodeStyle,
    CodeExampleConfig,
    CodeExample
)
from .language_adapters import (
    LanguageAdapter,
    PythonAdapter,
    JavaScriptAdapter,
    JavaAdapter,
    CppAdapter,
    RAdapter
)
from .template_manager import (
    CodeTemplateManager,
    CodeTemplate
)

__all__ = [
    "CodeExampleGenerator",
    "ProgrammingLanguage",
    "CodeStyle",
    "CodeExampleConfig",
    "CodeExample",
    "LanguageAdapter",
    "PythonAdapter",
    "JavaScriptAdapter",
    "JavaAdapter",
    "CppAdapter",
    "RAdapter",
    "CodeTemplateManager",
    "CodeTemplate"
]