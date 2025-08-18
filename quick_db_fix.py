import sqlite3
import os

# Quick database cleanup
db_path = r'c:\Users\aries\PycharmProjects\octopus\octopus_server\octopus.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find and delete malformed tasks
cursor.execute("SELECT id, plugin FROM tasks WHERE plugin = '' OR plugin IS NULL")
malformed_tasks = cursor.fetchall()

print(f"Found {len(malformed_tasks)} malformed tasks:")
for task_id, plugin in malformed_tasks:
    print(f"Task ID: {task_id}, Plugin: '{plugin}'")

if malformed_tasks:
    # Delete them
    cursor.execute("DELETE FROM tasks WHERE plugin = '' OR plugin IS NULL")
    cursor.execute("DELETE FROM executions WHERE task_id = '1755012735059'")  # Specific problematic task
    conn.commit()
    print(f"✓ Deleted {len(malformed_tasks)} malformed tasks")

conn.close()
print("Database cleanup completed!")
