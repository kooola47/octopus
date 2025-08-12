import time
import sqlite3
from flask import request, jsonify
from dbhelper import get_db_file


def register_heartbeat_routes(app, cache, logger):
    @app.route("/heartbeat", methods=["POST"])
    def heartbeat():
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        key = f"{data['username']}@{data['hostname']}"
        data['last_heartbeat'] = time.time()
        
        # Store in cache (for backward compatibility)
        cache.set(key, data)
        
        # Store in database
        try:
            with sqlite3.connect(get_db_file()) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO heartbeats 
                    (username, hostname, ip_address, cpu_usage, memory_usage, 
                     login_time, since_last_heartbeat, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('username'),
                    data.get('hostname'),
                    data.get('ip'),
                    data.get('cpu_usage', 0.0),
                    data.get('memory_usage', 0.0),
                    data.get('login_time'),
                    data.get('since_last_heartbeat'),
                    data['last_heartbeat']
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store heartbeat in database: {e}")
        
        logger.info(f"Heartbeat received: {data}")
        return jsonify({"status": "ok"})

    @app.route("/clients")
    def clients():
        logger.info("Clients status requested")
        return jsonify(cache.all())
