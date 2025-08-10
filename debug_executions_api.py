#!/usr/bin/env python3
"""
🔍 EXECUTIONS API DEBUG SCRIPT
==============================

Test the executions API to see what data is being returned.
"""

import requests
import json

def test_executions_api():
    """Test the executions API endpoint"""
    print("🔍 Testing Executions API")
    print("=" * 40)
    
    try:
        # Test the API endpoint
        url = "http://localhost:8000/api/executions?page=1&per_page=10"
        print(f"📡 Calling: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Response Type: {type(data)}")
            print(f"📄 Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict) and 'executions' in data:
                executions = data['executions']
                print(f"✅ Executions Count: {len(executions)}")
                
                if executions:
                    print(f"📋 First Execution Sample:")
                    first_exec = executions[0]
                    print(json.dumps(first_exec, indent=2))
                    
                    print(f"🔑 Execution Keys: {list(first_exec.keys())}")
                else:
                    print("⚠️  No executions found in response")
                    
                if 'pagination' in data:
                    print(f"📊 Pagination: {data['pagination']}")
            else:
                print("❌ Invalid response format - missing 'executions' key")
                print(f"📄 Full Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server is not running or not accessible")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_database_direct():
    """Test database directly to see execution data"""
    print("\n🗄️  Testing Database Direct Access")
    print("=" * 40)
    
    try:
        import sqlite3
        conn = sqlite3.connect('octopus_server/octopus.db')
        
        # Check table schema
        cursor = conn.execute("PRAGMA table_info(executions)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"🏗️  Database Columns: {columns}")
        
        # Check record count
        cursor = conn.execute("SELECT COUNT(*) FROM executions")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total Records: {total_count}")
        
        # Get sample data
        cursor = conn.execute("SELECT * FROM executions LIMIT 3")
        sample_data = cursor.fetchall()
        
        if sample_data:
            print(f"📋 Sample Records:")
            for i, row in enumerate(sample_data):
                print(f"   Record {i+1}: {dict(zip(columns, row))}")
        else:
            print("⚠️  No data found in executions table")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    test_executions_api()
    test_database_direct()
