#!/usr/bin/env python3
"""
Test script to simulate the exact POST request that clients send to the dashboard endpoint
"""
import requests
import time

def test_dashboard_post():
    """Test the dashboard POST endpoint with the same data format as the client"""
    
    print("=== Testing Dashboard POST Endpoint ===")
    
    # Simulate the exact request the client sends
    server_url = "http://127.0.0.1:8000"
    execution_id = f"1755011047040_test-client_{int(time.time() * 1000)}"
    
    data = {
        "add_execution": "1",
        "execution_id": execution_id,
        "task_id": "1755011047040",
        "client": "test-client",
        "exec_status": "success",
        "exec_result": "Test result from dashboard POST"
    }
    
    print(f"Sending POST request to {server_url}/dashboard")
    print(f"Data: {data}")
    
    try:
        response = requests.post(
            f"{server_url}/dashboard",
            data=data,
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Server returned 200 OK")
        elif response.status_code == 302:
            print(f"✅ Server returned 302 (redirect) - Location: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
        # Check if execution was recorded
        import sqlite3
        with sqlite3.connect('octopus.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM executions WHERE execution_id = ?', (execution_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"✅ Execution was recorded in database (execution_id: {execution_id})")
            else:
                print(f"❌ Execution was NOT recorded in database (execution_id: {execution_id})")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 5000.")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_dashboard_post()
