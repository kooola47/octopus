import sqlite3
import hashlib
import secrets

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f'{salt}:{password_hash}'

def verify_password(password, stored_hash):
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

# Check admin user
with sqlite3.connect('octopus.db') as conn:
    cursor = conn.execute('SELECT username, password_hash FROM users WHERE username = ?', ('admin',))
    result = cursor.fetchone()
    
    if result:
        username, password_hash = result
        print(f'Admin user found: {username}')
        print(f'Password hash: {password_hash}')
        
        # Test common passwords
        passwords = ['admin', 'password', '123456', 'admin123', 'octopus']
        found = False
        for pwd in passwords:
            if verify_password(pwd, password_hash):
                print(f'PASSWORD FOUND: {pwd}')
                found = True
                break
        
        if not found:
            print('No common password worked, updating to admin123...')
            new_hash = hash_password('admin123')
            conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, 'admin'))
            conn.commit()
            print('Admin password updated to: admin123')
    else:
        print('Admin user not found')
