#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Distributed Task Orchestration
=================================================

Main server application that provides:
- Web dashboard for task management
- RESTful API for client communication
- Plugin management system
- Task assignment and execution tracking
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from services.global_cache_manager import initialize_global_cache
# Load config once
from config import load_config
config = load_config()  # This will load based on command line args

# Extract configuration variables from the config class
SERVER_HOST = config.SERVER_HOST
SERVER_PORT = config.SERVER_PORT
DB_FILE = config.DB_FILE
PLUGINS_FOLDER = config.PLUGINS_FOLDER
LOG_LEVEL = config.LOG_LEVEL
LOG_FILE = config.LOG_FILE
PAGES_DIR = config.PAGES_DIR
STATIC_DIR = config.STATIC_DIR
CACHE_TTL = config.CACHE_TTL


# Setup logs folder and logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
# Disable werkzeug's default HTTP access logging and create custom one
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True
logger = logging.getLogger("octopus_server")



from models.flask_app_model import FlaskAppModel
flask_app_model = FlaskAppModel()
app = flask_app_model.config_flask_app(logger)

# Initialize database
from dbhelper import init_db
init_db()

# Initialize global cache system (handles all cache layers)
try:
    global_cache = initialize_global_cache()
    logger.info("Global cache system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize global cache: {e}")

# Register routes from other modules

from pluginhelper import register_plugin_routes
from heartbeat import register_heartbeat_routes
register_heartbeat_routes(app, global_cache, logger)
register_plugin_routes(app, global_cache,logger)

# Register all organized routes

from routes import register_all_routes
from routes.modern_routes import register_modern_routes
from routes.user_profile_routes import user_profile_bp, set_global_cache
# Set global_cache for user_profile_routes
set_global_cache(global_cache)
from routes.plugin_routes import plugin_bp
from helpers.template_helpers import register_template_helpers

register_all_routes(app, global_cache, logger)
register_modern_routes(app, global_cache, logger)

# Register template helpers for status management
register_template_helpers(app)

# Register user profile routes
app.register_blueprint(user_profile_bp)

# Register plugin management routes
app.register_blueprint(plugin_bp)


# --- Plugin Hot Reload Scheduler ---
import threading
import time
from plugin_discovery import PluginDiscovery

def plugin_hot_reload_scheduler(global_cache, plugins_folder, interval=60):
    """Background thread to rescan plugins folder and update global cache periodically."""
    discovery = PluginDiscovery(plugins_folder)
    while True:
        try:
            plugins_metadata = discovery.get_plugins_with_metadata()
            # Update the global cache atomically
            global_cache.set('plugins', plugins_metadata, cache_type='startup')
            logger.info(f"[Scheduler] Plugin cache refreshed with {len(plugins_metadata)} plugins.")
        except Exception as e:
            logger.error(f"[Scheduler] Error refreshing plugin cache: {e}")
        time.sleep(interval)

# Start the scheduler thread (daemon so it won't block shutdown)
threading.Thread(
    target=plugin_hot_reload_scheduler,
    args=(global_cache, PLUGINS_FOLDER, 60),
    daemon=True
).start()

# Log server startup information
logger.info(f"Octopus Server starting on {SERVER_HOST}:{SERVER_PORT}")
logger.info(f"Database: {DB_FILE}")
logger.info(f"Plugins folder: {PLUGINS_FOLDER}")
logger.info(f"Pages folder: {PAGES_DIR}")
logger.info(f"Static folder: {STATIC_DIR}")

if __name__ == "__main__":
    # Enable threading for concurrent request handling
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, debug=False)