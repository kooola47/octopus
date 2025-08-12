import time
import sqlite3
from flask import request, jsonify
from dbhelper import get_db_file
from client_cache_manager import get_client_cache_manager


def register_heartbeat_routes(app, cache, logger):
    @app.route("/heartbeat", methods=["POST"])
    def heartbeat():
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        # Update client cache manager (handles both cache and database)
        client_cache = get_client_cache_manager()
        success = client_cache.update_client_heartbeat(
            username=data.get('username', ''),
            hostname=data.get('hostname', ''),
            ip_address=data.get('ip', ''),
            cpu_usage=data.get('cpu_usage', 0.0),
            memory_usage=data.get('memory_usage', 0.0)
        )
        
        if not success:
            logger.error(f"Failed to update client cache for {data.get('username')}")
            return jsonify({"status": "error", "message": "Failed to update client data"}), 500
        
        # Maintain backward compatibility with old cache system
        key = f"{data['username']}@{data['hostname']}"
        data['last_heartbeat'] = time.time()
        cache.set(key, data)
        
        logger.info(f"Heartbeat received and cached: {data.get('username')}@{data.get('hostname')}")
        return jsonify({"status": "ok"})

    @app.route("/clients")
    def clients():
        logger.info("Clients status requested")
        # Use client cache manager for better performance
        client_cache = get_client_cache_manager()
        clients_data = {}
        
        # Get clients from cache
        page_clients, _ = client_cache.get_clients_paginated(page=1, page_size=1000)
        
        # Format for backward compatibility
        for client in page_clients:
            key = f"{client['username']}@{client['hostname']}"
            clients_data[key] = {
                'username': client['username'],
                'hostname': client['hostname'],
                'ip': client['ip_address'],
                'cpu_usage': client['cpu_usage'],
                'memory_usage': client['memory_usage'],
                'last_heartbeat': client['last_heartbeat'],
                'status': client['status']
            }
        
        return jsonify(clients_data)
