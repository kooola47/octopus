"""
🎯 TASK EXECUTION ENGINE
========================

Handles task execution logic, plugin loading, and result reporting.
"""

import importlib
import ast
import asyncio
import inspect
import time
import requests
import json
from typing import Dict, Any, Tuple, Optional

class TaskExecutor:
    """Manages task execution and result reporting"""
    
    def __init__(self, server_url: str, logger):
        self.server_url = server_url
        self.logger = logger
        self.executing_tasks = set()
        self.last_execution_times = {}  # Track last execution time for scheduled tasks
    
    def is_task_done(self, task: Dict[str, Any]) -> bool:
        """Returns True if the task is considered Done."""
        import datetime
        
        status = task.get("status")
        task_type = task.get("type")
        
        # If status is already Done, return True
        if status in ("Done", "success", "failed"):
            return True
        
        # For Adhoc tasks, check if there are successful/failed executions
        if task_type == "Adhoc":
            executions = task.get("executions", [])
            # For non-ALL tasks, if any execution is done, task is done
            if task.get("owner") != "ALL":
                return any(exec.get("status") in ("success", "failed") for exec in executions)
            # For ALL tasks, they remain active until server marks them done
            return False
            
        # For Schedule tasks, check if past end time
        elif task_type == "Schedule":
            end_time = task.get("execution_end_time")
            if end_time:
                try:
                    if isinstance(end_time, str) and end_time:
                        if end_time.isdigit():
                            end_ts = float(end_time)
                        else:
                            end_ts = datetime.datetime.fromisoformat(end_time).timestamp()
                    else:
                        end_ts = float(end_time)
                    if time.time() > end_ts:
                        return True
                except Exception:
                    pass
        
        return False
    
    def _is_within_execution_window(self, task: Dict[str, Any]) -> bool:
        """Check if current time is within the task's execution window"""
        import datetime
        
        start_time = task.get("execution_start_time")
        end_time = task.get("execution_end_time")
        current_time = time.time()
        
        # If no start time specified, assume it's ready to start
        if start_time:
            try:
                # Handle both timestamp and datetime string formats
                if isinstance(start_time, str):
                    # Try to parse as float first (timestamp)
                    try:
                        start_ts = float(start_time)
                    except ValueError:
                        # Parse datetime-local format: YYYY-MM-DDTHH:MM
                        dt = datetime.datetime.fromisoformat(start_time.replace('T', ' '))
                        start_ts = dt.timestamp()
                else:
                    # Already a numeric timestamp
                    start_ts = float(start_time)
                    
                if current_time < start_ts:
                    self.logger.debug(f"Task not yet ready to start. Current: {current_time}, Start: {start_ts}")
                    return False
            except Exception as e:
                self.logger.warning(f"Error parsing start time '{start_time}': {e}")
        
        # If no end time specified, assume it can run indefinitely
        if end_time:
            try:
                # Handle both timestamp and datetime string formats
                if isinstance(end_time, str):
                    # Try to parse as float first (timestamp)
                    try:
                        end_ts = float(end_time)
                    except ValueError:
                        # Parse datetime-local format: YYYY-MM-DDTHH:MM
                        dt = datetime.datetime.fromisoformat(end_time.replace('T', ' '))
                        end_ts = dt.timestamp()
                else:
                    # Already a numeric timestamp
                    end_ts = float(end_time)
                    
                if current_time > end_ts:
                    self.logger.debug(f"Task execution window has ended. Current: {current_time}, End: {end_ts}")
                    return False
            except Exception as e:
                self.logger.warning(f"Error parsing end time '{end_time}': {e}")
        
        return True
    
    def should_client_execute(self, task: Dict[str, Any], username: str) -> bool:
        """Returns True if this client should execute the task."""
        owner = task.get("owner")
        executor = task.get("executor")
        status = task.get("status")
        task_type = task.get("type", "Adhoc")
        task_id = task.get("id")
        
        # Basic checks first
        if status != "Active":
            return False
        
        # Check execution time window for scheduled tasks
        if task_type in ["Schedule", "scheduled"]:
            if not self._is_within_execution_window(task):
                return False
        
        # For Schedule tasks, check interval before allowing execution
        if task_type in ["Schedule", "scheduled"]:
            interval = task.get("interval")
            if interval:
                try:
                    interval_seconds = float(interval)
                    last_execution_time = self.last_execution_times.get(task_id)
                    
                    if last_execution_time:
                        time_since_last = time.time() - last_execution_time
                        if time_since_last < interval_seconds:
                            self.logger.debug(f"Schedule task {task_id}: Only {time_since_last:.1f}s since last execution, need {interval_seconds}s interval")
                            return False
                        else:
                            self.logger.info(f"Schedule task {task_id}: {time_since_last:.1f}s since last execution, interval {interval_seconds}s met - ready to execute")
                    else:
                        self.logger.info(f"Schedule task {task_id}: First execution for this client")
                except Exception as e:
                    self.logger.warning(f"Error checking interval for task {task_id}: {e}")
        
        # For ALL tasks, every client should execute if status is Active
        if owner == "ALL":
            return True
        
        # For tasks specifically assigned to this client (executor = username)
        if executor == username:
            return True
        
        # For tasks owned by this user (fallback)
        if owner == username:
            return True
            
        return False
    
    def claim_all_task(self, task: Dict[str, Any], username: str) -> bool:
        """Claim an ALL task if status is Created or executor is empty."""
        owner = task.get("owner")
        executor = task.get("executor")
        status = task.get("status")
        if owner == "ALL" and (not executor or status == "Created"):
            return True
        return False
    
    def execute_task(self, task: Dict[str, Any], tid: str, username: str) -> Tuple[str, str]:
        """Execute the given task and return status and result."""
        plugin = task.get("plugin")
        action = task.get("action", "run")
        args = task.get("args", [])
        kwargs = task.get("kwargs", {})
        task_type = task.get("type", "Adhoc")
        
        # Record execution time for scheduled tasks before execution
        if task_type == "Schedule":
            self.last_execution_times[tid] = time.time()
            self.logger.info(f"Recording execution time for Schedule task {tid}")
        
        # Parse string arguments
        if isinstance(args, str):
            try:
                args = ast.literal_eval(args)
            except Exception:
                args = []
        if isinstance(kwargs, str):
            try:
                kwargs = ast.literal_eval(kwargs)
            except Exception:
                kwargs = {}
        
        try:
            module = importlib.import_module(f"plugins.{plugin}")
            func = getattr(module, action, None)
            if callable(func):
                self.logger.info(f"Executing task {tid}: {plugin}.{action} args={args} kwargs={kwargs}")
                
                # Check if the function is async (coroutine)
                if inspect.iscoroutinefunction(func):
                    self.logger.debug(f"Function {plugin}.{action} is async, using asyncio.run()")
                    try:
                        # Run async function
                        result = asyncio.run(func(*args, **kwargs))
                    except Exception as e:
                        self.logger.error(f"Async execution failed for {plugin}.{action}: {e}")
                        result = str(e)
                        exec_status = "failed"
                        return exec_status, result
                else:
                    self.logger.debug(f"Function {plugin}.{action} is sync, calling directly")
                    # Run sync function normally
                    result = func(*args, **kwargs)
                
                # Process plugin response if it's in structured format
                exec_status, result_str = self._process_plugin_result(result, tid, username)
                
            else:
                result_str = f"Action {action} not found"
                exec_status = "failed"
        except Exception as e:
            self.logger.error(f"Plugin execution failed for {plugin}.{action}: {e}")
            result_str = str(e)
            exec_status = "failed"
        
        return exec_status, result_str
    
    def _process_plugin_result(self, result: Any, task_id: str, username: str) -> Tuple[str, str]:
        """Process plugin result - handle both simple strings and structured responses"""
        # If result is None or simple string, handle as before
        if result is None:
            return "success", ""
        
        if isinstance(result, str):
            # Try to parse as JSON (structured response)
            try:
                parsed_result = json.loads(result)
                if isinstance(parsed_result, dict) and "status_code" in parsed_result:
                    return self._process_structured_response(parsed_result, task_id, username)
            except json.JSONDecodeError:
                pass
            # Not JSON, treat as simple string result
            return "success", result
        
        # If result is already a dict, check if it's structured response
        if isinstance(result, dict) and "status_code" in result:
            return self._process_structured_response(result, task_id, username)
        
        # For other types, convert to string
        return "success", str(result)
    
    def _process_structured_response(self, response: Dict[str, Any], task_id: str, username: str) -> Tuple[str, str]:
        """Process structured plugin response with data operations"""
        try:
            # Import the processor
            from .plugin_response_processor import PluginResponseProcessor
            
            # Create processor instance
            processor = PluginResponseProcessor(logger=self.logger)
            
            # Create execution context
            context = {
                "task_id": task_id,
                "client": username,
                "execution_id": f"{task_id}_{username}_{int(time.time() * 1000)}"
            }
            
            # Process the response
            status, processed_result = processor.process_response(response, context)
            
            # Map status to execution status
            exec_status = "success" if status == "Completed" else "failed"
            
            return exec_status, processed_result
            
        except Exception as e:
            self.logger.error(f"Error processing structured response: {e}")
            # Fallback to simple processing
            status_code = response.get("status_code", 200)
            message = response.get("message", "Task completed")
            exec_status = "success" if 200 <= status_code < 300 else "failed"
            return exec_status, message
    
    def post_execution_result(self, tid: str, username: str, exec_status: str, result: str):
        """Post execution result for ALL tasks to the executions table with unique execution ID."""
        try:
            # Generate unique execution ID
            execution_id = f"{tid}_{username}_{int(time.time() * 1000)}"
            
            response = requests.post(
                f"{self.server_url}/api/execution-results",
                data={
                    "execution_id": execution_id,
                    "task_id": tid,
                    "client": username,
                    "exec_status": exec_status,
                    "exec_result": result
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info(f"Posted execution result: execution_id={execution_id}, task_id={tid}, client={username}, status={exec_status}")
            else:
                self.logger.warning(f"Server returned status {response.status_code} for execution {execution_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to post execution for task {tid}: {e}")
    
    def update_task_status(self, tid: str, username: str, result: str, status: str = "Done"):
        """Update the task status for direct user tasks."""
        update = {
            "status": status,
            "result": result,
            "executor": username,
            "updated_at": time.time()
        }
        try:
            requests.put(f"{self.server_url}/tasks/{tid}", json=update, timeout=5)
        except Exception as e:
            self.logger.error(f"Failed to update task {tid} status: {e}")
    
    def is_executing(self, task_id: str) -> bool:
        """Check if task is currently being executed"""
        return task_id in self.executing_tasks
    
    def start_execution(self, task_id: str):
        """Mark task as executing"""
        self.executing_tasks.add(task_id)
    
    def finish_execution(self, task_id: str):
        """Mark task execution as finished"""
        self.executing_tasks.discard(task_id)
    
    def reset_schedule_tracking(self, task_id: Optional[str] = None):
        """Reset execution time tracking for scheduled tasks"""
        if task_id:
            self.last_execution_times.pop(task_id, None)
            self.logger.info(f"Reset execution tracking for task {task_id}")
        else:
            self.last_execution_times.clear()
            self.logger.info("Reset execution tracking for all tasks")
    
    def get_last_execution_time(self, task_id: str) -> float:
        """Get the last execution time for a task"""
        return self.last_execution_times.get(task_id, 0)
