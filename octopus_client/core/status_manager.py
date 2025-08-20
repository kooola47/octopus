"""
📊 STATUS MANAGER
=================

Manages client status tracking and reporting.
"""

import time
from typing import Dict, Any

class StatusManager:
    """Manages client status and latest task information"""
    
    def __init__(self):
        # Track latest scheduled task and status
        self.latest_task_info = {
            "task": "",
            "status": "",
            "last_run": ""
        }
    
    def update_task_status(self, task_name: str, status: str):
        """Update the latest task information"""
        self.latest_task_info.update({
            "task": task_name,
            "status": status,
            "last_run": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def update_task(self, task_name: str, status: str, description: str = ""):
        """Update task with description support (alias for update_task_status)"""
        self.update_task_status(task_name, status)
        if description:
            # Add description to status if provided
            self.latest_task_info["status"] = f"{status}: {description}"
    
    def get_latest_task_info(self) -> Dict[str, str]:
        """Get the latest task information"""
        return self.latest_task_info.copy()
    
    def tracked_task(self, task_func, task_name: str):
        """Decorator to track task execution status"""
        def wrapper():
            try:
                self.update_task_status(task_name, "Running")
                task_func()
                self.update_task_status(task_name, "Success")
            except Exception as e:
                self.update_task_status(task_name, f"Failed: {e}")
        return wrapper
    
    def get_status_html(self) -> str:
        """Generate HTML status page"""
        return f"""
        <html>
        <head><title>Scheduled Task Status</title></head>
        <body>
            <h2>Latest Scheduled Task</h2>
            <p><b>Task:</b> {self.latest_task_info['task']}</p>
            <p><b>Status:</b> {self.latest_task_info['status']}</p>
            <p><b>Last Run:</b> {self.latest_task_info['last_run']}</p>
        </body>
        </html>
        """
