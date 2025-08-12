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
from contextlib import contextmanager

# Add parent directory to path for shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_FILE, CLIENT_TIMEOUT
from constants import TaskStatus, TaskOwnership, TaskType, Database
from utils import get_current_timestamp, is_task_completed, sanitize_string, safe_json_loads

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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
            
            # Migrate existing tables to add missing columns
            migrate_tasks_table(conn)
            
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
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
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
            task.get("type"),
            start_time,
            end_time,
            task.get("interval"),
            "Created",  # Changed from "pending" to "Created"
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
        original_type = task.get("type", "").lower()
        new_status = updates.get("status", "").lower()
        
        # Prevent scheduled tasks from being marked as Done unless execution window has ended
        if (original_type in ["scheduled", "schedule"] and 
            new_status in ["done", "completed", "success"] and
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
            task.get("status", "Created"),  # Changed from "pending" to "Created"
            task.get("executor", ""),
            task.get("result", ""),
            now_ts,
            task_id
        ))
        # Insert/update executions table only if there's actual result data (not just assignment)
        client = updates.get("executor")
        result = updates.get("result")
        exec_status = updates.get("status")
        
        # Only create execution record if we have actual execution results
        if client and (result or exec_status in ("success", "failed", "Done")):
            # Insert a new execution row; if a unique constraint is added later, replace with UPSERT
            conn.execute('''
                INSERT INTO executions (execution_id, task_id, client, status, result, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"{task_id}_{client}_{int(now_ts*1000)}",
                task_id,
                client,
                exec_status or "completed",
                str(result or ""),
                now_ts,
                now_ts
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
    Assigns unassigned 'Anyone' tasks to a random ONLINE client (by username).
    Only assigns if executor is empty and client has sent heartbeat recently.
    """
    import random
    # Only use clients that are currently active/online (filtered by get_active_clients)
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
    IMPORTANT: Only assigns tasks to ONLINE clients (clients passed in are pre-filtered by get_active_clients).
    """
    import random
    import logging
    
    logger = logging.getLogger("octopus_server")
    # Only use clients that are currently online (pre-filtered by caller)
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
            # For ALL tasks, complete when any client succeeds (first success wins)
            if owner == TaskOwnership.ALL:
                if any(TaskStatus.is_completed(exec.get("status")) for exec in executions):
                    return TaskStatus.DONE  # Complete when any client completes the ALL task
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

def add_execution_result(task_id, client, status, result):
    """
    Add execution result for a task with unique execution ID.
    Each execution gets its own record, allowing multiple executions per task per client.
    """
    import logging
    import time
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    # Generate unique execution ID
    execution_id = f"{task_id}_{client}_{int(time.time() * 1000)}"
    current_time = time.time()
    
    with sqlite3.connect(DB_FILE) as conn:
        logger.info(f"Adding execution result: execution_id={execution_id}, task_id={task_id}, client={client}, status={status}")
        
        # Always insert a new execution record (no conflict resolution)
        conn.execute('''
            INSERT INTO executions (execution_id, task_id, client, status, result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution_id,
            task_id,
            client,
            status,
            str(result),
            current_time,
            current_time
        ))
        
        # For adhoc tasks, update the task status to Done when execution completes
        # Check if this is an adhoc task and if the execution status indicates completion
        if status.lower() in ['success', 'completed', 'done', 'failed', 'error']:
            # Get the task type and timing info
            task_row = conn.execute('SELECT type, execution_end_time FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if task_row:
                task_type, end_time = task_row
                
                if task_type == 'Adhoc':
                    # Update task status to Done for completed adhoc tasks
                    task_status = 'Done' if status.lower() in ['success', 'completed', 'done'] else 'Failed'
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

def create_user(username, password, email='', role='user', is_active=True):
    """Create a new user"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    # Validate role
    if role not in ['admin', 'user']:
        logger.error(f"Invalid role: {role}")
        return None
    
    # Hash password
    password_hash = hash_password(password)
    current_time = time.time()
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute('''
                INSERT INTO users (username, email, password_hash, role, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, is_active, current_time, current_time))
            
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
            SELECT id, username, email, role, is_active, created_at, updated_at, last_login
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
                'last_login': user_row[7]
            }
    return None

def get_all_users():
    """Get all active users"""
    init_db()
    
    with sqlite3.connect(DB_FILE) as conn:
        user_rows = conn.execute('''
            SELECT id, username, email, role, is_active, created_at, updated_at, last_login
            FROM users WHERE is_active = 1 ORDER BY created_at DESC
        ''').fetchall()
        
        users = []
        for row in user_rows:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'is_active': row[4],
                'created_at': row[5],
                'updated_at': row[6],
                'last_login': row[7]
            })
        return users

def update_user(user_id, **kwargs):
    """Update user information"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    # Build update query dynamically
    allowed_fields = ['username', 'email', 'role', 'is_active']
    update_fields = []
    update_values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
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
    """Delete user (actually sets is_active to False)"""
    import time
    import logging
    logger = logging.getLogger("octopus_server")
    
    init_db()
    
    current_time = time.time()
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Check if user exists first
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.error(f"User {user_id} not found for deletion")
                return False
            
            # Set user as inactive instead of deleting
            cursor.execute('''
                UPDATE users SET is_active = 0, updated_at = ? WHERE id = ?
            ''', (current_time, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"User {user[1]} (ID: {user_id}) deactivated successfully")
                return True
            else:
                logger.error(f"Failed to update user {user_id} - no rows affected")
                return False
                
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return False