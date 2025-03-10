#!/usr/bin/env python3
"""
Common utility functions for agent frameworks.

This module provides shared helper functions used across different
parts of the agent examples project, including JSON handling,
result formatting, evaluation metrics, and code parsing utilities.
"""

import os
import json
import re
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Set, Callable

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================
# 1. JSON Data Loading/Saving Utilities
# ============================================================

def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
        raise

def save_json(data: Union[Dict[str, Any], List[Dict[str, Any]]], file_path: str, indent: int = 2) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the data to
        indent: Number of spaces for indentation (default: 2)
        
    Raises:
        Exception: If there's an error saving the data
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        logger.info(f"Data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {str(e)}")
        raise

# ============================================================
# 2. Result Formatting Utilities
# ============================================================

def format_results(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the output data for presentation.
    
    Args:
        data: Raw data dictionary
        
    Returns:
        Formatted data dictionary with added metadata
    """
    result = {
        "timestamp": get_timestamp(),
        "data": data
    }
    
    return result

def get_timestamp() -> str:
    """Get the current timestamp in ISO format with timezone info.
    
    Returns:
        ISO-formatted timestamp with timezone
    """
    return datetime.now(timezone.utc).isoformat()

# ============================================================
# 3. Evaluation Metrics Utilities
# ============================================================

def calculate_recall(found_items: int, total_items: int) -> float:
    """Calculate recall metric.
    
    Args:
        found_items: Number of items found
        total_items: Total number of items
        
    Returns:
        Recall value between 0.0 and 1.0
    """
    if total_items == 0:
        return 0.0
    return found_items / total_items

def calculate_precision(correct_items: int, total_found: int) -> float:
    """Calculate precision metric.
    
    Args:
        correct_items: Number of correctly identified items
        total_found: Total number of items found
        
    Returns:
        Precision value between 0.0 and 1.0
    """
    if total_found == 0:
        return 0.0
    return correct_items / total_found

def calculate_f1_score(precision: float, recall: float) -> float:
    """Calculate F1 score.
    
    Args:
        precision: Precision value
        recall: Recall value
        
    Returns:
        F1 score between 0.0 and 1.0
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

# ============================================================
# 4. Code Parsing Utilities
# ============================================================

def extract_patterns_from_file(file_path: str, pattern: str) -> List[Dict[str, Any]]:
    """Extract all occurrences of a regex pattern from a file.
    
    Args:
        file_path: Path to the file
        pattern: Regex pattern to search for
        
    Returns:
        List of dictionaries containing the matches, line numbers, and context
    """
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                matches = re.findall(pattern, line)
                if matches:
                    for match in matches:
                        results.append({
                            'file': file_path,
                            'line': i,
                            'match': match if isinstance(match, str) else match[0],
                            'content': line.strip()
                        })
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
    
    return results

def scan_directory_for_pattern(directory: str, pattern: str, 
                               file_extensions: Optional[List[str]] = None,
                               ignore_dirs: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
    """Scan a directory for files containing a specific pattern.
    
    Args:
        directory: Directory to scan
        pattern: Regex pattern to search for
        file_extensions: List of file extensions to include (default: ['.py'])
        ignore_dirs: Set of directory names to ignore
        
    Returns:
        List of dictionaries with file paths, line numbers, and matches
    """
    if file_extensions is None:
        file_extensions = ['.py']
    
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules'}
    
    results = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                file_results = extract_patterns_from_file(file_path, pattern)
                results.extend(file_results)
    
    return results

# ============================================================
# 5. Shell Command Utilities
# ============================================================

def run_shell_command(command: str, timeout: int = 60) -> Dict[str, str]:
    """Run a shell command and return stdout/stderr.
    
    Args:
        command: Command to run
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with 'stdout' and 'stderr' keys
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f'Error running command: {str(e)}',
            'returncode': -1
        }

def search_code(query: str, 
               directory: str = ".", 
               file_extensions: Optional[List[str]] = None,
               ignore_dirs: Optional[Set[str]] = None) -> List[str]:
    """Search for a string in code files.
    
    Args:
        query: String to search for
        directory: Directory to search in
        file_extensions: List of file extensions to include
        ignore_dirs: Set of directory names to ignore
        
    Returns:
        List of formatted match strings (path:line:content)
    """
    if file_extensions is None:
        file_extensions = ['.py', '.txt', '.md', '.json', '.js', '.html', '.css']
    
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules'}
    
    matches = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for fname in files:
            if any(fname.endswith(ext) for ext in file_extensions):
                path = os.path.join(root, fname)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if query in line:
                                matches.append(f"{path}:{line_num}:{line.strip()}")
                except Exception:
                    continue
    
    return matches

# ============================================================
# 6. Data Validation Utilities
# ============================================================

def validate_input_data(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate input data against a schema.
    
    Args:
        data: Data to validate
        schema: Schema to validate against
        
    Returns:
        List of validation errors, empty if valid
    """
    errors = []
    
    # Basic validation
    if not isinstance(data, dict):
        errors.append("Input must be a dictionary")
        return errors
    
    # Check required fields
    for field, field_schema in schema.items():
        if field_schema.get("required", False) and field not in data:
            errors.append(f"Missing required field: {field}")
        
        # Check data type if specified and field exists
        if "type" in field_schema and field in data:
            expected_type = field_schema["type"]
            if expected_type == "string" and not isinstance(data[field], str):
                errors.append(f"Field '{field}' must be a string")
            elif expected_type == "integer" and not isinstance(data[field], int):
                errors.append(f"Field '{field}' must be an integer")
            elif expected_type == "number" and not isinstance(data[field], (int, float)):
                errors.append(f"Field '{field}' must be a number")
            elif expected_type == "boolean" and not isinstance(data[field], bool):
                errors.append(f"Field '{field}' must be a boolean")
            elif expected_type == "array" and not isinstance(data[field], list):
                errors.append(f"Field '{field}' must be an array")
            elif expected_type == "object" and not isinstance(data[field], dict):
                errors.append(f"Field '{field}' must be an object")
    
    return errors

# ============================================================
# 7. Dictionary Utilities
# ============================================================

def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries recursively.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested dictionaries
        sep: Separator between keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)