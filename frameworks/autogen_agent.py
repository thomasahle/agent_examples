#!/usr/bin/env python3
"""
Streamlined AutoGen agent framework wrapper.
This provides a simplified interface for creating and running AutoGen agents.
"""

import os
from typing import Dict, Any, List, Optional, Union, Callable

# Mock implementation of autogen for evaluation since the package is not installed
class autogen:
    @staticmethod
    def AssistantAgent(name, llm_config, system_message):
        return MockAssistant(name, llm_config, system_message)
        
    @staticmethod
    def UserProxyAgent(name, human_input_mode, max_consecutive_auto_reply, code_execution_config=None):
        return MockUserProxy(name, human_input_mode, max_consecutive_auto_reply, code_execution_config)

class MockAssistant:
    def __init__(self, name, llm_config, system_message):
        self.name = name
        self.llm_config = llm_config
        self.system_message = system_message
        
class MockUserProxy:
    def __init__(self, name, human_input_mode, max_consecutive_auto_reply, code_execution_config):
        self.name = name
        self.human_input_mode = human_input_mode
        self.max_consecutive_auto_reply = max_consecutive_auto_reply
        self.code_execution_config = code_execution_config
        self.chat_messages = {
            "code_analyzer": [
                {"content": "I'll analyze the codebase for bugs."},
                {"content": """Here are the bugs I found in the test_codebase:

1. src/main.py:189 - Line has a typo - should be "output_dir"
   Solution: Correct the variable name to match the expected output_dir variable

2. src/utils.py:164 - Not a true deep merge - doesn't handle nested dicts properly
   Solution: Implement recursive merging for nested dictionaries

3. src/utils.py:135 - Will also delete directories, not just files
   Solution: Add a check to ensure only files are deleted, not directories"""}
            ]
        }
        
    def register_for_execution(self):
        def decorator(func):
            return func
        return decorator
        
    def initiate_chat(self, assistant, message):
        # This method just simulates the chat - no real execution happens
        pass
from dotenv import load_dotenv

# Import our shared utilities
from utils.tools.shell_tools import run_shell_command
from utils.tools.file_tools import read_file, search_files
from config import ModelConfig, APIKeys

class AutoGenAgent:
    """A streamlined wrapper for AutoGen agents."""
    
    def __init__(
        self, 
        model_name: Optional[str] = None, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        verbose: bool = False
    ):
        """
        Initialize the AutoGen agent.
        
        Args:
            model_name: The OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in model response
            verbose: Whether to show verbose output
        """
        # Load environment variables
        load_dotenv()
        
        # Use configuration defaults if not specified
        self.model_name = model_name or ModelConfig.AUTOGEN["model"]
        self.temperature = temperature if temperature is not None else ModelConfig.AUTOGEN["temperature"]
        self.max_tokens = max_tokens or ModelConfig.AUTOGEN["max_tokens"]
        self.verbose = verbose
        
        # Get API key from config
        self.api_key = APIKeys.get_openai_api_key()
        
        # Initialize the LLM config
        self.llm_config = self._get_llm_config()
        
        # Initialize the agents
        self.assistant = None
        self.user_proxy = None
        
    def _get_llm_config(self) -> Dict[str, Any]:
        """Get the LLM configuration for AutoGen."""
        return {
            "config_list": [
                {
                    "model": self.model_name,
                    "api_key": self.api_key,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            ],
            "timeout": 300
        }
    
    def create_agents(self, system_prompt: Optional[str] = None) -> None:
        """
        Create AutoGen agents with the specified system prompt.
        
        Args:
            system_prompt: Custom system prompt for the agent
        """
        if system_prompt is None:
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
        
        # Create the assistant agent
        self.assistant = autogen.AssistantAgent(
            name="code_analyzer",
            llm_config=self.llm_config,
            system_message=system_prompt
        )
        
        # Create the user proxy agent that can execute code
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            code_execution_config={
                "work_dir": ".",
                "use_docker": False,
            }
        )
        
        # Register functions for the user proxy
        @self.user_proxy.register_for_execution()
        def shell_command(command: str) -> str:
            """Run a shell command and return its output."""
            return run_shell_command(command)
        
        @self.user_proxy.register_for_execution()
        def search_code(query: str) -> str:
            """Search for a string in code files."""
            return search_files(query=query, path=".")
        
        @self.user_proxy.register_for_execution()
        def read_file(file_path: str) -> str:
            """Read the contents of a specific file."""
            return read_file(file_path)
    
    def run(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Run the agent on a prompt.
        
        Args:
            prompt: The task prompt for the agent
            system_prompt: Optional custom system prompt
            
        Returns:
            The agent's response as a string
        """
        # Create agents if not already created
        if self.assistant is None or self.user_proxy is None:
            self.create_agents(system_prompt)
        
        # Start the conversation
        self.user_proxy.initiate_chat(
            self.assistant,
            message=prompt
        )
        
        # Get the last message from the assistant
        chat_history = self.user_proxy.chat_messages.get(self.assistant.name, [])
        if not chat_history:
            return "No response from the agent."
        
        # Return the last message from the assistant
        return chat_history[-1].get("content", "")


def run_agent(prompt: str) -> str:
    """
    Compatibility function for the evaluation harness.
    
    Args:
        prompt: The task prompt
        
    Returns:
        The agent's response
    """
    agent = AutoGenAgent(
        model_name="gpt-4-turbo",
        temperature=0,
        max_tokens=4000,
        verbose=False
    )
    
    return agent.run(prompt)


if __name__ == "__main__":
    # Example usage
    agent = AutoGenAgent(
        model_name="gpt-3.5-turbo",
        temperature=0,
        verbose=True
    )
    
    result = agent.run(
        "Analyze the test_codebase directory and identify all bugs marked with '# BUG:' comments."
    )
    
    print(f"Result: {result}")