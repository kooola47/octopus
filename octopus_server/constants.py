#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Constants
=============================

Centralized constants and status management for the Octopus orchestration system.
"""

class TaskStatus:
    """Task status constants"""
    # Primary states - only these 5 statuses allowed
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    # Status groups
    PENDING_STATES = [PENDING]
    RUNNING_STATES = [RUNNING]
    COMPLETED_STATES = [COMPLETED]
    FAILED_STATES = [FAILED]
    CANCELLED_STATES = [CANCELLED]
    
    # All valid statuses
    ALL_STATUSES = [PENDING, RUNNING, COMPLETED, FAILED, CANCELLED]
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.PENDING
        
        status_lower = status.lower()
        
        # Map various inputs to the 5 allowed statuses
        if status_lower in ['pending', 'created', 'queued', 'waiting']:
            return cls.PENDING
        elif status_lower in ['running', 'active', 'executing', 'in_progress']:
            return cls.RUNNING
        elif status_lower in ['completed', 'done', 'success', 'successful', 'finished']:
            return cls.COMPLETED
        elif status_lower in ['cancelled', 'canceled', 'aborted', 'stopped']:
            return cls.CANCELLED
        elif status_lower in ['failed', 'error', 'failure', 'exception']:
            return cls.FAILED
        else:
            return cls.PENDING  # Default fallback
    
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
        elif normalized == cls.CANCELLED:
            return "bg-secondary"
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
        elif normalized == cls.CANCELLED:
            return "bi-stop-circle"
        else:
            return "bi-question-circle"
    
    @classmethod
    def is_final_state(cls, status):
        """Check if status is a final state (no more transitions expected)"""
        normalized = cls.normalize(status)
        return normalized in [cls.COMPLETED, cls.FAILED, cls.CANCELLED]

class ExecutionStatus:
    """Execution status constants"""
    # Primary states - only these 4 statuses allowed
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"
    CANCELLED = "cancelled"
    
    # Status groups
    RUNNING_STATES = [RUNNING]
    SUCCESS_STATES = [SUCCESS]
    FAILED_STATES = [FAILED]
    CANCELLED_STATES = [CANCELLED]
    
    # All valid statuses
    ALL_STATUSES = [RUNNING, FAILED, SUCCESS, CANCELLED]
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.FAILED  # Default to failed if no status provided
        
        status_lower = status.lower()
        
        # Map various inputs to the 4 allowed statuses
        if status_lower in ['running', 'active', 'executing', 'in_progress']:
            return cls.RUNNING
        elif status_lower in ['success', 'completed', 'done', 'successful']:
            return cls.SUCCESS
        elif status_lower in ['cancelled', 'canceled', 'aborted', 'stopped']:
            return cls.CANCELLED
        elif status_lower in ['failed', 'error', 'failure', 'exception']:
            return cls.FAILED
        else:
            return cls.FAILED  # Default fallback
    
    @classmethod
    def get_badge_class(cls, status):
        """Get Bootstrap badge class for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.RUNNING:
            return "bg-primary"
        elif normalized == cls.SUCCESS:
            return "bg-success"
        elif normalized == cls.FAILED:
            return "bg-danger"
        elif normalized == cls.CANCELLED:
            return "bg-secondary"
        else:
            return "bg-secondary"
    
    @classmethod
    def get_icon(cls, status):
        """Get Bootstrap icon for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.RUNNING:
            return "bi-gear"
        elif normalized == cls.SUCCESS:
            return "bi-check-circle-fill"
        elif normalized == cls.FAILED:
            return "bi-x-circle-fill"
        elif normalized == cls.CANCELLED:
            return "bi-stop-circle-fill"
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
    # Primary states - only these 3 statuses allowed
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    
    # Status groups
    ONLINE_STATES = [ONLINE]
    OFFLINE_STATES = [OFFLINE]
    BUSY_STATES = [BUSY]
    
    # All valid statuses
    ALL_STATUSES = [ONLINE, OFFLINE, BUSY]
    
    @classmethod
    def normalize(cls, status):
        """Normalize status to standard format"""
        if not status:
            return cls.OFFLINE
        
        status_lower = status.lower()
        
        # Map various inputs to the 3 allowed statuses
        if status_lower in ['online', 'connected', 'idle', 'available']:
            return cls.ONLINE
        elif status_lower in ['busy', 'executing', 'working', 'running']:
            return cls.BUSY
        elif status_lower in ['offline', 'disconnected', 'error', 'inactive']:
            return cls.OFFLINE
        else:
            return cls.OFFLINE  # Default fallback

    
    @classmethod
    def get_icon(cls, status):
        """Get Bootstrap icon for status"""
        normalized = cls.normalize(status)
        
        if normalized == cls.ONLINE:
            return "bi-circle-fill text-success"
        elif normalized == cls.BUSY:
            return "bi-circle-fill text-warning"
        elif normalized == cls.OFFLINE:
            return "bi-circle text-secondary"
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
