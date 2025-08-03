import requests
import os
import hashlib
import logging
import importlib
from config import SERVER_URL, PLUGINS_FOLDER

logger = logging.getLogger("octopus_client")

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
    plugins_path = os.path.abspath(PLUGINS_FOLDER)
    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)
    for filename in os.listdir(PLUGINS_FOLDER):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                logger.info(f"Plugin {module_name} loaded/reloaded.")
            except Exception as e:
                logger.error(f"Failed to load/reload plugin {module_name}: {e}")
