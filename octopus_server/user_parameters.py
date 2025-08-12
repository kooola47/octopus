#!/usr/bin/env python3
"""
👤 USER PROFILE PARAMETERS SYSTEM
=================================

Manages user-specific configuration parameters that can be accessed by plugins.
Supports encrypted storage of sensitive data like API keys.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
import base64
import hashlib
import os

logger = logging.getLogger(__name__)

class UserParametersManager:
    """Manages user-specific parameters for plugin customization"""
    
    def __init__(self, db_helper):
        self.db_helper = db_helper
        self.encryption_key = self._get_or_create_encryption_key()
        self.init_tables()
    
    def _get_or_create_encryption_key(self) -> str:
        """Get or create encryption key for sensitive parameters"""
        key_file = "user_params_key.txt"
        
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                return f.read().strip()
        else:
            # Generate new key (simple base64 key)
            import secrets
            key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            with open(key_file, 'w') as f:
                f.write(key)
            logger.info("Generated new encryption key for user parameters")
            return key
    
    def _encrypt_value(self, value: str) -> str:
        """Simple encryption using base64 and key XOR"""
        try:
            # Simple XOR encryption with the key
            key_bytes = self.encryption_key.encode()
            value_bytes = value.encode()
            
            encrypted = bytearray()
            for i, byte in enumerate(value_bytes):
                encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting value: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Simple decryption using base64 and key XOR"""
        try:
            # Reverse XOR encryption
            key_bytes = self.encryption_key.encode()
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            return encrypted_value
    
    def init_tables(self):
        """Initialize user parameters tables"""
        try:
            with self.db_helper.get_connection() as conn:
                # User parameters table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_parameters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        category TEXT NOT NULL,
                        param_name TEXT NOT NULL,
                        param_value TEXT,
                        param_type TEXT DEFAULT 'string',
                        is_encrypted BOOLEAN DEFAULT 0,
                        is_sensitive BOOLEAN DEFAULT 0,
                        description TEXT,
                        created_at REAL,
                        updated_at REAL,
                        UNIQUE(username, category, param_name)
                    )
                ''')
                
                # User parameter categories table (for organization)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_parameter_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        category_name TEXT NOT NULL,
                        display_name TEXT NOT NULL,
                        description TEXT,
                        icon TEXT,
                        sort_order INTEGER DEFAULT 0,
                        created_at REAL,
                        UNIQUE(username, category_name)
                    )
                ''')
                
                # Create indexes
                conn.execute('CREATE INDEX IF NOT EXISTS idx_user_params_username ON user_parameters(username)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_user_params_category ON user_parameters(username, category)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_user_params_name ON user_parameters(username, param_name)')
                
                conn.commit()
            logger.info("User parameters tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing user parameters tables: {e}")
    
    def set_parameter(self, username: str, category: str, param_name: str, value: Any, 
                     param_type: str = 'string', is_sensitive: bool = False, 
                     description: str = '') -> bool:
        """Set a user parameter"""
        try:
            with self.db_helper.get_connection() as conn:
                # Convert value to string for storage
                if param_type == 'json':
                    param_value = json.dumps(value)
                else:
                    param_value = str(value)
                
                # Encrypt if sensitive
                is_encrypted = False
                if is_sensitive and param_value:
                    param_value = self._encrypt_value(param_value)
                    is_encrypted = True
                
                current_time = time.time()
                
                # Insert or update parameter
                conn.execute('''
                    INSERT OR REPLACE INTO user_parameters 
                    (username, category, param_name, param_value, param_type, 
                     is_encrypted, is_sensitive, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT created_at FROM user_parameters 
                                    WHERE username=? AND category=? AND param_name=?), ?), ?)
                ''', (username, category, param_name, param_value, param_type,
                      is_encrypted, is_sensitive, description,
                      username, category, param_name, current_time, current_time))
                
                conn.commit()
            
            logger.info(f"Set parameter {category}.{param_name} for user {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting parameter {category}.{param_name} for user {username}: {e}")
            return False
    
    def get_parameter(self, username: str, category: str, param_name: str, default_value: Any = None) -> Any:
        """Get a user parameter value"""
        try:
            with self.db_helper.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT param_value, param_type, is_encrypted 
                    FROM user_parameters 
                    WHERE username=? AND category=? AND param_name=?
                ''', (username, category, param_name))
                
                result = cursor.fetchone()
            
            if not result:
                return default_value
            
            param_value, param_type, is_encrypted = result
            
            # Decrypt if encrypted
            if is_encrypted and param_value:
                try:
                    param_value = self._decrypt_value(param_value)
                except Exception as e:
                    logger.error(f"Error decrypting parameter {category}.{param_name}: {e}")
                    return default_value
            
            # Convert back to appropriate type
            if param_type == 'json':
                return json.loads(param_value) if param_value else default_value
            elif param_type == 'int':
                return int(param_value) if param_value else default_value
            elif param_type == 'float':
                return float(param_value) if param_value else default_value
            elif param_type == 'bool':
                return param_value.lower() in ('true', '1', 'yes') if param_value else default_value
            else:
                return param_value if param_value else default_value
                
        except Exception as e:
            logger.error(f"Error getting parameter {category}.{param_name} for user {username}: {e}")
            return default_value
    
    def get_user_parameters(self, username: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Get all parameters for a user, optionally filtered by category"""
        try:
            with self.db_helper.get_connection() as conn:
                if category:
                    cursor = conn.execute('''
                        SELECT category, param_name, param_value, param_type, is_encrypted, description
                        FROM user_parameters 
                        WHERE username=? AND category=?
                        ORDER BY category, param_name
                    ''', (username, category))
                else:
                    cursor = conn.execute('''
                        SELECT category, param_name, param_value, param_type, is_encrypted, description
                        FROM user_parameters 
                        WHERE username=?
                        ORDER BY category, param_name
                    ''', (username,))
                
                results = cursor.fetchall()
            
            parameters = {}
            for row in results:
                cat, name, value, param_type, is_encrypted, desc = row
                
                # Decrypt if encrypted
                if is_encrypted and value:
                    try:
                        value = self._decrypt_value(value)
                    except Exception as e:
                        logger.error(f"Error decrypting parameter {cat}.{name}: {e}")
                        continue
                
                # Convert to appropriate type
                if param_type == 'json':
                    value = json.loads(value) if value else {}
                elif param_type == 'int':
                    value = int(value) if value else 0
                elif param_type == 'float':
                    value = float(value) if value else 0.0
                elif param_type == 'bool':
                    value = value.lower() in ('true', '1', 'yes') if value else False
                
                # Organize by category
                if cat not in parameters:
                    parameters[cat] = {}
                parameters[cat][name] = {
                    'value': value,
                    'description': desc,
                    'type': param_type
                }
            
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting parameters for user {username}: {e}")
            return {}
    
    def delete_parameter(self, username: str, category: str, param_name: str) -> bool:
        """Delete a user parameter"""
        try:
            with self.db_helper.get_connection() as conn:
                cursor = conn.execute('''
                    DELETE FROM user_parameters 
                    WHERE username=? AND category=? AND param_name=?
                ''', (username, category, param_name))
                
                conn.commit()
                deleted = cursor.rowcount > 0
            
            if deleted:
                logger.info(f"Deleted parameter {category}.{param_name} for user {username}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting parameter {category}.{param_name} for user {username}: {e}")
            return False
    
    def set_category(self, username: str, category_name: str, display_name: str, 
                    description: str = '', icon: str = '', sort_order: int = 0) -> bool:
        """Set/update a parameter category"""
        try:
            with self.db_helper.get_connection() as conn:
                current_time = time.time()
                
                conn.execute('''
                    INSERT OR REPLACE INTO user_parameter_categories 
                    (username, category_name, display_name, description, icon, sort_order, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT created_at FROM user_parameter_categories 
                                    WHERE username=? AND category_name=?), ?))
                ''', (username, category_name, display_name, description, icon, sort_order,
                      username, category_name, current_time))
                
                conn.commit()
            
            logger.info(f"Set category {category_name} for user {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting category {category_name} for user {username}: {e}")
            return False
    
    def get_categories(self, username: str) -> List[Dict[str, Any]]:
        """Get all parameter categories for a user"""
        try:
            with self.db_helper.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT category_name, display_name, description, icon, sort_order
                    FROM user_parameter_categories 
                    WHERE username=?
                    ORDER BY sort_order, display_name
                ''', (username,))
                
                results = cursor.fetchall()
            
            categories = []
            for row in results:
                categories.append({
                    'name': row[0],
                    'display_name': row[1],
                    'description': row[2],
                    'icon': row[3],
                    'sort_order': row[4]
                })
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting categories for user {username}: {e}")
            return []
    
    def cache_user_parameters(self, username: str, cache_manager) -> bool:
        """Cache all user parameters for quick plugin access"""
        try:
            parameters = self.get_user_parameters(username)
            
            # Cache with structured keys for easy plugin access
            cache_key = f"user_params_{username}"
            cache_manager.set(cache_key, parameters, ttl=3600)  # 1 hour TTL
            
            # Also cache individual categories for faster access
            for category, params in parameters.items():
                category_key = f"user_params_{username}_{category}"
                cache_manager.set(category_key, params, ttl=3600)
            
            logger.info(f"Cached parameters for user {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching parameters for user {username}: {e}")
            return False


# Default parameter categories and examples
DEFAULT_CATEGORIES = {
    'api_credentials': {
        'display_name': 'API Credentials',
        'description': 'API keys and authentication tokens',
        'icon': 'fa-key',
        'sort_order': 1
    },
    'notifications': {
        'display_name': 'Notifications',
        'description': 'Email and messaging preferences',
        'icon': 'fa-bell',
        'sort_order': 2
    },
    'integrations': {
        'display_name': 'Integrations',
        'description': 'Third-party service configurations',
        'icon': 'fa-plug',
        'sort_order': 3
    },
    'preferences': {
        'display_name': 'Preferences',
        'description': 'General user preferences',
        'icon': 'fa-cog',
        'sort_order': 4
    },
    'custom': {
        'display_name': 'Custom Parameters',
        'description': 'User-defined custom parameters',
        'icon': 'fa-wrench',
        'sort_order': 5
    }
}

EXAMPLE_PARAMETERS = {
    'api_credentials': {
        'servicenow_api_key': {
            'description': 'ServiceNow API Key',
            'type': 'string',
            'sensitive': True
        },
        'jira_token': {
            'description': 'Jira API Token',
            'type': 'string',
            'sensitive': True
        },
        'slack_webhook': {
            'description': 'Slack Webhook URL',
            'type': 'string',
            'sensitive': True
        }
    },
    'notifications': {
        'email_address': {
            'description': 'Primary email for notifications',
            'type': 'string',
            'sensitive': False
        },
        'notify_on_completion': {
            'description': 'Send notification when tasks complete',
            'type': 'bool',
            'sensitive': False
        },
        'notification_channels': {
            'description': 'Preferred notification channels',
            'type': 'json',
            'sensitive': False
        }
    },
    'integrations': {
        'servicenow_instance': {
            'description': 'ServiceNow instance URL',
            'type': 'string',
            'sensitive': False
        },
        'jira_base_url': {
            'description': 'Jira base URL',
            'type': 'string',
            'sensitive': False
        },
        'default_priority': {
            'description': 'Default priority for tickets',
            'type': 'string',
            'sensitive': False
        }
    }
}
