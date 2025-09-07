#!/usr/bin/env python3
"""
Global Cache Manager for Client
===============================
Provides a comprehensive caching system accessible to all plugins and client components.
Handles multiple cache layers:
1. Startup cache - initialized when client starts
2. Server data cache - data received from server
3. Plugin-specific cache - isolated namespaces for plugins
4. User preferences cache - local user settings
"""

import time
import json
import threading
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from cache import Cache

class ClientGlobalCacheManager:
    """
    Comprehensive global cache manager for client-side operations
    """
    
    def __init__(self, server_url: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.server_url = server_url or "http://localhost:5000"
        
        # User identity
        self._user_name = None
        self._user_identity = None
        
        # Multiple cache layers
        self._caches = {
            'startup': Cache(),           # Data initialized at startup
            'server_data': Cache(),       # Data received from server
            'plugins': {},               # Plugin-specific caches {plugin_name: Cache()}
            'user_preferences': Cache(),  # Local user preferences
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
            'server_syncs': 0,
            'sync_errors': 0
        }
        
        # Server sync settings
        self._auto_sync_enabled = True
        self._last_server_sync = 0
        self._sync_interval = 60  # seconds
        
        # Initialize with default data
        self._initialize_startup_cache()
        
        self.logger.info("Client Global Cache Manager initialized")
    
    def _initialize_startup_cache(self):
        """Initialize cache with startup data"""
        try:
            # Client startup time
            self._caches['startup'].set('client_start_time', time.time())
            
            # Client configuration
            self._caches['startup'].set('client_config', {
                'version': '1.0.0',
                'cache_enabled': True,
                'server_sync_enabled': True,
                'server_url': self.server_url
            })
            
            # Default user preferences
            self._caches['user_preferences'].set('ui_theme', 'light')
            self._caches['user_preferences'].set('auto_refresh', True)
            self._caches['user_preferences'].set('notification_enabled', True)
            
            self.logger.info("Client startup cache initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing client startup cache: {e}")
    
    # === Core Cache Operations ===
    
    def set(self, key: str, value: Any, cache_type: str = 'temporary', ttl: Optional[int] = None, plugin_name: Optional[str] = None):
        """
        Set a value in the specified cache layer
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Cache layer ('startup', 'server_data', 'plugins', 'user_preferences', 'temporary', 'persistent')
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
    
    # === User Identity Methods ===
    
    def set_user_identity(self, user_name: str, user_identity: Optional[str] = None):
        """
        Set the user identity for this client
        
        Args:
            username: Username of the current user
            client_id: Optional client identifier
        """
        with self._lock:
            self._user_name = user_name
            self._user_identity = user_identity
            
            # Store in startup cache for persistence
            self.set('current_user_name', user_name, 'startup')
            if user_identity:
                self.set('current_user_identity', user_identity, 'startup')

            self.logger.info(f"User identity set: user_name: {user_name}, user_identity: {user_identity}")
    
    def get_current_user_name(self) -> Optional[str]:
        """Get the current user's username"""
        if self._user_name:
            return self._user_name
        
        # Try to get from startup cache
        return self.get('current_user_name', 'startup')

    def get_current_user_identity(self) -> Optional[str]:
        """Get the current user identity"""
        if self._user_identity:
            return self._user_identity
        
        # Try to get from startup cache
        return self.get('current_user_identity', 'startup')

    def clear_user_identity(self):
        """Clear the user identity"""
        with self._lock:
            self._user_name = None
            self._user_identity = None
            self.delete('current_user_name', 'startup')
            self.delete('current_user_identity', 'startup')

            self.logger.info("User identity cleared")
    
    # === User Preferences Methods ===
    
    def set_user_preference(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set user preference"""
        return self.set(key, value, 'user_preferences', ttl)
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.get(key, 'user_preferences', None, default)
    
    def get_all_user_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        return self._caches['user_preferences'].all()
    
    # === User Parameters Methods ===
    
    def get_user_parameter(self, category: str, param_name: str, default: Any = None) -> Any:
        """
        Get a user parameter value for the current user
        
        Args:
            category: Parameter category (e.g., 'api_credentials', 'notifications')
            param_name: Parameter name
            default: Default value if parameter not found
            
        Returns:
            Parameter value or default
        """
        user_name = self.get_current_user_name()
        if not user_name:
            self.logger.warning("No current user set, cannot get user parameter")
            return default
        
        # Try to get from category-specific cache first (faster)
        category_params = self.get(f"user_params_{user_name}_{category}", 'server_data', None, {})
        if category_params and param_name in category_params:
            param_data = category_params[param_name]
            return param_data.get('value', default) if isinstance(param_data, dict) else param_data
        
        # Fall back to full parameters cache
        all_params = self.get(f"user_params_{user_name}", 'server_data', None, {})
        if category in all_params and param_name in all_params[category]:
            param_data = all_params[category][param_name]
            return param_data.get('value', default) if isinstance(param_data, dict) else param_data
        
        return default
    
    def get_user_parameters_category(self, category: str) -> Dict[str, Any]:
        """
        Get all parameters for a specific category for the current user
        
        Args:
            category: Parameter category
            
        Returns:
            Dictionary of parameter_name -> parameter_data
        """
        user_name = self.get_current_user_name()
        if not user_name:
            self.logger.warning("No current user set, cannot get user parameters")
            return {}
        
        # Try category-specific cache first
        category_params = self.get(f"user_params_{user_name}_{category}", 'server_data', None, {})
        if category_params:
            return category_params
        
        # Fall back to full parameters cache
        all_params = self.get(f"user_params_{user_name}", 'server_data', None, {})
        return all_params.get(category, {})
    
    def get_all_user_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all user parameters for the current user
        
        Returns:
            Dictionary of category -> {parameter_name -> parameter_data}
        """
        user_name = self.get_current_user_name()
        if not user_name:
            self.logger.warning("No current user set, cannot get user parameters")
            return {}
        
        return self.get(f"user_params_{user_name}", 'server_data', None, {})
    
    def force_sync_user_parameters(self) -> bool:
        """Force sync user parameters from server"""
        user_name = self.get_current_user_name()
        if not user_name:
            self.logger.warning("No current user set, cannot sync user parameters")
            return False
        
        return self._sync_user_parameters(user_name)
    
    # === Simplified User Parameter Access (Auto-detects current user) ===
    
    def get_param(self, category: str, param_name: str, default: Any = None) -> Any:
        """
        Simplified method to get user parameter (auto-detects current user)
        
        Args:
            category: Parameter category
            param_name: Parameter name  
            default: Default value
            
        Returns:
            Parameter value or default
        """
        return self.get_user_parameter(category, param_name, default)
    
    def get_params(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user parameters by category or all parameters (auto-detects current user)
        
        Args:
            category: Specific category, or None for all categories
            
        Returns:
            Parameters dictionary organized by category
        """
        if category:
            return self.get_user_parameters_category(category)
        else:
            return self.get_all_user_parameters()
    
    def list_param_categories(self) -> List[str]:
        """
        Get list of available parameter categories for current user
        
        Returns:
            List of category names
        """
        all_params = self.get_all_user_parameters()
        return list(all_params.keys())
    
    def get_api_credentials(self) -> Dict[str, Any]:
        """Get all API credentials for current user"""
        return self.get_params('api_credentials')
    
    def get_notifications_config(self) -> Dict[str, Any]:
        """Get notification configuration for current user"""
        return self.get_params('notifications')
    
    def get_integrations_config(self) -> Dict[str, Any]:
        """Get integrations configuration for current user"""
        return self.get_params('integrations')
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences for current user"""
        return self.get_params('preferences')
    
    def get_custom_params(self) -> Dict[str, Any]:
        """Get custom parameters for current user"""
        return self.get_params('custom')
    
    def get_params_summary(self) -> Dict[str, Any]:
        """
        Get a summary of user parameters organized by category
        
        Returns:
            Organized summary with counts and available parameters
        """
        user_name = self.get_current_user_name()
        if not user_name:
            return {"error": "No current user set"}
        
        all_params = self.get_all_user_parameters()
        
        summary = {
            "user": user_name,
            "total_categories": len(all_params),
            "categories": {},
            "last_sync": self._last_server_sync
        }
        
        for category, params in all_params.items():
            param_list = []
            sensitive_count = 0
            
            for param_name, param_data in params.items():
                if isinstance(param_data, dict):
                    param_info = {
                        "name": param_name,
                        "type": param_data.get("type", "string"),
                        "description": param_data.get("description", ""),
                        "has_value": param_data.get("value") is not None
                    }
                    if param_data.get("type") == "string" and len(str(param_data.get("value", ""))) > 20:
                        sensitive_count += 1
                else:
                    param_info = {
                        "name": param_name,
                        "type": "unknown",
                        "description": "",
                        "has_value": param_data is not None
                    }
                
                param_list.append(param_info)
            
            summary["categories"][category] = {
                "param_count": len(params),
                "sensitive_params": sensitive_count,
                "parameters": param_list
            }
        
        return summary
    
    # === Server Data Sync Methods ===
    
    def sync_from_server(self, force: bool = False) -> bool:
        """
        Sync data from server
        
        Args:
            force: Force sync even if within sync interval
        """
        try:
            current_time = time.time()
            
            # Check if sync is needed
            if not force and (current_time - self._last_server_sync) < self._sync_interval:
                self.logger.debug("Skipping server sync - within interval")
                return True
            
            if not self._auto_sync_enabled and not force:
                self.logger.debug("Skipping server sync - auto sync disabled")
                return True
            
            # Sync global broadcast data
            success = self._sync_global_broadcast_data()
            
            if success:
                # Sync user profile data if we have a username
                user_name = self.get_current_user_name()
                if user_name:
                    self._sync_user_profile_data(user_name)
                    # Sync user parameters as well
                    self._sync_user_parameters(user_name)
                
                # Sync available plugins
                self._sync_available_plugins()
                
                self._last_server_sync = current_time
                self._stats['server_syncs'] += 1
                self.logger.info("Successfully synced data from server")
            else:
                self._stats['sync_errors'] += 1
                self.logger.warning("Failed to sync data from server")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error syncing from server: {e}")
            self._stats['sync_errors'] += 1
            return False
    
    def _sync_global_broadcast_data(self) -> bool:
        """Sync global broadcast data from server"""
        try:
            response = requests.get(f"{self.server_url}/api/cache/broadcast", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Store broadcast data
                for key, value in data.items():
                    self.set(key, value, 'server_data', 300)  # 5 minute TTL
                
                self.logger.debug(f"Synced {len(data)} broadcast items from server")
                return True
            else:
                self.logger.warning(f"Server returned {response.status_code} for broadcast data")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Network error syncing broadcast data: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing broadcast data: {e}")
            return False
    
    def _sync_user_profile_data(self, username: str) -> bool:
        """Sync user profile data from server"""
        try:
            # Prepare headers with user identity
            headers = {}
            user_identity = self.get_current_user_identity()
            current_user = self.get_current_user_name()

            if user_identity:
                headers['X-User-Identity'] = user_identity
            if current_user:
                headers['X-Username'] = current_user
            
            response = requests.get(
                f"{self.server_url}/api/cache/user/{username}/profile", 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Store user profile data (only if it's for the current user)
                if username == current_user:
                    self.set(f"profile:{username}", profile_data, 'server_data', 3600)  # 1 hour TTL
                    self.logger.debug(f"Synced profile data for user {username}")
                    return True
                else:
                    self.logger.warning(f"Received profile data for {username} but current user is {current_user}")
                    return False
            elif response.status_code == 403:
                self.logger.warning(f"Access denied when syncing profile for {username}")
                return False
            else:
                self.logger.warning(f"Server returned {response.status_code} for user profile")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Network error syncing user profile: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing user profile: {e}")
            return False
    
    def _sync_available_plugins(self) -> bool:
        """Sync available plugins from server"""
        try:
            response = requests.get(f"{self.server_url}/api/plugins", timeout=10)
            
            if response.status_code == 200:
                plugins_data = response.json()
                
                # Store plugins data
                self.set('available_plugins', plugins_data, 'server_data', 300)  # 5 minute TTL
                
                self.logger.debug("Synced available plugins from server")
                return True
            else:
                self.logger.warning(f"Server returned {response.status_code} for plugins")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Network error syncing plugins: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing plugins: {e}")
            return False

    def _sync_user_parameters(self, username: str) -> bool:
        """Sync user parameters from server"""
        try:
            # Prepare headers with user identity
            headers = {}
            user_identity = self.get_current_user_identity()
            current_user = self.get_current_user_name()

            if user_identity:
                headers['X-User-Identity'] = user_identity
            if current_user:
                headers['X-Username'] = current_user
            
            response = requests.get(
                f"{self.server_url}/api/cache/user/{username}/parameters", 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                parameters_data = response.json()
                
                # Store user parameters data (only if it's for the current user)
                if username == current_user:
                    # Store in server_data cache with structured keys for plugin access
                    self.set(f"user_params_{username}", parameters_data, 'server_data', 3600)  # 1 hour TTL
                    
                    # Also store individual categories for faster plugin access
                    for category, params in parameters_data.items():
                        self.set(f"user_params_{username}_{category}", params, 'server_data', 3600)
                    
                    self.logger.debug(f"Synced user parameters for user {username}")
                    return True
                else:
                    self.logger.warning(f"Received parameters for {username} but current user is {current_user}")
                    return False
            elif response.status_code == 403:
                self.logger.warning(f"Access denied when syncing parameters for {username}")
                return False
            elif response.status_code == 404:
                self.logger.debug(f"No parameters found for user {username}")
                # Store empty parameters to indicate we checked
                self.set(f"user_params_{username}", {}, 'server_data', 3600)
                return True
            else:
                self.logger.warning(f"Server returned {response.status_code} for user parameters")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Network error syncing user parameters: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing user parameters: {e}")
            return False
    
    # === Auto Sync Control ===
    
    def enable_auto_sync(self, interval: int = 60):
        """Enable automatic syncing with server"""
        self._auto_sync_enabled = True
        self._sync_interval = interval
        self.logger.info(f"Auto sync enabled with {interval}s interval")
    
    def disable_auto_sync(self):
        """Disable automatic syncing with server"""
        self._auto_sync_enabled = False
        self.logger.info("Auto sync disabled")
    
    def set_sync_interval(self, interval: int):
        """Set sync interval in seconds"""
        self._sync_interval = interval
        self.logger.info(f"Sync interval set to {interval}s")
    
    # === Helper Methods ===
    
    def get_server_data(self, key: str, default: Any = None) -> Any:
        """Get data that was synced from server"""
        return self.get(key, 'server_data', None, default)
    
    def is_online(self) -> bool:
        """Check if client can reach server"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
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
                'server_syncs': self._stats['server_syncs'],
                'sync_errors': self._stats['sync_errors'],
                'last_server_sync': self._last_server_sync,
                'auto_sync_enabled': self._auto_sync_enabled,
                'sync_interval': self._sync_interval,
                'server_online': self.is_online(),
                'cache_sizes': {
                    cache_type: len(cache.all())
                    for cache_type, cache in self._caches.items()
                    if cache_type != 'plugins'
                },
                'plugin_cache_sizes': {
                    plugin_name: len(cache.all())
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
    
    def all(self) -> Dict[str, Any]:
        """
        Retrieve all cache data from all layers.

        Returns:
            A dictionary containing all cache data categorized by cache type.
        """
        try:
            with self._lock:
                all_cache = {}
                for cache_type, cache in self._caches.items():
                    if cache_type == 'plugins':
                        # Aggregate plugin-specific caches
                        all_cache['plugins'] = {
                            plugin_name: plugin_cache.all()
                            for plugin_name, plugin_cache in cache.items()
                        }
                    else:
                        all_cache[cache_type] = cache.all()
                return all_cache
        except Exception as e:
            self.logger.error(f"Error retrieving all cache data: {e}")
            return {}


# Global instance
_client_global_cache_manager = None


def get_client_global_cache_manager() -> ClientGlobalCacheManager:
    """Get the client global cache manager instance"""
    global _client_global_cache_manager
    
    if _client_global_cache_manager is None:
        _client_global_cache_manager = ClientGlobalCacheManager()
    
    return _client_global_cache_manager


def initialize_client_global_cache(server_url: Optional[str] = None, user_name: Optional[str] = None,user_identity: Optional[str] = None) -> ClientGlobalCacheManager:
    """Initialize the client global cache manager"""
    global _client_global_cache_manager
    

    if _client_global_cache_manager is None:
        _client_global_cache_manager = ClientGlobalCacheManager(server_url)
    
    # Set user identity if provided
    if user_name:
        _client_global_cache_manager.set_user_identity(user_name,user_identity)
    
    # Perform initial sync
    _client_global_cache_manager.sync_from_server(force=True)
    
    return _client_global_cache_manager


# Plugin helper functions for easy access
def client_plugin_cache_set(plugin_name: str, key: str, value: Any, ttl: Optional[int] = None):
    """Global function for plugins to set cache data"""
    return get_client_global_cache_manager().plugin_set(plugin_name, key, value, ttl)


def client_plugin_cache_get(plugin_name: str, key: str, default: Any = None) -> Any:
    """Global function for plugins to get cache data"""
    return get_client_global_cache_manager().plugin_get(plugin_name, key, default)


def client_plugin_cache_delete(plugin_name: str, key: str):
    """Global function for plugins to delete cache data"""
    return get_client_global_cache_manager().plugin_delete(plugin_name, key)


def client_plugin_cache_clear(plugin_name: str):
    """Global function for plugins to clear their cache"""
    return get_client_global_cache_manager().plugin_clear(plugin_name)


def get_server_data(key: str, default: Any = None) -> Any:
    """Global function to get data synced from server"""
    return get_client_global_cache_manager().get_server_data(key, default)


def sync_from_server(force: bool = False) -> bool:
    """Global function to sync data from server"""
    return get_client_global_cache_manager().sync_from_server(force)


# User parameters helper functions for plugins
def get_user_parameter(category: str, param_name: str, default: Any = None) -> Any:
    """
    Global function for plugins to get user parameters
    
    Args:
        category: Parameter category (e.g., 'api_credentials', 'notifications')
        param_name: Parameter name  
        default: Default value if parameter not found
        
    Returns:
        Parameter value or default
        
    Example:
        api_key = get_user_parameter('api_credentials', 'servicenow_api_key', 'default_key')
    """
    return get_client_global_cache_manager().get_user_parameter(category, param_name, default)


def get_user_parameters_category(category: str) -> Dict[str, Any]:
    """
    Global function for plugins to get all parameters in a category
    
    Args:
        category: Parameter category
        
    Returns:
        Dictionary of parameter_name -> parameter_data
        
    Example:
        credentials = get_user_parameters_category('api_credentials')
        api_key = credentials.get('servicenow_api_key', {}).get('value')
    """
    return get_client_global_cache_manager().get_user_parameters_category(category)


def get_all_user_parameters() -> Dict[str, Dict[str, Any]]:
    """
    Global function for plugins to get all user parameters
    
    Returns:
        Dictionary of category -> {parameter_name -> parameter_data}
    """
    return get_client_global_cache_manager().get_all_user_parameters()


def force_sync_user_parameters() -> bool:
    """
    Global function to force sync user parameters from server
    
    Returns:
        True if sync successful, False otherwise
    """
    return get_client_global_cache_manager().force_sync_user_parameters()


# Simplified user parameter access (no username required)
def get_param(category: str, param_name: str, default: Any = None) -> Any:
    """
    Simplified global function to get user parameter (auto-detects current user)
    
    Args:
        category: Parameter category
        param_name: Parameter name
        default: Default value
        
    Returns:
        Parameter value or default
        
    Example:
        api_key = get_param('api_credentials', 'servicenow_api_key')
        email = get_param('notifications', 'email_address', 'no-email@example.com')
    """
    return get_client_global_cache_manager().get_param(category, param_name, default)


def get_params(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get user parameters by category or all parameters (auto-detects current user)
    
    Args:
        category: Specific category, or None for all categories
        
    Returns:
        Parameters dictionary organized by category
        
    Examples:
        # Get all API credentials
        credentials = get_params('api_credentials')
        
        # Get all user parameters
        all_params = get_params()
    """
    return get_client_global_cache_manager().get_params(category)


def list_param_categories() -> List[str]:
    """
    Get list of available parameter categories for current user
    
    Returns:
        List of category names
        
    Example:
        categories = list_param_categories()
        # Returns: ['api_credentials', 'notifications', 'integrations', 'preferences']
    """
    return get_client_global_cache_manager().list_param_categories()


def get_api_credentials() -> Dict[str, Any]:
    """
    Get all API credentials for current user
    
    Returns:
        Dictionary of API credentials
        
    Example:
        creds = get_api_credentials()
        servicenow_key = creds.get('servicenow_api_key', {}).get('value')
    """
    return get_client_global_cache_manager().get_api_credentials()


def get_notifications_config() -> Dict[str, Any]:
    """
    Get notification configuration for current user
    
    Returns:
        Dictionary of notification settings
        
    Example:
        notifications = get_notifications_config()
        email = notifications.get('email_address', {}).get('value')
    """
    return get_client_global_cache_manager().get_notifications_config()


def get_integrations_config() -> Dict[str, Any]:
    """
    Get integrations configuration for current user
    
    Returns:
        Dictionary of integration settings
        
    Example:
        integrations = get_integrations_config()
        servicenow_url = integrations.get('servicenow_instance', {}).get('value')
    """
    return get_client_global_cache_manager().get_integrations_config()


def get_user_preferences() -> Dict[str, Any]:
    """
    Get user preferences for current user
    
    Returns:
        Dictionary of user preferences
    """
    return get_client_global_cache_manager().get_user_preferences()


def get_params_summary() -> Dict[str, Any]:
    """
    Get a summary of user parameters organized by category
    
    Returns:
        Organized summary with counts and available parameters
        
    Example:
        summary = get_params_summary()
        print(f"User: {summary['user']}")
        print(f"Categories: {list(summary['categories'].keys())}")
    """
    return get_client_global_cache_manager().get_params_summary()
