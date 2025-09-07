"""
Constants for Octopus Client
Centralized status management and other constants
"""

class TaskStatus:
    """Centralized task status constants for client-server communication"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    @classmethod
    def normalize(cls, status: str) -> str:
        """Normalize status input to standard format"""
        if not status:
            return cls.PENDING
        
        status_lower = status.lower().strip()
        
        # Map various input formats to standard statuses
        status_mapping = {
            # Pending variations
            "pending": cls.PENDING,
            "created": cls.PENDING,
            "new": cls.PENDING,
            "queued": cls.PENDING,
            
            # Running variations
            "running": cls.RUNNING,
            "active": cls.RUNNING,
            "in progress": cls.RUNNING,
            "executing": cls.RUNNING,
            
            # Completed variations
            "completed": cls.COMPLETED,
            "done": cls.COMPLETED,
            "finished": cls.COMPLETED,
            "success": cls.COMPLETED,  # Map execution success to task completion
            
            # Failed variations
            "failed": cls.FAILED,
            "error": cls.FAILED,
            "failure": cls.FAILED,
            
            # Cancelled variations
            "cancelled": cls.CANCELLED,
            "canceled": cls.CANCELLED,
            "stopped": cls.CANCELLED,
            "aborted": cls.CANCELLED,
        }
        
        return status_mapping.get(status_lower, status_lower)
    
    @classmethod
    def is_final_state(cls, status: str) -> bool:
        """Check if status represents a final state"""
        normalized = cls.normalize(status)
        return normalized in [cls.COMPLETED, cls.FAILED, cls.CANCELLED]


class ExecutionStatus:
    """Centralized execution status constants for client-server communication"""
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"
    CANCELLED = "cancelled"
    
    @classmethod
    def normalize(cls, status: str) -> str:
        """Normalize status input to standard format"""
        if not status:
            return cls.SUCCESS
        
        status_lower = status.lower().strip()
        
        # Map various input formats to standard statuses
        status_mapping = {
            # Success variations
            "success": cls.SUCCESS,
            "successful": cls.SUCCESS,
            "completed": cls.SUCCESS,
            "done": cls.SUCCESS,
            "ok": cls.SUCCESS,
            "passed": cls.SUCCESS,
            
            # Running variations
            "running": cls.RUNNING,
            "executing": cls.RUNNING,
            "in_progress": cls.RUNNING,
            "active": cls.RUNNING,
            
            # Failed variations
            "failed": cls.FAILED,
            "failure": cls.FAILED,
            "error": cls.FAILED,
            "exception": cls.FAILED,
            
            # Cancelled variations
            "cancelled": cls.CANCELLED,
            "canceled": cls.CANCELLED,
            "stopped": cls.CANCELLED,
            "aborted": cls.CANCELLED,
        }
        
        return status_mapping.get(status_lower, status_lower)


class ClientStatus:
    """Centralized client status constants"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    
    @classmethod
    def normalize(cls, status: str) -> str:
        """Normalize status input to standard format"""
        if not status:
            return cls.OFFLINE
        
        status_lower = status.lower().strip()
        
        # Map various input formats to standard statuses
        status_mapping = {
            "online": cls.ONLINE,
            "active": cls.ONLINE,
            "available": cls.ONLINE,
            "connected": cls.ONLINE,
            
            "offline": cls.OFFLINE,
            "inactive": cls.OFFLINE,
            "disconnected": cls.OFFLINE,
            
            "busy": cls.BUSY,
            "working": cls.BUSY,
            "executing": cls.BUSY,
        }
        
        return status_mapping.get(status_lower, status_lower)
