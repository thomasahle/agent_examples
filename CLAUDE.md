# Development Guide for Agents Repository

## Commands
- **Run Evaluations**: `./run_bug_evaluations.sh` (requires OPENAI_API_KEY)
- **Run Specific Evaluation**: `python3.12 -m eval.harness --codebase test_codebase --output results.json`
- **Run Single Agent**: `python3.12 -m eval.harness --agent [framework_name] --codebase test_codebase`
- **Scan Only**: `python3.12 -m eval.harness --scan-only --codebase test_codebase`
- **Visualize Results**: `python3.12 ./visualize_results.py --input results.json --output-bar chart.png --output-radar radar.png`
- **Note**: Must use Python 3.12 for all commands

## Code Style Guidelines
- **Python**: Follow PEP 8 conventions for code formatting
- **Imports**: Group imports by standard library, third-party, and local modules with blank line separators
- **Framework Usage**: Follow each framework's idiomatic style (LangChain, LlamaIndex, AutoGen, etc.)
- **Error Handling**: Use try/except with specific exception types; avoid bare except
- **Documentation**: Include docstrings for all functions with parameters and return values
- **Naming**: snake_case for variables/functions, CamelCase for classes
- **Type Hints**: Use type annotations for all function parameters and return values
- **Comments**: Add explanatory comments for complex logic; mark bugs with `# BUG: description`

## Agent Framework Implementation
- Support for multiple frameworks (LangChain, LlamaIndex, AutoGen, Semantic Kernel, SmolAgents, DSPy)
- Implement ReAct paradigm (Reasoning and Acting with tools)
- Standardized wrapper interface in agent_wrappers.py for common evaluation