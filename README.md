# 🐙 OCTOPUS - Distributed Task Orchestration System

![Octopus Banner](https://img.shields.io/badge/🐙-Octopus-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?style=flat-square)

A powerful distributed task orchestration system that allows you to create, distribute, and execute tasks across multiple client machines using a flexible plugin architecture.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- SQLite3
- Flask and dependencies (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd octopus
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**
   ```bash
   cd octopus_server
   python main.py
   ```

4. **Start a client** (in another terminal)
   ```bash
   cd octopus_client
   python main.py
   ```

5. **Access the dashboard**
   Open http://localhost:8000 in your browser

### 🖥️ PowerShell Deployment (Windows)

For Windows environments, use the included PowerShell scripts for automated setup with conda environments:

#### Server Setup
```powershell
# Basic server setup (creates conda environment and starts server)
.\setup_server.ps1

# Skip environment setup (if already configured)
.\setup_server.ps1 -SkipEnvSetup

# Run on custom port
.\setup_server.ps1 -Port 9000
```

#### Client Setup
```powershell
# Basic client setup (creates conda environment and starts client)
.\setup_client.ps1

# Connect to custom server
.\setup_client.ps1 -ServerUrl "http://192.168.1.100:8000"

# Set custom client name
.\setup_client.ps1 -ClientName "WorkStation-01"

# Skip environment setup
.\setup_client.ps1 -SkipEnvSetup
```

#### Features of PowerShell Scripts
- ✅ **Automatic conda environment creation** (octopus_server/octopus_client)
- ✅ **Dependency installation** from requirements.txt
- ✅ **Playwright browser extraction** from bundled zip file (for offline deployments)
- ✅ **Server connectivity testing** (client script)
- ✅ **Colored console output** with status indicators
- ✅ **Error handling** and validation
- ✅ **Customizable parameters** (port, server URL, client name)

#### Offline Deployment
For corporate environments without internet access:

1. **Create playwright browser package** (run on machine with internet):
   ```powershell
   .\create_playwright_package.ps1
   ```

2. **Include playwright_browsers.zip** in your deployment package

3. **Deploy to target machines** - scripts will automatically extract browsers

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions and troubleshooting.

## 📋 Features

### 🎯 Core Capabilities
- **Web Dashboard** - Create and monitor tasks through a clean web interface
- **RESTful API** - Programmatic access for automation and integration
- **Plugin System** - Extensible task execution using Python plugins
- **Multi-Client Support** - Deploy clients on multiple machines
- **Real-time Monitoring** - Live status updates and execution tracking
- **Flexible Task Assignment** - Support for ALL, Anyone, or specific user assignments

### 🔧 Technical Features
- **Heartbeat Monitoring** - Track client connectivity and health
- **Execution History** - Complete audit trail of task executions
- **Error Handling** - Robust error reporting and recovery
- **Configuration Management** - Environment-based configuration
- **Logging System** - Comprehensive logging for debugging
- **Database Storage** - SQLite for reliable data persistence

## 🏗️ Architecture

```
🐙 Octopus Ecosystem
├── 🖥️  Server Component
│   ├── Flask Web Application
│   ├── SQLite Database
│   ├── Plugin Management
│   ├── Task Assignment Logic
│   └── RESTful API
│
└── 🔌 Client Components (Multiple)
    ├── Task Execution Engine
    ├── Plugin Synchronization
    ├── Heartbeat Service
    └── Result Reporting
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **Server** | Central orchestration hub, web dashboard, task management |
| **Client** | Distributed execution agents, plugin runners |
| **Database** | Task storage, execution history, client tracking |
| **Plugins** | Modular task implementations |
| **Cache** | Performance optimization, temporary data |

## 📖 Usage Guide

### Creating Tasks

#### Via Web Dashboard
1. Navigate to http://localhost:8000
2. Click "Create New Task"
3. Fill in the task details:
   - **Owner**: ALL (all clients), Anyone (any available), or specific user
   - **Plugin**: Choose from available plugins
   - **Action**: Plugin method to execute
   - **Arguments**: JSON array of parameters
   - **Type**: Adhoc (one-time) or Scheduled (recurring)

#### Via API
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "Anyone",
    "plugin": "create_incident",
    "action": "main",
    "args": ["P1", "Database connection failed"],
    "type": "Adhoc"
  }'
```

### Task Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Adhoc** | One-time execution | Immediate tasks, incident responses |
| **Scheduled** | Time-based execution | Maintenance, reports, backups |
| **Interval** | Recurring intervals | Monitoring, health checks |

### Task Ownership

| Owner | Description | Behavior |
|-------|-------------|----------|
| **ALL** | Execute on all clients | Fan-out execution, data collection |
| **Anyone** | Execute on any available client | Load balancing, general tasks |
| **Specific** | Execute on named client | Targeted execution, specific resources |

## 🔌 Plugin Development

### Plugin Structure
```python
# plugins/my_plugin.py
def main(*args, **kwargs):
    """
    Main plugin entry point.
    
    Args:
        *args: Positional arguments from task
        **kwargs: Keyword arguments from task
    
    Returns:
        dict: Result with status and data
    """
    try:
        # Your plugin logic here
        result = perform_operation(args, kwargs)
        
        return {
            "status": "success",
            "message": "Operation completed",
            "data": result
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Operation failed: {str(e)}"
        }

def perform_operation(args, kwargs):
    # Implementation here
    pass
```

### Plugin Best Practices
- Always return a dict with 'status' key
- Use try/catch for error handling
- Log important operations
- Keep plugins focused and simple
- Document expected arguments

## ⚙️ Configuration

### Server Configuration
```python
# octopus_server/config.py
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
CLIENT_TIMEOUT = 30
HEARTBEAT_CLEANUP_INTERVAL = 60
LOG_LEVEL = "INFO"
```

### Client Configuration
```python
# octopus_client/config.py
SERVER_URL = "http://localhost:8000"
HEARTBEAT_INTERVAL = 10
TASK_CHECK_INTERVAL = 5
MAX_RETRY_ATTEMPTS = 3
```

### Environment Variables
Override any config value using environment variables:
```bash
export OCTOPUS_SERVER_HOST=192.168.1.100
export OCTOPUS_SERVER_PORT=9000
export OCTOPUS_LOG_LEVEL=DEBUG
```

## 📊 Monitoring & Debugging

### Dashboard Tabs
- **Tasks** - View, create, edit, and delete tasks
- **Executions** - Monitor task execution history
- **Clients** - Track connected clients and their status

### Client Status Management

The system tracks client availability in real-time and manages task assignments based on client status:

| Client Status | Heartbeat Age | Task Assignment | UI Display |
|---------------|---------------|-----------------|------------|
| **Online** | < 60 seconds | ✅ **Receives tasks** | Green, "Online" |
| **Idle** | 1-5 minutes | ❌ **No task assignment** | Orange, "Idle" |
| **Offline** | > 5 minutes | ❌ **No task assignment** | Gray, "Offline" |

#### Status Behavior:
- **Online Clients**: Actively connected and ready to receive new task assignments
- **Idle Clients**: Recently active but may be temporarily disconnected or executing long-running tasks
- **Offline Clients**: Considered unavailable and will not receive new task assignments

#### Task Assignment Rules:
- Tasks are **only assigned to Online clients** (heartbeat within 60 seconds)
- **Idle and Offline clients are skipped** during task assignment to prevent failed executions
- Clients automatically return to Online status when they resume sending heartbeats

### Log Files
```bash
# Server logs
tail -f octopus_server/logs/server.log

# Client logs
tail -f octopus_client/logs/client.log
```

### Database Access
```bash
# Direct database access
sqlite3 octopus_server/octopus.db

# View tasks
sqlite3 octopus_server/octopus.db "SELECT * FROM tasks;"

# View executions
sqlite3 octopus_server/octopus.db "SELECT * FROM executions;"
```

## 🛠️ Development

### Project Structure (Improved)
```
octopus/
├── constants.py           # Shared constants
├── requirements.txt      # Dependencies
├── README.md            # This file
├── ARCHITECTURE.md      # Detailed architecture guide
│
├── octopus_server/      # Server application
│   ├── config.py        # Server configuration
│   ├── main.py         # Flask application
│   ├── dbhelper.py     # Database operations
│   ├── heartbeat.py    # Client heartbeat handling
│   ├── pluginhelper.py # Plugin management
│   ├── cache.py        # Caching system
│   ├── utils.py        # Server utilities
│   ├── templates/      # HTML templates
│   ├── plugins/        # Server plugins
│   └── logs/          # Server logs
│
└── octopus_client/     # Client application
    ├── config.py       # Client configuration
    ├── main.py        # Client main loop
    ├── taskmanager.py # Task management
    ├── heartbeat.py   # Heartbeat service
    ├── pluginhelper.py # Plugin sync
    ├── utils.py       # Client utilities
    ├── plugins/       # Client plugins
    └── logs/         # Client logs
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## 🚨 Troubleshooting

### Common Issues

#### Tasks Not Being Executed
1. Check client connectivity: `grep "heartbeat" logs/server.log`
2. Verify plugin exists: `ls octopus_client/plugins/`
3. Check task assignment: `grep "Task assignment" logs/server.log`

#### Dashboard Not Showing Results
1. Check execution records: `sqlite3 octopus.db "SELECT * FROM executions;"`
2. Verify client reporting: `grep "execution result" logs/client.log`
3. Check server processing: `grep "Adding execution result" logs/server.log`

#### Connection Issues
1. Verify server is running: `netstat -an | grep :8000`
2. Check firewall settings
3. Verify client configuration: `cat octopus_client/config.py`

### Debug Mode
Enable detailed logging:
```python
# In config.py
LOG_LEVEL = "DEBUG"
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system documentation
- **Issues**: Create an issue for bug reports or feature requests
- **Questions**: Check the troubleshooting section or logs for debugging

---

**Built with ❤️ for distributed task orchestration** 🐙
