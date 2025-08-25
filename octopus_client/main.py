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

# Load config once
from config import load_config
config = load_config()  # This will load based on command line args


# Setup logs folder and logging using config
import logging
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


# Initialize global cache once
from global_cache_manager import initialize_client_global_cache
logging.info(f"Initializing global cache: server_url:{config.SERVER_URL}, user_name:{config.USER_NAME}, user_identity:{config.USER_IDENTITY}")
global_cache = initialize_client_global_cache(config.SERVER_URL, config.USER_NAME,config.USER_IDENTITY)


from heartbeat import send_heartbeat
from pluginhelper import check_plugin_updates
from scheduler import Scheduler
scheduler = Scheduler()
from flask import Flask
app = Flask(__name__)
# Import organized modules
from core.task_execution import TaskExecutor
from core.server_communication import ServerCommunicator
from core.status_manager import StatusManager
from core.task_loop import TaskExecutionLoop


# Initialize core components with config values
status_manager = StatusManager()

if not config.SERVER_URL:
    logger.error("SERVER_URL is not set in the configuration. Please provide a valid server URL.")
    raise ValueError("SERVER_URL must not be None or empty.")

task_executor = TaskExecutor(config.SERVER_URL, logger)
server_comm = ServerCommunicator(config.SERVER_URL, config.TASK_CHECK_INTERVAL, config.RETRY_DELAY, logger)
task_loop = TaskExecutionLoop(task_executor, server_comm, config.SERVER_URL, config.TASK_CHECK_INTERVAL, config.RETRY_DELAY, logger)

# Make status manager available globally for routes
latest_task_info = status_manager.latest_task_info

from routes import register_all_routes
register_all_routes(app, global_cache, logger)

# Log client startup information
logger.info("🐙 Octopus Client starting...")
logger.info(f"Environment: {config.ENVIRONMENT}")
logger.info(f"Debug Mode: {config.DEBUG}")
logger.info(f"Server URL: {config.SERVER_URL}")
logger.info(f"Heartbeat interval: {config.HEARTBEAT_INTERVAL}s")
logger.info(f"Task check interval: {config.TASK_CHECK_INTERVAL}s")
logger.info(f"Plugins folder: {config.PLUGINS_FOLDER}")
logger.info(f"Plugins update interval: {config.PLUGINS_UPDATE_INTERVAL}s")
logger.info(f"Username: {config.USER_NAME}")
logger.info(f"User identity: {config.USER_IDENTITY}")

def run():
    """Main client execution function"""
    global_cache.set('login_time', str(time.time()), cache_type='startup')

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
                time.sleep(config.PLUGINS_UPDATE_INTERVAL)  # Check every 30 seconds
            except Exception as e:
                status_manager.update_task("Plugin Updates", "Error", f"Plugin check failed: {str(e)}")
                logger.error(f"Plugin update error: {e}")
                time.sleep(config.PLUGINS_UPDATE_INTERVAL)

    import threading
    # Start background threads
    heartbeat_thread = threading.Thread(target=track_heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    plugin_thread = threading.Thread(target=track_plugin_updates)
    plugin_thread.daemon = True
    plugin_thread.start()

    # Start task execution loop
    task_loop_thread = threading.Thread(target=task_loop.run, args=(config.USER_NAME,))
    task_loop_thread.daemon = True
    task_loop_thread.start()

    # Start Flask app (this will block)
    try:
        app.run(host='localhost', port=config.CLIENT_PORT, debug=config.DEBUG)
    except KeyboardInterrupt:
        logger.info("Client shutting down...")
        status_manager.update_task("Client", "Stopped", "Client shutdown by user")
    except Exception as e:
        logger.error(f"Client error: {e}")
        status_manager.update_task("Client", "Error", f"Client error: {str(e)}")

if __name__ == "__main__":
    run()
