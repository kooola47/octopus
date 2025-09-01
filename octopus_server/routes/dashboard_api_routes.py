"""
📊 DASHBOARD API ROUTES
======================

Flask routes for dashboard data APIs.
"""

import time
import sqlite3
import logging
from flask import jsonify, request
from dbhelper import (
    get_tasks, get_active_clients, assign_all_tasks,
    compute_task_status, get_db_file, DB_FILE
)

def register_dashboard_api_routes(app, global_cache, logger):
    """Register dashboard API routes with the Flask app"""

    @app.route("/api/clients", methods=["GET"])
    def api_clients():
        """API endpoint to get client data for statistics dashboard"""
        clients = global_cache.all()
        now = time.time()
        active_clients = get_active_clients(clients, now=now, timeout=60)  # Align with "online" status
        
        return jsonify({
            "clients": active_clients,
            "now": now,
            "timestamp": time.time()
        })

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks():
        """API endpoint to get task data for statistics dashboard with pagination and status filtering"""
        # Get pagination parameters - default to 10 records per page
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Get status filter - default to empty string for "all status"
        status_filter = request.args.get('status', '').strip()
        
        tasks = get_tasks()
        clients = global_cache.all()
        now = time.time()
        active_clients = get_active_clients(clients, now=now, timeout=60)  # Align with "online" status
        
        # Use centralized assignment service with fallback
        try:
            from services.task_assignment_service import get_assignment_service
            assignment_service = get_assignment_service(global_cache)
            assignment_result = assignment_service.assign_pending_tasks()
            logger.info(f"Task assignment result: {assignment_result}")
        except Exception as e:
            logger.error(f"Assignment service failed, using direct assignment: {e}")
            assign_all_tasks(tasks, active_clients)
        
        # Refresh tasks after assignment
        tasks = get_tasks()
        
        # Update task statuses after assignment, but don't override completed tasks
        for tid, task in tasks.items():
            db_status = task.get("status", "")
            # Only compute status if the task isn't already Done/completed
            if db_status not in ("Done", "success", "failed", "completed"):
                computed_status = compute_task_status(task, active_clients)
                task["status"] = computed_status
        
        # Convert tasks dict to list
        tasks_list = list(tasks.values()) if tasks else []
        
        # Apply status filter if specified (empty means "all status")
        if status_filter:
            tasks_list = [task for task in tasks_list if task.get('status', '').lower() == status_filter.lower()]
        
        total_count = len(tasks_list)
        
        # Sort by updated_at in descending order (most recent first)
        if tasks_list:
            tasks_list.sort(key=lambda x: x.get('updated_at', 0), reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_tasks = tasks_list[start_idx:end_idx]
        else:
            paginated_tasks = []
        
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        # Format tasks as a dictionary with proper IDs (matching original dashboard format)
        tasks_dict = {}
        for i, task in enumerate(paginated_tasks):
            task_id = task.get('id', f"task_{i}")
            tasks_dict[task_id] = task
        
        return jsonify({
            "tasks": tasks_dict,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "now": now,
            "timestamp": time.time()
        })

    @app.route("/api/executions", methods=["GET"])
    def api_executions():
        """Returns execution data for the dashboard with pagination and comprehensive server-side filtering."""
        logger.info(f"API /api/executions called with args: {request.args}")
        
        # Get pagination parameters - default to 10 records per page
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Get all filter parameters
        status_filter = request.args.get('status', '').strip()
        client_filter = request.args.get('client', '').strip()
        task_id_filter = request.args.get('task_id', '').strip()
        result_filter = request.args.get('result', '').strip()
        execution_id_filter = request.args.get('execution_id', '').strip()
        search_filter = request.args.get('search', '').strip()  # Global search
        
        logger.info(f"Executions API: page={page}, per_page={per_page}, status_filter='{status_filter}'")
        logger.info(f"Filters: client='{client_filter}', task_id='{task_id_filter}', result='{result_filter}', search='{search_filter}'")
        
        db_file = get_db_file()
        executions = []
        total_count = 0
        
        try:
            logger.info(f"Opening database connection to: {db_file}")
            with sqlite3.connect(db_file) as conn:
                logger.info("Database connection established")
                
                # Build dynamic WHERE clause based on filters
                where_conditions = []
                params = []
                
                # Individual field filters
                if status_filter:
                    where_conditions.append("LOWER(status) LIKE LOWER(?)")
                    params.append(f"%{status_filter}%")
                
                if client_filter:
                    where_conditions.append("LOWER(client) LIKE LOWER(?)")
                    params.append(f"%{client_filter}%")
                
                if task_id_filter:
                    where_conditions.append("CAST(task_id AS TEXT) = ?")
                    params.append(str(task_id_filter))
                
                if result_filter:
                    where_conditions.append("LOWER(result) LIKE LOWER(?)")
                    params.append(f"%{result_filter}%")
                
                if execution_id_filter:
                    where_conditions.append("LOWER(execution_id) LIKE LOWER(?)")
                    params.append(f"%{execution_id_filter}%")
                
                # Global search filter (searches across multiple fields)
                if search_filter:
                    search_condition = """(
                        LOWER(execution_id) LIKE LOWER(?) OR 
                        LOWER(CAST(task_id AS TEXT)) LIKE LOWER(?) OR 
                        LOWER(client) LIKE LOWER(?) OR 
                        LOWER(status) LIKE LOWER(?) OR 
                        LOWER(result) LIKE LOWER(?)
                    )"""
                    where_conditions.append(search_condition)
                    search_param = f"%{search_filter}%"
                    params.extend([search_param, search_param, search_param, search_param, search_param])
                
                # Build final WHERE clause
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Build count and data queries
                count_query = f"SELECT COUNT(*) FROM executions {where_clause}"
                data_query = f"""
                    SELECT id, execution_id, task_id, client, status, result, created_at, updated_at 
                    FROM executions 
                    {where_clause}
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                
                logger.info(f"Executing count query: {count_query} with params: {params}")
                # Get total count
                count_cur = conn.execute(count_query, params)
                total_count = count_cur.fetchone()[0]
                logger.info(f"Total count: {total_count}")
                
                # Calculate pagination
                offset = (page - 1) * per_page
                total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
                
                # Get paginated records with same filters
                data_params = params + [per_page, offset]
                
                logger.info(f"Executing data query with params: {data_params}")
                cur = conn.execute(data_query, data_params)
                
                logger.info("Fetching execution records...")
                row_count = 0
                for row in cur.fetchall():
                    row_count += 1
                    status_val = row[4]
                    result_val = row[5]
                    executions.append({
                        "id": row[0],
                        "execution_id": row[1],
                        "task_id": row[2],
                        "client": row[3],
                        # Standard fields
                        "status": status_val,
                        "result": result_val,
                        # Backward-compatible aliases
                        "exec_status": status_val,
                        "exec_result": result_val,
                        "created_at": row[6],
                        "updated_at": row[7],
                    })
                logger.info(f"Processed {row_count} execution records")
        except sqlite3.Error as e:
            logger.error(f"Database error in api_executions: {e}")
            return jsonify({
                "executions": [],
                "pagination": {
                    "page": 1,
                    "per_page": per_page,
                    "total_count": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False
                },
                "error": "Database error"
            })
        
        logger.info(f"Returning {len(executions)} executions, total_count={total_count}")
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

    @app.route("/api/dashboard-data", methods=["GET"])
    def api_dashboard_data():
        """API endpoint to get fresh dashboard data for AJAX updates"""
        tasks = get_tasks()
        clients = global_cache.all()
        now = time.time()
        active_clients = get_active_clients(clients, now=now, timeout=60)  # Align with "online" status
        
        # Use centralized assignment service with fallback
        try:
            from services.task_assignment_service import get_assignment_service
            assignment_service = get_assignment_service(global_cache)
            assignment_result = assignment_service.assign_pending_tasks()
            logger.info(f"Dashboard refresh - Task assignment result: {assignment_result}")
        except Exception as e:
            logger.error(f"Assignment service failed in dashboard refresh, using direct assignment: {e}")
            assign_all_tasks(tasks, active_clients)
        
        # Refresh tasks after assignment
        tasks = get_tasks()
        
        # Update task statuses after assignment, but don't override completed tasks
        for tid, task in tasks.items():
            db_status = task.get("status", "")
            # Only compute status if the task isn't already Done/completed
            if db_status not in ("Done", "success", "failed", "completed"):
                computed_status = compute_task_status(task, active_clients)
                task["status"] = computed_status
        
        # Apply default filtering to tasks (recent 40 records)
        tasks_list = list(tasks.values()) if tasks else []
        tasks_total_count = len(tasks_list)
        if tasks_list:
            tasks_list.sort(key=lambda x: x.get('updated_at', 0), reverse=True)
            tasks_list = tasks_list[:40]
        
        # Get executions data with default filtering
        db_file = get_db_file()
        executions = []
        executions_total_count = 0
        
        with sqlite3.connect(db_file) as conn:
            # Get total count of executions
            count_cur = conn.execute("SELECT COUNT(*) FROM executions")
            executions_total_count = count_cur.fetchone()[0]
            
            # Get recent 40 executions sorted by updated_at DESC
            cur = conn.execute("""
                SELECT id, task_id, client, status, result, updated_at 
                FROM executions 
                ORDER BY updated_at DESC 
                LIMIT 40
            """)
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
            "tasks": {task.get('id', i): task for i, task in enumerate(tasks_list)},
            "tasks_total_count": tasks_total_count,
            "tasks_displayed_count": len(tasks_list),
            "clients": active_clients,
            "executions": executions,
            "executions_total_count": executions_total_count,
            "executions_displayed_count": len(executions),
            "filter_applied": "Recent 40 records, sorted by update time desc",
            "now": now,
            "timestamp": time.time()
        })
