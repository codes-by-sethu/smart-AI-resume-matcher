
## Enhanced `utils.py` :


"""
Utility Functions for Smart Resume-Job Matcher
Author: Professional Development Team
Version: 1.0.0
"""

import json
import numpy as np
import logging
from typing import Dict, List, Any, Union
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to Python native types for JSON serialization.
    
    Args:
        obj: Any Python object that may contain numpy types
        
    Returns:
        Object with numpy types converted to Python native types
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64, np.int8, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.complex64, np.complex128)):
        return complex(obj)
    else:
        return obj


def save_results(results: Dict[str, Any], filename: str, 
                 ensure_ascii: bool = False, indent: int = 2) -> bool:
    """
    Save match results to a JSON file with proper error handling.
    
    Args:
        results: Dictionary containing match results
        filename: Output filename or path
        ensure_ascii: Whether to escape non-ASCII characters
        indent: JSON indentation level
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Add metadata
        results_with_meta = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'application': 'Smart Resume-Job Matcher',
                'version': '1.0.0'
            },
            'results': convert_numpy_types(results)
        }
        
        # Ensure directory exists
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_with_meta, f, indent=indent, 
                     ensure_ascii=ensure_ascii, default=str)
        
        logger.info(f"✅ Results saved successfully to: {filename}")
        return True
        
    except TypeError as e:
        logger.error(f"❌ Type error while saving results: {e}")
        # Try to save with custom JSON encoder
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_with_meta, f, indent=indent,
                         ensure_ascii=ensure_ascii, cls=CustomJSONEncoder)
            logger.info(f"✅ Results saved with custom encoder to: {filename}")
            return True
        except Exception as e2:
            logger.error(f"❌ Failed even with custom encoder: {e2}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to save results to {filename}: {e}")
        return False


def load_results(filename: str) -> Dict[str, Any]:
    """
    Load saved results from a JSON file.
    
    Args:
        filename: Input filename or path
        
    Returns:
        Dict: Loaded results, empty dict if failed
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"✅ Results loaded successfully from: {filename}")
        return data
        
    except FileNotFoundError:
        logger.error(f"❌ Results file not found: {filename}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {filename}: {e}")
        return {}
    except Exception as e:
        logger.error(f"❌ Failed to load results from {filename}: {e}")
        return {}


def validate_file_path(filepath: str, allowed_extensions: List[str] = None) -> bool:
    """
    Validate if a file path exists and has allowed extension.
    
    Args:
        filepath: Path to validate
        allowed_extensions: List of allowed file extensions
        
    Returns:
        bool: True if valid, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.docx', '.txt', '.doc']
    
    path = Path(filepath)
    
    if not path.exists():
        logger.error(f"File does not exist: {filepath}")
        return False
    
    if not path.is_file():
        logger.error(f"Path is not a file: {filepath}")
        return False
    
    if path.suffix.lower() not in allowed_extensions:
        logger.error(f"Unsupported file extension: {path.suffix}. "
                    f"Allowed: {allowed_extensions}")
        return False
    
    return True


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal value as a percentage string.
    
    Args:
        value: Decimal value (0.0 to 1.0)
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"


def calculate_statistics(scores: List[float]) -> Dict[str, float]:
    """
    Calculate statistics for a list of match scores.
    
    Args:
        scores: List of match scores
        
    Returns:
        Dict: Statistics including mean, median, min, max, std
    """
    if not scores:
        return {}
    
    scores_array = np.array(scores)
    
    return {
        'mean': float(np.mean(scores_array)),
        'median': float(np.median(scores_array)),
        'min': float(np.min(scores_array)),
        'max': float(np.max(scores_array)),
        'std': float(np.std(scores_array)),
        'count': len(scores_array)
    }


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle additional data types.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.generic):
            return obj.item()
        else:
            return super().default(obj)


def setup_logging(log_file: str = 'app.log', 
                  level: str = 'INFO',
                  console: bool = True) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Path to log file
        level: Logging level
        console: Whether to log to console
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        handlers.append(console_handler)
    
    handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logger.info(f"✅ Logging configured. Level: {level}, File: {log_file}")