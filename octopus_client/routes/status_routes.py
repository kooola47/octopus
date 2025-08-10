"""
📊 STATUS ROUTES
================

Flask routes for client status monitoring and reporting.
"""

import time
from flask import jsonify

def register_status_routes(app, cache, logger):
    """Register status monitoring routes with the Flask client app"""

    @app.route("/status", methods=["GET"])
    def client_status():
        """Get current client status including tasks and system info"""
        try:
            login_time = cache.get("login_time", time.time())
            uptime = time.time() - login_time
            
            # Get latest task info from the global state
            from main import latest_task_info
            
            status_data = {
                "status": "running",
                "uptime_seconds": uptime,
                "uptime_human": _format_uptime(uptime),
                "login_time": login_time,
                "latest_task": latest_task_info,
                "timestamp": time.time()
            }
            
            return jsonify(status_data)
            
        except Exception as e:
            logger.error(f"Error getting client status: {e}")
            return jsonify({
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }), 500

    @app.route("/health", methods=["GET"])
    def health_check():
        """Simple health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": time.time()
        })

def _format_uptime(seconds):
    """Format uptime seconds into human readable format"""
    try:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        elif seconds < 86400:
            return f"{seconds//3600}h {(seconds%3600)//60}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    except Exception:
        return str(seconds)
