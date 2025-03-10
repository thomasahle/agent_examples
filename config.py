#!/usr/bin/env python3
"""
Centralized configuration module for agent frameworks.
This module provides a unified configuration interface for API keys,
model settings, tool configurations, and path settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CODEBASE_PATH = BASE_DIR / "test_codebase"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# API Key Configuration
class APIKeys:
    """API key management for various services."""
    
    @staticmethod
    def get_openai_api_key() -> str:
        """Get OpenAI API key from environment variable or raise error."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
        return api_key
    
    @staticmethod
    def get_anthropic_api_key() -> Optional[str]:
        """Get Anthropic API key from environment variable."""
        return os.environ.get("ANTHROPIC_API_KEY")
    
    @staticmethod
    def get_azure_openai_api_key() -> Optional[str]:
        """Get Azure OpenAI API key from environment variable."""
        return os.environ.get("AZURE_OPENAI_API_KEY")
    
    @staticmethod
    def get_azure_openai_endpoint() -> Optional[str]:
        """Get Azure OpenAI endpoint from environment variable."""
        return os.environ.get("AZURE_OPENAI_ENDPOINT")

# Model Configuration
class ModelConfig:
    """Configuration for language models across different frameworks."""
    
    # Default model settings
    DEFAULT_MODEL = "gpt-4-turbo"
    DEFAULT_TEMPERATURE = 0.0
    DEFAULT_MAX_TOKENS = 4000
    DEFAULT_CONTEXT_WINDOW = 8192
    
    # Model configurations by framework
    LANGCHAIN = {
        "model": os.environ.get("LANGCHAIN_MODEL", DEFAULT_MODEL),
        "temperature": float(os.environ.get("LANGCHAIN_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.environ.get("LANGCHAIN_MAX_TOKENS", DEFAULT_MAX_TOKENS))
    }
    
    LLAMAINDEX = {
        "model": os.environ.get("LLAMAINDEX_MODEL", DEFAULT_MODEL),
        "temperature": float(os.environ.get("LLAMAINDEX_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.environ.get("LLAMAINDEX_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        "context_window": int(os.environ.get("LLAMAINDEX_CONTEXT_WINDOW", DEFAULT_CONTEXT_WINDOW))
    }
    
    SEMANTIC_KERNEL = {
        "model": os.environ.get("SEMANTIC_KERNEL_MODEL", DEFAULT_MODEL),
        "temperature": float(os.environ.get("SEMANTIC_KERNEL_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.environ.get("SEMANTIC_KERNEL_MAX_TOKENS", DEFAULT_MAX_TOKENS))
    }
    
    AUTOGEN = {
        "model": os.environ.get("AUTOGEN_MODEL", DEFAULT_MODEL),
        "temperature": float(os.environ.get("AUTOGEN_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.environ.get("AUTOGEN_MAX_TOKENS", DEFAULT_MAX_TOKENS))
    }
    
    SMOLAGENTS = {
        "model": os.environ.get("SMOLAGENTS_MODEL", DEFAULT_MODEL),
        "temperature": float(os.environ.get("SMOLAGENTS_TEMPERATURE", DEFAULT_TEMPERATURE))
    }
    
    DSPY = {
        "model": os.environ.get("DSPY_MODEL", DEFAULT_MODEL),
        "temperature": float(os.environ.get("DSPY_TEMPERATURE", DEFAULT_TEMPERATURE))
    }

# Tool Configuration
class ToolConfig:
    """Configuration for agent tools."""
    
    # Default tool timeout
    DEFAULT_TIMEOUT = 60  # seconds
    
    # Ignored directories for file operations
    IGNORED_DIRS = {".git", "__pycache__", "venv", "env", "node_modules", "bug_finder_env"}
    
    # File extensions to search
    SEARCHABLE_EXTENSIONS = (".py", ".txt", ".md", ".json", ".js", ".html", ".css")
    
    # Max content length for file reads
    MAX_CONTENT_LENGTH = 10000
    
    # Shell command configuration
    SHELL_CONFIG = {
        "timeout": int(os.environ.get("TOOL_SHELL_TIMEOUT", DEFAULT_TIMEOUT)),
        "allowed_commands": ["ls", "grep", "find", "cat", "head", "tail", "wc", "echo"]
    }
    
    # Search configuration
    SEARCH_CONFIG = {
        "max_matches": int(os.environ.get("TOOL_SEARCH_MAX_MATCHES", 100)),
        "ignored_dirs": IGNORED_DIRS,
        "file_extensions": SEARCHABLE_EXTENSIONS
    }
    
    # File read configuration
    FILE_READ_CONFIG = {
        "max_content_length": int(os.environ.get("TOOL_READ_MAX_LENGTH", MAX_CONTENT_LENGTH)),
        "ignored_dirs": IGNORED_DIRS
    }

# Agent Configurations
class AgentConfig:
    """Configuration for agent frameworks."""
    
    # List of available agents
    AVAILABLE_AGENTS = [
        "langchain",
        "llamaindex",
        "semantic_kernel",
        "autogen",
        "smolagents",
        "dspy"
    ]
    
    # Default system prompt template for agents
    DEFAULT_SYSTEM_PROMPT = """You are a code analysis assistant that specializes in finding bugs and issues in code.
Your task is to analyze the test_codebase directory and identify all bugs marked with '# BUG:' comments.

Follow these steps:
1. Use tools to explore the codebase and locate all files containing '# BUG:' comments
2. For each bug you find, analyze the surrounding code to understand what the issue is
3. Explain each bug clearly and suggest a possible solution
4. Present your findings in a structured, numbered list format

Be thorough and systematic in your analysis. Your response should include:
- The file and line number where each bug is located
- A clear explanation of what's wrong
- A specific suggestion for how to fix each issue"""
    
    # Agent execution configuration
    EXECUTION_CONFIG = {
        "max_iterations": int(os.environ.get("AGENT_MAX_ITERATIONS", 15)),
        "max_execution_time": int(os.environ.get("AGENT_MAX_EXECUTION_TIME", 300)),  # 5 minutes
        "verbose": os.environ.get("AGENT_VERBOSE", "False").lower() == "true"
    }
    
    # Bug pattern for searching
    BUG_PATTERN = r"# BUG:\s*(.*)"
    
    # Output file for evaluation results
    OUTPUT_FILE = "agent_bug_evaluation_results.json"

# Paths Configuration
class PathConfig:
    """Configuration for file and directory paths."""
    
    # Base directory paths
    BASE_DIR = BASE_DIR
    CODEBASE_PATH = CODEBASE_PATH
    OUTPUT_DIR = OUTPUT_DIR
    
    # Tool-specific paths
    TOOL_OUTPUT_PATH = OUTPUT_DIR / "tool_outputs"
    
    # Results paths
    RESULTS_PATH = OUTPUT_DIR / AgentConfig.OUTPUT_FILE
    
    # Ensure all directories exist
    @classmethod
    def ensure_dirs(cls):
        """Ensure all required directories exist."""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.TOOL_OUTPUT_PATH.mkdir(exist_ok=True)