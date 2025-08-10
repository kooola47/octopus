"""
🐙 OCTOPUS SERVER ROUTES
========================

Route modules for organized Flask application structure.
"""

from .dashboard_routes import register_dashboard_routes
from .client_api_routes import register_client_api_routes
from .dashboard_api_routes import register_dashboard_api_routes
from .plugin_api_routes import register_plugin_api_routes
from .nlp_api_routes import register_nlp_api_routes
from .performance_api_routes import register_performance_api_routes

def register_all_routes(app, cache, logger):
    """Register all route modules with the Flask app"""
    register_dashboard_routes(app, cache, logger)
    register_client_api_routes(app, cache, logger)
    register_dashboard_api_routes(app, cache, logger)
    register_plugin_api_routes(app, cache, logger)
    register_nlp_api_routes(app, cache, logger)
    register_performance_api_routes(app, cache, logger)
