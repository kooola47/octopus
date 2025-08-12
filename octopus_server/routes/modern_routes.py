"""
🎨 MODERN UI ROUTES
==================

Flask routes for the modern UI pages.
"""

import time
import math
import sqlite3
import logging
import os
from flask import request, render_template, url_for, jsonify, Response
from dbhelper import get_db_file, get_tasks, get_active_clients
from plugin_discovery import PluginDiscovery
from plugin_cache_manager import get_plugin_cache_manager
from client_cache_manager import get_client_cache_manager

# Get logger
logger = logging.getLogger(__name__)

def register_modern_routes(app, cache, logger):
    """Register modern UI routes with the Flask app"""

    @app.route("/modern")
    @app.route("/modern/dashboard")
    def modern_dashboard():
        """Modern dashboard page"""
        try:
            # Get dashboard statistics
            stats = get_dashboard_stats(cache)
            
            # Get recent activity
            recent_activity = get_recent_activity(limit=10)
            
            # Get recent tasks and executions
            recent_tasks = get_recent_tasks(limit=5)
            recent_executions = get_recent_executions(limit=5)
            
            # Get system health info
            system_health = get_system_health()
            
            return render_template('modern_dashboard.html',
                                 stats=stats,
                                 recent_activity=recent_activity,
                                 recent_tasks=recent_tasks,
                                 recent_executions=recent_executions,
                                 system_health=system_health)
        except Exception as e:
            logger.error(f"Error loading modern dashboard: {e}")
            return render_template('modern_dashboard.html',
                                 stats={},
                                 recent_activity=[],
                                 recent_tasks=[],
                                 recent_executions=[],
                                 system_health={})

    @app.route("/modern/clients")
    def modern_clients():
        """Modern clients page with pagination using cache"""
        try:
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 25))
            search = request.args.get('search', '').strip()
            status_filter = request.args.get('status', '').strip()
            
            # Get clients from cache
            client_cache = get_client_cache_manager()
            clients, total_clients = client_cache.get_clients_paginated(
                page=page,
                page_size=page_size,
                search=search,
                status_filter=status_filter
            )
            
            # Calculate pagination
            total_pages = math.ceil(total_clients / page_size) if total_clients > 0 else 1
            
            # Get client statistics from cache
            stats = client_cache.get_client_stats()
            
            return render_template('modern_clients.html',
                                 clients=clients,
                                 stats=stats,
                                 current_page=page,
                                 page_size=page_size,
                                 total_pages=total_pages,
                                 total_clients=total_clients,
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading modern clients page: {e}")
            return render_template('modern_clients.html',
                                 clients=[],
                                 stats={},
                                 current_page=1,
                                 page_size=25,
                                 total_pages=1,
                                 total_clients=0,
                                 current_timestamp=time.time())

    @app.route("/modern/tasks")
    def modern_tasks():
        """Modern tasks page with pagination"""
        try:
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 25))
            search = request.args.get('search', '').strip()
            status_filter = request.args.get('status', '').strip()
            type_filter = request.args.get('type', '').strip()
            owner_filter = request.args.get('owner', '').strip()
            
            # Get tasks with filters
            tasks, total_tasks = get_tasks_paginated(
                page=page,
                page_size=page_size,
                search=search,
                status_filter=status_filter,
                type_filter=type_filter,
                owner_filter=owner_filter
            )
            
            # Calculate pagination
            total_pages = math.ceil(total_tasks / page_size) if total_tasks > 0 else 1
            
            # Get task statistics
            stats = get_task_stats()
            
            # Get available owners for filter dropdown
            client_cache = get_client_cache_manager()
            active_clients = client_cache.get_active_clients()
            legacy_owners = get_available_owners()
            available_owners = sorted(set(active_clients + legacy_owners))
            
            # Get plugin names for create task modal
            plugin_names = get_available_plugins()
            
            return render_template('modern_tasks.html',
                                 tasks=tasks,
                                 stats=stats,
                                 available_owners=available_owners,
                                 plugin_names=plugin_names,
                                 owner_options=available_owners,
                                 current_page=page,
                                 page_size=page_size,
                                 total_pages=total_pages,
                                 total_tasks=total_tasks,
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading modern tasks page: {e}")
            return render_template('modern_tasks.html',
                                 tasks=[],
                                 stats={},
                                 available_owners=[],
                                 plugin_names=['web_utils', 'file_utils', 'system_utils'],
                                 owner_options=[],
                                 current_page=1,
                                 page_size=25,
                                 total_pages=1,
                                 total_tasks=0,
                                 current_timestamp=time.time())

    @app.route("/modern/executions")
    def modern_executions():
        """Modern executions page with pagination"""
        try:
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 25))
            search = request.args.get('search', '').strip()
            status_filter = request.args.get('status', '').strip()
            client_filter = request.args.get('client', '').strip()
            time_range = request.args.get('time_range', '').strip()
            
            # Get executions with filters
            executions, total_executions = get_executions_paginated(
                page=page,
                page_size=page_size,
                search=search,
                status_filter=status_filter,
                client_filter=client_filter,
                time_range=time_range
            )
            
            # Calculate pagination
            total_pages = math.ceil(total_executions / page_size) if total_executions > 0 else 1
            
            # Get execution statistics
            stats = get_execution_stats()
            
            # Get available clients for filter dropdown
            available_clients = get_available_clients()
            
            # Get all clients data for client filter
            clients = get_all_clients_dict()
            
            return render_template('modern_executions.html',
                                 executions=executions,
                                 stats=stats,
                                 available_clients=available_clients,
                                 clients=clients,
                                 current_page=page,
                                 page_size=page_size,
                                 total_pages=total_pages,
                                 total_executions=total_executions,
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading modern executions page: {e}")
            return render_template('modern_executions.html',
                                 executions=[],
                                 stats={},
                                 available_clients=[],
                                 clients={},
                                 current_page=1,
                                 page_size=25,
                                 total_pages=1,
                                 total_executions=0,
                                 current_timestamp=time.time())

    # Client Management API Endpoints
    @app.route("/api/clients/<client_id>", methods=["GET"])
    def api_client_details(client_id):
        """Get detailed information about a specific client from cache"""
        try:
            client_cache = get_client_cache_manager()
            client = client_cache.get_client_by_id(client_id)
            
            if not client:
                return {"error": "Client not found"}, 404
            
            # Get client execution history from database
            try:
                with sqlite3.connect(get_db_file()) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, task_id, status, start_time, end_time, result
                        FROM executions 
                        WHERE client = ? 
                        ORDER BY start_time DESC 
                        LIMIT 10
                    """, (client_id,))
                    executions = [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"Error getting client executions: {e}")
                executions = []
            
            # Add execution history to client details
            client_details = {
                **client,
                'recent_executions': executions
            }
            
            return {"client": client_details}
            
        except Exception as e:
            logger.error(f"Error getting client details: {e}")
            return {"error": "Internal server error"}, 500
    
    @app.route("/api/clients/<client_id>/assign-task", methods=["POST"])
    def api_assign_task_to_client(client_id):
        """Assign a task to a specific client"""
        try:
            data = request.get_json()
            task_id = data.get('task_id')
            
            if not task_id:
                return {"error": "Task ID is required"}, 400
                
            # Check if client exists and is active
            clients = cache.all()
            client = clients.get(client_id)
            if not client:
                return {"error": "Client not found"}, 404
                
            now = time.time()
            last_seen = client.get('last_seen', now)
            if (now - last_seen) > 30:
                return {"error": "Client is not active"}, 400
                
            # Check if task exists
            try:
                with sqlite3.connect(get_db_file()) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                    task = cursor.fetchone()
                    if not task:
                        return {"error": "Task not found"}, 404
            except Exception as e:
                logger.error(f"Error checking task: {e}")
                return {"error": "Error checking task"}, 500
                
            # Create execution record
            try:
                with sqlite3.connect(get_db_file()) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO executions (task_id, client, status, start_time, result)
                        VALUES (?, ?, 'pending', ?, 'Task assigned to client')
                    """, (task_id, client_id, now))
                    conn.commit()
                    execution_id = cursor.lastrowid
            except Exception as e:
                logger.error(f"Error creating execution: {e}")
                return {"error": "Error creating execution"}, 500
                
            return {
                "message": f"Task {task_id} assigned to client {client_id}",
                "execution_id": execution_id
            }
            
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/clients/<client_id>", methods=["DELETE"])
    def api_delete_client(client_id):
        """Delete a client using cache manager for dual cache/DB cleanup"""
        try:
            client_cache = get_client_cache_manager()
            success = client_cache.delete_client(client_id)
            
            if not success:
                return {"error": "Client not found"}, 404
                
            logger.info(f"Client {client_id} deleted successfully from cache and database")
            return {"message": f"Client {client_id} removed successfully"}
                
        except Exception as e:
            logger.error(f"Error deleting client {client_id}: {e}")
            return {"error": "Internal server error"}, 500

    # Task Management API Endpoints
    @app.route("/api/tasks/<int:task_id>", methods=["GET"])
    def api_task_details(task_id):
        """Get detailed information about a specific task"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                if not task:
                    return {"error": "Task not found"}, 404
                    
                return {"task": dict(task)}
                
        except Exception as e:
            logger.error(f"Error getting task details: {e}")
            return {"error": "Internal server error"}, 500
    
    @app.route("/api/tasks/<int:task_id>/run", methods=["POST"])
    def api_run_task(task_id):
        """Run a specific task"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                if not task:
                    return {"error": "Task not found"}, 404
                    
                # Create execution record
                now = time.time()
                cursor.execute("""
                    INSERT INTO executions (task_id, status, start_time, result)
                    VALUES (?, 'pending', ?, 'Task started manually')
                """, (task_id, now))
                conn.commit()
                execution_id = cursor.lastrowid
                
                return {
                    "message": f"Task {task_id} started successfully",
                    "execution_id": execution_id
                }
                
        except Exception as e:
            logger.error(f"Error running task: {e}")
            return {"error": "Internal server error"}, 500
    
    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def api_delete_task(task_id):
        """Delete a specific task"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                if not task:
                    return {"error": "Task not found"}, 404
                    
                # Delete the task
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                
                return {"message": f"Task {task_id} deleted successfully"}
                
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return {"error": "Internal server error"}, 500

    # Execution Management API Endpoints
    @app.route("/api/executions/<int:execution_id>", methods=["GET"])
    def api_execution_details(execution_id):
        """Get detailed information about a specific execution"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM executions WHERE id = ?", (execution_id,))
                execution = cursor.fetchone()
                
                if not execution:
                    return {"error": "Execution not found"}, 404
                    
                return {"execution": dict(execution)}
                
        except Exception as e:
            logger.error(f"Error getting execution details: {e}")
            return {"error": "Internal server error"}, 500
    
    @app.route("/api/executions/<int:execution_id>/retry", methods=["POST"])
    def api_retry_execution(execution_id):
        """Retry a failed execution"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM executions WHERE id = ?", (execution_id,))
                execution = cursor.fetchone()
                
                if not execution:
                    return {"error": "Execution not found"}, 404
                    
                # Create new execution record
                now = time.time()
                cursor.execute("""
                    INSERT INTO executions (task_id, client, status, start_time, result)
                    VALUES (?, ?, 'pending', ?, 'Retrying failed execution')
                """, (execution['task_id'], execution['client'], now))
                conn.commit()
                new_execution_id = cursor.lastrowid
                
                return {
                    "message": f"Execution {execution_id} retried successfully",
                    "execution_id": new_execution_id
                }
                
        except Exception as e:
            logger.error(f"Error retrying execution: {e}")
            return {"error": "Internal server error"}, 500
    
    @app.route("/api/executions/<int:execution_id>/download", methods=["GET"])
    def api_download_execution_result(execution_id):
        """Download execution result as a file"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT result FROM executions WHERE id = ?", (execution_id,))
                execution = cursor.fetchone()
                
                if not execution:
                    return {"error": "Execution not found"}, 404
                    
                result = execution['result'] or 'No result available'
                
                # Return as downloadable file
                return Response(
                    result,
                    mimetype='text/plain',
                    headers={
                        'Content-Disposition': f'attachment; filename=execution_{execution_id}_result.txt'
                    }
                )
                
        except Exception as e:
            logger.error(f"Error downloading execution result: {e}")
            return {"error": "Internal server error"}, 500

    # Plugin Discovery API Endpoints
    @app.route("/api/plugins", methods=["GET"])
    def api_get_plugins():
        """Get all available plugins with their metadata from cache"""
        try:
            cache_manager = get_plugin_cache_manager()
            formatted_plugins = cache_manager.get_formatted_plugins_for_ui()
            
            return jsonify({
                "plugins": formatted_plugins,
                "cache_stats": cache_manager.get_cache_stats()
            })
            
        except Exception as e:
            logger.error(f"Error getting plugins: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/plugins/<plugin_name>/functions", methods=["GET"])
    def api_get_plugin_functions(plugin_name):
        """Get functions for a specific plugin from cache"""
        try:
            cache_manager = get_plugin_cache_manager()
            functions = cache_manager.get_plugin_function_details(plugin_name)
            
            if not functions:
                return {"error": "Plugin not found or has no functions"}, 404
            
            return jsonify({
                "plugin_name": plugin_name,
                "functions": functions
            })
            
        except Exception as e:
            logger.error(f"Error getting plugin functions: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/plugins/<plugin_name>/functions/<function_name>/parameters", methods=["GET"])
    def api_get_function_parameters(plugin_name, function_name):
        """Get parameters for a specific plugin function from cache"""
        try:
            cache_manager = get_plugin_cache_manager()
            parameters = cache_manager.get_function_parameters(plugin_name, function_name)
            
            if not parameters:
                return {"error": "Function not found or has no parameters"}, 404
                
            return jsonify({
                "plugin_name": plugin_name,
                "function_name": function_name,
                "parameters": parameters
            })
            
        except Exception as e:
            logger.error(f"Error getting function parameters: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/plugins/cache/refresh", methods=["POST"])
    def api_refresh_plugin_cache():
        """Manually refresh the plugin cache"""
        try:
            cache_manager = get_plugin_cache_manager()
            success = cache_manager.refresh_cache()
            
            if success:
                return jsonify({
                    "message": "Plugin cache refreshed successfully",
                    "cache_stats": cache_manager.get_cache_stats()
                })
            else:
                return {"error": "Failed to refresh plugin cache"}, 500
                
        except Exception as e:
            logger.error(f"Error refreshing plugin cache: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/plugins/cache/stats", methods=["GET"])
    def api_get_plugin_cache_stats():
        """Get plugin cache statistics"""
        try:
            cache_manager = get_plugin_cache_manager()
            return jsonify(cache_manager.get_cache_stats())
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/owners", methods=["GET"])
    def api_get_available_owners():
        """Get available owners for task assignment from active clients"""
        try:
            client_cache = get_client_cache_manager()
            # Get active client usernames as potential owners
            owners = client_cache.get_active_clients()
            
            # Also include owners from existing tasks for backward compatibility
            legacy_owners = get_available_owners()
            
            # Combine and deduplicate
            all_owners = sorted(set(owners + legacy_owners))
            
            return jsonify({"owners": all_owners})
            
        except Exception as e:
            logger.error(f"Error getting owners: {e}")
            return {"error": "Internal server error"}, 500

# Helper functions for data retrieval

def get_dashboard_stats(cache):
    """Get dashboard statistics from real data"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get total tasks
            cursor.execute("SELECT COUNT(*) as count FROM tasks")
            total_tasks = cursor.fetchone()['count']
            
            # Get active clients from cache (heartbeat system)
            active_clients = 0
            try:
                clients = cache.all()
                now = time.time()
                for client_id, client_data in clients.items():
                    last_heartbeat = client_data.get('last_heartbeat', 0)
                    if now - last_heartbeat < 60:  # Active within last 60 seconds
                        active_clients += 1
            except Exception as e:
                logger.error(f"Error getting active clients from cache: {e}")
                active_clients = 0
            
            # Get running tasks
            cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status IN ('running', 'Active')")
            running_tasks = cursor.fetchone()['count']
            
            # Get today's executions
            today_start = time.time() - 86400  # 24 hours ago
            cursor.execute("SELECT COUNT(*) as count FROM executions WHERE created_at > ?", (today_start,))
            total_executions = cursor.fetchone()['count']
            
            return {
                'total_tasks': total_tasks,
                'active_clients': active_clients,
                'running_tasks': running_tasks,
                'total_executions': total_executions
            }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {
            'total_tasks': 0,
            'active_clients': 0,
            'running_tasks': 0,
            'total_executions': 0
        }

def get_recent_activity(limit=10):
    """Get recent activity from real execution data"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent executions as activity
            cursor.execute("""
                SELECT 
                    execution_id,
                    task_id,
                    client,
                    status,
                    result,
                    created_at,
                    updated_at
                FROM executions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            activities = []
            for row in cursor.fetchall():
                # Determine event type and description based on status
                if row['status'] == 'success':
                    event_type = 'Task Completed'
                    description = f"Successfully executed task {row['task_id'][:8] if row['task_id'] else 'unknown'}"
                elif row['status'] == 'failed':
                    event_type = 'Task Failed'
                    description = f"Failed to execute task {row['task_id'][:8] if row['task_id'] else 'unknown'}"
                else:
                    event_type = 'Task Started'
                    description = f"Started executing task {row['task_id'][:8] if row['task_id'] else 'unknown'}"
                
                # Determine client status (simplified)
                client_status = 'online' if row['status'] in ['success', 'running'] else 'offline'
                
                activities.append({
                    'timestamp': row['created_at'],
                    'created_at': row['created_at'],
                    'event_type': event_type,
                    'description': description,
                    'client': row['client'] or 'Unknown',
                    'client_status': client_status,
                    'status': row['status']
                })
            
            return activities
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return []

def get_recent_tasks(limit=5):
    """Get recent tasks for dashboard"""
    try:
        tasks = get_tasks()
        # Sort by created_at and limit
        recent = sorted(tasks, key=lambda x: x.get('created_at', 0), reverse=True)[:limit]
        return recent
    except Exception:
        return []

def get_recent_executions(limit=5):
    """Get recent executions for dashboard"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT execution_id, task_id, client, status, created_at
                FROM executions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            executions = []
            for row in cursor.fetchall():
                executions.append(dict(row))
            
            return executions
    except Exception:
        return []

def get_system_health():
    """Get system health metrics"""
    # Mock data for now - in real implementation, this would collect actual metrics
    return {
        'cpu_usage': 25,
        'memory_usage': 45,
        'db_size': '2.3 MB'
    }

def get_clients_paginated(page=1, page_size=25, search='', status_filter=''):
    """Get clients with pagination and filters from real heartbeat data"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try to get client data from heartbeats table
            try:
                # Get unique clients with their latest heartbeat and system stats
                base_query = """
                    SELECT 
                        h1.username as name,
                        h1.hostname,
                        h1.ip_address,
                        h1.timestamp as last_heartbeat,
                        h1.cpu_usage,
                        h1.memory_usage,
                        COUNT(h2.id) as heartbeat_count
                    FROM heartbeats h1
                    LEFT JOIN heartbeats h2 ON h1.username = h2.username 
                        AND h1.hostname = h2.hostname 
                        AND h1.ip_address = h2.ip_address
                    WHERE h1.username IS NOT NULL
                        AND h1.timestamp = (
                            SELECT MAX(timestamp) 
                            FROM heartbeats h3 
                            WHERE h3.username = h1.username 
                                AND h3.hostname = h1.hostname 
                                AND h3.ip_address = h1.ip_address
                        )
                    GROUP BY h1.username, h1.hostname, h1.ip_address
                """
                
                cursor.execute(base_query)
                heartbeat_data = cursor.fetchall()
                
                # Convert to client objects
                current_time = time.time()
                all_clients = []
                
                for i, row in enumerate(heartbeat_data):
                    time_diff = current_time - row['last_heartbeat']
                    if time_diff < 60:
                        status = 'online'
                    elif time_diff < 300:  # 5 minutes
                        status = 'idle'
                    else:
                        status = 'offline'
                    
                    # Get execution count for this client
                    cursor.execute("SELECT COUNT(*) as count FROM executions WHERE client = ?", (row['name'],))
                    exec_result = cursor.fetchone()
                    tasks_executed = exec_result['count'] if exec_result else 0
                    
                    # Get success rate
                    cursor.execute("SELECT COUNT(*) as count FROM executions WHERE client = ? AND status = 'success'", (row['name'],))
                    success_result = cursor.fetchone()
                    success_count = success_result['count'] if success_result else 0
                    success_rate = (success_count / tasks_executed * 100) if tasks_executed > 0 else 0
                    
                    client = {
                        'id': row['name'],
                        'name': row['name'],
                        'status': status,
                        'hostname': row['hostname'] or 'unknown',
                        'ip_address': row['ip_address'] or '127.0.0.1',
                        'last_heartbeat': row['last_heartbeat'],
                        'tasks_executed': tasks_executed,
                        'success_rate': round(success_rate, 1),
                        'cpu_usage': round(row['cpu_usage'] or 0.0, 1),  # Real CPU usage from heartbeat
                        'memory_usage': round(row['memory_usage'] or 0.0, 1),  # Real memory usage from heartbeat
                        'version': 'v2.0.0'
                    }
                    all_clients.append(client)
                
            except Exception as e:
                logger.error(f"Error getting heartbeat data: {e}")
                # Fallback to execution data if heartbeats table issues
                cursor.execute("SELECT DISTINCT client FROM executions WHERE client IS NOT NULL ORDER BY client")
                client_names = [row[0] for row in cursor.fetchall()]
                
                all_clients = []
                current_time = time.time()
                for i, client_name in enumerate(client_names):
                    # Get latest execution time as approximation for last seen
                    cursor.execute("SELECT MAX(created_at) as last_seen FROM executions WHERE client = ?", (client_name,))
                    result = cursor.fetchone()
                    last_seen = result['last_seen'] if result and result['last_seen'] else current_time - 3600
                    
                    time_diff = current_time - last_seen
                    status = 'online' if time_diff < 3600 else 'offline'  # 1 hour threshold
                    
                    # Get execution stats
                    cursor.execute("SELECT COUNT(*) as count FROM executions WHERE client = ?", (client_name,))
                    exec_result = cursor.fetchone()
                    tasks_executed = exec_result['count'] if exec_result else 0
                    
                    cursor.execute("SELECT COUNT(*) as count FROM executions WHERE client = ? AND status = 'success'", (client_name,))
                    success_result = cursor.fetchone()
                    success_count = success_result['count'] if success_result else 0
                    success_rate = (success_count / tasks_executed * 100) if tasks_executed > 0 else 0
                    
                    client = {
                        'id': client_name,
                        'name': client_name,
                        'status': status,
                        'hostname': f'host-{client_name}',
                        'ip_address': '192.168.1.100',
                        'last_heartbeat': last_seen,
                        'tasks_executed': tasks_executed,
                        'success_rate': round(success_rate, 1),
                        'cpu_usage': 25 + (i % 30),
                        'memory_usage': 30 + (i % 40),
                        'version': 'v2.0.0'
                    }
                    all_clients.append(client)
        
        # Apply filters
        filtered_clients = all_clients
        if search:
            filtered_clients = [c for c in filtered_clients if search.lower() in c['name'].lower()]
        if status_filter:
            filtered_clients = [c for c in filtered_clients if c['status'] == status_filter]
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_clients = filtered_clients[start_idx:end_idx]
        
        return paginated_clients, len(filtered_clients)
        
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        return [], 0

def get_client_stats():
    """Get client statistics from real data"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            current_time = time.time()
            online_clients = 0
            offline_clients = 0
            idle_clients = 0
            
            try:
                # Try heartbeats table first
                cursor.execute("""
                    SELECT username, MAX(timestamp) as last_heartbeat
                    FROM heartbeats 
                    WHERE username IS NOT NULL
                    GROUP BY username
                """)
                
                for row in cursor.fetchall():
                    time_diff = current_time - row['last_heartbeat']
                    if time_diff < 60:
                        online_clients += 1
                    elif time_diff < 300:
                        idle_clients += 1
                    else:
                        offline_clients += 1
                        
            except Exception:
                # Fallback to executions table
                cursor.execute("SELECT DISTINCT client FROM executions WHERE client IS NOT NULL")
                client_names = [row[0] for row in cursor.fetchall()]
                
                for client_name in client_names:
                    cursor.execute("SELECT MAX(created_at) as last_seen FROM executions WHERE client = ?", (client_name,))
                    result = cursor.fetchone()
                    last_seen = result['last_seen'] if result and result['last_seen'] else current_time - 3600
                    
                    time_diff = current_time - last_seen
                    if time_diff < 3600:  # 1 hour
                        online_clients += 1
                    else:
                        offline_clients += 1
            
            total_clients = online_clients + offline_clients + idle_clients
            
            return {
                'online_clients': online_clients,
                'offline_clients': offline_clients,
                'idle_clients': idle_clients,
                'total_clients': total_clients
            }
    except Exception as e:
        logger.error(f"Error getting client stats: {e}")
        return {
            'online_clients': 0,
            'offline_clients': 0,
            'idle_clients': 0,
            'total_clients': 0
        }

def get_tasks_paginated(page=1, page_size=25, search='', status_filter='', type_filter='', owner_filter=''):
    """Get tasks with pagination and filters using real database data"""
    try:
        # Get all tasks from database
        tasks_dict = get_tasks()
        all_tasks = []
        
        # Convert dictionary to list format for easier processing
        for task_id, task_data in tasks_dict.items():
            # Calculate execution statistics
            executions = task_data.get('executions', [])
            total_executions = len(executions)
            success_executions = len([e for e in executions if e.get('status') == 'success'])
            success_rate = (success_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Determine priority based on execution frequency and status
            if total_executions > 10:
                priority = 'high'
            elif total_executions > 5:
                priority = 'medium'
            else:
                priority = 'low'
            
            # Get the most recent execution
            last_execution = None
            if executions:
                latest_exec = max(executions, key=lambda x: x.get('created_at', 0))
                last_execution = latest_exec.get('created_at')
            
            all_tasks.append({
                'id': task_id,
                'name': task_data.get('plugin', f'Task {task_id[:8]}'),
                'description': f"Plugin: {task_data.get('plugin', 'Unknown')} | Action: {task_data.get('action', 'run')}",
                'owner': task_data.get('owner', 'System'),
                'plugin': task_data.get('plugin', 'unknown'),
                'status': task_data.get('status', 'pending'),
                'type': task_data.get('type', 'scheduled'),
                'priority': priority,
                'last_execution': last_execution,
                'total_executions': total_executions,
                'success_rate': success_rate,
                'created_at': task_data.get('created_at'),
                'updated_at': task_data.get('updated_at')
            })
        
        # Apply filters
        filtered_tasks = all_tasks
        if search:
            filtered_tasks = [t for t in filtered_tasks if 
                            search.lower() in t.get('name', '').lower() or 
                            search.lower() in t.get('plugin', '').lower() or
                            search.lower() in t.get('description', '').lower()]
        if status_filter:
            filtered_tasks = [t for t in filtered_tasks if t.get('status') == status_filter]
        if type_filter:
            filtered_tasks = [t for t in filtered_tasks if t.get('type') == type_filter]
        if owner_filter:
            filtered_tasks = [t for t in filtered_tasks if t.get('owner') == owner_filter]
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_tasks = filtered_tasks[start_idx:end_idx]
        
        return paginated_tasks, len(filtered_tasks)
    except Exception as e:
        logger.error(f"Error getting paginated tasks: {e}")
        return [], 0

def get_task_stats():
    """Get task statistics from real database data"""
    try:
        tasks_dict = get_tasks()
        
        total = len(tasks_dict)
        running = 0
        completed = 0
        failed = 0
        
        for task_id, task_data in tasks_dict.items():
            status = task_data.get('status', '').lower()
            if status in ['running', 'executing']:
                running += 1
            elif status in ['success', 'done', 'completed']:
                completed += 1
            elif status in ['failed', 'error']:
                failed += 1
        
        return {
            'total_tasks': total,
            'running_tasks': running,
            'completed_tasks': completed,
            'failed_tasks': failed
        }
    except Exception as e:
        logger.error(f"Error getting task stats: {e}")
        return {
            'total_tasks': 0,
            'running_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0
        }

def get_available_owners():
    """Get list of available task owners from real database data"""
    try:
        tasks_dict = get_tasks()
        owners = set()
        
        for task_id, task_data in tasks_dict.items():
            owner = task_data.get('owner')
            if owner and owner not in ['ALL', 'Anyone', '', None]:
                owners.add(owner)
        
        return sorted(list(owners))
    except Exception as e:
        logger.error(f"Error getting available owners: {e}")
        return []

def get_executions_paginated(page=1, page_size=25, search='', status_filter='', client_filter='', time_range=''):
    """Get executions with pagination and filters"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(execution_id LIKE ? OR task_id LIKE ? OR client LIKE ?)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            if status_filter:
                where_conditions.append("status = ?")
                params.append(status_filter)
            
            if client_filter:
                where_conditions.append("client = ?")
                params.append(client_filter)
            
            if time_range:
                time_cutoff = time.time()
                if time_range == '1h':
                    time_cutoff -= 3600
                elif time_range == '24h':
                    time_cutoff -= 86400
                elif time_range == '7d':
                    time_cutoff -= 604800
                elif time_range == '30d':
                    time_cutoff -= 2592000
                
                where_conditions.append("created_at > ?")
                params.append(time_cutoff)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Get total count
            count_query = f"SELECT COUNT(*) as count FROM executions WHERE {where_clause}"
            cursor.execute(count_query, params)
            total_executions = cursor.fetchone()['count']
            
            # Get paginated results
            offset = (page - 1) * page_size
            query = f"""
                SELECT execution_id, task_id, client, status, result, created_at, updated_at
                FROM executions 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [page_size, offset])
            
            executions = []
            for row in cursor.fetchall():
                exec_dict = dict(row)
                # Calculate duration if available
                if exec_dict['updated_at'] and exec_dict['created_at']:
                    exec_dict['duration'] = exec_dict['updated_at'] - exec_dict['created_at']
                else:
                    exec_dict['duration'] = None
                
                # Mock additional fields
                exec_dict['client_online'] = True
                exec_dict['plugin'] = 'unknown'
                exec_dict['retry_count'] = 0
                
                executions.append(exec_dict)
            
            return executions, total_executions
    except Exception as e:
        return [], 0

def get_execution_stats():
    """Get execution statistics"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get total executions
            cursor.execute("SELECT COUNT(*) as count FROM executions")
            total = cursor.fetchone()['count']
            
            # Get successful executions
            cursor.execute("SELECT COUNT(*) as count FROM executions WHERE status = 'success'")
            successful = cursor.fetchone()['count']
            
            # Get failed executions
            cursor.execute("SELECT COUNT(*) as count FROM executions WHERE status = 'failed'")
            failed = cursor.fetchone()['count']
            
            # Get running executions
            cursor.execute("SELECT COUNT(*) as count FROM executions WHERE status = 'running'")
            running = cursor.fetchone()['count']
            
            return {
                'total_executions': total,
                'successful_executions': successful,
                'failed_executions': failed,
                'running_executions': running
            }
    except Exception:
        return {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'running_executions': 0
        }

def format_uptime(seconds):
    """Format uptime seconds into human readable string"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    elif seconds < 86400:
        hours = int(seconds/3600)
        minutes = int((seconds%3600)/60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds/86400)
        hours = int((seconds%86400)/3600)
        return f"{days}d {hours}h"

def get_available_clients():
    """Get list of available clients for filtering"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT client FROM executions WHERE client IS NOT NULL ORDER BY client")
            clients = [row[0] for row in cursor.fetchall()]
            return clients
    except Exception:
        return []

def get_available_plugins():
    """Get list of available plugins for task creation from cache"""
    try:
        # Get plugins from cache first
        cache_manager = get_plugin_cache_manager()
        plugin_names = cache_manager.get_plugin_names()
        
        if plugin_names:
            return plugin_names
        
        # Fallback to database if cache is empty
        with sqlite3.connect(get_db_file()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT plugin FROM tasks WHERE plugin IS NOT NULL ORDER BY plugin")
            plugins = [row[0] for row in cursor.fetchall()]
            if plugins:
                return plugins
                
        # Final fallback to hardcoded list
        return ['web_utils', 'file_operations', 'system_info', 'notifications']
        
    except Exception as e:
        logger.error(f"Error getting available plugins: {e}")
        return ['web_utils', 'file_operations', 'system_info', 'notifications']

def get_all_clients_dict():
    """Get all clients as a dictionary for template use"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT client FROM executions WHERE client IS NOT NULL")
            clients = {}
            for row in cursor.fetchall():
                client_id = row[0]
                clients[client_id] = client_id
            return clients
    except Exception:
        return {}
