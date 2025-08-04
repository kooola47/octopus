# =============================================================================
# 🐙 OCTOPUS SHARED UTILITIES
# =============================================================================
"""
Shared utility functions between Octopus Server and Client components.
This file contains common functions that need to be consistent across
both server and client applications.
"""

import json
import logging
import socket
import time
import datetime
import os
import sys
from typing import Any, Dict, Optional, Union

from constants import TaskStatus, Validation

# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def setup_logging(log_file: str, log_level: str = "INFO", console_output: bool = True):
    """
    Set up logging configuration for the application.
    
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
            logging.StreamHandler(sys.stdout) if console_output else logging.NullHandler()
        ]
    )

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

def is_timestamp_expired(timestamp: str, timeout: int) -> bool:
    """
    Check if a timestamp has expired based on timeout.
    
    Args:
        timestamp: ISO format timestamp string
        timeout: Timeout in seconds
        
    Returns:
        True if timestamp is expired, False otherwise
    """
    try:
        ts = datetime.datetime.fromisoformat(timestamp)
        now = datetime.datetime.now()
        return (now - ts).total_seconds() > timeout
    except Exception:
        return True

def parse_timestamp(timestamp: Union[str, float, int]) -> datetime.datetime:
    """
    Parse various timestamp formats into datetime object.
    
    Args:
        timestamp: Timestamp in various formats
        
    Returns:
        datetime object
    """
    if isinstance(timestamp, str):
        try:
            return datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            # Try parsing as float
            return datetime.datetime.fromtimestamp(float(timestamp))
    elif isinstance(timestamp, (int, float)):
        return datetime.datetime.fromtimestamp(timestamp)
    else:
        return datetime.datetime.now()

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
        else:
            dt = parse_timestamp(timestamp)
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

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize string for database storage.
    
    Args:
        text: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    # Remove null bytes and control characters
    text = text.replace('\x00', '').replace('\r', '').replace('\n', ' ')
    
    return text.strip()

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
# VALIDATION UTILITIES
# =============================================================================

def validate_task_data(task: Dict[str, Any]) -> tuple:
    """
    Validate task data structure.
    
    Args:
        task: Task dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    for field in Validation.REQUIRED_TASK_FIELDS:
        if field not in task or not task[field]:
            return False, f"Missing required field: {field}"
    
    # Validate field lengths
    if len(task.get('plugin', '')) > Validation.MAX_PLUGIN_NAME_LENGTH:
        return False, f"Plugin name too long (max {Validation.MAX_PLUGIN_NAME_LENGTH} chars)"
    
    if len(task.get('action', '')) > Validation.MAX_ACTION_NAME_LENGTH:
        return False, f"Action name too long (max {Validation.MAX_ACTION_NAME_LENGTH} chars)"
    
    # Validate JSON fields
    if not safe_json_loads(task.get('args', '[]')):
        return False, "Invalid args JSON format"
    
    if not safe_json_loads(task.get('kwargs', '{}')):
        return False, "Invalid kwargs JSON format"
    
    return True, ""

def validate_execution_data(execution: Dict[str, Any]) -> tuple:
    """
    Validate execution data structure.
    
    Args:
        execution: Execution dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    for field in Validation.REQUIRED_EXECUTION_FIELDS:
        if field not in execution or execution[field] is None:
            return False, f"Missing required field: {field}"
    
    # Validate status
    status = execution.get('status')
    if status and not is_valid_task_status(status):
        return False, f"Invalid status: {status}"
    
    return True, ""

def is_valid_task_status(status: str) -> bool:
    """Check if status is valid."""
    return status in TaskStatus.all_statuses()

def is_task_completed(status: str) -> bool:
    """Check if a status indicates task completion."""
    return TaskStatus.is_completed(status)

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

def safe_file_write(file_path: str, content: str, encoding: str = 'utf-8'):
    """
    Safely write content to file.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
    """
    ensure_directory_exists(file_path)
    
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logging.error(f"Failed to write file {file_path}: {e}")
        return False

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

def debug_execution(execution: Dict[str, Any], prefix: str = "EXECUTION") -> str:
    """
    Generate debug string for execution object.
    
    Args:
        execution: Execution dictionary
        prefix: Debug prefix
        
    Returns:
        Debug string
    """
    return f"{prefix}: ID={execution.get('id')}, TaskID={execution.get('task_id')}, " \
           f"Client={execution.get('client')}, Status={execution.get('status')}, " \
           f"Updated={execution.get('updated_at')}"

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

def get_config_value(config_dict: Dict[str, Any], key: str, env_key: Optional[str] = None, 
                    default: Any = None, var_type: type = str) -> Any:
    """
    Get configuration value from dict or environment variable.
    
    Args:
        config_dict: Configuration dictionary
        key: Configuration key
        env_key: Environment variable key (defaults to key.upper())
        default: Default value
        var_type: Type to convert to
        
    Returns:
        Configuration value
    """
    # Try environment variable first
    if env_key is None:
        env_key = key.upper()
    
    env_value = get_env_var(env_key, None, var_type)
    if env_value is not None:
        return env_value
    
    # Fall back to config dict
    return config_dict.get(key, default)
