#!/usr/bin/env python3
"""
Clean up malformed tasks with empty plugin names
"""
import sqlite3
import sys
import os

def clean_empty_plugin_tasks():
    """Remove tasks with empty plugin names from the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'octopus_server', 'octopus.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find tasks with empty plugin names
        cursor.execute('SELECT id, plugin, action, owner, status FROM tasks WHERE plugin = "" OR plugin IS NULL')
        empty_plugin_tasks = cursor.fetchall()
        
        print('Tasks with empty plugin names:')
        if empty_plugin_tasks:
            for task in empty_plugin_tasks:
                print(f'ID: {task[0]}, Plugin: "{task[1]}", Action: {task[2]}, Owner: {task[3]}, Status: {task[4]}')
            
            # Ask for confirmation to delete
            print(f'\nFound {len(empty_plugin_tasks)} malformed task(s).')
            response = input('Do you want to delete these tasks? (y/N): ')
            
            if response.lower() == 'y':
                # Delete tasks with empty plugin names
                cursor.execute('DELETE FROM tasks WHERE plugin = "" OR plugin IS NULL')
                deleted_count = cursor.rowcount
                
                # Also clean up related executions
                cursor.execute('DELETE FROM executions WHERE task_id IN (SELECT id FROM tasks WHERE plugin = "" OR plugin IS NULL)')
                
                conn.commit()
                print(f'✓ Deleted {deleted_count} malformed task(s) and their executions.')
            else:
                print('No tasks deleted.')
        else:
            print('No tasks with empty plugin names found.')
        
        # Show remaining active tasks
        cursor.execute('SELECT id, plugin, action, owner, status FROM tasks WHERE status = "Active" LIMIT 10')
        active_tasks = cursor.fetchall()
        
        print(f'\nRemaining active tasks (showing first 10):')
        for task in active_tasks:
            print(f'ID: {task[0]}, Plugin: "{task[1]}", Action: {task[2]}, Owner: {task[3]}, Status: {task[4]}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_empty_plugin_tasks()
