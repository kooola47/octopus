#!/usr/bin/env python3
"""
Client Cache Manager
===================
Manages cached client data with real-time heartbeat updates
"""

import time
import threading
import sqlite3
import logging
from typing import Dict, Any, Optional, List
from dbhelper import get_db_file

class ClientCacheManager:
    """Manages client cache with real-time heartbeat synchronization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Cache storage - one record per client (username)
        self._cache = {
            'clients': {},  # {username: client_data}
            'stats': {
                'online': 0,
                'idle': 0,
                'offline': 0,
                'total': 0
            },
            'last_updated': 0
        }
        
        # Thread lock for cache updates
        self._lock = threading.Lock()
        
        # Load initial data
        self._initialize_cache()
        
    def _initialize_cache(self):
        """Initialize cache from database on startup"""
        try:
            self.logger.info("Initializing client cache from database...")
            with self._lock:
                self._load_clients_from_db()
                self._calculate_stats()
            self.logger.info(f"Client cache initialized with {len(self._cache['clients'])} clients")
        except Exception as e:
            self.logger.error(f"Error initializing client cache: {e}")
    
    def _load_clients_from_db(self):
        """Load latest client data from database"""
        try:
            with sqlite3.connect(get_db_file()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get latest heartbeat for each client (one record per username)
                cursor.execute("""
                    SELECT 
                        h1.username,
                        h1.hostname,
                        h1.ip_address,
                        h1.timestamp,
                        h1.cpu_usage,
                        h1.memory_usage
                    FROM heartbeats h1
                    WHERE h1.username IS NOT NULL
                        AND h1.timestamp = (
                            SELECT MAX(timestamp) 
                            FROM heartbeats h2 
                            WHERE h2.username = h1.username
                        )
                    ORDER BY h1.username
                """)
                
                self._cache['clients'] = {}
                current_time = time.time()
                
                for row in cursor.fetchall():
                    client_data = self._create_client_data(dict(row), current_time)
                    self._cache['clients'][row['username']] = client_data
                    
        except Exception as e:
            self.logger.error(f"Error loading clients from database: {e}")
    
    def _create_client_data(self, heartbeat_row: Dict, current_time: float) -> Dict[str, Any]:
        """Create standardized client data structure"""
        time_diff = current_time - heartbeat_row['timestamp']
        
        # Determine status based on last heartbeat
        if time_diff < 60:  # < 1 minute
            status = 'online'
        elif time_diff < 300:  # < 5 minutes
            status = 'idle'
        else:
            status = 'offline'
        
        return {
            'id': heartbeat_row['username'],
            'name': heartbeat_row['username'],
            'username': heartbeat_row['username'],
            'hostname': heartbeat_row['hostname'] or 'unknown',
            'ip_address': heartbeat_row['ip_address'] or '127.0.0.1',
            'status': status,
            'last_heartbeat': heartbeat_row['timestamp'],
            'last_seen': heartbeat_row['timestamp'],
            'cpu_usage': round(heartbeat_row.get('cpu_usage', 0.0), 1),
            'memory_usage': round(heartbeat_row.get('memory_usage', 0.0), 1),
            'version': 'v2.0.0',
            'time_diff': time_diff
        }
    
    def _calculate_stats(self):
        """Calculate client statistics from cache"""
        online = idle = offline = 0
        
        for client in self._cache['clients'].values():
            if client['status'] == 'online':
                online += 1
            elif client['status'] == 'idle':
                idle += 1
            else:
                offline += 1
        
        self._cache['stats'] = {
            'online': online,
            'idle': idle,
            'offline': offline,
            'total': len(self._cache['clients'])
        }
        self._cache['last_updated'] = time.time()
    
    def update_client_heartbeat(self, username: str, hostname: str, ip_address: str, 
                              cpu_usage: float = 0.0, memory_usage: float = 0.0) -> bool:
        """
        Update client heartbeat in both cache and database
        
        Args:
            username: Client username (unique identifier)
            hostname: Client hostname
            ip_address: Client IP address
            cpu_usage: CPU usage percentage
            memory_usage: Memory usage percentage
            
        Returns:
            bool: True if update successful
        """
        try:
            current_time = time.time()
            
            # Update database first
            with sqlite3.connect(get_db_file()) as conn:
                cursor = conn.cursor()
                
                # Insert new heartbeat record
                cursor.execute("""
                    INSERT INTO heartbeats (username, hostname, ip_address, timestamp, cpu_usage, memory_usage)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, hostname, ip_address, current_time, cpu_usage, memory_usage))
                
                # Clean up old heartbeat records for this client (keep only latest)
                cursor.execute("""
                    DELETE FROM heartbeats 
                    WHERE username = ? AND timestamp < ?
                """, (username, current_time))
                
                conn.commit()
            
            # Update cache
            with self._lock:
                heartbeat_data = {
                    'username': username,
                    'hostname': hostname,
                    'ip_address': ip_address,
                    'timestamp': current_time,
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage
                }
                
                client_data = self._create_client_data(heartbeat_data, current_time)
                self._cache['clients'][username] = client_data
                self._calculate_stats()
            
            self.logger.debug(f"Updated heartbeat for client {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating client heartbeat for {username}: {e}")
            return False
    
    def delete_client(self, username: str) -> bool:
        """
        Delete client from both cache and database
        
        Args:
            username: Client username to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            # Delete from database
            with sqlite3.connect(get_db_file()) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM heartbeats WHERE username = ?", (username,))
                deleted_count = cursor.rowcount
                conn.commit()
            
            # Delete from cache
            with self._lock:
                if username in self._cache['clients']:
                    del self._cache['clients'][username]
                    self._calculate_stats()
                    cache_deleted = True
                else:
                    cache_deleted = False
            
            self.logger.info(f"Deleted client {username}: DB records={deleted_count}, Cache={'yes' if cache_deleted else 'no'}")
            return deleted_count > 0 or cache_deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting client {username}: {e}")
            return False
    
    def get_clients_paginated(self, page: int = 1, page_size: int = 25, 
                             search: str = '', status_filter: str = '') -> tuple:
        """
        Get paginated clients from cache with filtering
        
        Args:
            page: Page number (1-based)
            page_size: Number of clients per page
            search: Search term for hostname, username, or IP
            status_filter: Filter by status (online, idle, offline)
            
        Returns:
            tuple: (clients_list, total_count)
        """
        with self._lock:
            # Update client statuses based on current time
            current_time = time.time()
            filtered_clients = []
            
            for client in self._cache['clients'].values():
                # Update status based on current time
                time_diff = current_time - client['last_heartbeat']
                if time_diff < 60:
                    client['status'] = 'online'
                elif time_diff < 300:
                    client['status'] = 'idle'
                else:
                    client['status'] = 'offline'
                client['time_diff'] = time_diff
                
                # Apply filters
                if search:
                    search_lower = search.lower()
                    if not (search_lower in client['username'].lower() or
                           search_lower in client['hostname'].lower() or
                           search_lower in client['ip_address'].lower()):
                        continue
                
                if status_filter and client['status'] != status_filter:
                    continue
                
                filtered_clients.append(client.copy())
            
            # Sort by username
            filtered_clients.sort(key=lambda x: x['username'])
            
            # Calculate pagination
            total_count = len(filtered_clients)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_clients = filtered_clients[start_idx:end_idx]
            
            # Recalculate stats with updated statuses
            self._calculate_stats()
            
            return page_clients, total_count
    
    def get_client_stats(self) -> Dict[str, int]:
        """Get client statistics from cache"""
        with self._lock:
            # Update stats with current time
            current_time = time.time()
            online = idle = offline = 0
            
            for client in self._cache['clients'].values():
                time_diff = current_time - client['last_heartbeat']
                if time_diff < 60:
                    online += 1
                elif time_diff < 300:
                    idle += 1
                else:
                    offline += 1
            
            stats = {
                'online_clients': online,
                'idle_clients': idle,
                'offline_clients': offline,
                'total_clients': len(self._cache['clients'])
            }
            
            # Update cached stats
            self._cache['stats'] = {
                'online': online,
                'idle': idle,
                'offline': offline,
                'total': len(self._cache['clients'])
            }
            
            return stats
    
    def get_client_by_id(self, username: str) -> Optional[Dict[str, Any]]:
        """Get specific client from cache"""
        with self._lock:
            if username in self._cache['clients']:
                client = self._cache['clients'][username].copy()
                # Update status based on current time
                current_time = time.time()
                time_diff = current_time - client['last_heartbeat']
                if time_diff < 60:
                    client['status'] = 'online'
                elif time_diff < 300:
                    client['status'] = 'idle'
                else:
                    client['status'] = 'offline'
                client['time_diff'] = time_diff
                return client
            return None
    
    def get_active_clients(self, timeout: int = 60) -> List[str]:
        """Get list of active client usernames"""
        with self._lock:
            current_time = time.time()
            active_clients = []
            
            for username, client in self._cache['clients'].items():
                time_diff = current_time - client['last_heartbeat']
                if time_diff < timeout:
                    active_clients.append(username)
            
            return active_clients
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information and statistics"""
        with self._lock:
            return {
                'client_count': len(self._cache['clients']),
                'stats': self._cache['stats'].copy(),
                'last_updated': self._cache['last_updated'],
                'cache_age_seconds': time.time() - self._cache['last_updated']
            }

# Global client cache manager instance
_client_cache_manager = None

def get_client_cache_manager() -> ClientCacheManager:
    """Get or create the global client cache manager"""
    global _client_cache_manager
    
    if _client_cache_manager is None:
        _client_cache_manager = ClientCacheManager()
        
    return _client_cache_manager

def initialize_client_cache():
    """Initialize the client cache system"""
    cache_manager = get_client_cache_manager()
    return cache_manager
