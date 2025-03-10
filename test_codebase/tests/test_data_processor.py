"""
Tests for the DataProcessor module.
"""

import unittest
from src.data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""
    
    def setUp(self):
        self.processor = DataProcessor()
        
    def test_process_sample_data(self):
        """Test processing sample data."""
        data = {"sample": "test"}
        result = self.processor.process(data)
        
        self.assertIn("processed_sample", result)
        self.assertEqual(result["processed_sample"], "PROCESSED: test")
        
    def test_metadata_added(self):
        """Test that metadata is added to the result."""
        data = {"key": "value"}
        result = self.processor.process(data)
        
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["version"], "1.0.0")
        
    # TODO: Add more test cases for edge conditions

if __name__ == "__main__":
    unittest.main()