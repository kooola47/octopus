import json
import datetime
import time
import socket
import os
import hashlib
from typing import Any, Dict, Union, List, Optional

def get_current_timestamp():
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

def format_timestamp(timestamp: Union[str, float, int, datetime.datetime, None]) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Timestamp in various formats
        
    Returns:
        Formatted timestamp string
    """
    try:
        if timestamp is None:
            return "N/A"
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
        return str(timestamp) if timestamp is not None else "N/A"

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

def is_task_completed(status):
    return status in ['Done', 'success', 'failed', 'completed']

def sanitize_string(text, max_length=1000):
    if not text:
        return ""
    text = str(text)
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    return text.strip()

def safe_json_loads(json_str, default=None):
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except:
        return default

def require_login(f):
    """Decorator to require user authentication"""
    from functools import wraps
    from flask import session, redirect, url_for, request, jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    from flask import session, redirect, url_for, request, jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        # Check if user is admin
        if session.get('role') != 'admin':
            if request.is_json:
                return jsonify({'success': False, 'error': 'Admin privileges required'}), 403
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function
