#!/usr/bin/env python3
"""
Reset scheduled tasks back to Active status if still within execution window
"""

import sqlite3
import time
from datetime import datetime

def main():
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()

    # Reset scheduled tasks that are still within their execution window
    current_time = time.time()

    # Find scheduled tasks marked as Done that are still within execution window
    cursor.execute('''
        SELECT id, execution_end_time 
        FROM tasks 
        WHERE type IN ('scheduled', 'Schedule') 
        AND status = 'Done'
        AND execution_end_time IS NOT NULL
    ''')

    tasks_to_reset = []
    for task_id, end_time in cursor.fetchall():
        try:
            end_timestamp = float(end_time)
            if current_time < end_timestamp:
                tasks_to_reset.append((task_id, end_timestamp))
        except:
            pass

    print(f'Found {len(tasks_to_reset)} scheduled tasks to reset to Active status')

    for task_id, end_timestamp in tasks_to_reset:
        cursor.execute('''
            UPDATE tasks SET status = 'Active', updated_at = ? WHERE id = ?
        ''', (current_time, task_id))
        end_dt = datetime.fromtimestamp(end_timestamp)
        print(f'Reset task {task_id} to Active (ends at {end_dt.strftime("%Y-%m-%d %H:%M:%S")})')

    conn.commit()
    conn.close()
    print('Done!')

if __name__ == '__main__':
    main()
