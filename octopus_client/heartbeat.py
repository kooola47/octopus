import requests
import socket
import getpass
import time
import logging
from cache import Cache
from config import SERVER_URL

cache = Cache()
logger = logging.getLogger("octopus_client")

def send_heartbeat():
    data = {
        "username": getpass.getuser(),
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "login_time": cache.get("login_time") or time.time(),
        "since_last_heartbeat": time.time() - (cache.get("last_heartbeat") or time.time())
    }
    try:
        requests.post(f"{SERVER_URL}/heartbeat", json=data, timeout=5)
        logger.info(f"Heartbeat sent: {data}")
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
    cache.set("last_heartbeat", time.time())
