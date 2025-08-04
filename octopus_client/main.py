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
from http.server import BaseHTTPRequestHandler, HTTPServer
from cache import Cache
from config import *
from scheduler import Scheduler
from flask import Flask, request, jsonify
from taskmanager import get_tasks, add_task, update_task, delete_task

from heartbeat import send_heartbeat
from pluginhelper import check_plugin_updates
from utils import get_hostname, get_local_ip, get_client_id
import socket
import requests   
import importlib
import json

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
logger = logging.getLogger("octopus_client")

# Log client startup information
logger.info("Octopus Client starting")
logger.info(f"Server URL: {SERVER_URL}")
logger.info(f"Heartbeat interval: {HEARTBEAT_INTERVAL}s")
logger.info(f"Task check interval: {TASK_CHECK_INTERVAL}s")
logger.info(f"Plugins folder: {PLUGINS_FOLDER}")

# =============================================================================
# CLIENT STATE MANAGEMENT
# =============================================================================

# Track latest scheduled task and status
latest_task_info = {
    "task": "",
    "status": "",
    "last_run": ""
}

# Track currently executing tasks to prevent duplicate executions
executing_tasks = set()

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
    hostname = get_hostname()
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
            # Poll for new tasks
            time.sleep(TASK_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Command polling failed: {e}")
            time.sleep(RETRY_DELAY)


def is_task_done(task):
    """
    Returns True if the task is considered Done.
    """
    import datetime, time
    
    status = task.get("status")
    task_type = task.get("type")
    
    # If status is already Done, return True
    if status in ("Done", "success", "failed"):
        return True
    
    # For Adhoc tasks, check if there are successful/failed executions
    if task_type == "Adhoc":
        executions = task.get("executions", [])
        # For non-ALL tasks, if any execution is done, task is done
        if task.get("owner") != "ALL":
            return any(exec.get("status") in ("success", "failed") for exec in executions)
        # For ALL tasks, they remain active until server marks them done
        return False
        
    # For Schedule tasks, check if past end time
    elif task_type == "Schedule":
        end_time = task.get("execution_end_time")
        if end_time:
            try:
                if isinstance(end_time, str) and end_time:
                    if end_time.isdigit():
                        end_ts = float(end_time)
                    else:
                        end_ts = datetime.datetime.fromisoformat(end_time).timestamp()
                else:
                    end_ts = float(end_time)
                if time.time() > end_ts:
                    return True
            except Exception:
                pass
    
    return False

def should_client_execute(task, username):
    """
    Returns True if this client should execute the task.
    Logic:
    - ALL tasks with status=Active: all clients execute
    - Tasks with executor=username and status=Active: only this client executes
    - Tasks with owner=username and status=Active: this client executes
    """
    owner = task.get("owner")
    executor = task.get("executor")
    status = task.get("status")
    
    # For ALL tasks, every client should execute if status is Active
    if owner == "ALL" and status == "Active":
        return True
    
    # For tasks specifically assigned to this client (executor = username)
    if executor == username and status == "Active":
        return True
    
    # For tasks owned by this user (fallback)
    if owner == username and status == "Active":
        return True
        
    return False

def claim_all_task(task, username):
    """
    Claim an ALL task if status is Created or executor is empty.
    """
    owner = task.get("owner")
    executor = task.get("executor")
    status = task.get("status")
    if owner == "ALL" and (not executor or status == "Created"):
        return True
    return False

def post_execution_result(server_url, tid, username, exec_status, result):
    """
    Post execution result for ALL tasks to the executions table.
    """
    try:
        requests.post(
            f"{server_url}/dashboard",
            data={
                "add_execution": "1",
                "task_id": tid,
                "client": username,
                "exec_status": exec_status,
                "exec_result": result
            },
            timeout=5
        )
        logger.info(f"Posted execution result for ALL task {tid} by {username}")
    except Exception as e:
        logger.error(f"Failed to post execution for ALL task {tid}: {e}")

def update_task_status(server_url, tid, username, result, status="Done"):
    """
    Update the task status for direct user tasks.
    """
    update = {
        "status": status,
        "result": result,
        "executor": username,
        "updated_at": time.time()
    }
    try:
        requests.put(f"{server_url}/tasks/{tid}", json=update, timeout=5)
    except Exception as e:
        logger.error(f"Failed to update task {tid} status: {e}")

def execute_task(task, tid, username, server_url):
    """
    Execute the given task and report result.
    Supports both synchronous and asynchronous plugin functions.
    """
    import importlib, ast, asyncio, inspect
    plugin = task.get("plugin")
    action = task.get("action", "run")
    args = task.get("args", [])
    kwargs = task.get("kwargs", {})
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
    try:
        module = importlib.import_module(f"plugins.{plugin}")
        func = getattr(module, action, None)
        if callable(func):
            logger.info(f"Executing task {tid}: {plugin}.{action} args={args} kwargs={kwargs}")
            
            # Check if the function is async (coroutine)
            if inspect.iscoroutinefunction(func):
                logger.debug(f"Function {plugin}.{action} is async, using asyncio.run()")
                try:
                    # Run async function
                    result = asyncio.run(func(*args, **kwargs))
                except Exception as e:
                    logger.error(f"Async execution failed for {plugin}.{action}: {e}")
                    result = str(e)
                    exec_status = "failed"
                    return exec_status, result
            else:
                logger.debug(f"Function {plugin}.{action} is sync, calling directly")
                # Run sync function normally
                result = func(*args, **kwargs)
            
            exec_status = "success"
        else:
            result = f"Action {action} not found"
            exec_status = "failed"
    except Exception as e:
        logger.error(f"Plugin execution failed for {plugin}.{action}: {e}")
        result = str(e)
        exec_status = "failed"
    return exec_status, result

def task_execution_loop():
    """
    Periodically fetch tasks from the server and execute if assigned to this client.
    """
    from heartbeat import USERNAME as username
    logger.info(f"Starting task execution loop for client: {username}")
    
    while True:
        try:
            # Use the taskmanager function which includes filtering
            tasks = get_tasks()
            logger.info(f"Fetched {len(tasks)} tasks from server")
            
            # Handle both dict and list formats
            if isinstance(tasks, dict):
                task_items = tasks.items()
            elif isinstance(tasks, list):
                # Convert list to dict-like items
                task_items = [(task.get('id', i), task) for i, task in enumerate(tasks)]
            else:
                logger.warning(f"Unexpected tasks format: {type(tasks)}")
                continue
                
            for tid, task in task_items:
                    owner = task.get("owner")
                    executor = task.get("executor") 
                    status = task.get("status")
                    
                    logger.debug(f"Checking task {tid}: owner={owner}, executor={executor}, status={status}")
                    
                    if is_task_done(task):
                        logger.debug(f"Task {tid} is already done, skipping")
                        continue
                        
                    # Claim ALL tasks if needed
                    if claim_all_task(task, username):
                        update = {
                            "executor": username,
                            "status": "Active",
                            "updated_at": time.time()
                        }
                        try:
                            requests.put(f"{SERVER_URL}/tasks/{tid}", json=update, timeout=5)
                            logger.info(f"Picked up ALL task {tid} as executor {username}")
                        except Exception as e:
                            logger.error(f"Failed to pick up ALL task {tid}: {e}")
                        continue  # Will execute on next poll as Active
                        
                    # Should this client execute?
                    if should_client_execute(task, username):
                        # Check if task is already being executed to prevent duplicates
                        if tid in executing_tasks:
                            logger.debug(f"Task {tid} is already being executed, skipping duplicate")
                            continue
                            
                        logger.info(f"Executing task {tid} assigned to {username}")
                        
                        # Mark task as executing before starting
                        executing_tasks.add(tid)
                        
                        try:
                            exec_status, result = execute_task(task, tid, username, SERVER_URL)
                            
                            if task.get("owner") == "ALL":
                                post_execution_result(SERVER_URL, tid, username, exec_status, result)
                            else:
                                update_task_status(SERVER_URL, tid, username, result)
                                
                            logger.info(f"Task {tid} execution completed: {exec_status}")
                        finally:
                            # Always remove from executing set when done
                            executing_tasks.discard(tid)
                    else:
                        logger.debug(f"Task {tid} not assigned to this client ({username})")
                        
            time.sleep(TASK_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Task execution polling failed: {e}")
            time.sleep(RETRY_DELAY)



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
    # Ensure a response is always returned
    return jsonify({"error": "Method not allowed"}), 405


def run():
    cache.set("login_time", time.time())
    # Wrap tasks to track their status
    scheduler.add_task(tracked_task(send_heartbeat, "send_heartbeat"), HEARTBEAT_INTERVAL)
    scheduler.add_task(tracked_task(check_plugin_updates, "check_plugin_updates"), 60)
    threading.Thread(target=handle_server_commands, daemon=True).start()
    threading.Thread(target=task_execution_loop, daemon=True).start()
    app.run(port=5001)  # Client UI/API

if __name__ == "__main__":
    run()
