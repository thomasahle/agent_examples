# Training Codebase

This directory contains a training codebase with intentional bugs for training agent models. The bugs are marked with `# BUG:` comments and cover various common programming mistakes.

## Structure

- `src/` - Source code containing Python modules with bugs
  - `math_utils.py` - Mathematical utility functions (division by zero, inefficient implementations)
  - `list_utils.py` - List manipulation utilities (off-by-one errors, logic bugs)
  - `file_handler.py` - File I/O operations (resource leaks, error handling)
  - `data_processor.py` - Data processing utilities (logging errors, validation issues)
  - `api_client.py` - API client for making HTTP requests (error handling, validation)

## Bug Types

The codebase includes common bug patterns:

1. **Division by Zero**: Functions that don't check for zero before division
2. **Off-by-One Errors**: Incorrect indexing in list operations
3. **Resource Leaks**: Files not properly closed
4. **Error Handling Issues**: Exceptions not properly caught or raised
5. **Parameter Validation**: Input parameters not validated
6. **Logic Errors**: Implementation that doesn't match the intended behavior
7. **Inefficient Implementations**: Code that works but could be improved

## Usage

This codebase is designed for training LLM agents to find and fix bugs. It provides examples of real-world bugs for compilation-based training.

To use:

1. Let the agent analyze this codebase to learn bug patterns
2. Use program compilation techniques to train the agent
3. Apply the trained agent to the test codebase to find similar bugs

## Note

Do not use this code in production as it contains intentional bugs for educational purposes.