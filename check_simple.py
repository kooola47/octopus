import sqlite3

conn = sqlite3.connect('octopus_server/octopus.db')
cursor = conn.cursor()

print("=== USER DATA SUMMARY FOR aries-7044 ===")

# Check heartbeats
cursor.execute('SELECT COUNT(*) FROM heartbeats WHERE username = ?', ('aries-7044',))
heartbeat_count = cursor.fetchone()[0]
print(f'Heartbeats: {heartbeat_count} records')

if heartbeat_count > 0:
    cursor.execute('SELECT * FROM heartbeats WHERE username = ? ORDER BY timestamp DESC LIMIT 1', ('aries-7044',))
    latest_heartbeat = cursor.fetchone()
    print(f'Latest heartbeat: {latest_heartbeat}')

# Check tasks table structure
cursor.execute('PRAGMA table_info(tasks)')
task_columns = cursor.fetchall()
print(f'\nTasks table columns: {[col[1] for col in task_columns]}')

# Check if there are any tasks
cursor.execute('SELECT COUNT(*) FROM tasks')
total_tasks = cursor.fetchone()[0]
print(f'Total tasks in system: {total_tasks}')

# Check executions
cursor.execute('SELECT COUNT(*) FROM executions')
total_executions = cursor.fetchone()[0]
print(f'Total executions: {total_executions}')

# Check user_parameters
cursor.execute('SELECT * FROM user_parameters WHERE username = ?', ('aries-7044',))
user_params = cursor.fetchall()
print(f'User parameters: {len(user_params)} records')
for param in user_params:
    print(f'  Parameter: {param}')

conn.close()
