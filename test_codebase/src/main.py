"""
Main application entry point.
"""

# TODO: Add proper logging configuration
import logging
import os
import sys
import json
import argparse
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from .utils import load_config, format_output, validate_input, save_results
from .data_processor import DataProcessor
from .models import InputData, OutputData, ProcessingMode

logger = logging.getLogger(__name__)

# BUG: This global variable creates side effects across multiple calls
processing_stats = {
    "processed_count": 0,
    "error_count": 0,
    "last_run": None
}

def initialize_app(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Initialize the application components.
    
    Args:
        config_path: Optional path to the config file
        
    Returns:
        Configuration dictionary
    """
    config = load_config(config_path)
    
    # TODO: Add error handling for missing configuration
    if not config:
        # Default configuration if none provided
        config = {
            "processing_mode": "standard",
            "max_items": 100,
            "output_dir": "./output"
        }
    
    # BUG: This doesn't create output directory if it doesn't exist
    # output_dir = config.get("output_dir", "./output")
    # os.makedirs(output_dir, exist_ok=True)
    
    # Configure logging based on config
    log_level = config.get("log_level", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info("Application initialized with config: %s", config)
    return config

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Data Processing Application")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--input", help="Input data file (JSON)")
    parser.add_argument("--mode", choices=["standard", "batch", "streaming"], 
                       help="Processing mode")
    parser.add_argument("--output-dir", help="Output directory")
    
    return parser.parse_args()

def load_input_data(input_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load input data from a file or use default.
    
    Args:
        input_path: Path to input data file
        
    Returns:
        List of input data items
    """
    if input_path and os.path.exists(input_path):
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
                # BUG: Doesn't validate that the input is a list
                return data
        except json.JSONDecodeError:
            logger.error("Invalid JSON in input file")
            return [{"sample": "default_data"}]
    else:
        # Default test data
        return [{"sample": "default_data"}]

def process_data(
    input_data: Dict[str, Any], 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Process the input data using the DataProcessor.
    
    Args:
        input_data: The data to process
        config: Application configuration
        
    Returns:
        Processed data as a dictionary
    """
    # BUG: This validation schema is never defined
    schema = config.get("validation_schema", {})
    validation_errors = validate_input(input_data, schema)
    
    if validation_errors:
        # BUG: This logger reference uses an incorrect format string
        logger.warning("Validation errors: %d", validation_errors)
        processing_stats["error_count"] += 1
    
    # Get processing mode from config
    mode = config.get("processing_mode", "standard")
    
    processor = DataProcessor(mode=mode)
    result = processor.process(input_data)
    
    # Update processing stats
    processing_stats["processed_count"] += 1
    processing_stats["last_run"] = datetime.now().isoformat()
    
    # BUG: This will add stats to every result, creating duplicated data
    result["processing_stats"] = processing_stats
    
    return format_output(result)

def process_batch(
    items: List[Dict[str, Any]], 
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Process a batch of items.
    
    Args:
        items: List of data items to process
        config: Application configuration
        
    Returns:
        List of processed results
    """
    results = []
    max_items = config.get("max_items", 100)
    
    # BUG: This incorrectly limits the number of items - should use min()
    items_to_process = items[:max_items]
    
    for item in items_to_process:
        try:
            result = process_data(item, config)
            results.append(result)
        except Exception as e:
            logger.error("Error processing item: %s", str(e))
            processing_stats["error_count"] += 1
    
    return results

def main() -> int:
    """Main application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Initialize the application
        config = initialize_app(args.config)
        
        # Override config with command line arguments
        if args.mode:
            config["processing_mode"] = args.mode
        if args.output_dir:
            config["output_dir"] = args.output_dir
        
        # Load input data
        input_items = load_input_data(args.input)
        
        # Process the data
        results = process_batch(input_items, config)
        
        # Save results
        # BUG: This line has a typo - should be "output_dir"
        output_path = os.path.join(config.get("output_dir", "./output"), "results.json")
        save_results(results, output_path)
        
        print(f"Processing complete. Processed {len(results)} items.")
        print(f"Results saved to {output_path}")
        
        return 0
    except Exception as e:
        logger.error("Error in main: %s", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())