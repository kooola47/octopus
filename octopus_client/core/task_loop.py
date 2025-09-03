"""
🔄 TASK EXECUTION LOOP
======================

Main task execution loop that coordinates fetching, claiming, and executing tasks.
"""

import time
from typing import List, Dict, Any, Tuple
from core.task_execution import TaskExecutor
from core.server_communication import ServerCommunicator

class TaskExecutionLoop:
    """Manages the main task execution loop"""
    
    def __init__(self, task_executor: TaskExecutor, server_comm: ServerCommunicator, 
                 server_url: str, task_check_interval: int, retry_delay: int, logger):
        self.task_executor = task_executor
        self.server_comm = server_comm
        self.server_url = server_url
        self.task_check_interval = task_check_interval
        self.retry_delay = retry_delay
        self.logger = logger
    
    def run(self, username: str):
        """Main task execution loop"""
        self.logger.info(f"Starting task execution loop for client: {username}")
        
        while True:
            try:
                tasks = self.server_comm.fetch_tasks()
                
                # Handle both dict and list formats
                if isinstance(tasks, dict):
                    task_items = tasks.items()
                elif isinstance(tasks, list):
                    # Convert list to dict-like items
                    task_items = [(task.get('id', i), task) for i, task in enumerate(tasks)]
                else:
                    self.logger.warning(f"Unexpected tasks format: {type(tasks)}")
                    continue
                
                for tid, task in task_items:
                    self._process_task(tid, task, username)
                        
                time.sleep(self.task_check_interval)
            except Exception as e:
                self.logger.error(f"Task execution polling failed: {e}")
                time.sleep(self.retry_delay)
    
    def _process_task(self, tid: str, task: Dict[str, Any], username: str):
        """Process a single task"""
        owner = task.get("owner")
        executor = task.get("executor") 
        status = task.get("status")
        
        self.logger.debug(f"Checking task {tid}: owner={owner}, executor={executor}, status={status}")
        
        if self.task_executor.is_task_done(task):
            self.logger.debug(f"Task {tid} is already done, skipping")
            return
            
        # Claim ALL tasks if needed
        if self.task_executor.claim_all_task(task, username):
            if self.server_comm.claim_task(tid, username):
                return  # Will execute on next poll as Active
                
        # Should this client execute?
        if self.task_executor.should_client_execute(task, username):
            # Atomically claim the task for execution to prevent race conditions
            if not self.task_executor.is_executing(tid):
                # Try to claim the task atomically using server-side coordination
                if self.task_executor.start_execution(tid, username):
                    self.logger.info(f"Successfully claimed and executing task {tid} assigned to {username}")
                    self._execute_task_safely(tid, task, username)
                else:
                    self.logger.info(f"Task {tid} already being executed by another process, skipping")
            else:
                self.logger.debug(f"Task {tid} is already being executed locally, skipping duplicate")
        else:
            self.logger.debug(f"Task {tid} not assigned to this client ({username})")
    
    def _execute_task_safely(self, tid: str, task: Dict[str, Any], username: str):
        """Execute a task with proper error handling and cleanup"""
        # Task is already marked as executing by the caller
        
        try:
            exec_status, result = self.task_executor.execute_task(task, tid, username)
            
            if task.get("owner") == "ALL":
                # For ALL tasks, create execution record only
                self.task_executor.post_execution_result(tid, username, exec_status, result)
            else:
                # For scheduled tasks, create execution record but don't mark as Done
                task_type = (task.get("type") or "").lower()
                if task_type in ["scheduled", "schedule"]:
                    self.task_executor.post_execution_result(tid, username, exec_status, result)
                    self.logger.info(f"Posted execution result for scheduled task {tid}: {exec_status}")
                else:
                    # For adhoc tasks, only mark as Done - no execution record needed
                    self.task_executor.update_task_status(tid, username, result)
                    self.logger.info(f"Updated adhoc task {tid} status to Done")
                
            self.logger.info(f"Task {tid} execution completed: {exec_status}")
        finally:
            # Always remove from executing set when done
            self.task_executor.finish_execution(tid)
