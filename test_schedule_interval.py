import sqlite3
from datetime import datetime
import time

conn = sqlite3.connect('octopus.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, owner, executor, type, execution_start_time, execution_end_time, interval, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 3')
tasks = cursor.fetchall()

print('Recent tasks (user-friendly format):')
print()

for t in tasks:
    print(f'Task ID: {t[0]}')
    print(f'  Owner: {t[2]} → Executor: {t[3]}')
    print(f'  Type: {t[4] or \"adhoc\"}')
    
    if t[5]:
        start_dt = datetime.fromtimestamp(float(t[5]))
        print(f'  Start Time: {start_dt.strftime(\"%Y-%m-%d %H:%M:%S\")}')
    else:
        print(f'  Start Time: Not set')
    
    if t[6]:
        end_dt = datetime.fromtimestamp(float(t[6]))
        print(f'  End Time: {end_dt.strftime(\"%Y-%m-%d %H:%M:%S\")}')
    else:
        print(f'  End Time: Not set')
    
    if t[7]:
        interval_sec = int(t[7])
        minutes = interval_sec // 60
        seconds = interval_sec % 60
        print(f'  Interval: {interval_sec}s ({minutes}min {seconds}s)')
    else:
        print(f'  Interval: Not set')
    
    print(f'  Status: {t[8]}')
    created_dt = datetime.fromtimestamp(t[9])
    print(f'  Created: {created_dt.strftime(\"%Y-%m-%d %H:%M:%S\")}')
    
    # Check if task should still be running
    current_time = time.time()
    if t[5] and t[6]:
        if current_time < float(t[5]):
            print(f'  🕐 Task has not started yet')
        elif current_time > float(t[6]):
            print(f'  ⏰ Task execution window has ended')
        else:
            print(f'  ✅ Task is within execution window')
    
    print()

conn.close()