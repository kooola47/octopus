#!/usr/bin/env python3
"""
🐙 OCTOPUS SHARED - Constants
============================

Shared constants used across client and server components.
Centralized definition prevents inconsistencies and makes maintenance easier.
"""

from enum import Enum

# =============================================================================
# TASK-RELATED CONSTANTS
# =============================================================================

class TaskStatus:
    """Task status constants"""
    CREATED = "Created"
    ACTIVE = "Active"
    DONE = "Done"
    SUCCESS = "success"
    FAILED = "failed"
    COMPLETED = "completed"
    ERROR = "error"
    PENDING = "pending"
    RUNNING = "running"
    CANCELLED = "cancelled"

class TaskType:
    """Task type constants"""
    ADHOC = "Adhoc"
    SCHEDULED = "Scheduled"
    INTERVAL = "Interval"
    RECURRING = "Recurring"
    ONE_TIME = "OneTime"

class TaskOwnership:
    """Task ownership constants"""
    ALL = "ALL"
    ANYONE = "Anyone"
    SPECIFIC = "Specific"

class ExecutionStatus:
    """Execution status constants"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

# =============================================================================
# CLIENT-RELATED CONSTANTS
# =============================================================================

class ClientStatus:
    """Client status constants"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONNECTED = "disconnected"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class ClientCapabilities:
    """Client capability constants"""
    BASIC_EXECUTION = "basic_execution"
    SCHEDULED_TASKS = "scheduled_tasks"
    PLUGIN_MANAGEMENT = "plugin_management"
    FILE_OPERATIONS = "file_operations"
    NETWORK_OPERATIONS = "network_operations"
    DATABASE_OPERATIONS = "database_operations"

# =============================================================================
# USER-RELATED CONSTANTS
# =============================================================================

class UserRole:
    """User role constants"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    OPERATOR = "operator"

class UserStatus:
    """User status constants"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"

# =============================================================================
# PLUGIN-RELATED CONSTANTS
# =============================================================================

class PluginStatus:
    """Plugin status constants"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"
    DISABLED = "disabled"

class PluginAction:
    """Common plugin action constants"""
    RUN = "run"
    EXECUTE = "execute"
    VALIDATE = "validate"
    INIT = "init"
    CLEANUP = "cleanup"
    STATUS = "status"

# =============================================================================
# API-RELATED CONSTANTS
# =============================================================================

class APIResponse:
    """API response status constants"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class HTTPStatus:
    """HTTP status code constants"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503

# =============================================================================
# LOGGING-RELATED CONSTANTS
# =============================================================================

class LogLevel:
    """Logging level constants"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat:
    """Logging format constants"""
    STANDARD = "%(asctime)s %(levelname)s %(name)s %(message)s"
    DETAILED = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    SIMPLE = "%(levelname)s - %(message)s"

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

class DefaultConfig:
    """Default configuration values"""
    SERVER_PORT = 8000
    CLIENT_PORT = 8001
    HEARTBEAT_INTERVAL = 30
    CLIENT_TIMEOUT = 90
    MAX_RETRY_ATTEMPTS = 3
    PLUGIN_SYNC_INTERVAL = 300
    LOG_LEVEL = "INFO"
    DATABASE_TIMEOUT = 30
    MAX_TASK_EXECUTION_TIME = 3600
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_LOG_FILES = 5

class Timeouts:
    """Timeout constants in seconds"""
    CONNECTION = 30
    HEARTBEAT = 30
    TASK_EXECUTION = 3600
    PLUGIN_SYNC = 300
    DATABASE_OPERATION = 30
    HTTP_REQUEST = 60
    CLIENT_RESPONSE = 120

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

class ValidationLimits:
    """Validation limit constants"""
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100
    MAX_PLUGIN_NAME_LENGTH = 100
    MAX_TASK_DESCRIPTION_LENGTH = 1000
    MAX_RESULT_LENGTH = 10000
    MAX_ERROR_MESSAGE_LENGTH = 2000
    MAX_HOSTNAME_LENGTH = 253
    MAX_IP_ADDRESS_LENGTH = 45  # IPv6

class FileConstants:
    """File-related constants"""
    MAX_PLUGIN_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_LOG_SIZE = 50 * 1024 * 1024     # 50MB
    SUPPORTED_PLUGIN_EXTENSIONS = ['.py']
    LOG_FILE_ENCODING = 'utf-8'
    CONFIG_FILE_ENCODING = 'utf-8'

# =============================================================================
# NETWORK CONSTANTS
# =============================================================================

class NetworkConfig:
    """Network configuration constants"""
    DEFAULT_HOST = "localhost"
    DEFAULT_SERVER_PORT = 8000
    DEFAULT_CLIENT_PORT = 8001
    MAX_CONNECTIONS = 100
    SOCKET_TIMEOUT = 30
    KEEP_ALIVE = True
    BUFFER_SIZE = 8192

# =============================================================================
# ERROR CODES
# =============================================================================

class ErrorCode:
    """Error code constants"""
    # General errors
    UNKNOWN_ERROR = "E0000"
    VALIDATION_ERROR = "E0001"
    AUTHENTICATION_ERROR = "E0002"
    AUTHORIZATION_ERROR = "E0003"
    NOT_FOUND_ERROR = "E0004"
    CONFLICT_ERROR = "E0005"
    
    # Task errors
    TASK_NOT_FOUND = "E1001"
    TASK_VALIDATION_ERROR = "E1002"
    TASK_EXECUTION_ERROR = "E1003"
    TASK_TIMEOUT_ERROR = "E1004"
    
    # Client errors
    CLIENT_NOT_FOUND = "E2001"
    CLIENT_TIMEOUT = "E2002"
    CLIENT_DISCONNECTED = "E2003"
    
    # Plugin errors
    PLUGIN_NOT_FOUND = "E3001"
    PLUGIN_LOAD_ERROR = "E3002"
    PLUGIN_EXECUTION_ERROR = "E3003"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "E4001"
    DATABASE_QUERY_ERROR = "E4002"
    DATABASE_CONSTRAINT_ERROR = "E4003"

# =============================================================================
# MESSAGE TEMPLATES
# =============================================================================

class MessageTemplate:
    """Message template constants"""
    TASK_CREATED = "Task {task_id} created successfully"
    TASK_ASSIGNED = "Task {task_id} assigned to client {client_id}"
    TASK_COMPLETED = "Task {task_id} completed with status {status}"
    CLIENT_CONNECTED = "Client {client_id} connected from {hostname}"
    CLIENT_DISCONNECTED = "Client {client_id} disconnected"
    PLUGIN_LOADED = "Plugin {plugin_name} loaded successfully"
    PLUGIN_ERROR = "Error in plugin {plugin_name}: {error}"
    USER_LOGIN = "User {username} logged in successfully"
    USER_LOGOUT = "User {username} logged out"

# =============================================================================
# REGEX PATTERNS
# =============================================================================

class RegexPattern:
    """Common regex patterns"""
    USERNAME = r'^[a-zA-Z0-9_-]{3,50}$'
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    IP_ADDRESS = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    HOSTNAME = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    PLUGIN_NAME = r'^[a-zA-Z][a-zA-Z0-9_]{2,99}$'
    TASK_ID = r'^[a-zA-Z0-9_-]+$'

# =============================================================================
# VERSION CONSTANTS
# =============================================================================

class Version:
    """Version-related constants"""
    OCTOPUS_VERSION = "2.0.0"
    API_VERSION = "v1"
    MINIMUM_PYTHON_VERSION = "3.8"
    DATABASE_SCHEMA_VERSION = "1.0"
