#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

def clean_database():
    """Clean all data from tasks and executions tables"""
    
    db_file = 'octopus.db'
    
    if not os.path.exists(db_file):
        print(f"Database file {db_file} not found!")
        return
    
    print("=== Database Cleanup Script ===")
    print(f"Target database: {db_file}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get current counts before deletion
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM tasks')
    task_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM executions')
    execution_count = cursor.fetchone()[0]
    
    print(f"Current data:")
    print(f"  Tasks: {task_count}")
    print(f"  Executions: {execution_count}")
    print()
    
    if task_count == 0 and execution_count == 0:
        print("Database is already clean. No data to remove.")
        conn.close()
        return
    
    # Confirm deletion
    response = input(f"Are you sure you want to delete {task_count} tasks and {execution_count} executions? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        conn.close()
        return
    
    print("\nProceeding with cleanup...")
    
    try:
        # Delete executions first (due to foreign key constraints)
        print("Deleting executions...")
        cursor.execute('DELETE FROM executions')
        deleted_executions = cursor.rowcount
        
        # Delete tasks
        print("Deleting tasks...")
        cursor.execute('DELETE FROM tasks')
        deleted_tasks = cursor.rowcount
        
        # Reset auto-increment counters
        print("Resetting auto-increment counters...")
        cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("tasks", "executions")')
        
        # Commit changes
        conn.commit()
        
        print("\n=== Cleanup Complete ===")
        print(f"Deleted {deleted_executions} executions")
        print(f"Deleted {deleted_tasks} tasks")
        print("Auto-increment counters reset")
        
        # Verify cleanup
        cursor.execute('SELECT COUNT(*) FROM tasks')
        remaining_tasks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM executions')
        remaining_executions = cursor.fetchone()[0]
        
        print(f"\nVerification:")
        print(f"  Remaining tasks: {remaining_tasks}")
        print(f"  Remaining executions: {remaining_executions}")
        
        if remaining_tasks == 0 and remaining_executions == 0:
            print("✅ Database cleanup successful!")
        else:
            print("⚠️  Some data may still remain.")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_database()
