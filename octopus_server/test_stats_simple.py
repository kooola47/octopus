#!/usr/bin/env python3

import sqlite3
import sys
import os

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_db_file():
    return 'octopus.db'

# Test the actual get_execution_stats function
def test_get_execution_stats():
    print("Testing get_execution_stats function...")
    
    try:
        from constants import ExecutionStatus
        import logging
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("octopus_server")
        
        with sqlite3.connect(get_db_file()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all executions with their statuses
            cursor.execute("SELECT status FROM executions")
            all_executions = cursor.fetchall()
            
            total = len(all_executions)
            successful = 0
            failed = 0
            running = 0
            
            # Debug: log all statuses found
            status_found = [row['status'] for row in all_executions]
            print(f"Found {total} executions with statuses: {status_found}")
            
            # Count statuses using centralized logic
            for row in all_executions:
                status = row['status']
                normalized = ExecutionStatus.normalize(status)
                print(f"Status '{status}' normalized to '{normalized}'")
                
                if normalized == ExecutionStatus.SUCCESS:
                    successful += 1
                elif normalized == ExecutionStatus.FAILED:
                    failed += 1
                elif normalized == ExecutionStatus.RUNNING:
                    running += 1
            
            print(f"Stats - Total: {total}, Success: {successful}, Failed: {failed}, Running: {running}")
            
            # Calculate average duration for completed executions
            cursor.execute("""
                SELECT AVG(
                    CASE 
                        WHEN updated_at IS NOT NULL AND created_at IS NOT NULL 
                        THEN (updated_at - created_at)
                        ELSE NULL 
                    END
                ) as avg_duration 
                FROM executions 
                WHERE status IS NOT NULL
            """)
            avg_duration_result = cursor.fetchone()
            avg_duration = round(avg_duration_result['avg_duration'] or 0, 1)
            
            result = {
                'total_executions': total,
                'completed_executions': successful,
                'failed_executions': failed,
                'running_executions': running,
                'avg_duration': avg_duration
            }
            
            print(f"Final result: {result}")
            return result
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_executions': 0,
            'completed_executions': 0,
            'failed_executions': 0,
            'running_executions': 0,
            'avg_duration': 0
        }

if __name__ == "__main__":
    test_get_execution_stats()
