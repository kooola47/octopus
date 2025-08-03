from flask import Flask
from cache import Cache
from config import SERVER_HOST, SERVER_PORT
import os
import logging
from flask import request, jsonify
from dashboard_template import DASHBOARD_TEMPLATE
from taskmanager import get_tasks, add_task, update_task, delete_task

from pluginhelper import register_plugin_routes
from heartbeat import register_heartbeat_routes
from flask import render_template_string, redirect, url_for

app = Flask(__name__)
cache = Cache()

# Setup logs folder and logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("logs/server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("octopus_server")

register_heartbeat_routes(app, cache, logger)
register_plugin_routes(app, logger)

@app.route("/latest-task")
def latest_task():
    # Example: Replace with your actual cache/task retrieval logic
    latest_task = cache.get("latest_task")  # Should return a dict or None
    if not latest_task:
        return render_template_string("""
            <h2>No scheduled tasks found.</h2>
        """)
    return render_template_string("""
        <h2>Latest Scheduled Task</h2>
        <ul>
            <li><strong>Task Name:</strong> {{ task['name'] }}</li>
            <li><strong>Scheduled Time:</strong> {{ task['scheduled_time'] }}</li>
            <li><strong>Status:</strong> {{ task['status'] }}</li>
            <li><strong>Last Execution:</strong> {{ task['last_execution'] }}</li>
        </ul>
    """, task=latest_task)

# In-memory command queue for demonstration
COMMANDS = {}

@app.route("/commands/<hostname>", methods=["GET", "POST"])
def commands(hostname):
    if request.method == "POST":
        cmd = request.json
        COMMANDS.setdefault(hostname, []).append(cmd)
        return {"status": "queued"}
    else:
        cmds = COMMANDS.pop(hostname, [])
        return jsonify(cmds)

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

import glob

def get_plugin_names():
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    plugins = []
    for f in glob.glob(os.path.join(plugin_dir, "*.py")):
        name = os.path.splitext(os.path.basename(f))[0]
        if not name.startswith("__"):
            plugins.append(name)
    return plugins

def get_owner_options(clients):
    owners = ["ALL", "Anyone"]
    # Fix: Use the latest usernames from heartbeat (which now include PID)
    owners.extend(sorted({str(client['username']) for client in clients.values() if 'username' in client}))
    return owners

@app.template_filter('datetimeformat')
def datetimeformat_filter(value):
    import datetime
    try:
        return datetime.datetime.fromtimestamp(float(value)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return value

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

def assign_anyone_task(tasks, clients):
    """
    Assigns unassigned 'Anyone' tasks to a random available client (by username).
    Only assigns if executor is empty and client is online.
    """
    import random
    # Fix: Use the latest usernames from heartbeat (which now include PID)
    available_users = [str(client['username']) for client in clients.values() if 'username' in client]
    for tid, task in tasks.items():
        # Only assign if executor is empty and status is not 'success' or 'failed'
        if task.get("owner") == "Anyone" and (not task.get("executor")) and task.get("status") not in ("success", "failed"):
            if available_users:
                chosen = random.choice(available_users)
                task["executor"] = chosen
                update_task(tid, {"executor": chosen})

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    import time
    tasks = get_tasks()
    clients = cache.all()
    now = time.time()
    plugin_names = get_plugin_names()
    owner_options = get_owner_options(clients)
    # Assign 'Anyone' tasks to available clients if not already assigned and not completed
    assign_anyone_task(tasks, clients)
    if request.method == "POST":
        form = request.form
        task_id = form.get("id") or None
        task_type = form.get("type", "Adhoc")
        owner = form.get("owner")
        plugin = form.get("plugin")
        # If manual input was used, prefer that value
        if owner == "__manual__":
            owner = form.get("owner", "")
        if plugin == "__manual__":
            plugin = form.get("plugin", "")
        task = {
            "id": task_id,
            "owner": owner,
            "plugin": plugin,
            "action": form.get("action", "run"),
            "args": form.get("args", "[]"),
            "kwargs": form.get("kwargs", "{}"),
            "type": task_type,
            "execution_start_time": form.get("execution_start_time"),
            "execution_end_time": form.get("execution_end_time"),
            "interval": form.get("interval"),
            # Ensure executor is cleared if owner is changed to Anyone
            "executor": "" if owner == "Anyone" else None
        }
        if task_id and task_id in tasks:
            update_task(task_id, task)
        else:
            add_task(task)
        return redirect(url_for("dashboard"))
    return render_template_string(
        DASHBOARD_TEMPLATE,
        tasks=tasks,
        clients=clients,
        now=now,
        plugin_names=plugin_names,
        owner_options=owner_options
    )

@app.route("/tasks-ui/delete/<task_id>")
def delete_task_ui(task_id):
    delete_task(task_id)
    return redirect(url_for("dashboard"))
# ...add more endpoints here if needed...

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
