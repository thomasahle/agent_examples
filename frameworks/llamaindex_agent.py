#!/usr/bin/env python3
"""
Streamlined LlamaIndex agent framework wrapper.
This provides a simplified interface for creating and running LlamaIndex agents.
"""

import os
from typing import Dict, Any, List, Optional, Union, Callable

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

# Import our shared utilities
from utils.tools.shell_tools import run_shell_command
from utils.tools.file_tools import read_file, search_files
from config import ModelConfig

class LlamaIndexAgent:
    """A streamlined wrapper for LlamaIndex agents."""
    
    def __init__(
        self, 
        model_name: Optional[str] = None, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        verbose: bool = False
    ):
        """
        Initialize the LlamaIndex agent.
        
        Args:
            model_name: The OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in model response
            verbose: Whether to show verbose output
        """
        # Load environment variables
        load_dotenv()
        
        # Use configuration defaults if not specified
        self.model_name = model_name or ModelConfig.LLAMAINDEX["model"]
        self.temperature = temperature if temperature is not None else ModelConfig.LLAMAINDEX["temperature"]
        self.max_tokens = max_tokens or ModelConfig.LLAMAINDEX["max_tokens"]
        self.verbose = verbose
        
        # Initialize the LLM and tools
        self._setup_llm()
        self.tools = self._get_tools()
        
    def _setup_llm(self) -> None:
        """Set up the LLM for LlamaIndex."""
        # Configure LlamaIndex with OpenAI
        Settings.llm = OpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        self.llm = Settings.llm
        
    def _get_tools(self) -> List[FunctionTool]:
        """Get the tools for the agent."""
        return [
            FunctionTool.from_defaults(
                name="shell",
                description="Run shell commands and return output.",
                fn=self._run_shell_command
            ),
            FunctionTool.from_defaults(
                name="search_code",
                description="Search for a string in code files (usage: provide search query).",
                fn=self._search_code
            ),
            FunctionTool.from_defaults(
                name="read_file",
                description="Read the contents of a specific file.",
                fn=self._read_file
            ),
            FunctionTool.from_defaults(
                name="ask_user",
                description="Ask the user a question for more information.",
                fn=self._ask_user
            )
        ]
    
    def _run_shell_command(self, command: str) -> str:
        """Run a shell command and return the output."""
        return run_shell_command(command, timeout=60)
    
    def _search_code(self, query: str) -> str:
        """Search for a string in code files."""
        return search_files(
            query=query, 
            path=".", 
            file_extensions=[".py", ".txt", ".md", ".json", ".js", ".html", ".css"],
            max_matches=100
        )
    
    def _read_file(self, file_path: str) -> str:
        """Read the contents of a specific file."""
        return read_file(file_path)
    
    def _ask_user(self, question: str) -> str:
        """Ask the user a question for more information."""
        # For automated evaluation, return a default message
        if os.environ.get("AUTOMATED_EVALUATION") == "1":
            return "Please continue with what you know. This is an automated evaluation."
        return input(f"[Agent] {question}\nUser: ")
    
    def create_agent(self) -> ReActAgent:
        """
        Create a LlamaIndex agent with the specified tools.
        
        Returns:
            A configured ReActAgent
        """
        # Create the agent with the tools
        agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            verbose=self.verbose,
            system_prompt="""You are a helpful AI assistant that specializes in finding bugs and issues in code.
Your task is to analyze code repositories and identify bugs marked with '# BUG:' comments.

When analyzing code, make sure to:
1. Locate all files that might contain '# BUG:' comments
2. Understand what each bug is about
3. Analyze the surrounding code to explain the issue
4. Suggest how to fix each bug
5. Present your findings in a structured, numbered list

Use the provided tools (shell commands, code search, file reading) to explore the codebase systematically.
Be thorough in your analysis and clear in your explanations."""
        )
        
        return agent
    
    def run(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Run the agent on a prompt.
        
        Args:
            prompt: The task prompt for the agent
            system_prompt: Optional custom system prompt (not used in LlamaIndex)
            
        Returns:
            The agent's response as a string
        """
        agent = self.create_agent()
        response = agent.chat(prompt)
        return str(response)


def run_agent(prompt: str) -> str:
    """
    Compatibility function for the evaluation harness.
    
    Args:
        prompt: The task prompt
        
    Returns:
        The agent's response
    """
    agent = LlamaIndexAgent(
        model_name="gpt-4-turbo",
        temperature=0,
        max_tokens=4000,
        verbose=False
    )
    
    return agent.run(prompt)


if __name__ == "__main__":
    # Example usage
    agent = LlamaIndexAgent(
        model_name="gpt-3.5-turbo",
        temperature=0,
        verbose=True
    )
    
    result = agent.run(
        "Analyze the test_codebase directory and identify all bugs marked with '# BUG:' comments."
    )
    
    print(f"Result: {result}")