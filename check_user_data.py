#!/usr/bin/env python3
"""
Check user data for aries-7044
"""
import sqlite3
import sys
import os

# Change to server directory
os.chdir('octopus_server')

def check_user_data():
    conn = sqlite3.connect('octopus.db')
    cursor = conn.cursor()

    username = 'aries-7044'
    print(f'=== USER DATA FOR {username} ===')

    # Check users table
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    users = cursor.fetchall()
    print(f'Users table: {len(users)} records')
    if users:
        print('User record:', users[0])

    # Check heartbeats
    cursor.execute('SELECT COUNT(*) FROM heartbeats WHERE username = ?', (username,))
    heartbeat_count = cursor.fetchone()[0]
    print(f'Heartbeats: {heartbeat_count} records')

    if heartbeat_count > 0:
        cursor.execute('SELECT * FROM heartbeats WHERE username = ? ORDER BY timestamp DESC LIMIT 1', (username,))
        latest_heartbeat = cursor.fetchone()
        print('Latest heartbeat:', latest_heartbeat)

    # Check user_parameters
    cursor.execute('SELECT * FROM user_parameters WHERE username = ?', (username,))
    user_params = cursor.fetchall()
    print(f'User parameters: {len(user_params)} records')
    if user_params:
        for param in user_params:
            print('Parameter:', param)

    # Check tasks created by user
    cursor.execute('SELECT COUNT(*) FROM tasks WHERE created_by = ?', (username,))
    tasks_created = cursor.fetchone()[0]
    print(f'Tasks created by user: {tasks_created}')

    # Check tasks assigned to user
    cursor.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ?', (username,))
    tasks_assigned = cursor.fetchone()[0]
    print(f'Tasks assigned to user: {tasks_assigned}')

    # Check plugin submissions
    cursor.execute('SELECT COUNT(*) FROM plugin_submissions WHERE username = ?', (username,))
    plugin_submissions = cursor.fetchone()[0]
    print(f'Plugin submissions: {plugin_submissions}')

    # Check execution records
    cursor.execute('SELECT COUNT(*) FROM executions WHERE client_name LIKE ?', (f'%{username}%',))
    executions = cursor.fetchone()[0]
    print(f'Execution records: {executions}')

    conn.close()

def check_global_cache():
    print('\n=== GLOBAL CACHE DATA ===')
    try:
        sys.path.append('./octopus_server')
        from global_cache_manager import get_global_cache_manager
        
        cache_manager = get_global_cache_manager()
        username = 'aries-7044'
        
        # Check user profile data
        try:
            profile_data = cache_manager.get_user_profile_data(username, requesting_user=username)
            print(f'User profile data: {profile_data}')
        except Exception as e:
            print(f'No profile data or error: {e}')

        # Check cache stats
        stats = cache_manager.get_stats()
        print(f'Cache stats: {stats}')

        # List cache contents
        try:
            user_profiles_cache = cache_manager._caches.get('user_profiles', {})
            if user_profiles_cache:
                print(f'User profiles cache keys: {list(user_profiles_cache.keys())}')
            else:
                print('No user profiles cache found')
        except Exception as e:
            print(f'Error accessing cache: {e}')

    except ImportError as e:
        print(f'Cannot import cache manager: {e}')

if __name__ == "__main__":
    check_user_data()
    check_global_cache()
