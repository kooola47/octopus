#!/usr/bin/env python3
"""
Force update scheduled tasks to Active status
"""

import sqlite3
import time

def main():
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()

    current_time = time.time()

    # Force update all scheduled tasks to Active status
    cursor.execute('''
        UPDATE tasks 
        SET status = 'Active', updated_at = ? 
        WHERE type IN ('scheduled', 'Schedule')
    ''', (current_time,))

    affected_rows = cursor.rowcount
    print(f'Updated {affected_rows} scheduled tasks to Active status')

    conn.commit()
    conn.close()
    print('Done!')

if __name__ == '__main__':
    main()
