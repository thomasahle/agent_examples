#!/usr/bin/env python3
"""
List manipulation utilities.
"""

def get_last_n_elements(items, n):
    """Return the last n elements from a list."""
    # BUG: Off-by-one error, should use items[-n:] to get last n elements
    return items[-n+1:]

def get_first_n_elements(items, n):
    """Return the first n elements from a list."""
    if n <= 0:
        return []
    # BUG: Should check if n is greater than list length to avoid unnecessary slicing
    return items[:n]

def find_duplicates(items):
    """Find all duplicate items in a list."""
    seen = set()
    # BUG: Logic error - this will find all unique elements, not duplicates
    duplicates = {x for x in items if x not in seen and not seen.add(x)}
    return list(duplicates)

def chunk_list(items, chunk_size):
    """Split a list into chunks of specified size."""
    # BUG: Doesn't handle empty list or negative chunk_size
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def rotate_list(items, positions):
    """Rotate list elements by a given number of positions."""
    if not items:
        return []
    # BUG: Should handle negative positions and use modulo to avoid unnecessary rotations
    positions = positions % len(items)
    return items[positions:] + items[:positions]