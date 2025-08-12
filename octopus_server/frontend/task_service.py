#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Frontend Task Service
=========================================

Frontend service layer for task-related operations.
Handles data transformation, validation, and presentation logic for the frontend.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from ..models.task_model import task_model
from ..models.execution_model import execution_model
from ..models.plugin_model import plugin_model
from ..models.client_model import client_model
from ...shared.utils import format_timestamp, format_duration, safe_json_loads, sanitize_string
from ...shared.constants import TaskStatus, TaskType, TaskOwnership

logger = logging.getLogger(__name__)

class TaskFrontendService:
    """Frontend service for task operations"""
    
    def __init__(self):
        self.task_model = task_model
        self.execution_model = execution_model
        self.plugin_model = plugin_model
        self.client_model = client_model
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for frontend"""
        try:
            # Get tasks with executions
            tasks = self.task_model.get_tasks_with_executions()
            
            # Get active clients
            active_clients = self.client_model.get_active_clients()
            
            # Get plugin names
            plugin_names = self.plugin_model.get_plugin_names()
            
            # Transform tasks for frontend display
            transformed_tasks = {}
            for task_id, task in tasks.items():
                transformed_tasks[task_id] = self._transform_task_for_frontend(task)
            
            # Transform clients for frontend display
            transformed_clients = [self._transform_client_for_frontend(client) for client in active_clients]
            
            return {
                'tasks': transformed_tasks,
                'clients': transformed_clients,
                'plugins': plugin_names,
                'stats': self._get_dashboard_stats()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {'tasks': {}, 'clients': [], 'plugins': [], 'stats': {}}
    
    def _transform_task_for_frontend(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Transform task data for frontend display"""
        try:
            # Parse JSON fields safely
            args = safe_json_loads(task.get('args', '[]'), [])
            kwargs = safe_json_loads(task.get('kwargs', '{}'), {})
            
            # Format timestamps
            created_at_formatted = format_timestamp(task.get('created_at'))
            updated_at_formatted = format_timestamp(task.get('updated_at'))
            
            # Calculate execution duration if available
            execution_duration = None
            if task.get('execution_start_time') and task.get('execution_end_time'):
                try:
                    start = float(task['execution_start_time'])
                    end = float(task['execution_end_time'])
                    execution_duration = format_duration(end - start)
                except (ValueError, TypeError):
                    pass
            
            # Transform executions
            executions = []
            for execution in task.get('executions', []):
                executions.append(self._transform_execution_for_frontend(execution))
            
            # Determine task priority based on status and age
            priority = self._calculate_task_priority(task)
            
            # Determine display status
            display_status = self._get_display_status(task.get('status', ''), executions)
            
            return {
                'id': task.get('id'),
                'owner': task.get('owner', ''),
                'plugin': task.get('plugin', ''),
                'action': task.get('action', 'run'),
                'args': args,
                'kwargs': kwargs,
                'type': task.get('type', TaskType.ADHOC),
                'status': task.get('status', TaskStatus.CREATED),
                'display_status': display_status,
                'executor': task.get('executor', ''),
                'result': sanitize_string(task.get('result', ''), 500),
                'created_at': created_at_formatted,
                'updated_at': updated_at_formatted,
                'execution_duration': execution_duration,
                'executions': executions,
                'priority': priority,
                'can_edit': self._can_edit_task(task),
                'can_delete': self._can_delete_task(task),
                'can_execute': self._can_execute_task(task)
            }
        except Exception as e:
            logger.error(f"Error transforming task for frontend: {e}")
            return task  # Return original if transformation fails
    
    def _transform_execution_for_frontend(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Transform execution data for frontend display"""
        try:
            return {
                'id': execution.get('id'),
                'execution_id': execution.get('execution_id'),
                'client': execution.get('client', ''),
                'status': execution.get('status', 'unknown'),
                'result': sanitize_string(execution.get('result', ''), 300),
                'created_at': format_timestamp(execution.get('created_at')),
                'updated_at': format_timestamp(execution.get('updated_at')),
                'duration': self._calculate_execution_duration(execution)
            }
        except Exception as e:
            logger.error(f"Error transforming execution for frontend: {e}")
            return execution
    
    def _transform_client_for_frontend(self, client: Dict[str, Any]) -> Dict[str, Any]:
        """Transform client data for frontend display"""
        try:
            # Calculate time since last heartbeat
            last_heartbeat = client.get('last_heartbeat')
            heartbeat_age = None
            if last_heartbeat:
                try:
                    import time
                    heartbeat_age = format_duration(time.time() - float(last_heartbeat))
                except (ValueError, TypeError):
                    pass
            
            return {
                'client_id': client.get('client_id', ''),
                'hostname': client.get('hostname', ''),
                'ip_address': client.get('ip_address', ''),
                'username': client.get('username', ''),
                'status': client.get('status', 'unknown'),
                'last_heartbeat': format_timestamp(last_heartbeat) if last_heartbeat else 'Never',
                'heartbeat_age': heartbeat_age,
                'version': client.get('version', ''),
                'platform': client.get('platform', ''),
                'capabilities': safe_json_loads(client.get('capabilities', '[]'), []),
                'is_online': self._is_client_online(client)
            }
        except Exception as e:
            logger.error(f"Error transforming client for frontend: {e}")
            return client
    
    def _calculate_task_priority(self, task: Dict[str, Any]) -> str:
        """Calculate task priority for frontend sorting"""
        status = task.get('status', '')
        task_type = task.get('type', '')
        
        # High priority: Failed or error tasks
        if status in [TaskStatus.FAILED, TaskStatus.ERROR]:
            return 'high'
        
        # Medium priority: Active or scheduled tasks
        if status in [TaskStatus.ACTIVE, TaskStatus.RUNNING] or task_type == TaskType.SCHEDULED:
            return 'medium'
        
        # Low priority: Completed or created tasks
        return 'low'
    
    def _get_display_status(self, status: str, executions: List[Dict[str, Any]]) -> str:
        """Get display-friendly status"""
        if not status:
            return 'Unknown'
        
        # Map internal statuses to display statuses
        status_map = {
            TaskStatus.CREATED: 'Pending',
            TaskStatus.ACTIVE: 'Running',
            TaskStatus.DONE: 'Completed',
            TaskStatus.SUCCESS: 'Success',
            TaskStatus.FAILED: 'Failed',
            TaskStatus.ERROR: 'Error',
            TaskStatus.PENDING: 'Pending',
            TaskStatus.RUNNING: 'Running',
            TaskStatus.COMPLETED: 'Completed'
        }
        
        return status_map.get(status, status.title())
    
    def _calculate_execution_duration(self, execution: Dict[str, Any]) -> Optional[str]:
        """Calculate execution duration"""
        try:
            created_at = execution.get('created_at')
            updated_at = execution.get('updated_at')
            
            if created_at and updated_at:
                duration = float(updated_at) - float(created_at)
                return format_duration(duration)
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _is_client_online(self, client: Dict[str, Any]) -> bool:
        """Check if client is considered online"""
        try:
            import time
            last_heartbeat = client.get('last_heartbeat')
            if not last_heartbeat:
                return False
            
            # Consider online if heartbeat within last 90 seconds
            return (time.time() - float(last_heartbeat)) < 90
        except (ValueError, TypeError):
            return False
    
    def _can_edit_task(self, task: Dict[str, Any]) -> bool:
        """Check if task can be edited"""
        status = task.get('status', '')
        # Can edit if not completed/running
        completed_statuses = [TaskStatus.DONE, TaskStatus.SUCCESS, TaskStatus.COMPLETED]
        running_statuses = [TaskStatus.ACTIVE, TaskStatus.RUNNING]
        return status not in completed_statuses and status not in running_statuses
    
    def _can_delete_task(self, task: Dict[str, Any]) -> bool:
        """Check if task can be deleted"""
        status = task.get('status', '')
        # Can delete if not currently running
        running_statuses = [TaskStatus.ACTIVE, TaskStatus.RUNNING]
        return status not in running_statuses
    
    def _can_execute_task(self, task: Dict[str, Any]) -> bool:
        """Check if task can be executed immediately"""
        status = task.get('status', '')
        # Can execute if created or failed
        executable_statuses = [TaskStatus.CREATED, TaskStatus.FAILED, TaskStatus.ERROR]
        return status in executable_statuses
    
    def _get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            # Task statistics
            task_stats = {
                'total': self.task_model.count(),
                'active': self.task_model.count({'status': TaskStatus.ACTIVE}),
                'completed': self.task_model.count({'status': TaskStatus.COMPLETED}),
                'failed': self.task_model.count({'status': TaskStatus.FAILED})
            }
            
            # Execution statistics
            execution_stats = self.execution_model.get_execution_stats()
            
            # Client statistics
            client_stats = self.client_model.get_client_stats()
            
            # Plugin statistics
            plugin_stats = self.plugin_model.get_plugin_stats()
            
            return {
                'tasks': task_stats,
                'executions': execution_stats,
                'clients': client_stats,
                'plugins': plugin_stats
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    def create_task_from_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task from frontend form data with validation and transformation"""
        try:
            # Validate required fields
            required_fields = ['owner', 'plugin', 'action']
            missing_fields = [field for field in required_fields if not form_data.get(field)]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            # Transform form data to task data
            task_data = {
                'owner': form_data.get('owner'),
                'plugin': form_data.get('plugin'),
                'action': form_data.get('action', 'run'),
                'type': form_data.get('type', TaskType.ADHOC),
                'args': form_data.get('args', '[]'),
                'kwargs': form_data.get('kwargs', '{}'),
                'execution_start_time': form_data.get('execution_start_time'),
                'execution_end_time': form_data.get('execution_end_time'),
                'interval': form_data.get('interval')
            }
            
            # Validate JSON fields
            try:
                json.loads(task_data['args'])
                json.loads(task_data['kwargs'])
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Invalid JSON in arguments: {str(e)}'
                }
            
            # Create the task
            task_id = self.task_model.create(task_data)
            
            if task_id:
                return {
                    'success': True,
                    'task_id': task_id,
                    'message': f'Task {task_id} created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create task'
                }
                
        except Exception as e:
            logger.error(f"Error creating task from form: {e}")
            return {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }
    
    def get_task_for_editing(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data formatted for editing form"""
        try:
            task = self.task_model.get_by_id(task_id)
            if not task:
                return None
            
            # Format for editing form
            return {
                'id': task.get('id'),
                'owner': task.get('owner', ''),
                'plugin': task.get('plugin', ''),
                'action': task.get('action', 'run'),
                'type': task.get('type', TaskType.ADHOC),
                'args': task.get('args', '[]'),
                'kwargs': task.get('kwargs', '{}'),
                'execution_start_time': task.get('execution_start_time', ''),
                'execution_end_time': task.get('execution_end_time', ''),
                'interval': task.get('interval', ''),
                'status': task.get('status', TaskStatus.CREATED)
            }
        except Exception as e:
            logger.error(f"Error getting task for editing: {e}")
            return None

# Singleton instance
task_frontend_service = TaskFrontendService()
