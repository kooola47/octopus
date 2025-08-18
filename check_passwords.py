#!/usr/bin/env python3
"""
Check for users with old hash format and fix them
"""

import sys
import os
import sqlite3

# Add the octopus_server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'octopus_server'))

from octopus_server.dbhelper import DB_FILE, hash_password

def check_and_fix_password_hashes():
    """Check for users with old hash format and suggest fixes"""
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Get all users and their password hashes
            users = conn.execute('SELECT id, username, password_hash FROM users').fetchall()
            
            old_format_users = []
            
            for user_id, username, password_hash in users:
                # Check if hash is in old format (no colon separator)
                if ':' not in password_hash:
                    old_format_users.append((user_id, username, password_hash))
            
            if old_format_users:
                print(f"Found {len(old_format_users)} users with old hash format:")
                for user_id, username, old_hash in old_format_users:
                    print(f"  - User ID {user_id}: {username}")
                
                print("\nThese users will need to have their passwords reset by an admin")
                print("or you can update the default admin password manually.")
                
                # Special handling for default admin
                admin_users = [u for u in old_format_users if u[1] == 'admin']
                if admin_users:
                    print(f"\nFound admin user with old hash format.")
                    print("Updating admin password to use new hash format...")
                    
                    # Update admin password to use new format
                    new_hash = hash_password('admin')
                    conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', 
                               (new_hash, 'admin'))
                    conn.commit()
                    print("Admin password updated successfully!")
            else:
                print("All users are using the correct salted hash format.")
                
    except Exception as e:
        print(f"Error checking password hashes: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(check_and_fix_password_hashes())
