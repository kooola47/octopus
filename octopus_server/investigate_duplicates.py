#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def investigate_duplicate_executions():
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()
    
    # Check for duplicate executions of the same task
    print("=== Investigating Duplicate Task Executions ===\n")
    
    # Get executions for task 1755007291030 by aries-23640
    cursor.execute('''
        SELECT id, execution_id, task_id, client, status, result, created_at, updated_at 
        FROM executions 
        WHERE task_id LIKE ? AND client = ? 
        ORDER BY created_at
    ''', ('%1755007291030%', 'aries-23640'))
    
    executions = cursor.fetchall()
    
    print(f"Found {len(executions)} executions for task 1755007291030 by aries-23640:")
    print("ID | Execution_ID | Task_ID | Client | Status | Created_At | Updated_At")
    print("-" * 80)
    
    for exec in executions:
        exec_id, execution_id, task_id, client, status, result, created_at, updated_at = exec
        created_time = datetime.fromtimestamp(created_at).strftime("%H:%M:%S.%f")[:-3]
        updated_time = datetime.fromtimestamp(updated_at).strftime("%H:%M:%S.%f")[:-3]
        print(f"{exec_id} | {execution_id} | {task_id[:12]}... | {client} | {status} | {created_time} | {updated_time}")
    
    print("\n=== Checking for General Duplicate Pattern ===")
    
    # Check for any tasks executed multiple times by same client at same time
    cursor.execute('''
        SELECT task_id, client, COUNT(*) as exec_count,
               MIN(created_at) as first_exec, MAX(created_at) as last_exec
        FROM executions 
        GROUP BY task_id, client, ROUND(created_at, 0)
        HAVING COUNT(*) > 1
        ORDER BY exec_count DESC
    ''')
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\nFound {len(duplicates)} cases of duplicate executions:")
        print("Task_ID | Client | Count | First_Exec | Last_Exec")
        print("-" * 70)
        
        for dup in duplicates:
            task_id, client, count, first_exec, last_exec = dup
            first_time = datetime.fromtimestamp(first_exec).strftime("%H:%M:%S")
            last_time = datetime.fromtimestamp(last_exec).strftime("%H:%M:%S")
            print(f"{task_id[:12]}... | {client} | {count} | {first_time} | {last_time}")
    else:
        print("No duplicate executions found.")
    
    print("\n=== Checking Task Assignment Logic ===")
    
    # Check the task details
    cursor.execute('SELECT * FROM tasks WHERE id LIKE ?', ('%1755007291030%',))
    task = cursor.fetchone()
    
    if task:
        print(f"\nTask Details:")
        print(f"ID: {task[0]}")
        print(f"Owner: {task[1]}")
        print(f"Plugin: {task[2]}")
        print(f"Action: {task[3]}")
        print(f"Type: {task[6]}")
        print(f"Status: {task[10]}")
        print(f"Executor: {task[11]}")
        
        if task[6] == 'scheduled':
            start_time = datetime.fromtimestamp(float(task[7])) if task[7] else None
            end_time = datetime.fromtimestamp(float(task[8])) if task[8] else None
            interval = int(float(task[9])) if task[9] else None
            
            print(f"Start Time: {start_time.strftime('%H:%M:%S') if start_time else 'Not set'}")
            print(f"End Time: {end_time.strftime('%H:%M:%S') if end_time else 'Not set'}")
            print(f"Interval: {interval}s" if interval else 'Not set')
    
    conn.close()

if __name__ == "__main__":
    investigate_duplicate_executions()
