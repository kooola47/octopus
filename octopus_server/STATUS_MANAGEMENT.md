# 🎯 Centralized Status Management System

This document explains how to use the centralized status management system for consistent status handling across Tasks, Executions, Users, and Clients.

## 📁 File Structure

```
octopus_server/
├── constants.py          # Status definitions and utility functions
├── template_helpers.py   # Jinja2 template filters and context processors
└── main.py              # Registers template helpers
```

## 🎨 Status Classes Available

### TaskStatus
- **Primary States**: pending, running, completed, failed
- **Legacy Support**: created, active, executing, done, success, error, cancelled
- **Features**: Status normalization, badge classes, icons

### ExecutionStatus  
- **Primary States**: pending, running, completed, failed
- **Legacy Support**: success, error, cancelled
- **Features**: Status normalization, badge classes, icons

### UserStatus
- **Primary States**: active, inactive
- **Legacy Support**: enabled, disabled, locked, suspended
- **Features**: Status normalization, badge classes, icons

### ClientStatus
- **Primary States**: online, offline
- **Extended States**: connected, disconnected, idle, busy, error
- **Features**: Status normalization, badge classes, icons

### UserRole
- **Available Roles**: admin, operator, user, viewer
- **Features**: Badge classes, icons

## 🔧 Backend Usage

### Python Code Examples

```python
from constants import TaskStatus, UserStatus, ClientStatus

# Normalize status from any format
normalized_status = TaskStatus.normalize("Done")  # Returns "completed"
normalized_status = TaskStatus.normalize("running")  # Returns "running"

# Check if status is final
is_final = TaskStatus.is_final_state("completed")  # Returns True

# Get badge class for UI
badge_class = TaskStatus.get_badge_class("running")  # Returns "bg-primary"

# Get icon for UI
icon_class = TaskStatus.get_icon("failed")  # Returns "bi-exclamation-triangle"

# Statistics calculation example
def get_task_stats():
    tasks = get_tasks()
    stats = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
    
    for task in tasks:
        normalized = TaskStatus.normalize(task.get('status'))
        stats[normalized] += 1
    
    return stats
```

### Database Integration

```python
# When updating task status
def update_task_status(task_id, new_status):
    normalized_status = TaskStatus.normalize(new_status)
    # Save normalized_status to database
    update_task(task_id, status=normalized_status)
```

## 🖼️ Template Usage

### Available Template Filters

```html
<!-- Task Status -->
{{ task.status|task_status_badge }}        <!-- Returns: bg-primary, bg-success, etc. -->
{{ task.status|task_status_icon }}         <!-- Returns: bi-play-circle, bi-check-circle, etc. -->
{{ task.status|task_status_normalize }}    <!-- Returns: normalized status string -->

<!-- Execution Status -->
{{ execution.status|execution_status_badge }}
{{ execution.status|execution_status_icon }}

<!-- User Status -->
{{ user.status|user_status_badge }}
{{ user.status|user_status_icon }}

<!-- Client Status -->
{{ client.status|client_status_badge }}
{{ client.status|client_status_icon }}

<!-- User Role -->
{{ user.role|user_role_badge }}
{{ user.role|user_role_icon }}
```

### Template Examples

#### Before (Hard-coded):
```html
<span class="badge {% if task.status == 'completed' or task.status == 'Done' %}bg-success{% elif task.status == 'failed' %}bg-danger{% elif task.status == 'running' %}bg-primary{% else %}bg-warning{% endif %}">
    {% if task.status == 'Done' %}Completed{% else %}{{ task.status|title or 'Pending' }}{% endif %}
</span>
```

#### After (Centralized):
```html
<span class="badge {{ task.status|task_status_badge }}">
    <i class="{{ task.status|task_status_icon }} me-1"></i>
    {{ task.status|task_status_normalize|title }}
</span>
```

#### User Role and Status:
```html
<!-- Role Badge -->
<span class="badge {{ user.role|user_role_badge }}">
    <i class="{{ user.role|user_role_icon }} me-1"></i>
    {{ user.role|title }}
</span>

<!-- Status Badge -->
<span class="badge {{ user.status|user_status_badge }}">
    <i class="{{ user.status|user_status_icon }} me-1"></i>
    {{ user.status|title }}
</span>
```

#### Client Status:
```html
<span class="badge {{ client.status|client_status_badge }}">
    <i class="{{ client.status|client_status_icon }} me-1"></i>
    {{ client.status|title }}
</span>
```

## 🔍 JavaScript Filtering

### Before (Complex Logic):
```javascript
function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
    
    rows.forEach(row => {
        const status = row.querySelector('.badge').textContent.toLowerCase().trim();
        let statusMatch = true;
        
        if (statusFilter) {
            switch (statusFilter) {
                case 'pending':
                    statusMatch = status === 'pending';
                    break;
                case 'running':
                    statusMatch = status === 'running';
                    break;
                case 'completed':
                    statusMatch = status === 'completed' || status === 'done';
                    break;
                // ... more cases
            }
        }
        
        row.style.display = statusMatch ? '' : 'none';
    });
}
```

### After (Simplified):
```javascript
function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
    
    rows.forEach(row => {
        const status = row.querySelector('.badge').textContent.toLowerCase().trim();
        const statusMatch = !statusFilter || status === statusFilter;
        row.style.display = statusMatch ? '' : 'none';
    });
}
```

## ✅ Benefits

1. **Consistency**: All status displays use the same styling and logic
2. **Maintainability**: Change status colors/icons in one place
3. **Flexibility**: Easy to add new statuses or modify existing ones
4. **Backwards Compatibility**: Supports legacy status values
5. **Type Safety**: Centralized status validation
6. **Reduced Code**: Less template code, fewer conditional statements

## 🚀 Adding New Status Types

### Step 1: Add to constants.py
```python
class NewEntityStatus:
    # Primary states
    STATE1 = "state1"
    STATE2 = "state2"
    
    @classmethod
    def normalize(cls, status):
        # Implementation
        pass
    
    @classmethod
    def get_badge_class(cls, status):
        # Implementation
        pass
    
    @classmethod
    def get_icon(cls, status):
        # Implementation
        pass
```

### Step 2: Add to template_helpers.py
```python
@app.template_filter('new_entity_status_badge')
def new_entity_status_badge(status):
    return NewEntityStatus.get_badge_class(status)

@app.template_filter('new_entity_status_icon')
def new_entity_status_icon(status):
    return NewEntityStatus.get_icon(status)
```

### Step 3: Use in templates
```html
<span class="badge {{ entity.status|new_entity_status_badge }}">
    <i class="{{ entity.status|new_entity_status_icon }} me-1"></i>
    {{ entity.status|title }}
</span>
```

## 🎨 Available Badge Classes

- `bg-primary` - Blue (Running/Active)
- `bg-success` - Green (Completed/Active)
- `bg-warning` - Yellow (Pending/Warning)
- `bg-danger` - Red (Failed/Error)
- `bg-info` - Light Blue (Info/Idle)
- `bg-secondary` - Gray (Inactive/Disabled)

## 🎯 Available Icons

- `bi-clock-history` - Pending
- `bi-play-circle` - Running
- `bi-check-circle` - Completed
- `bi-exclamation-triangle` - Failed
- `bi-person-check` - Active User
- `bi-shield-fill-check` - Admin
- `bi-circle-fill` - Online Client
- And many more...
