#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Base Model
=============================

Base model class with common database operations and validation.
All models should inherit from this base class.
"""

import sqlite3
import time
import logging
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Union
from config import DB_FILE

logger = logging.getLogger(__name__)
_db_lock = threading.RLock()

class BaseModel(ABC):
    """Base model class with common database operations"""
    
    TABLE_NAME = None  # Must be defined in subclasses
    REQUIRED_FIELDS = []  # Must be defined in subclasses
    
    def __init__(self):
        self.init_table()
    
    @contextmanager
    def get_db_connection(self):
        """Thread-safe database connection context manager"""
        with _db_lock:
            conn = sqlite3.connect(DB_FILE)
            try:
                # Enable WAL mode for better concurrent performance
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                conn.execute('PRAGMA cache_size=10000')
                conn.execute('PRAGMA temp_store=memory')
                conn.execute('PRAGMA mmap_size=268435456')  # 256MB
                yield conn
            finally:
                conn.close()
    
    @abstractmethod
    def init_table(self):
        """Initialize the database table. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data before database operations. Must be implemented by subclasses."""
        pass
    
    def create(self, data: Dict[str, Any]) -> Optional[Union[str, int]]:
        """Create a new record"""
        if not self.validate_data(data):
            logger.error(f"Invalid data for {self.TABLE_NAME}: {data}")
            return None
        
        try:
            with self.get_db_connection() as conn:
                return self._create_record(conn, data)
        except Exception as e:
            logger.error(f"Error creating {self.TABLE_NAME} record: {e}")
            return None
    
    def get_by_id(self, record_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute(f"SELECT * FROM {self.TABLE_NAME} WHERE id=?", (record_id,))
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting {self.TABLE_NAME} by ID {record_id}: {e}")
            return None
    
    def get_all(self, conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all records with optional conditions"""
        try:
            with self.get_db_connection() as conn:
                if conditions:
                    where_clause = " AND ".join([f"{k}=?" for k in conditions.keys()])
                    query = f"SELECT * FROM {self.TABLE_NAME} WHERE {where_clause}"
                    cursor = conn.execute(query, list(conditions.values()))
                else:
                    cursor = conn.execute(f"SELECT * FROM {self.TABLE_NAME}")
                
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all {self.TABLE_NAME} records: {e}")
            return []
    
    def update(self, record_id: Union[str, int], updates: Dict[str, Any]) -> bool:
        """Update a record by ID"""
        try:
            updates['updated_at'] = time.time()
            with self.get_db_connection() as conn:
                set_clause = ", ".join([f"{k}=?" for k in updates.keys()])
                query = f"UPDATE {self.TABLE_NAME} SET {set_clause} WHERE id=?"
                conn.execute(query, list(updates.values()) + [record_id])
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating {self.TABLE_NAME} record {record_id}: {e}")
            return False
    
    def delete(self, record_id: Union[str, int]) -> bool:
        """Delete a record by ID"""
        try:
            with self.get_db_connection() as conn:
                conn.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id=?", (record_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting {self.TABLE_NAME} record {record_id}: {e}")
            return False
    
    def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional conditions"""
        try:
            with self.get_db_connection() as conn:
                if conditions:
                    where_clause = " AND ".join([f"{k}=?" for k in conditions.keys()])
                    query = f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE {where_clause}"
                    cursor = conn.execute(query, list(conditions.values()))
                else:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {self.TABLE_NAME}")
                
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting {self.TABLE_NAME} records: {e}")
            return 0
    
    @abstractmethod
    def _create_record(self, conn, data: Dict[str, Any]) -> Optional[Union[str, int]]:
        """Create record implementation. Must be implemented by subclasses."""
        pass
    
    def _add_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add created_at and updated_at timestamps to data"""
        now = time.time()
        data['created_at'] = data.get('created_at', now)
        data['updated_at'] = now
        return data
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> bool:
        """Validate that all required fields are present"""
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in data or data[field] is None]
        if missing_fields:
            logger.error(f"Missing required fields for {self.TABLE_NAME}: {missing_fields}")
            return False
        return True
