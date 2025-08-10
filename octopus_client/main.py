#!/usr/bin/env python3
"""
🐙 OCTOPUS CLIENT - Distributed Task Execution Agent
===================================================

Client agent that connects to the Octopus server to:
- Receive and execute tasks
- Send heartbeat signals
- Manage plugin synchronization
- Report execution results
"""

import os
import time
import logging
import threading
from flask import Flask
from cache import Cache
from config import *
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

# Disable werkzeug's default HTTP access logging for consistency
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True

logger = logging.getLogger("octopus_client")

# Initialize core components
status_manager = StatusManager()
task_executor = TaskExecutor(SERVER_URL, logger)
server_comm = ServerCommunicator(SERVER_URL, TASK_CHECK_INTERVAL, RETRY_DELAY, logger)
task_loop = TaskExecutionLoop(task_executor, server_comm, SERVER_URL, TASK_CHECK_INTERVAL, RETRY_DELAY, logger)
http_status_server = HTTPStatusServer("localhost", 8080, status_manager, logger)

# Make status manager available globally for routes
latest_task_info = status_manager.latest_task_info

# Register organized routes
from routes import register_all_routes
register_all_routes(app, cache, logger)

# Log client startup information
logger.info("Octopus Client starting")
logger.info(f"Server URL: {SERVER_URL}")
logger.info(f"Heartbeat interval: {HEARTBEAT_INTERVAL}s")
logger.info(f"Task check interval: {TASK_CHECK_INTERVAL}s")
logger.info(f"Plugins folder: {PLUGINS_FOLDER}")

def run():
    """Main client execution function"""
    cache.set("login_time", time.time())
    
    # Start HTTP status server
    http_status_server.start()
    
    # Wrap tasks to track their status
    scheduler.add_task(status_manager.tracked_task(send_heartbeat, "send_heartbeat"), HEARTBEAT_INTERVAL)
    scheduler.add_task(status_manager.tracked_task(check_plugin_updates, "check_plugin_updates"), 60)
    
    # Start background threads
    threading.Thread(target=server_comm.handle_server_commands, daemon=True).start()
    
    # Import username from heartbeat module
    from heartbeat import USERNAME as username
    threading.Thread(target=lambda: task_loop.run(username), daemon=True).start()
    
    # Start Flask app for client API
    app.run(port=5001, debug=False)

if __name__ == "__main__":
    run()
