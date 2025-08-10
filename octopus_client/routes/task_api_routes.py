"""
🔧 TASK API ROUTES
==================

Flask routes for task management API endpoints.
"""

from flask import request, jsonify
from taskmanager import get_tasks, add_task, update_task, delete_task

def register_task_api_routes(app, cache, logger):
    """Register task API routes with the Flask client app"""

    @app.route("/tasks", methods=["GET", "POST"])
    def tasks():
        """Handle task operations - GET to retrieve tasks, POST to add new tasks"""
        if request.method == "POST":
            task = request.json
            task_id = add_task(task)
            return jsonify({"id": task_id})
        return jsonify(get_tasks())

    @app.route("/tasks/<task_id>", methods=["PUT", "DELETE"])
    def task_ops(task_id):
        """Handle individual task operations - PUT to update, DELETE to remove"""
        if request.method == "PUT":
            updates = request.json
            ok = update_task(task_id, updates)
            return jsonify({"success": ok})
        elif request.method == "DELETE":
            ok = delete_task(task_id)
            return jsonify({"success": ok})
        # Ensure a response is always returned
        return jsonify({"error": "Method not allowed"}), 405
