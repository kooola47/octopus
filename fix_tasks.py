import sqlite3

# Connect to database
conn = sqlite3.connect('octopus_server/octopus.db')
cursor = conn.cursor()

# Find tasks with owner "ALL" that should be "Anyone" 
cursor.execute("SELECT id, owner, executor, status FROM tasks WHERE owner = 'ALL' AND executor = 'ALL'")
tasks_to_fix = cursor.fetchall()

print(f'Found {len(tasks_to_fix)} tasks with owner="ALL" and executor="ALL"')

for task in tasks_to_fix:
    task_id, owner, executor, status = task
    print(f'Updating task {task_id}: owner "ALL" -> "" (Anyone), executor "ALL" -> ""')
    
    # Update to empty owner (which represents "Anyone") and clear executor so it can be reassigned
    cursor.execute("UPDATE tasks SET owner = '', executor = '' WHERE id = ?", (task_id,))

# Commit changes
conn.commit()

# Verify changes
cursor.execute("SELECT id, owner, executor, status FROM tasks WHERE id LIKE '%17556%'")
updated_tasks = cursor.fetchall()

print('\nUpdated task data:')
for task in updated_tasks:
    print(f'  ID: {task[0]}')
    print(f'  Owner: "{task[1]}"')
    print(f'  Executor: "{task[2]}"') 
    print(f'  Status: {task[3]}')
    print()

conn.close()
print('Database updated successfully!')
