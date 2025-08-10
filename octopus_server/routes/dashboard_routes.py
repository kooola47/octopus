"""
🏠 WEB DASHBOARD ROUTES
======================

Flask routes for the web dashboard interface.
"""

import json
import urllib.parse
import sqlite3
import time
from flask import request, render_template, redirect, url_for, render_template_string
from dbhelper import (
    get_tasks, add_task, update_task, delete_task,
    get_owner_options, assign_all_tasks,
    compute_task_status, get_active_clients, get_db_file,
    get_plugin_names, add_execution_result
)
from performance_monitor import get_performance_report

def register_dashboard_routes(app, cache, logger):
    """Register dashboard routes with the Flask app"""

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        """Redirect old dashboard to modern dashboard"""
        from flask import redirect, url_for
        return redirect(url_for('modern_dashboard'))

    @app.route("/tasks-ui/delete/<task_id>")
    def delete_task_ui(task_id):
        """Delete a task and redirect back to the dashboard with the appropriate tab."""
        try:
            delete_task(task_id)
            logger.info(f"Task {task_id} deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
        
        # Get the tab parameter, default to 'tasks'
        tab = request.args.get('tab', 'tasks')
        return redirect(url_for("dashboard", tab=tab))

    @app.route("/nlp-test")
    def nlp_test_page():
        """NLP test page for natural language task creation"""
        return render_template("nlp_test.html")

    @app.route("/confidence-guide")
    def confidence_guide():
        """Guide for improving NLP confidence levels"""
        return render_template("confidence_guide.html")

    @app.route("/performance-report")
    def performance_report():
        """Human-readable performance report"""
        report = get_performance_report()
        return f"<pre>{report}</pre>"
