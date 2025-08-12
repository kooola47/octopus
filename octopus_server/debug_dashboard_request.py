#!/usr/bin/env python3
"""
Debug script to test dashboard route behavior
"""
import requests
import time

def debug_dashboard_request():
    """Send a POST request and analyze what happens"""
    
    print("=== Debug Dashboard Request ===")
    
    server_url = "http://127.0.0.1:8000"
    execution_id = f"1755011047040_debug-client_{int(time.time() * 1000)}"
    
    # Test with the exact same data format as the client
    test_data = {
        "add_execution": "1",
        "execution_id": execution_id,
        "task_id": "1755011047040",
        "client": "debug-client",
        "exec_status": "success",  
        "exec_result": "Debug test result"
    }
    
    print(f"Sending POST to: {server_url}/dashboard")
    print(f"Data keys: {list(test_data.keys())}")
    print(f"add_execution value: '{test_data['add_execution']}'")
    print(f"Full data: {test_data}")
    
    try:
        response = requests.post(
            f"{server_url}/dashboard",
            data=test_data,
            timeout=10,
            allow_redirects=False  # Don't follow redirects automatically
        )
        
        print(f"\nResponse:")
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if 'Location' in response.headers:
            print(f"  Redirect Location: {response.headers['Location']}")
            
        # Try to get response content (if any)
        try:
            content = response.text[:500]  # First 500 chars
            print(f"  Content preview: {content}")
        except:
            print("  Content: (unable to read)")
            
        # Check database immediately after
        import sqlite3
        with sqlite3.connect('octopus.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM executions WHERE execution_id = ?', (execution_id,))
            found = cursor.fetchone()[0]
            print(f"\nDatabase check:")
            print(f"  Found execution with ID {execution_id}: {'YES' if found > 0 else 'NO'}")
            
            cursor.execute('SELECT COUNT(*) FROM executions')
            total = cursor.fetchone()[0]
            print(f"  Total executions in database: {total}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dashboard_request()
