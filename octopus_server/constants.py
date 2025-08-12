#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Constants
=============================

Constants and enums for the Octopus orchestration system.
"""

class TaskStatus:
    """Task status constants"""
    CREATED = "Created"
    ACTIVE = "Active"
    RUNNING = "Running"
    DONE = "Done"
    SUCCESS = "Success"
    COMPLETED = "Completed"
    FAILED = "Failed"
    ERROR = "Error"
    CANCELLED = "Cancelled"
    
    @classmethod
    def is_completed(cls, status):
        """Check if a status indicates task completion"""
        if not status:
            return False
        completed_statuses = [cls.DONE, cls.SUCCESS, cls.COMPLETED, cls.FAILED, cls.ERROR, cls.CANCELLED]
        return status in completed_statuses

class TaskOwnership:
    """Task ownership constants"""
    ALL = "ALL"
    ANYONE = "ANYONE"

class TaskType:
    """Task type constants"""
    ADHOC = "adhoc"
    SCHEDULED = "scheduled"
    INTERVAL = "interval"

class Database:
    """Database related constants"""
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    CONNECTION_POOL_SIZE = 10
