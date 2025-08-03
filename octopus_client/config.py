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
HEARTBEAT_INTERVAL = 10  # Send heartbeat every 10 seconds
TASK_CHECK_INTERVAL = 5  # Check for new tasks every 5 seconds
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
CLIENT_METADATA = {
    "version": "1.0.0",
    "capabilities": ["plugin_execution", "task_scheduling"]
}
