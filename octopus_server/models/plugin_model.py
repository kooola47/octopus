#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Plugin Model
===============================

Plugin model for managing plugin metadata, versions, and distribution.
Handles all plugin-related database operations separately from other models.
"""

import os
import time
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class PluginModel(BaseModel):
    """Plugin model for plugin management operations"""
    
    TABLE_NAME = "plugins"
    REQUIRED_FIELDS = ["name", "file_path"]
    
    def init_table(self):
        """Initialize the plugins table"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS plugins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        file_path TEXT NOT NULL,
                        md5_hash TEXT,
                        version TEXT DEFAULT '1.0.0',
                        description TEXT,
                        author TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        file_size INTEGER,
                        last_modified REAL,
                        install_count INTEGER DEFAULT 0,
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_plugins_name ON plugins(name)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_plugins_is_active ON plugins(is_active)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_plugins_md5_hash ON plugins(md5_hash)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_plugins_last_modified ON plugins(last_modified)')
                
                conn.commit()
                logger.info("Plugins table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing plugins table: {e}")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate plugin data"""
        if not self._validate_required_fields(data):
            return False
        
        # Validate plugin name
        name = data.get('name', '').strip()
        if not name or len(name) < 3:
            logger.error("Plugin name must be at least 3 characters long")
            return False
        
        # Validate file path exists
        file_path = data.get('file_path', '')
        if not os.path.exists(file_path):
            logger.error(f"Plugin file does not exist: {file_path}")
            return False
        
        return True
    
    def _create_record(self, conn, data: Dict[str, Any]) -> Optional[int]:
        """Create a new plugin record"""
        data = self._add_timestamps(data)
        
        # Set defaults
        data.setdefault('version', '1.0.0')
        data.setdefault('is_active', True)
        data.setdefault('install_count', 0)
        
        # Calculate file metadata
        if os.path.exists(data['file_path']):
            data['file_size'] = os.path.getsize(data['file_path'])
            data['last_modified'] = os.path.getmtime(data['file_path'])
            data['md5_hash'] = self._calculate_md5(data['file_path'])
        
        cursor = conn.execute('''
            INSERT OR REPLACE INTO plugins 
            (name, file_path, md5_hash, version, description, author, 
             is_active, file_size, last_modified, install_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['file_path'],
            data.get('md5_hash'),
            data['version'],
            data.get('description'),
            data.get('author'),
            data['is_active'],
            data.get('file_size'),
            data.get('last_modified'),
            data['install_count'],
            data['created_at'],
            data['updated_at']
        ))
        conn.commit()
        
        plugin_id = cursor.lastrowid
        logger.info(f"Registered plugin {data['name']} with ID {plugin_id}")
        return plugin_id
    
    def _calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5 for {file_path}: {e}")
            return ""
    
    def get_plugin_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get plugin by name"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM plugins WHERE name=?", (name,))
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting plugin by name {name}: {e}")
            return None
    
    def get_active_plugins(self) -> List[Dict[str, Any]]:
        """Get all active plugins"""
        return self.get_all({'is_active': True})
    
    def get_plugin_names(self) -> List[str]:
        """Get list of active plugin names"""
        try:
            active_plugins = self.get_active_plugins()
            return [plugin['name'] for plugin in active_plugins]
        except Exception as e:
            logger.error(f"Error getting plugin names: {e}")
            return []

# Singleton instance
plugin_model = PluginModel()
