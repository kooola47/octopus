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
import inspect
import importlib
from typing import List
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
from performance_monitor import time_request, get_performance_report, monitor

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
@time_request("tasks")
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
    """Delete a task and redirect back to the dashboard with the appropriate tab."""
    try:
        delete_task(task_id)
        logger.info(f"Task {task_id} deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
    
    # Get the tab parameter, default to 'tasks'
    tab = request.args.get('tab', 'tasks')
    return redirect(url_for("dashboard", tab=tab))

@app.route("/client-tasks", methods=["GET"])
def client_tasks():
    """
    Returns a list of all tasks (for clients).
    """
    return jsonify(list(get_tasks().values()))

@app.route("/api/executions", methods=["GET"])
def api_executions():
    """
    Returns execution data for the dashboard with proper field names.
    """
    import sqlite3

    def get_db_file():
        return DB_FILE

    db_file = get_db_file()
    executions = []
    try:
        with sqlite3.connect(db_file) as conn:
            cur = conn.execute("SELECT id, task_id, client, status, result, updated_at FROM executions ORDER BY updated_at DESC")
            for row in cur.fetchall():
                executions.append({
                    "id": row[0],
                    "task_id": row[1],
                    "client": row[2],
                    "exec_status": row[3],  # Match the frontend field name
                    "exec_result": row[4],  # Match the frontend field name
                    "updated_at": row[5],
                })
    except sqlite3.Error as e:
        logger.error(f"Database error in api_executions: {e}")
        return jsonify([])  # Return empty list on error
    
    return jsonify(executions)

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

@app.route("/api/plugin-functions", methods=["GET"])
def api_plugin_functions():
    """
    API endpoint to get function signatures for plugins
    """
    plugin_name = request.args.get('plugin')
    if not plugin_name:
        return jsonify({"error": "Plugin parameter required"}), 400
    
    try:
        # Import the plugin module
        module = importlib.import_module(f"plugins.{plugin_name}")
        
        # Get all callable functions from the module
        functions = {}
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            # Skip private functions
            if name.startswith('_'):
                continue
                
            try:
                # Get function signature
                sig = inspect.signature(obj)
                parameters = {}
                
                for param_name, param in sig.parameters.items():
                    param_info = {
                        "name": param_name,
                        "required": param.default == inspect.Parameter.empty,
                        "type": "str"  # Default type
                    }
                    
                    # Try to get type hints
                    if param.annotation != inspect.Parameter.empty:
                        param_info["type"] = getattr(param.annotation, '__name__', str(param.annotation))
                    
                    # Get default value
                    if param.default != inspect.Parameter.empty:
                        param_info["default"] = param.default
                    
                    parameters[param_name] = param_info
                
                functions[name] = {
                    "parameters": parameters,
                    "docstring": inspect.getdoc(obj) or "No description available"
                }
                
            except Exception as e:
                logger.warning(f"Could not inspect function {name}: {e}")
                functions[name] = {
                    "parameters": {},
                    "docstring": "Function signature could not be determined"
                }
        
        return jsonify({"functions": functions})
        
    except ImportError:
        return jsonify({"error": f"Plugin '{plugin_name}' not found"}), 404
    except Exception as e:
        logger.error(f"Error inspecting plugin {plugin_name}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/nlp-parse", methods=["POST"])
@time_request("nlp-parse")
def api_nlp_parse():
    """
    API endpoint to parse natural language and convert to task definition
    """
    try:
        from nlp_processor import get_nlp_processor
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Text parameter required"}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Get NLP processor instance
        nlp_processor = get_nlp_processor()
        
        if not nlp_processor.is_available():
            return jsonify({
                "error": "NLP processor not available. Install spaCy with: pip install spacy && python -m spacy download en_core_web_sm"
            }), 503
        
        # Parse the natural language input
        result = nlp_processor.parse_natural_language(text)
        
        if not result.get("success"):
            return jsonify(result), 400
        
        logger.info(f"NLP parsed '{text}' with confidence {result.get('confidence', 0):.2f}")
        return jsonify(result)
        
    except ImportError:
        return jsonify({
            "error": "NLP processor module not found. Ensure nlp_processor.py is present."
        }), 500
    except Exception as e:
        logger.error(f"Error in NLP parsing: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/nlp-test")
def nlp_test_page():
    """
    NLP test page for natural language task creation
    """
    return render_template("nlp_test.html")

@app.route("/confidence-guide")
def confidence_guide():
    """
    Guide for improving NLP confidence levels
    """
    return render_template("confidence_guide.html")

@app.route("/api/performance", methods=["GET"])
def api_performance():
    """
    API endpoint to get performance statistics
    """
    return jsonify(monitor.get_stats())

@app.route("/performance-report")
def performance_report():
    """
    Human-readable performance report
    """
    report = get_performance_report()
    return f"<pre>{report}</pre>"

@app.route("/api/plugin-examples", methods=["GET"])
def api_plugin_examples():
    """
    API endpoint to get dynamic examples based on available plugins
    """
    try:
        from nlp_processor import get_nlp_processor
        
        # Get NLP processor to access plugin metadata
        nlp_processor = get_nlp_processor()
        
        examples = []
        plugin_names = get_plugin_names()
        
        for plugin_name in plugin_names:
            try:
                # Get plugin metadata if available
                if plugin_name in nlp_processor.plugin_metadata:
                    metadata = nlp_processor.plugin_metadata[plugin_name]
                    
                    # Use examples from plugin comments
                    for example in metadata.get('examples', []):
                        examples.append({
                            "text": example,
                            "plugin": plugin_name,
                            "description": metadata.get('description', '').split('\n')[0],  # First line
                            "category": _get_plugin_category(plugin_name)
                        })
                
                # If no metadata examples, create default ones
                if plugin_name not in nlp_processor.plugin_metadata or not nlp_processor.plugin_metadata[plugin_name].get('examples'):
                    default_examples = _get_default_examples(plugin_name)
                    for example in default_examples:
                        examples.append({
                            "text": example,
                            "plugin": plugin_name,
                            "description": f"Execute {plugin_name} plugin",
                            "category": _get_plugin_category(plugin_name)
                        })
                        
            except Exception as e:
                logger.warning(f"Could not load examples for plugin {plugin_name}: {e}")
        
        # Add some generic enhanced examples with shortcuts
        enhanced_examples = [
            {
                "text": "backup prod db to backup dir tonight",
                "plugin": "backup_database",
                "description": "Uses shortcuts: prod db → production database, backup dir → /backup, tonight → at 11 PM",
                "category": "database"
            },
            {
                "text": "create urgent incident for api server down",
                "plugin": "create_incident", 
                "description": "High priority incident with server specification",
                "category": "incident"
            },
            {
                "text": "send email to ops about system maintenance morning",
                "plugin": "send_email",
                "description": "Email notification with time shortcut: morning → at 9 AM",
                "category": "notification"
            }
        ]
        
        examples.extend(enhanced_examples)
        
        # Group examples by category for better organization
        categorized = {}
        for example in examples:
            category = example.get('category', 'other')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(example)
        
        return jsonify({
            "success": True,
            "examples": examples,
            "categorized": categorized,
            "total_plugins": len(plugin_names)
        })
        
    except Exception as e:
        logger.error(f"Error getting plugin examples: {e}")
        return jsonify({"error": "Failed to load plugin examples"}), 500

def _get_plugin_category(plugin_name: str) -> str:
    """Categorize plugin for better organization"""
    categories = {
        'create_incident': 'incident',
        'send_email': 'notification', 
        'backup_database': 'database',
        'cleanup_logs': 'maintenance',
        'generate_report': 'reporting',
        'monitor_system': 'monitoring'
    }
    return categories.get(plugin_name, 'other')

def _get_default_examples(plugin_name: str) -> List[str]:
    """Generate default examples for plugins without metadata"""
    defaults = {
        'create_incident': [
            f"create P1 incident for system failure",
            f"report critical issue with {plugin_name}"
        ],
        'send_email': [
            f"send email to admin about server status",
            f"notify team about maintenance window"
        ],
        'backup_database': [
            f"backup production database daily",
            f"create database backup now"
        ],
        'cleanup_logs': [
            f"cleanup old log files from /var/log",
            f"remove logs older than 30 days"
        ],
        'generate_report': [
            f"generate monthly system report",
            f"create performance analysis"
        ],
        'monitor_system': [
            f"monitor system health hourly",
            f"check server performance"
        ]
    }
    
    return defaults.get(plugin_name, [f"run {plugin_name} with default parameters"])

@app.route("/api/reload-plugins", methods=["POST"])
@time_request("reload-plugins")
def reload_plugins():
    """Reload plugin metadata for NLP processing"""
    try:
        from nlp_processor import get_nlp_processor
        
        nlp_processor = get_nlp_processor()
        nlp_processor.reload_plugin_metadata()
        
        # Get updated plugin count
        plugin_count = len(nlp_processor.plugin_metadata)
        
        return jsonify({
            "success": True,
            "message": "Plugin metadata reloaded successfully",
            "plugins_loaded": plugin_count,
            "plugins": list(nlp_processor.plugin_metadata.keys())
        })
        
    except ImportError:
        return jsonify({
            "error": "NLP processor module not found"
        }), 500
    except Exception as e:
        logger.error(f"Error reloading plugins: {e}")
        return jsonify({"error": "Failed to reload plugin metadata"}), 500

if __name__ == "__main__":
    # Enable threading for concurrent request handling
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, debug=False)
