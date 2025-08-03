import requests
from config import SERVER_URL

def get_tasks():
    resp = requests.get(f"{SERVER_URL}/tasks", timeout=10)
    resp.raise_for_status()
    return resp.json()

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

