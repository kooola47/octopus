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
from flask import request, jsonify
from dbhelper import (
    get_tasks, add_task, update_task, delete_task,
    get_owner_options, assign_anyone_task, assign_all_tasks,
    compute_task_status, get_active_clients, get_db_file,
    get_plugin_names, add_execution_result
)
from pluginhelper import register_plugin_routes
from heartbeat import register_heartbeat_routes
from flask import render_template, redirect, url_for, render_template_string
import sqlite3
from sqlite_web import sqlite_web
from datetime import datetime

# Set template_folder to a "templates" directory for best practice
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)
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
logger = logging.getLogger("octopus_server")

# Initialize database
from dbhelper import init_db
init_db()

# Register routes from other modules
register_heartbeat_routes(app, cache, logger)
register_plugin_routes(app, logger)

# Log server startup information
logger.info(f"Octopus Server starting on {SERVER_HOST}:{SERVER_PORT}")
logger.info(f"Database: {DB_FILE}")
logger.info(f"Plugins folder: {PLUGINS_FOLDER}")
logger.info(f"Template folder: {TEMPLATE_DIR}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

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
    
    # Handle GET request with optional filtering
    exclude_finished = request.args.get('exclude_finished', 'false').lower() == 'true'
    all_tasks = get_tasks()
    
    logger.info(f"Tasks endpoint called. exclude_finished={exclude_finished}, total_tasks={len(all_tasks) if isinstance(all_tasks, (dict, list)) else 'unknown'}")
    
    if exclude_finished:
        # Filter out finished tasks - be more comprehensive with status checking
        finished_statuses = ['Done', 'done', 'Failed', 'failed', 'error', 'Error', 'Completed', 'completed', 'success', 'Success']
        
        if isinstance(all_tasks, dict):
            original_count = len(all_tasks)
            filtered_tasks = {}
            for task_id, task in all_tasks.items():
                task_status = task.get('status', '')
                logger.debug(f"Task {task_id}: status='{task_status}', finished={task_status in finished_statuses}")
                if task_status not in finished_statuses:
                    filtered_tasks[task_id] = task
                else:
                    logger.debug(f"Filtering out finished task {task_id} with status '{task_status}'")
            logger.info(f"Filtered tasks: {original_count} -> {len(filtered_tasks)} (removed {original_count - len(filtered_tasks)} finished tasks)")
            return jsonify(filtered_tasks)
        elif isinstance(all_tasks, list):
            original_count = len(all_tasks)
            filtered_tasks = []
            for task in all_tasks:
                task_status = task.get('status', '')
                task_id = task.get('id', 'unknown')
                logger.debug(f"Task {task_id}: status='{task_status}', finished={task_status in finished_statuses}")
                if task_status not in finished_statuses:
                    filtered_tasks.append(task)
                else:
                    logger.debug(f"Filtering out finished task {task_id} with status '{task_status}'")
            logger.info(f"Filtered tasks: {original_count} -> {len(filtered_tasks)} (removed {original_count - len(filtered_tasks)} finished tasks)")
            return jsonify(filtered_tasks)
    
    logger.info(f"Returning all {len(all_tasks) if isinstance(all_tasks, (dict, list)) else 'unknown'} tasks (no filtering)")
    return jsonify(all_tasks)


@app.route("/tasks/<task_id>", methods=["PUT", "DELETE"])
def task_ops(task_id):
    if request.method == "PUT":
        updates = request.json or {}
        logger.info(f"Updating task {task_id} with: {updates}")
        
        # If this is an execution result (has result field), record it separately
        if "result" in updates and updates.get("executor"):
            add_execution_result(
                task_id, 
                updates.get("executor"), 
                updates.get("status", "completed"),
                updates.get("result", "")
            )
        
        ok = update_task(task_id, updates)
        logger.info(f"Task {task_id} update result: {ok}")
        return jsonify({"success": ok})
    elif request.method == "DELETE":
        ok = delete_task(task_id)
        return jsonify({"success": ok})
    # Ensure a response is always returned
    return jsonify({"error": "Method not allowed"}), 405

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

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    import time
    tasks = get_tasks()
    clients = cache.all()
    now = time.time()
    active_clients = get_active_clients(clients, now=now, timeout=30)
    plugin_names = get_plugin_names()
    owner_options = get_owner_options(active_clients)
    
    # Use the comprehensive task assignment function
    assign_all_tasks(tasks, active_clients)
    
    # Update task statuses after assignment, but don't override completed tasks
    for tid, task in tasks.items():
        db_status = task.get("status", "")
        # Only compute status if the task isn't already Done/completed
        if db_status not in ("Done", "success", "failed", "completed"):
            computed_status = compute_task_status(task, active_clients)
            task["status"] = computed_status
        # Keep the database status for completed tasks
    
    active_tab = "clients"
    if request.method == "POST":
        form = request.form
        db_file = get_db_file()
        if form.get("add_execution"):
            task_id = form.get("task_id")
            client = form.get("client")
            status = form.get("exec_status")
            result = form.get("exec_result")
            logger.info(f"Adding execution via dashboard: task_id={task_id}, client={client}, status={status}")
            add_execution_result(task_id, client, status, result)
            active_tab = "executions"
            return redirect(url_for("dashboard", tab=active_tab))
        elif form.get("edit_execution"):
            task_id = form.get("task_id")
            client = form.get("client")
            status = form.get("exec_status")
            result = form.get("exec_result")
            with sqlite3.connect(db_file) as conn:
                conn.execute(
                    "UPDATE executions SET status=?, result=?, updated_at=? WHERE task_id=? AND client=?",
                    (status, result, time.time(), task_id, client)
                )
                conn.commit()
            active_tab = "tasks"
            return redirect(url_for("dashboard", tab=active_tab))
        else:
            task_id = form.get("id") or None
            task_type = form.get("type", "Adhoc")
            owner = form.get("owner")
            plugin = form.get("plugin")
            if owner == "__manual__":
                owner = form.get("owner", "")
            if plugin == "__manual__":
                plugin = form.get("plugin", "")
            interval = form.get("interval")
            if interval:
                try:
                    interval = int(interval)
                except Exception:
                    interval = None
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
                "interval": interval,
                "executor": "" if owner == "Anyone" else None
            }
            if task_id and task_id in tasks:
                update_task(task_id, task)
            else:
                add_task(task)
            active_tab = "tasks"
            return redirect(url_for("dashboard", tab=active_tab))
    active_tab = request.args.get("tab", active_tab)
    
    # Get executions data
    db_file = get_db_file()
    executions = []
    with sqlite3.connect(db_file) as conn:
        # First, let's count total executions
        total_count = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
        logger.info(f"Dashboard: Total executions in database: {total_count}")
        
        cur = conn.execute("SELECT id, task_id, client, status, result, updated_at FROM executions ORDER BY updated_at DESC")
        for row in cur.fetchall():
            executions.append({
                "id": row[0],
                "task_id": row[1],
                "client": row[2],
                "status": row[3],
                "result": row[4],
                "updated_at": row[5],
            })
    
    logger.info(f"Dashboard: Found {len(executions)} executions for template")
    if executions:
        logger.info(f"Sample execution: {executions[0]}")
    
    return render_template(
        "dashboard_template.html",
        tasks=tasks,
        clients=active_clients,
        executions=executions,
        now=now,
        plugin_names=plugin_names,
        owner_options=owner_options,
        active_tab=active_tab
    )

@app.route("/tasks-ui/delete/<task_id>")
def delete_task_ui(task_id):
    delete_task(task_id)
    return redirect(url_for("dashboard", tab="tasks"))

@app.route("/client-tasks", methods=["GET"])
def client_tasks():
    """
    Returns a list of all tasks (for clients).
    """
    return jsonify(list(get_tasks().values()))

@app.route("/client-executions", methods=["GET"])
def client_executions():
    """
    Returns a flat list of all executions with task_id and client.
    """
    import sqlite3

    def get_db_file():
        return DB_FILE

    db_file = get_db_file()
    executions = []
    with sqlite3.connect(db_file) as conn:
        cur = conn.execute("SELECT id, task_id, client, status, result, updated_at FROM executions")
        for row in cur.fetchall():
            executions.append({
                "id": row[0],
                "task_id": row[1],
                "client": row[2],
                "status": row[3],
                "result": row[4],
                "updated_at": row[5],
            })
    return jsonify(executions)

@app.route("/api/test-executions", methods=["GET"])
def api_test_executions():
    """Test endpoint to create sample execution data"""
    try:
        import uuid
        import time
        
        # Create some test execution data
        test_executions = [
            {
                'task_id': str(uuid.uuid4()),
                'client': 'test-client-1',
                'status': 'success',
                'result': 'Task completed successfully',
                'updated_at': time.time()
            },
            {
                'task_id': str(uuid.uuid4()),
                'client': 'test-client-2', 
                'status': 'failed',
                'result': 'Task failed with error',
                'updated_at': time.time() - 300
            }
        ]
        
        # Insert test data into database
        db_file = get_db_file()
        with sqlite3.connect(db_file) as conn:
            for exec_data in test_executions:
                conn.execute("""
                    INSERT OR REPLACE INTO executions (task_id, client, status, result, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (exec_data['task_id'], exec_data['client'], exec_data['status'], 
                     exec_data['result'], exec_data['updated_at']))
            conn.commit()
            
        return jsonify({"message": "Test executions created", "count": len(test_executions)})
        
    except Exception as e:
        logging.error(f"Error creating test executions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/dashboard-data", methods=["GET"])
def api_dashboard_data():
    """
    API endpoint to get fresh dashboard data for AJAX updates
    """
    import time
    tasks = get_tasks()
    clients = cache.all()
    now = time.time()
    active_clients = get_active_clients(clients, now=now, timeout=30)
    
    # Use the comprehensive task assignment function
    assign_all_tasks(tasks, active_clients)
    
    # Update task statuses after assignment, but don't override completed tasks
    for tid, task in tasks.items():
        db_status = task.get("status", "")
        # Only compute status if the task isn't already Done/completed
        if db_status not in ("Done", "success", "failed", "completed"):
            computed_status = compute_task_status(task, active_clients)
            task["status"] = computed_status
    
    # Get executions data
    db_file = get_db_file()
    executions = []
    with sqlite3.connect(db_file) as conn:
        cur = conn.execute("SELECT id, task_id, client, status, result, updated_at FROM executions")
        for row in cur.fetchall():
            executions.append({
                "id": row[0],
                "task_id": row[1],
                "client": row[2],
                "status": row[3],
                "result": row[4],
                "updated_at": row[5],
            })
    
    return jsonify({
        "tasks": tasks,
        "clients": active_clients,
        "executions": executions,
        "now": now,
        "timestamp": time.time()
    })

# ...existing code...
if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
