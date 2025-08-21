# =============================================================================
# 🐙 OCTOPUS CLIENT BASE CONFIGURATION
# =============================================================================
"""
Base configuration class with common settings for all environments.
"""

import os
from utils import get_hostname, get_local_ip

class BaseConfig:
    """Base configuration class with default settings."""
    
    # =============================================================================
    # SERVER CONNECTION (must be defined in subclasses)
    # =============================================================================
    SERVER_URL = None  # Must be overridden in subclasses
    
    CLIENT_HOSTNAME = get_hostname()
    CLIENT_IP = get_local_ip()
    CLIENT_PORT = 8081
    # =============================================================================
    # CLIENT BEHAVIOR
    # =============================================================================
    HEARTBEAT_INTERVAL = 30  # Send heartbeat every 30 seconds
    TASK_CHECK_INTERVAL = 15  # Check for new tasks every 15 seconds
    MAX_RETRY_ATTEMPTS = 3  # Maximum retries for failed operations
    RETRY_DELAY = 2  # Seconds to wait between retries
    
    # =============================================================================
    # PLUGIN SETTINGS
    # =============================================================================
    PLUGINS_FOLDER = "./plugins"
    
    # =============================================================================
    # CACHE SETTINGS
    # =============================================================================
    CACHE_TTL = 600  # Cache time-to-live in seconds (10 minutes)
    
    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join("logs", "client.log")
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # =============================================================================
    # API ENDPOINTS
    # =============================================================================
    HEARTBEAT_ENDPOINT = "/heartbeat"
    TASKS_ENDPOINT = "/tasks"
    PLUGINS_ENDPOINT = "/plugins"
    
    # =============================================================================
    # CLIENT IDENTIFICATION
    # =============================================================================
    CLIENT_NAME_PREFIX = "client"  # Will be suffixed with PID
    USERNAME = os.getenv("OCTOPUS_USERNAME", "default_user")  # Can be overridden via environment variable
    CLIENT_METADATA = {
        "version": "1.0.0",
        "capabilities": ["plugin_execution", "task_scheduling"]
    }
    
    # =============================================================================
    # ENVIRONMENT IDENTIFICATION
    # =============================================================================
    ENVIRONMENT = "base"
    DEBUG = False
    
    @classmethod
    def get_config_summary(cls):
        """Get a summary of the current configuration."""
        return {
            "environment": cls.ENVIRONMENT,
            "server_url": cls.SERVER_URL,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "heartbeat_interval": cls.HEARTBEAT_INTERVAL,
            "task_check_interval": cls.TASK_CHECK_INTERVAL,
            "username": cls.USERNAME
        }
    
    @classmethod
    def validate_config(cls):
        """Validate the configuration settings."""
        errors = []
        
        if not hasattr(cls, 'SERVER_URL') or not cls.SERVER_URL:
            errors.append("SERVER_URL must be defined")
            
        if cls.HEARTBEAT_INTERVAL <= 0:
            errors.append("HEARTBEAT_INTERVAL must be positive")
            
        if cls.TASK_CHECK_INTERVAL <= 0:
            errors.append("TASK_CHECK_INTERVAL must be positive")
            
        if cls.MAX_RETRY_ATTEMPTS < 0:
            errors.append("MAX_RETRY_ATTEMPTS must be non-negative")
            
        if cls.CACHE_TTL <= 0:
            errors.append("CACHE_TTL must be positive")
            
        return errors
