"""
CACHE API ROUTES
================

Flask routes for cache-related API endpoints (migrated from modern_routes.py).
"""


from flask import request, jsonify
import logging
from .get_requesting_user_identity import get_requesting_user_identity

def register_cache_api_routes(app, global_cache, logger):
    @app.route("/api/cache/broadcast", methods=["GET"])
    def api_get_broadcast_cache():
        """Get data that should be broadcast to all clients"""
        try:
            broadcast_data = global_cache.get_broadcast_data()
            return jsonify(broadcast_data)
        except Exception as e:
            logger.error(f"Error getting broadcast cache: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/cache/stats", methods=["GET"])
    def api_get_cache_stats():
        """Get cache statistics"""
        try:
            stats = global_cache.get_stats()
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return jsonify({"error": str(e)}), 500
    """Register cache API routes with the Flask app"""

    @app.route("/api/cache/all", methods=["GET"])
    def api_get_all_cache_data():
        """Get all cache data (admin endpoint)"""
        try:
            include_plugins = request.args.get('include_plugins', 'false').lower() == 'true'
            all_data = global_cache.get_all_data(include_plugins)
            return jsonify(all_data)
        except Exception as e:
            logger.error(f"Error getting all cache data: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/cache/user/<username>/profile", methods=["GET"])
    def api_get_user_profile_cache(username):
        """Get user profile cache data"""
        try:
            client_id = request.headers.get('X-Client-ID') or request.args.get('client_id')
            requesting_user = get_requesting_user_identity(logger)
            logger.info(f"Requesting user for profile {username}: {requesting_user} : {client_id}")
            profile_data = global_cache.get_user_profile_data(username, requesting_user)
            if profile_data is None:
                if requesting_user and requesting_user != username and not global_cache._is_admin_user(requesting_user):
                    return jsonify({"error": "Access denied: You can only access your own profile data"}), 403
                else:
                    return jsonify({"error": "Profile not found"}), 404
            return jsonify(profile_data)
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
        except Exception as e:
            logger.error(f"Error getting user profile cache for {username}: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/cache/user/<username>/profile", methods=["POST"])
    def api_set_user_profile_cache(username):
        """Set user profile cache data"""
        try:
            requesting_user = get_requesting_user_identity(logger)
            data = request.get_json()
            if not data:
                return jsonify({"error": "Profile data is required"}), 400
            ttl = data.get('_ttl', 3600)  # Default 1 hour
            profile_data = {k: v for k, v in data.items() if k != '_ttl'}
            global_cache.set_user_profile_data(username, profile_data, ttl, requesting_user)
            return jsonify({"message": "User profile cache updated successfully"})
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
        except Exception as e:
            logger.error(f"Error setting user profile cache for {username}: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/cache/broadcast/<key>", methods=["POST"])
    def api_broadcast_to_clients(key):
        """Broadcast data to all clients"""
        try:
            data = request.get_json()
            if not data or 'value' not in data:
                return jsonify({"error": "Value is required"}), 400
            ttl = data.get('ttl')
            global_cache.broadcast_to_clients(key, data['value'], ttl)
            return jsonify({"message": "Data broadcast successfully"})
        except Exception as e:
            logger.error(f"Error broadcasting {key}: {e}")
            return jsonify({"error": str(e)}), 500
