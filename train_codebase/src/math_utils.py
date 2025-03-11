#!/usr/bin/env python3
"""
Math utility functions for numerical operations.
"""

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    # BUG: Should check if len(numbers) > 0 to avoid division by zero
    return total / len(numbers)

def calculate_median(numbers):
    """Calculate the median of a list of numbers."""
    # BUG: Should handle empty list case
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 0:
        return (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2
    else:
        return sorted_numbers[n // 2]

def calculate_percentage(part, total):
    """Calculate what percentage part is of total."""
    # BUG: Should check for division by zero
    return (part / total) * 100

def factorial(n):
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    # BUG: Inefficient implementation, should use recursion or math.factorial
    for i in range(2, n + 1):
        result *= i
    return result