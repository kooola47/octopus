# 📋 Task Model Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Task Types](#task-types)
- [Task Status](#task-status)
- [Task Assignment](#task-assignment)
- [Scheduling](#scheduling)
- [Related Documentation](#related-documentation)

---

## 🏁 Overview

The Task Model is responsible for managing all aspects of tasks in the Octopus system. It handles task creation, assignment, execution tracking, and lifecycle management.

### Key Responsibilities
- Task creation and validation
- Task assignment to clients
- Task status tracking
- Task scheduling (adhoc, scheduled, recurring)
- Task cleanup and maintenance

### Related Files
- `models/task_model.py` - Main model implementation
- `dbhelper.py` - Database operations
- `routes/modern_routes.py` - Task-related API endpoints
- `constants.py` - Task status and type constants

---

## 🗄️ Database Schema

The tasks table stores all task-related information:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    plugin TEXT NOT NULL,
    action TEXT NOT NULL DEFAULT 'run',
    args TEXT DEFAULT '[]',
    kwargs TEXT DEFAULT '{}',
    type TEXT DEFAULT 'Adhoc',
    execution_start_time TEXT,
    execution_end_time TEXT,
    interval TEXT,
    status TEXT DEFAULT 'Created',
    executor TEXT DEFAULT '',
    result TEXT DEFAULT '',
    created_at REAL,
    updated_at REAL
)
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT (Primary Key) | Unique task identifier |
| owner | TEXT | Task owner (ALL, Anyone, specific user) |
| plugin | TEXT | Plugin name to execute |
| action | TEXT | Action to perform (default: 'run') |
| args | TEXT | JSON array of positional arguments |
| kwargs | TEXT | JSON object of keyword arguments |
| type | TEXT | Task type (Adhoc, Scheduled, Recurring) |
| execution_start_time | TEXT | Scheduled start time |
| execution_end_time | TEXT | Scheduled end time |
| interval | TEXT | Execution interval for recurring tasks |
| status | TEXT | Current task status |
| executor | TEXT | Assigned client for execution |
| result | TEXT | Task execution result |
| created_at | REAL | Creation timestamp |
| updated_at | REAL | Last update timestamp |

### Indexes

- `idx_tasks_status` - For status-based queries
- `idx_tasks_owner` - For owner-based queries

---

## 🎯 Task Types

The system supports several task types:

### Adhoc Tasks
- Execute once immediately
- Can be assigned to ALL clients, Anyone, or specific users
- Complete when executed successfully

### Scheduled Tasks
- Execute within a specific time window
- Have defined start and end times
- Complete when the execution window ends

### Recurring Tasks
- Execute at regular intervals
- Defined by an interval parameter
- Continue until manually stopped or end time reached

---

## 📊 Task Status

Task status follows a defined lifecycle:

### Primary States
- **Created** - Task has been created but not yet assigned
- **Active** - Task is assigned and ready for execution
- **Completed** - Task has been successfully executed
- **Failed** - Task execution failed

### Status Transitions
```
Created → Active → Completed/Failed
```

### Status Management
Status transitions are managed automatically based on:
- Task assignment
- Execution results
- Time constraints
- System events

---

## 🎯 Task Assignment

Tasks are assigned to clients based on their owner field:

### Assignment Types
1. **ALL** - Assigned to all connected clients
2. **Anyone** - Assigned to a random available client
3. **Specific User** - Assigned to a specific client/user

### Assignment Logic
- Tasks are assigned by the server when clients check in
- Assignment considers client availability and capabilities
- Tasks remain unassigned until suitable clients connect

### Assignment Process
1. Server evaluates unassigned tasks
2. Matches tasks with available clients
3. Updates task status to Active
4. Clients receive assigned tasks on next check-in

---

## ⏰ Scheduling

The system supports time-based task execution:

### Scheduled Tasks
- Define execution start and end times
- Execute within the specified window
- Automatically complete after end time

### Recurring Tasks
- Execute at regular intervals
- Continue until manually stopped
- Support complex scheduling patterns

### Time Management
- All times stored as timestamps
- Support for time zones (planned)
- Automatic cleanup of expired tasks

---

## 📚 Related Documentation

### Internal Documentation
- [STATUS_MANAGEMENT.md](../STATUS_MANAGEMENT.md) - Detailed status management
- [SCHEDULE_INTERVAL_FIX.md](../SCHEDULE_INTERVAL_FIX.md) - Scheduling fixes
- [TASK_LIFECYCLE.md](#) - Task lifecycle documentation (planned)

### External Resources
- [Dashboard Documentation](dashboard.md) - Web interface for tasks
- [API Documentation](api.md) - RESTful endpoints for tasks
- [Client Documentation](client.md) - How clients execute tasks