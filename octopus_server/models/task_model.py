#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Task Model
=============================

Task model for managing task operations and business logic.
Handles all task-related database operations separately from other models.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from .base_model import BaseModel
from constants import TaskStatus, TaskOwnership, TaskType

logger = logging.getLogger(__name__)

class TaskModel(BaseModel):
    """Task model for task management operations"""
    
    TABLE_NAME = "tasks"
    REQUIRED_FIELDS = ["owner", "plugin", "action"]
    
    def init_table(self):
        """Initialize the tasks table"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        owner TEXT NOT NULL,
                        plugin TEXT NOT NULL,
                        action TEXT NOT NULL DEFAULT 'run',
                        args TEXT DEFAULT '[]',
                        kwargs TEXT DEFAULT '{}',
                        type TEXT DEFAULT 'Adhoc',
                        execution_start_time TEXT,
                        execution_end_time TEXT,
                        interval TEXT,
                        status TEXT DEFAULT 'Created',
                        executor TEXT DEFAULT '',
                        result TEXT DEFAULT '',
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_plugin ON tasks(plugin)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_executor ON tasks(executor)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at)')
                
                conn.commit()
                logger.info("Tasks table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing tasks table: {e}")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate task data"""
        if not self._validate_required_fields(data):
            return False
        
        # Validate owner
        if data.get('owner') not in [TaskOwnership.ALL, TaskOwnership.ANYONE] and not isinstance(data.get('owner'), str):
            logger.error(f"Invalid owner: {data.get('owner')}")
            return False
        
        # Validate type
        if data.get('type') and data['type'] not in [TaskType.ADHOC, TaskType.SCHEDULED, TaskType.INTERVAL]:
            logger.error(f"Invalid task type: {data.get('type')}")
            return False
        
        # Validate status
        valid_statuses = [TaskStatus.CREATED, TaskStatus.ACTIVE, TaskStatus.DONE, 
                         TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.COMPLETED]
        if data.get('status') and data['status'] not in valid_statuses:
            logger.error(f"Invalid task status: {data.get('status')}")
            return False
        
        # Validate JSON fields
        try:
            if data.get('args') and isinstance(data['args'], str):
                json.loads(data['args'])
            if data.get('kwargs') and isinstance(data['kwargs'], str):
                json.loads(data['kwargs'])
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in task data: {e}")
            return False
        
        return True
    
    def _create_record(self, conn, data: Dict[str, Any]) -> Optional[str]:
        """Create a new task record"""
        task_id = data.get("id") or str(int(time.time() * 1000))
        data = self._add_timestamps(data)
        
        # Set defaults
        data.setdefault('action', 'run')
        data.setdefault('args', '[]')
        data.setdefault('kwargs', '{}')
        data.setdefault('type', TaskType.ADHOC)
        data.setdefault('status', TaskStatus.CREATED)
        data.setdefault('executor', '')
        data.setdefault('result', '')
        
        # Convert lists/dicts to JSON strings if needed
        if isinstance(data.get('args'), list):
            data['args'] = json.dumps(data['args'])
        if isinstance(data.get('kwargs'), dict):
            data['kwargs'] = json.dumps(data['kwargs'])
        
        conn.execute('''
            INSERT OR REPLACE INTO tasks 
            (id, owner, plugin, action, args, kwargs, type, execution_start_time, 
             execution_end_time, interval, status, executor, result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            data['owner'],
            data['plugin'],
            data['action'],
            data['args'],
            data['kwargs'],
            data['type'],
            data.get('execution_start_time'),
            data.get('execution_end_time'),
            data.get('interval'),
            data['status'],
            data['executor'],
            data['result'],
            data['created_at'],
            data['updated_at']
        ))
        conn.commit()
        
        logger.info(f"Created task {task_id} for plugin {data['plugin']}")
        return task_id
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all tasks with a specific status"""
        return self.get_all({"status": status})
    
    def get_tasks_by_owner(self, owner: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific owner"""
        return self.get_all({"owner": owner})
    
    def get_tasks_by_plugin(self, plugin: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific plugin"""
        return self.get_all({"plugin": plugin})
    
    def get_tasks_by_executor(self, executor: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a specific executor"""
        return self.get_all({"executor": executor})
    
    def assign_task_to_executor(self, task_id: str, executor: str) -> bool:
        """Assign a task to a specific executor"""
        return self.update(task_id, {
            "executor": executor,
            "status": TaskStatus.ACTIVE
        })
    
    def complete_task(self, task_id: str, status: str, result: str = "") -> bool:
        """Mark a task as completed with result"""
        valid_completion_statuses = [TaskStatus.DONE, TaskStatus.SUCCESS, 
                                   TaskStatus.FAILED, TaskStatus.COMPLETED]
        if status not in valid_completion_statuses:
            logger.error(f"Invalid completion status: {status}")
            return False
        
        return self.update(task_id, {
            "status": status,
            "result": result,
            "execution_end_time": time.time()
        })
    
    def get_available_tasks_for_assignment(self) -> List[Dict[str, Any]]:
        """Get tasks that are available for assignment (status=Created)"""
        return self.get_tasks_by_status(TaskStatus.CREATED)
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        return self.get_tasks_by_status(TaskStatus.ACTIVE)
    
    def get_tasks_with_executions(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks with their execution history"""
        from .execution_model import ExecutionModel
        
        tasks = self.get_all()
        execution_model = ExecutionModel()
        
        tasks_dict = {}
        for task in tasks:
            task_executions = execution_model.get_executions_by_task(task['id'])
            task['executions'] = task_executions
            tasks_dict[task['id']] = task
        
        return tasks_dict
    
    def is_task_completed(self, task_id: str) -> bool:
        """Check if a task is completed"""
        task = self.get_by_id(task_id)
        if not task:
            return False
        
        completed_statuses = [TaskStatus.DONE, TaskStatus.SUCCESS, 
                            TaskStatus.FAILED, TaskStatus.COMPLETED]
        return task.get('status') in completed_statuses
    
    def delete_task_cascade(self, task_id: str) -> bool:
        """Delete a task and all its executions"""
        from .execution_model import ExecutionModel
        
        try:
            # Delete executions first
            execution_model = ExecutionModel()
            execution_model.delete_executions_by_task(task_id)
            
            # Delete the task
            return self.delete(task_id)
        except Exception as e:
            logger.error(f"Error deleting task {task_id} with cascade: {e}")
            return False

# Singleton instance
task_model = TaskModel()