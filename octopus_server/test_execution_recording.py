#!/usr/bin/env python3
"""
Test script to manually add execution results and debug the recording issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dbhelper import add_execution_result
import sqlite3
import time

def test_execution_recording():
    """Test adding execution results directly"""
    
    print("=== Testing Execution Result Recording ===")
    
    # Test data
    task_id = "1755011047040"
    client = "test-client"
    status = "success"
    result = "Test execution result"
    
    print(f"Adding test execution:")
    print(f"  Task ID: {task_id}")
    print(f"  Client: {client}")
    print(f"  Status: {status}")
    print(f"  Result: {result}")
    
    try:
        # Add execution result
        add_execution_result(task_id, client, status, result)
        print("✅ add_execution_result() completed successfully")
        
        # Check if it was actually saved
        with sqlite3.connect('octopus.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM executions')
            count = cursor.fetchone()[0]
            print(f"✅ Total executions in database: {count}")
            
            cursor.execute('SELECT * FROM executions ORDER BY created_at DESC LIMIT 1')
            latest = cursor.fetchone()
            if latest:
                print(f"✅ Latest execution: ID={latest[0]}, Task={latest[2]}, Client={latest[3]}, Status={latest[4]}")
            else:
                print("❌ No executions found in database")
                
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_execution_recording()
