"""
🔌 PLUGIN API ROUTES
===================

Flask routes for plugin-related APIs.
"""

import inspect
import importlib
import os
import sys
from typing import List
from flask import request, jsonify
from dbhelper import get_plugin_names
from services.performance_monitor import time_request

def _setup_plugin_paths():
    """Setup sys.path for proper plugin and dependency imports"""
    # Get current server directory
    server_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # octopus_server
    client_path = os.path.join(os.path.dirname(server_path), 'octopus_client')  # octopus_client
    root_path = os.path.dirname(server_path)  # project root
    
    # Plugin paths
    server_plugins_path = os.path.join(server_path, 'plugins')
    client_plugins_path = os.path.join(client_path, 'plugins')
    
    # Routes paths for imports like user_profile_routes
    server_routes_path = os.path.join(server_path, 'routes')
    
    # Add all necessary paths
    paths_to_add = [
        server_path, client_path, root_path,
        server_plugins_path, client_plugins_path, 
        server_routes_path
    ]
    
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)

def _import_plugin_with_fallback(plugin_name):
    """
    Import plugin with fallback mechanisms for better compatibility
    Tries multiple import strategies to handle user-created libraries
    """
    import importlib.util
    
    # Strategy 1: Try standard import with plugins prefix
    try:
        return importlib.import_module(f"plugins.{plugin_name}")
    except ImportError as e1:
        pass
    
    # Strategy 2: Try direct import (for plugins in sys.path)
    try:
        return importlib.import_module(plugin_name)
    except ImportError as e2:
        pass
    
    # Strategy 3: Try file-based loading from both client and server plugins
    server_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client_path = os.path.join(os.path.dirname(server_path), 'octopus_client')
    
    plugin_locations = [
        os.path.join(server_path, 'plugins', f"{plugin_name}.py"),
        os.path.join(client_path, 'plugins', f"{plugin_name}.py")
    ]
    
    for plugin_path in plugin_locations:
        if os.path.exists(plugin_path):
            try:
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # Add to sys.modules for potential imports by the plugin
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)
                    return module
            except Exception as e3:
                continue
    
    return None

def register_plugin_api_routes(app, global_cache, logger):
    """Register plugin API routes with the Flask app"""
    
    # Setup paths once when routes are registered
    _setup_plugin_paths()

    @app.route("/api/plugin-functions", methods=["GET"])
    def api_plugin_functions():
        """API endpoint to get function signatures for plugins"""
        plugin_name = request.args.get('plugin')
        if not plugin_name:
            return jsonify({"error": "Plugin parameter required"}), 400
        
        try:
            # Enhanced plugin import with folder-based loading
            module = _import_plugin_with_fallback(plugin_name)
            if not module:
                return jsonify({"error": f"Failed to import plugin {plugin_name}"}), 404
            
            # Get all callable functions from the module
            functions = {}
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                # Skip private functions
                if name.startswith('_'):
                    continue
                    
                try:
                    # Get function signature
                    sig = inspect.signature(obj)
                    parameters = {}
                    
                    for param_name, param in sig.parameters.items():
                        param_info = {
                            "name": param_name,
                            "required": param.default == inspect.Parameter.empty,
                            "type": "str"  # Default type
                        }
                        
                        # Try to get type hints
                        if param.annotation != inspect.Parameter.empty:
                            param_info["type"] = getattr(param.annotation, '__name__', str(param.annotation))
                        
                        # Get default value
                        if param.default != inspect.Parameter.empty:
                            param_info["default"] = param.default
                        
                        parameters[param_name] = param_info
                    
                    functions[name] = {
                        "parameters": parameters,
                        "docstring": inspect.getdoc(obj) or "No description available"
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not inspect function {name}: {e}")
                    functions[name] = {
                        "parameters": {},
                        "docstring": "Function signature could not be determined"
                    }
            
            return jsonify({"functions": functions})
            
        except ImportError:
            return jsonify({"error": f"Plugin '{plugin_name}' not found"}), 404
        except Exception as e:
            logger.error(f"Error inspecting plugin {plugin_name}: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/plugin-examples", methods=["GET"])
    def api_plugin_examples():
        """API endpoint to get dynamic examples based on available plugins"""
        try:
            from nlp_processor import get_nlp_processor
            
            # Get NLP processor to access plugin metadata
            nlp_processor = get_nlp_processor()
            
            examples = []
            plugin_names = get_plugin_names()
            
            for plugin_name in plugin_names:
                try:
                    # Get plugin metadata if available
                    if plugin_name in nlp_processor.plugin_metadata:
                        metadata = nlp_processor.plugin_metadata[plugin_name]
                        
                        # Use examples from plugin comments
                        for example in metadata.get('examples', []):
                            examples.append({
                                "text": example,
                                "plugin": plugin_name,
                                "description": metadata.get('description', '').split('\n')[0],  # First line
                                "category": _get_plugin_category(plugin_name)
                            })
                    
                    # If no metadata examples, create default ones
                    if plugin_name not in nlp_processor.plugin_metadata or not nlp_processor.plugin_metadata[plugin_name].get('examples'):
                        default_examples = _get_default_examples(plugin_name)
                        for example in default_examples:
                            examples.append({
                                "text": example,
                                "plugin": plugin_name,
                                "description": f"Execute {plugin_name} plugin",
                                "category": _get_plugin_category(plugin_name)
                            })
                            
                except Exception as e:
                    logger.warning(f"Could not load examples for plugin {plugin_name}: {e}")
            
            # Add some generic enhanced examples with shortcuts
            enhanced_examples = [
                {
                    "text": "backup prod db to backup dir tonight",
                    "plugin": "backup_database",
                    "description": "Uses shortcuts: prod db → production database, backup dir → /backup, tonight → at 11 PM",
                    "category": "database"
                },
                {
                    "text": "create urgent incident for api server down",
                    "plugin": "create_incident", 
                    "description": "High priority incident with server specification",
                    "category": "incident"
                },
                {
                    "text": "send email to ops about system maintenance morning",
                    "plugin": "send_email",
                    "description": "Email notification with time shortcut: morning → at 9 AM",
                    "category": "notification"
                }
            ]
            
            examples.extend(enhanced_examples)
            
            # Group examples by category for better organization
            categorized = {}
            for example in examples:
                category = example.get('category', 'other')
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(example)
            
            return jsonify({
                "success": True,
                "examples": examples,
                "categorized": categorized,
                "total_plugins": len(plugin_names)
            })
            
        except Exception as e:
            logger.error(f"Error getting plugin examples: {e}")
            return jsonify({"error": "Failed to load plugin examples"}), 500

    @app.route("/api/reload-plugins", methods=["POST"])
    @time_request("reload-plugins")
    def reload_plugins():
        """Reload plugin metadata for NLP processing"""
        try:
            from nlp_processor import get_nlp_processor
            
            nlp_processor = get_nlp_processor()
            nlp_processor.reload_plugin_metadata()
            
            # Get updated plugin count
            plugin_count = len(nlp_processor.plugin_metadata)
            
            return jsonify({
                "success": True,
                "message": "Plugin metadata reloaded successfully",
                "plugins_loaded": plugin_count,
                "plugins": list(nlp_processor.plugin_metadata.keys())
            })
            
        except ImportError:
            return jsonify({
                "error": "NLP processor module not found"
            }), 500
        except Exception as e:
            logger.error(f"Error reloading plugins: {e}")
            return jsonify({"error": "Failed to reload plugin metadata"}), 500


def _get_plugin_category(plugin_name: str) -> str:
    """Categorize plugin for better organization"""
    categories = {
        'create_incident': 'incident',
        'send_email': 'notification', 
        'backup_database': 'database',
        'cleanup_logs': 'maintenance',
        'generate_report': 'reporting',
        'monitor_system': 'monitoring'
    }
    return categories.get(plugin_name, 'other')

def _get_default_examples(plugin_name: str) -> List[str]:
    """Generate default examples for plugins without metadata"""
    defaults = {
        'create_incident': [
            f"create P1 incident for system failure",
            f"report critical issue with {plugin_name}"
        ],
        'send_email': [
            f"send email to admin about server status",
            f"notify team about maintenance window"
        ],
        'backup_database': [
            f"backup production database daily",
            f"create database backup now"
        ],
        'cleanup_logs': [
            f"cleanup old log files from /var/log",
            f"remove logs older than 30 days"
        ],
        'generate_report': [
            f"generate monthly system report",
            f"create performance analysis"
        ],
        'monitor_system': [
            f"monitor system health hourly",
            f"check server performance"
        ]
    }
    
    return defaults.get(plugin_name, [f"run {plugin_name} with default parameters"])
