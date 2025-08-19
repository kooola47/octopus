import sqlite3

conn = sqlite3.connect('octopus_server/octopus.db')
cursor = conn.cursor()

# Check the specific task
cursor.execute("SELECT id, owner, executor, status FROM tasks WHERE id LIKE '%17556%'")
rows = cursor.fetchall()

print('Current task data:')
for row in rows:
    print(f'  ID: {row[0]}')
    print(f'  Owner: "{row[1]}"')
    print(f'  Executor: "{row[2]}"') 
    print(f'  Status: {row[3]}')
    print()

conn.close()
