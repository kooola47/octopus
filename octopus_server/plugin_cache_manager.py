#!/usr/bin/env python3
"""
Plugin Cache Manager
===================
Manages cached plugin metadata with background refresh capabilities
"""

import os
import time
import threading
import logging
from typing import Dict, Any, Optional
from plugin_discovery import PluginDiscovery

class PluginCacheManager:
    """Manages plugin metadata cache with background refresh"""
    
    def __init__(self, plugins_folder: str, cache_duration: int = 300):  # 5 minutes default
        self.plugins_folder = plugins_folder
        self.cache_duration = cache_duration
        self.discovery = PluginDiscovery(plugins_folder)
        self.logger = logging.getLogger(__name__)
        
        # Cache storage
        self._cache = {
            'plugins': {},
            'last_updated': 0,
            'is_loading': False
        }
        
        # Thread lock for cache updates
        self._lock = threading.Lock()
        
        # Background refresh thread
        self._refresh_thread = None
        self._stop_refresh = threading.Event()
        
    def start_background_refresh(self, interval: int = 300):  # 5 minutes default
        """Start background cache refresh"""
        if self._refresh_thread and self._refresh_thread.is_alive():
            self.logger.warning("Background refresh already running")
            return
            
        self._stop_refresh.clear()
        self._refresh_thread = threading.Thread(
            target=self._background_refresh_worker,
            args=(interval,),
            daemon=True
        )
        self._refresh_thread.start()
        self.logger.info(f"Started background plugin cache refresh with {interval}s interval")
        
    def stop_background_refresh(self):
        """Stop background cache refresh"""
        if self._refresh_thread:
            self._stop_refresh.set()
            if self._refresh_thread.is_alive():
                self._refresh_thread.join(timeout=5)
            self.logger.info("Stopped background plugin cache refresh")
    
    def _background_refresh_worker(self, interval: int):
        """Background worker that refreshes cache periodically"""
        while not self._stop_refresh.wait(interval):
            try:
                self.refresh_cache()
            except Exception as e:
                self.logger.error(f"Error in background cache refresh: {e}")
    
    def get_plugins(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get plugins from cache, refreshing if needed
        
        Args:
            force_refresh: Force cache refresh even if not expired
            
        Returns:
            Dict of plugin metadata
        """
        with self._lock:
            current_time = time.time()
            cache_age = current_time - self._cache['last_updated']
            
            # Check if cache needs refresh
            if (force_refresh or 
                cache_age > self.cache_duration or 
                not self._cache['plugins']):
                
                if not self._cache['is_loading']:
                    self._refresh_cache_internal()
                    
            return self._cache['plugins'].copy()
    
    def get_plugin_names(self) -> list:
        """Get list of plugin names from cache"""
        plugins = self.get_plugins()
        return list(plugins.keys())
    
    def get_plugin_functions(self, plugin_name: str) -> list:
        """Get list of function names for a specific plugin"""
        plugins = self.get_plugins()
        if plugin_name in plugins:
            return list(plugins[plugin_name].get('functions', {}).keys())
        return []
    
    def get_function_parameters(self, plugin_name: str, function_name: str) -> list:
        """Get parameters for a specific plugin function"""
        plugins = self.get_plugins()
        if (plugin_name in plugins and 
            function_name in plugins[plugin_name].get('functions', {})):
            return plugins[plugin_name]['functions'][function_name].get('parameters', [])
        return []
    
    def refresh_cache(self) -> bool:
        """
        Manually refresh the cache
        
        Returns:
            bool: True if refresh was successful
        """
        with self._lock:
            return self._refresh_cache_internal()
    
    def _refresh_cache_internal(self) -> bool:
        """Internal cache refresh method (assumes lock is held)"""
        try:
            self._cache['is_loading'] = True
            self.logger.info("Refreshing plugin cache...")
            
            start_time = time.time()
            plugins = self.discovery.get_plugins_with_metadata()
            refresh_time = time.time() - start_time
            
            self._cache['plugins'] = plugins
            self._cache['last_updated'] = time.time()
            self._cache['is_loading'] = False
            
            self.logger.info(f"Plugin cache refreshed successfully in {refresh_time:.2f}s. "
                           f"Found {len(plugins)} plugins: {list(plugins.keys())}")
            return True
            
        except Exception as e:
            self._cache['is_loading'] = False
            self.logger.error(f"Error refreshing plugin cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            current_time = time.time()
            cache_age = current_time - self._cache['last_updated']
            
            return {
                'plugin_count': len(self._cache['plugins']),
                'last_updated': self._cache['last_updated'],
                'cache_age_seconds': cache_age,
                'is_loading': self._cache['is_loading'],
                'cache_duration': self.cache_duration,
                'is_expired': cache_age > self.cache_duration
            }
    
    def clear_cache(self):
        """Clear the cache"""
        with self._lock:
            self._cache['plugins'] = {}
            self._cache['last_updated'] = 0
            self.logger.info("Plugin cache cleared")
    
    def get_formatted_plugins_for_ui(self) -> list:
        """Get plugins formatted for UI consumption"""
        plugins = self.get_plugins()
        formatted_plugins = []
        
        for plugin_name, plugin_info in plugins.items():
            formatted_plugins.append({
                'name': plugin_name,
                'description': plugin_info.get('description', '').split('\n')[0] if plugin_info.get('description') else f"{plugin_name} plugin",
                'functions': list(plugin_info.get('functions', {}).keys()),
                'file': plugin_info.get('file', ''),
                'function_count': len(plugin_info.get('functions', {}))
            })
        
        # Sort by name for consistent UI
        formatted_plugins.sort(key=lambda x: x['name'])
        return formatted_plugins
    
    def get_plugin_function_details(self, plugin_name: str) -> list:
        """Get detailed function information for a plugin"""
        plugins = self.get_plugins()
        
        if plugin_name not in plugins:
            return []
            
        plugin_info = plugins[plugin_name]
        functions = []
        
        for func_name, func_info in plugin_info.get('functions', {}).items():
            functions.append({
                'name': func_name,
                'description': func_info.get('description', '').split('\n')[0] if func_info.get('description') else f"{func_name} function",
                'parameters': func_info.get('parameters', []),
                'parameter_count': len(func_info.get('parameters', [])),
                'nlp_keywords': func_info.get('nlp_keywords', []),
                'nlp_examples': func_info.get('nlp_examples', []),
                'has_required_params': any(p.get('required', True) for p in func_info.get('parameters', [])),
                'has_optional_params': any(not p.get('required', True) for p in func_info.get('parameters', []))
            })
        
        # Sort by name for consistent UI
        functions.sort(key=lambda x: x['name'])
        return functions

# Global cache manager instance
_plugin_cache_manager = None

def get_plugin_cache_manager(plugins_folder: str = None) -> PluginCacheManager:
    """Get or create the global plugin cache manager"""
    global _plugin_cache_manager
    
    if _plugin_cache_manager is None:
        if plugins_folder is None:
            # Default to server plugins folder
            server_dir = os.path.dirname(os.path.abspath(__file__))
            plugins_folder = os.path.join(server_dir, 'plugins')
            
        _plugin_cache_manager = PluginCacheManager(plugins_folder)
        
    return _plugin_cache_manager

def initialize_plugin_cache(plugins_folder: str = None, start_background_refresh: bool = True):
    """Initialize the plugin cache system"""
    cache_manager = get_plugin_cache_manager(plugins_folder)
    
    # Initial cache load
    cache_manager.refresh_cache()
    
    # Start background refresh if requested
    if start_background_refresh:
        cache_manager.start_background_refresh()
    
    return cache_manager
