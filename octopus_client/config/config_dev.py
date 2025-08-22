# =============================================================================
# 🐙 OCTOPUS CLIENT DEVELOPMENT CONFIGURATION
# =============================================================================
"""
Development configuration with local server settings and verbose logging.
"""

import os
from .config_base import BaseConfig
from utils import get_hostname, get_local_ip

class DevelopmentConfig(BaseConfig):
    """Development configuration with local settings and enhanced debugging."""
    
    # =============================================================================
    # ENVIRONMENT IDENTIFICATION
    # =============================================================================
    ENVIRONMENT = "development"
    DEBUG = False
    SERVER_URL = os.getenv("OCTOPUS_SERVER_URL", "http://localhost:18900")

    # =============================================================================
    # Client Configuration
    # =============================================================================
    CLIENT_NAME_PREFIX = ""
    CLIENT_HOSTNAME = get_hostname()
    CLIENT_IP = get_local_ip()
    CLIENT_PORT = 8900
    CLIENT_DOMAIN = os.environ.get("USERDOMAIN", "")
    CLIENT_VERSION = "2025.08.15.140922"
    CLIENT_METADATA = {
        "version": "1.0.0",
        "capabilities": ["plugin_execution", "task_scheduling"],
        "environment": "development"
    }
    # =============================================================================
    # Client Configuration
    # =============================================================================
    USER_NAME = os.environ.get("OCTOPUS_SamAccountName", "Tuser")
    USER_DISPLAY_NAME = os.environ.get("OCTOPUS_DisplayName", "Display,Name")
    USER_IDENTITY = os.environ.get("OCTOPUS_EmployeeNumber", "Gnumber")
    USER_EMAIL = os.environ.get("OCTOPUS_EmailAddress", "myemail@outlook.com")
    USER_CHROMEUSERDATA = os.environ.get("OCTOPUS_ChromeUserData", "C:\\Users\\aries\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    
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