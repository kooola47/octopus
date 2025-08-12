#!/usr/bin/env python3
"""
Create test tasks to demonstrate pagination
"""
import sqlite3
import time

def create_test_tasks():
    """Create multiple test tasks to demonstrate pagination"""
    
    print("=== Creating Test Tasks for Pagination Demo ===")
    
    with sqlite3.connect('octopus.db') as conn:
        cursor = conn.cursor()
        
        # Check current task count
        cursor.execute('SELECT COUNT(*) FROM tasks')
        current_count = cursor.fetchone()[0]
        print(f"Current task count: {current_count}")
        
        if current_count >= 30:
            print("Already have enough tasks for pagination demo")
            return
        
        # Create test tasks to reach 30 total (for pagination demo)
        tasks_to_create = 30 - current_count
        print(f"Creating {tasks_to_create} test tasks...")
        
        for i in range(tasks_to_create):
            task_id = f"test_task_{int(time.time() * 1000)}_{i}"
            task_name = f"Test Task {i + 1 + current_count}"
            
            conn.execute('''
                INSERT INTO tasks (id, name, owner, type, status, plugin, action, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                task_name,
                "Anyone" if i % 3 == 0 else "ALL" if i % 3 == 1 else "test-user",
                "adhoc",
                "pending",
                "web_utils",
                "create_incident",
                time.time(),
                time.time()
            ))
        
        conn.commit()
        
        # Verify final count
        cursor.execute('SELECT COUNT(*) FROM tasks')
        final_count = cursor.fetchone()[0]
        print(f"✅ Final task count: {final_count}")
        
        # Show pagination breakdown
        page_size = 25
        total_pages = (final_count + page_size - 1) // page_size
        print(f"\nPagination Breakdown (page size: {page_size}):")
        print(f"  Total pages: {total_pages}")
        for page in range(1, total_pages + 1):
            start = (page - 1) * page_size + 1
            end = min(page * page_size, final_count)
            print(f"  Page {page}: Tasks {start}-{end}")

if __name__ == "__main__":
    create_test_tasks()
