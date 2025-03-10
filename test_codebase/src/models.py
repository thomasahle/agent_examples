"""
Data models for the application.
"""

import enum
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

class ProcessingMode(enum.Enum):
    """Enumeration of processing modes."""
    
    STANDARD = "standard"
    BATCH = "batch"
    STREAMING = "streaming"

# BUG: This class is using inheritance incorrectly - no parent class provided
class DataValidationError():
    """Error raised during data validation."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        """Initialize error.
        
        Args:
            message: Error message
            field: Optional field name that has the error
        """
        self.message = message
        self.field = field
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message

@dataclass
class InputData:
    """Input data model."""
    
    # Required fields
    id: str
    
    # Optional fields with defaults
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    
    # BUG: Post-init validation missing but needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "id": self.id,
            "data": self.data,
            "metadata": self.metadata,
        }
        
        if self.timestamp:
            # BUG: Should convert datetime to string but doesn't
            result["timestamp"] = self.timestamp
        
        return result

@dataclass
class OutputData:
    """Output data model."""
    
    # Required fields
    id: str
    processed_data: Dict[str, Any]
    
    # Optional fields with defaults
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "success"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "processed_data": self.processed_data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }

# BUG: These validation schemas should be defined as classes but are dictionaries
VALIDATION_SCHEMAS = {
    "input_data": {
        "id": {"type": "string", "required": True},
        "data": {"type": "object", "required": True},
        "metadata": {"type": "object", "required": False},
        "timestamp": {"type": "string", "required": False},
    },
    "output_data": {
        "id": {"type": "string", "required": True},
        "processed_data": {"type": "object", "required": True},
        "metadata": {"type": "object", "required": False},
        "timestamp": {"type": "string", "required": True},
        "status": {"type": "string", "required": True},
    }
}