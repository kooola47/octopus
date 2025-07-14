import os
import hashlib
from flask import jsonify, send_from_directory
from config import PLUGINS_FOLDER

def register_plugin_routes(app, logger):
    @app.route("/plugins")
    def plugins():
        os.makedirs(PLUGINS_FOLDER, exist_ok=True)
        logger.info(f"where is the plugin path : {os.path.abspath(PLUGINS_FOLDER)}")
        # List files and their md5 values
        files = []
        for f in os.listdir(PLUGINS_FOLDER):
            file_path = os.path.join(PLUGINS_FOLDER, f)
            if os.path.isfile(file_path):
                hash_md5 = hashlib.md5()
                with open(file_path, "rb") as file_obj:
                    for chunk in iter(lambda: file_obj.read(4096), b""):
                        hash_md5.update(chunk)
                files.append({"filename": f, "md5": hash_md5.hexdigest()})
        logger.info(f"Plugins list requested: {files}")
        return jsonify(files)

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
