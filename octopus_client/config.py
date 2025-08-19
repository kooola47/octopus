# =============================================================================
# 🐙 OCTOPUS CLIENT CONFIGURATION
# =============================================================================

import os

# =============================================================================
# SERVER CONNECTION
# =============================================================================
SERVER_URL = "http://localhost:8000"

# =============================================================================
# CLIENT BEHAVIOR
# =============================================================================
HEARTBEAT_INTERVAL = 30  # Send heartbeat every 30 seconds (was 10)
TASK_CHECK_INTERVAL = 15  # Check for new tasks every 15 seconds (was 5)
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
