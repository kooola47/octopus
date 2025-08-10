"""
📈 PERFORMANCE API ROUTES
=========================

Flask routes for performance monitoring APIs.
"""

from flask import jsonify
from performance_monitor import monitor

def register_performance_api_routes(app, cache, logger):
    """Register performance API routes with the Flask app"""

    @app.route("/api/performance", methods=["GET"])
    def api_performance():
        """API endpoint to get performance statistics"""
        return jsonify(monitor.get_stats())
