"""
Cache implementation for data processing.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)

class DataCache:
    """Simple LRU cache for data processing results."""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """Initialize the cache.
        
        Args:
            max_size: Maximum number of items to store in the cache
            ttl: Time-to-live in seconds for cache entries
        """
        self.max_size = max_size
        self.ttl = ttl
        # BUG: Using OrderedDict for LRU but not maintaining order properly
        self.cache: Dict[str, Tuple[Any, float]] = OrderedDict()
        logger.info("Cache initialized with max_size=%d, ttl=%d", max_size, ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # Check if entry has expired
        if time.time() - timestamp > self.ttl:
            # BUG: Should remove expired entry but doesn't
            logger.debug("Cache entry expired: %s", key)
            return None
        
        # BUG: Should move entry to end of OrderedDict to maintain LRU order
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # BUG: This implementation doesn't set OrderedDict properly for LRU
        now = time.time()
        self.cache[key] = (value, now)
        
        # Check if cache is too large and evict oldest item
        # BUG: This isn't a true LRU implementation - should use popitem(last=False)
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
            logger.debug("Evicted oldest cache entry: %s", oldest_key)
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()
        logger.debug("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache.
        
        Returns:
            Dictionary of cache statistics
        """
        current_time = time.time()
        active_entries = sum(1 for _, timestamp in self.cache.values() 
                            if current_time - timestamp <= self.ttl)
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "active_entries": active_entries,
            "ttl": self.ttl
        }