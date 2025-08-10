#!/usr/bin/env python3

import sqlite3
import os

# Change to the server directory
os.chdir('octopus_server')

try:
    conn = sqlite3.connect('octopus.db')
    cur = conn.execute('SELECT COUNT(*) FROM executions')
    count = cur.fetchone()[0]
    print(f'✅ Total executions in database: {count}')
    
    if count > 0:
        cur = conn.execute('SELECT id, execution_id, task_id, client, status, result FROM executions LIMIT 5')
        print('\n📋 Sample executions:')
        for i, row in enumerate(cur.fetchall(), 1):
            print(f'{i}. ID: {row[0]}, Exec ID: {row[1]}, Task: {row[2]}, Client: {row[3]}, Status: {row[4]}')
            print(f'   Result: {row[5][:50] if row[5] else "None"}...\n')
    else:
        print('❌ No execution records found')
        
    conn.close()

except sqlite3.Error as e:
    print(f'❌ Database error: {e}')
except Exception as e:
    print(f'❌ Error: {e}')
