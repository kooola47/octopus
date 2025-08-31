# 🐙 OCTOPUS SYSTEM DOCUMENTATION

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Core Models](#core-models)
  - [Task Model](#task-model)
  - [Execution Model](#execution-model)
  - [Client Model](#client-model)
  - [User Model](#user-model)
  - [Plugin Model](#plugin-model)
- [System Components](#system-components)
  - [Configuration Management](#configuration-management)
  - [Database Schema](#database-schema)
  - [API Endpoints](#api-endpoints)
  - [Web Dashboard](#web-dashboard)
- [Deployment & Maintenance](#deployment--maintenance)
  - [Installation](#installation)
  - [Deployment](#deployment)
  - [Maintenance Tasks](#maintenance-tasks)
- [Advanced Features](#advanced-features)
  - [Performance Optimizations](#performance-optimizations)
  - [Caching System](#caching-system)
  - [NLP Processing](#nlp-processing)
  - [Security](#security)

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

## 🧠 Core Models

The Octopus system is organized around several core models that represent the main entities in the system.

### Task Model

The Task Model manages task creation, assignment, and lifecycle.

**Key Features:**
- Task creation and management
- Task assignment to clients
- Task scheduling (adhoc, scheduled, recurring)
- Task status tracking

**Related Documentation:**
- [Task Lifecycle](#task-lifecycle)
- [Scheduling](#scheduling)

### Execution Model

The Execution Model tracks task execution records across all clients.

**Key Features:**
- Execution record creation
- Execution status tracking
- Result collection and storage
- Performance metrics

**Related Documentation:**
- [Execution Records Fix](#execution-records-fix)
- [Unique Execution IDs](#unique-execution-ids)

### Client Model

The Client Model manages connected client agents and their status.

**Key Features:**
- Client registration and tracking
- Heartbeat monitoring
- Client capability management
- Online/offline status

**Related Documentation:**
- [Heartbeat Service](#heartbeat-service)
- [Client Management](#client-management)

### User Model

The User Model handles user authentication, authorization, and profiles.

**Key Features:**
- User authentication and password management
- Role-based access control (RBAC)
- User profile management
- Session handling

**Related Documentation:**
- [User Profile Guide](#user-profile-guide)
- [Security Implementation](#security-implementation)

### Plugin Model

The Plugin Model manages plugins that define the actual tasks to be executed.

**Key Features:**
- Plugin discovery and registration
- Plugin metadata management
- Plugin versioning
- Plugin distribution

**Related Documentation:**
- [Plugin System](#plugin-system)
- [Plugin Response Specification](#plugin-response-specification)

---

## 🧩 System Components

### Configuration Management

The system uses a flexible configuration system that supports multiple environments.

**Configuration Files:**
- `config/config_base.py` - Base configuration
- `config/config_dev.py` - Development configuration
- `config/config_prod.py` - Production configuration

**Key Settings:**
- Server host and port
- Database file location
- Cache settings
- Plugin directory
- Logging configuration

### Database Schema

The system uses SQLite for data persistence with the following main tables:

1. **Tasks** - Stores task definitions and status
2. **Executions** - Tracks task execution records
3. **Clients** - Manages connected clients
4. **Users** - Handles user accounts and authentication
5. **Plugins** - Manages plugin metadata

### API Endpoints

The system provides a RESTful API for programmatic access:

- `/tasks` - Task management
- `/executions` - Execution tracking
- `/clients` - Client status
- `/users` - User management
- `/plugins` - Plugin operations
- `/heartbeat` - Client heartbeat

### Web Dashboard

The web dashboard provides a user-friendly interface for:

- Task creation and monitoring
- Client status visualization
- Execution result tracking
- User management
- Plugin management

---

## 🚀 Deployment & Maintenance

### Installation

**Prerequisites:**
- Python 3.7+
- SQLite3
- Flask and dependencies

**Installation Steps:**
1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Configure environment settings
4. Start the server with `python main.py`

### Deployment

The system supports multiple deployment methods:

- **Manual deployment** - Direct installation on target systems
- **PowerShell scripts** - Automated Windows deployment
- **Docker** - Containerized deployment (planned)

### Maintenance Tasks

Regular maintenance tasks include:

- Database cleanup
- Log rotation
- Cache invalidation
- Plugin updates

---

## ⚡ Advanced Features

### Performance Optimizations

The system implements several performance optimizations:

- Database indexing
- In-memory caching
- Connection pooling
- Efficient query patterns

### Caching System

A multi-layer caching system improves response times:

- Global cache for frequently accessed data
- Session-based caching
- Plugin metadata caching

### NLP Processing

Natural Language Processing capabilities allow:

- Task creation through natural language
- Intent recognition
- Parameter extraction

### Security

Security features include:

- User authentication
- Role-based access control
- Secure session management
- Input validation