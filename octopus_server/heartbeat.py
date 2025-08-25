import time
import sqlite3
from flask import request, jsonify
from dbhelper import get_db_file

def register_heartbeat_routes(app, global_cache, logger):
    @app.route("/heartbeat", methods=["POST"])
    def heartbeat():
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Update client info in global cache
        username = data.get('username', '')
        hostname = data.get('hostname', '')
        ip_address = data.get('ip', '')
        cpu_usage = data.get('cpu_usage', 0.0)
        memory_usage = data.get('memory_usage', 0.0)
        client_version = data.get('version', '-')
        now = time.time()

        # Compose client data
        client_data = {
            'id': username,
            'name': username,
            'username': username,
            'hostname': hostname or 'unknown',
            'ip_address': ip_address or '127.0.0.1',
            'status': 'online',
            'last_heartbeat': now,
            'last_seen': now,
            'cpu_usage': round(cpu_usage, 1),
            'memory_usage': round(memory_usage, 1),
            'tasks_executed': 0,  # Optionally update from DB
            'success_rate': 0.0,  # Optionally update from DB
            'version': client_version,
            'time_diff': 0.0
        }

        # Store/update only this client in global cache (thread-safe)
        global_cache.set(username, client_data, 'clients')

        # --- Sync to DB: Save this client to DB as backup ---
        #try:
        #    save_client_to_db(client_data)
        #except Exception as db_sync_err:
        #    logger.error(f"Failed to sync client {username} to DB: {db_sync_err}")

        logger.info(f"Heartbeat received and cached: {username}@{hostname}")
        return jsonify({"status": "ok"})

    @app.route("/clients")
    def clients():
        logger.info("Clients status requested")
        clients_data = {}
        # Get clients dict from cache, ensure it's always a dict
        clients_dict = global_cache.get_by_cache_type('clients')
        logger.info(f"Clients retrieved from cache: {clients_dict}")
        if not isinstance(clients_dict, dict):
            clients_dict = {}
        logger.info(f"Clients retrieved from cache: {list(clients_dict.keys())}")
        # Format for backward compatibility
        for client in clients_dict.values():
            try:
                key = f"{client.get('username', '-') }@{client.get('hostname', '-') }"
                clients_data[key] = {
                    'username': client.get('username', '-'),
                    'hostname': client.get('hostname', '-'),
                    'ip': client.get('ip_address', '-'),
                    'cpu_usage': client.get('cpu_usage', 0.0),
                    'memory_usage': client.get('memory_usage', 0.0),
                    'last_heartbeat': client.get('last_heartbeat', 0.0),
                    'status': client.get('status', '-')
                }
            except Exception as e:
                logger.error(f"Error formatting client data: {e}")
        return jsonify(clients_data)

def save_client_to_db(client):
    """Save a single client record to the heartbeats table as backup, using (username, hostname, ip_address) as unique key."""
    import sqlite3
    import time
    from dbhelper import get_db_file
    now = time.time()
    with sqlite3.connect(get_db_file()) as conn:
        conn.execute('''
            INSERT INTO heartbeats (username, hostname, ip_address, cpu_usage, memory_usage, login_time, since_last_heartbeat, timestamp, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username, hostname, ip_address) DO UPDATE SET
                cpu_usage=excluded.cpu_usage,
                memory_usage=excluded.memory_usage,
                login_time=excluded.login_time,
                since_last_heartbeat=excluded.since_last_heartbeat,
                timestamp=excluded.timestamp,
                created_at=excluded.created_at
        ''', (
            client.get('username'),
            client.get('hostname'),
            client.get('ip_address'),
            client.get('cpu_usage', 0.0),
            client.get('memory_usage', 0.0),
            client.get('last_seen', now),
            now - client.get('last_heartbeat', now),
            client.get('last_heartbeat', now),
            now
        ))
        conn.commit()
