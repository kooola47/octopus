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
    # ENVIRONMENT IDENTIFICATION
    # =============================================================================
    ENVIRONMENT = "base"
    DEBUG = False
    SERVER_URL = os.getenv("OCTOPUS_SERVER_URL", "http://base-server:18900")
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
        "environment": "base"
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
    PLUGINS_UPDATE_INTERVAL = 30  # Check for plugin updates every 30 seconds
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
            "username": cls.USER_NAME
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