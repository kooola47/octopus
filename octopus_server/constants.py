#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Constants
=============================

Centralized constants and status management for the Octopus orchestration system.
"""

class TaskStatus:
    """Task status constants"""
    # Primary states
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    
    # Legacy/Alternative names for compatibility
    CREATED = "created"
    ACTIVE = "active"
    EXECUTING = "executing"
    DONE = "done"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
    
    # Status groups
    PENDING_STATES = [PENDING, CREATED]
    RUNNING_STATES = [RUNNING, ACTIVE, EXECUTING]
    COMPLETED_STATES = [COMPLETED, DONE, SUCCESS]
    FAILED_STATES = [FAILED, ERROR, CANCELLED]
    
    # All valid statuses
    ALL_STATUSES = PENDING_STATES + RUNNING_STATES + COMPLETED_STATES + FAILED_STATES
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.PENDING
        
        status_lower = status.lower()
        
        # Map to primary states
        if status_lower in ['pending', 'created']:
            return cls.PENDING
        elif status_lower in ['running', 'active', 'executing']:
            return cls.RUNNING
        elif status_lower in ['completed', 'done', 'success']:
            return cls.COMPLETED
        elif status_lower in ['failed', 'error', 'cancelled']:
            return cls.FAILED
        else:
            return cls.PENDING
    
    @classmethod
    def get_badge_class(cls, status):
        """Get Bootstrap badge class for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.PENDING:
            return "bg-warning"
        elif normalized == cls.RUNNING:
            return "bg-primary"
        elif normalized == cls.COMPLETED:
            return "bg-success"
        elif normalized == cls.FAILED:
            return "bg-danger"
        else:
            return "bg-secondary"
    
    @classmethod
    def get_icon(cls, status):
        """Get Bootstrap icon for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.PENDING:
            return "bi-clock-history"
        elif normalized == cls.RUNNING:
            return "bi-play-circle"
        elif normalized == cls.COMPLETED:
            return "bi-check-circle"
        elif normalized == cls.FAILED:
            return "bi-exclamation-triangle"
        else:
            return "bi-question-circle"
    
    @classmethod
    def is_final_state(cls, status):
        """Check if status is a final state (no more transitions expected)"""
        normalized = cls.normalize(status)
        return normalized in [cls.COMPLETED, cls.FAILED]

class ExecutionStatus:
    """Execution status constants"""
    # Primary states
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    
    # Legacy/Alternative names
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
    
    # Status groups
    PENDING_STATES = [PENDING]
    RUNNING_STATES = [RUNNING]
    COMPLETED_STATES = [COMPLETED, SUCCESS]
    FAILED_STATES = [FAILED, ERROR, CANCELLED]
    
    # All valid statuses
    ALL_STATUSES = PENDING_STATES + RUNNING_STATES + COMPLETED_STATES + FAILED_STATES
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.PENDING
        
        status_lower = status.lower()
        
        if status_lower == 'pending':
            return cls.PENDING
        elif status_lower == 'running':
            return cls.RUNNING
        elif status_lower in ['completed', 'success']:
            return cls.COMPLETED
        elif status_lower in ['failed', 'error', 'cancelled']:
            return cls.FAILED
        else:
            return cls.PENDING
    
    @classmethod
    def get_badge_class(cls, status):
        """Get Bootstrap badge class for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.PENDING:
            return "bg-warning"
        elif normalized == cls.RUNNING:
            return "bg-primary" 
        elif normalized == cls.COMPLETED:
            return "bg-success"
        elif normalized == cls.FAILED:
            return "bg-danger"
        else:
            return "bg-secondary"
    
    @classmethod
    def get_icon(cls, status):
        """Get Bootstrap icon for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.PENDING:
            return "bi-hourglass"
        elif normalized == cls.RUNNING:
            return "bi-gear"
        elif normalized == cls.COMPLETED:
            return "bi-check-circle-fill"
        elif normalized == cls.FAILED:
            return "bi-x-circle-fill"
        else:
            return "bi-question-circle"

class UserStatus:
    """User status constants"""
    # Primary states
    ACTIVE = "active"
    INACTIVE = "inactive"
    
    # Legacy/Alternative names
    ENABLED = "enabled"
    DISABLED = "disabled"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    
    # Status groups
    ACTIVE_STATES = [ACTIVE, ENABLED]
    INACTIVE_STATES = [INACTIVE, DISABLED, LOCKED, SUSPENDED]
    
    # All valid statuses
    ALL_STATUSES = ACTIVE_STATES + INACTIVE_STATES
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.ACTIVE
        
        status_lower = status.lower()
        
        if status_lower in ['active', 'enabled']:
            return cls.ACTIVE
        elif status_lower in ['inactive', 'disabled', 'locked', 'suspended']:
            return cls.INACTIVE
        else:
            return cls.ACTIVE
    
    @classmethod
    def get_badge_class(cls, status):
        """Get Bootstrap badge class for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.ACTIVE:
            return "bg-success"
        elif normalized == cls.INACTIVE:
            return "bg-secondary"
        else:
            return "bg-warning"
    
    @classmethod
    def get_icon(cls, status):
        """Get Bootstrap icon for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.ACTIVE:
            return "bi-person-check"
        elif normalized == cls.INACTIVE:
            return "bi-person-x"
        else:
            return "bi-person-dash"

class ClientStatus:
    """Client status constants"""
    # Primary states
    ONLINE = "online"
    OFFLINE = "offline"
    
    # Extended states
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    
    # Status groups
    ONLINE_STATES = [ONLINE, CONNECTED, IDLE, BUSY]
    OFFLINE_STATES = [OFFLINE, DISCONNECTED, ERROR]
    
    # All valid statuses
    ALL_STATUSES = ONLINE_STATES + OFFLINE_STATES
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.OFFLINE
        status_lower = status.lower()
        # Map to primary states
        if status_lower in ['online', 'connected', 'idle', 'busy']:
            return cls.ONLINE
        elif status_lower in ['offline', 'disconnected', 'error']:
            return cls.OFFLINE
        else:
            return cls.OFFLINE

    
    @classmethod
    def get_icon(cls, status):
        """Get Bootstrap icon for status"""
        if not status:
            return "bi-circle"
            
        status_lower = status.lower()
        
        if status_lower in ['online', 'connected']:
            return "bi-circle-fill text-success"
        elif status_lower == 'idle':
            return "bi-circle-fill text-info"
        elif status_lower == 'busy':
            return "bi-circle-fill text-warning"
        elif status_lower in ['offline', 'disconnected']:
            return "bi-circle text-secondary"
        elif status_lower == 'error':
            return "bi-circle-fill text-danger"
        else:
            return "bi-circle"

class UserRole:
    """User role constants"""
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"
    VIEWER = "viewer"
    
    ALL_ROLES = [ADMIN, OPERATOR, USER, VIEWER]
    
    @classmethod
    def get_badge_class(cls, role):
        """Get Bootstrap badge class for role"""
        if role == cls.ADMIN:
            return "bg-danger"
        elif role == cls.OPERATOR:
            return "bg-warning"
        elif role == cls.USER:
            return "bg-primary"
        elif role == cls.VIEWER:
            return "bg-info"
        else:
            return "bg-secondary"
    
    @classmethod
    def get_icon(cls, role):
        """Get Bootstrap icon for role"""
        if role == cls.ADMIN:
            return "bi-shield-fill-check"
        elif role == cls.OPERATOR:
            return "bi-gear-fill"
        elif role == cls.USER:
            return "bi-person-fill"
        elif role == cls.VIEWER:
            return "bi-eye-fill"
        else:
            return "bi-person"

class TaskOwnership:
    """Task ownership constants"""
    ALL = "ALL"
    ANYONE = "Anyone"
    SPECIFIC = "Specific"

class TaskType:
    """Task type constants"""
    ADHOC = "Adhoc"
    SCHEDULED = "Scheduled"
    INTERVAL = "Interval"
    RECURRING = "Recurring"
    ONE_TIME = "OneTime"
    ERROR = "error"

class Database:
    """Database related constants"""
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    CONNECTION_POOL_SIZE = 10
