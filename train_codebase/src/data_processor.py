#!/usr/bin/env python3
"""
Data processing utilities.
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Processor for handling data transformations."""
    
    def __init__(self, config=None, logger=None):
        """Initialize the processor with configuration."""
        self.config = config or {}
        # BUG: Logger parameter is unused, should use the passed logger
        self.logger = logging.getLogger(__name__)
        self.transformations = []
    
    def add_transformation(self, transform_func):
        """Add a transformation function to the pipeline."""
        # BUG: Should validate that transform_func is callable
        self.transformations.append(transform_func)
    
    def process_item(self, item):
        """Process a single data item through all transformations."""
        result = item
        # BUG: Should log before transformation, not after
        for transform in self.transformations:
            result = transform(result)
            logger.info(f"Applied transformation {transform.__name__}")
        return result
    
    def process_batch(self, items):
        """Process a batch of items."""
        results = []
        for item in items:
            try:
                results.append(self.process_item(item))
            except Exception as e:
                # BUG: Should raise a custom exception with context, not continue silently
                logger.error(f"Error processing item: {e}")
        return results
    
    def filter_data(self, data, condition):
        """Filter data based on a condition function."""
        # BUG: Doesn't handle case where condition is not callable
        return [item for item in data if condition(item)]

    def serialize(self, data):
        """Serialize data to JSON."""
        # BUG: This will fail for non-serializable objects
        return json.dumps(data)

    def get_statistics(self, data):
        """Get basic statistics about numerical data."""
        if not data:
            return {}
        
        # BUG: Doesn't check if items are numeric
        return {
            "count": len(data),
            "sum": sum(data),
            "average": sum(data) / len(data),
            "min": min(data),
            "max": max(data)
        }