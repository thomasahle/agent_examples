#!/usr/bin/env python3
"""
File handling utilities.
"""

import os
import json
import csv

def read_config(filename):
    """Read configuration from a file."""
    # BUG: Resource leak - file is not properly closed
    f = open(filename, 'r')
    content = f.read()
    return content

def write_data(data, filename):
    """Write data to a file."""
    # BUG: Should use with statement to ensure file is closed
    f = open(filename, 'w')
    f.write(data)
    f.close()

def append_to_log(log_file, message):
    """Append a message to a log file."""
    # BUG: Should create directory if it doesn't exist
    with open(log_file, 'a') as f:
        f.write(message + '\n')

def read_json_file(filename):
    """Read and parse a JSON file."""
    # BUG: No error handling for JSON parsing errors
    with open(filename, 'r') as f:
        return json.load(f)

def read_csv_file(filename):
    """Read a CSV file and return rows as dictionaries."""
    rows = []
    # BUG: Doesn't handle CSV format errors or encoding issues
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows