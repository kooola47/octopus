#!/usr/bin/env python3
"""
Cache Demo Plugin
================
Demonstrates how to use the global cache manager in plugins.

This plugin shows how to:
1. Store data in plugin-specific cache
2. Retrieve data from server cache
3. Use user profile cache
4. Broadcast data to clients

FUNCTIONS AVAILABLE:
- demo_plugin_cache: Store and retrieve data in plugin-specific cache
- demo_user_cache: Store and retrieve user-specific data
- demo_broadcast_cache: Broadcast data to all clients
- demo_server_data: Retrieve data from server cache
- demo_cache_stats: Show cache statistics
"""

import time
import json

# Plugin Information
PLUGIN_NAME = "cache_demo"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Demonstrates global cache manager usage"

def demo_plugin_cache(action="set", key="demo_key", value="demo_value", ttl=None):
    """
    Demonstrate plugin-specific cache operations
    
    Args:
        action: 'set', 'get', 'delete', 'clear', 'all'
        key: Cache key
        value: Value to store (for set action)
        ttl: Time to live in seconds
    """
    try:
        # Import global cache functions (works on both server and client)
        try:
            # Try server-side import first
            from global_cache_manager import plugin_cache_set, plugin_cache_get, plugin_cache_delete, plugin_cache_clear, get_global_cache_manager
            cache_manager = get_global_cache_manager()
            location = "server"
        except ImportError:
            # Fall back to client-side import
            from global_cache_manager import client_plugin_cache_set as plugin_cache_set, client_plugin_cache_get as plugin_cache_get, client_plugin_cache_delete as plugin_cache_delete, client_plugin_cache_clear as plugin_cache_clear, get_client_global_cache_manager as get_global_cache_manager
            cache_manager = get_global_cache_manager()
            location = "client"
        
        result = {
            "plugin": PLUGIN_NAME,
            "action": action,
            "location": location,
            "timestamp": time.time()
        }
        
        if action == "set":
            plugin_cache_set(PLUGIN_NAME, key, value, ttl)
            result["message"] = f"Set cache key '{key}' = '{value}'"
            if ttl:
                result["message"] += f" (TTL: {ttl}s)"
        
        elif action == "get":
            cached_value = plugin_cache_get(PLUGIN_NAME, key, "NOT_FOUND")
            result["key"] = key
            result["value"] = cached_value
            result["message"] = f"Retrieved cache key '{key}'"
        
        elif action == "delete":
            plugin_cache_delete(PLUGIN_NAME, key)
            result["message"] = f"Deleted cache key '{key}'"
        
        elif action == "clear":
            plugin_cache_clear(PLUGIN_NAME)
            result["message"] = f"Cleared all cache for plugin '{PLUGIN_NAME}'"
        
        elif action == "all":
            all_data = cache_manager.plugin_get_all(PLUGIN_NAME)
            result["all_data"] = all_data
            result["count"] = len(all_data)
            result["message"] = f"Retrieved all cache data for plugin '{PLUGIN_NAME}'"
        
        else:
            result["error"] = f"Unknown action: {action}"
        
        return {
            "status": "success",
            "result": result,
            "type": "cache"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "cache"
        }

def demo_user_cache(username="demo_user", action="set", setting="theme", value="dark"):
    """
    Demonstrate user profile cache operations (server-side only)
    
    Args:
        username: Username
        action: 'set', 'get'
        setting: Setting name
        value: Value to store (for set action)
    """
    try:
        # This only works on server side
        from global_cache_manager import get_global_cache_manager
        cache_manager = get_global_cache_manager()
        
        result = {
            "plugin": PLUGIN_NAME,
            "action": action,
            "username": username,
            "setting": setting,
            "timestamp": time.time()
        }
        
        if action == "set":
            cache_manager.set_user_setting(username, setting, value)
            result["message"] = f"Set user setting '{setting}' = '{value}' for {username}"
        
        elif action == "get":
            cached_value = cache_manager.get_user_setting(username, setting, "NOT_SET")
            result["value"] = cached_value
            result["message"] = f"Retrieved user setting '{setting}' for {username}"
        
        else:
            result["error"] = f"Unknown action: {action}"
        
        return {
            "status": "success",
            "result": result,
            "type": "cache"
        }
        
    except ImportError:
        return {
            "status": "error",
            "error": "User cache operations only available on server side",
            "type": "cache"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "cache"
        }

def demo_broadcast_cache(key="demo_broadcast", value="Hello all clients!", ttl=300):
    """
    Demonstrate broadcasting data to all clients (server-side only)
    
    Args:
        key: Broadcast key
        value: Value to broadcast
        ttl: Time to live in seconds
    """
    try:
        # This only works on server side
        from global_cache_manager import broadcast_to_clients
        
        broadcast_to_clients(key, value, ttl)
        
        result = {
            "plugin": PLUGIN_NAME,
            "action": "broadcast",
            "key": key,
            "value": value,
            "ttl": ttl,
            "timestamp": time.time(),
            "message": f"Broadcast '{key}' to all clients"
        }
        
        return {
            "status": "success",
            "result": result,
            "type": "cache"
        }
        
    except ImportError:
        return {
            "status": "error",
            "error": "Broadcast operations only available on server side",
            "type": "cache"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "cache"
        }

def demo_server_data(key="available_plugins"):
    """
    Demonstrate retrieving data from server cache (client-side)
    
    Args:
        key: Server data key to retrieve
    """
    try:
        # Try client-side import first
        try:
            from global_cache_manager import get_server_data
            server_data = get_server_data(key, "NOT_FOUND")
            location = "client"
        except ImportError:
            # Fall back to server-side
            from global_cache_manager import get_global_cache_manager
            cache_manager = get_global_cache_manager()
            server_data = cache_manager.get(key, 'global_broadcast', None, "NOT_FOUND")
            location = "server"
        
        result = {
            "plugin": PLUGIN_NAME,
            "action": "get_server_data",
            "key": key,
            "value": server_data,
            "location": location,
            "timestamp": time.time(),
            "message": f"Retrieved server data for key '{key}'"
        }
        
        return {
            "status": "success",
            "result": result,
            "type": "cache"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "cache"
        }

def demo_cache_stats():
    """
    Demonstrate retrieving cache statistics
    """
    try:
        # Import appropriate cache manager
        try:
            # Try server-side import first
            from global_cache_manager import get_global_cache_manager
            cache_manager = get_global_cache_manager()
            location = "server"
        except ImportError:
            # Fall back to client-side import
            from global_cache_manager import get_client_global_cache_manager
            cache_manager = get_client_global_cache_manager()
            location = "client"
        
        stats = cache_manager.get_stats()
        
        result = {
            "plugin": PLUGIN_NAME,
            "action": "get_stats",
            "location": location,
            "stats": stats,
            "timestamp": time.time(),
            "message": f"Retrieved cache statistics from {location}"
        }
        
        return {
            "status": "success",
            "result": result,
            "type": "cache"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "cache"
        }

def demo_sync_from_server():
    """
    Demonstrate syncing data from server (client-side only)
    """
    try:
        # This only works on client side
        from global_cache_manager import sync_from_server
        
        success = sync_from_server(force=True)
        
        result = {
            "plugin": PLUGIN_NAME,
            "action": "sync_from_server",
            "success": success,
            "timestamp": time.time(),
            "message": "Forced sync from server completed"
        }
        
        return {
            "status": "success",
            "result": result,
            "type": "cache"
        }
        
    except ImportError:
        return {
            "status": "error",
            "error": "Sync operations only available on client side",
            "type": "cache"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "cache"
        }

# Main plugin functions for UI
def run():
    """Default plugin execution - demo all cache operations"""
    results = []
    
    # Demo plugin cache
    results.append(demo_plugin_cache("set", "demo_counter", 1))
    results.append(demo_plugin_cache("get", "demo_counter"))
    results.append(demo_plugin_cache("set", "demo_data", {"timestamp": time.time(), "message": "Hello Cache!"}, 60))
    results.append(demo_plugin_cache("all"))
    
    # Demo cache stats
    results.append(demo_cache_stats())
    
    return {
        "status": "success",
        "message": "Cache demo completed successfully",
        "results": results,
        "type": "cache"
    }

if __name__ == "__main__":
    # Test the plugin
    result = run()
    print(json.dumps(result, indent=2))
