import requests
import os
import hashlib
import logging
import importlib
import importlib.util
import sys
from config import SERVER_URL, PLUGINS_FOLDER

logger = logging.getLogger("octopus_client")

def _setup_plugin_paths():
    """Setup sys.path for proper plugin and dependency imports"""
    # Add necessary paths for plugin dependencies
    plugins_path = os.path.abspath(PLUGINS_FOLDER)
    client_path = os.path.dirname(plugins_path)  # octopus_client folder
    server_path = os.path.join(os.path.dirname(client_path), 'octopus_server')  # octopus_server folder
    root_path = os.path.dirname(client_path)  # project root
    
    # Add all necessary paths to sys.path for plugin imports
    paths_to_add = [plugins_path, client_path, server_path, root_path]
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
    
    # Add server routes path for plugins that import user_profile_routes
    server_routes_path = os.path.join(server_path, 'routes')
    if os.path.exists(server_routes_path) and server_routes_path not in sys.path:
        sys.path.insert(0, server_routes_path)

def import_plugin(plugin_name):
    """
    Import a plugin with robust error handling and path setup.
    Returns the plugin module or None if import fails.
    """
    if not plugin_name or not plugin_name.strip():
        logger.error("Empty plugin name provided")
        return None
    
    plugin_name = plugin_name.strip()
    
    # Ensure paths are set up
    _setup_plugin_paths()
    
    try:
        # Strategy 1: Try standard import with plugins prefix
        return importlib.import_module(f"plugins.{plugin_name}")
    except ImportError:
        pass
    
    try:
        # Strategy 2: Try direct import (for plugins in sys.path)
        return importlib.import_module(plugin_name)
    except ImportError:
        pass
    
    try:
        # Strategy 3: Try file-based loading
        plugins_path = os.path.abspath(PLUGINS_FOLDER)
        plugin_path = os.path.join(plugins_path, f"{plugin_name}.py")
        
        if os.path.exists(plugin_path):
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)
                return module
    except Exception as e:
        logger.error(f"File-based import failed for plugin {plugin_name}: {e}")
    
    logger.error(f"Failed to import plugin {plugin_name} using all strategies")
    return None

def md5sum(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_plugin_updates():
    try:
        resp = requests.get(f"{SERVER_URL}/plugins", timeout=5)
        plugins = resp.json()
        os.makedirs(PLUGINS_FOLDER, exist_ok=True)
        updated = []
        for plugin in plugins:
            plugin_name = plugin["filename"]
            plugin_md5 = plugin["md5"]
            local_plugin_path = os.path.join(PLUGINS_FOLDER, plugin_name)
            need_download = False
            if not os.path.exists(local_plugin_path):
                need_download = True
            else:
                local_md5 = md5sum(local_plugin_path)
                if local_md5 != plugin_md5:
                    need_download = True
            if need_download:
                try:
                    server_plugin_path = f"{SERVER_URL}/plugins/{plugin_name}"
                    file_resp = requests.get(server_plugin_path, timeout=10)
                    if file_resp.status_code == 200:
                        with open(local_plugin_path, "wb") as f:
                            f.write(file_resp.content)
                        logger.info(f"Downloaded/updated plugin: {plugin_name}")
                        updated.append(plugin_name)
                    else:
                        logger.error(f"Failed to download plugin {plugin_name}: HTTP {file_resp.status_code}")
                except Exception as e:
                    logger.error(f"Failed to download plugin {plugin_name}: {e}")
        logger.info(f"Checked plugin updates: {[p['filename'] for p in plugins]}, updated: {updated}")
        reload_plugins()
    except Exception as e:
        logger.error(f"Plugin update failed: {e}")

def reload_plugins():
    import sys
    import importlib
    import importlib.util
    
    # Use shared path setup
    _setup_plugin_paths()
    plugins_path = os.path.abspath(PLUGINS_FOLDER)
    
    for filename in os.listdir(PLUGINS_FOLDER):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                # Use folder-based module loading for better path resolution
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    logger.info(f"Plugin {module_name} reloaded.")
                else:
                    # Load module with proper spec for better error handling
                    module_path = os.path.join(plugins_path, filename)
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        logger.info(f"Plugin {module_name} loaded.")
                    else:
                        # Fallback to simple import
                        importlib.import_module(module_name)
                        logger.info(f"Plugin {module_name} loaded (fallback).")
            except Exception as e:
                logger.error(f"Failed to load/reload plugin {module_name}: {e}")
                # Print more detailed error information
                import traceback
                logger.error(f"Plugin {module_name} traceback: {traceback.format_exc()}")
