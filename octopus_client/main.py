import os
import time
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from cache import Cache
from config import HEARTBEAT_INTERVAL
from scheduler import Scheduler

from heartbeat import send_heartbeat
from pluginhelper import check_plugin_updates

cache = Cache()
scheduler = Scheduler()

# Setup logs folder and logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("logs/client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("octopus_client")

# Track latest scheduled task and status
latest_task_info = {
    "task": None,
    "status": None,
    "last_run": None
}

def tracked_task(task_func, task_name):
    def wrapper():
        try:
            latest_task_info["task"] = task_name
            latest_task_info["status"] = "Running"
            latest_task_info["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            task_func()
            latest_task_info["status"] = "Success"
        except Exception as e:
            latest_task_info["status"] = f"Failed: {e}"
    return wrapper

# HTTP handler to show latest scheduled task info
class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html>
            <head><title>Scheduled Task Status</title></head>
            <body>
                <h2>Latest Scheduled Task</h2>
                <p><b>Task:</b> {latest_task_info['task']}</p>
                <p><b>Status:</b> {latest_task_info['status']}</p>
                <p><b>Last Run:</b> {latest_task_info['last_run']}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_status_server():
    server = HTTPServer(('0.0.0.0', 8080), StatusHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info("Status page available at http://localhost:8080/status")

def run():
    cache.set("login_time", time.time())
    # Wrap tasks to track their status
    scheduler.add_task(tracked_task(send_heartbeat, "send_heartbeat"), HEARTBEAT_INTERVAL)
    scheduler.add_task(tracked_task(check_plugin_updates, "check_plugin_updates"), 60)
    start_status_server()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()
