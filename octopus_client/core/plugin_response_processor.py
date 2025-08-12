#!/usr/bin/env python3
"""
🔌 PLUGIN RESPONSE PROCESSOR (Client Side)
==========================================

Lightweight version of the plugin response processor for client-side execution.
"""

import json
import os
import time
from typing import Dict, List, Any, Tuple


class PluginResponseProcessor:
    """Processes standardized plugin responses on client side"""
    
    def __init__(self, logger=None):
        self.logger = logger
        
    def process_response(self, plugin_response: Any, execution_context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Process a plugin response and execute specified data operations.
        
        Args:
            plugin_response: JSON string or dict response from plugin
            execution_context: Context with task_id, client, execution_id, etc.
            
        Returns:
            Tuple of (status, processed_result)
        """
        try:
            # Parse the plugin response
            if isinstance(plugin_response, str):
                response_data = json.loads(plugin_response)
            elif isinstance(plugin_response, dict):
                response_data = plugin_response
            else:
                # Not a structured response, treat as simple result
                return "Completed", str(plugin_response) if plugin_response is not None else ""
            
            # Check if this is a structured response
            if not isinstance(response_data, dict) or "status_code" not in response_data:
                return "Completed", str(plugin_response)
            
            # Extract status code and translate to status
            status_code = response_data.get("status_code", 200)
            status = self._translate_status_code(status_code)
            
            # Get message
            message = response_data.get("message", "Task completed")
            
            # Process data operations
            data_operations = response_data.get("data", [])
            operation_results = []
            
            for operation in data_operations:
                try:
                    result = self._process_data_operation(operation, execution_context)
                    operation_results.append(result)
                except Exception as e:
                    error_msg = f"Failed to process {operation.get('type', 'unknown')} operation: {e}"
                    operation_results.append(error_msg)
                    if self.logger:
                        self.logger.error(error_msg)
            
            # Build final result
            result_parts = [message]
            if operation_results:
                result_parts.append("\nData Operations:")
                result_parts.extend([f"  - {result}" for result in operation_results])
            
            final_result = "\n".join(result_parts)
            
            if self.logger:
                self.logger.info(f"Processed plugin response: status={status}, operations={len(data_operations)}")
            
            return status, final_result
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in plugin response: {e}"
            if self.logger:
                self.logger.error(error_msg)
            return "Failed", error_msg
            
        except Exception as e:
            error_msg = f"Error processing plugin response: {e}"
            if self.logger:
                self.logger.error(error_msg)
            return "Failed", error_msg
    
    def _translate_status_code(self, status_code: int) -> str:
        """Translate HTTP status code to execution status"""
        if 200 <= status_code < 300:
            return "Completed"
        elif 400 <= status_code < 600:
            return "Failed"
        else:
            return "Failed"
    
    def _process_data_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Process a single data operation"""
        op_type = operation.get("type")
        name = operation.get("name")
        value = operation.get("value")
        
        if not op_type or not name:
            raise ValueError("Operation must have 'type' and 'name' fields")
        
        if op_type == "cache":
            return self._process_cache_operation(name, value, context)
        elif op_type == "file":
            return self._process_file_operation(name, value, context)
        elif op_type == "db":
            return self._process_db_operation(name, value, context)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def _process_cache_operation(self, key: str, value: Any, context: Dict[str, Any]) -> str:
        """Store value in local cache (client-side caching)"""
        try:
            # Create local cache directory
            cache_dir = os.path.join(os.getcwd(), "cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Add context prefix to key for namespacing
            cache_key = f"plugin_{context.get('task_id', 'unknown')}_{key}"
            cache_file = os.path.join(cache_dir, f"{cache_key}.json")
            
            # Store with timestamp
            cache_data = {
                "value": value,
                "timestamp": time.time(),
                "context": context
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            
            return f"Cached '{key}': {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}"
            
        except Exception as e:
            return f"Cache operation failed for '{key}': {e}"
    
    def _process_file_operation(self, path: str, value: Any, context: Dict[str, Any]) -> str:
        """Write value to file"""
        try:
            # Ensure path is within allowed directory
            safe_path = self._get_safe_file_path(path, context)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            
            # Write value to file
            with open(safe_path, 'w', encoding='utf-8') as f:
                if isinstance(value, (dict, list)):
                    json.dump(value, f, indent=2)
                else:
                    f.write(str(value))
            
            return f"Wrote to file '{path}': {len(str(value))} characters"
            
        except Exception as e:
            return f"File operation failed for '{path}': {e}"
    
    def _process_db_operation(self, name: str, value: Any, context: Dict[str, Any]) -> str:
        """Store value for database operations (client-side preparation)"""
        try:
            # Store data operation for server-side processing
            db_operations_dir = os.path.join(os.getcwd(), "db_operations")
            os.makedirs(db_operations_dir, exist_ok=True)
            
            # Create operation file
            task_id = context.get('task_id', 'unknown')
            timestamp = int(time.time() * 1000)
            operation_file = os.path.join(db_operations_dir, f"{task_id}_{name}_{timestamp}.json")
            
            # Store operation data
            operation_data = {
                "name": name,
                "value": value,
                "context": context,
                "timestamp": time.time()
            }
            
            with open(operation_file, 'w', encoding='utf-8') as f:
                json.dump(operation_data, f, indent=2)
            
            return f"Prepared DB operation '{name}': {len(str(value))} characters"
            
        except Exception as e:
            return f"DB operation preparation failed for '{name}': {e}"
    
    def _get_safe_file_path(self, path: str, context: Dict[str, Any]) -> str:
        """Get safe file path within allowed directory"""
        # Define safe directory for plugin outputs
        safe_dir = os.path.join(os.getcwd(), "plugin_outputs")
        
        # Add task context to path
        task_id = context.get('task_id', 'unknown')
        client = context.get('client', 'unknown')
        
        # Create subdirectory structure
        subdir = os.path.join(safe_dir, task_id, client)
        
        # Clean the provided path
        clean_path = os.path.basename(path)  # Remove any directory traversal
        
        # Combine for final safe path
        safe_path = os.path.join(subdir, clean_path)
        
        return safe_path
