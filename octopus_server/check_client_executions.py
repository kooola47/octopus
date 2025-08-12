#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def check_client_executions(client_name):
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()
    
    # Get all executions for the specified client, sorted by date desc
    cursor.execute('''
        SELECT id, execution_id, task_id, client, status, result, created_at, updated_at 
        FROM executions 
        WHERE client = ? 
        ORDER BY created_at DESC
    ''', (client_name,))
    
    executions = cursor.fetchall()
    
    print(f"=== Execution History for {client_name} ===")
    print(f"Total executions: {len(executions)}")
    print()
    
    if executions:
        print("ID | Execution_ID | Task_ID | Status | Created_At | Updated_At | Result")
        print("-" * 100)
        
        for exec in executions:
            exec_id, execution_id, task_id, client, status, result, created_at, updated_at = exec
            created_time = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
            updated_time = datetime.fromtimestamp(updated_at).strftime("%Y-%m-%d %H:%M:%S")
            result_preview = (result[:30] + "...") if result and len(result) > 30 else (result or "None")
            
            print(f"{exec_id:3} | {execution_id[:20]}... | {task_id[:12]}... | {status:8} | {created_time} | {updated_time} | {result_preview}")
    else:
        print("No executions found for this client.")
    
    # Get execution count by date
    print(f"\n=== Daily Execution Summary for {client_name} ===")
    cursor.execute('''
        SELECT DATE(datetime(created_at, 'unixepoch')) as exec_date, 
               COUNT(*) as count,
               COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
               COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
        FROM executions 
        WHERE client = ? 
        GROUP BY DATE(datetime(created_at, 'unixepoch'))
        ORDER BY exec_date DESC
    ''', (client_name,))
    
    daily_stats = cursor.fetchall()
    
    if daily_stats:
        print("Date       | Total | Success | Failed")
        print("-" * 35)
        for date, total, success, failed in daily_stats:
            print(f"{date} | {total:5} | {success:7} | {failed:6}")
    
    # Get recent task types executed
    print(f"\n=== Recent Task Types for {client_name} ===")
    cursor.execute('''
        SELECT t.plugin, t.action, COUNT(*) as count,
               MAX(e.created_at) as last_execution
        FROM executions e
        JOIN tasks t ON e.task_id = t.id
        WHERE e.client = ?
        GROUP BY t.plugin, t.action
        ORDER BY last_execution DESC
        LIMIT 10
    ''', (client_name,))
    
    task_types = cursor.fetchall()
    
    if task_types:
        print("Plugin | Action | Count | Last Execution")
        print("-" * 50)
        for plugin, action, count, last_exec in task_types:
            last_time = datetime.fromtimestamp(last_exec).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{plugin:10} | {action:10} | {count:5} | {last_time}")
    
    conn.close()

if __name__ == "__main__":
    check_client_executions("aries-33040")
