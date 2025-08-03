# =============================================================================
# 🐙 OCTOPUS SYSTEM UTILITIES
# =============================================================================
"""
Shared utility functions between Octopus Server and Client components.
This module provides common functionality that both applications need.
"""

import os
import time
import json
import logging
import socket
from datetime import datetime
from constants import TaskStatus, Logging

# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def setup_logging(log_file, log_level="INFO", max_size=10*1024*1024, backup_count=5):
    """
    Setup standardized logging for Octopus components.
    
    Args:
        log_file (str): Path to log file
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_size (int): Maximum log file size in bytes
        backup_count (int): Number of backup log files to keep
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=Logging.FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger()

# =============================================================================
# NETWORK UTILITIES
# =============================================================================

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def get_hostname():
    """Get the hostname of this machine."""
    return socket.gethostname()

def get_client_id():
    """Generate a unique client identifier."""
    hostname = get_hostname()
    pid = os.getpid()
    return f"{hostname}_{pid}"

# =============================================================================
# TIME UTILITIES
# =============================================================================

def get_current_timestamp():
    """Get current timestamp as ISO format string."""
    return datetime.now().isoformat()

def format_duration(seconds):
    """Format duration in seconds to human readable format."""
    try:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        elif seconds < 86400:
            return f"{seconds//3600}h {(seconds%3600)//60}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    except:
        return str(seconds)

def is_timestamp_expired(timestamp, timeout_seconds):
    """Check if a timestamp is older than timeout_seconds."""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp = dt.timestamp()
        
        return (time.time() - timestamp) > timeout_seconds
    except:
        return True

# =============================================================================
# DATA UTILITIES
# =============================================================================

def safe_json_loads(json_str, default=None):
    """Safely parse JSON string, return default on error."""
    try:
        return json.loads(json_str) if json_str else default
    except:
        return default

def safe_json_dumps(obj, default="{}"):
    """Safely serialize object to JSON, return default on error."""
    try:
        return json.dumps(obj)
    except:
        return default

def sanitize_string(value, max_length=255):
    """Sanitize string value for database storage."""
    if not value:
        return ""
    
    # Convert to string and strip whitespace
    value = str(value).strip()
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length-3] + "..."
    
    return value

# =============================================================================
# TASK UTILITIES
# =============================================================================

def is_task_completed(task):
    """Check if a task is in a completed state."""
    status = task.get("status", "")
    return TaskStatus.is_completed(status)

def validate_task_data(task):
    """Validate task data structure."""
    required_fields = ["owner", "plugin", "action"]
    
    for field in required_fields:
        if not task.get(field):
            return False, f"Missing required field: {field}"
    
    return True, "Valid"

def extract_task_args(task):
    """Extract and parse task arguments safely."""
    args = safe_json_loads(task.get("args", "[]"), [])
    kwargs = safe_json_loads(task.get("kwargs", "{}"), {})
    
    # Ensure args is a list and kwargs is a dict
    if not isinstance(args, list):
        args = []
    if not isinstance(kwargs, dict):
        kwargs = {}
    
    return args, kwargs

# =============================================================================
# FILE UTILITIES
# =============================================================================

def ensure_directory_exists(directory_path):
    """Ensure a directory exists, create if necessary."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {directory_path}: {e}")
        return False

def get_file_size_mb(file_path):
    """Get file size in megabytes."""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0

def rotate_log_file(log_file, max_size_mb=10, backup_count=5):
    """Rotate log file if it exceeds max size."""
    try:
        if get_file_size_mb(log_file) > max_size_mb:
            # Move existing backups
            for i in range(backup_count - 1, 0, -1):
                old_file = f"{log_file}.{i}"
                new_file = f"{log_file}.{i + 1}"
                if os.path.exists(old_file):
                    os.rename(old_file, new_file)
            
            # Move current log to .1
            if os.path.exists(log_file):
                os.rename(log_file, f"{log_file}.1")
            
            return True
    except Exception as e:
        logging.error(f"Failed to rotate log file {log_file}: {e}")
    
    return False

# =============================================================================
# ERROR HANDLING UTILITIES
# =============================================================================

def log_exception(logger, message, exception=None):
    """Log exception with context."""
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(message, exc_info=True)

def retry_operation(operation, max_retries=3, delay=1, logger=None):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation (callable): Function to retry
        max_retries (int): Maximum number of retry attempts
        delay (float): Initial delay between retries
        logger (logging.Logger): Logger for retry messages
    
    Returns:
        Result of operation or None if all retries failed
    """
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries:
                if logger:
                    logger.error(f"Operation failed after {max_retries} retries: {e}")
                raise
            
            if logger:
                logger.warning(f"Operation attempt {attempt + 1} failed: {e}, retrying in {delay}s")
            
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    
    return None

# =============================================================================
# CONFIGURATION UTILITIES
# =============================================================================

def load_config_from_env(config_dict, prefix="OCTOPUS_"):
    """
    Load configuration values from environment variables.
    
    Args:
        config_dict (dict): Configuration dictionary to update
        prefix (str): Environment variable prefix
    
    Returns:
        dict: Updated configuration dictionary
    """
    updated_config = config_dict.copy()
    
    for key, default_value in config_dict.items():
        env_key = f"{prefix}{key.upper()}"
        env_value = os.environ.get(env_key)
        
        if env_value is not None:
            # Try to convert to same type as default value
            try:
                if isinstance(default_value, bool):
                    updated_config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default_value, int):
                    updated_config[key] = int(env_value)
                elif isinstance(default_value, float):
                    updated_config[key] = float(env_value)
                else:
                    updated_config[key] = env_value
            except ValueError:
                # Keep original value if conversion fails
                pass
    
    return updated_config
