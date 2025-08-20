# =============================================================================
# 🐙 OCTOPUS CLIENT DEVELOPMENT CONFIGURATION
# =============================================================================
"""
Development configuration with local server settings and verbose logging.
"""

import os
from .config_base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development configuration with local settings and enhanced debugging."""
    
    # =============================================================================
    # ENVIRONMENT IDENTIFICATION
    # =============================================================================
    ENVIRONMENT = "development"
    DEBUG = True
    
    # =============================================================================
    # SERVER CONNECTION
    # =============================================================================
    SERVER_URL = "http://localhost:8000"
    
    # =============================================================================
    # CLIENT BEHAVIOR (More frequent checks for development)
    # =============================================================================
    HEARTBEAT_INTERVAL = 10  # More frequent heartbeats for development
    TASK_CHECK_INTERVAL = 5   # More frequent task checks for development
    MAX_RETRY_ATTEMPTS = 5    # More retries for development debugging
    RETRY_DELAY = 1          # Shorter delay for faster development iteration
    
    # =============================================================================
    # LOGGING SETTINGS (Verbose for development)
    # =============================================================================
    LOG_LEVEL = "DEBUG"
    LOG_FILE = os.path.join("logs", "client_dev.log")
    LOG_MAX_SIZE = 5 * 1024 * 1024  # 5MB for development
    LOG_BACKUP_COUNT = 3
    
    # =============================================================================
    # CACHE SETTINGS (Shorter TTL for development)
    # =============================================================================
    CACHE_TTL = 300  # 5 minutes for development
    
    # =============================================================================
    # DEVELOPMENT SPECIFIC SETTINGS
    # =============================================================================
    ENABLE_PERFORMANCE_MONITORING = True
    DETAILED_ERROR_LOGGING = True
    AUTO_RELOAD_PLUGINS = True
    MOCK_EXTERNAL_SERVICES = False
    
    # =============================================================================
    # CLIENT IDENTIFICATION
    # =============================================================================
    USERNAME = os.getenv("OCTOPUS_USERNAME", "dev_user")
    CLIENT_METADATA = {
        "version": "1.0.0",
        "capabilities": ["plugin_execution", "task_scheduling", "development_mode"],
        "environment": "development"
    }
