#!/usr/bin/env python3
"""
🔐 DEBUG ADMIN PASSWORD
======================

Script to check admin user password hash and create a test login.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from octopus_server.dbhelper import hash_password, verify_password, authenticate_user

def check_admin_user():
    """Check admin user details"""
    print("🔍 Checking admin user...")
    
    # Connect to database
    db_path = "octopus_server/octopus.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("""
            SELECT username, password_hash, role, is_active 
            FROM users 
            WHERE username = 'admin'
        """)
        
        result = cursor.fetchone()
        
        if result:
            username, password_hash, role, is_active = result
            print(f"✅ Admin user found:")
            print(f"   Username: {username}")
            print(f"   Role: {role}")
            print(f"   Active: {bool(is_active)}")
            print(f"   Password hash: {password_hash}")
            
            # Test common passwords
            common_passwords = ['admin', 'password', '123456', 'admin123', 'octopus']
            
            print(f"\n🔐 Testing common passwords...")
            for pwd in common_passwords:
                if verify_password(pwd, password_hash):
                    print(f"✅ Password found: '{pwd}'")
                    return pwd
                else:
                    print(f"❌ Not '{pwd}'")
            
            print(f"\n⚠️  None of the common passwords work.")
            return None
        else:
            print("❌ Admin user not found")
            return None

def create_new_admin_password():
    """Create new admin user with known password"""
    print("\n🔧 Creating new admin user with password 'admin123'...")
    
    db_path = "octopus_server/octopus.db"
    password = "admin123"
    
    # Hash the password
    password_hash = hash_password(password)
    
    with sqlite3.connect(db_path) as conn:
        # Update existing admin user
        conn.execute("""
            UPDATE users 
            SET password_hash = ?, updated_at = ?
            WHERE username = 'admin'
        """, (password_hash, time.time()))
        
        conn.commit()
    
    print(f"✅ Admin password updated to: '{password}'")
    
    # Test the new password
    result = authenticate_user('admin', password)
    if result:
        print(f"✅ Authentication test successful!")
        return password
    else:
        print(f"❌ Authentication test failed!")
        return None

if __name__ == "__main__":
    import time
    
    # Check existing admin
    found_password = check_admin_user()
    
    if not found_password:
        # Create new password
        found_password = create_new_admin_password()
    
    if found_password:
        print(f"\n🎉 Admin login credentials:")
        print(f"   Username: admin")
        print(f"   Password: {found_password}")
    else:
        print(f"\n❌ Could not determine admin password")
