"""
Implementation Details package for the Research Understanding Engine.

This package provides components for extracting detailed implementation information
from research papers to facilitate accurate code generation.
"""

from .detail_collector import (
    CodeSnippet,
    ImplementationRequirement,
    DatasetInfo,
    EvaluationMetric,
    HyperparameterInfo,
    EnvironmentInfo,
    ImplementationDetail,
    ImplementationDetailCollector
)

__all__ = [
    'CodeSnippet',
    'ImplementationRequirement',
    'DatasetInfo',
    'EvaluationMetric',
    'HyperparameterInfo',
    'EnvironmentInfo',
    'ImplementationDetail',
    'ImplementationDetailCollector',
]