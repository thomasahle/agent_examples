#!/usr/bin/env python3
"""
Streamlined LangChain agent framework wrapper.
This provides a simplified interface for creating and running LangChain agents.
"""

import os
from typing import Dict, Any, List, Optional, Union, Callable

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.tools import Tool
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

# Import our shared utilities
from utils.tools.shell_tools import run_shell_command
from utils.tools.file_tools import read_file, search_files
from config import ModelConfig

class LangChainAgent:
    """A streamlined wrapper for LangChain agents."""
    
    def __init__(
        self, 
        model_name: Optional[str] = None, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
        verbose: bool = False
    ):
        """
        Initialize the LangChain agent.
        
        Args:
            model_name: The OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in model response
            tools: Optional list of custom tools
            verbose: Whether to show verbose output
        """
        # Load environment variables
        load_dotenv()
        
        # Use configuration defaults if not specified
        model_name = model_name or ModelConfig.LANGCHAIN["model"]
        temperature = temperature if temperature is not None else ModelConfig.LANGCHAIN["temperature"]
        max_tokens = max_tokens or ModelConfig.LANGCHAIN["max_tokens"]
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize with default tools if none provided
        self.tools = tools if tools is not None else self._default_tools()
        self.verbose = verbose
        
    def _default_tools(self) -> List[Tool]:
        """Create default tools for the agent."""
        return [
            Tool(
                name="shell",
                func=self._run_shell_command,
                description="Run shell commands and return output."
            ),
            Tool(
                name="search_code",
                func=self._search_code,
                description="Search for a string in code files (usage: provide search query)."
            ),
            Tool(
                name="read_file",
                func=self._read_file,
                description="Read the contents of a specific file."
            ),
            Tool(
                name="ask_user",
                func=self._ask_user,
                description="Ask the user a question for more information."
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
    
    def create_agent(self, system_prompt: str = None) -> AgentExecutor:
        """
        Create a LangChain agent with the specified system prompt.
        
        Args:
            system_prompt: Custom system prompt for the agent
            
        Returns:
            A configured AgentExecutor
        """
        if system_prompt is None:
            system_prompt = "You are a helpful assistant that can use tools to answer questions."
        
        # Create a prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        
        # Create and return the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            max_iterations=10,
            max_execution_time=300,  # 5 minutes timeout
            early_stopping_method="generate"
        )
    
    def run(self, prompt: str, system_prompt: str = None) -> str:
        """
        Run the agent on a prompt.
        
        Args:
            prompt: The task prompt for the agent
            system_prompt: Optional custom system prompt
            
        Returns:
            The agent's response as a string
        """
        agent_executor = self.create_agent(system_prompt)
        result = agent_executor.invoke({"input": prompt})
        return result["output"]


def run_agent(prompt: str) -> str:
    """
    Compatibility function for the evaluation harness.
    
    Args:
        prompt: The task prompt
        
    Returns:
        The agent's response
    """
    agent = LangChainAgent(
        model_name="gpt-4-turbo",
        temperature=0,
        max_tokens=4000,
        verbose=False
    )
    
    system_prompt = """You are a code analysis assistant that specializes in finding bugs and issues in code.
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
    
    return agent.run(prompt, system_prompt)


if __name__ == "__main__":
    # Example usage
    agent = LangChainAgent(
        model_name="gpt-3.5-turbo",
        temperature=0,
        verbose=True
    )
    
    result = agent.run(
        "List the files in the current directory and summarize what they contain."
    )
    
    print(f"Result: {result}")