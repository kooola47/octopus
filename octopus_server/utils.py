import json
import datetime

def get_current_timestamp():
    return datetime.datetime.now().isoformat()

def is_task_completed(status):
    return status in ['Done', 'success', 'failed', 'completed']

def sanitize_string(text, max_length=1000):
    if not text:
        return ""
    text = str(text)
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    return text.strip()

def safe_json_loads(json_str, default=None):
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except:
        return default
