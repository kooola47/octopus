import requests
import socket
import getpass
import time
import logging
import os
import psutil
from cache import Cache
from config import get_current_config
config = get_current_config()


cache = Cache()
logger = logging.getLogger("octopus_client")

USERNAME = config.USERNAME
HOSTNAME = config.CLIENT_HOSTNAME
IP_ADDRESS = config.CLIENT_IP

def get_cpu_usage():
    """Get current CPU usage percentage"""
    try:
        return round(psutil.cpu_percent(interval=1), 1)
    except Exception as e:
        logger.warning(f"Failed to get CPU usage: {e}")
        return 0.0

def get_memory_usage():
    """Get current memory usage percentage"""
    try:
        memory = psutil.virtual_memory()
        return round(memory.percent, 1)
    except Exception as e:
        logger.warning(f"Failed to get memory usage: {e}")
        return 0.0

def send_heartbeat():
    data = {
        "username": config.USERNAME,
        "hostname": HOSTNAME,
        "ip": IP_ADDRESS,
        "login_time": cache.get("login_time") or time.time(),
        "since_last_heartbeat": time.time() - (cache.get("last_heartbeat") or time.time()),
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage()
    }
    try:
        requests.post(f"{config.SERVER_URL}/heartbeat", json=data, timeout=5)
        logger.info(f"Heartbeat sent: {data}")
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
    cache.set("last_heartbeat", time.time())
