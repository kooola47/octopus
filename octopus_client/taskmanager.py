import requests
import logging
from config import SERVER_URL

logger = logging.getLogger("octopus_client.taskmanager")

def get_tasks():
    """
    Get tasks from server, excluding completed/finished tasks.
    Uses server-side filtering to avoid downloading unnecessary data.
    """
    # Request only active/pending tasks from server
    url = f"{SERVER_URL}/tasks?exclude_finished=true"
    logger.info(f"Requesting tasks from: {url}")
    
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    tasks = resp.json()
    
    task_count = len(tasks) if isinstance(tasks, (dict, list)) else 'unknown count'
    logger.info(f"Retrieved {task_count} active tasks from server")
    return tasks

def add_task(task):
    resp = requests.post(f"{SERVER_URL}/tasks", json=task, timeout=10)
    resp.raise_for_status()
    return resp.json().get("id")

def update_task(task_id, updates):
    resp = requests.put(f"{SERVER_URL}/tasks/{task_id}", json=updates, timeout=10)
    resp.raise_for_status()
    return resp.json().get("success", False)

def delete_task(task_id):
    resp = requests.delete(f"{SERVER_URL}/tasks/{task_id}", timeout=10)
    resp.raise_for_status()
    return resp.json().get("success", False)

