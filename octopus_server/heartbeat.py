import time
from flask import request, jsonify

def register_heartbeat_routes(app, cache, logger):
    @app.route("/heartbeat", methods=["POST"])
    def heartbeat():
        data = request.json
        key = f"{data['username']}@{data['hostname']}"
        data['last_heartbeat'] = time.time()
        cache.set(key, data)
        logger.info(f"Heartbeat received: {data}")
        return jsonify({"status": "ok"})

    @app.route("/clients")
    def clients():
        logger.info("Clients status requested")
        return jsonify(cache.all())
