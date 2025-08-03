#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Database Helper
==================================

Database operations and task management for the Octopus orchestration system.
Handles SQLite operations for tasks, executions, and client management.
"""

import sqlite3
import time
import os
import sys
import logging

# Add parent directory to path for shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_FILE, CLIENT_TIMEOUT
from constants import TaskStatus, TaskOwnership, TaskType, Database
from utils import get_current_timestamp, is_task_completed, sanitize_string, safe_json_loads

logger = logging.getLogger(__name__)

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                owner TEXT,
                plugin TEXT,
                action TEXT,
                args TEXT,
                kwargs TEXT,
                type TEXT,
                execution_start_time TEXT,
                execution_end_time TEXT,
                interval TEXT,
                status TEXT,
                executor TEXT,
                result TEXT,
                updated_at REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                client TEXT,
                status TEXT,
                result TEXT,
                updated_at REAL,
                UNIQUE(task_id, client)
            )
        ''')

def get_tasks():
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT * FROM tasks")
        tasks = {}
        for row in cur.fetchall():
            columns = [col[0] for col in cur.description]
            task = dict(zip(columns, row))
            # Add executions for all tasks (not just ALL tasks)
            exec_cur = conn.execute("SELECT id, client, status, result, updated_at FROM executions WHERE task_id=?", (task["id"],))
            task["executions"] = [
                {"id": r[0], "client": r[1], "status": r[2], "result": r[3], "updated_at": r[4]} for r in exec_cur.fetchall()
            ]
            tasks[task["id"]] = task
        return tasks

def add_task(task):
    init_db()
    task_id = task.get("id") or str(int(time.time() * 1000))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            INSERT OR REPLACE INTO tasks (id, owner, plugin, action, args, kwargs, type, execution_start_time, execution_end_time, interval, status, executor, result, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            task.get("owner"),
            task.get("plugin"),
            task.get("action", "run"),
            str(task.get("args", [])),
            str(task.get("kwargs", {})),
            task.get("type"),
            task.get("execution_start_time"),
            task.get("execution_end_time"),
            task.get("interval"),
            "Created",  # Changed from "pending" to "Created"
            task.get("executor", ""),
            task.get("result", ""),
            time.time()
        ))
        conn.commit()
    return task_id

def update_task(task_id, updates):
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        if not row:
            return False
        columns = [col[0] for col in cur.description]
        task = dict(zip(columns, row))
        task.update(updates)
        conn.execute('''
            UPDATE tasks SET owner=?, plugin=?, action=?, args=?, kwargs=?, type=?, execution_start_time=?, execution_end_time=?, interval=?, status=?, executor=?, result=?, updated_at=?
            WHERE id=?
        ''', (
            task.get("owner"),
            task.get("plugin"),
            task.get("action", "run"),
            str(task.get("args", [])),
            str(task.get("kwargs", {})),
            task.get("type"),
            task.get("execution_start_time"),
            task.get("execution_end_time"),
            task.get("interval"),
            task.get("status", "Created"),  # Changed from "pending" to "Created"
            task.get("executor", ""),
            task.get("result", ""),
            time.time(),
            task_id
        ))
        # Insert/update executions table only if there's actual result data (not just assignment)
        client = updates.get("executor")
        result = updates.get("result")
        exec_status = updates.get("status")
        
        # Only create execution record if we have actual execution results
        if client and (result or exec_status in ("success", "failed", "Done")):
            conn.execute('''
                INSERT INTO executions (task_id, client, status, result, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(task_id, client) DO UPDATE SET
                    status=excluded.status,
                    result=excluded.result,
                    updated_at=excluded.updated_at
            ''', (
                task_id,
                client,
                exec_status or "completed",
                str(result or ""),
                time.time()
            ))
        conn.commit()
    return True

def delete_task(task_id):
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.execute("DELETE FROM executions WHERE task_id=?", (task_id,))
        conn.commit()
    return True

def get_db_file():
    """Return the database file path"""
    return DB_FILE

def get_plugin_names():
    """Get list of available plugin names from the plugins directory"""
    from config import PLUGINS_FOLDER
    import os
    
    plugin_names = []
    if os.path.exists(PLUGINS_FOLDER):
        for filename in os.listdir(PLUGINS_FOLDER):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_names.append(filename[:-3])  # Remove .py extension
    return plugin_names

def get_owner_options(active_clients):
    """Get list of owner options including active client usernames"""
    owners = ["ALL", "Anyone"]
    # Add active client usernames
    for client in active_clients.values():
        username = client.get('username', '')
        if username and username not in owners:
            owners.append(username)
    return owners

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

def assign_all_tasks(tasks, clients):
    """
    Assign tasks to appropriate executors based on owner type.
    This handles ALL, Anyone, and specific user assignments.
    """
    import random
    import logging
    
    logger = logging.getLogger("octopus_server")
    available_users = [str(client['username']) for client in clients.values() if 'username' in client]
    logger.info(f"Available users for task assignment: {available_users}")
    
    for tid, task in tasks.items():
        owner = task.get("owner")
        executor = task.get("executor")
        status = task.get("status", "")
        
        logger.info(f"Processing task {tid}: owner={owner}, executor={executor}, status={status}")
        
        # Skip if task is already done
        if status in ("success", "failed", "Done"):
            continue
            
        # Handle different owner types
        if owner == "ALL":
            # ALL tasks should be marked as Active immediately so all clients can pick them up
            if not executor:
                logger.info(f"Assigning ALL task {tid} to all clients")
                update_task(tid, {"executor": "ALL", "status": "Active"})
                task["executor"] = "ALL"
                
        elif owner == "Anyone":
            # Assign to a random available client
            if (not executor or executor == "") and available_users:
                chosen = random.choice(available_users)
                logger.info(f"Assigning Anyone task {tid} to {chosen}")
                update_task(tid, {"executor": chosen, "status": "Active"})
                task["executor"] = chosen
                
        else:
            # Specific user assignment
            if owner in available_users:
                if not executor or executor == "":
                    logger.info(f"Assigning specific user task {tid} to {owner}")
                    update_task(tid, {"executor": owner, "status": "Active"}) 
                    task["executor"] = owner
            else:
                logger.warning(f"Task {tid} owner '{owner}' is not in available users: {available_users}")

def compute_task_status(task, clients):
    """
    Returns the status for a task:
    - Created: when only created (no executor assigned)
    - Active: executor assigned but not executed yet
    - Done: Adhoc executed or now > end time for Schedule
    
    NOTE: This function should NOT override database status for completed tasks
    """
    import time
    now = time.time()
    
    executor = task.get("executor")
    task_type = task.get("type")
    owner = task.get("owner")
    db_status = task.get("status", "")
    
    # If task is already marked as completed in database, don't override
    if TaskStatus.is_completed(db_status):
        logger.debug(f"Task {task.get('id')} already completed with status: {db_status}")
        return db_status
    
    # If no executor assigned, it's Created
    if not executor or executor == "":
        return TaskStatus.CREATED
    
    # Check if task type is Adhoc
    if task_type == TaskType.ADHOC:
        # Check if any execution for this task is success/failed
        executions = task.get("executions", [])
        if executions:
            # For ALL tasks, check if any client has completed it
            if owner == TaskOwnership.ALL:
                if any(TaskStatus.is_completed(exec.get("status")) for exec in executions):
                    return TaskStatus.ACTIVE  # Still active until all clients complete or task expires
            else:
                # For specific user or Anyone tasks, check if completed
                if any(TaskStatus.is_completed(exec.get("status")) for exec in executions):
                    return TaskStatus.DONE
        
        # If executor is assigned but no executions yet, it's Active
        return TaskStatus.ACTIVE
    
    # Check if task type is Schedule
    elif task_type == "Schedule":
        end_time = task.get("execution_end_time")
        if end_time:
            try:
                # end_time may be string or None
                if isinstance(end_time, str) and end_time:
                    # Try to parse as timestamp or ISO string
                    if end_time.isdigit():
                        end_ts = float(end_time)
                    else:
                        import datetime
                        end_ts = datetime.datetime.fromisoformat(end_time).timestamp()
                else:
                    end_ts = float(end_time)
                if now > end_ts:
                    return "Done"
            except Exception:
                pass
        # If not past end time and has executor, it's active
        return "Active"
    
    # Default case
    return "Created"

def get_active_clients(clients, now=None, timeout=30):
    """
    Returns a dict of clients that have sent heartbeat within the last `timeout` seconds.
    """
    if now is None:
        import time
        now = time.time()
    return {
        key: client
        for key, client in clients.items()
        if client.get("last_heartbeat") and now - client["last_heartbeat"] <= timeout
    }

def add_execution_result(task_id, client, status, result):
    """
    Add or update an execution result for a task.
    This is specifically for recording task execution results.
    """
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        logger.info(f"Adding execution result: task_id={task_id}, client={client}, status={status}")
        conn.execute('''
            INSERT INTO executions (task_id, client, status, result, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(task_id, client) DO UPDATE SET
                status=excluded.status,
                result=excluded.result,
                updated_at=excluded.updated_at
        ''', (
            task_id,
            client,
            status,
            str(result),
            time.time()
        ))
        conn.commit()
        logger.info(f"Execution result added successfully for task {task_id}")
    return True