#!/usr/bin/env python3
"""
Evaluation harness for agent frameworks.
Streamlined version of the main evaluation harness that works with the new framework structure.
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

from . import metrics

# Default configuration
DEFAULT_CODEBASE_PATH = Path("test_codebase")
DEFAULT_BUG_PATTERN = r"# BUG:\s*(.*)"
DEFAULT_OUTPUT_FILE = "agent_evaluation_results.json"

class EvaluationHarness:
    """Main evaluation harness for testing agent frameworks."""
    
    def __init__(
        self, 
        codebase_path: Path = DEFAULT_CODEBASE_PATH,
        agents: Optional[List[str]] = None,
        bug_pattern: str = DEFAULT_BUG_PATTERN,
        output_file: str = DEFAULT_OUTPUT_FILE
    ):
        """
        Initialize the evaluation harness.
        
        Args:
            codebase_path: Path to the codebase to scan for bugs
            agents: List of agent framework script names to test
            bug_pattern: Regular expression to match bug comments
            output_file: Path to save results
        """
        self.codebase_path = Path(codebase_path)
        self.bug_pattern = bug_pattern
        self.output_file = output_file
        self.bugs = []
        self.results = {}
        
        # Default agents if not provided
        self.agents = agents or [
            "langchain_example.py",
            "llamaindex_example.py",
            "semantic_kernel_example.py",
            "autogen_example.py", 
            "smolagents_example.py",
            "dspy_react_example.py"
        ]
    
    def scan_for_bugs(self) -> List[Dict[str, Any]]:
        """
        Scan the codebase for all bugs marked with the bug pattern.
        
        Returns:
            List of bug dictionaries with file, line and description
        """
        print(f"Scanning codebase for bugs in {self.codebase_path}...")
        
        for root, _, files in os.walk(self.codebase_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self._extract_bugs_from_file(file_path)
        
        print(f"Found {len(self.bugs)} bugs in the codebase.")
        return self.bugs
    
    def _extract_bugs_from_file(self, file_path: Path) -> None:
        """
        Extract all bugs from a single file.
        
        Args:
            file_path: Path to the file to scan
        """
        rel_path = file_path.relative_to(self.codebase_path)
        
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                match = re.search(self.bug_pattern, line)
                if match:
                    bug_desc = match.group(1).strip()
                    self.bugs.append({
                        'file': str(rel_path),
                        'line': i,
                        'description': bug_desc
                    })
    
    def run_agent(self, agent_script: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a single agent framework on the bug finding task.
        
        Args:
            agent_script: Name of the agent script to run
            prompt: Custom prompt to use (if None, use default)
            
        Returns:
            Dictionary with agent results
        """
        if not prompt:
            prompt = ("Analyze the test_codebase directory and identify all bugs marked with "
                    "'# BUG:' comments. For each bug, explain what the issue is and suggest a solution.")
        
        print(f"\nRunning agent: {agent_script}")
        
        try:
            # Import the wrapper function
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from agent_wrappers import run_agent
            
            # Run the agent with the prompt
            print(f"  Running agent with wrapper...")
            response = run_agent(agent_script, prompt)
            
            # Return the response
            print(f"  Agent completed successfully.")
            
            return {
                'agent': agent_script,
                'success': True,
                'response': response,
                'stderr': None
            }
            
        except TimeoutError:
            print(f"  Error: {agent_script} timed out")
            return {
                'agent': agent_script,
                'success': False,
                'response': "Timeout - agent took too long to respond",
                'stderr': "Process timed out"
            }
        except Exception as e:
            print(f"  Error running {agent_script}: {str(e)}")
            return {
                'agent': agent_script,
                'success': False,
                'response': "Error running agent",
                'stderr': str(e)
            }
    
    def run_all_agents(self, custom_prompt: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run all agents and collect their responses.
        
        Args:
            custom_prompt: Custom prompt to use for all agents
            
        Returns:
            Dictionary mapping agent names to result objects
        """
        for agent in self.agents:
            result = self.run_agent(agent, custom_prompt)
            self.results[agent] = result
        
        return self.results
    
    def evaluate_all_responses(self) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all agent responses and generate metrics.
        
        Returns:
            Dictionary with evaluation metrics for each agent
        """
        return metrics.calculate_evaluation_metrics(self.results, self.bugs)
    
    def save_results(self, filename: Optional[str] = None) -> None:
        """
        Save the full evaluation results to a file.
        
        Args:
            filename: Path to save results (if None, use default)
        """
        output = {
            'known_bugs': self.bugs,
            'agent_results': self.results,
            'evaluation': self.evaluate_all_responses()
        }
        
        output_path = filename or self.output_file
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {output_path}")
    
    def print_summary(self) -> None:
        """Print a summary of the evaluation results."""
        evaluation = self.evaluate_all_responses()
        sorted_agents = metrics.get_sorted_evaluation(evaluation)
        
        print("\n=== AGENT EVALUATION SUMMARY ===")
        print(f"Total bugs in codebase: {len(self.bugs)}")
        print("\nPerformance by agent:")
        
        for agent, results in sorted_agents:
            print(f"\n{agent}:")
            print(f"  Unique bugs found: {results.get('unique_bugs_found', 0)} / {results['total_known_bugs']}")
            print(f"  Recall: {results['recall']:.2%}")
            print(f"  Total matched bugs: {results.get('bugs_found', 0)}")
            print(f"  Unmatched bugs: {results.get('unmatched_bugs', 0)}")
            if 'error' in results:
                print(f"  Error: {results['error']}")

def main():
    """Command-line entry point for the evaluation harness."""
    parser = argparse.ArgumentParser(description='Evaluate agent frameworks on bug finding')
    parser.add_argument('--agent', help='Run only a specific agent')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for bugs, don\'t run agents')
    parser.add_argument('--api-key', help='OpenAI API key to use for the agents')
    parser.add_argument('--codebase', default=str(DEFAULT_CODEBASE_PATH), help='Path to codebase to analyze')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_FILE, help='Path to save results')
    args = parser.parse_args()
    
    # Check for API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.scan_only:
        print("Error: No OpenAI API key provided. Please provide one with --api-key or set the OPENAI_API_KEY environment variable.")
        return
    
    # Set API key in environment if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Initialize evaluator
    evaluator = EvaluationHarness(
        codebase_path=Path(args.codebase),
        output_file=args.output
    )
    
    # Scan for bugs
    evaluator.scan_for_bugs()
    
    # If scan only, print bugs and exit
    if args.scan_only:
        for i, bug in enumerate(evaluator.bugs, 1):
            print(f"{i}. {bug['file']} (line {bug['line']}): {bug['description']}")
        return
    
    # Run agents
    if args.agent:
        if args.agent not in evaluator.agents:
            print(f"Error: Unknown agent '{args.agent}'. Available agents: {', '.join(evaluator.agents)}")
            return
        
        result = evaluator.run_agent(args.agent)
        evaluator.results[args.agent] = result
    else:
        evaluator.run_all_agents()
    
    # Evaluate and save results
    evaluator.save_results()
    evaluator.print_summary()

if __name__ == "__main__":
    main()