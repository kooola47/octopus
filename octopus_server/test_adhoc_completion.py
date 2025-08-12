#!/usr/bin/env python3
"""
Test script to verify adhoc task completion logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dbhelper import add_execution_result
import sqlite3
import time

def test_adhoc_completion():
    """Test that adhoc tasks are properly completed after execution"""
    
    print("=== Testing Adhoc Task Completion Logic ===")
    
    # Create a test adhoc task
    with sqlite3.connect('octopus.db') as conn:
        task_id = f"test_adhoc_{int(time.time() * 1000)}"
        conn.execute('''
            INSERT INTO tasks (id, name, owner, type, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            "Test Adhoc Task",
            "ALL",
            "adhoc",  # lowercase as it appears in the database
            "Active",
            time.time(),
            time.time()
        ))
        conn.commit()
        print(f"✅ Created test adhoc task: {task_id}")
    
    # Add a successful execution result
    print("📝 Adding successful execution result...")
    add_execution_result(task_id, "test-client", "success", "Test successful completion")
    
    # Check if task status was updated to Done
    with sqlite3.connect('octopus.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM tasks WHERE id = ?', (task_id,))
        result = cursor.fetchone()
        
        if result:
            status = result[0]
            print(f"📊 Task status after execution: {status}")
            
            if status == "Done":
                print("✅ SUCCESS: Adhoc task automatically completed!")
                return True
            else:
                print(f"❌ FAILED: Task status is '{status}', expected 'Done'")
                return False
        else:
            print("❌ FAILED: Task not found")
            return False

if __name__ == "__main__":
    success = test_adhoc_completion()
    if success:
        print("\n🎉 Adhoc task completion logic is working correctly!")
    else:
        print("\n💥 Adhoc task completion logic needs further investigation.")
