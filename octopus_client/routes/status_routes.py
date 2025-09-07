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

    @app.route("/user-params", methods=["GET"])
    def get_user_params():
        """Return user parameters organized by category"""
        try:
            from global_cache_manager import get_params_summary, get_params, list_param_categories
            
            # Get organized summary
            summary = get_params_summary()
            
            # Get all parameters organized by category
            all_params = get_params()
            
            # Format for better display
            formatted_params = {}
            for category, params in all_params.items():
                formatted_params[category] = {}
                for param_name, param_data in params.items():
                    if isinstance(param_data, dict):
                        # Show value but mask sensitive data
                        value = param_data.get('value', '')
                        if param_data.get('type') == 'string' and len(str(value)) > 20:
                            # Likely sensitive data, mask it
                            value = f"{str(value)[:4]}...{str(value)[-4:]}" if len(str(value)) > 8 else "***"
                        
                        formatted_params[category][param_name] = {
                            "value": value,
                            "type": param_data.get('type', 'string'),
                            "description": param_data.get('description', ''),
                            "is_set": param_data.get('value') is not None
                        }
                    else:
                        formatted_params[category][param_name] = {
                            "value": param_data,
                            "type": "unknown",
                            "description": "",
                            "is_set": param_data is not None
                        }
            
            return jsonify({
                "status": "ok",
                "summary": summary,
                "parameters": formatted_params,
                "categories": list_param_categories(),
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Error getting user parameters: {e}")
            return jsonify({"status": "error", "error": str(e), "timestamp": time.time()}), 500

    @app.route("/user-params/<category>", methods=["GET"])
    def get_user_params_category(category):
        """Return user parameters for a specific category"""
        try:
            from global_cache_manager import get_params
            
            params = get_params(category)
            
            # Format the response
            formatted_params = {}
            for param_name, param_data in params.items():
                if isinstance(param_data, dict):
                    # Show value but mask sensitive data
                    value = param_data.get('value', '')
                    if param_data.get('type') == 'string' and len(str(value)) > 20:
                        # Likely sensitive data, mask it
                        value = f"{str(value)[:4]}...{str(value)[-4:]}" if len(str(value)) > 8 else "***"
                    
                    formatted_params[param_name] = {
                        "value": value,
                        "type": param_data.get('type', 'string'),
                        "description": param_data.get('description', ''),
                        "is_set": param_data.get('value') is not None
                    }
                else:
                    formatted_params[param_name] = {
                        "value": param_data,
                        "type": "unknown", 
                        "description": "",
                        "is_set": param_data is not None
                    }
            
            return jsonify({
                "status": "ok",
                "category": category,
                "parameters": formatted_params,
                "param_count": len(formatted_params),
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Error getting user parameters for category {category}: {e}")
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
