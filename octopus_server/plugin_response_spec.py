#!/usr/bin/env python3
"""
🔌 PLUGIN RESPONSE SPECIFICATION
================================

Standardized plugin response format for automatic processing by the Octopus system.

Response Format:
{
    "status_code": 200,           # HTTP-style status code
    "message": "Task completed",  # Human-readable message
    "data": [                     # Array of data operations to perform
        {
            "type": "cache",      # Operation type: cache, file, db
            "name": "key_name",   # Key/path/identifier
            "value": "data"       # Value to store
        }
    ]
}

Status Code Translation:
- 200-299: Success → "Completed" 
- 400-499: Client Error → "Failed"
- 500-599: Server Error → "Failed"
- Other: Unknown → "Failed"

Data Types:
- cache: Store value in system cache with given key
- file: Write value to file at given path
- db: Store value in database as execution result
"""

import json
import os
import time
from typing import Dict, List, Any, Tuple


class PluginResponseProcessor:
    """Processes standardized plugin responses"""
    
    def __init__(self, cache_manager=None, logger=None):
        self.cache_manager = cache_manager
        self.logger = logger
        
    def process_response(self, plugin_response: str, execution_context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Process a plugin response and execute specified data operations.
        
        Args:
            plugin_response: JSON string response from plugin
            execution_context: Context with task_id, client, execution_id, etc.
            
        Returns:
            Tuple of (status, processed_result)
        """
        try:
            # Parse the plugin response
            response_data = json.loads(plugin_response) if isinstance(plugin_response, str) else plugin_response
            
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
        """Store value in cache"""
        if self.cache_manager:
            # Add context prefix to key for namespacing
            cache_key = f"plugin_{context.get('task_id', 'unknown')}_{key}"
            self.cache_manager.set(cache_key, value, ttl=3600)  # 1 hour TTL
            return f"Cached '{key}': {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}"
        else:
            return f"Cache not available for '{key}'"
    
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
            raise Exception(f"File operation failed: {e}")
    
    def _process_db_operation(self, name: str, value: Any, context: Dict[str, Any]) -> str:
        """Store value in database as execution result"""
        try:
            # Import here to avoid circular imports
            from dbhelper import add_execution_result
            
            # Create a sub-execution record
            task_id = context.get('task_id')
            client = context.get('client', 'system')
            
            if not task_id:
                raise ValueError("task_id required for db operation")
            
            # Store as JSON if complex data
            if isinstance(value, (dict, list)):
                db_value = json.dumps(value, indent=2)
            else:
                db_value = str(value)
            
            # Create execution record
            add_execution_result(
                task_id=f"{task_id}_data_{name}",
                client=client,
                status="completed",
                result=db_value
            )
            
            return f"Stored in DB '{name}': {len(db_value)} characters"
            
        except Exception as e:
            raise Exception(f"DB operation failed: {e}")
    
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


# Example plugin response formats
EXAMPLE_RESPONSES = {
    "simple_success": {
        "status_code": 200,
        "message": "Incident created successfully",
        "data": [
            {
                "type": "cache",
                "name": "last_incident_id",
                "value": "INC-12345"
            }
        ]
    },
    
    "complex_data": {
        "status_code": 200,
        "message": "Web scraping completed",
        "data": [
            {
                "type": "cache",
                "name": "scrape_timestamp",
                "value": "2025-08-12T15:30:00Z"
            },
            {
                "type": "file",
                "name": "scraped_data.json",
                "value": {"urls": ["url1", "url2"], "count": 50}
            },
            {
                "type": "db",
                "name": "scrape_results",
                "value": {"status": "completed", "items_found": 50}
            }
        ]
    },
    
    "error_response": {
        "status_code": 500,
        "message": "API connection failed",
        "data": [
            {
                "type": "cache",
                "name": "last_error",
                "value": "Connection timeout after 30 seconds"
            }
        ]
    }
}


if __name__ == "__main__":
    # Example usage
    processor = PluginResponseProcessor()
    
    print("=== Plugin Response Processing Examples ===\n")
    
    for name, example in EXAMPLE_RESPONSES.items():
        print(f"Example: {name}")
        print(f"Input: {json.dumps(example, indent=2)}")
        
        context = {
            "task_id": "test_task_123",
            "client": "test_client",
            "execution_id": "exec_456"
        }
        
        status, result = processor.process_response(json.dumps(example), context)
        print(f"Status: {status}")
        print(f"Result: {result}")
        print("-" * 50)
