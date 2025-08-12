#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - User Model
=============================

User model for managing user accounts, authentication, and authorization.
Handles all user-related database operations separately from other models.
"""

import time
import hashlib
import secrets
import logging
from typing import Dict, List, Optional, Any, Union
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class UserModel(BaseModel):
    """User model for user management operations"""
    
    TABLE_NAME = "users"
    REQUIRED_FIELDS = ["username", "password_hash"]
    
    def init_table(self):
        """Initialize the users table"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        is_active BOOLEAN DEFAULT 1,
                        last_login REAL,
                        login_attempts INTEGER DEFAULT 0,
                        locked_until REAL,
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)')
                
                conn.commit()
                logger.info("Users table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing users table: {e}")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate user data"""
        if not self._validate_required_fields(data):
            return False
        
        # Validate username
        username = data.get('username', '').strip()
        if not username or len(username) < 3:
            logger.error("Username must be at least 3 characters long")
            return False
        
        # Validate role
        valid_roles = ['admin', 'user', 'viewer']
        if data.get('role') and data['role'] not in valid_roles:
            logger.error(f"Invalid user role: {data.get('role')}")
            return False
        
        # Validate email format if provided
        email = data.get('email', '').strip()
        if email and '@' not in email:
            logger.error(f"Invalid email format: {email}")
            return False
        
        return True
    
    def _create_record(self, conn, data: Dict[str, Any]) -> Optional[int]:
        """Create a new user record"""
        data = self._add_timestamps(data)
        
        # Set defaults
        data.setdefault('role', 'user')
        data.setdefault('is_active', True)
        data.setdefault('login_attempts', 0)
        
        # Generate salt if not provided
        if 'salt' not in data:
            data['salt'] = secrets.token_hex(16)
        
        cursor = conn.execute('''
            INSERT INTO users 
            (username, email, password_hash, salt, role, is_active, 
             login_attempts, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['username'],
            data.get('email', ''),
            data['password_hash'],
            data['salt'],
            data['role'],
            data['is_active'],
            data['login_attempts'],
            data['created_at'],
            data['updated_at']
        ))
        conn.commit()
        
        user_id = cursor.lastrowid
        logger.info(f"Created user {data['username']} with ID {user_id}")
        return user_id
    
    def hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash a password with salt using SHA-256"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine password and salt
        password_salt = f"{password}{salt}"
        
        # Hash using SHA-256
        hash_obj = hashlib.sha256(password_salt.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify a password against the stored hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return computed_hash == stored_hash
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def create_user(self, username: str, password: str, email: str = '', role: str = 'user', is_active: bool = True) -> Optional[int]:
        """Create a new user with hashed password"""
        try:
            # Hash the password
            password_hash, salt = self.hash_password(password)
            
            user_data = {
                'username': username.strip(),
                'email': email.strip(),
                'password_hash': password_hash,
                'salt': salt,
                'role': role,
                'is_active': is_active
            }
            
            return self.create(user_data)
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data if successful"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None
            
            # Check if user is active
            if not user.get('is_active', False):
                logger.warning(f"Login attempt for inactive user: {username}")
                return None
            
            # Check if user is locked
            if self._is_user_locked(user):
                logger.warning(f"Login attempt for locked user: {username}")
                return None
            
            # Verify password
            if self.verify_password(password, user['password_hash'], user['salt']):
                # Reset login attempts on successful login
                self.update(user['id'], {
                    'login_attempts': 0,
                    'last_login': time.time(),
                    'locked_until': None
                })
                
                # Remove sensitive data before returning
                user_safe = user.copy()
                user_safe.pop('password_hash', None)
                user_safe.pop('salt', None)
                
                logger.info(f"Successful login for user: {username}")
                return user_safe
            else:
                # Increment login attempts
                login_attempts = user.get('login_attempts', 0) + 1
                updates = {'login_attempts': login_attempts}
                
                # Lock user if too many attempts
                if login_attempts >= 5:
                    updates['locked_until'] = time.time() + (15 * 60)  # Lock for 15 minutes
                
                self.update(user['id'], updates)
                logger.warning(f"Failed login attempt for user: {username} (attempt {login_attempts})")
                return None
                
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM users WHERE username=?", (username,))
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM users WHERE email=?", (email,))
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        try:
            password_hash, salt = self.hash_password(new_password)
            return self.update(user_id, {
                'password_hash': password_hash,
                'salt': salt,
                'login_attempts': 0,  # Reset login attempts
                'locked_until': None  # Unlock user
            })
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account"""
        return self.update(user_id, {'is_active': True})
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account"""
        return self.update(user_id, {'is_active': False})
    
    def unlock_user(self, user_id: int) -> bool:
        """Unlock a user account"""
        return self.update(user_id, {
            'login_attempts': 0,
            'locked_until': None
        })
    
    def change_user_role(self, user_id: int, new_role: str) -> bool:
        """Change user role"""
        valid_roles = ['admin', 'user', 'viewer']
        if new_role not in valid_roles:
            logger.error(f"Invalid role: {new_role}")
            return False
        
        return self.update(user_id, {'role': new_role})
    
    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get all users with a specific role"""
        return self.get_all({'role': role})
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users"""
        return self.get_all({'is_active': True})
    
    def _is_user_locked(self, user: Dict[str, Any]) -> bool:
        """Check if user is currently locked"""
        locked_until = user.get('locked_until')
        if locked_until and locked_until > time.time():
            return True
        return False
    
    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        try:
            with self.get_db_connection() as conn:
                stats = {}
                
                # Total users
                cursor = conn.execute("SELECT COUNT(*) FROM users")
                stats['total'] = cursor.fetchone()[0]
                
                # Active users
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                stats['active'] = cursor.fetchone()[0]
                
                # By role
                cursor = conn.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
                for role, count in cursor.fetchall():
                    stats[f'role_{role}'] = count
                
                return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}

# Singleton instance
user_model = UserModel()
