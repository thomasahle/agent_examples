#!/usr/bin/env python3
"""
Shell command execution utilities for agent frameworks.

This module provides a unified set of shell operation tools that can be used
across different agent frameworks, including functions for executing shell
commands with proper error handling and security measures.
"""

import os
import subprocess
import shlex
import platform
from typing import Optional, List, Dict, Union, Tuple

def run_shell_command(command: str, timeout: int = 60, shell: bool = True, 
                     capture_output: bool = True, workdir: Optional[str] = None) -> str:
    """
    Run a shell command and return its output.

    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds
        shell: Whether to execute through the shell
        capture_output: Whether to capture and return stdout/stderr
        workdir: Working directory for command execution (None for current directory)

    Returns:
        Command output (stdout, stderr) or error message
    """
    try:
        # Execute the command
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=workdir
        )
        
        # Return output, prioritizing stdout if it exists
        if result.stdout:
            return result.stdout.strip()
        elif result.stderr:
            return result.stderr.strip()
        else:
            return "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}: {e.stderr or str(e)}"
    except Exception as e:
        return f"Error executing command: {e}"

def run_shell_command_interactive(command: str, workdir: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Run a shell command and return detailed execution results.

    Args:
        command: Shell command to execute
        workdir: Working directory for command execution (None for current directory)

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=workdir
        )
        
        stdout, stderr = process.communicate()
        return_code = process.returncode
        
        return (return_code, stdout.strip() if stdout else "", stderr.strip() if stderr else "")
    except Exception as e:
        return (1, "", f"Error executing command: {e}")

def get_system_info() -> Dict[str, str]:
    """
    Get basic system information.

    Returns:
        Dictionary containing system information
    """
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "node": platform.node(),
        "processor": platform.processor()
    }
    
    # Add additional OS-specific information
    if platform.system() == "Linux":
        try:
            info["distribution"] = " ".join(platform.linux_distribution())
        except:
            pass
    
    return info

def safe_run_command(command: str, allowed_commands: Optional[List[str]] = None) -> str:
    """
    Run a shell command with safety checks.

    Args:
        command: Shell command to execute
        allowed_commands: List of allowed command prefixes, e.g. ['ls', 'grep', 'cat']
                         If None, basic safe commands are allowed by default

    Returns:
        Command output or error message
    """
    # Default safe commands if not specified
    if allowed_commands is None:
        allowed_commands = ['ls', 'grep', 'find', 'cat', 'echo', 'pwd', 'dir', 
                           'head', 'tail', 'wc', 'sort', 'uniq', 'diff']
    
    # Parse the command to check if it's allowed
    try:
        command_parts = shlex.split(command)
        base_command = command_parts[0]
        
        # Check if the base command is in the allowed list
        if base_command not in allowed_commands:
            return f"Error: Command '{base_command}' is not allowed. Allowed commands: {', '.join(allowed_commands)}"
        
        # Execute the command if it's allowed
        return run_shell_command(command)
    except Exception as e:
        return f"Error parsing or executing command: {e}"

def run_python_code(code: str) -> str:
    """
    Execute Python code in a controlled environment and return the result.

    Args:
        code: Python code to execute

    Returns:
        Output of the executed code or error message
    """
    # Create a temporary namespace for code execution
    local_vars = {}
    
    try:
        # Execute the code and capture its output
        exec(code, {"__builtins__": __builtins__}, local_vars)
        
        # Return the result variable if it exists
        if "result" in local_vars:
            return str(local_vars["result"])
        else:
            return "Code executed successfully (no result variable defined)"
    except Exception as e:
        return f"Error executing Python code: {e}"