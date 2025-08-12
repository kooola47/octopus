#!/usr/bin/env python3
"""
Test the new unauthenticated execution results endpoint
"""
import requests
import time

def test_execution_results_endpoint():
    """Test the new /api/execution-results endpoint"""
    
    print("=== Testing New Execution Results Endpoint ===")
    
    server_url = "http://127.0.0.1:8000"
    execution_id = f"1755011047040_test-new-endpoint_{int(time.time() * 1000)}"
    
    # Test data matching the new client format
    test_data = {
        "execution_id": execution_id,
        "task_id": "1755011047040",
        "client": "test-new-endpoint",
        "exec_status": "success",
        "exec_result": "Test result from new endpoint"
    }
    
    print(f"Sending POST to: {server_url}/api/execution-results")
    print(f"Data: {test_data}")
    
    try:
        response = requests.post(
            f"{server_url}/api/execution-results",
            data=test_data,
            timeout=10
        )
        
        print(f"\nResponse:")
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"  Response JSON: {response.json()}")
        else:
            print(f"  Response Text: {response.text}")
            
        # Check database immediately after
        import sqlite3
        with sqlite3.connect('octopus.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM executions WHERE client = ?', ("test-new-endpoint",))
            found = cursor.fetchone()[0]
            print(f"\nDatabase check:")
            print(f"  Found executions from test-new-endpoint: {found}")
            
            cursor.execute('SELECT COUNT(*) FROM executions')
            total = cursor.fetchone()[0]
            print(f"  Total executions in database: {total}")
            
            if found > 0:
                cursor.execute('SELECT execution_id, task_id, client, status FROM executions WHERE client = ?', ("test-new-endpoint",))
                execution = cursor.fetchone()
                print(f"  Latest test execution: ID={execution[0]}, Task={execution[1]}, Client={execution[2]}, Status={execution[3]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_execution_results_endpoint()
