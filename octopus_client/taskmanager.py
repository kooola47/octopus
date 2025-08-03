import sqlite3
import time
import socket
import getpass
import importlib
import os

DB_FILE = "octopus_tasks.db"
HOSTNAME = socket.gethostname()
USERNAME = getpass.getuser()

def _get_conn():
    return sqlite3.connect(DB_FILE, timeout=10)

def _init_db():
    with _get_conn() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                owner TEXT,
                plugin TEXT,
                action TEXT,
                args TEXT,
                kwargs TEXT,
                status TEXT,
                executor TEXT,
                result TEXT,
                updated_at REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS locks (
                task_id TEXT PRIMARY KEY,
                hostname TEXT,
                locked_at REAL
            )
        ''')

def sync_tasks():
    _init_db()
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tasks")
        for row in cur.fetchall():
            task = dict(zip([col[0] for col in cur.description], row))
            owner = task.get("owner")
            executor = task.get("executor")
            status = task.get("status")
            should_execute = False
            if owner == "ALL":
                should_execute = True
            elif owner == USERNAME:
                should_execute = True
            elif owner == "Anyone" and (not executor or executor == HOSTNAME):
                if _lock_task(conn, task["id"]):
                    task["executor"] = HOSTNAME
                    should_execute = True
            if should_execute and status not in ("success", "failed"):
                execute_task(conn, task["id"], task)

def _lock_task(conn, task_id):
    try:
        conn.execute("INSERT INTO locks (task_id, hostname, locked_at) VALUES (?, ?, ?)", (task_id, HOSTNAME, time.time()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        cur = conn.execute("SELECT hostname FROM locks WHERE task_id=?", (task_id,))
        row = cur.fetchone()
        return row and row[0] == HOSTNAME

def execute_task(conn, task_id, task):
    plugin = task.get("plugin")
    action = task.get("action", "run")
    args = eval(task.get("args", "[]"))
    kwargs = eval(task.get("kwargs", "{}"))
    try:
        module = importlib.import_module(f"plugins.{plugin}")
        func = getattr(module, action, None)
        if callable(func):
            result = func(*args, **kwargs)
            status = "success"
        else:
            result = f"Action {action} not found"
            status = "failed"
    except Exception as e:
        result = str(e)
        status = "failed"
    conn.execute("UPDATE tasks SET status=?, result=?, executor=?, updated_at=? WHERE id=?",
                 (status, str(result), HOSTNAME, time.time(), task_id))
    conn.commit()
            INSERT OR REPLACE INTO tasks (id, owner, plugin, action, args, kwargs, status, executor, result, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            task.get("owner"),
            task.get("plugin"),
            task.get("action", "run"),
            str(task.get("args", [])),
            str(task.get("kwargs", {})),
            "pending",
            "",
            "",
            time.time()
        ))
        conn.commit()
    return task_id

def update_task(task_id, updates):
    _init_db()
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        if not row:
            return False
        task = dict(zip([col[0] for col in cur.description], row))
        task.update(updates)
        conn.execute('''
            UPDATE tasks SET owner=?, plugin=?, action=?, args=?, kwargs=?, status=?, executor=?, result=?, updated_at=?
            WHERE id=?
        ''', (
            task.get("owner"),
            task.get("plugin"),
            task.get("action", "run"),
            str(task.get("args", [])),
            str(task.get("kwargs", {})),
            task.get("status"),
            task.get("executor"),
            str(task.get("result")),
            time.time(),
            task_id
        ))
        conn.commit()
    return True

def delete_task(task_id):
    _init_db()
    with _get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.execute("DELETE FROM locks WHERE task_id=?", (task_id,))
        conn.commit()
    return True

def get_tasks():
    _init_db()
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tasks")
        tasks = {}
        for row in cur.fetchall():
            task = dict(zip([col[0] for col in cur.description], row))
            tasks[task["id"]] = task
        return tasks
