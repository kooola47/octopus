#!/usr/bin/env python3
"""
Test script to check and create execution data
"""

import sqlite3
import uuid
import time
import os
import sys

# Add octopus_server to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'octopus_server'))

# Go to server directory
server_dir = os.path.join(os.path.dirname(__file__), 'octopus_server')
os.chdir(server_dir)

# Check if database exists and has executions table
db_file = 'octopus.db'

print(f"Checking database: {db_file}")
print(f"Database exists: {os.path.exists(db_file)}")

if not os.path.exists(db_file):
    print("Database doesn't exist. Creating...")
    # Import the server's init function
    try:
        from dbhelper import init_db
        init_db()
    except ImportError:
        print("Could not import dbhelper, creating database manually...")
        with sqlite3.connect(db_file) as conn:
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
            conn.commit()

with sqlite3.connect(db_file) as conn:
    # Check tables
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print(f"Tables in database: {[t[0] for t in tables]}")
    
    # Check executions table structure
    if ('executions',) in tables:
        cur = conn.execute("PRAGMA table_info(executions)")
        columns = cur.fetchall()
        print(f"Executions table columns: {[c[1] for c in columns]}")
        
        # Check current data
        cur = conn.execute("SELECT COUNT(*) FROM executions")
        count = cur.fetchone()[0]
        print(f"Current executions count: {count}")
        
        if count == 0:
            print("No executions found. Creating test data...")
            # Create test execution data
            test_data = [
                {
                    'task_id': str(uuid.uuid4()),
                    'client': 'test-client-1',
                    'status': 'success',
                    'result': 'Task completed successfully',
                    'updated_at': time.time()
                },
                {
                    'task_id': str(uuid.uuid4()),
                    'client': 'test-client-2',
                    'status': 'failed',
                    'result': 'Task failed with error',
                    'updated_at': time.time() - 300
                },
                {
                    'task_id': str(uuid.uuid4()),
                    'client': 'test-client-3',
                    'status': 'success',
                    'result': 'Another successful task',
                    'updated_at': time.time() - 600
                }
            ]
            
            for data in test_data:
                conn.execute("""
                    INSERT INTO executions (task_id, client, status, result, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['task_id'], data['client'], data['status'], data['result'], data['updated_at']))
            
            conn.commit()
            print(f"Created {len(test_data)} test execution records")
        
        # Show current data
        cur = conn.execute("SELECT id, task_id, client, status, result, updated_at FROM executions LIMIT 5")
        executions = cur.fetchall()
        print(f"Sample executions data:")
        for exec_row in executions:
            print(f"  ID: {exec_row[0]}, TaskID: {exec_row[1][:8]}..., Client: {exec_row[2]}, Status: {exec_row[3]}")
    else:
        print("Executions table doesn't exist!")

print("Done.")
