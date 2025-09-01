"""
⚡ TASK ASSIGNMENT SERVICE
=========================

Centralized task assignment to prevent duplicate executions and race conditions.
"""

import time
import threading
import logging
from typing import Dict, Any
from dbhelper import get_tasks, get_active_clients, assign_all_tasks


class TaskAssignmentService:
    """Centralized service to handle task assignments"""
    
    def __init__(self, global_cache):
        self.global_cache = global_cache
        self.logger = logging.getLogger(__name__)
        self._assignment_lock = threading.Lock()
        self._last_assignment = 0
        self._assignment_interval = 2.0  # Minimum seconds between assignments
    
    def assign_pending_tasks(self, force: bool = False) -> Dict[str, Any]:
        """
        Assign pending tasks to available clients.
        
        Args:
            force: If True, bypass the rate limiting
            
        Returns:
            Dict containing assignment results
        """
        current_time = time.time()
        
        # Rate limiting: prevent assignments more frequently than interval
        if not force and (current_time - self._last_assignment < self._assignment_interval):
            self.logger.debug(f"Skipping task assignment due to rate limiting ({self._assignment_interval}s interval)")
            return {"status": "rate_limited", "message": "Assignment skipped due to rate limiting"}
        
        # Try to acquire lock, but don't block if another assignment is in progress
        if not self._assignment_lock.acquire(blocking=False):
            self.logger.debug("Skipping task assignment - another assignment in progress")
            return {"status": "locked", "message": "Another assignment in progress"}
        
        try:
            self._last_assignment = current_time
            
            # Get current tasks and active clients
            tasks = get_tasks()
            clients = self.global_cache.get_by_cache_type('clients')
            active_clients = get_active_clients(clients, now=current_time, timeout=60)
            
            # Count tasks before assignment
            unassigned_tasks = sum(1 for task in tasks.values() 
                                 if not task.get("executor") and task.get("status") not in ("success", "failed", "Done"))
            
            self.logger.info(f"Starting task assignment: {len(tasks)} total tasks, {unassigned_tasks} unassigned, {len(active_clients)} active clients")
            
            # Perform the assignment
            assign_all_tasks(tasks, active_clients)
            
            # Count results
            assigned_tasks = sum(1 for task in tasks.values() 
                               if task.get("executor") and task.get("status") not in ("success", "failed", "Done"))
            
            result = {
                "status": "success",
                "total_tasks": len(tasks),
                "unassigned_before": unassigned_tasks,
                "assigned_after": assigned_tasks,
                "active_clients": len(active_clients),
                "assignment_time": current_time
            }
            
            self.logger.info(f"Task assignment completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task assignment failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self._assignment_lock.release()
    
    def get_assignment_status(self) -> Dict[str, Any]:
        """Get current assignment service status"""
        return {
            "last_assignment": self._last_assignment,
            "assignment_interval": self._assignment_interval,
            "is_locked": not self._assignment_lock.acquire(blocking=False)
        }


# Global instance
_assignment_service = None

def get_assignment_service(global_cache):
    """Get or create the global assignment service instance"""
    global _assignment_service
    if _assignment_service is None:
        _assignment_service = TaskAssignmentService(global_cache)
    return _assignment_service
