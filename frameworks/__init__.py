"""
Agent framework implementations.

This package provides standardized wrappers for different agent frameworks,
including LangChain, LlamaIndex, AutoGen, and others.
"""

from frameworks.langchain_agent import run_agent as run_langchain
from frameworks.llamaindex_agent import run_agent as run_llamaindex
from frameworks.autogen_agent import run_agent as run_autogen
from frameworks.semantic_kernel_agent import run_agent as run_semantic_kernel
from frameworks.dspy_agent import run_agent as run_dspy
from frameworks.smolagents_agent import run_agent as run_smolagents

# Export run functions for each framework
__all__ = [
    'run_langchain',
    'run_llamaindex',
    'run_autogen',
    'run_semantic_kernel',
    'run_dspy',
    'run_smolagents'
]