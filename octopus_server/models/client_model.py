#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Client Model
===============================

Client model for managing client connections and heartbeat tracking.
Handles all client-related database operations separately from other models.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class ClientModel(BaseModel):
    """Client model for client management operations"""
    
    TABLE_NAME = "clients"
    REQUIRED_FIELDS = ["client_id", "hostname"]
    
    def init_table(self):
        """Initialize the clients table"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id TEXT UNIQUE NOT NULL,
                        hostname TEXT NOT NULL,
                        ip_address TEXT,
                        username TEXT,
                        status TEXT DEFAULT 'active',
                        last_heartbeat REAL,
                        version TEXT,
                        platform TEXT,
                        capabilities TEXT DEFAULT '[]',
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_clients_client_id ON clients(client_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_clients_last_heartbeat ON clients(last_heartbeat)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_clients_hostname ON clients(hostname)')
                
                conn.commit()
                logger.info("Clients table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing clients table: {e}")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate client data"""
        if not self._validate_required_fields(data):
            return False
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'disconnected', 'maintenance']
        if data.get('status') and data['status'] not in valid_statuses:
            logger.error(f"Invalid client status: {data.get('status')}")
            return False
        
        return True
    
    def _create_record(self, conn, data: Dict[str, Any]) -> Optional[int]:
        """Create a new client record"""
        data = self._add_timestamps(data)
        
        # Set defaults
        data.setdefault('status', 'active')
        data.setdefault('last_heartbeat', time.time())
        data.setdefault('capabilities', '[]')
        
        cursor = conn.execute('''
            INSERT OR REPLACE INTO clients 
            (client_id, hostname, ip_address, username, status, last_heartbeat, 
             version, platform, capabilities, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['client_id'],
            data['hostname'],
            data.get('ip_address'),
            data.get('username'),
            data['status'],
            data['last_heartbeat'],
            data.get('version'),
            data.get('platform'),
            data['capabilities'],
            data['created_at'],
            data['updated_at']
        ))
        conn.commit()
        
        client_db_id = cursor.lastrowid
        logger.info(f"Registered client {data['client_id']} from {data['hostname']}")
        return client_db_id
    
    def get_client_by_client_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by client_id (not database id)"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM clients WHERE client_id=?", (client_id,))
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"Error getting client by client_id {client_id}: {e}")
            return None
    
    def update_client_heartbeat(self, client_id: str, heartbeat_data: Dict[str, Any] = None) -> bool:
        """Update client heartbeat and optional data"""
        updates = {
            'last_heartbeat': time.time(),
            'status': 'active'
        }
        
        if heartbeat_data:
            # Update other fields if provided in heartbeat
            if 'ip_address' in heartbeat_data:
                updates['ip_address'] = heartbeat_data['ip_address']
            if 'username' in heartbeat_data:
                updates['username'] = heartbeat_data['username']
            if 'version' in heartbeat_data:
                updates['version'] = heartbeat_data['version']
            if 'platform' in heartbeat_data:
                updates['platform'] = heartbeat_data['platform']
            if 'capabilities' in heartbeat_data:
                updates['capabilities'] = str(heartbeat_data['capabilities'])
        
        try:
            with self.get_db_connection() as conn:
                set_clause = ", ".join([f"{k}=?" for k in updates.keys()])
                query = f"UPDATE clients SET {set_clause} WHERE client_id=?"
                conn.execute(query, list(updates.values()) + [client_id])
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating client heartbeat for {client_id}: {e}")
            return False
    
    def get_active_clients(self, timeout_seconds: int = 30) -> List[Dict[str, Any]]:
        """Get clients that have sent heartbeat within timeout"""
        cutoff_time = time.time() - timeout_seconds
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM clients WHERE last_heartbeat > ? AND status = 'active' ORDER BY last_heartbeat DESC",
                    (cutoff_time,)
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting active clients: {e}")
            return []
    
    def get_inactive_clients(self, timeout_seconds: int = 30) -> List[Dict[str, Any]]:
        """Get clients that haven't sent heartbeat within timeout"""
        cutoff_time = time.time() - timeout_seconds
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM clients WHERE last_heartbeat <= ? OR status != 'active' ORDER BY last_heartbeat DESC",
                    (cutoff_time,)
                )
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting inactive clients: {e}")
            return []
    
    def mark_client_inactive(self, client_id: str) -> bool:
        """Mark a client as inactive"""
        return self.update_by_client_id(client_id, {'status': 'inactive'})
    
    def mark_client_disconnected(self, client_id: str) -> bool:
        """Mark a client as disconnected"""
        return self.update_by_client_id(client_id, {'status': 'disconnected'})
    
    def update_by_client_id(self, client_id: str, updates: Dict[str, Any]) -> bool:
        """Update client by client_id instead of database id"""
        try:
            updates['updated_at'] = time.time()
            with self.get_db_connection() as conn:
                set_clause = ", ".join([f"{k}=?" for k in updates.keys()])
                query = f"UPDATE clients SET {set_clause} WHERE client_id=?"
                conn.execute(query, list(updates.values()) + [client_id])
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating client {client_id}: {e}")
            return False
    
    def delete_by_client_id(self, client_id: str) -> bool:
        """Delete client by client_id"""
        try:
            with self.get_db_connection() as conn:
                conn.execute("DELETE FROM clients WHERE client_id=?", (client_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting client {client_id}: {e}")
            return False
    
    def get_client_stats(self) -> Dict[str, int]:
        """Get client statistics"""
        try:
            with self.get_db_connection() as conn:
                stats = {}
                
                # Total clients
                cursor = conn.execute("SELECT COUNT(*) FROM clients")
                stats['total'] = cursor.fetchone()[0]
                
                # Active clients (last 30 seconds)
                cutoff_time = time.time() - 30
                cursor = conn.execute("SELECT COUNT(*) FROM clients WHERE last_heartbeat > ? AND status = 'active'", (cutoff_time,))
                stats['active'] = cursor.fetchone()[0]
                
                # By status
                cursor = conn.execute("SELECT status, COUNT(*) FROM clients GROUP BY status")
                for status, count in cursor.fetchall():
                    stats[f'status_{status}'] = count
                
                return stats
        except Exception as e:
            logger.error(f"Error getting client stats: {e}")
            return {}
    
    def cleanup_old_clients(self, days_old: int = 7) -> int:
        """Remove clients that haven't been active for specified days"""
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            with self.get_db_connection() as conn:
                cursor = conn.execute("DELETE FROM clients WHERE last_heartbeat < ?", (cutoff_time,))
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old client records")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old clients: {e}")
            return 0
    
    def register_or_update_client(self, client_data: Dict[str, Any]) -> bool:
        """Register a new client or update existing one"""
        client_id = client_data.get('client_id')
        if not client_id:
            logger.error("No client_id provided for registration")
            return False
        
        existing_client = self.get_client_by_client_id(client_id)
        if existing_client:
            # Update existing client
            return self.update_client_heartbeat(client_id, client_data)
        else:
            # Create new client
            db_id = self.create(client_data)
            return db_id is not None

# Singleton instance
client_model = ClientModel()