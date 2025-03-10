"""
Data processing module.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor
from .cache import DataCache

logger = logging.getLogger(__name__)

# BUG: Cache singleton is created regardless of whether caching is enabled
data_cache = DataCache(max_size=100)

class ProcessingError(Exception):
    """Exception raised for errors during data processing."""
    pass

class DataProcessor:
    """Process data for the application."""
    
    def __init__(self, mode: str = "standard", max_workers: int = 4):
        """Initialize the data processor.
        
        Args:
            mode: Processing mode (standard, batch, streaming)
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.mode = mode
        self.max_workers = max_workers
        self.use_cache = True  # Default to using cache
        
        # BUG: In streaming mode, transforms are applied in reverse order
        if mode == "streaming":
            self.transforms = [
                self._enrich_data,
                self._transform_data,
                self._clean_data
            ]
        else:
            self.transforms = [
                self._clean_data,
                self._transform_data,
                self._enrich_data
            ]
        
        # Register additional transforms based on mode
        if mode == "batch":
            self.transforms.append(self._batch_postprocess)
        
        # BUG: The _add_timestamps is added to transforms but not defined in the class
        self.transforms.append(self._add_timestamps)
        
        logger.info("DataProcessor initialized with mode: %s", mode)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data through all transforms.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed data dictionary
        """
        logger.info("Processing data: %s", data)
        
        # Check cache first
        if self.use_cache:
            cache_key = self._generate_cache_key(data)
            cached_result = data_cache.get(cache_key)
            if cached_result:
                logger.info("Cache hit for key: %s", cache_key)
                return cached_result
        
        result = data.copy()
        
        # Apply transforms
        for transform in self.transforms:
            try:
                start_time = time.time()
                
                # BUG: Transform names should be logged before execution, not after
                result = transform(result)
                
                end_time = time.time()
                logger.debug(
                    "Transform %s took %.2f seconds",
                    transform.__name__,
                    end_time - start_time
                )
            except Exception as e:
                # TODO: Add better error handling and recovery
                logger.error("Error in transform %s: %s", transform.__name__, str(e))
                # BUG: Should raise a ProcessingError, not continue silently
                
        # Save to cache
        if self.use_cache:
            cache_key = self._generate_cache_key(data)
            data_cache.set(cache_key, result)
        
        return result
    
    def process_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of items, potentially in parallel.
        
        Args:
            items: List of data items to process
            
        Returns:
            List of processed results
        """
        if self.mode == "batch" and len(items) > 1:
            # Process in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = list(executor.map(self.process, items))
            return results
        else:
            # Process sequentially
            return [self.process(item) for item in items]
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a cache key from the input data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Cache key string
        """
        # BUG: This will fail for non-serializable objects
        return json.dumps(data, sort_keys=True)
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the input data by removing null values, etc.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Cleaned data dictionary
        """
        # TODO: Implement data cleaning
        cleaned = {}
        
        # BUG: This will remove empty strings and zero values, which might be valid
        for key, value in data.items():
            if value:
                cleaned[key] = value
        
        return cleaned
    
    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the data for further processing.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Transformed data dictionary
        """
        result = data.copy()
        
        # Process 'sample' field if present
        if 'sample' in result:
            result['processed_sample'] = f"PROCESSED: {result['sample']}"
            
            # BUG: Original sample field is deleted, losing data
            del result['sample']
        
        return result
    
    def _enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich the data with additional information.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Enriched data dictionary
        """
        # TODO: Add data enrichment from external sources
        result = data.copy()
        
        result['metadata'] = {
            'version': '1.0.0',
            'source': 'internal',
            'processed_time': datetime.now().isoformat()
        }
        
        # BUG: metadata should be deep merged if it already exists, not overwritten
        
        return result
    
    def _batch_postprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Additional processing for batch mode.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Postprocessed data dictionary
        """
        result = data.copy()
        
        # Add batch processing flag
        result['batch_processed'] = True
        
        # BUG: batch_id is added but not utilized elsewhere
        result['batch_id'] = f"batch_{int(time.time())}"
        
        return result