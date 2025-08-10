"""
🐙 OCTOPUS CLIENT ROUTES
========================

Route modules for organized Flask client application structure.
"""

from .task_api_routes import register_task_api_routes
from .status_routes import register_status_routes

def register_all_routes(app, cache, logger):
    """Register all route modules with the Flask client app"""
    register_task_api_routes(app, cache, logger)
    register_status_routes(app, cache, logger)
