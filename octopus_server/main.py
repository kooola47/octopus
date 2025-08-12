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

from flask import Flask
from cache import Cache
from config import *
import os
import logging
from datetime import datetime

# Set template_folder and static_folder for best practice
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
PAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Create directories if they don't exist
for directory in [TEMPLATE_DIR, PAGES_DIR, STATIC_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

app = Flask(
    __name__,
    template_folder=PAGES_DIR,  # Use pages directory for modern templates
    static_folder=STATIC_DIR
)

# Configure Flask secret key for sessions (required for authentication)
app.secret_key = 'octopus-secret-key-change-in-production'

# Configure session settings for proper persistence
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

cache = Cache()

# Custom template filter for datetime formatting
@app.template_filter('datetimeformat')
def datetimeformat(value):
    if value is None:
        return 'Unknown'
    try:
        # If it's a timestamp (float), convert to datetime
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(value)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return str(value)
    except:
        return str(value)

@app.template_filter('seconds_to_human')
def seconds_to_human_filter(seconds):
    try:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        elif seconds < 86400:
            return f"{seconds//3600}h {(seconds%3600)//60}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    except Exception:
        return str(seconds)

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

# Create custom HTTP request logger
http_logger = logging.getLogger("http_requests")

# Custom middleware to log HTTP requests in standardized format
def log_request_info():
    """Log HTTP request in standardized format"""
    from flask import request
    http_logger.info(f"{request.remote_addr} {request.method} {request.path} {request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')}")

# Register the after_request handler
@app.after_request
def after_request(response):
    # Log the request with response status in standardized format
    from flask import request
    http_logger.info(f"{request.remote_addr} {request.method} {request.path} -> {response.status_code} {response.status}")
    return response

logger = logging.getLogger("octopus_server")

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

# Register routes from other modules
from pluginhelper import register_plugin_routes
from heartbeat import register_heartbeat_routes
register_heartbeat_routes(app, cache, logger)
register_plugin_routes(app, logger)

# Register all organized routes
from routes import register_all_routes
from routes.modern_routes import register_modern_routes
register_all_routes(app, cache, logger)
register_modern_routes(app, cache, logger)

# Log server startup information
logger.info(f"Octopus Server starting on {SERVER_HOST}:{SERVER_PORT}")
logger.info(f"Database: {DB_FILE}")
logger.info(f"Plugins folder: {PLUGINS_FOLDER}")
logger.info(f"Template folder: {TEMPLATE_DIR}")
logger.info(f"Modern pages folder: {PAGES_DIR}")
logger.info(f"Static folder: {STATIC_DIR}")

if __name__ == "__main__":
    # Enable threading for concurrent request handling
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, debug=False)
