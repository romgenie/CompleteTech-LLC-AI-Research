"""
Setup script for the AI Research Integration Project.
"""

from setuptools import setup, find_packages

setup(
    name="ai-research-integration",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.0",
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
    ],
    python_requires=">=3.9",
)