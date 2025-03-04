"""
Utility functions for the Research Orchestration Framework.

This module provides common utility functions used across the Research
Orchestration Framework.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger.remove()  # Remove default handler
    logger.add(
        "logs/research_orchestrator_{time}.log",
        rotation="100 MB",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    )
    logger.add(
        lambda msg: print(msg),
        level=log_level,
        format="{time:HH:mm:ss} | {level} | {message}",
    )


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the configuration
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        yaml.YAMLError: If the configuration file can't be parsed
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise


def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """
    Save configuration to a YAML file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration file
        
    Raises:
        yaml.YAMLError: If the configuration can't be serialized to YAML
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w") as f:
        try:
            yaml.dump(config, f, default_flow_style=False)
        except yaml.YAMLError as e:
            logger.error(f"Error saving configuration file: {e}")
            raise


def generate_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        A unique string identifier
    """
    return str(uuid.uuid4())


def timestamp() -> str:
    """
    Get the current timestamp as a string.
    
    Returns:
        Current timestamp in ISO format
    """
    return datetime.now().isoformat()


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for the directory
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict containing the JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file can't be parsed as JSON
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            raise


def save_json(data: Dict[str, Any], file_path: Union[str, Path], pretty: bool = True) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the JSON file
        pretty: Whether to format the JSON with indentation
        
    Raises:
        json.JSONDecodeError: If the data can't be serialized to JSON
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w") as f:
        try:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        except (TypeError, OverflowError) as e:
            logger.error(f"Error saving JSON file: {e}")
            raise