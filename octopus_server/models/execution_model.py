#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Execution Model
==================================

Execution model for managing task execution records and business logic.
Handles all execution-related database operations separately from other models.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class ExecutionModel(BaseModel):
    """Execution model for task execution management operations"""
    
    TABLE_NAME = "executions"
    REQUIRED_FIELDS = ["execution_id", "task_id", "client"]
    
    def init_table(self):
        """Initialize the executions table"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execution_id TEXT UNIQUE NOT NULL,
                        task_id TEXT NOT NULL,
                        client TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        result TEXT DEFAULT '',
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_execution_id ON executions(execution_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_task_id ON executions(task_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_client ON executions(client)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_executions_updated_at ON executions(updated_at)')
                
                conn.commit()
                logger.info("Executions table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing executions table: {e}")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate execution data"""
        if not self._validate_required_fields(data):
            return False
        
        # Validate execution_id uniqueness (will be handled by database constraint)
        # Validate status
        valid_statuses = ['pending', 'running', 'success', 'failed', 'completed', 'error']
        if data.get('status') and data['status'] not in valid_statuses:
            logger.error(f"Invalid execution status: {data.get('status')}")
            return False
        
        return True
    
    def _create_record(self, conn, data: Dict[str, Any]) -> Optional[int]:
        """Create a new execution record"""
        data = self._add_timestamps(data)
        
        # Set defaults
        data.setdefault('status', 'pending')
        data.setdefault('result', '')
        
        cursor = conn.execute('''
            INSERT INTO executions 
            (execution_id, task_id, client, status, result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['execution_id'],
            data['task_id'],
            data['client'],
            data['status'],
            data['result'],
            data['created_at'],
            data['updated_at']
        ))
        conn.commit()
        
        execution_db_id = cursor.lastrowid
        logger.info(f"Created execution {data['execution_id']} for task {data['task_id']} by client {data['client']}")
        return execution_db_id
    
    def get_executions_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all executions for a specific task"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, execution_id, client, status, result, created_at, updated_at "
                    "FROM executions WHERE task_id=? ORDER BY created_at DESC", 
                    (task_id,)
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting executions for task {task_id}: {e}")
            return []
    
    def get_executions_by_client(self, client: str) -> List[Dict[str, Any]]:
        """Get all executions for a specific client"""
        return self.get_all({"client": client})
    
    def get_executions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all executions with a specific status"""
        return self.get_all({"status": status})
    
    def get_execution_by_execution_id(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by execution_id (not database id)"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,))
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting execution by execution_id {execution_id}: {e}")
            return None
    
    def update_execution_status(self, execution_id: str, status: str, result: str = "") -> bool:
        """Update execution status and result"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    UPDATE executions SET status=?, result=?, updated_at=? 
                    WHERE execution_id=?
                ''', (status, result, time.time(), execution_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating execution {execution_id}: {e}")
            return False
    
    def add_execution_result(self, task_id: str, client: str, status: str, result: str = "") -> str:
        """Add a new execution result and return execution_id"""
        # Generate unique execution ID
        execution_id = f"{task_id}_{client}_{int(time.time() * 1000)}"
        
        execution_data = {
            "execution_id": execution_id,
            "task_id": task_id,
            "client": client,
            "status": status,
            "result": result
        }
        
        db_id = self.create(execution_data)
        if db_id:
            return execution_id
        return None
    
    def get_recent_executions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent executions with limit"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM executions ORDER BY created_at DESC LIMIT ?", 
                    (limit,)
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting recent executions: {e}")
            return []
    
    def get_execution_stats(self) -> Dict[str, int]:
        """Get execution statistics"""
        try:
            with self.get_db_connection() as conn:
                stats = {}
                
                # Total executions
                cursor = conn.execute("SELECT COUNT(*) FROM executions")
                stats['total'] = cursor.fetchone()[0]
                
                # By status
                cursor = conn.execute("SELECT status, COUNT(*) FROM executions GROUP BY status")
                for status, count in cursor.fetchall():
                    stats[f'status_{status}'] = count
                
                return stats
        except Exception as e:
            logger.error(f"Error getting execution stats: {e}")
            return {}
    
    def delete_executions_by_task(self, task_id: str) -> bool:
        """Delete all executions for a specific task"""
        try:
            with self.get_db_connection() as conn:
                conn.execute("DELETE FROM executions WHERE task_id=?", (task_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting executions for task {task_id}: {e}")
            return False
    
    def delete_old_executions(self, days_old: int = 30) -> int:
        """Delete executions older than specified days"""
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            with self.get_db_connection() as conn:
                cursor = conn.execute("DELETE FROM executions WHERE created_at < ?", (cutoff_time,))
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Deleted {deleted_count} old execution records")
                return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old executions: {e}")
            return 0

# Singleton instance
execution_model = ExecutionModel()