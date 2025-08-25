import os
import hashlib
from flask import jsonify, send_from_directory
from config import PLUGINS_FOLDER
from global_cache_manager import GlobalCacheManager

def register_plugin_routes(app, global_cache: GlobalCacheManager, logger):
    @app.route("/plugins")
    def plugins():
        from plugin_discovery import PluginDiscovery
        os.makedirs(PLUGINS_FOLDER, exist_ok=True)
        logger.info(f"where is the plugin path : {os.path.abspath(PLUGINS_FOLDER)}")
        # Try to get plugin metadata from cache
        plugins_meta = global_cache.get('plugins', 'startup', None, None)
        if not isinstance(plugins_meta, dict):
            plugins_meta = None
        # If not cached, discover and cache
        if plugins_meta is None:
            discovery = PluginDiscovery(PLUGINS_FOLDER)
            plugins_meta = discovery.get_plugins_with_metadata()
            global_cache.set('plugins', plugins_meta, 'startup')
        logger.info(f"Plugins metadata requested: {list(plugins_meta.keys())}")
        # Return a summary list for UI (filename, description, function count)
        summary = []
        for name, meta in plugins_meta.items():
            summary.append({
                'plugin_name': name,
                'file': meta.get('file'),
                'description': meta.get('description', ''),
                'function_count': len(meta.get('functions', {})),
                'functions': list(meta.get('functions', {}).keys())
            })
        return jsonify(summary)

    @app.route("/plugins/<path:filename>")
    def get_plugin_file(filename):
        return send_from_directory(PLUGINS_FOLDER, filename)

    @app.route("/plugins/md5/<path:filename>")
    def plugin_md5(filename):
        file_path = os.path.join(PLUGINS_FOLDER, filename)
        if not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return jsonify({"md5": hash_md5.hexdigest()})
