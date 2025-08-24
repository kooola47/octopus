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
from cache import Cache
from config import *


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


cache = Cache()
# Initialize database
from dbhelper import init_db
init_db()

# Initialize plugin cache system
from plugin_cache_manager import initialize_plugin_cache
try:
    plugin_cache = initialize_plugin_cache(
        plugins_folder=PLUGINS_FOLDER,
        start_background_refresh=True
    )
    logger.info("Plugin cache system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize plugin cache: {e}")

# Initialize client cache system
from client_cache_manager import get_client_cache_manager
try:
    client_cache = get_client_cache_manager()
    logger.info("Client cache system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize client cache: {e}")

# Initialize global cache system
from global_cache_manager import initialize_global_cache
try:
    global_cache = initialize_global_cache()
    logger.info("Global cache system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize global cache: {e}")

# Register routes from other modules
from pluginhelper import register_plugin_routes
from heartbeat import register_heartbeat_routes
register_heartbeat_routes(app, cache, logger)
register_plugin_routes(app, logger)

# Register all organized routes
from routes import register_all_routes
from routes.modern_routes import register_modern_routes
from routes.user_profile_routes import user_profile_bp
from routes.plugin_routes import plugin_bp
from template_helpers import register_template_helpers

register_all_routes(app, cache, logger)
register_modern_routes(app, cache, logger)

# Register template helpers for status management
register_template_helpers(app)

# Register user profile routes
app.register_blueprint(user_profile_bp)

# Register plugin management routes
app.register_blueprint(plugin_bp)

# Log server startup information
logger.info(f"Octopus Server starting on {SERVER_HOST}:{SERVER_PORT}")
logger.info(f"Database: {DB_FILE}")
logger.info(f"Plugins folder: {PLUGINS_FOLDER}")
logger.info(f"Pages folder: {PAGES_DIR}")
logger.info(f"Static folder: {STATIC_DIR}")

if __name__ == "__main__":
    # Enable threading for concurrent request handling
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, debug=False)
