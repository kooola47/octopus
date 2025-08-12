#!/usr/bin/env python3
"""
Check tasks with user-friendly timestamp formatting
"""

import sqlite3
from datetime import datetime
import time

def main():
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()
    
    # Get recent tasks
    cursor.execute('''
        SELECT id, name, owner, executor, type, execution_start_time, 
               execution_end_time, interval, status, created_at 
        FROM tasks 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    
    tasks = cursor.fetchall()
    
    print('Recent tasks (user-friendly format):')
    print('=' * 60)
    print()
    
    current_time = time.time()
    
    for i, task in enumerate(tasks, 1):
        task_id, name, owner, executor, task_type, start_time, end_time, interval, status, created_at = task
        
        print(f'{i}. Task ID: {task_id}')
        print(f'   Name: {name or "Unnamed"}')
        print(f'   Owner: {owner} → Executor: {executor}')
        print(f'   Type: {task_type or "adhoc"}')
        
        # Format start time
        if start_time:
            start_dt = datetime.fromtimestamp(float(start_time))
            print(f'   Start Time: {start_dt.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            print(f'   Start Time: Not set')
        
        # Format end time
        if end_time:
            end_dt = datetime.fromtimestamp(float(end_time))
            print(f'   End Time: {end_dt.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            print(f'   End Time: Not set')
        
        # Format interval
        if interval:
            interval_sec = int(interval)
            if interval_sec >= 3600:
                hours = interval_sec // 3600
                minutes = (interval_sec % 3600) // 60
                seconds = interval_sec % 60
                print(f'   Interval: {interval_sec}s ({hours}h {minutes}m {seconds}s)')
            elif interval_sec >= 60:
                minutes = interval_sec // 60
                seconds = interval_sec % 60
                print(f'   Interval: {interval_sec}s ({minutes}m {seconds}s)')
            else:
                print(f'   Interval: {interval_sec}s')
        else:
            print(f'   Interval: Not set')
        
        print(f'   Status: {status}')
        
        # Format created time
        created_dt = datetime.fromtimestamp(created_at)
        print(f'   Created: {created_dt.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Check execution window status
        if start_time and end_time:
            if current_time < float(start_time):
                remaining = float(start_time) - current_time
                remaining_min = int(remaining // 60)
                print(f'   🕐 Task has not started yet (starts in {remaining_min} minutes)')
            elif current_time > float(end_time):
                elapsed = current_time - float(end_time)
                elapsed_min = int(elapsed // 60)
                print(f'   ⏰ Task execution window ended {elapsed_min} minutes ago')
            else:
                remaining = float(end_time) - current_time
                remaining_min = int(remaining // 60)
                print(f'   ✅ Task is within execution window ({remaining_min} minutes remaining)')
        elif start_time:
            if current_time >= float(start_time):
                print(f'   ▶️ Task started (no end time specified)')
            else:
                print(f'   ⏸️ Task waiting to start')
        
        print()
    
    # Summary stats
    cursor.execute('SELECT COUNT(*) FROM tasks')
    total_tasks = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "Done"')
    completed_tasks = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tasks WHERE type = "scheduled"')
    scheduled_tasks = cursor.fetchone()[0]
    
    print('Summary:')
    print(f'  Total tasks: {total_tasks}')
    print(f'  Completed tasks: {completed_tasks}')
    print(f'  Scheduled tasks: {scheduled_tasks}')
    print(f'  Current time: {datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")}')
    
    conn.close()

if __name__ == '__main__':
    main()
