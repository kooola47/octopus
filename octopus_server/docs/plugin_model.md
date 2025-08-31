# 🔌 Plugin Model Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Plugin Discovery](#plugin-discovery)
- [Plugin Management](#plugin-management)
- [Plugin Execution](#plugin-execution)
- [Plugin Distribution](#plugin-distribution)
- [Related Documentation](#related-documentation)

---

## 🏁 Overview

The Plugin Model manages plugins that define the actual tasks executed by the Octopus system. It handles plugin discovery, metadata management, versioning, and distribution to clients.

### Key Responsibilities
- Plugin discovery and registration
- Plugin metadata management
- Plugin version control
- Plugin distribution to clients
- Plugin execution coordination

### Related Files
- `models/plugin_model.py` - Main model implementation
- `pluginhelper.py` - Plugin helper functions
- `plugin_discovery.py` - Plugin discovery logic
- `routes/plugin_routes.py` - Plugin management routes
- `dbhelper.py` - Database operations

---

## 🗄️ Database Schema

The plugins table stores all plugin-related information:

```sql
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
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER (Primary Key) | Internal plugin record ID |
| name | TEXT (Unique) | Unique plugin name |
| file_path | TEXT | Path to plugin file |
| md5_hash | TEXT | MD5 hash for integrity checking |
| version | TEXT | Plugin version (default: 1.0.0) |
| description | TEXT | Plugin description |
| author | TEXT | Plugin author |
| is_active | BOOLEAN | Plugin active status |
| file_size | INTEGER | Plugin file size in bytes |
| last_modified | REAL | Plugin file modification timestamp |
| install_count | INTEGER | Number of times plugin installed |
| created_at | REAL | Plugin registration timestamp |
| updated_at | REAL | Last update timestamp |

### Indexes

- `idx_plugins_name` - For plugin name lookups
- `idx_plugins_is_active` - For active status queries
- `idx_plugins_md5_hash` - For integrity checking
- `idx_plugins_last_modified` - For modification time queries

---

## 🔍 Plugin Discovery

The system automatically discovers available plugins:

### Discovery Process
1. Scan plugins directory for Python files
2. Extract metadata from plugin files
3. Register new plugins in database
4. Update existing plugin information

### Plugin Directory
- Default location: `./plugins`
- Configurable via `PLUGINS_FOLDER` setting
- Supports subdirectories (future enhancement)

### Metadata Extraction
- Plugin name from filename
- Description from docstrings
- Author information
- Function list and parameters

### Discovery Triggers
- Server startup
- Manual refresh
- File system monitoring (planned)

---

## 🧮 Plugin Management

Plugin management includes registration, activation, and metadata handling:

### Plugin Registration
- Automatic registration of new plugins
- Manual registration through dashboard
- Metadata validation
- Duplicate detection

### Plugin Activation
- Active/inactive status control
- Selective plugin availability
- Bulk activation/deactivation

### Plugin Metadata
- Name and description
- Version information
- Author details
- Function signatures
- Parameter specifications

### Management Interface
- Web dashboard for plugin management
- API endpoints for programmatic access
- Plugin search and filtering

---

## ⚡ Plugin Execution

Plugins define the actual task execution logic:

### Execution Model
- Plugins are Python files with specific structure
- Tasks call plugin functions with parameters
- Results are returned to the server

### Plugin Structure
```python
def run(*args, **kwargs):
    # Plugin execution logic
    return result
```

### Parameter Handling
- Positional arguments (`args`)
- Keyword arguments (`kwargs`)
- Type validation (planned)
- Default values

### Result Processing
- Results returned as strings
- Structured data support (JSON)
- Error handling and reporting

---

## 📦 Plugin Distribution

Plugins are distributed from server to clients:

### Distribution Mechanism
- HTTP endpoint for plugin download
- MD5 hash verification
- Client-side caching

### Synchronization Process
1. Client requests plugin list
2. Server provides plugin metadata
3. Client identifies missing/outdated plugins
4. Client downloads required plugins
5. Client verifies plugin integrity

### Version Management
- Version-based update decisions
- Backward compatibility considerations
- Rollback support (planned)

### Integrity Checking
- MD5 hash verification
- File size validation
- Corruption detection

---

## 📚 Related Documentation

### Internal Documentation
- [PLUGIN_RESPONSE_SPECIFICATION.md](../PLUGIN_RESPONSE_SPECIFICATION.md) - Plugin response format
- [PLUGIN_RELOAD_FIX.md](../PLUGIN_RELOAD_FIX.md) - Plugin reload implementation
- [PLUGIN_DISCOVERY.md](#) - Plugin discovery details (planned)

### External Resources
- [pluginhelper.py](../pluginhelper.py) - Plugin helper functions
- [plugin_discovery.py](../plugin_discovery.py) - Plugin discovery implementation
- [routes/plugin_routes.py](../routes/plugin_routes.py) - Plugin management routes
- [Plugin System Documentation](#) - Comprehensive plugin system guide (planned)
- [API Documentation](api.md) - RESTful endpoints for plugin data