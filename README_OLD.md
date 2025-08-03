# 🐙 Octopus - Distributed Task Orchestration System

Octopus is a distributed task orchestration system designed for Business-as-Usual (BAU) operations. It consists of a central server that manages and distributes tasks to multiple client agents deployed across different user PCs.

## 🏗️ Architecture

- **Server** (`octopus_server`): Central Flask-based orchestrator deployed on server infrastructure
  - Manages task creation, scheduling, and monitoring
  - Provides web dashboard for administration
  - Hosts plugins that are automatically distributed to clients
  - Tracks client connectivity and task execution status

- **Client** (`octopus_client`): Lightweight agent deployed on user PCs
  - Automatically pulls plugins from server
  - Executes assigned tasks based on ownership rules
  - Reports execution status back to server
  - Sends heartbeat signals to maintain connectivity

- **Plugins**: Modular task implementations that define business logic
  - Created on server side
  - Automatically synchronized to all connected clients
  - Support both synchronous and asynchronous execution patterns

## 🚀 Features

### Server Features
- **Web Dashboard**: Monitor connected clients, create/manage tasks, view execution results
- **Plugin Management**: Create plugins that auto-sync to all clients
- **Task Orchestration**: Create scheduled and ad-hoc tasks with flexible ownership models
- **Client Monitoring**: Real-time view of connected clients and their status
- **Execution Tracking**: Monitor task execution across distributed clients

### Client Features
- **Auto Plugin Sync**: Automatically downloads and updates plugins from server
- **Task Execution**: Executes assigned tasks based on ownership rules
- **Heartbeat Monitoring**: Maintains connection status with server
- **BAU Operations**: Designed for Business-as-Usual operational tasks

### Task Management
- **Ownership Models**:
  - `ALL`: Every connected client executes the task
  - `Anyone`: Server randomly selects one active client to execute
  - `Specific User`: Only the specified user's client executes the task
- **Task Types**:
  - `Scheduled`: Recurring tasks with start/end times and intervals
  - `Ad-hoc`: One-time execution tasks
- **Status Tracking**: 
  - `Created`: Task created but not yet assigned
  - `Active`: Task assigned and being executed
  - `Completed`: Task execution finished

## 📦 Installation & Deployment

### Prerequisites
- Python 3.7+
- SQLite (included with Python)
- Network connectivity between server and client machines

### Server Deployment (Central Infrastructure)
```bash
# Clone or copy octopus_server to your server
cd octopus_server
pip install -r ../requirements.txt
python main.py
```
Server will be available at: `http://server-ip:8000/dashboard`

### Client Deployment (User PCs)
```bash
# Deploy octopus_client to each user PC
cd octopus_client
pip install -r ../requirements.txt

# Edit config.py to point to your server
# SERVER_URL = "http://your-server-ip:8000"

python main.py
```

⚠️ **Note**: Since we removed duplicate `requirements.txt` files, use the main project `requirements.txt` file for installation.

### Configuration
- **Server**: Edit `octopus_server/config.py` for server settings
- **Client**: Edit `octopus_client/config.py` to point to your server URL

## 🌐 Usage Workflow

### 1. Start the Server
```bash
python octopus_server/main.py
```

### 2. Access the Web Dashboard
Navigate to: `http://server-ip:8000/dashboard`

### 3. Deploy Clients to User PCs
- Install octopus_client on each user PC
- Configure `SERVER_URL` in client config
- Start the client: `python octopus_client/main.py`

### 4. Monitor Connected Clients
- View connected clients in the dashboard
- Monitor heartbeat status and connectivity

### 5. Create and Manage Tasks
- **Create Plugins**: Add Python files to `octopus_server/plugins/`
- **Create Tasks**: Use the web interface to create scheduled or ad-hoc tasks
- **Set Ownership**: Choose `ALL`, `Anyone`, or specific user
- **Monitor Execution**: Track task status and results in real-time

### 6. Task Execution Flow
1. **Created**: Task is created in the system
2. **Active**: Task is assigned to client(s) based on ownership rules
3. **Completed**: Task execution finished, results available

## 📁 Project Structure

```
octopus/
├── README.md                    # Project documentation
├── requirements.txt            # Unified dependencies
├── .gitignore                  # Git ignore rules
├── CLEANUP_PLAN.md            # Refactoring roadmap
├── 
├── octopus_server/            # Central Server (Deploy to Infrastructure)
│   ├── main.py               # Flask server entry point
│   ├── config.py             # Server configuration
│   ├── dbhelper.py           # Database operations & task management
│   ├── heartbeat.py          # Client heartbeat handling
│   ├── pluginhelper.py       # Plugin distribution to clients
│   ├── cache.py              # Server-side caching
│   ├── scheduler.py          # Task scheduling logic
│   ├── octopus.db           # SQLite database (created on first run)
│   ├── templates/           # Web dashboard templates
│   │   ├── dashboard_template.html
│   │   ├── dashboard_clients.html
│   │   ├── dashboard_tasks.html
│   │   └── dashboard_executions.html
│   ├── plugins/             # Server plugins (auto-synced to clients)
│   │   └── create_incident.py
│   └── logs/                # Server logs
│       └── server.log
├── 
├── octopus_client/           # Client Agent (Deploy to User PCs)
│   ├── main.py              # Client entry point
│   ├── config.py            # Client configuration (set SERVER_URL)
│   ├── taskmanager.py       # Task execution management
│   ├── heartbeat.py         # Heartbeat sender
│   ├── pluginhelper.py      # Plugin sync from server
│   ├── cache.py             # Client-side caching
│   ├── scheduler.py         # Client scheduling
│   ├── plugins/             # Downloaded plugins (auto-synced)
│   │   └── create_incident.py
│   └── logs/                # Client logs
│       └── client.log
└── 
└── common/                   # Shared utilities (created during cleanup)
    └── __init__.py
```

### Key Components

**Server Components:**
- `main.py`: Web dashboard and API endpoints
- `dbhelper.py`: Task and execution database operations
- `pluginhelper.py`: Plugin file distribution to clients

**Client Components:**
- `main.py`: Task execution engine and server communication
- `taskmanager.py`: Server API communication for tasks
- `pluginhelper.py`: Plugin synchronization from server

## 🔧 Configuration

### Server Configuration (`octopus_server/config.py`)
```python
SERVER_HOST = "0.0.0.0"          # Bind to all interfaces
SERVER_PORT = 8000               # Dashboard port
CACHE_TTL = 600                  # Cache timeout in seconds
PLUGINS_FOLDER = "./plugins"     # Plugin directory
```

### Client Configuration (`octopus_client/config.py`)
```python
SERVER_URL = "http://your-server-ip:8000"  # ⚠️ UPDATE THIS!
HEARTBEAT_INTERVAL = 10          # Heartbeat frequency (seconds)
PLUGINS_FOLDER = "./plugins"     # Local plugin cache
CACHE_TTL = 600                  # Cache timeout
```

### Network Requirements
- Clients must be able to reach server on port 8000
- HTTP/HTTPS connectivity required
- Firewall rules may need adjustment for corporate networks

## 🚀 Deployment Scenarios

### Scenario 1: Corporate BAU Operations
- **Server**: Deploy on internal infrastructure
- **Clients**: Install on employee workstations
- **Use Cases**: System maintenance, data collection, automated reporting

### Scenario 2: Distributed Monitoring
- **Server**: Central monitoring system
- **Clients**: Monitoring agents on various systems
- **Use Cases**: Health checks, log collection, performance monitoring

### Scenario 3: Batch Processing
- **Server**: Job scheduler
- **Clients**: Processing nodes
- **Use Cases**: Data processing, file operations, batch tasks

## 🧩 Creating Plugins

Plugins are created on the server and automatically distributed to all clients.

### 1. Create Plugin on Server
Create a new Python file in `octopus_server/plugins/`:

```python
# octopus_server/plugins/my_bau_task.py
import logging
import time

logger = logging.getLogger("octopus")

def run(*args, **kwargs):
    """
    Main plugin execution function
    Args and kwargs are passed from the task definition
    """
    logger.info(f"Executing BAU task with args={args}, kwargs={kwargs}")
    
    # Your business logic here
    time.sleep(2)  # Simulate work
    
    # Return result (will be stored in task execution results)
    return f"BAU task completed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}"

# Optional: Add other functions for different actions
def validate(*args, **kwargs):
    """Optional validation function"""
    return "Validation passed"
```

### 2. Plugin Auto-Sync
- Clients automatically detect new/updated plugins
- MD5 checksums ensure plugins are current
- Plugins are downloaded and loaded dynamically
- No client restart required for new plugins

### 3. Create Tasks Using Plugins
- Use the web dashboard to create tasks
- Select your plugin from the dropdown
- Set ownership (ALL/Anyone/Specific User)
- Choose scheduled or ad-hoc execution

## 📊 Task Types & Ownership Models

### Task Types
- **Scheduled Tasks**: 
  - Recurring execution with defined intervals
  - Start and end time boundaries
  - Suitable for regular BAU operations
- **Ad-hoc Tasks**: 
  - One-time execution
  - Immediate or delayed execution
  - Perfect for on-demand operations

### Ownership Models
- **ALL**: 
  - Every connected client executes the task
  - Useful for system-wide updates or checks
  - All clients report execution status independently
- **Anyone**: 
  - Server randomly selects one active client
  - First-available execution model
  - Prevents duplicate work across clients
- **Specific User**: 
  - Task assigned to a particular user's client
  - User-specific operations or personalized tasks
  - Only that user's client will execute

### Task Status Lifecycle
```
Created → Active → Completed
   ↓        ↓         ↓
Created  Assigned   Execution
in UI    to Client  Finished
```

## 🤝 Contributing

⚠️ **This project is currently undergoing major refactoring**
Please see `CLEANUP_PLAN.md` for current status and planned improvements.

## 📝 License

MIT License - see LICENSE file for details

---

**Status**: 🚧 Under active refactoring - expect breaking changes