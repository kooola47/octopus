import os
import time
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from cache import Cache
from config import HEARTBEAT_INTERVAL,SERVER_URL
from scheduler import Scheduler
from flask import Flask, request, jsonify
from taskmanager import sync_tasks, get_tasks, add_task, update_task, delete_task

from heartbeat import send_heartbeat
from pluginhelper import check_plugin_updates
import socket
import requests
import importlib
import json

cache = Cache()
scheduler = Scheduler()
app = Flask(__name__)

# Setup logs folder and logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("logs/client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("octopus_client")

# Track latest scheduled task and status
latest_task_info = {
    "task": "",
    "status": "",
    "last_run": ""
}

def tracked_task(task_func, task_name):
    def wrapper():
        try:
            latest_task_info["task"] = task_name
            latest_task_info["status"] = "Running"
            latest_task_info["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            task_func()
            latest_task_info["status"] = "Success"
        except Exception as e:
            latest_task_info["status"] = f"Failed: {e}"
    return wrapper

# HTTP handler to show latest scheduled task info
class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html>
            <head><title>Scheduled Task Status</title></head>
            <body>
                <h2>Latest Scheduled Task</h2>
                <p><b>Task:</b> {latest_task_info['task']}</p>
                <p><b>Status:</b> {latest_task_info['status']}</p>
                <p><b>Last Run:</b> {latest_task_info['last_run']}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_status_server():
    server = HTTPServer((SERVER_URL, 8080), StatusHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info("Status page available at http://localhost:8080/status")

def handle_server_commands():
    hostname = socket.gethostname()
    while True:
        try:
            resp = requests.get(f"{SERVER_URL}/commands/{hostname}", timeout=5)
            if resp.status_code == 200:
                commands = resp.json()
                for cmd in commands:
                    plugin_name = cmd.get("plugin")
                    action = cmd.get("action")
                    args = cmd.get("args", [])
                    kwargs = cmd.get("kwargs", {})
                    try:
                        module = importlib.import_module(f"plugins.{plugin_name}")
                        func = getattr(module, action, None)
                        if callable(func):
                            func(*args, **kwargs)
                            logger.info(f"Executed {plugin_name}.{action} with args={args}, kwargs={kwargs}")
                        else:
                            logger.error(f"Action {action} not found in plugin {plugin_name}")
                    except Exception as e:
                        logger.error(f"Failed to execute plugin {plugin_name}: {e}")
            # Poll every 5 seconds
            time.sleep(5)
        except Exception as e:
            logger.error(f"Command polling failed: {e}")
            time.sleep(5)

def task_sync_loop():
    while True:
        sync_tasks()
        time.sleep(5)

def task_execution_loop():
    """
    Periodically fetch tasks from the server and execute if assigned to this client.
    Executes if:
      - owner == "ALL"
      - owner == <this username>
      - owner == "Anyone" and executor == <this username>
    Only executes if status is not 'success' or 'failed'.
    """
    import getpass
    import importlib
    import ast
    from heartbeat import USERNAME as username, HOSTNAME as hostname
    # Get username and hostname from heartbeat module to keep in sync
    while True:
        try:
            resp = requests.get(f"{SERVER_URL}/tasks", timeout=10)
            if resp.status_code == 200:
                tasks = resp.json()
                for tid, task in tasks.items():
                    owner = task.get("owner")
                    executor = task.get("executor")
                    status = task.get("status")
                    plugin = task.get("plugin")
                    action = task.get("action", "run")
                    args = task.get("args", [])
                    kwargs = task.get("kwargs", {})
                    # Parse args/kwargs if they are strings
                    if isinstance(args, str):
                        try:
                            args = ast.literal_eval(args)
                        except Exception:
                            args = []
                    if isinstance(kwargs, str):
                        try:
                            kwargs = ast.literal_eval(kwargs)
                        except Exception:
                            kwargs = {}
                    should_execute = False
                    if owner == "ALL":
                        should_execute = True
                    elif owner == username:
                        should_execute = True
                    elif owner == "Anyone" and executor == username:
                        should_execute = True
                    if should_execute and status not in ("success", "failed"):
                        try:
                            module = importlib.import_module(f"plugins.{plugin}")
                            func = getattr(module, action, None)
                            if callable(func):
                                logger.info(f"Executing task {tid}: {plugin}.{action} args={args} kwargs={kwargs}")
                                result = func(*args, **kwargs)
                                update = {
                                    "status": "success",
                                    "result": result,
                                    "executor": username,
                                    "updated_at": time.time()
                                }
                            else:
                                update = {
                                    "status": "failed",
                                    "result": f"Action {action} not found",
                                    "executor": username,
                                    "updated_at": time.time()
                                }
                        except Exception as e:
                            update = {
                                "status": "failed",
                                "result": str(e),
                                "executor": username,
                                "updated_at": time.time()
                            }
                        try:
                            requests.put(f"{SERVER_URL}/tasks/{tid}", json=update, timeout=5)
                        except Exception as e:
                            logger.error(f"Failed to update task {tid} status: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Task execution polling failed: {e}")
            time.sleep(5)

def run():
    cache.set("login_time", time.time())
    # Wrap tasks to track their status
    scheduler.add_task(tracked_task(send_heartbeat, "send_heartbeat"), HEARTBEAT_INTERVAL)
    scheduler.add_task(tracked_task(check_plugin_updates, "check_plugin_updates"), 60)
    threading.Thread(target=handle_server_commands, daemon=True).start()
    threading.Thread(target=task_sync_loop, daemon=True).start()
    threading.Thread(target=task_execution_loop, daemon=True).start()
    app.run(port=5001)  # Client UI/API

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "POST":
        task = request.json
        task_id = add_task(task)
        return jsonify({"id": task_id})
    return jsonify(get_tasks())

@app.route("/tasks/<task_id>", methods=["PUT", "DELETE"])
def task_ops(task_id):
    if request.method == "PUT":
        updates = request.json
        ok = update_task(task_id, updates)
        return jsonify({"success": ok})
    elif request.method == "DELETE":
        ok = delete_task(task_id)
        return jsonify({"success": ok})

if __name__ == "__main__":
    run()
