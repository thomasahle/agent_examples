#!/usr/bin/env python3
"""
File operation utilities for agent frameworks.

This module provides a unified set of file operation tools that can be used
across different agent frameworks, including functions for reading files,
searching for patterns in files, and managing file paths.
"""

import os
from typing import List, Optional, Union, Dict, Tuple, Set

def read_file(file_path: str, limit: Optional[int] = None, offset: int = 0) -> str:
    """
    Read the contents of a specific file.

    Args:
        file_path: Path to the file to read
        limit: Maximum number of lines to read (None for all)
        offset: Line number to start reading from (0-indexed)

    Returns:
        String containing the file contents or an error message
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if limit is None and offset == 0:
                content = f.read()
                if len(content) > 100000:  # Truncate very large files
                    return content[:100000] + "\n... [truncated, file too large] ..."
                return content
            else:
                # Read specific lines
                lines = f.readlines()
                end = len(lines) if limit is None else min(offset + limit, len(lines))
                return "".join(lines[offset:end])
    except Exception as e:
        return f"Error reading file: {e}"

def search_files(query: str, 
                 path: str = ".", 
                 file_extensions: Optional[List[str]] = None,
                 max_matches: int = 100,
                 ignore_dirs: Optional[Set[str]] = None) -> str:
    """
    Search for a string pattern in files and return matching lines.

    Args:
        query: The string pattern to search for
        path: Directory path to search in (default: current directory)
        file_extensions: List of file extensions to search (default: common code files)
        max_matches: Maximum number of matches to return
        ignore_dirs: Set of directory names to ignore

    Returns:
        String with the search results in format "file:line_number:matching_line"
    """
    if file_extensions is None:
        file_extensions = [".py", ".txt", ".md", ".json", ".js", ".html", ".css"]
    
    if ignore_dirs is None:
        ignore_dirs = {".git", "__pycache__", "venv", "env", "node_modules"}
    
    matches = []
    file_count = 0
    
    for root, dirs, files in os.walk(path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for fname in files:
            if any(fname.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, fname)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if query in line:
                                matches.append(f"{file_path}:{line_num}:{line.strip()}")
                                if len(matches) >= max_matches:
                                    break
                    if matches and file_path not in [m.split(":", 1)[0] for m in matches]:
                        file_count += 1
                except Exception:
                    continue
                
                if len(matches) >= max_matches:
                    break
        
        if len(matches) >= max_matches:
            break
    
    if not matches:
        return "No matches found."
    
    if len(matches) == max_matches:
        return "\n".join(matches) + f"\n... (reached maximum of {max_matches} matches, there might be more)"
    
    return "\n".join(matches)

def list_files(path: str = ".", 
               recursive: bool = True, 
               file_extensions: Optional[List[str]] = None,
               ignore_dirs: Optional[Set[str]] = None) -> List[str]:
    """
    List files in a directory, optionally filtering by extension.

    Args:
        path: Directory path to list files from
        recursive: Whether to search subdirectories recursively
        file_extensions: List of file extensions to include (None for all files)
        ignore_dirs: Set of directory names to ignore

    Returns:
        List of file paths matching the criteria
    """
    if ignore_dirs is None:
        ignore_dirs = {".git", "__pycache__", "venv", "env", "node_modules"}
    
    result = []
    
    if recursive:
        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for fname in files:
                if file_extensions is None or any(fname.endswith(ext) for ext in file_extensions):
                    result.append(os.path.join(root, fname))
    else:
        # Non-recursive, just list the current directory
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                if file_extensions is None or any(item.endswith(ext) for ext in file_extensions):
                    result.append(item_path)
    
    return result

def get_file_info(file_path: str) -> Dict[str, Union[str, int, bool]]:
    """
    Get detailed information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary containing file information (size, modification time, etc.)
    """
    try:
        stat_info = os.stat(file_path)
        return {
            "path": file_path,
            "size": stat_info.st_size,
            "last_modified": stat_info.st_mtime,
            "is_directory": os.path.isdir(file_path),
            "exists": True,
            "extension": os.path.splitext(file_path)[1] if os.path.isfile(file_path) else None
        }
    except Exception as e:
        return {
            "path": file_path,
            "exists": False,
            "error": str(e)
        }

def save_file(file_path: str, content: str, mode: str = "w") -> str:
    """
    Save content to a file.

    Args:
        file_path: Path to the file to save
        content: String content to write to the file
        mode: File opening mode ('w' for write, 'a' for append)

    Returns:
        Success message or error message
    """
    try:
        # Create directories if they don't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)
        return f"Successfully saved to {file_path}"
    except Exception as e:
        return f"Error saving file: {e}"