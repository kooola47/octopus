#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def search_task(partial_id):
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()
    
    # Search for tasks containing the partial ID
    cursor.execute('SELECT * FROM tasks WHERE id LIKE ?', (f'%{partial_id}%',))
    tasks = cursor.fetchall()
    
    print(f'Tasks containing "{partial_id}":')
    print()
    
    if not tasks:
        print('No tasks found with that partial ID')
        
        # Show recent tasks for reference
        cursor.execute('SELECT id, name, owner, plugin, status FROM tasks ORDER BY created_at DESC LIMIT 5')
        recent_tasks = cursor.fetchall()
        print('\nRecent tasks for reference:')
        for task in recent_tasks:
            print(f'ID: {task[0][:20]}... | Name: {task[1]} | Owner: {task[2]} | Plugin: {task[3]} | Status: {task[4]}')
    else:
        for task in tasks:
            print(f'Complete ID: {task[0]}')
            print(f'Name: {task[15] or "Unnamed"}')
            print(f'Owner: {task[1]}')
            print(f'Executor: {task[11]}')
            print(f'Plugin: {task[2]}')
            print(f'Action: {task[3]}')
            print(f'Args: {task[4]}')
            print(f'Kwargs: {task[5]}')
            print(f'Type: {task[6]}')
            print(f'Status: {task[10]}')
            
            if task[7]:
                try:
                    start_time = datetime.fromtimestamp(float(task[7]))
                    print(f'Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
                except:
                    print(f'Start Time: {task[7]} (raw)')
            else:
                print('Start Time: Not set')
                
            if task[8]:
                try:
                    end_time = datetime.fromtimestamp(float(task[8]))
                    print(f'End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
                except:
                    print(f'End Time: {task[8]} (raw)')
            else:
                print('End Time: Not set')
                
            if task[9]:
                try:
                    interval = int(float(task[9]))
                    minutes = interval // 60
                    seconds = interval % 60
                    print(f'Interval: {interval}s ({minutes}m {seconds}s)')
                except:
                    print(f'Interval: {task[9]} (raw)')
            else:
                print('Interval: Not set')
                
            if task[13]:
                created_at = datetime.fromtimestamp(task[13])
                print(f'Created At: {created_at.strftime("%Y-%m-%d %H:%M:%S")}')
            else:
                print('Created At: Not set')
                
            if task[14]:
                updated_at = datetime.fromtimestamp(task[14])
                print(f'Updated At: {updated_at.strftime("%Y-%m-%d %H:%M:%S")}')
            else:
                print('Updated At: Not set')
            
            print('-' * 50)
    
    conn.close()

if __name__ == "__main__":
    search_task("17550095")
