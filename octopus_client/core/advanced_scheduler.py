"""
🗓️ ADVANCED TASK SCHEDULER
==========================

APScheduler-based task scheduling system for reliable task execution.
Handles both adhoc (one-time) and scheduled (recurring) tasks.
"""

import time
import requests
from constants import TaskStatus, ExecutionStatus
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED


class AdvancedTaskScheduler:
    """Advanced task scheduler using APScheduler"""
    
    def __init__(self, server_url: str, username: str, task_executor, logger):
        self.server_url = server_url
        self.username = username
        self.task_executor = task_executor
        self.logger = logger
        
        # Initialize APScheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
        
        # Track scheduled jobs
        self.scheduled_jobs = {}  # task_id -> job_id mapping
        
        # Start scheduler
        self.scheduler.start()
        self.logger.info("Advanced Task Scheduler initialized with APScheduler")
    
    def start(self):
        """Start the task scheduling system"""
        self.logger.info("Starting Advanced Task Scheduler...")
        
        # Continuously sync with server for new tasks
        try:
            while True:
                self._sync_tasks_with_server()
                time.sleep(10)  # Check for new tasks every 10 seconds
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the scheduler and cleanup"""
        self.logger.info("Stopping Advanced Task Scheduler...")
        self.scheduler.shutdown(wait=True)
    
    def _sync_tasks_with_server(self):
        """Sync tasks from server and schedule them appropriately"""
        try:
            # Get tasks assigned to this client
            response = requests.get(f"{self.server_url}/client-tasks", 
                                  params={"client": self.username, "status": TaskStatus.RUNNING}, 
                                  timeout=5)
            
            if response.status_code == 200:
                response_data = response.json()
                self.logger.debug(f"Raw server response: {response_data}")
                
                # Extract tasks from the response (client-tasks returns {"tasks": [...], "pagination": {...}})
                if isinstance(response_data, dict):
                    tasks = response_data.get("tasks", [])
                elif isinstance(response_data, list):
                    # Fallback if server returns tasks directly as array
                    tasks = response_data
                else:
                    self.logger.error(f"Unexpected response format: {type(response_data)}")
                    return
                
                self.logger.info(f"Fetched {len(tasks)} active tasks from server for client {self.username}")
                
                for task in tasks:
                    if isinstance(task, dict):  # Ensure task is a dictionary
                        self._process_server_task(task)
                    else:
                        self.logger.warning(f"Invalid task format received: {type(task)} - {task}")
            else:
                self.logger.warning(f"Failed to fetch tasks from server: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error syncing tasks with server: {e}")
        except Exception as e:
            self.logger.error(f"Error syncing tasks with server: {e}")
            import traceback
            self.logger.debug(f"Full error traceback: {traceback.format_exc()}")
    
    def _process_server_task(self, task: Dict[str, Any]):
        """Process a task from server and schedule it appropriately"""
        task_id = str(task.get("id", ""))
        if not task_id:
            self.logger.warning("Task missing ID, skipping")
            return
            
        task_type = task.get("type", "adhoc").lower()
        status = task.get("status")
        owner = task.get("owner")
        executor = task.get("executor")
        
        self.logger.debug(f"Processing task {task_id}: type={task_type}, status={status}, owner={owner}, executor={executor}")
        
        # Skip if task is not running
        if status != TaskStatus.RUNNING:
            # Remove from scheduler if it exists
            if task_id in self.scheduled_jobs:
                self._remove_scheduled_task(task_id)
                self.logger.info(f"Removed inactive task {task_id} from scheduler")
            return
        
        # Skip if already scheduled
        if task_id in self.scheduled_jobs:
            self.logger.debug(f"Task {task_id} already scheduled, skipping")
            return
        
        # Schedule based on task type
        if task_type == "adhoc":
            self._schedule_adhoc_task(task)
        elif task_type in ["schedule", "scheduled"]:
            self._schedule_recurring_task(task)
        else:
            self.logger.warning(f"Unknown task type: {task_type} for task {task_id}")
    
    def _schedule_adhoc_task(self, task: Dict[str, Any]):
        """Schedule a one-time adhoc task"""
        task_id = task.get("id")
        start_time = task.get("execution_start_time")
        
        try:
            # Parse start time
            if start_time:
                if isinstance(start_time, str):
                    try:
                        start_ts = float(start_time)
                        run_date = datetime.fromtimestamp(start_ts)
                    except ValueError:
                        # Parse datetime-local format
                        run_date = datetime.fromisoformat(start_time.replace('T', ' '))
                else:
                    run_date = datetime.fromtimestamp(float(start_time))
            else:
                # Run immediately if no start time specified
                run_date = datetime.now()
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=self._execute_task_job,
                trigger=DateTrigger(run_date=run_date),
                args=[task],
                id=f"adhoc_{task_id}",
                name=f"Adhoc Task {task_id}",
                misfire_grace_time=60  # Allow 60 seconds grace for missed jobs
            )
            
            self.scheduled_jobs[task_id] = job.id
            self.logger.info(f"Scheduled adhoc task {task_id} for {run_date}")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule adhoc task {task_id}: {e}")
    
    def _schedule_recurring_task(self, task: Dict[str, Any]):
        """Schedule a recurring scheduled task"""
        task_id = task.get("id")
        interval = task.get("interval")
        start_time = task.get("execution_start_time")
        end_time = task.get("execution_end_time")
        
        try:
            # Parse times
            start_date = None
            if start_time:
                if isinstance(start_time, str):
                    try:
                        start_ts = float(start_time)
                        start_date = datetime.fromtimestamp(start_ts)
                    except ValueError:
                        start_date = datetime.fromisoformat(start_time.replace('T', ' '))
                else:
                    start_date = datetime.fromtimestamp(float(start_time))
            
            end_date = None
            if end_time:
                if isinstance(end_time, str):
                    try:
                        end_ts = float(end_time)
                        end_date = datetime.fromtimestamp(end_ts)
                    except ValueError:
                        end_date = datetime.fromisoformat(end_time.replace('T', ' '))
                else:
                    end_date = datetime.fromtimestamp(float(end_time))
            
            # Create interval trigger
            if interval:
                interval_seconds = int(float(interval))
                trigger = IntervalTrigger(
                    seconds=interval_seconds,
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                self.logger.warning(f"No interval specified for scheduled task {task_id}")
                return
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=self._execute_task_job,
                trigger=trigger,
                args=[task],
                id=f"scheduled_{task_id}",
                name=f"Scheduled Task {task_id}",
                misfire_grace_time=60
            )
            
            self.scheduled_jobs[task_id] = job.id
            self.logger.info(f"Scheduled recurring task {task_id} with {interval_seconds}s interval")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule recurring task {task_id}: {e}")
    
    def _remove_scheduled_task(self, task_id: str):
        """Remove a task from scheduler"""
        if task_id in self.scheduled_jobs:
            job_id = self.scheduled_jobs[task_id]
            try:
                self.scheduler.remove_job(job_id)
                del self.scheduled_jobs[task_id]
                self.logger.info(f"Removed scheduled task {task_id}")
            except Exception as e:
                self.logger.error(f"Failed to remove scheduled task {task_id}: {e}")
    
    def _execute_task_job(self, task: Dict[str, Any]):
        """Execute a scheduled task job"""
        task_id = str(task.get("id", ""))
        if not task_id:
            self.logger.error("Task missing ID, cannot execute")
            return
            
        task_type = task.get("type", "adhoc").lower()
        
        self.logger.info(f"Executing scheduled task {task_id} (type: {task_type})")
        
        # Create a unique execution ID for this execution
        execution_id = f"{task_id}_{self.username}_{int(time.time() * 1000)}"
        
        try:
            # Create initial execution record with running status
            self._create_execution_record(execution_id, task_id, ExecutionStatus.RUNNING, "Task execution started")
            
            # Execute the task
            exec_status, result = self.task_executor.execute_task(task, task_id, self.username)
            
            # Map execution status to standardized values using constants
            final_status = ExecutionStatus.SUCCESS if exec_status == ExecutionStatus.SUCCESS else ExecutionStatus.FAILED
            
            # Update the same execution record with final status
            self._update_execution_record(execution_id, final_status, result)
            
            # Update task status to final state after execution
            if exec_status == ExecutionStatus.SUCCESS:
                self._update_task_status(task_id, TaskStatus.COMPLETED, result)
            else:
                self._update_task_status(task_id, TaskStatus.FAILED, result)
            
            # For adhoc tasks, also remove from scheduler
            if task_type == "adhoc":
                self._remove_scheduled_task(task_id)
            
            self.logger.info(f"Task {task_id} execution completed: {final_status}")
            
        except Exception as e:
            self.logger.error(f"Error executing scheduled task {task_id}: {e}")
            # Update the same execution record with failed status
            self._update_execution_record(execution_id, ExecutionStatus.FAILED, str(e))
            
            # Update task status to failed on error
            self._update_task_status(task_id, TaskStatus.FAILED, str(e))
            
            # For adhoc tasks, also remove from scheduler
            if task_type == "adhoc":
                self._remove_scheduled_task(task_id)
    
    def _create_execution_record(self, execution_id: str, task_id: str, status: str, result: str):
        """Create a new execution record on server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/execution-results",
                data={
                    "execution_id": execution_id,
                    "task_id": task_id,
                    "client": self.username,
                    "exec_status": status,
                    "exec_result": result
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info(f"Created execution record {execution_id} for task {task_id}: {status}")
            else:
                self.logger.warning(f"Failed to create execution record: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error creating execution record for task {task_id}: {e}")
    
    def _update_execution_record(self, execution_id: str, status: str, result: str):
        """Update an existing execution record on server - uses same POST endpoint with same execution_id"""
        try:
            # Use the same POST endpoint but with the same execution_id
            # The server will handle it as an update operation
            task_id = execution_id.split('_')[0]  # Extract task_id from execution_id
            
            response = requests.post(
                f"{self.server_url}/api/execution-results",
                data={
                    "execution_id": execution_id,
                    "task_id": task_id,
                    "client": self.username,
                    "exec_status": status,
                    "exec_result": result
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info(f"Updated execution record {execution_id}: {status}")
            else:
                self.logger.warning(f"Failed to update execution record: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error updating execution record {execution_id}: {e}")
    
    def _update_task_status(self, task_id: str, status: str, result: str):
        """Update task status on server"""
        try:
            update = {
                "status": status,
                "result": result,
                "executor": self.username,
                "updated_at": time.time()
            }
            
            response = requests.put(f"{self.server_url}/tasks/{task_id}", json=update, timeout=5)
            
            if response.status_code == 200:
                self.logger.info(f"Updated task {task_id} status to {status}")
            else:
                self.logger.warning(f"Failed to update task status: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error updating task status for task {task_id}: {e}")
    
    def _job_listener(self, event):
        """Listen to job events for monitoring"""
        if event.exception:
            self.logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            self.logger.debug(f"Job {event.job_id} executed successfully")
    
    def get_scheduled_jobs_info(self):
        """Get information about currently scheduled jobs"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs_info
    
    def add_background_task(self, func, interval_seconds: int, task_name: Optional[str] = None, **kwargs):
        """
        Add a background task that runs at regular intervals
        
        Args:
            func: Function to execute
            interval_seconds: Interval in seconds between executions
            task_name: Name for the task (defaults to function name)
            **kwargs: Additional arguments to pass to the function
        
        Returns:
            str: Job ID of the scheduled task
        """
        if task_name is None:
            task_name = func.__name__
        
        job = self.scheduler.add_job(
            func=func,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=f"background_{task_name}",
            name=f"Background: {task_name}",
            replace_existing=True,
            kwargs=kwargs
        )
        
        self.logger.info(f"Added background task '{task_name}' with {interval_seconds}s interval")
        return job.id
    
    def remove_background_task(self, task_name: str):
        """Remove a background task by name"""
        job_id = f"background_{task_name}"
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f"Removed background task '{task_name}'")
        except Exception as e:
            self.logger.warning(f"Could not remove background task '{task_name}': {e}")
