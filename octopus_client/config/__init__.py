# =============================================================================
# 🐙 OCTOPUS CLIENT CONFIGURATION PACKAGE
# =============================================================================
"""
Configuration package for Octopus Client with environment-specific settings.

Usage:
    python main.py          # Loads development config
    python main.py dev      # Loads development config
    python main.py prod     # Loads production config
"""

from .config_loader import load_config, get_current_config
from .config_base import BaseConfig
from .config_dev import DevelopmentConfig
from .config_prod import ProductionConfig

# Export the current configuration
config = get_current_config()

# Export commonly used configuration values for backward compatibility
SERVER_URL = config.SERVER_URL
HEARTBEAT_INTERVAL = config.HEARTBEAT_INTERVAL
TASK_CHECK_INTERVAL = config.TASK_CHECK_INTERVAL
MAX_RETRY_ATTEMPTS = config.MAX_RETRY_ATTEMPTS
RETRY_DELAY = config.RETRY_DELAY
PLUGINS_FOLDER = config.PLUGINS_FOLDER
CACHE_TTL = config.CACHE_TTL
LOG_LEVEL = config.LOG_LEVEL
LOG_FILE = config.LOG_FILE
LOG_MAX_SIZE = config.LOG_MAX_SIZE
LOG_BACKUP_COUNT = config.LOG_BACKUP_COUNT
HEARTBEAT_ENDPOINT = config.HEARTBEAT_ENDPOINT
TASKS_ENDPOINT = config.TASKS_ENDPOINT
PLUGINS_ENDPOINT = config.PLUGINS_ENDPOINT
CLIENT_NAME_PREFIX = config.CLIENT_NAME_PREFIX
USER_NAME = config.USER_NAME
CLIENT_METADATA = config.CLIENT_METADATA

__all__ = [
    'load_config',
    'get_current_config',
    'config',
    'BaseConfig',
    'DevelopmentConfig', 
    'ProductionConfig',
    'SERVER_URL',
    'HEARTBEAT_INTERVAL',
    'TASK_CHECK_INTERVAL',
    'MAX_RETRY_ATTEMPTS',
    'RETRY_DELAY',
    'PLUGINS_FOLDER',
    'CACHE_TTL',
    'LOG_LEVEL',
    'LOG_FILE',
    'LOG_MAX_SIZE',
    'LOG_BACKUP_COUNT',
    'HEARTBEAT_ENDPOINT',
    'TASKS_ENDPOINT',
    'PLUGINS_ENDPOINT',
    'CLIENT_NAME_PREFIX',
    'USER_NAME',
    'CLIENT_METADATA'
]
