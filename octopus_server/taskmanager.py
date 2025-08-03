# filepath: c:\Users\aries\PycharmProjects\octopus\octopus_server\taskmanager.py
import sqlite3
import time
import os

DB_FILE = "octopus_tasks.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        # Add missing columns if they do not exist
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
        # Check for missing columns and add them if needed
        cur = conn.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cur.fetchall()]
        required_columns = [
            ("type", "TEXT"),
            ("execution_start_time", "TEXT"),
            ("execution_end_time", "TEXT"),
            ("interval", "TEXT"),
        ]
        for col, coltype in required_columns:
            if col not in columns:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {col} {coltype}")

def get_tasks():
    init_db()  # Ensure table exists before querying
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT * FROM tasks")
        tasks = {}
        for row in cur.fetchall():
            columns = [col[0] for col in cur.description]
            task = dict(zip(columns, row))
            tasks[task["id"]] = task
        return tasks

def add_task(task):
    init_db()  # Ensure table exists before inserting
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
            "pending",
            task.get("executor", ""),
            task.get("result", ""),
            time.time()
        ))
        conn.commit()
    return task_id

def update_task(task_id, updates):
    init_db()  # Ensure table exists before updating
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
            task.get("status", "pending"),
            task.get("executor", ""),
            task.get("result", ""),
            time.time(),
            task_id
        ))
        conn.commit()
    return True

def delete_task(task_id):
    init_db()  # Ensure table exists before deleting
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
    return True