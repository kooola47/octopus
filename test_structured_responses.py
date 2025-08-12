#!/usr/bin/env python3
"""
🧪 Test Structured Plugin Responses
==================================

Script to test the new structured plugin response format with a real task.
"""

import requests
import json
import time
from datetime import datetime

# Server configuration
SERVER_URL = "http://127.0.0.1:5000"

def create_test_task():
    """Create a test task that uses structured responses"""
    
    task_data = {
        "name": "Test Structured Response",
        "description": "Testing the new structured plugin response format",
        "type": "Adhoc",
        "plugin": "servicenow_example",
        "action": "create_incident",
        "args": ["Test incident from structured response", "This is a detailed description", "2"],
        "kwargs": {},
        "owner": "test_user",
        "executor": "test_user",
        "status": "Created",
        "priority": "Medium",
        "created_at": time.time(),
        "updated_at": time.time()
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/tasks", json=task_data, timeout=10)
        response.raise_for_status()
        result = response.json()
        task_id = result.get("id")
        print(f"✅ Created test task with ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"❌ Failed to create task: {e}")
        return None

def create_legacy_test_task():
    """Create a test task that uses legacy simple responses"""
    
    task_data = {
        "name": "Test Legacy Response",
        "description": "Testing backward compatibility with simple string responses",
        "type": "Adhoc", 
        "plugin": "servicenow_example",
        "action": "legacy_create_incident",
        "args": ["Legacy test incident"],
        "kwargs": {},
        "owner": "test_user",
        "executor": "test_user", 
        "status": "Created",
        "priority": "Low",
        "created_at": time.time(),
        "updated_at": time.time()
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/tasks", json=task_data, timeout=10)
        response.raise_for_status()
        result = response.json()
        task_id = result.get("id")
        print(f"✅ Created legacy test task with ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"❌ Failed to create legacy task: {e}")
        return None

def create_webscraping_test_task():
    """Create a web scraping test task"""
    
    task_data = {
        "name": "Test Web Scraping Response",
        "description": "Testing structured response with web scraping plugin",
        "type": "Adhoc",
        "plugin": "webscraping_example", 
        "action": "scrape_website",
        "args": ["https://example.com", "title"],
        "kwargs": {},
        "owner": "test_user",
        "executor": "test_user",
        "status": "Created",
        "priority": "Medium",
        "created_at": time.time(),
        "updated_at": time.time()
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/tasks", json=task_data, timeout=10)
        response.raise_for_status()
        result = response.json()
        task_id = result.get("id")
        print(f"✅ Created webscraping test task with ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"❌ Failed to create webscraping task: {e}")
        return None

def wait_for_execution(task_id, timeout=30):
    """Wait for task execution to complete"""
    print(f"⏳ Waiting for task {task_id} to execute...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Check task status
            response = requests.get(f"{SERVER_URL}/tasks/{task_id}", timeout=5)
            if response.status_code == 200:
                task = response.json()
                status = task.get("status")
                if status in ["Done", "success", "failed"]:
                    print(f"✅ Task {task_id} completed with status: {status}")
                    return task
            
            # Check executions table
            response = requests.get(f"{SERVER_URL}/executions", timeout=5)
            if response.status_code == 200:
                executions = response.json()
                for exec in executions:
                    if exec.get("task_id") == task_id:
                        print(f"✅ Found execution for task {task_id}")
                        print(f"   Status: {exec.get('status')}")
                        print(f"   Result: {exec.get('result', '')[:100]}...")
                        return exec
                        
        except Exception as e:
            print(f"⚠️ Error checking task status: {e}")
        
        time.sleep(2)
    
    print(f"⏰ Timeout waiting for task {task_id}")
    return None

def main():
    print("🧪 Testing Structured Plugin Responses")
    print("=" * 50)
    
    # Test 1: Structured response
    print("\n📋 Test 1: Structured ServiceNow Response")
    task_id = create_test_task()
    if task_id:
        execution = wait_for_execution(task_id)
        if execution:
            print("✅ Structured response test completed")
        else:
            print("❌ Structured response test failed - no execution found")
    
    # Test 2: Legacy response  
    print("\n📋 Test 2: Legacy Response (Backward Compatibility)")
    task_id = create_legacy_test_task()
    if task_id:
        execution = wait_for_execution(task_id)
        if execution:
            print("✅ Legacy response test completed")
        else:
            print("❌ Legacy response test failed - no execution found")
    
    # Test 3: Web scraping response
    print("\n📋 Test 3: Web Scraping Structured Response")
    task_id = create_webscraping_test_task()
    if task_id:
        execution = wait_for_execution(task_id)
        if execution:
            print("✅ Web scraping response test completed")
        else:
            print("❌ Web scraping response test failed - no execution found")
    
    print("\n🎯 Testing Complete!")
    print("\nNext steps:")
    print("1. Check the client logs for structured response processing")
    print("2. Look for generated files in plugin_outputs/")
    print("3. Check cache/ directory for cached values")
    print("4. Verify executions in the web dashboard")

if __name__ == "__main__":
    main()
