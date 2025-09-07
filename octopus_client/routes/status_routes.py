"""
📊 STATUS ROUTES
================

Flask routes for client status monitoring and reporting.
"""

import time
from flask import jsonify
from constants import ExecutionStatus

def register_status_routes(app, cache, logger):
    @app.route("/config", methods=["GET"])
    def get_config():
        """Return current configuration values as JSON"""
        try:
            from config import get_current_config
            config_obj = get_current_config()
            config_dict = {k: getattr(config_obj, k) for k in dir(config_obj) if k.isupper() and not k.startswith('_')}
            return jsonify({"status": "ok", "config": config_dict, "timestamp": time.time()})
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({"status": "error", "error": str(e), "timestamp": time.time()}), 500
    @app.route("/cache/all", methods=["GET"])
    def get_all_cache():
        """Return all cache data from the client-side cache"""
        try:
            all_cache = cache.all()
            return jsonify({"status": "ok", "cache": all_cache, "timestamp": time.time()})
        except Exception as e:
            logger.error(f"Error getting all cache data: {e}")
            return jsonify({"status": "error", "error": str(e), "timestamp": time.time()}), 500
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
                "status": ExecutionStatus.RUNNING,
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
