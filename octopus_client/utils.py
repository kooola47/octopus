# =============================================================================
# 🐙 OCTOPUS CLIENT UTILITIES
# =============================================================================
"""
Client-specific utility functions for the Octopus orchestration system.
"""

import json
import logging
import socket
import os
import datetime
import time
from typing import Any, Dict, Union

# =============================================================================
# NETWORK UTILITIES
# =============================================================================

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def get_hostname():
    """Get the hostname of the machine."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"

def get_client_id():
    """Generate a unique client identifier."""
    hostname = get_hostname()
    pid = os.getpid()
    return f"{hostname}_{pid}"

def get_client_info():
    """Get comprehensive client information."""
    return {
        "hostname": get_hostname(),
        "ip": get_local_ip(),
        "pid": os.getpid(),
        "client_id": get_client_id()
    }

# =============================================================================
# TIME UTILITIES
# =============================================================================

def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.datetime.now().isoformat()

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_timestamp(timestamp: Union[str, float, int, datetime.datetime]) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Timestamp in various formats
        
    Returns:
        Formatted timestamp string
    """
    try:
        if isinstance(timestamp, datetime.datetime):
            dt = timestamp
        elif isinstance(timestamp, str):
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, (int, float)):
            dt = datetime.datetime.fromtimestamp(timestamp)
        else:
            dt = datetime.datetime.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(timestamp)

# =============================================================================
# DATA UTILITIES
# =============================================================================

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with default fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    if not json_str:
        return default
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON string.
    
    Args:
        obj: Object to serialize
        default: Default JSON string if serialization fails
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def extract_task_args(task: Dict[str, Any]) -> tuple:
    """
    Extract and parse task arguments.
    
    Args:
        task: Task dictionary
        
    Returns:
        Tuple of (args_list, kwargs_dict)
    """
    args = safe_json_loads(task.get('args', '[]'), [])
    kwargs = safe_json_loads(task.get('kwargs', '{}'), {})
    
    # Ensure args is a list
    if not isinstance(args, list):
        args = [args] if args else []
    
    # Ensure kwargs is a dict
    if not isinstance(kwargs, dict):
        kwargs = {}
    
    return args, kwargs

# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def setup_logging(log_file: str, log_level: str = "INFO", console_output: bool = True):
    """
    Set up logging configuration for the client.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to also output to console
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() if console_output else logging.NullHandler()
        ]
    )

# =============================================================================
# FILE UTILITIES
# =============================================================================

def ensure_directory_exists(file_path: str):
    """
    Ensure the directory for a file path exists.
    
    Args:
        file_path: Path to file
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def safe_file_read(file_path: str, encoding: str = 'utf-8', default: str = '') -> str:
    """
    Safely read content from file.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        default: Default content if read fails
        
    Returns:
        File content or default
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logging.warning(f"Failed to read file {file_path}: {e}")
        return default

# =============================================================================
# ENVIRONMENT UTILITIES
# =============================================================================

def get_env_var(key: str, default: Any = None, var_type: type = str) -> Any:
    """
    Get environment variable with type conversion.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        var_type: Type to convert to (str, int, float, bool)
        
    Returns:
        Environment variable value with proper type
    """
    value = os.environ.get(key)
    
    if value is None:
        return default
    
    try:
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        else:
            return str(value)
    except (ValueError, TypeError):
        return default

# =============================================================================
# DEBUGGING UTILITIES
# =============================================================================

def debug_task(task: Dict[str, Any], prefix: str = "TASK") -> str:
    """
    Generate debug string for task object.
    
    Args:
        task: Task dictionary
        prefix: Debug prefix
        
    Returns:
        Debug string
    """
    return f"{prefix}: ID={task.get('id')}, Owner={task.get('owner')}, " \
           f"Plugin={task.get('plugin')}, Action={task.get('action')}, " \
           f"Status={task.get('status')}, Type={task.get('type')}"

def debug_execution_result(result: Dict[str, Any], prefix: str = "RESULT") -> str:
    """
    Generate debug string for execution result.
    
    Args:
        result: Execution result dictionary
        prefix: Debug prefix
        
    Returns:
        Debug string
    """
    return f"{prefix}: Status={result.get('status')}, " \
           f"Message={result.get('message', 'N/A')[:50]}..."
