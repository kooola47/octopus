# =============================================================================
# 🐙 OCTOPUS CLIENT PRODUCTION CONFIGURATION
# =============================================================================
"""
Production configuration with optimized settings for performance and stability.
"""

import os
from .config_base import BaseConfig
from utils import get_hostname, get_local_ip


class ProductionConfig(BaseConfig):
    """Production configuration with optimized settings."""
    
    # =============================================================================
    # ENVIRONMENT IDENTIFICATION
    # =============================================================================
    ENVIRONMENT = "production"
    DEBUG = False
    SERVER_URL = os.getenv("OCTOPUS_SERVER_URL", "http://production-server:18900")

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
        "environment": "production"
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
    # CLIENT BEHAVIOR (Optimized for production)
    # =============================================================================
    HEARTBEAT_INTERVAL = 60   # Less frequent heartbeats for production efficiency
    TASK_CHECK_INTERVAL = 30  # Less frequent task checks for production
    MAX_RETRY_ATTEMPTS = 3    # Standard retry attempts
    RETRY_DELAY = 5          # Longer delay for production stability
    PLUGINS_UPDATE_INTERVAL = 30    # Check for plugin updates every 30 seconds
    # =============================================================================
    # LOGGING SETTINGS (Minimal for production)
    # =============================================================================
    LOG_LEVEL = "WARNING"
    LOG_FILE = os.path.join("logs", "client_prod.log")
    LOG_MAX_SIZE = 50 * 1024 * 1024  # 50MB for production
    LOG_BACKUP_COUNT = 10
    
    # =============================================================================
    # CACHE SETTINGS (Longer TTL for production)
    # =============================================================================
    CACHE_TTL = 1800  # 30 minutes for production
    
    # =============================================================================
    # PRODUCTION SPECIFIC SETTINGS
    # =============================================================================
    ENABLE_PERFORMANCE_MONITORING = False
    DETAILED_ERROR_LOGGING = False
    AUTO_RELOAD_PLUGINS = True
    MOCK_EXTERNAL_SERVICES = False
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    ENABLE_SSL_VERIFICATION = True
    CONNECTION_TIMEOUT = 30
    READ_TIMEOUT = 60
    
    # =============================================================================
    # RESOURCE LIMITS
    # =============================================================================
    MAX_CONCURRENT_TASKS = 10
    MAX_MEMORY_USAGE_MB = 512
    MAX_CPU_USAGE_PERCENT = 80

    
    # =============================================================================
    # PRODUCTION MONITORING
    # =============================================================================
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes
    METRICS_COLLECTION_ENABLED = True
    CRASH_REPORTING_ENABLED = True
