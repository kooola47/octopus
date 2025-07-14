from flask import Flask
from cache import Cache
from config import SERVER_HOST, SERVER_PORT
import os
import logging

from pluginhelper import register_plugin_routes
from heartbeat import register_heartbeat_routes
from flask import render_template_string

app = Flask(__name__)
cache = Cache()

# Setup logs folder and logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("logs/server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("octopus_server")

register_heartbeat_routes(app, cache, logger)
register_plugin_routes(app, logger)

@app.route("/latest-task")
def latest_task():
    # Example: Replace with your actual cache/task retrieval logic
    latest_task = cache.get("latest_task")  # Should return a dict or None
    if not latest_task:
        return render_template_string("""
            <h2>No scheduled tasks found.</h2>
        """)
    return render_template_string("""
        <h2>Latest Scheduled Task</h2>
        <ul>
            <li><strong>Task Name:</strong> {{ task['name'] }}</li>
            <li><strong>Scheduled Time:</strong> {{ task['scheduled_time'] }}</li>
            <li><strong>Status:</strong> {{ task['status'] }}</li>
            <li><strong>Last Execution:</strong> {{ task['last_execution'] }}</li>
        </ul>
    """, task=latest_task)

# ...add more endpoints here if needed...

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
