import requests
import socket
import getpass
import time
import logging
import os
from cache import Cache
from config import SERVER_URL
from utils import get_hostname, get_local_ip, get_client_id

cache = Cache()
logger = logging.getLogger("octopus_client")

USERNAME = f"{getpass.getuser()}-{os.getpid()}"
HOSTNAME = get_hostname()
IP_ADDRESS = get_local_ip()

def send_heartbeat():
    data = {
        "username": USERNAME,
        "hostname": HOSTNAME,
        "ip": get_local_ip(),
        "login_time": cache.get("login_time") or time.time(),
        "since_last_heartbeat": time.time() - (cache.get("last_heartbeat") or time.time())
    }
    try:
        requests.post(f"{SERVER_URL}/heartbeat", json=data, timeout=5)
        logger.info(f"Heartbeat sent: {data}")
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
    cache.set("last_heartbeat", time.time())
