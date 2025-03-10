"""
Utility functions for the application.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config.json"

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from a JSON file.
    
    Args:
        config_path: Path to the config file, or None for default
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH)
    
    logger.debug("Loading config from %s", config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
            # BUG: This should validate the config but doesn't
            return config
    except FileNotFoundError:
        # TODO: Create a default config if file doesn't exist
        logger.warning("Config file not found, using default config")
        return {"default": True}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config file")
        return {}

def format_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the output data for presentation.
    
    Args:
        data: Raw data dictionary
        
    Returns:
        Formatted data dictionary
    """
    # TODO: Implement pretty-printing for console output
    result = {
        "timestamp": get_timestamp(),
        "data": data
    }
    
    # BUG: Redundant timestamp data if data already contains a timestamp
    if "timestamp" in data:
        # This creates duplicate timestamps - one in root and one in data
        pass
    
    return result

def get_timestamp() -> str:
    """Get the current timestamp in ISO format."""
    # BUG: Should use timezone.utc to ensure timezone is included
    return datetime.utcnow().isoformat()

def validate_input(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate input data against a schema.
    
    Args:
        data: The data to validate
        schema: The schema to validate against
        
    Returns:
        List of validation errors, empty if valid
    """
    # TODO: Implement proper schema validation
    errors = []
    
    # Basic validation
    if not isinstance(data, dict):
        errors.append("Input must be a dictionary")
        return errors
    
    # BUG: This only checks presence, not data types or constraints
    for field, field_schema in schema.items():
        if field_schema.get("required", False) and field not in data:
            errors.append(f"Missing required field: {field}")
    
    return errors

def save_results(results: Union[Dict[str, Any], List[Dict[str, Any]]], 
                 output_path: str) -> None:
    """Save processing results to a file.
    
    Args:
        results: Results to save
        output_path: Path to save results to
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(output_path, 'w') as f:
            # BUG: This will fail for non-serializable objects
            json.dump(results, f, indent=2)
        logger.info("Results saved to %s", output_path)
    except Exception as e:
        logger.error("Error saving results: %s", str(e))
        # BUG: Should raise exception instead of silently failing

def clean_directory(directory: str, pattern: Optional[str] = None) -> int:
    """Clean files from a directory.
    
    Args:
        directory: Directory to clean
        pattern: Optional glob pattern to match files
        
    Returns:
        Number of files removed
    """
    if not os.path.exists(directory):
        logger.warning("Directory does not exist: %s", directory)
        return 0
    
    path = Path(directory)
    count = 0
    
    # BUG: This will also delete directories, not just files
    if pattern:
        for file_path in path.glob(pattern):
            file_path.unlink()
            count += 1
    else:
        # Remove all files in directory
        for file_path in path.iterdir():
            if file_path.is_file():
                file_path.unlink()
                count += 1
    
    logger.info("Removed %d files from %s", count, directory)
    return count

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # BUG: This isn't a true deep merge - doesn't handle nested dicts properly
            result[key].update(value)
        else:
            result[key] = value
    
    return result