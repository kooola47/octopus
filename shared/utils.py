#!/usr/bin/env python3
"""
🐙 OCTOPUS SHARED - Common Utilities
====================================

Shared utility functions that can be used by both client and server.
These functions should be pure functions without dependencies on specific implementations.
"""

import json
import datetime
import time
import socket
import os
import hashlib
from typing import Any, Dict, Union, List, Optional

# =============================================================================
# TIME UTILITIES
# =============================================================================

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.datetime.now().isoformat()

def get_current_unix_timestamp() -> float:
    """Get current Unix timestamp."""
    return time.time()

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
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

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

def is_timestamp_recent(timestamp: Union[str, float, int], max_age_seconds: int = 30) -> bool:
    """Check if timestamp is within max_age_seconds from now"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp = dt.timestamp()
        elif isinstance(timestamp, datetime.datetime):
            timestamp = timestamp.timestamp()
        
        return (time.time() - timestamp) <= max_age_seconds
    except Exception:
        return False

# =============================================================================
# JSON UTILITIES
# =============================================================================

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string, returning default on error."""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely serialize object to JSON string, returning default on error."""
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    except (TypeError, ValueError):
        return default

def validate_json_structure(json_str: str, required_keys: List[str] = None) -> bool:
    """Validate JSON string has required structure."""
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            return False
        
        if required_keys:
            for key in required_keys:
                if key not in data:
                    return False
        
        return True
    except (json.JSONDecodeError, TypeError):
        return False

# =============================================================================
# STRING UTILITIES
# =============================================================================

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize and truncate string for safe storage/display."""
    if not text:
        return ""
    
    text = str(text).strip()
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text

def normalize_identifier(name: str) -> str:
    """Normalize string to be used as identifier (lowercase, underscores)."""
    if not name:
        return ""
    
    # Convert to lowercase and replace spaces/special chars with underscores
    normalized = "".join(c if c.isalnum() else "_" for c in name.lower())
    # Remove multiple consecutive underscores
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    # Remove leading/trailing underscores
    return normalized.strip("_")

def truncate_with_ellipsis(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if longer than max_length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

# =============================================================================
# NETWORK UTILITIES
# =============================================================================

def get_local_ip() -> str:
    """Get the local IP address of the machine."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def get_hostname() -> str:
    """Get the hostname of the machine."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"

def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def is_port_open(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a port is open on a host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

# =============================================================================
# FILE UTILITIES
# =============================================================================

def calculate_file_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def get_file_size_human(file_path: str) -> str:
    """Get file size in human-readable format."""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except Exception:
        return "Unknown"

def ensure_directory_exists(dir_path: str) -> bool:
    """Ensure directory exists, create if necessary."""
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception:
        return False

# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    if not email or "@" not in email:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
    
    local, domain = parts
    if not local or not domain or "." not in domain:
        return False
    
    return True

def is_valid_username(username: str) -> bool:
    """Validate username format."""
    if not username:
        return False
    
    username = username.strip()
    if len(username) < 3 or len(username) > 50:
        return False
    
    # Allow alphanumeric, underscore, dash
    return all(c.isalnum() or c in "_-" for c in username)

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate required fields are present and not empty. Returns list of missing fields."""
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing.append(field)
    return missing

# =============================================================================
# TASK/STATUS UTILITIES
# =============================================================================

def is_task_completed(status: str) -> bool:
    """Check if task status indicates completion."""
    completed_statuses = ['Done', 'success', 'failed', 'completed', 'error']
    return status in completed_statuses

def normalize_status(status: str) -> str:
    """Normalize status string to standard format."""
    if not status:
        return 'unknown'
    
    status = status.lower().strip()
    status_mapping = {
        'done': 'completed',
        'ok': 'success',
        'fail': 'failed',
        'err': 'error',
        'running': 'active',
        'pending': 'created'
    }
    
    return status_mapping.get(status, status)

# =============================================================================
# ID GENERATION UTILITIES
# =============================================================================

def generate_unique_id(prefix: str = "", length: int = 12) -> str:
    """Generate a unique ID with optional prefix."""
    timestamp = str(int(time.time() * 1000))
    unique_part = timestamp[-length:]
    
    if prefix:
        return f"{prefix}_{unique_part}"
    return unique_part

def generate_execution_id(task_id: str, client_id: str) -> str:
    """Generate a unique execution ID."""
    timestamp = int(time.time() * 1000)
    return f"{task_id}_{client_id}_{timestamp}"

# =============================================================================
# ERROR HANDLING UTILITIES
# =============================================================================

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int, return default on error."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float, return default on error."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value: Any, default: bool = False) -> bool:
    """Safely convert value to bool, return default on error."""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on', 'enabled')
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    return default
