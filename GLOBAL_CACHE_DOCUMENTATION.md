# Global Cache Manager Documentation

## Overview

The Global Cache Manager provides a comprehensive caching system for both Octopus server and client sides, enabling plugins and components to store and retrieve data efficiently across the distributed system. It includes robust security features to ensure users can only access their own profile data.

## Architecture

### Server-Side Cache Manager (`octopus_server/global_cache_manager.py`)

The server-side cache manager provides multiple cache layers:

1. **Startup Cache** - Data initialized when server starts
2. **User Profiles Cache** - Data from user profile pages (with user access control)
3. **Global Broadcast Cache** - Data published to all clients
4. **Plugin-Specific Cache** - Isolated namespaces for plugins
5. **Temporary Cache** - Short-lived data
6. **Persistent Cache** - Long-lived data

### Client-Side Cache Manager (`octopus_client/global_cache_manager.py`)

The client-side cache manager provides:

1. **Startup Cache** - Data initialized when client starts
2. **Server Data Cache** - Data received from server
3. **Plugin-Specific Cache** - Isolated namespaces for plugins
4. **User Preferences Cache** - Local user settings
5. **Temporary Cache** - Short-lived data
6. **Persistent Cache** - Long-lived data

## Security Features

### User Identity Verification

The cache system includes robust security to ensure users can only access their own profile data:

- **User Identity Management**: Clients identify themselves with username and client ID
- **Server-Side Verification**: Server verifies user identity before granting access to profile data
- **Access Control**: Users can only access their own profile data and settings
- **Admin Privileges**: Admin users have elevated access to manage user data
- **API Security**: All user profile API endpoints verify identity and return 403 for unauthorized access

### Identity Setup

```python
# Client-side identity setup (done automatically on initialization)
cache_manager.set_user_identity("username")

# Get current identity
username = cache_manager.get_current_username()
client_id = cache_manager.get_current_client_id()
```

## Usage

### Basic Cache Operations

#### Server-Side

```python
from global_cache_manager import get_global_cache_manager

cache_manager = get_global_cache_manager()

# Set data with optional TTL
cache_manager.set('my_key', 'my_value', 'temporary', ttl=300)

# Get data
value = cache_manager.get('my_key', 'temporary', default='not_found')

# Delete data
cache_manager.delete('my_key', 'temporary')
```

#### Client-Side

```python
from global_cache_manager import get_client_global_cache_manager

cache_manager = get_client_global_cache_manager()

# Same API as server-side
cache_manager.set('my_key', 'my_value', 'temporary', ttl=300)
value = cache_manager.get('my_key', 'temporary')
```

### Plugin-Specific Cache

#### Server-Side Plugin

```python
from global_cache_manager import plugin_cache_set, plugin_cache_get, plugin_cache_delete

# Easy plugin cache functions
plugin_cache_set('my_plugin', 'config', {'setting': 'value'}, ttl=3600)
config = plugin_cache_get('my_plugin', 'config', {})
plugin_cache_delete('my_plugin', 'config')
```

#### Client-Side Plugin

```python
from global_cache_manager import client_plugin_cache_set, client_plugin_cache_get

# Client-side plugin cache functions
client_plugin_cache_set('my_plugin', 'local_data', 'value')
data = client_plugin_cache_get('my_plugin', 'local_data')
```

### User Profile Cache (Server-Side Only) - SECURE ACCESS

**Important**: User profile operations now include security controls. Users can only access their own profile data.

```python
from global_cache_manager import get_global_cache_manager

cache_manager = get_global_cache_manager()

# Set user profile data (requires user identity verification)
# The requesting_user parameter ensures only the user or admin can modify this data
cache_manager.set_user_profile_data('username', {
    'theme': 'dark',
    'language': 'en',
    'notifications': True
}, requesting_user='username')  # Must match target username or be admin

# Get user profile data (requires user identity verification)
# Users can only access their own profile data
profile = cache_manager.get_user_profile_data('username', requesting_user='username')

# Set specific user setting (secure)
cache_manager.set_user_setting('username', 'theme', 'light', requesting_user='username')

# Get specific user setting (secure)
theme = cache_manager.get_user_setting('username', 'theme', 'light', requesting_user='username')
```

**Security Notes:**
- All user profile methods now require a `requesting_user` parameter
- Users can only access their own data (requesting_user must match username)
- Admin users have elevated access to manage any user's data
- API endpoints verify identity through X-Client-ID and X-Username headers
- Unauthorized access attempts return HTTP 403 Forbidden responses

### Broadcasting to Clients (Server-Side Only)

```python
from global_cache_manager import broadcast_to_clients

# Broadcast data to all clients
broadcast_to_clients('system_message', {
    'type': 'maintenance',
    'message': 'System will be down at 2 AM',
    'timestamp': time.time()
}, ttl=3600)
```

### Syncing Data from Server (Client-Side Only)

```python
from global_cache_manager import sync_from_server, get_server_data

# Force sync from server
success = sync_from_server(force=True)

# Get data that was synced from server
plugins = get_server_data('available_plugins', [])
```

## API Endpoints

The server exposes several API endpoints for cache operations:

### Cache Statistics
- `GET /api/cache/stats` - Get cache statistics

### Broadcast Cache
- `GET /api/cache/broadcast` - Get broadcast data for clients

### Plugin Cache
- `GET /api/cache/plugin/<plugin_name>` - Get all plugin cache data
- `GET /api/cache/plugin/<plugin_name>/<key>` - Get specific plugin cache key
- `POST /api/cache/plugin/<plugin_name>/<key>` - Set plugin cache key
- `DELETE /api/cache/plugin/<plugin_name>/<key>` - Delete plugin cache key

### Global Broadcast
- `POST /api/cache/broadcast/<key>` - Broadcast data to all clients

### User Profile Cache - SECURE ENDPOINTS
- `GET /api/cache/user/<username>/profile` - Get user profile cache
  - **Security**: Requires X-Client-ID and X-Username headers
  - **Access Control**: Users can only access their own profile data
  - **Returns**: HTTP 403 if unauthorized
- `POST /api/cache/user/<username>/profile` - Set user profile cache
  - **Security**: Requires X-Client-ID and X-Username headers
  - **Access Control**: Users can only modify their own profile data
  - **Returns**: HTTP 403 if unauthorized

**Required Headers for User Profile Endpoints:**
```
X-Client-ID: <client_id>
X-Username: <username>
```

**Access Control Rules:**
- Users can only access profiles where `<username>` matches their authenticated username
- Admin users have elevated access to any user's profile data
- Missing or invalid headers result in HTTP 403 Forbidden responses

### Admin Endpoints
- `GET /api/cache/all` - Get all cache data (admin only)

## Cache Layers

### Server-Side Cache Types

1. **startup** - Server initialization data
   - Server start time
   - Server configuration
   - Initial settings

2. **user_profiles** - User-specific data
   - User preferences
   - Profile settings
   - User-specific configurations

3. **global_broadcast** - Data to broadcast to clients
   - System announcements
   - Global settings
   - Available plugins list

4. **plugins** - Plugin-specific data
   - Plugin configurations
   - Plugin state
   - Plugin results

5. **temporary** - Short-lived data (default)
   - Session data
   - Temporary results

6. **persistent** - Long-lived data
   - Application state
   - Long-term configurations

### Client-Side Cache Types

1. **startup** - Client initialization data
2. **server_data** - Data synced from server
3. **plugins** - Plugin-specific data
4. **user_preferences** - Local user settings
5. **temporary** - Short-lived data
6. **persistent** - Long-lived data

## Auto-Sync Features (Client-Side)

The client cache manager automatically syncs data from the server:

```python
# Enable auto-sync (enabled by default)
cache_manager.enable_auto_sync(interval=60)  # 60 seconds

# Disable auto-sync
cache_manager.disable_auto_sync()

# Change sync interval
cache_manager.set_sync_interval(120)  # 2 minutes

# Check if server is online
online = cache_manager.is_online()
```

## Integration Examples

### Plugin with Server and Client Caching

```python
# my_plugin.py (works on both server and client)

def save_user_data(username, data):
    """Save user data with appropriate caching"""
    try:
        # Try server-side caching
        from global_cache_manager import get_global_cache_manager
        cache_manager = get_global_cache_manager()
        cache_manager.set_user_profile_data(username, data)
        return "saved_on_server"
    except ImportError:
        # Fall back to client-side caching
        from global_cache_manager import client_plugin_cache_set
        client_plugin_cache_set('my_plugin', f'user_data_{username}', data)
        return "saved_on_client"

def get_user_data(username):
    """Get user data from appropriate cache"""
    try:
        # Try server-side first
        from global_cache_manager import get_global_cache_manager
        cache_manager = get_global_cache_manager()
        return cache_manager.get_user_profile_data(username)
    except ImportError:
        # Fall back to client-side
        from global_cache_manager import client_plugin_cache_get
        return client_plugin_cache_get('my_plugin', f'user_data_{username}')
```

### Broadcasting System Announcements

```python
# Server-side: Send announcement
from global_cache_manager import broadcast_to_clients

def send_system_announcement(message, priority='normal'):
    announcement = {
        'message': message,
        'priority': priority,
        'timestamp': time.time(),
        'id': str(uuid.uuid4())
    }
    
    # Broadcast to all clients
    broadcast_to_clients('system_announcement', announcement, ttl=3600)
    
    return announcement

# Client-side: Receive announcement
from global_cache_manager import get_server_data

def check_announcements():
    announcement = get_server_data('system_announcement')
    if announcement:
        print(f"System announcement: {announcement['message']}")
        return announcement
    return None
```

## Statistics and Monitoring

Get detailed cache statistics:

```python
from global_cache_manager import get_global_cache_manager

cache_manager = get_global_cache_manager()
stats = cache_manager.get_stats()

print(f"Cache hit rate: {stats['hit_rate']}%")
print(f"Total hits: {stats['hits']}")
print(f"Total misses: {stats['misses']}")
print(f"Cache sizes: {stats['cache_sizes']}")
print(f"Plugin cache sizes: {stats['plugin_cache_sizes']}")
```

## Error Handling

The cache manager includes comprehensive error handling:

```python
try:
    from global_cache_manager import plugin_cache_set
    plugin_cache_set('my_plugin', 'key', 'value')
except ImportError:
    # Cache manager not available
    print("Cache manager not available")
except ValueError as e:
    # Invalid parameters
    print(f"Invalid cache parameters: {e}")
except Exception as e:
    # Other errors
    print(f"Cache error: {e}")
```

## Best Practices

1. **Use appropriate cache types**:
   - Use `temporary` for short-lived data
   - Use `persistent` for long-lived data
   - Use plugin-specific cache for plugin data

2. **Set appropriate TTL values**:
   - Short TTL for frequently changing data
   - Long TTL for static data
   - No TTL for persistent data

3. **Handle ImportError gracefully**:
   - Always handle cases where cache manager might not be available
   - Provide fallback mechanisms

4. **Use plugin-specific helpers**:
   - Use `plugin_cache_*` functions for plugin data
   - This provides automatic namespacing

5. **Monitor cache performance**:
   - Regularly check cache statistics
   - Adjust TTL values based on usage patterns

6. **Clean up resources**:
   - Clear plugin cache when appropriate
   - Don't cache sensitive data without proper TTL

## Initialization

### Server-Side Initialization

The global cache manager is automatically initialized when the server starts:

```python
# In octopus_server/main.py
from global_cache_manager import initialize_global_cache

# This is called automatically during server startup
global_cache = initialize_global_cache()
```

### Client-Side Initialization

The client global cache manager is automatically initialized when the client starts:

```python
# In octopus_client/main.py
from global_cache_manager import initialize_client_global_cache

# This is called automatically during client startup
global_cache = initialize_client_global_cache(server_url)
```

## Example Plugin: Cache Demo

See `plugins/cache_demo.py` for a comprehensive example that demonstrates all cache features:

- Plugin-specific caching
- User profile caching
- Broadcasting to clients
- Retrieving server data
- Cache statistics
- Cross-platform compatibility

Run the demo plugin to see the cache system in action!
