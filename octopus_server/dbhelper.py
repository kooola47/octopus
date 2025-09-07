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
import threading
from constants import TaskStatus, ExecutionStatus
from contextlib import contextmanager

# Add parent directory to path for shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import get_current_config
config = get_current_config()
DB_FILE = config.DB_FILE
PLUGINS_FOLDER = config.PLUGINS_FOLDER
from constants import TaskStatus, TaskOwnership, TaskType, Database
from helpers.utils import get_current_timestamp, is_task_completed, sanitize_string, safe_json_loads

logger = logging.getLogger(__name__)

# Database connection lock for thread safety
_db_lock = threading.RLock()

def init_db():
    with _db_lock:
        with sqlite3.connect(DB_FILE) as conn:
            # Enable WAL mode for better concurrent performance
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL') 
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=memory')
            conn.execute('PRAGMA mmap_size=268435456')  # 256MB
            
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
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT UNIQUE,
                    task_id TEXT,
                    client TEXT,
                    status TEXT,
                    result TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS heartbeats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    hostname TEXT,
                    ip_address TEXT,
                    cpu_usage REAL DEFAULT 0.0,
                    memory_usage REAL DEFAULT 0.0,
                    login_time REAL,
                    since_last_heartbeat REAL,
                    timestamp REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(username, hostname, ip_address)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_active INTEGER DEFAULT 1,
                    last_login REAL,
                    full_name TEXT,
                    user_ident TEXT,
                    tags TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_execution_id ON executions(execution_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_task_id ON executions(task_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_client ON executions(client)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_updated_at ON executions(updated_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_heartbeats_username ON heartbeats(username)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_heartbeats_hostname ON heartbeats(hostname)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_heartbeats_timestamp ON heartbeats(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_heartbeats_user_host_time ON heartbeats(username, hostname, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            
            # Plugin management tables
            conn.execute('''
                CREATE TABLE IF NOT EXISTS plugin_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_name TEXT NOT NULL,
                    plugin_code TEXT NOT NULL,
                    description TEXT,
                    author TEXT NOT NULL,
                    language TEXT DEFAULT 'python',
                    status TEXT DEFAULT 'pending',
                    created_at REAL,
                    updated_at REAL,
                    reviewed_by TEXT,
                    reviewed_at REAL,
                    review_notes TEXT,
                    test_results TEXT,
                    deployment_path TEXT,
                    version TEXT DEFAULT '1.0.0',
                    UNIQUE(plugin_name)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS plugin_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER,
                    test_type TEXT,
                    test_status TEXT,
                    test_output TEXT,
                    test_error TEXT,
                    executed_at REAL,
                    FOREIGN KEY (submission_id) REFERENCES plugin_submissions (id)
                )
            ''')
            
            # Create indexes for plugin tables
            conn.execute('CREATE INDEX IF NOT EXISTS idx_plugin_submissions_status ON plugin_submissions(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_plugin_submissions_author ON plugin_submissions(author)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_plugin_submissions_created_at ON plugin_submissions(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_plugin_tests_submission_id ON plugin_tests(submission_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_plugin_tests_status ON plugin_tests(test_status)')
            
            # Migrate existing tables to add missing columns
            migrate_tasks_table(conn)
            migrate_users_table(conn)
            
            # Create default admin user if no users exist
            create_default_admin_user(conn)
            
            # Backfill created_at for existing rows if column exists but values are NULL
            try:
                conn.execute('UPDATE tasks SET created_at = COALESCE(created_at, updated_at)')
            except Exception:
                pass
            conn.commit()

def create_default_admin_user(conn):
    """Create a default admin user if no users exist"""
    import time
    import hashlib
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        print("Creating default admin user...")
        current_time = time.time()
        
        # Default admin credentials: admin/admin
        username = "admin"
        password = "admin"
        password_hash = hash_password(password)  # Use the same salted hash as other users
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, "admin@localhost", password_hash, "admin", 1, current_time, current_time))
        
        print(f"Default admin user created: {username}/admin")

def migrate_tasks_table(conn):
    """Add missing columns to existing tasks table"""
    try:
        # Check if created_at column exists
        cursor = conn.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding created_at column to tasks table...")
            conn.execute('ALTER TABLE tasks ADD COLUMN created_at REAL')
            # Set current timestamp for existing tasks
            now_ts = time.time()
            conn.execute('UPDATE tasks SET created_at = ?', (now_ts,))
            
        if 'updated_at' not in columns:
            print("Adding updated_at column to tasks table...")
            conn.execute('ALTER TABLE tasks ADD COLUMN updated_at REAL')
            # Set current timestamp for existing tasks
            now_ts = time.time()
            conn.execute('UPDATE tasks SET updated_at = ?', (now_ts,))
            
    except Exception as e:
        print(f"Migration warning: {e}")
        # Continue execution even if migration fails

def migrate_users_table(conn):
    """Add missing columns to existing users table"""
    import time
    try:
        # Check if new columns exist
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'full_name' not in columns:
            print("Adding full_name column to users table...")
            conn.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
            
        if 'user_ident' not in columns:
            print("Adding user_ident column to users table...")
            conn.execute('ALTER TABLE users ADD COLUMN user_ident TEXT')
            
        if 'tags' not in columns:
            print("Adding tags column to users table...")
            conn.execute('ALTER TABLE users ADD COLUMN tags TEXT')
            
        if 'status' not in columns:
            print("Adding status column to users table...")
            conn.execute('ALTER TABLE users ADD COLUMN status TEXT DEFAULT "active"')
            # Update existing users to have active status
            conn.execute('UPDATE users SET status = "active" WHERE status IS NULL')
            
    except Exception as e:
        print(f"User table migration warning: {e}")
        # Continue execution even if migration fails

@contextmanager
def get_db_connection():
    """Thread-safe database connection context manager"""
    connection = None
    try:
        with _db_lock:
            connection = sqlite3.connect(DB_FILE, timeout=30.0)  # 30 second timeout
            connection.execute('PRAGMA busy_timeout=30000')  # 30 second busy timeout
            yield connection
    except sqlite3.OperationalError as e:
        logger.error(f"Database operation error: {e}")
        raise
    finally:
        if connection:
            connection.close()

def get_tasks():
    init_db()
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM tasks")
        tasks = {}
        for row in cur.fetchall():
            columns = [col[0] for col in cur.description]
            task = dict(zip(columns, row))
            # Add executions for all tasks (not just ALL tasks)
            exec_cur = conn.execute("SELECT id, execution_id, client, status, result, created_at, updated_at FROM executions WHERE task_id=? ORDER BY created_at DESC", (task["id"],))
            task["executions"] = [
                {
                    "id": r[0], 
                    "execution_id": r[1], 
                    "client": r[2], 
                    "status": r[3], 
                    "result": r[4], 
                    "created_at": r[5],
                    "updated_at": r[6]
                } for r in exec_cur.fetchall()
            ]
            tasks[task["id"]] = task
        return tasks

def add_task(task):
    init_db()
    task_id = task.get("id") or str(int(time.time() * 1000))
    
    # Convert datetime-local strings to timestamps for consistent storage
    def convert_datetime_to_timestamp(dt_string):
        if not dt_string:
            return None
        try:
            import datetime
            # Parse datetime-local format: YYYY-MM-DDTHH:MM
            dt = datetime.datetime.fromisoformat(dt_string.replace('T', ' '))
            return dt.timestamp()
        except Exception:
            # If parsing fails, return as-is (might already be a timestamp)
            return dt_string
    
    start_time = convert_datetime_to_timestamp(task.get("execution_start_time"))
    end_time = convert_datetime_to_timestamp(task.get("execution_end_time"))
    
    with get_db_connection() as conn:
        now_ts = time.time()
        conn.execute('''
            INSERT OR REPLACE INTO tasks (id, owner, plugin, action, args, kwargs, type, execution_start_time, execution_end_time, interval, status, executor, result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            task.get("owner"),
            task.get("plugin"),
            task.get("action", "run"),
            str(task.get("args", [])),
            str(task.get("kwargs", {})),
            task.get("type", "adhoc"),
            start_time,
            end_time,
            task.get("interval"),
            TaskStatus.PENDING,  # Use centralized TaskStatus constant
            task.get("executor", ""),
            task.get("result", ""),
            now_ts,
            now_ts
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
        
        # Debug logging for task updates
        logger.info(f"UPDATE_TASK: Task {task_id} update requested with: {updates}")
        logger.info(f"UPDATE_TASK: Current task type: {task.get('type')}, status: {task.get('status')}")
        
        # Before applying updates, check if this is a scheduled task being marked as Done
        original_type = (task.get("type") or "").lower()
        new_status = (updates.get("status") or "").lower()
        
        # Prevent scheduled tasks from being marked as Done unless execution window has ended
        if (original_type in ["scheduled", "schedule"] and 
            new_status in [TaskStatus.COMPLETED, "Inactive"] and  # Standardized task completion statuses
            task.get("execution_end_time")):
            try:
                end_time_val = task.get("execution_end_time")
                if end_time_val is not None:
                    end_timestamp = float(end_time_val)
                    current_time = time.time()
                    logger.info(f"UPDATE_TASK: Scheduled task {task_id} - current: {current_time}, end: {end_timestamp}")
                    if current_time < end_timestamp:
                        # Still within execution window, don't mark as Done
                        logger.info(f"UPDATE_TASK: Preventing scheduled task {task_id} from being marked as Done - still within execution window")
                        updates = updates.copy()  # Don't modify the original
                        updates.pop("status", None)  # Remove status update
                    else:
                        logger.info(f"UPDATE_TASK: Allowing scheduled task {task_id} to be marked as Done - execution window ended")
            except (ValueError, TypeError):
                logger.warning(f"UPDATE_TASK: Invalid end_time format for scheduled task {task_id}: {task.get('execution_end_time')}")
        
        task.update(updates)
        now_ts = time.time()
        logger.info(f"UPDATE_TASK: Final status for task {task_id}: {task.get('status')}")
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
            task.get("status", TaskStatus.PENDING),  # Use centralized TaskStatus constant
            task.get("executor", ""),
            task.get("result", ""),
            now_ts,
            task_id
        ))
        # Note: Execution records should only be created by the proper execution flow
        # via add_execution_result() function, not during task status updates
        conn.commit()
    return True

def delete_task(task_id):
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.execute("DELETE FROM executions WHERE task_id=?", (task_id,))
        conn.commit()
    return True

def claim_task_for_execution(task_id, executor):
    """
    Atomically claim a task for execution by setting it to 'running' status.
    Returns (success, message) tuple.
    """
    logger = logging.getLogger("octopus_server")
    try:
        with get_db_connection() as conn:
            # First, get the current task status
            cursor = conn.execute("SELECT status, executor FROM tasks WHERE id=?", (task_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, f"Task {task_id} not found"
            
            current_status, current_executor = row
            
            # Check if task is already being executed
            if current_status == TaskStatus.RUNNING:
                if current_executor == executor:
                    return True, f"Task {task_id} already claimed by {executor}"
                else:
                    return False, f"Task {task_id} already being executed by {current_executor}"
            
            # Check if task is in a state that can be executed
            if current_status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.FAILED]:
                return False, f"Task {task_id} is already {current_status}"
            
            # Atomically claim the task
            cursor = conn.execute("""
                UPDATE tasks 
                SET status = ?, executor = ?, updated_at = ?
                WHERE id = ? AND status NOT IN (?, ?, ?)
            """, (TaskStatus.RUNNING, executor, time.time(), task_id, 
                 TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.CANCELLED))
            
            # Check if we actually updated a row
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Task {task_id} claimed by {executor}")
                return True, f"Task {task_id} claimed successfully"
            else:
                # Someone else claimed it between our SELECT and UPDATE
                return False, f"Task {task_id} was claimed by another process"
                
    except Exception as e:
        logger.error(f"Error claiming task {task_id}: {str(e)}")
        return False, f"Database error: {str(e)}"

def get_db_file():
    """Return the database file path"""
    return DB_FILE

def get_plugin_names():
    """Get list of available plugin names from the plugins directory"""
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

def assign_all_tasks(tasks, clients):
    """
    Assign tasks to appropriate executors based on owner type.
    This handles ALL, Anyone, and specific user assignments.
    IMPORTANT: Only assigns tasks to ONLINE clients (clients passed in are pre-filtered by get_active_clients).
    """
    import random
    import logging
    import threading
    import time
    
    logger = logging.getLogger("octopus_server")
    
    # Global lock to prevent concurrent task assignments
    if not hasattr(assign_all_tasks, '_assignment_lock'):
        assign_all_tasks._assignment_lock = threading.Lock()
        assign_all_tasks._last_assignment = 0
    
    # Rate limiting: prevent assignments more than once per second
    current_time = time.time()
    if current_time - assign_all_tasks._last_assignment < 1.0:
        logger.debug("Skipping task assignment due to rate limiting")
        return
    
    # Try to acquire lock, but don't block if another assignment is in progress
    if not assign_all_tasks._assignment_lock.acquire(blocking=False):
        logger.debug("Skipping task assignment - another assignment in progress")
        return
    
    try:
        assign_all_tasks._last_assignment = current_time
        
        # Only use clients that are currently online (pre-filtered by caller)
        logger.info(f"Client data received: {list(clients.keys())} clients")
        logger.info(f"Client data structure sample: {list(clients.values())[:2] if clients else 'No clients'}")
        available_users = [str(client['username']) for client in clients.values() if 'username' in client]
        logger.info(f"Available users for task assignment: {available_users}")
        
        for tid, task in tasks.items():
            owner = task.get("owner")
            executor = task.get("executor")
            status = task.get("status", "")
            
            logger.debug(f"Processing task {tid}: owner={owner}, executor={executor}, status={status}")
            
            # Skip if task is already done
            if TaskStatus.is_final_state(status):
                continue
                
            # Skip if task already has an executor (prevent re-assignment)
            if executor and executor.strip():
                continue
                
            # Handle different owner types
            if owner == "ALL":
                # ALL tasks should be marked as running immediately so all clients can pick them up
                logger.info(f"Assigning ALL task {tid} to all clients")
                update_task(tid, {"executor": "ALL", "status": TaskStatus.RUNNING})
                task["executor"] = "ALL"
                    
            elif owner == "Anyone" or not owner or owner.strip() == "":
                # Assign to a random available client (Anyone or empty owner)
                if available_users:
                    chosen = random.choice(available_users)
                    logger.info(f"Assigning Anyone task {tid} to {chosen}")
                    update_task(tid, {"executor": chosen, "status": TaskStatus.RUNNING})
                    task["executor"] = chosen
                else:
                    logger.warning(f"No available users to assign Anyone task {tid}, leaving as unassigned")
                    # Set executor to empty string instead of leaving it as "ALL"
                    update_task(tid, {"executor": "", "status": TaskStatus.PENDING})
                    task["executor"] = ""
                    
            else:
                # Specific user assignment
                if owner in available_users:
                    logger.info(f"Assigning specific user task {tid} to {owner}")
                    update_task(tid, {"executor": owner, "status": TaskStatus.RUNNING}) 
                    task["executor"] = owner
                else:
                    logger.warning(f"Task {tid} owner '{owner}' is not in available users: {available_users}")
                    
    finally:
        assign_all_tasks._assignment_lock.release()

def compute_task_status(task, clients):
    """
    Returns the status for a task using centralized TaskStatus constants:
    - pending: when only created (no executor assigned)
    - running: executor assigned but not executed yet
    - completed: Adhoc executed or now > end time for Schedule
    - failed/cancelled: based on execution results
    
    NOTE: This function should NOT override database status for completed tasks
    """
    import time
    now = time.time()
    
    executor = task.get("executor")
    task_type = task.get("type")
    owner = task.get("owner")
    db_status = task.get("status", "")
    
    # If task is already marked as completed in database, don't override
    if TaskStatus.is_final_state(db_status):
        logger.debug(f"Task {task.get('id')} already completed with status: {db_status}")
        return db_status
    
    # If no executor assigned, it's pending
    if not executor or executor == "":
        return TaskStatus.PENDING
    
    # Check if task type is Adhoc
    if task_type == TaskType.ADHOC:
        # Check if any execution for this task is success/failed
        executions = task.get("executions", [])
        if executions:
            # For ALL tasks, complete when any client succeeds (first success wins)
            if owner == TaskOwnership.ALL:
                if any(TaskStatus.is_final_state(exec.get("status")) for exec in executions):
                    return TaskStatus.COMPLETED  # Complete when any client completes the ALL task
            else:
                # For specific user or Anyone tasks, check if completed
                if any(TaskStatus.is_final_state(exec.get("status")) for exec in executions):
                    return TaskStatus.COMPLETED
        
        # If executor is assigned but no executions yet, it's running
        return TaskStatus.RUNNING
    
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
                    return TaskStatus.COMPLETED
            except Exception:
                pass
        # If not past end time and has executor, it's running
        return TaskStatus.RUNNING
    
    # Default case
    return TaskStatus.PENDING

def get_active_clients(clients, now=None, timeout=30):
    """
    Returns a dict of clients that have sent heartbeat within the last `timeout` seconds.
    These are considered ONLINE clients available for task assignment.
    Default timeout=30 seconds for strict availability, but should be called with 
    timeout=60 to align with UI "online" status definition.
    """
    if now is None:
        import time
        now = time.time()
    return {
        key: client
        for key, client in clients.items()
        if client.get("last_heartbeat") and now - client["last_heartbeat"] <= timeout
    }

def update_execution_result(execution_id, status, result):
    """
    Update an existing execution result by execution_id.
    Returns True if update was successful, False if execution_id not found.
    """
    import logging
    import time
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    current_time = time.time()
    
    with sqlite3.connect(DB_FILE) as conn:
        logger.info(f"Updating execution result: execution_id={execution_id}, status={status}")
        
        # Check if execution exists
        cursor = conn.execute('SELECT id FROM executions WHERE execution_id = ?', (execution_id,))
        if not cursor.fetchone():
            logger.warning(f"Execution {execution_id} not found for update")
            return False
        
        # Update the execution record
        conn.execute('''
            UPDATE executions SET status = ?, result = ?, updated_at = ? 
            WHERE execution_id = ?
        ''', (status, str(result), current_time, execution_id))
        
        conn.commit()
        logger.info(f"Successfully updated execution {execution_id}")
        return True

def add_execution_result(task_id, client, status, result, execution_id=None):
    """
    Add execution result for a task with unique execution ID.
    Each execution gets its own record, allowing multiple executions per task per client.
    If execution_id is provided, use it; otherwise generate a new one.
    Status is normalized using centralized ExecutionStatus system.
    """
    import logging
    import time
    from constants import ExecutionStatus
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    # Normalize status using centralized system
    normalized_status = ExecutionStatus.normalize(status)
    logger.info(f"Normalizing status '{status}' to '{normalized_status}'")
    
    # Use provided execution_id or generate unique execution ID
    if execution_id is None:
        execution_id = f"{task_id}_{client}_{int(time.time() * 1000)}"
    current_time = time.time()

    with sqlite3.connect(DB_FILE) as conn:
        logger.info(f"Adding execution result: execution_id={execution_id}, task_id={task_id}, client={client}, status={normalized_status}")        # Always insert a new execution record (no conflict resolution)
        conn.execute('''
            INSERT INTO executions (execution_id, task_id, client, status, result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution_id,
            task_id,
            client,
            normalized_status,  # Use normalized status
            str(result),
            current_time,
            current_time
        ))
        
        # For adhoc tasks, update the task status to Done when execution completes
        # Check if this is an adhoc task and if the execution status indicates completion
        if normalized_status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED]:  # Only Success and Failed indicate completion
            # Get the task type and timing info
            task_row = conn.execute('SELECT type, execution_end_time FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if task_row:
                task_type, end_time = task_row
                
                if task_type.lower() == 'adhoc':
                    # Update task status to Done for completed adhoc tasks  
                    # Use standardized execution statuses: Success -> Done, Failed -> Failed
                    task_status = 'Done' if status == 'Success' else 'Failed'
                    conn.execute('''
                        UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?
                    ''', (task_status, current_time, task_id))
                    logger.info(f"Updated adhoc task {task_id} status to {task_status}")
                
                elif task_type in ['scheduled', 'Schedule'] and end_time:
                    # For scheduled tasks, check if execution window has ended
                    try:
                        end_timestamp = float(end_time)
                        if current_time > end_timestamp:
                            # Execution window has ended, mark as Done
                            conn.execute('''
                                UPDATE tasks SET status = 'Done', updated_at = ? WHERE id = ?
                            ''', (current_time, task_id))
                            logger.info(f"Updated scheduled task {task_id} status to Done - execution window ended")
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid end_time format for scheduled task {task_id}: {end_time}")
        
        conn.commit()
        logger.info(f"Execution result added successfully: execution_id={execution_id}, task_id={task_id}")
    return execution_id


def update_expired_scheduled_tasks():
    """Check and update status for scheduled tasks whose execution window has ended"""
    import time
    
    with sqlite3.connect(DB_FILE) as conn:
        current_time = time.time()
        
        # Find scheduled tasks that are still Active but past their end time
        cursor = conn.execute('''
            SELECT id, execution_end_time FROM tasks 
            WHERE type IN ('scheduled', 'Schedule') 
            AND status = 'Active' 
            AND execution_end_time IS NOT NULL
        ''')
        
        expired_tasks = []
        for task_id, end_time in cursor.fetchall():
            try:
                end_timestamp = float(end_time)
                if current_time > end_timestamp:
                    expired_tasks.append(task_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid end_time format for task {task_id}: {end_time}")
        
        # Update expired tasks to Done status
        if expired_tasks:
            for task_id in expired_tasks:
                conn.execute('''
                    UPDATE tasks SET status = 'Done', updated_at = ? WHERE id = ?
                ''', (current_time, task_id))
                logger.info(f"Marked expired scheduled task {task_id} as Done")
            
            conn.commit()
            logger.info(f"Updated {len(expired_tasks)} expired scheduled tasks")
        
        return len(expired_tasks)


# ========================================
# USER MANAGEMENT FUNCTIONS
# ========================================

def hash_password(password, salt=None):
    """Hash a password with salt using SHA-256"""
    import hashlib
    import secrets
    
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify a password against the stored hash"""
    import hashlib
    
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def authenticate_user(username, password):
    """Authenticate a user and return user info if valid"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    with sqlite3.connect(DB_FILE) as conn:
        user_row = conn.execute('''
            SELECT id, username, email, password_hash, role, is_active, last_login
            FROM users WHERE username = ? AND is_active = 1
        ''', (username,)).fetchone()
        
        if user_row and verify_password(password, user_row[3]):
            # Update last login time
            current_time = time.time()
            conn.execute('''
                UPDATE users SET last_login = ?, updated_at = ? WHERE id = ?
            ''', (current_time, current_time, user_row[0]))
            conn.commit()
            
            return {
                'id': user_row[0],
                'username': user_row[1],
                'email': user_row[2],
                'role': user_row[4],
                'is_active': user_row[5],
                'last_login': current_time
            }
    return None

def create_user(username, password, email='', role='user', is_active=True, full_name='', user_ident='', tags=''):
    """Create a new user"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    # Validate role
    if role not in ['admin', 'user', 'operator', 'viewer']:
        logger.error(f"Invalid role: {role}")
        return None
    
    # Hash password
    password_hash = hash_password(password)
    current_time = time.time()
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute('''
                INSERT INTO users (username, email, password_hash, role, is_active, full_name, user_ident, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, is_active, full_name, user_ident, tags, current_time, current_time))
            
            user_id = cursor.lastrowid
            conn.commit()
            logger.info(f"User created successfully: {username} (ID: {user_id})")
            return user_id
            
    except sqlite3.IntegrityError:
        logger.error(f"User creation failed: username {username} already exists")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    init_db()
    
    with sqlite3.connect(DB_FILE) as conn:
        user_row = conn.execute('''
            SELECT id, username, email, role, is_active, created_at, updated_at, last_login, full_name, user_ident, tags, status
            FROM users WHERE id = ?
        ''', (user_id,)).fetchone()
        
        if user_row:
            return {
                'id': user_row[0],
                'username': user_row[1],
                'email': user_row[2],
                'role': user_row[3],
                'is_active': user_row[4],
                'created_at': user_row[5],
                'updated_at': user_row[6],
                'last_login': user_row[7],
                'full_name': user_row[8],
                'user_ident': user_row[9],
                'tags': user_row[10],
                'status': user_row[11] or 'active'  # Default to 'active' if None
            }
    return None

def get_all_users():
    """Get all users (both active and inactive)"""
    init_db()
    
    with sqlite3.connect(DB_FILE) as conn:
        user_rows = conn.execute('''
            SELECT id, username, email, role, is_active, created_at, updated_at, last_login, full_name, user_ident, tags, status
            FROM users ORDER BY created_at DESC
        ''').fetchall()
        
        users = []
        for row in user_rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'is_active': row[4],
                'status': row[11] or ('active' if row[4] else 'inactive'),  # Use status column or fall back to is_active
                'created_at': row[5],
                'updated_at': row[6],
                'last_login': row[7],
                'full_name': row[8],
                'user_ident': row[9],
                'tags': row[10]
            })
        return users

def update_user(user_id, **kwargs):
    """Update user information"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    # Build update query dynamically
    allowed_fields = ['username', 'email', 'role', 'status', 'user_ident', 'tags', 'full_name']
    update_fields = []
    update_values = []
    
    for field, value in kwargs.items():
        if field == 'password':
            # Handle password hashing - use the same salted hash as create_user
            password_hash = hash_password(value)
            update_fields.append("password_hash = ?")
            update_values.append(password_hash)
        elif field in allowed_fields:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    if not update_fields:
        return False
    
    # Add updated_at
    update_fields.append("updated_at = ?")
    update_values.append(time.time())
    update_values.append(user_id)
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(f'''
                UPDATE users SET {', '.join(update_fields)} WHERE id = ?
            ''', update_values)
            
            conn.commit()
            logger.info(f"User {user_id} updated successfully")
            return True
            
    except sqlite3.IntegrityError:
        logger.error(f"User update failed: constraint violation")
        return False

def update_user_password(user_id, new_password):
    """Update user password"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    password_hash = hash_password(new_password)
    current_time = time.time()
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?
        ''', (password_hash, current_time, user_id))
        
        conn.commit()
        logger.info(f"Password updated for user {user_id}")
        return True

def delete_user(user_id):
    """Permanently delete user from database"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Check if user exists first
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.error(f"User {user_id} not found for deletion")
                return False
            
            # Permanently delete the user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"User {user[1]} (ID: {user_id}) permanently deleted")
                return True
            else:
                logger.error(f"Failed to delete user {user_id} - no rows affected")
                return False
                
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return False

def toggle_user_status(user_id, new_status):
    """Toggle user active/inactive status"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    current_time = time.time()
    is_active = 1 if new_status == 'active' else 0
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Check if user exists first
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.error(f"User {user_id} not found for status update")
                return False
            
            # Update user status
            cursor.execute('''
                UPDATE users SET is_active = ?, updated_at = ? WHERE id = ?
            ''', (is_active, current_time, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                status_text = "activated" if is_active else "deactivated"
                logger.info(f"User {user[1]} (ID: {user_id}) {status_text} successfully")
                return True
            else:
                logger.error(f"Failed to update status for user {user_id} - no rows affected")
                return False
                
    except Exception as e:
        logger.error(f"Error updating status for user {user_id}: {e}")
        return False

# ========================================
# PLUGIN MANAGEMENT FUNCTIONS
# ========================================

def submit_plugin(plugin_name, plugin_code, description, author, language='python'):
    """Submit a new plugin for review"""
    import time
    
    with _db_lock:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                current_time = time.time()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO plugin_submissions 
                    (plugin_name, plugin_code, description, author, language, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                ''', (plugin_name, plugin_code, description, author, language, current_time, current_time))
                
                submission_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Plugin '{plugin_name}' submitted for review by {author}")
                return submission_id
                
        except Exception as e:
            logger.error(f"Error submitting plugin: {e}")
            return None

def get_plugin_submissions(status=None, author=None):
    """Get plugin submissions, optionally filtered by status or author"""
    with _db_lock:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM plugin_submissions'
                params = []
                conditions = []
                
                if status:
                    conditions.append('status = ?')
                    params.append(status)
                    
                if author:
                    conditions.append('author = ?')
                    params.append(author)
                    
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
                    
                query += ' ORDER BY created_at DESC'
                
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting plugin submissions: {e}")
            return []

def update_plugin_submission_status(submission_id, status, reviewer=None, notes=None):
    """Update plugin submission status"""
    import time
    
    with _db_lock:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                current_time = time.time()
                
                cursor.execute('''
                    UPDATE plugin_submissions 
                    SET status = ?, updated_at = ?, reviewed_by = ?, reviewed_at = ?, review_notes = ?
                    WHERE id = ?
                ''', (status, current_time, reviewer, current_time, notes, submission_id))
                
                conn.commit()
                logger.info(f"Plugin submission {submission_id} status updated to {status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating plugin submission status: {e}")
            return False

def record_plugin_test(submission_id, test_type, test_status, test_output=None, test_error=None):
    """Record plugin test results"""
    import time
    
    with _db_lock:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                current_time = time.time()
                
                cursor.execute('''
                    INSERT INTO plugin_tests 
                    (submission_id, test_type, test_status, test_output, test_error, executed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (submission_id, test_type, test_status, test_output, test_error, current_time))
                
                conn.commit()
                logger.info(f"Plugin test recorded for submission {submission_id}: {test_type} - {test_status}")
                return True
                
        except Exception as e:
            logger.error(f"Error recording plugin test: {e}")
            return False

def get_plugin_tests(submission_id):
    """Get test results for a plugin submission"""
    with _db_lock:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM plugin_tests WHERE submission_id = ? ORDER BY executed_at DESC', (submission_id,))
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting plugin tests: {e}")
            return []

def deploy_plugin(submission_id, deployment_path):
    """Mark plugin as deployed"""
    import time
    
    with _db_lock:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                current_time = time.time()
                
                cursor.execute('''
                    UPDATE plugin_submissions 
                    SET status = 'deployed', deployment_path = ?, updated_at = ?
                    WHERE id = ?
                ''', (deployment_path, current_time, submission_id))
                
                conn.commit()
                logger.info(f"Plugin submission {submission_id} marked as deployed to {deployment_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error deploying plugin: {e}")
            return False