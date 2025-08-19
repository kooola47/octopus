import sqlite3
import sys
import os

def check_and_create_user():
    conn = sqlite3.connect('octopus_server/octopus.db')
    cursor = conn.cursor()
    
    username = 'aries-7044'
    
    print("=== USER CREATION FOR aries-7044 ===")
    
    # Check users table structure
    cursor.execute('PRAGMA table_info(users)')
    user_columns = cursor.fetchall()
    print('Users table structure:')
    for col in user_columns:
        print(f'  {col[1]} ({col[2]})')
    
    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        print(f'\nUser {username} already exists: {existing_user}')
    else:
        print(f'\nUser {username} does not exist. Creating...')
        
        # Create the user record
        try:
            cursor.execute('''
                INSERT INTO users (username, email, created_at, updated_at, active) 
                VALUES (?, ?, datetime('now'), datetime('now'), 1)
            ''', (username, f'{username}@localhost'))
            
            conn.commit()
            print(f'✅ User {username} created successfully!')
            
            # Verify creation
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            new_user = cursor.fetchone()
            print(f'New user record: {new_user}')
            
        except Exception as e:
            print(f'❌ Error creating user: {e}')
    
    # Check all existing users
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    print(f'\nAll users in system: {len(all_users)} records')
    for user in all_users:
        print(f'  {user}')
    
    conn.close()

def setup_user_profile():
    print("\n=== SETTING UP USER PROFILE IN CACHE ===")
    try:
        sys.path.append('./octopus_server')
        from global_cache_manager import get_global_cache_manager
        
        cache_manager = get_global_cache_manager()
        username = 'aries-7044'
        
        # Set up basic user profile
        profile_data = {
            'theme': 'dark',
            'language': 'en',
            'timezone': 'UTC',
            'notifications': True,
            'created_at': '2025-08-20',
            'last_login': '2025-08-20'
        }
        
        cache_manager.set_user_profile_data(username, profile_data, requesting_user=username)
        print(f'✅ Profile data set for {username}')
        
        # Set up user settings
        cache_manager.set_user_setting(username, 'theme', 'dark', requesting_user=username)
        cache_manager.set_user_setting(username, 'auto_refresh', True, requesting_user=username)
        cache_manager.set_user_setting(username, 'task_notifications', True, requesting_user=username)
        
        print(f'✅ User settings configured for {username}')
        
        # Verify the data
        retrieved_profile = cache_manager.get_user_profile_data(username, requesting_user=username)
        print(f'Profile data: {retrieved_profile}')
        
        theme = cache_manager.get_user_setting(username, 'theme', requesting_user=username)
        print(f'Theme setting: {theme}')
        
    except ImportError as e:
        print(f'❌ Cannot import cache manager: {e}')
    except Exception as e:
        print(f'❌ Error setting up profile: {e}')

if __name__ == "__main__":
    check_and_create_user()
    setup_user_profile()
