"""
🏠 WEB DASHBOARD ROUTES
======================

Flask routes for the web dashboard interface.
"""

import json
import urllib.parse
import sqlite3
import time
from flask import request, render_template, redirect, url_for, render_template_string, flash
from dbhelper import (
    get_tasks, add_task, update_task, delete_task,
    get_owner_options, assign_all_tasks,
    compute_task_status, get_active_clients, get_db_file,
    get_plugin_names, add_execution_result
)
from performance_monitor import get_performance_report
from .auth_routes import login_required

def register_dashboard_routes(app, global_cache, logger):
    """Register dashboard routes with the Flask app"""

    @app.route("/dashboard", methods=["GET", "POST"])
    @login_required
    def dashboard():
        """Main web dashboard interface"""
        # Add debugging for NLP task creation
        logger.info("Dashboard route called with args: %s", request.args)
        
        # Parse NLP task data from URL parameters
        nlp_task_data = None
        edit_mode = False
        
        create_task_param = request.args.get('createTask')
        edit_task_param = request.args.get('editTask')
        
        if create_task_param:
            try:
                nlp_task_data = json.loads(urllib.parse.unquote(create_task_param))
                logger.info("Parsed createTask data: %s", nlp_task_data)
            except Exception as e:
                logger.error("Failed to parse createTask parameter: %s", e)
        
        if edit_task_param:
            try:
                nlp_task_data = json.loads(urllib.parse.unquote(edit_task_param))
                edit_mode = True
                logger.info("Parsed editTask data: %s", nlp_task_data)
            except Exception as e:
                logger.error("Failed to parse editTask parameter: %s", e)
        
        # Auto-create task if createTask parameter is provided
        if nlp_task_data and not edit_mode:
            try:
                # Validate plugin name from NLP data
                plugin_name = nlp_task_data.get("plugin", "").strip()
                if not plugin_name:
                    flash("NLP task creation failed: No plugin specified", "error")
                    return redirect(url_for("dashboard", tab="tasks"))
                
                # Create task from NLP data
                task = {
                    "owner": nlp_task_data.get("owner", "Anyone"),
                    "plugin": plugin_name,
                    "action": nlp_task_data.get("action", "main"),
                    "args": json.dumps(nlp_task_data.get("args", [])),
                    "kwargs": json.dumps(nlp_task_data.get("kwargs", {})),
                    "type": nlp_task_data.get("type", "Adhoc"),
                    "execution_start_time": nlp_task_data.get("execution_start_time"),
                    "execution_end_time": nlp_task_data.get("execution_end_time"),
                    "interval": nlp_task_data.get("interval"),
                    "executor": "" if nlp_task_data.get("owner") == "Anyone" else None
                }
                task_id = add_task(task)
                logger.info("Auto-created NLP task with ID: %s", task_id)
                
                # Redirect to clear the URL parameters and show the created task
                tab = request.args.get('tab', 'tasks')
                return redirect(url_for("dashboard", tab=tab))
                
            except Exception as e:
                logger.error("Failed to auto-create NLP task: %s", e)
        
        # For edit mode, keep the nlp_task_data to pass to template for modal opening
        logger.info("Template variables - nlp_task_data: %s, edit_mode: %s", nlp_task_data, edit_mode)
        tasks = get_tasks()
        clients = global_cache.get('clients', 'startup', None, {})
        now = time.time()
        active_clients = get_active_clients(clients, now=now, timeout=60)  # Align with "online" status
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
                execution_id = form.get("execution_id")
                status = form.get("exec_status")
                result = form.get("exec_result")
                if execution_id:
                    with sqlite3.connect(db_file) as conn:
                        conn.execute(
                            "UPDATE executions SET status=?, result=?, updated_at=? WHERE execution_id=?",
                            (status, result, time.time(), execution_id)
                        )
                        conn.commit()
                        logger.info(f"Updated execution {execution_id}")
                else:
                    logger.warning("No execution_id provided for edit_execution")
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
                
                # Validate plugin name
                if not plugin or not plugin.strip():
                    flash("Task creation failed: Plugin name is required", "error")
                    active_tab = "tasks"
                    return redirect(url_for("dashboard", tab=active_tab))
                
                plugin = plugin.strip()
                
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
        
        # Get pagination parameters - default to 10 records per page
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Initialize default values for variables used in logging
        tasks_total_count = 0
        executions_total_count = 0
        
        # For tabs that use client-side pagination, don't load data server-side
        # This prevents conflicts between server-side and client-side data loading
        if active_tab in ["tasks"]:
            # Let client-side pagination handle the data loading for tasks
            executions = []
            tasks = {}
        elif active_tab == "executions":
            # For executions tab, load server-side data to ensure it displays properly
            db_file = get_db_file()
            executions = []
            executions_total_count = 0
            tasks = {}  # Don't need tasks data for executions tab
            
            with sqlite3.connect(db_file) as conn:
                # First, get total count of executions
                executions_total_count = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
                logger.info(f"Dashboard: Total executions in database: {executions_total_count}")
                
                # Get executions with pagination (limit to first 10 for initial load)
                offset = (page - 1) * per_page
                cursor = conn.execute("""
                    SELECT id, task_id, client, status, result, updated_at
                    FROM executions
                    ORDER BY updated_at DESC
                    LIMIT ? OFFSET ?
                """, (per_page, offset))
                
                executions_raw = cursor.fetchall()
                logger.info(f"Dashboard: Found {len(executions_raw)} executions for template")
                
                executions = []
                for row in executions_raw:
                    execution = {
                        'id': row[0],
                        'task_id': row[1],
                        'client': row[2],
                        'status': row[3],
                        'result': row[4],
                        'updated_at': row[5]
                    }
                    executions.append(execution)
                    if len(executions) == 1:  # Log first execution as sample
                        logger.info(f"Sample execution: {execution}")
        else:
            # Get executions data with pagination
            
            db_file = get_db_file()
            executions = []
            executions_total_count = 0
            
            with sqlite3.connect(db_file) as conn:
                # First, get total count of executions
                executions_total_count = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
                logger.info(f"Dashboard: Total executions in database: {executions_total_count}")
                
                # Calculate pagination for executions
                offset = (page - 1) * per_page
                
                # Get paginated executions sorted by updated_at DESC
                cur = conn.execute("""
                    SELECT id, task_id, client, status, result, updated_at 
                    FROM executions 
                    ORDER BY updated_at DESC 
                    LIMIT ? OFFSET ?
                """, (per_page, offset))
                
                for row in cur.fetchall():
                    executions.append({
                        "id": row[0],
                        "task_id": row[1],
                        "client": row[2],
                        "status": row[3],
                        "result": row[4],
                        "updated_at": row[5],
                    })
            
            logger.info(f"Dashboard: Showing page {page} with {len(executions)} executions (of {executions_total_count} total)")
            if executions:
                logger.info(f"Sample execution: {executions[0]}")
            
            # Apply pagination to tasks
            tasks_list = list(tasks.values()) if tasks else []
            tasks_total_count = len(tasks_list)
            
            if tasks_list:
                tasks_list.sort(key=lambda x: x.get('updated_at', 0), reverse=True)
                # Apply pagination for tasks
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                tasks_list = tasks_list[start_idx:end_idx]
                # Convert back to dict format for template compatibility
                tasks = {task.get('id', i): task for i, task in enumerate(tasks_list)}
        
        logger.info(f"Dashboard: Showing page {page} with {len(tasks)} tasks (of {tasks_total_count} total)")
        
        # Handle NLP task creation/editing parameters
        nlp_task_data = None
        edit_mode = False
        
        create_task_param = request.args.get("createTask")
        if create_task_param:
            try:
                nlp_task_data = json.loads(urllib.parse.unquote(create_task_param))
                edit_mode = False
                logger.info(f"Parsed createTask data: {nlp_task_data}")
            except Exception as e:
                logger.error(f"Error parsing createTask data: {e}")
        
        edit_task_param = request.args.get("editTask")
        if edit_task_param:
            try:
                nlp_task_data = json.loads(urllib.parse.unquote(edit_task_param))
                edit_mode = True
                logger.info(f"Parsed editTask data: {nlp_task_data}")
            except Exception as e:
                logger.error(f"Error parsing editTask data: {e}")
        
        logger.info(f"Dashboard rendering with nlp_task_data: {nlp_task_data}, edit_mode: {edit_mode}")
        
        # Calculate pagination info for executions
        if active_tab == "executions":
            total_pages = (executions_total_count + per_page - 1) // per_page  # Ceiling division
            pagination_info = {
                'page': page,
                'per_page': per_page,
                'total_count': executions_total_count,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
        else:
            pagination_info = None
        
        # Get simple dashboard stats (safely handle different data types)
        stats = {
            'active_tasks': len(tasks) if tasks else 0,
            'completed_tasks': 0,  # We'll calculate this safely
            'online_clients': len(active_clients),
            'total_executions': len(executions)
        }
        
        # Safely count completed tasks
        try:
            if tasks:
                if isinstance(tasks, dict):
                    # If tasks is a dict, count values with completed status
                    stats['completed_tasks'] = len([t for t in tasks.values() if isinstance(t, dict) and t.get('status') == 'completed'])
                    stats['active_tasks'] = len([t for t in tasks.values() if isinstance(t, dict) and t.get('status') != 'completed'])
                elif isinstance(tasks, list):
                    # If tasks is a list, check each item
                    completed = 0
                    active = 0
                    for t in tasks:
                        if isinstance(t, dict):
                            if t.get('status') == 'completed':
                                completed += 1
                            else:
                                active += 1
                        else:
                            active += 1  # Assume non-dict tasks are active
                    stats['completed_tasks'] = completed
                    stats['active_tasks'] = active
        except Exception as e:
            logger.error(f"Error calculating task stats: {e}")
            # Keep the default values
        
        return render_template(
            "modern_dashboard.html",
            stats=stats,
            recent_executions=executions[:10] if executions else [],
            tasks=tasks,
            clients=active_clients,
            executions=executions
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

    @app.route("/nlp-test")
    def nlp_test_page():
        """NLP test page for natural language task creation"""
        return render_template("nlp_test.html")

    @app.route("/confidence-guide")
    def confidence_guide():
        """Guide for improving NLP confidence levels"""
        return render_template("confidence_guide.html")

    @app.route("/performance-report")
    def performance_report():
        """Human-readable performance report"""
        report = get_performance_report()
        return f"<pre>{report}</pre>"
