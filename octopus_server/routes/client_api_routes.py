"""
🤖 CLIENT API ROUTES
===================

Flask routes for client API communication.

---
Terminology:
    - Client: The octopus_client service running on a user's PC. Each client is a unique agent instance that communicates with the Octopus server and executes commands/tasks on behalf of the user.
    - User: The human user of the PC and octopus_client. User-specific data (profile, preferences, etc.) is associated with this identity.

This distinction is important: 'client' refers to the agent/service and its machine, while 'user' refers to the person and their personalized data.
---
"""

import time
from flask import request, jsonify, render_template_string
from dbhelper import (
    get_tasks, add_task, update_task, delete_task,
    add_execution_result, get_db_file
)
from performance_monitor import time_request
import sqlite3
from global_cache_manager import get_global_cache_manager

def register_client_api_routes(app, cache, logger):
    """Register client API routes with the Flask app"""

    @app.route("/latest-task")
    def latest_task():
        """Get the latest scheduled task"""
        cache_manager = get_global_cache_manager()
        latest_task = cache_manager.get("latest_task")  # Should return a dict or None
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
        """Handle commands for specific hostname"""
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
        """Handle task operations"""
        if request.method == "POST":
            task = request.json
            task_id = add_task(task)
            return jsonify({"id": task_id})
        
        # Handle GET request - simple task listing
        all_tasks = get_tasks()
        return jsonify(all_tasks)

    @app.route("/tasks/<task_id>", methods=["PUT", "DELETE"])
    def task_ops(task_id):
        """Handle individual task operations"""
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

    @app.route("/client-tasks", methods=["GET"])
    def client_tasks():
        """Returns a list of tasks with pagination and status filtering."""
        # Get pagination parameters - default to 10 records per page
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Get status filter - default to empty string for "all status"
        status_filter = request.args.get('status', '').strip()
        
        all_tasks = list(get_tasks().values())
        
        # Apply status filter if specified (empty means "all status")
        if status_filter:
            all_tasks = [task for task in all_tasks if task.get('status', '').lower() == status_filter.lower()]
        
        total_count = len(all_tasks)
        
        # Sort by updated_at in descending order (most recent first)
        if all_tasks:
            all_tasks.sort(key=lambda x: x.get('updated_at', 0), reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_tasks = all_tasks[start_idx:end_idx]
        else:
            paginated_tasks = []
        
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        return jsonify({
            "tasks": paginated_tasks,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })

    @app.route("/client-executions", methods=["GET"])
    def client_executions():
        """Returns a list of executions with pagination and status filtering."""
        # Get pagination parameters - default to 10 records per page
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Get status filter - default to empty string for "all status"
        status_filter = request.args.get('status', '').strip()
        
        from dbhelper import DB_FILE
        
        db_file = DB_FILE
        executions = []
        total_count = 0
        
        with sqlite3.connect(db_file) as conn:
            # Build query with optional status filter
            if status_filter:
                count_query = "SELECT COUNT(*) FROM executions WHERE LOWER(status) = LOWER(?)"
                count_params = (status_filter,)
                
                data_query = """
                    SELECT id, task_id, client, status, result, updated_at 
                    FROM executions 
                    WHERE LOWER(status) = LOWER(?)
                    ORDER BY updated_at DESC 
                    LIMIT ? OFFSET ?
                """
            else:
                # No status filter - show all executions ("all status" default)
                count_query = "SELECT COUNT(*) FROM executions"
                count_params = ()
                
                data_query = """
                    SELECT id, task_id, client, status, result, updated_at 
                    FROM executions 
                    ORDER BY updated_at DESC 
                    LIMIT ? OFFSET ?
                """
            
            # Get total count
            count_cur = conn.execute(count_query, count_params)
            total_count = count_cur.fetchone()[0]
            
            # Calculate pagination
            offset = (page - 1) * per_page
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
            
            # Get paginated records
            if status_filter:
                data_params = (status_filter, per_page, offset)
            else:
                data_params = (per_page, offset)
                
            cur = conn.execute(data_query, data_params)
            
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
            "executions": executions,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })

    @app.route("/api/execution-results", methods=["POST"])
    def submit_execution_result():
        """
        Unauthenticated endpoint for clients to submit execution results.
        This endpoint specifically handles execution result submissions without requiring web session authentication.
        """
        try:
            # Handle both form data and JSON data
            if request.is_json:
                data = request.json or {}
            else:
                data = request.form.to_dict() or {}
            
            logger.info(f"Received execution result submission: {data}")
            
            # Extract required fields
            task_id = data.get("task_id")
            client = data.get("client") 
            status = data.get("exec_status") or data.get("status", "completed")
            result = data.get("exec_result") or data.get("result", "")
            
            # Validate required fields
            if not task_id or not client:
                logger.warning(f"Missing required fields in execution submission: task_id={task_id}, client={client}")
                return jsonify({"error": "Missing required fields: task_id and client"}), 400
            
            # Record the execution result
            logger.info(f"Recording execution result: task_id={task_id}, client={client}, status={status}")
            add_execution_result(task_id, client, status, result)
            
            logger.info(f"Successfully recorded execution result for task {task_id} from client {client}")
            return jsonify({"success": True, "message": "Execution result recorded successfully"})
            
        except Exception as e:
            logger.error(f"Error processing execution result submission: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": "Failed to record execution result"}), 500
