#!/usr/bin/env python3
"""
Global Cache Manager for Server
===============================
Provides a comprehensive caching system accessible to all plugins and server components.
Handles multiple cache layers:
1. Startup cache - initialized when server starts
2. User profile cache - from user profile pages  
3. Global broadcast cache - published to all clients
4. Plugin-specific cache - isolated namespaces for plugins
"""

import time
import json
import threading
import logging
from typing import Dict, Any, Optional, List, Union
from cache import Cache
from client_cache_manager import get_client_cache_manager
from plugin_cache_manager import get_plugin_cache_manager

class GlobalCacheManager:
    """
    Comprehensive global cache manager for server-side operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Multiple cache layers
        self._caches = {
            'startup': Cache(),           # Data initialized at startup
            'user_profiles': Cache(),     # Data from user profile pages
            'global_broadcast': Cache(),  # Data to broadcast to all clients
            'plugins': {},               # Plugin-specific caches {plugin_name: Cache()}
            'temporary': Cache(),         # Short-lived temporary data
            'persistent': Cache()         # Long-lived persistent data
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'broadcasts': 0
        }
        
        # Initialize with default data
        self._initialize_startup_cache()
        
        self.logger.info("Global Cache Manager initialized")
    
    def _initialize_startup_cache(self):
        """Initialize cache with startup data"""
        try:
            with self._lock:
                # Server startup time
                self._caches['startup'].set('server_start_time', time.time())
                
                # Server configuration
                self._caches['startup'].set('server_config', {
                    'version': '1.0.0',
                    'cache_enabled': True,
                    'broadcast_enabled': True
                })
                
                # Default global settings
                self._caches['global_broadcast'].set('global_settings', {
                    'maintenance_mode': False,
                    'max_concurrent_tasks': 10,
                    'default_timeout': 300
                })
                
            self.logger.info("Startup cache initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing startup cache: {e}")
    
    # === Core Cache Operations ===
    
    def set(self, key: str, value: Any, cache_type: str = 'temporary', ttl: Optional[int] = None, plugin_name: Optional[str] = None):
        """
        Set a value in the specified cache layer
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Cache layer ('startup', 'user_profiles', 'global_broadcast', 'plugins', 'temporary', 'persistent')
            ttl: Time to live in seconds
            plugin_name: Required if cache_type is 'plugins'
        """
        try:
            with self._lock:
                if cache_type == 'plugins':
                    if not plugin_name:
                        raise ValueError("plugin_name is required for plugin cache")
                    
                    if plugin_name not in self._caches['plugins']:
                        self._caches['plugins'][plugin_name] = Cache()
                    
                    self._caches['plugins'][plugin_name].set(key, value, ttl)
                else:
                    if cache_type not in self._caches:
                        raise ValueError(f"Invalid cache type: {cache_type}")
                    
                    self._caches[cache_type].set(key, value, ttl)
                
                self._stats['sets'] += 1
                
                # Auto-broadcast if it's global_broadcast cache
                if cache_type == 'global_broadcast':
                    self._broadcast_to_clients(key, value)
                
            self.logger.debug(f"Set cache: {cache_type}:{plugin_name or ''}:{key}")
            
        except Exception as e:
            self.logger.error(f"Error setting cache {key}: {e}")
            raise
    
    def get(self, key: str, cache_type: str = 'temporary', plugin_name: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a value from the specified cache layer
        
        Args:
            key: Cache key
            cache_type: Cache layer to search
            plugin_name: Required if cache_type is 'plugins'
            default: Default value if key not found
        """
        try:
            with self._lock:
                if cache_type == 'plugins':
                    if not plugin_name:
                        raise ValueError("plugin_name is required for plugin cache")
                    
                    if plugin_name not in self._caches['plugins']:
                        self._stats['misses'] += 1
                        return default
                    
                    value = self._caches['plugins'][plugin_name].get(key)
                else:
                    if cache_type not in self._caches:
                        raise ValueError(f"Invalid cache type: {cache_type}")
                    
                    value = self._caches[cache_type].get(key)
                
                if value is not None:
                    self._stats['hits'] += 1
                else:
                    self._stats['misses'] += 1
                    value = default
                
                return value
                
        except Exception as e:
            self.logger.error(f"Error getting cache {key}: {e}")
            self._stats['misses'] += 1
            return default
    
    def delete(self, key: str, cache_type: str = 'temporary', plugin_name: Optional[str] = None):
        """Delete a key from the specified cache layer"""
        try:
            with self._lock:
                if cache_type == 'plugins':
                    if not plugin_name:
                        raise ValueError("plugin_name is required for plugin cache")
                    
                    if plugin_name in self._caches['plugins']:
                        self._caches['plugins'][plugin_name].delete(key)
                else:
                    if cache_type not in self._caches:
                        raise ValueError(f"Invalid cache type: {cache_type}")
                    
                    self._caches[cache_type].delete(key)
                
                self._stats['deletes'] += 1
                
        except Exception as e:
            self.logger.error(f"Error deleting cache {key}: {e}")
    
    def clear(self, cache_type: str = 'temporary', plugin_name: Optional[str] = None):
        """Clear a cache layer"""
        try:
            with self._lock:
                if cache_type == 'plugins':
                    if plugin_name:
                        if plugin_name in self._caches['plugins']:
                            self._caches['plugins'][plugin_name].clear()
                    else:
                        # Clear all plugin caches
                        for plugin_cache in self._caches['plugins'].values():
                            plugin_cache.clear()
                else:
                    if cache_type not in self._caches:
                        raise ValueError(f"Invalid cache type: {cache_type}")
                    
                    self._caches[cache_type].clear()
                
        except Exception as e:
            self.logger.error(f"Error clearing cache {cache_type}: {e}")
    
    # === Plugin-Specific Methods ===
    
    def plugin_set(self, plugin_name: str, key: str, value: Any, ttl: Optional[int] = None):
        """Convenience method for plugin cache operations"""
        return self.set(key, value, 'plugins', ttl, plugin_name)
    
    def plugin_get(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """Convenience method for plugin cache operations"""
        return self.get(key, 'plugins', plugin_name, default)
    
    def plugin_delete(self, plugin_name: str, key: str):
        """Convenience method for plugin cache operations"""
        return self.delete(key, 'plugins', plugin_name)
    
    def plugin_clear(self, plugin_name: str):
        """Convenience method for plugin cache operations"""
        return self.clear('plugins', plugin_name)
    
    def plugin_get_all(self, plugin_name: str) -> Dict[str, Any]:
        """Get all cache entries for a plugin"""
        try:
            with self._lock:
                if plugin_name not in self._caches['plugins']:
                    return {}
                return self._caches['plugins'][plugin_name].all()
        except Exception as e:
            self.logger.error(f"Error getting all plugin cache for {plugin_name}: {e}")
            return {}
    
    # === User Profile Cache Methods ===
    
    def set_user_profile_data(self, username: str, data: Dict[str, Any], ttl: Optional[int] = 3600, requesting_user: Optional[str] = None):
        """
        Set user profile data (from user profile pages)
        
        Args:
            username: Target username
            data: Profile data to store
            ttl: Time to live in seconds
            requesting_user: Username of the user making the request (for access control)
        """
        # Verify access rights - only the user themselves or admin can set their profile data
        if requesting_user and requesting_user != username and not self._is_admin_user(requesting_user):
            raise PermissionError(f"User '{requesting_user}' cannot modify profile data for '{username}'")
        
        key = f"user_profile:{username}"
        return self.set(key, data, 'user_profiles', ttl)
    
    def get_user_profile_data(self, username: str, requesting_user: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get user profile data
        
        Args:
            username: Target username
            requesting_user: Username of the user making the request (for access control)
        """
        # Verify access rights - only the user themselves or admin can access their profile data
        if requesting_user and requesting_user != username and not self._is_admin_user(requesting_user):
            self.logger.warning(f"Access denied: User '{requesting_user}' tried to access profile data for '{username}'")
            raise PermissionError(f"User '{requesting_user}' cannot access profile data for '{username}'")
        
        key = f"user_profile:{username}"
        return self.get(key, 'user_profiles')
    
    def set_user_setting(self, username: str, setting_name: str, value: Any, ttl: Optional[int] = 3600, requesting_user: Optional[str] = None):
        """
        Set a specific user setting
        
        Args:
            username: Target username
            setting_name: Setting name
            value: Setting value
            ttl: Time to live in seconds
            requesting_user: Username of the user making the request (for access control)
        """
        # Verify access rights
        if requesting_user and requesting_user != username and not self._is_admin_user(requesting_user):
            raise PermissionError(f"User '{requesting_user}' cannot modify settings for '{username}'")
        
        key = f"user_setting:{username}:{setting_name}"
        return self.set(key, value, 'user_profiles', ttl)
    
    def get_user_setting(self, username: str, setting_name: str, default: Any = None, requesting_user: Optional[str] = None) -> Any:
        """
        Get a specific user setting
        
        Args:
            username: Target username
            setting_name: Setting name
            default: Default value if not found
            requesting_user: Username of the user making the request (for access control)
        """
        # Verify access rights
        if requesting_user and requesting_user != username and not self._is_admin_user(requesting_user):
            self.logger.warning(f"Access denied: User '{requesting_user}' tried to access setting '{setting_name}' for '{username}'")
            raise PermissionError(f"User '{requesting_user}' cannot access setting '{setting_name}' for '{username}'")
        
        key = f"user_setting:{username}:{setting_name}"
        return self.get(key, 'user_profiles', None, default)
    
    def _is_admin_user(self, username: str) -> bool:
        """
        Check if a user has admin privileges
        
        Args:
            username: Username to check
            
        Returns:
            True if user is admin, False otherwise
        """
        # Get admin users from startup cache or configuration
        admin_users = self.get('admin_users', 'startup', None, ['admin', 'administrator'])
        return username.lower() in [admin.lower() for admin in admin_users]
    
    def get_user_identity_from_client_id(self, client_id: str) -> Optional[str]:
        """
        Get username from client ID using client cache manager
        
        Args:
            client_id: Client identifier
            
        Returns:
            Username if found, None otherwise
        """
        try:
            from client_cache_manager import get_client_cache_manager
            client_cache = get_client_cache_manager()
            
            # Get client info from cache
            client_info = client_cache.get_client_by_id(client_id)
            if client_info and 'username' in client_info:
                return client_info['username']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user identity for client {client_id}: {e}")
            return None
    
    # === Global Broadcast Methods ===
    
    def broadcast_to_clients(self, key: str, value: Any, ttl: Optional[int] = None):
        """Broadcast data to all clients"""
        self.set(key, value, 'global_broadcast', ttl)
    
    def _broadcast_to_clients(self, key: str, value: Any):
        """Internal method to handle broadcasting"""
        try:
            # This will be implemented to send to all connected clients
            self._stats['broadcasts'] += 1
            self.logger.info(f"Broadcasting {key} to all clients")
            
            # TODO: Implement actual client notification mechanism
            # Could use WebSocket, SSE, or polling endpoint
            
        except Exception as e:
            self.logger.error(f"Error broadcasting {key}: {e}")
    
    def get_broadcast_data(self) -> Dict[str, Any]:
        """Get all data that should be broadcast to clients"""
        return self._caches['global_broadcast'].all()
    
    # === Statistics and Management ===
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'sets': self._stats['sets'],
                'deletes': self._stats['deletes'],
                'broadcasts': self._stats['broadcasts'],
                'cache_sizes': {
                    cache_type: cache.size() if hasattr(cache, 'size') else len(cache.all())
                    for cache_type, cache in self._caches.items()
                    if cache_type != 'plugins'
                },
                'plugin_cache_sizes': {
                    plugin_name: cache.size() if hasattr(cache, 'size') else len(cache.all())
                    for plugin_name, cache in self._caches['plugins'].items()
                }
            }
    
    def get_all_data(self, include_plugins: bool = False) -> Dict[str, Any]:
        """Get all cache data for debugging/admin purposes"""
        result = {}
        
        with self._lock:
            for cache_type, cache in self._caches.items():
                if cache_type == 'plugins':
                    if include_plugins:
                        result[cache_type] = {
                            plugin_name: plugin_cache.all()
                            for plugin_name, plugin_cache in cache.items()
                        }
                else:
                    result[cache_type] = cache.all()
        
        return result
    
    # === Integration with Existing Cache Managers ===
    
    def sync_with_client_cache(self):
        """Sync relevant data with client cache manager"""
        try:
            client_cache = get_client_cache_manager()
            
            # Get online clients for broadcasting
            active_clients = client_cache.get_active_clients()
            self.set('active_clients', active_clients, 'startup', 60)  # Cache for 1 minute
            
        except Exception as e:
            self.logger.error(f"Error syncing with client cache: {e}")
    
    def sync_with_plugin_cache(self):
        """Sync relevant data with plugin cache manager"""
        try:
            plugin_cache = get_plugin_cache_manager()
            
            # Get plugin metadata for broadcasting
            plugins_data = plugin_cache.get_formatted_plugins_for_ui()
            self.set('available_plugins', plugins_data, 'global_broadcast', 300)  # Cache for 5 minutes
            
        except Exception as e:
            self.logger.error(f"Error syncing with plugin cache: {e}")


# Global instance
_global_cache_manager = None


def get_global_cache_manager() -> GlobalCacheManager:
    """Get the global cache manager instance"""
    global _global_cache_manager
    
    if _global_cache_manager is None:
        _global_cache_manager = GlobalCacheManager()
    
    return _global_cache_manager


def initialize_global_cache():
    """Initialize the global cache manager"""
    cache_manager = get_global_cache_manager()
    
    # Sync with existing cache managers
    cache_manager.sync_with_client_cache()
    cache_manager.sync_with_plugin_cache()
    
    return cache_manager


# Plugin helper functions for easy access
def plugin_cache_set(plugin_name: str, key: str, value: Any, ttl: Optional[int] = None):
    """Global function for plugins to set cache data"""
    return get_global_cache_manager().plugin_set(plugin_name, key, value, ttl)


def plugin_cache_get(plugin_name: str, key: str, default: Any = None) -> Any:
    """Global function for plugins to get cache data"""
    return get_global_cache_manager().plugin_get(plugin_name, key, default)


def plugin_cache_delete(plugin_name: str, key: str):
    """Global function for plugins to delete cache data"""
    return get_global_cache_manager().plugin_delete(plugin_name, key)


def plugin_cache_clear(plugin_name: str):
    """Global function for plugins to clear their cache"""
    return get_global_cache_manager().plugin_clear(plugin_name)


def broadcast_to_clients(key: str, value: Any, ttl: Optional[int] = None):
    """Global function to broadcast data to all clients"""
    return get_global_cache_manager().broadcast_to_clients(key, value, ttl)
