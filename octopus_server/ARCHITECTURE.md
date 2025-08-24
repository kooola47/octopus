# 🐙 OCTOPUS SYSTEM ARCHITECTURE & MAINTENANCE GUIDE

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Project Structure](#project-structure)
- [Configuration Management](#configuration-management)
- [Constants & Utilities](#constants--utilities)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Task Lifecycle](#task-lifecycle)
- [Maintenance Tasks](#maintenance-tasks)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ System Overview

**Octopus** is a distributed task orchestration system that allows you to:
- **Create tasks** via web dashboard or API
- **Distribute tasks** to client agents running on different machines
- **Execute tasks** using a plugin system
- **Monitor execution** through a web interface
- **Track results** and execution history

### Core Components

```
🐙 Octopus System
├── 🖥️  Server (octopus_server/)
│   ├── Web Dashboard
│   ├── RESTful API
│   ├── Task Assignment Logic
│   ├── Plugin Management
│   └── SQLite Database
│
└── 🔌 Client (octopus_client/)
    ├── Task Execution Engine
    ├── Plugin System
    ├── Heartbeat Service
    └── Result Reporting
```

---

## 📁 Project Structure

### Improved Structure (Current)
```
octopus/
├── 📜 constants.py              # Shared constants for both server/client
├── 🛠️  utils.py                 # Shared utility functions
├── 📋 requirements.txt          # Project dependencies
├── 📖 README.md                # Project documentation
├── 📝 ARCHITECTURE.md          # This file
├── 🔧 EXECUTION_RECORDS_FIX.md # Bug fix documentation
│
├── 🖥️  octopus_server/          # Server application
│   ├── ⚙️  config.py            # Server configuration
│   ├── 🚀 main.py              # Flask web application
│   ├── 💾 dbhelper.py          # Database operations
│   ├── 💓 heartbeat.py         # Client heartbeat handling
│   ├── 🔌 pluginhelper.py     # Plugin management
│   ├── 📦 cache.py             # In-memory caching
│   ├── ⏰ scheduler.py         # Task scheduling
│   ├── 🗄️  octopus.db          # SQLite database
│   ├── 📁 templates/           # HTML templates
│   ├── 📁 plugins/            # Server-side plugins
│   └── 📁 logs/               # Server logs
│
├── 🔌 octopus_client/          # Client application
│   ├── ⚙️  config.py           # Client configuration
│   ├── 🚀 main.py             # Client main application
│   ├── 📋 taskmanager.py      # Task management
│   ├── 💓 heartbeat.py        # Heartbeat service
│   ├── 🔌 pluginhelper.py    # Plugin synchronization
│   ├── 📦 cache.py            # Client-side caching
│   ├── ⏰ scheduler.py        # Client scheduling
│   ├── 📁 plugins/           # Client-side plugins
│   └── 📁 logs/              # Client logs
│
└── 📁 plugins/                # Shared plugins (deprecated)
```

---

## ⚙️ Configuration Management

### Server Configuration (`octopus_server/config.py`)

```python
# Server Settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
DEBUG_MODE = False

# Database
DB_FILE = os.path.join(os.path.dirname(__file__), "octopus.db")

# Client Management
CLIENT_TIMEOUT = 30              # Offline after 30s
HEARTBEAT_CLEANUP_INTERVAL = 60  # Clean every 60s

# Task Management
TASK_ASSIGNMENT_DELAY = 2        # Wait 2s before assignment
TASK_CLEANUP_INTERVAL = 300      # Clean every 5min

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/server.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
```

### Client Configuration (`octopus_client/config.py`)

```python
# Server Connection
SERVER_URL = "http://localhost:8000"

# Client Behavior
HEARTBEAT_INTERVAL = 10      # Send every 10s
TASK_CHECK_INTERVAL = 5      # Check every 5s
MAX_RETRY_ATTEMPTS = 3       # Max retries
RETRY_DELAY = 2              # Wait 2s between retries

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/client.log"
```

### Environment Variable Override

Both server and client configurations can be overridden using environment variables:

```bash
# Server
OCTOPUS_SERVER_HOST=192.168.1.100
OCTOPUS_SERVER_PORT=9000
OCTOPUS_LOG_LEVEL=DEBUG

# Client
OCTOPUS_SERVER_URL=http://192.168.1.100:9000
OCTOPUS_HEARTBEAT_INTERVAL=15
```

---

## 🏗️ Constants & Utilities

### Constants (`constants.py`)

Central place for all system constants to ensure consistency:

```python
class TaskStatus:
    CREATED = "Created"
    ACTIVE = "Active" 
    DONE = "Done"
    SUCCESS = "success"
    FAILED = "failed"
    COMPLETED = "completed"

class TaskOwnership:
    ALL = "ALL"           # All clients
    ANYONE = "Anyone"     # Any available client
    SPECIFIC = "Specific" # Specific client

class TaskType:
    ADHOC = "Adhoc"       # One-time task
    SCHEDULED = "Scheduled" # Recurring task
    INTERVAL = "Interval" # Interval-based task
```

### Utilities (`utils.py`)

Shared functions for common operations:

```python
# Logging setup
setup_logging(log_file, log_level="INFO")

# Network utilities
get_local_ip()
get_hostname()
get_client_id()

# Time utilities
get_current_timestamp()
format_duration(seconds)
is_timestamp_expired(timestamp, timeout)

# Data utilities
safe_json_loads(json_str, default=None)
validate_task_data(task)
extract_task_args(task)
```

---

## 💾 Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,              -- Unique task identifier
    owner TEXT,                      -- ALL/Anyone/Specific user
    plugin TEXT,                     -- Plugin name
    action TEXT,                     -- Action to execute
    args TEXT,                       -- JSON array of arguments
    kwargs TEXT,                     -- JSON object of keyword args
    type TEXT,                       -- Adhoc/Scheduled/Interval
    execution_start_time TEXT,       -- When to start execution
    execution_end_time TEXT,         -- When to end execution
    interval TEXT,                   -- Execution interval
    status TEXT,                     -- Created/Active/Done/success/failed
    executor TEXT,                   -- Assigned client
    result TEXT,                     -- Execution result
    updated_at TEXT                  -- Last update timestamp
);
```

### Executions Table
```sql
CREATE TABLE executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,                    -- Reference to tasks.id
    client TEXT,                     -- Client that executed
    status TEXT,                     -- success/failed/completed
    result TEXT,                     -- Execution result/output
    updated_at TEXT,                 -- Execution timestamp
    FOREIGN KEY (task_id) REFERENCES tasks (id)
);
```

---

## 🌐 API Endpoints

### Server Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web dashboard |
| `POST` | `/heartbeat` | Client heartbeat |
| `GET/POST` | `/tasks` | List/create tasks |
| `PUT/DELETE` | `/tasks/<id>` | Update/delete task |
| `GET` | `/plugins` | List available plugins |

### Client Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/tasks` | Local task management |
| `PUT/DELETE` | `/tasks/<id>` | Local task operations |

---

## 🔄 Task Lifecycle

### 1. Task Creation
```
User creates task via dashboard
├── Task stored in database with status="Created"
├── No executor assigned yet
└── Available for assignment
```

### 2. Task Assignment
```
Server assignment logic runs periodically
├── Finds tasks with status="Created"
├── Matches task.owner with available clients
├── Updates task.executor and status="Active"
└── Task ready for client pickup
```

### 3. Task Pickup
```
Client polls server for assigned tasks
├── Checks if task.executor matches client ID
├── Downloads task details and plugin if needed
├── Queues task for execution
└── Client begins execution
```

### 4. Task Execution
```
Client executes task using plugin system
├── Loads plugin module
├── Calls specified action with args/kwargs
├── Captures result and status
└── Reports back to server
```

### 5. Result Recording
```
Server receives execution results
├── Creates record in executions table
├── Updates task status to "Done"/"success"/"failed"
├── Results visible in dashboard
└── Task lifecycle complete
```

---

## 🛠️ Maintenance Tasks

### Daily Maintenance

1. **Log Rotation**
   ```bash
   # Server logs
   tail -f octopus_server/logs/server.log
   
   # Client logs  
   tail -f octopus_client/logs/client.log
   ```

2. **Database Cleanup**
   ```sql
   -- Remove old completed tasks (older than 30 days)
   DELETE FROM tasks WHERE 
       status IN ('Done', 'success', 'failed') 
       AND datetime(updated_at) < datetime('now', '-30 days');
   
   -- Remove old executions
   DELETE FROM executions WHERE 
       datetime(updated_at) < datetime('now', '-30 days');
   ```

### Weekly Maintenance

1. **Plugin Updates**
   - Check for new plugins in shared folder
   - Verify plugin compatibility
   - Test plugin functionality

2. **Performance Review**
   - Check task execution times
   - Monitor client connection stability
   - Review error logs

### Monthly Maintenance

1. **Database Optimization**
   ```sql
   -- Rebuild database indexes
   REINDEX;
   
   -- Vacuum database to reclaim space
   VACUUM;
   ```

2. **Configuration Review**
   - Review timeout settings
   - Check log retention policies
   - Update client configurations

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Tasks Not Being Assigned
```bash
# Check server logs
grep "Task assignment" octopus_server/logs/server.log

# Check client heartbeats
grep "Heartbeat received" octopus_server/logs/server.log

# Verify client connectivity
curl http://localhost:8000/heartbeat -X POST -H "Content-Type: application/json" -d '{"client": "test"}'
```

#### 2. Tasks Not Being Executed
```bash
# Check client task pickup
grep "should_client_execute" octopus_client/logs/client.log

# Check plugin loading
grep "Plugin.*loaded" octopus_client/logs/client.log

# Verify plugin exists
ls octopus_client/plugins/
```

#### 3. Execution Records Missing
```bash
# Check execution result reporting
grep "Adding execution result" octopus_server/logs/server.log

# Check client result submission
grep "post_execution_result\|update_task_status" octopus_client/logs/client.log

# Verify database records
sqlite3 octopus_server/octopus.db "SELECT * FROM executions ORDER BY updated_at DESC LIMIT 10;"
```

#### 4. Dashboard Status Issues
```bash
# Check status computation
grep "compute_task_status" octopus_server/logs/server.log

# Verify database status
sqlite3 octopus_server/octopus.db "SELECT id, status, executor FROM tasks WHERE status != 'Created';"

# Check template rendering
grep "dashboard" octopus_server/logs/server.log
```

### Debug Mode

Enable debug logging for more detailed information:

```python
# Server config.py
LOG_LEVEL = "DEBUG"

# Client config.py  
LOG_LEVEL = "DEBUG"
```

### Health Checks

Create monitoring scripts to verify system health:

```bash
#!/bin/bash
# health_check.sh

echo "🐙 Octopus Health Check"
echo "======================"

# Check server process
if pgrep -f "octopus_server/main.py" > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running"
fi

# Check client process
if pgrep -f "octopus_client/main.py" > /dev/null; then
    echo "✅ Client is running"
else
    echo "❌ Client is not running"
fi

# Check database connection
if sqlite3 octopus_server/octopus.db "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database is accessible"
else
    echo "❌ Database is not accessible"
fi

# Check recent heartbeats
recent_heartbeats=$(sqlite3 octopus_server/octopus.db "SELECT COUNT(*) FROM tasks WHERE updated_at > datetime('now', '-5 minutes');" 2>/dev/null || echo "0")
echo "💓 Recent heartbeats: $recent_heartbeats"

# Check pending tasks
pending_tasks=$(sqlite3 octopus_server/octopus.db "SELECT COUNT(*) FROM tasks WHERE status = 'Created';" 2>/dev/null || echo "0")
echo "📋 Pending tasks: $pending_tasks"

# Check active tasks
active_tasks=$(sqlite3 octopus_server/octopus.db "SELECT COUNT(*) FROM tasks WHERE status = 'Active';" 2>/dev/null || echo "0")
echo "🔄 Active tasks: $active_tasks"
```

---

## 🎯 Best Practices

### Configuration Management
- Use environment variables for deployment-specific settings
- Keep sensitive data (if any) in separate config files
- Document all configuration options

### Error Handling
- Use structured logging with consistent format
- Implement retry logic for network operations
- Capture and log all exceptions with context

### Performance Optimization
- Monitor task execution times
- Use connection pooling for database operations
- Implement caching for frequently accessed data

### Security Considerations
- Validate all input data
- Sanitize database queries (using parameterized queries)
- Implement proper error handling without exposing internals
- Consider adding authentication for production use

### Scalability
- Design for horizontal scaling (multiple clients)
- Use database indexes for performance
- Implement proper cleanup for old data
- Monitor resource usage

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review log files for error messages
3. Verify configuration settings
4. Test with debug logging enabled

This architecture provides a solid foundation for maintaining and extending the Octopus distributed task orchestration system! 🐙
