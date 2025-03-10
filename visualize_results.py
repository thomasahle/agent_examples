#!/usr/bin/env python3
"""
Visualize the agent evaluation results.

This script creates visualizations from agent evaluation result JSON files,
including bar charts and radar charts for comparing performance metrics.
"""

import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

def load_results(results_file: str) -> Dict[str, Any]:
    """
    Load the evaluation results from a JSON file.
    
    Args:
        results_file: Path to the JSON results file
        
    Returns:
        Dictionary containing the evaluation results
    """
    with open(results_file, 'r') as f:
        return json.load(f)

def create_bar_chart(results: Dict[str, Any], output_file: Optional[str] = None) -> None:
    """
    Create a bar chart of agent recall performance.
    
    Args:
        results: Evaluation results dictionary
        output_file: Path to save the chart (if None, display the chart)
    """
    evaluation = results.get('evaluation', {})
    
    # Sort agents by recall
    sorted_agents = sorted(
        evaluation.items(),
        key=lambda x: x[1].get('recall', 0),
        reverse=True
    )
    
    # Extract agent names and recall values
    agent_names = [agent.replace('_example.py', '').replace('_', ' ').title() 
                  for agent, _ in sorted_agents]
    recall_values = [metrics.get('recall', 0) * 100 for _, metrics in sorted_agents]
    bugs_found = [metrics.get('unique_bugs_found', 0) for _, metrics in sorted_agents]
    total_bugs = evaluation[sorted_agents[0][0]].get('total_known_bugs', 0) if sorted_agents else 0
    
    # Create the bar chart
    plt.figure(figsize=(12, 7))
    bars = plt.bar(agent_names, recall_values, color='steelblue')
    
    # Add a line for average recall
    avg_recall = sum(recall_values) / len(recall_values) if recall_values else 0
    plt.axhline(y=avg_recall, color='red', linestyle='--', 
                label=f'Average: {avg_recall:.1f}%')
    
    # Add data labels on top of each bar
    for bar, recall, bugs in zip(bars, recall_values, bugs_found):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f'{recall:.1f}% ({bugs}/{total_bugs})',
            ha='center',
            fontweight='bold'
        )
    
    # Add chart details
    plt.title('Agent Framework Bug Finding Performance', fontsize=16)
    plt.ylabel('Recall (%)', fontsize=14)
    plt.xlabel('Agent Framework', fontsize=14)
    plt.ylim(0, max(recall_values) * 1.2 if recall_values else 100)  # Add space for labels
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    # Save or show the chart
    if output_file:
        plt.savefig(output_file)
        print(f"Bar chart saved to {output_file}")
    else:
        plt.show()

def create_radar_chart(results: Dict[str, Any], output_file: Optional[str] = None) -> None:
    """
    Create a radar chart comparing different metrics across agent frameworks.
    
    Args:
        results: Evaluation results dictionary
        output_file: Path to save the chart (if None, display the chart)
    """
    evaluation = results.get('evaluation', {})
    
    # Prepare data for radar chart
    agent_names = []
    metrics_data = []
    
    for agent, metrics in evaluation.items():
        # Skip agents with errors
        if 'error' in metrics:
            continue
            
        agent_names.append(agent.replace('_example.py', '').replace('_', ' ').title())
        
        # Gather various metrics (normalize to 0-1 scale)
        agent_metrics = {
            'Recall': metrics.get('recall', 0),
            'Bug Accuracy': metrics.get('bugs_found', 0) / 
                           (metrics.get('bugs_found', 0) + metrics.get('unmatched_bugs', 0)) 
                           if (metrics.get('bugs_found', 0) + metrics.get('unmatched_bugs', 0)) > 0 else 0,
            'Line Match': metrics.get('line_match_rate', 0) if 'line_match_rate' in metrics else 0.5,
            'File Match': metrics.get('file_match_rate', 0) if 'file_match_rate' in metrics else 0.5,
            'Detail Score': metrics.get('detail_score', 0) if 'detail_score' in metrics else 0.5
        }
        metrics_data.append(agent_metrics)
    
    # Skip if no valid data
    if not agent_names or not metrics_data:
        print("No valid data for radar chart")
        return
    
    # Set up the radar chart
    categories = list(metrics_data[0].keys())
    N = len(categories)
    
    # Create angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Draw each agent
    for i, (name, metrics) in enumerate(zip(agent_names, metrics_data)):
        values = [metrics[cat] for cat in categories]
        values += values[:1]  # Close the loop
        
        # Plot values
        ax.plot(angles, values, linewidth=2, label=name)
        ax.fill(angles, values, alpha=0.1)
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # Add legend and title
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('Agent Framework Performance Comparison', size=16)
    
    # Save or show the chart
    if output_file:
        plt.savefig(output_file)
        print(f"Radar chart saved to {output_file}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Visualize agent evaluation results')
    parser.add_argument('--input', default='agent_evaluation_results.json',
                        help='Input JSON file with evaluation results')
    parser.add_argument('--output-bar', default='agent_comparison_bar.png',
                        help='Output file for the bar chart')
    parser.add_argument('--output-radar', default='agent_comparison_radar.png',
                        help='Output file for the radar chart')
    parser.add_argument('--show', action='store_true',
                        help='Show the charts instead of saving them')
    args = parser.parse_args()
    
    # Load the results
    results = load_results(args.input)
    
    # Create the visualizations
    if args.show:
        create_bar_chart(results)
        create_radar_chart(results)
    else:
        create_bar_chart(results, args.output_bar)
        create_radar_chart(results, args.output_radar)

if __name__ == "__main__":
    main()