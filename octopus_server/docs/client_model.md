# 💻 Client Model Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Client Registration](#client-registration)
- [Heartbeat System](#heartbeat-system)
- [Client Status](#client-status)
- [Client Capabilities](#client-capabilities)
- [Related Documentation](#related-documentation)

---

## 🏁 Overview

The Client Model manages all aspects of client agents in the Octopus system. It handles client registration, status tracking, heartbeat monitoring, and capability management.

### Key Responsibilities
- Client registration and identification
- Heartbeat monitoring and status updates
- Client capability tracking
- Online/offline status management
- Client metadata storage

### Related Files
- `models/client_model.py` - Main model implementation
- `heartbeat.py` - Heartbeat handling
- `routes/modern_routes.py` - Client-related API endpoints
- `constants.py` - Client status constants

---

## 🗄️ Database Schema

The clients table stores all client-related information:

```sql
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT UNIQUE NOT NULL,
    hostname TEXT NOT NULL,
    ip_address TEXT,
    username TEXT,
    status TEXT DEFAULT 'active',
    last_heartbeat REAL,
    version TEXT,
    platform TEXT,
    capabilities TEXT DEFAULT '[]',
    created_at REAL,
    updated_at REAL
)
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER (Primary Key) | Internal client record ID |
| client_id | TEXT (Unique) | Unique client identifier |
| hostname | TEXT | Client machine hostname |
| ip_address | TEXT | Client IP address |
| username | TEXT | Username associated with client |
| status | TEXT | Client status (active, inactive, offline) |
| last_heartbeat | REAL | Timestamp of last heartbeat |
| version | TEXT | Client software version |
| platform | TEXT | Client platform information |
| capabilities | TEXT | JSON array of client capabilities |
| created_at | REAL | Registration timestamp |
| updated_at | REAL | Last update timestamp |

### Indexes

- `idx_clients_client_id` - For client ID lookups
- `idx_clients_status` - For status-based queries
- `idx_clients_last_heartbeat` - For heartbeat-based queries
- `idx_clients_hostname` - For hostname-based queries

---

## 📝 Client Registration

Clients register with the server when they first connect:

### Registration Process
1. Client sends registration request with metadata
2. Server creates or updates client record
3. Client receives unique client_id
4. Client begins sending heartbeats

### Required Information
- Hostname
- IP address
- Username
- Version information
- Platform details

### Optional Information
- Capabilities list
- Custom metadata

### Registration Validation
- Duplicate client detection
- Data validation
- Status initialization

---

## 💓 Heartbeat System

The heartbeat system monitors client connectivity:

### Heartbeat Mechanism
- Clients send periodic heartbeat messages
- Server updates last_heartbeat timestamp
- Missed heartbeats trigger status changes

### Heartbeat Interval
- Configurable via `CLIENT_TIMEOUT` setting
- Default: 30 seconds
- Server considers client offline after 2 missed heartbeats

### Heartbeat Processing
- Timestamp validation
- Client status updates
- Online/offline transition handling

### Heartbeat Data
- Client status information
- System metrics (future enhancement)
- Task execution updates

---

## 📊 Client Status

Client status indicates current connectivity and availability:

### Status Values
- **Active** - Client is online and available
- **Inactive** - Client is registered but administratively disabled
- **Offline** - Client has not sent heartbeat within timeout period

### Status Transitions
```
Active ↔ Offline (automatic)
Active ↔ Inactive (administrative)
```

### Status Management
- Automatic transitions based on heartbeat timing
- Administrative controls for manual status changes
- Dashboard display of current status

---

## ⚙️ Client Capabilities

Clients can advertise their capabilities:

### Capability System
- Clients report supported features
- Server uses capabilities for task assignment
- Extensible capability framework

### Common Capabilities
- Plugin support
- Platform-specific features
- Hardware capabilities
- Network configuration

### Capability Management
- JSON array storage
- Query-based capability matching
- Task assignment based on capabilities

---

## 📚 Related Documentation

### Internal Documentation
- [HEARTBEAT.md](#) - Heartbeat implementation details (planned)
- [CLIENT_MANAGEMENT.md](#) - Client management procedures (planned)

### External Resources
- [heartbeat.py](../heartbeat.py) - Heartbeat handling implementation
- [Task Model Documentation](task_model.md) - Task assignment to clients
- [Dashboard Documentation](dashboard.md) - Client status display
- [API Documentation](api.md) - RESTful endpoints for client data