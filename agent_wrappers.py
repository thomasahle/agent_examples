#!/usr/bin/env python3
"""
Unified wrapper module for different agent frameworks.
This module provides a consistent interface to load and run agents
from various frameworks (LangChain, LlamaIndex, AutoGen, etc.).
"""

import importlib
import os
from typing import Dict, Any, List, Optional, Union

from config import AgentConfig

def run_agent(framework: str, prompt: str) -> str:
    """
    Run an agent with the specified framework and prompt.
    
    Args:
        framework: Name of the agent framework to use (or path to script)
        prompt: The task description
        
    Returns:
        Agent's response as a string
    """
    print(f"Running agent with framework: {framework}")
    
    # Handle agent by name
    framework_name = _normalize_framework_name(framework)
    
    # Import the module for the specified framework
    try:
        # Handle both framework names and explicit script paths
        if framework_name in AgentConfig.AVAILABLE_AGENTS:
            # Known framework name
            module_name = f"frameworks.{framework_name}_agent"
            module = importlib.import_module(module_name)
            
            # Call the run_agent function from the imported module
            return module.run_agent(prompt)
        else:
            # Try importing as a path (legacy support)
            base_name = os.path.basename(framework)
            module_name = os.path.splitext(base_name)[0]
            
            # Add the current directory to the path temporarily
            import sys
            sys.path.append(".")
            
            # Import the module
            try:
                module = importlib.import_module(module_name)
                return module.run_agent(prompt)
            except (ImportError, AttributeError):
                raise ValueError(f"Could not load agent from {framework}")
            finally:
                # Remove the current directory from the path
                if "." in sys.path:
                    sys.path.remove(".")
                    
    except ImportError as e:
        raise ImportError(f"Framework '{framework_name}' not found: {str(e)}")
    except AttributeError:
        raise AttributeError(f"Framework '{framework_name}' does not have a run_agent function")

def _normalize_framework_name(framework: str) -> str:
    """
    Normalize the framework name.
    
    Args:
        framework: Name of the framework or path to script
        
    Returns:
        Normalized framework name
    """
    # Handle file paths
    if os.path.isfile(framework):
        basename = os.path.basename(framework)
        framework_name = os.path.splitext(basename)[0]
        
        # Convert example.py naming to base name
        if framework_name.endswith("_example"):
            framework_name = framework_name[:-8]
            
        return framework_name
    
    # Handle framework names with variations
    framework = framework.lower()
    
    # Map common variations to standard names
    name_mapping = {
        "langchain_example.py": "langchain",
        "langchain_example": "langchain",
        "langchain": "langchain",
        "llamaindex_example.py": "llamaindex",
        "llamaindex_example": "llamaindex",
        "llamaindex": "llamaindex",
        "semantic_kernel_example.py": "semantic_kernel",
        "semantic_kernel_example": "semantic_kernel",
        "semantic_kernel": "semantic_kernel",
        "semantickernel": "semantic_kernel",
        "autogen_example.py": "autogen",
        "autogen_example": "autogen",
        "autogen": "autogen",
        "smolagents_example.py": "smolagents",
        "smolagents_example": "smolagents",
        "smolagents": "smolagents",
        "dspy_react_example.py": "dspy",
        "dspy_react_example": "dspy",
        "dspy_react": "dspy",
        "dspy": "dspy"
    }
    
    return name_mapping.get(framework, framework)

if __name__ == "__main__":
    # Example usage
    response = run_agent(
        "langchain",
        "Find all files in the test_codebase directory with bug comments"
    )
    print(f"Response: {response}")