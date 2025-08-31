# =============================================================================
# 🐙 OCTOPUS SERVER CONFIGURATION
# =============================================================================

import os
from config.config_prod import BaseConfig


class DevelopmentConfig(BaseConfig):
    ENVIRONMENT = "development"
    DEBUG = False

    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 18900
    DEBUG_MODE = False

    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "octopus.db")

    # =============================================================================
    # CACHE SETTINGS
    # =============================================================================
    CACHE_TTL = 600  # Cache time-to-live in seconds (10 minutes)

    # =============================================================================
    # PLUGIN SETTINGS
    # =============================================================================
    PLUGINS_FOLDER = "./plugins"

    # =============================================================================
    # CLIENT MANAGEMENT
    # =============================================================================
    CLIENT_TIMEOUT = 30  # Consider client offline after 30 seconds
    HEARTBEAT_CLEANUP_INTERVAL = 60  # Clean up old heartbeats every 60 seconds

    # =============================================================================
    # TASK SETTINGS
    # =============================================================================
    TASK_ASSIGNMENT_DELAY = 2  # Seconds to wait before assigning tasks
    TASK_CLEANUP_INTERVAL = 300  # Clean up old tasks every 5 minutes

    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join("logs", "server.log")
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # =============================================================================
    # API ENDPOINTS
    # =============================================================================
    API_BASE_URL = ""
    HEARTBEAT_ENDPOINT = "/heartbeat"
    TASKS_ENDPOINT = "/tasks"
    PLUGINS_ENDPOINT = "/plugins"
    DASHBOARD_ENDPOINT = "/"

    # =============================================================================
    # HTML AND STATIC FILES
    # =============================================================================
    # Set template_folder and static_folder for best practice
    PAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pages")
    STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
