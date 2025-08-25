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
from .auth_routes import register_auth_routes
from .user_routes import register_user_routes
from .cache_api_routes import register_cache_api_routes

def register_all_routes(app, global_cache, logger):
    """Register all route modules with the Flask app"""
    register_auth_routes(app, global_cache, logger)  # Register auth routes first
    register_user_routes(app)  # Register user routes
    register_dashboard_routes(app, global_cache, logger)
    register_client_api_routes(app, global_cache, logger)
    register_dashboard_api_routes(app, global_cache, logger)
    register_plugin_api_routes(app, global_cache, logger)
    register_nlp_api_routes(app, global_cache, logger)
    register_performance_api_routes(app, global_cache, logger)
    register_cache_api_routes(app, global_cache, logger)
