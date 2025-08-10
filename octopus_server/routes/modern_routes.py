"""
🎨 MODERN UI ROUTES
==================

Flask routes for the modern UI pages.
"""

import time
import math
import sqlite3
import logging
import uuid
from flask import request, render_template, url_for, Response, jsonify
from dbhelper import get_db_file, get_tasks, get_active_clients
from config import SERVER_PORT

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
            stats = get_dashboard_stats()
            
            # Get recent activity
            recent_activity = get_recent_activity(limit=10)
            
            # Get recent tasks and executions
            recent_tasks = get_recent_tasks(limit=5)
            recent_executions = get_recent_executions(limit=5)
            
            # Get system health info
            system_health = get_system_health()
            
            return render_template('dashboard.html',
                                 stats=stats,
                                 recent_activity=recent_activity,
                                 recent_tasks=recent_tasks,
                                 recent_executions=recent_executions,
                                 system_health=system_health)
        except Exception as e:
            logger.error(f"Error loading modern dashboard: {e}")
            return render_template('dashboard.html',
                                 stats={},
                                 recent_activity=[],
                                 recent_tasks=[],
                                 recent_executions=[],
                                 system_health={})

    @app.route("/modern/clients")
    def modern_clients():
        """Modern clients page with pagination"""
        try:
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 25))
            search = request.args.get('search', '').strip()
            status_filter = request.args.get('status', '').strip()
            
            # Get clients with filters
            clients, total_clients = get_clients_paginated(
                cache=cache,
                page=page,
                page_size=page_size,
                search=search,
                status_filter=status_filter
            )
            
            # Calculate pagination
            total_pages = math.ceil(total_clients / page_size) if total_clients > 0 else 1
            
            # Get client statistics
            stats = get_client_stats(cache)
            
            return render_template('clients.html',
                                 clients=clients,
                                 stats=stats,
                                 current_page=page,
                                 page_size=page_size,
                                 total_pages=total_pages,
                                 total_clients=total_clients,
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading modern clients page: {e}")
            return render_template('clients.html',
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
            available_owners = get_available_owners()
            
            return render_template('tasks.html',
                                 tasks=tasks,
                                 stats=stats,
                                 available_owners=available_owners,
                                 current_page=page,
                                 page_size=page_size,
                                 total_pages=total_pages,
                                 total_tasks=total_tasks,
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading modern tasks page: {e}")
            return render_template('tasks.html',
                                 tasks=[],
                                 stats={},
                                 available_owners=[],
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
            
            return render_template('executions.html',
                                 executions=executions,
                                 stats=stats,
                                 available_clients=available_clients,
                                 current_page=page,
                                 page_size=page_size,
                                 total_pages=total_pages,
                                 total_executions=total_executions,
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading modern executions page: {e}")
            return render_template('executions.html',
                                 executions=[],
                                 stats={},
                                 available_clients=[],
                                 current_page=1,
                                 page_size=25,
                                 total_pages=1,
                                 total_executions=0,
                                 current_timestamp=time.time())

# Helper functions for data retrieval

def get_dashboard_stats():
    """Get dashboard statistics from real data"""
    try:
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get total tasks
            cursor.execute("SELECT COUNT(*) as count FROM tasks")
            total_tasks = cursor.fetchone()['count']
            
            # Get active clients (check heartbeats table)
            cutoff_time = time.time() - 60  # Consider active if heartbeat within last 60 seconds
            try:
                cursor.execute("""
                    SELECT COUNT(DISTINCT username) as count 
                    FROM heartbeats
                    WHERE timestamp > ?
                """, (cutoff_time,))
                active_clients = cursor.fetchone()['count']
            except:
                # If heartbeats table doesn't exist or has issues, try alternative
                try:
                    cursor.execute("SELECT COUNT(DISTINCT client) as count FROM executions WHERE created_at > ?", (time.time() - 3600,))
                    active_clients = cursor.fetchone()['count']
                except:
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
    """Get recent tasks for dashboard using real database data"""
    try:
        tasks_dict = get_tasks()
        tasks_list = []
        
        # Convert dictionary to list format with proper data
        for task_id, task_data in tasks_dict.items():
            tasks_list.append({
                'id': task_id,
                'plugin': task_data.get('plugin', 'Unknown'),
                'owner': task_data.get('owner', 'System'),
                'status': task_data.get('status', 'pending'),
                'created_at': task_data.get('created_at', 0)
            })
        
        # Sort by created_at and limit
        recent = sorted(tasks_list, key=lambda x: x.get('created_at', 0), reverse=True)[:limit]
        return recent
    except Exception as e:
        logger.error(f"Error getting recent tasks: {e}")
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
    """Get system health metrics using real system data"""
    import psutil
    import os
    
    try:
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get database size
        db_file = get_db_file()
        if os.path.exists(db_file):
            db_size_bytes = os.path.getsize(db_file)
            if db_size_bytes < 1024 * 1024:  # Less than 1MB
                db_size = f"{db_size_bytes / 1024:.1f} KB"
            else:
                db_size = f"{db_size_bytes / (1024 * 1024):.1f} MB"
        else:
            db_size = "0 KB"
        
        return {
            'cpu_usage': round(cpu_usage, 1),
            'memory_usage': round(memory_usage, 1),
            'db_size': db_size
        }
    except ImportError:
        # If psutil is not available, provide fallback data
        logger.warning("psutil not available, using fallback system health data")
        return {
            'cpu_usage': 25.0,
            'memory_usage': 45.0,
            'db_size': '2.3 MB'
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            'cpu_usage': 0,
            'memory_usage': 0,
            'db_size': 'Unknown'
        }

def get_clients_paginated(cache, page=1, page_size=25, search='', status_filter=''):
    """Get clients with pagination and filters from cache heartbeat data"""
    try:
        # Get all clients from cache (heartbeat data)
        all_cached_clients = cache.all()
        logger.info(f"Found {len(all_cached_clients)} clients in cache")
        
        # Convert cache data to client objects
        current_time = time.time()
        all_clients = []
        
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for client_key, client_data in all_cached_clients.items():
                try:
                    # Parse client key (format: username@hostname)
                    if '@' in client_key:
                        username, hostname = client_key.split('@', 1)
                    else:
                        username = client_key
                        hostname = client_data.get('hostname', 'unknown')
                    
                    # Calculate status based on last heartbeat
                    last_heartbeat = client_data.get('last_heartbeat', 0)
                    time_diff = current_time - last_heartbeat
                    
                    if time_diff < 60:  # Less than 1 minute
                        status = 'online'
                    elif time_diff < 300:  # Less than 5 minutes
                        status = 'idle'
                    else:
                        status = 'offline'
                    
                    # Get execution count for this client
                    cursor.execute("SELECT COUNT(*) as count FROM executions WHERE client = ?", (username,))
                    exec_result = cursor.fetchone()
                    tasks_executed = exec_result['count'] if exec_result else 0
                    
                    # Get success rate
                    cursor.execute("SELECT COUNT(*) as count FROM executions WHERE client = ? AND status = 'success'", (username,))
                    success_result = cursor.fetchone()
                    success_count = success_result['count'] if success_result else 0
                    success_rate = (success_count / tasks_executed * 100) if tasks_executed > 0 else 0
                    
                    client = {
                        'id': client_key,  # Use full key for unique identification
                        'name': username,
                        'status': status,
                        'hostname': hostname,
                        'ip_address': client_data.get('ip_address', client_data.get('ip', '127.0.0.1')),
                        'last_heartbeat': last_heartbeat,
                        'tasks_executed': tasks_executed,
                        'success_rate': round(success_rate, 1),
                        'cpu_usage': client_data.get('cpu_usage', 0),
                        'memory_usage': client_data.get('memory_usage', 0),
                        'version': client_data.get('version', 'v2.0.0'),
                        'python_version': client_data.get('python_version', '3.11'),
                        'platform': client_data.get('platform', 'Unknown'),
                        'pid': client_data.get('pid', 0)
                    }
                    all_clients.append(client)
                    
                except Exception as e:
                    logger.error(f"Error processing client {client_key}: {e}")
                    continue
        
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

def get_client_stats(cache):
    """Get client statistics from cache data"""
    try:
        # Get all clients from cache
        all_cached_clients = cache.all()
        current_time = time.time()
        
        online_clients = 0
        offline_clients = 0
        idle_clients = 0
        
        for client_key, client_data in all_cached_clients.items():
            last_heartbeat = client_data.get('last_heartbeat', 0)
            time_diff = current_time - last_heartbeat
            
            if time_diff < 60:  # Less than 1 minute
                online_clients += 1
            elif time_diff < 300:  # Less than 5 minutes
                idle_clients += 1
            else:
                offline_clients += 1
        
        total_clients = len(all_cached_clients)
        uptime_percentage = (online_clients / total_clients * 100) if total_clients > 0 else 0
        
        return {
            'total': total_clients,
            'online': online_clients,
            'offline': offline_clients,
            'idle': idle_clients,
            'uptime_percentage': round(uptime_percentage, 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting client stats: {e}")
        return {
            'total': 0,
            'online': 0,
            'offline': 0,
            'idle': 0,
            'uptime_percentage': 0
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
                
                # Add additional computed fields
                exec_dict['client_online'] = exec_dict['status'] in ['success', 'running']
                exec_dict['plugin'] = 'system'  # Default plugin type
                exec_dict['retry_count'] = 0    # Default retry count
                
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

    # API Endpoints for task actions
    @app.route('/api/plugins', methods=['GET'])
    def api_get_plugins():
        """Get available plugins from the plugins directory"""
        try:
            import os
            import glob
            
            plugins = []
            
            # Check both server plugins and root plugins directories
            plugin_dirs = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins'),  # octopus_server/plugins
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'plugins')  # root/plugins
            ]
            
            for plugin_dir in plugin_dirs:
                if os.path.exists(plugin_dir):
                    # Get all Python files in plugins directory
                    plugin_files = glob.glob(os.path.join(plugin_dir, "*.py"))
                    
                    for plugin_file in plugin_files:
                        plugin_name = os.path.basename(plugin_file)
                        
                        # Skip __init__.py and setup files
                        if plugin_name.startswith('__') or plugin_name in ['plugin_setup.py']:
                            continue
                            
                        # Remove .py extension
                        plugin_name = plugin_name[:-3]
                        
                        # Try to get plugin description by reading the file
                        description = ""
                        try:
                            with open(plugin_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Look for docstring or description
                                lines = content.split('\n')
                                for line in lines[:10]:  # Check first 10 lines
                                    if '"""' in line or "'''" in line:
                                        desc_line = line.strip().replace('"""', '').replace("'''", '').strip()
                                        if desc_line and not desc_line.startswith('#'):
                                            description = desc_line
                                            break
                                    elif line.strip().startswith('#') and 'description' in line.lower():
                                        description = line.strip().replace('#', '').strip()
                                        break
                        except:
                            pass
                        
                        plugin_info = {
                            'name': plugin_name,
                            'display_name': plugin_name.replace('_', ' ').title(),
                            'description': description or f"Plugin for {plugin_name.replace('_', ' ')}"
                        }
                        
                        # Avoid duplicates
                        if not any(p['name'] == plugin_name for p in plugins):
                            plugins.append(plugin_info)
            
            # Sort by name
            plugins.sort(key=lambda x: x['name'])
            
            return {
                'success': True,
                'plugins': plugins
            }
            
        except Exception as e:
            logger.error(f"Error getting plugins: {e}")
            return {
                'success': False,
                'message': f'Error getting plugins: {str(e)}',
                'plugins': []
            }

    @app.route('/api/tasks', methods=['POST'])
    def api_create_task():
        """Create a new task via API"""
        try:
            from dbhelper import add_task
            import uuid
            import time
            
            task_data = request.get_json()
            
            # Generate unique task ID
            task_id = str(int(time.time() * 1000))
            
            # Prepare task for database
            db_task = {
                'id': task_id,
                'owner': task_data.get('owner'),
                'plugin': task_data.get('plugin'),
                'action': task_data.get('action', 'run'),
                'args': task_data.get('args', []),
                'kwargs': task_data.get('kwargs', {}),
                'type': task_data.get('type', 'scheduled'),
                'interval': task_data.get('interval', ''),
                'status': 'Active',
                'description': task_data.get('description', '')
            }
            
            # Add task to database
            add_task(db_task)
            
            return {
                'success': True,
                'message': 'Task created successfully',
                'task_id': task_id
            }
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {
                'success': False,
                'message': f'Error creating task: {str(e)}'
            }, 500

    # API Endpoints for execution actions
    @app.route("/api/executions/<execution_id>", methods=['GET'])
    def api_get_execution(execution_id):
        """Get single execution details"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT execution_id, task_id, client, status, result, created_at, updated_at
                    FROM executions 
                    WHERE execution_id = ?
                """, (execution_id,))
                
                row = cursor.fetchone()
                if row:
                    execution = dict(row)
                    return execution
                else:
                    return {"error": "Execution not found"}, 404
        except Exception as e:
            logger.error(f"Error getting execution {execution_id}: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/executions/<execution_id>/result", methods=['GET'])
    def api_get_execution_result(execution_id):
        """Get execution result as downloadable file"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT result FROM executions WHERE execution_id = ?", (execution_id,))
                row = cursor.fetchone()
                
                if row and row[0]:
                    from flask import Response
                    return Response(
                        row[0],
                        mimetype='text/plain',
                        headers={'Content-Disposition': f'attachment; filename=execution_{execution_id}_result.txt'}
                    )
                else:
                    return {"error": "No result found"}, 404
        except Exception as e:
            logger.error(f"Error getting execution result {execution_id}: {e}")
            return {"error": "Internal server error"}, 500

    @app.route("/api/executions/<execution_id>/retry", methods=['POST'])
    def api_retry_execution(execution_id):
        """Retry a failed execution"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                cursor = conn.cursor()
                
                # Get original execution details
                cursor.execute("""
                    SELECT task_id, client FROM executions WHERE execution_id = ?
                """, (execution_id,))
                row = cursor.fetchone()
                
                if not row:
                    return {"success": False, "message": "Original execution not found"}, 404
                
                task_id, client = row
                
                # Create new execution (simplified - in real implementation you'd use task manager)
                import time
                import uuid
                new_execution_id = str(uuid.uuid4())
                now = time.time()
                
                cursor.execute("""
                    INSERT INTO executions (execution_id, task_id, client, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'pending', ?, ?)
                """, (new_execution_id, task_id, client, now, now))
                
                conn.commit()
                
                return {
                    "success": True, 
                    "message": "Execution retry initiated",
                    "new_execution_id": new_execution_id
                }
                
        except Exception as e:
            logger.error(f"Error retrying execution {execution_id}: {e}")
            return {"success": False, "message": "Internal server error"}, 500

    @app.route("/api/clients/<client_id>/restart", methods=["POST"])
    def restart_client_endpoint(client_id):
        """Send restart command to a specific client"""
        try:
            logger.info(f"🔄 Restart request for client: {client_id}")
            
            # Extract hostname from client_id (format: username@hostname)
            if '@' in client_id:
                hostname = client_id.split('@')[1]
            else:
                hostname = client_id
            
            # Queue restart command for the client using the commands endpoint
            restart_command = {
                "plugin": "client_control",
                "action": "restart_client",
                "args": [],
                "kwargs": {},
                "timestamp": time.time()
            }
            
            # Use shared commands manager
            from commands_manager import add_command
            
            success = add_command(hostname, restart_command)
            
            logger.info(f"✅ Restart command queued for client {client_id} (hostname: {hostname})")
            
            return jsonify({
                "success": True,
                "message": f"Restart command sent to client {client_id}",
                "command": restart_command
            })
            
        except Exception as e:
            logger.error(f"❌ Error sending restart command to client {client_id}: {e}")
            return jsonify({
                "success": False,
                "message": f"Failed to send restart command: {str(e)}"
            }), 500

    @app.route("/api/clients/<client_id>/shutdown", methods=["POST", "OPTIONS"])
    def shutdown_client_endpoint(client_id):
        """Send shutdown command to a specific client"""
        
        # Handle CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
            return response
            
        try:
            logger.info(f"⛔ Shutdown request for client: {client_id}")
            
            # Extract hostname from client_id (format: username@hostname)
            if '@' in client_id:
                hostname = client_id.split('@')[1]
            else:
                hostname = client_id
            
            # Queue shutdown command for the client
            shutdown_command = {
                "plugin": "client_control",
                "action": "shutdown_client",
                "args": [],
                "kwargs": {},
                "timestamp": time.time()
            }
            
            # Use shared commands manager
            from commands_manager import add_command
            
            success = add_command(hostname, shutdown_command)
            
            logger.info(f"✅ Shutdown command queued for client {client_id} (hostname: {hostname})")
            
            response = jsonify({
                "success": True,
                "message": f"Shutdown command sent to client {client_id}",
                "command": shutdown_command
            })
            
            # Add CORS headers
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error sending shutdown command to client {client_id}: {e}")
            
            response = jsonify({
                "success": False,
                "message": f"Failed to send shutdown command: {str(e)}"
            })
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 500

    @app.route("/api/clients/<client_id>/info", methods=["GET"])
    def get_client_info_endpoint(client_id):
        """Get detailed information from a specific client"""
        try:
            logger.info(f"📊 Info request for client: {client_id}")
            
            # Extract hostname from client_id (format: username@hostname)
            if '@' in client_id:
                hostname = client_id.split('@')[1]
            else:
                hostname = client_id
            
            # Queue info command for the client
            info_command = {
                "plugin": "client_control",
                "action": "get_client_info",
                "args": [],
                "kwargs": {},
                "timestamp": time.time()
            }
            
            # Use shared commands manager
            from commands_manager import add_command
            
            success = add_command(hostname, info_command)
            
            logger.info(f"✅ Info command queued for client {client_id} (hostname: {hostname})")
            
            return jsonify({
                "success": True,
                "message": f"Info request sent to client {client_id}",
                "command": info_command
            })
            
        except Exception as e:
            logger.error(f"❌ Error sending info request to client {client_id}: {e}")
            return jsonify({
                "success": False,
                "message": f"Failed to send info request: {str(e)}"
            }), 500
