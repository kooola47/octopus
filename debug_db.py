#!/usr/bin/env python3

import sqlite3
import os

# Change to the server directory
os.chdir('octopus_server')

try:
    conn = sqlite3.connect('octopus.db')
    
    # Check the executions table schema
    print("📋 Executions table schema:")
    cur = conn.execute("PRAGMA table_info(executions)")
    for row in cur.fetchall():
        print(f"  {row[1]} ({row[2]}) - Nullable: {not row[3]}")
    
    # Check for very large result fields
    print(f"\n🔍 Checking result field lengths:")
    cur = conn.execute("SELECT id, execution_id, LENGTH(result) as result_len FROM executions ORDER BY result_len DESC LIMIT 5")
    for row in cur.fetchall():
        print(f"  ID {row[0]} ({row[1]}): {row[2]} characters")
    
    # Try a simple query first
    print(f"\n🧪 Testing simple queries:")
    cur = conn.execute("SELECT COUNT(*) FROM executions")
    count = cur.fetchone()[0]
    print(f"  Total count: {count}")
    
    # Try without the result field
    cur = conn.execute("SELECT id, execution_id, task_id, client, status FROM executions LIMIT 3")
    print(f"  Sample without result field:")
    for row in cur.fetchall():
        print(f"    {row}")
    
    conn.close()

except sqlite3.Error as e:
    print(f'❌ Database error: {e}')
except Exception as e:
    print(f'❌ Error: {e}')
