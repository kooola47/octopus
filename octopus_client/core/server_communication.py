"""
🌐 SERVER COMMUNICATION MANAGER
===============================

Handles all communication with the Octopus server including commands and heartbeat.
"""

import time
import requests
import importlib
from taskmanager import get_tasks
from utils import get_hostname
from typing import Dict, Any, List

class ServerCommunicator:
    """Manages server communication and command handling"""
    
    def __init__(self, server_url: str, task_check_interval: int, retry_delay: int, logger):
        self.server_url = server_url
        self.task_check_interval = task_check_interval
        self.retry_delay = retry_delay
        self.logger = logger
    
    def handle_server_commands(self):
        """Poll server for commands and execute them"""
        hostname = get_hostname()
        while True:
            try:
                resp = requests.get(f"{self.server_url}/commands/{hostname}", timeout=5)
                if resp.status_code == 200:
                    commands = resp.json()
                    for cmd in commands:
                        self._execute_command(cmd)
                # Poll for new tasks
                time.sleep(self.task_check_interval)
            except Exception as e:
                self.logger.error(f"Command polling failed: {e}")
                time.sleep(self.retry_delay)
    
    def _execute_command(self, cmd: Dict[str, Any]):
        """Execute a single command from the server"""
        plugin_name = cmd.get("plugin")
        action = cmd.get("action")
        args = cmd.get("args", [])
        kwargs = cmd.get("kwargs", {})
        
        try:
            module = importlib.import_module(f"plugins.{plugin_name}")
            func = getattr(module, action, None)
            if callable(func):
                func(*args, **kwargs)
                self.logger.info(f"Executed {plugin_name}.{action} with args={args}, kwargs={kwargs}")
            else:
                self.logger.error(f"Action {action} not found in plugin {plugin_name}")
        except Exception as e:
            self.logger.error(f"Failed to execute plugin {plugin_name}: {e}")
    
    def fetch_tasks(self) -> List[Dict[str, Any]]:
        """Fetch tasks from the server"""
        try:
            tasks = get_tasks()
            self.logger.info(f"Fetched {len(tasks)} tasks from server")
            return tasks
        except Exception as e:
            self.logger.error(f"Failed to fetch tasks: {e}")
            return []
    
    def claim_task(self, task_id: str, username: str) -> bool:
        """Claim an ALL task for execution"""
        update = {
            "executor": username,
            "status": "Active",
            "updated_at": time.time()
        }
        try:
            requests.put(f"{self.server_url}/tasks/{task_id}", json=update, timeout=5)
            self.logger.info(f"Picked up ALL task {task_id} as executor {username}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pick up ALL task {task_id}: {e}")
            return False
