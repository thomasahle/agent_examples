"""
Agent framework implementations.

This package provides standardized wrappers for different agent frameworks,
including LangChain, LlamaIndex, AutoGen, and others.
"""

from frameworks.langchain_agent import run_agent as run_langchain

# Export run functions for each framework
__all__ = [
    'run_langchain'
]