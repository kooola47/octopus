#!/usr/bin/env python3
"""
🐙 OCTOPUS CLIENT - Distributed Task Execution Agent
===================================================

Client agent that connects to the Octopus server to:
- Receive and execute tasks
- Send heartbeat signals
- Manage plugin synchronization
- Report execution results

Usage:
    python main.py          # Development mode
    python main.py dev      # Development mode  
    python main.py prod     # Production mode
"""

import os
import sys
import time
import logging
import threading

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load configuration first (this will parse command line arguments)
from config import load_config, get_current_config
config = load_config()  # This will load based on command line args

from flask import Flask
from cache import Cache
from scheduler import Scheduler
from heartbeat import send_heartbeat
from pluginhelper import check_plugin_updates
from utils import get_hostname, get_local_ip, get_client_id

# Import organized modules
from core.task_execution import TaskExecutor
from core.server_communication import ServerCommunicator
from core.status_manager import StatusManager
from core.task_loop import TaskExecutionLoop
from core.http_status_server import HTTPStatusServer

# Initialize components
cache = Cache()
scheduler = Scheduler()
app = Flask(__name__)

# Setup logs folder and logging using config
os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Disable werkzeug's default HTTP access logging for consistency
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True

logger = logging.getLogger("octopus_client")

# Initialize global cache system
from global_cache_manager import initialize_client_global_cache
try:
    global_cache = initialize_client_global_cache(config.SERVER_URL, config.USERNAME)
    logger.info(f"Client global cache system initialized successfully for user: {config.USERNAME}")
except Exception as e:
    logger.error(f"Failed to initialize client global cache: {e}")

# Initialize core components with config values
status_manager = StatusManager()

if not config.SERVER_URL:
    logger.error("SERVER_URL is not set in the configuration. Please provide a valid server URL.")
    raise ValueError("SERVER_URL must not be None or empty.")

task_executor = TaskExecutor(config.SERVER_URL, logger)
server_comm = ServerCommunicator(config.SERVER_URL, config.TASK_CHECK_INTERVAL, config.RETRY_DELAY, logger)
task_loop = TaskExecutionLoop(task_executor, server_comm, config.SERVER_URL, config.TASK_CHECK_INTERVAL, config.RETRY_DELAY, logger)
http_status_server = HTTPStatusServer("localhost", 8080, status_manager, logger)

# Make status manager available globally for routes
latest_task_info = status_manager.latest_task_info

# Register organized routes
from routes import register_all_routes
register_all_routes(app, cache, logger)

# Log client startup information
logger.info("🐙 Octopus Client starting...")
logger.info(f"Environment: {config.ENVIRONMENT}")
logger.info(f"Debug Mode: {config.DEBUG}")
logger.info(f"Server URL: {config.SERVER_URL}")
logger.info(f"Heartbeat interval: {config.HEARTBEAT_INTERVAL}s")
logger.info(f"Task check interval: {config.TASK_CHECK_INTERVAL}s")
logger.info(f"Plugins folder: {config.PLUGINS_FOLDER}")
logger.info(f"Username: {config.USERNAME}")

def run():
    """Main client execution function"""
    cache.set("login_time", time.time())
    
    # Start HTTP status server
    http_status_server.start()
    
    # Wrap tasks to track their status
    def track_heartbeat():
        while True:
            try:
                status_manager.update_task("Heartbeat", "Running", "Sending heartbeat to server")
                send_heartbeat()
                status_manager.update_task("Heartbeat", "Success", f"Last heartbeat: {time.strftime('%H:%M:%S')}")
                time.sleep(config.HEARTBEAT_INTERVAL)
            except Exception as e:
                status_manager.update_task("Heartbeat", "Error", f"Heartbeat failed: {str(e)}")
                logger.error(f"Heartbeat error: {e}")
                time.sleep(config.HEARTBEAT_INTERVAL)

    def track_plugin_updates():
        while True:
            try:
                status_manager.update_task("Plugin Updates", "Running", "Checking for plugin updates")
                check_plugin_updates()
                status_manager.update_task("Plugin Updates", "Success", f"Last check: {time.strftime('%H:%M:%S')}")
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                status_manager.update_task("Plugin Updates", "Error", f"Plugin check failed: {str(e)}")
                logger.error(f"Plugin update error: {e}")
                time.sleep(30)

    # Start background threads
    heartbeat_thread = threading.Thread(target=track_heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    plugin_thread = threading.Thread(target=track_plugin_updates)
    plugin_thread.daemon = True
    plugin_thread.start()

    # Start task execution loop
    task_loop_thread = threading.Thread(target=task_loop.run, args=(config.USERNAME,))
    task_loop_thread.daemon = True
    task_loop_thread.start()

    # Start Flask app (this will block)
    try:
        app.run(host="0.0.0.0", port=8081, debug=config.DEBUG)
    except KeyboardInterrupt:
        logger.info("Client shutting down...")
        status_manager.update_task("Client", "Stopped", "Client shutdown by user")
    except Exception as e:
        logger.error(f"Client error: {e}")
        status_manager.update_task("Client", "Error", f"Client error: {str(e)}")

if __name__ == "__main__":
    run()
