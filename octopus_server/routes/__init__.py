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
from .modern_routes import register_modern_routes
from .user_profile_routes import register_user_profile_routes
from .plugin_routes import register_plugin_routes
from .task_assignment_api_routes import register_task_assignment_api_routes

def register_all_routes(app, global_cache, logger):
    """Register all route modules with the Flask app"""
    register_auth_routes(app, global_cache, logger)  # Register auth routes first
    register_user_routes(app, global_cache, logger)  # Register user routes
    register_dashboard_routes(app, global_cache, logger)
    register_client_api_routes(app, global_cache, logger)
    register_dashboard_api_routes(app, global_cache, logger)
    register_plugin_api_routes(app, global_cache, logger)
    register_nlp_api_routes(app, global_cache, logger)
    register_performance_api_routes(app, global_cache, logger)
    register_cache_api_routes(app, global_cache, logger)
    register_modern_routes(app, global_cache, logger)  # Register modern UI routes
    register_user_profile_routes(app, global_cache, logger)  # Register user profile routes
    register_plugin_routes(app, global_cache, logger)  # Register plugin management routes
    register_task_assignment_api_routes(app, global_cache, logger)  # Register task assignment API
