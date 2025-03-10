# Agent Frameworks Evaluation

This repository contains a framework for evaluating different agent-based LLM frameworks on practical tasks like bug finding.

## Overview

The project provides:

1. A standardized evaluation harness for agent frameworks
2. Unified wrappers for multiple agent frameworks:
   - LangChain
   - LlamaIndex
   - Semantic Kernel
   - AutoGen
   - SmolAgents
   - DSPy

3. Common utilities for agents including:
   - File operations
   - Shell commands
   - Evaluation metrics

## Project Structure

```
agent_examples/
├── README.md                # This file
├── requirements.txt         # Dependencies
├── config.py                # Centralized configuration
├── agent_wrappers.py        # Unified agent interface
│
├── eval/                    # Evaluation harness
│   ├── __init__.py
│   ├── metrics.py           # Evaluation metrics
│   └── harness.py           # Main evaluation framework
│
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── common.py            # Common helper functions
│   └── tools/               # Common tool implementations
│       ├── __init__.py
│       ├── file_tools.py    # File operation tools
│       └── shell_tools.py   # Shell command tools
│
├── frameworks/              # Framework implementations
│   ├── __init__.py
│   ├── langchain_agent.py   # LangChain wrapper
│   └── ...                  # Other frameworks
│
└── test_codebase/           # Test codebase with bugs
    ├── README.md
    ├── src/
    ├── tests/
    └── docs/
```

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

3. Run the evaluation:
   ```
   python -m eval.harness --codebase test_codebase
   ```

## Adding a New Agent Framework

To add a new agent framework:

1. Create a new file in the `frameworks/` directory (e.g., `frameworks/new_framework_agent.py`)
2. Implement the required `run_agent(prompt: str) -> str` function
3. Add the framework name to `AVAILABLE_AGENTS` in `config.py`
4. Update the imports in `frameworks/__init__.py`

## Evaluation Tasks

The primary task for evaluation is bug finding, where agents analyze a codebase to find bugs marked with `# BUG:` comments.

### Example:

```python
def calculate_average(numbers):
    total = 0
    for number in numbers:
        total += number
    # BUG: Division by zero when numbers is empty
    return total / len(numbers)
```

## Metrics

The evaluation produces the following metrics for each agent:

- **Recall**: Percentage of known bugs found
- **Bugs Found**: Total number of bugs correctly identified
- **Unmatched Bugs**: Bugs reported by the agent that don't match known bugs

## Visualization

Run the visualization script to generate comparison charts:

```
python visualize_results.py --input agent_evaluation_results.json
```

## License

MIT