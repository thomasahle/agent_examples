#!/usr/bin/env python3
"""
Metrics calculation functions for agent evaluations.
Extracted from agent_bug_evaluator.py for reusability.
"""

import re
from typing import List, Dict, Any, Set

def analyze_agent_response(response: str, known_bugs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze an agent's response to determine how many bugs it found.
    
    Args:
        response: The agent's response text
        known_bugs: List of known bugs with file, line, and description
        
    Returns:
        Dict with evaluation metrics
    """
    # Convert all bug descriptions to lowercase for easier matching
    known_bug_descriptions = [bug['description'].lower() for bug in known_bugs]
    found_bugs = []
    
    # List of key phrases that might indicate a bug in the agent's response
    bug_indicators = [
        "bug", "issue", "problem", "error", "incorrect", "wrong", 
        "missing", "should", "improper", "invalid", "fail"
    ]
    
    # First, try to extract numbered bug descriptions (1. Bug description...)
    numbered_bugs = re.findall(r'(?:^|\n)\s*(\d+\.?\s*\*?\*?(?:File:|\*\*File:\*\*)?.*?)(?=\n\s*\d+\.|\Z)', 
                              response, re.DOTALL)
    
    # If that doesn't find enough, look for sections with file and line information
    file_line_sections = re.findall(r'(?:^|\n)(?:File|Line).*?(?:Bug|Issue|Problem).*?(?=\n\n|\Z)', 
                                   response, re.DOTALL | re.IGNORECASE)
    
    # Combine our findings
    paragraphs = numbered_bugs
    
    # If we found file/line sections, add those 
    if file_line_sections:
        paragraphs.extend(file_line_sections)
    
    # If we haven't found enough, look for sections with bold text (markdown)
    if len(paragraphs) < 5:
        bold_sections = re.findall(r'(?:^|\n)\s*\*\*(.*?)\*\*:?(.*?)(?=\n\s*\*\*|\Z)', 
                                 response, re.DOTALL)
        if bold_sections:
            for bold_text, description in bold_sections:
                paragraphs.append(f"{bold_text}: {description}")
    
    # If still not enough, split by blank lines
    if len(paragraphs) < 5:
        paragraphs = re.split(r'\n\s*\n', response)
    
    for paragraph in paragraphs:
        # Clean the paragraph
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if this paragraph describes a bug
        is_bug_paragraph = any(indicator in paragraph.lower() for indicator in bug_indicators)
        
        if is_bug_paragraph or any("# bug:" in p.lower() for p in paragraph.lower().split('\n')):
            found_bug = False
            # Try to match this paragraph to a known bug
            # Extract line number and file references if they exist
            line_match = re.search(r'(?:line|line:|\*\*line\*\*:?)\s*(\d+)', paragraph.lower())
            line_num = int(line_match.group(1)) if line_match else None
            
            file_match = re.search(r'(?:file|file:|\*\*file\*\*:?)\s*[\'"]?([\w./]+\.py)[\'"]?', paragraph.lower())
            file_path = file_match.group(1) if file_match else None
            
            for bug_index, bug in enumerate(known_bugs):
                bug_desc = bug['description'].lower()
                bug_file = bug['file'].lower()
                bug_line = bug['line']
                
                # Check exact line number match if available
                if line_num and line_num == bug_line:
                    # Add extra weight to line number matches
                    found_bugs.append({
                        'known_bug': bug_desc,
                        'agent_description': paragraph.strip(),
                        'bug_index': bug_index,
                        'match_type': 'line_number'
                    })
                    found_bug = True
                    break
                    
                # Check file path match if available
                if file_path and bug_file in file_path:
                    # Extract keywords from the bug description
                    key_words = [w for w in bug_desc.split() if len(w) > 3 and w not in 
                                ['this', 'that', 'should', 'would', 'could', 'will']]
                    
                    # If we have keywords and any match, this is likely the same bug
                    if key_words and any(word in paragraph.lower() for word in key_words):
                        found_bugs.append({
                            'known_bug': bug_desc,
                            'agent_description': paragraph.strip(),
                            'bug_index': bug_index,
                            'match_type': 'file_and_keyword'
                        })
                        found_bug = True
                        break
                
                # Fall back to keyword matching if no file/line match
                key_words = [w for w in bug_desc.split() if len(w) > 3 and w not in 
                            ['this', 'that', 'should', 'would', 'could', 'will']]
                
                # If we have key words and a good number match, consider it a match
                matching_words = [word for word in key_words if word in paragraph.lower()]
                if len(matching_words) >= 2 or (len(matching_words) == 1 and len(key_words) == 1):
                    found_bugs.append({
                        'known_bug': bug_desc,
                        'agent_description': paragraph.strip(),
                        'bug_index': bug_index,
                        'match_type': 'keyword'
                    })
                    found_bug = True
                    break
            
            # If we didn't find a match but this looks like a bug description, log it
            if not found_bug and (len(paragraph) > 20 or "# bug:" in paragraph.lower()):
                found_bugs.append({
                    'known_bug': "UNKNOWN",
                    'agent_description': paragraph.strip(),
                    'bug_index': -1
                })
    
    # Count only matched bugs for recall calculation
    matched_bugs = [b for b in found_bugs if b.get('known_bug') != "UNKNOWN"]
    unique_bugs = set(b.get('bug_index', -1) for b in matched_bugs if b.get('bug_index', -1) >= 0)
    
    return {
        'total_known_bugs': len(known_bugs),
        'bugs_found': len(matched_bugs),
        'unique_bugs_found': len(unique_bugs),
        'found_bug_details': found_bugs,
        'recall': len(unique_bugs) / len(known_bugs) if known_bugs else 0,
        'unmatched_bugs': len([b for b in found_bugs if b.get('known_bug') == "UNKNOWN"])
    }

def calculate_evaluation_metrics(results: Dict[str, Dict[str, Any]], known_bugs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate all agent responses and generate metrics.
    
    Args:
        results: Dictionary mapping agent names to result objects
        known_bugs: List of known bugs with details
        
    Returns:
        Dictionary with metrics for each agent
    """
    evaluation = {}
    
    for agent, result in results.items():
        if result['success']:
            analysis = analyze_agent_response(result['response'], known_bugs)
            evaluation[agent] = analysis
        else:
            evaluation[agent] = {
                'total_known_bugs': len(known_bugs),
                'bugs_found': 0,
                'found_bug_details': [],
                'recall': 0,
                'error': result['stderr']
            }
    
    return evaluation

def get_sorted_evaluation(evaluation: Dict[str, Dict[str, Any]]) -> List[tuple]:
    """
    Sort agents by recall score in descending order.
    
    Args:
        evaluation: Dictionary with evaluation metrics for each agent
        
    Returns:
        List of (agent_name, metrics) tuples sorted by recall score
    """
    return sorted(
        evaluation.items(), 
        key=lambda x: x[1]['recall'], 
        reverse=True
    )