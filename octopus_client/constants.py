# =============================================================================
# 🐙 OCTOPUS SYSTEM CONSTANTS
# =============================================================================
"""
Shared constants between Octopus Server and Client components.
This file contains all the constants that need to be consistent across
both server and client applications.
"""

# =============================================================================
# TASK STATUS CONSTANTS
# =============================================================================
class TaskStatus:
    CREATED = "Created"
    ACTIVE = "Active"
    DONE = "Done"
    SUCCESS = "success"
    FAILED = "failed"
    COMPLETED = "completed"
    
    @classmethod
    def is_completed(cls, status):
        """Check if a status indicates task completion."""
        return status in [cls.DONE, cls.SUCCESS, cls.FAILED, cls.COMPLETED]
    
    @classmethod
    def all_statuses(cls):
        """Get all possible task statuses."""
        return [cls.CREATED, cls.ACTIVE, cls.DONE, cls.SUCCESS, cls.FAILED, cls.COMPLETED]

# =============================================================================
# TASK OWNERSHIP TYPES
# =============================================================================
class TaskOwnership:
    ALL = "ALL"           # Task assigned to all clients
    ANYONE = "Anyone"     # Task assigned to any available client
    SPECIFIC = "Specific" # Task assigned to specific user/client

# =============================================================================
# TASK TYPES
# =============================================================================
class TaskType:
    ADHOC = "Adhoc"       # One-time task
    SCHEDULED = "Scheduled" # Recurring task
    INTERVAL = "Interval" # Task with specific intervals

# =============================================================================
# HTTP STATUS CODES
# =============================================================================
class HttpStatus:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

# =============================================================================
# API RESPONSE KEYS
# =============================================================================
class ApiKeys:
    SUCCESS = "success"
    ERROR = "error"
    MESSAGE = "message"
    DATA = "data"
    ID = "id"
    STATUS = "status"
    RESULT = "result"

# =============================================================================
# DATABASE CONSTANTS
# =============================================================================
class Database:
    TASKS_TABLE = "tasks"
    EXECUTIONS_TABLE = "executions"
    
    # Task table columns
    TASK_COLUMNS = [
        "id", "owner", "plugin", "action", "args", "kwargs", 
        "type", "execution_start_time", "execution_end_time", 
        "interval", "status", "executor", "result", "updated_at"
    ]
    
    # Execution table columns
    EXECUTION_COLUMNS = [
        "id", "task_id", "client", "status", "result", "updated_at"
    ]

# =============================================================================
# PLUGIN CONSTANTS
# =============================================================================
class Plugin:
    DEFAULT_ACTION = "main"
    INIT_FILE = "__init__.py"
    PYTHON_EXTENSION = ".py"

# =============================================================================
# TIME CONSTANTS (in seconds)
# =============================================================================
class Time:
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 24 * 60 * 60
    WEEK = 7 * 24 * 60 * 60

# =============================================================================
# LOGGING CONSTANTS
# =============================================================================
class Logging:
    FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Log levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================
class Validation:
    MAX_TASK_NAME_LENGTH = 255
    MAX_PLUGIN_NAME_LENGTH = 100
    MAX_ACTION_NAME_LENGTH = 100
    MAX_RESULT_LENGTH = 10000
    
    # Required fields
    REQUIRED_TASK_FIELDS = ["owner", "plugin", "action"]
    REQUIRED_EXECUTION_FIELDS = ["task_id", "client", "status"]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def format_timestamp(timestamp):
    """Format timestamp for display."""
    import datetime
    try:
        if isinstance(timestamp, str):
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

def is_valid_task_status(status):
    """Check if status is valid."""
    return status in TaskStatus.all_statuses()

def get_client_identifier(hostname=None, pid=None):
    """Generate consistent client identifier."""
    import os
    import socket
    
    if not hostname:
        hostname = socket.gethostname()
    if not pid:
        pid = os.getpid()
    
    return f"{hostname}_{pid}"
