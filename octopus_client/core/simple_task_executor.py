"""
🎯 SIMPLIFIED TASK EXECUTOR
===========================

Clean task execution engine focused only on running tasks.
Scheduling is handled by AdvancedTaskScheduler.
"""

import ast
import asyncio
from constants import ExecutionStatus
import inspect
import json
import time
from typing import Dict, Any, Tuple


class SimpleTaskExecutor:
    """Simplified task executor for core plugin execution"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def execute_task(self, task: Dict[str, Any], task_id: str, username: str) -> Tuple[str, str]:
        """Execute the given task and return status and result."""
        self.logger.debug(f"Executing task {task_id}: {task}")
        
        plugin = task.get("plugin")
        action = task.get("action", "run")
        args = task.get("args", [])
        kwargs = task.get("kwargs", {})
        
        # Validate plugin name
        if not plugin or not plugin.strip():
            error_msg = f"Task {task_id} missing or empty plugin name. Task data: {task}"
            self.logger.error(error_msg)
            return "failure", error_msg
        
        plugin = plugin.strip()
        
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
            from pluginhelper import import_plugin
            module = import_plugin(plugin)
            if not module:
                self.logger.error(f"Failed to import plugin: {plugin}")
                return "failure", f"Failed to import plugin: {plugin}"
            
            func = getattr(module, action, None)
            if callable(func):
                self.logger.info(f"Executing task {task_id}: {plugin}.{action} args={args} kwargs={kwargs}")
                
                # Check if the function is async (coroutine)
                if inspect.iscoroutinefunction(func):
                    self.logger.debug(f"Function {plugin}.{action} is async, using asyncio.run()")
                    try:
                        # Run async function
                        result = asyncio.run(func(*args, **kwargs))
                    except Exception as e:
                        self.logger.error(f"Async execution failed for {plugin}.{action}: {e}")
                        return ExecutionStatus.FAILED, str(e)
                else:
                    self.logger.debug(f"Function {plugin}.{action} is sync, calling directly")
                    # Run sync function normally
                    result = func(*args, **kwargs)
                
                # Process plugin response if it's in structured format
                exec_status, result_str = self._process_plugin_result(result, task_id, username)
                
            else:
                result_str = f"Action {action} not found"
                exec_status = ExecutionStatus.FAILED
                
        except Exception as e:
            self.logger.error(f"Plugin execution failed for {plugin}.{action}: {e}")
            result_str = str(e)
            exec_status = ExecutionStatus.FAILED
        
        return exec_status, result_str
    
    def _process_plugin_result(self, result: Any, task_id: str, username: str) -> Tuple[str, str]:
        """Process plugin result - handle both simple strings and structured responses"""
        # If result is None or simple string, handle as before
        if result is None:
            return ExecutionStatus.SUCCESS, ""
        
        if isinstance(result, str):
            # Try to parse as JSON (structured response)
            try:
                parsed_result = json.loads(result)
                if isinstance(parsed_result, dict) and "status_code" in parsed_result:
                    return self._process_structured_response(parsed_result, task_id, username)
            except json.JSONDecodeError:
                pass
            # Not JSON, treat as simple string result
            return ExecutionStatus.SUCCESS, result
        
        # If result is already a dict, check if it's structured response
        if isinstance(result, dict) and "status_code" in result:
            return self._process_structured_response(result, task_id, username)
        
        # For other types, convert to string
        return ExecutionStatus.SUCCESS, str(result)
    
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
            exec_status = ExecutionStatus.SUCCESS if status == "Completed" else ExecutionStatus.FAILED
            
            return exec_status, processed_result
            
        except Exception as e:
            self.logger.error(f"Error processing structured response: {e}")
            # Fallback to simple processing
            status_code = response.get("status_code", 200)
            message = response.get("message", "Task completed")
            exec_status = ExecutionStatus.SUCCESS if 200 <= status_code < 300 else ExecutionStatus.FAILED
            return exec_status, message
