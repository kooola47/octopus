#!/usr/bin/env python3
"""Quick test of production configuration loading"""

import sys
sys.argv = ['main.py', 'prod']

from config import load_config

print("🐙 Testing Production Configuration Load")
print("=" * 50)

config = load_config()

print(f"✅ Environment: {config.ENVIRONMENT}")
print(f"✅ Server URL: {config.SERVER_URL}")
print(f"✅ Debug Mode: {config.DEBUG}")
print(f"✅ Log Level: {config.LOG_LEVEL}")
print(f"✅ Username: {config.USERNAME}")
print(f"✅ Heartbeat Interval: {config.HEARTBEAT_INTERVAL}s")
print(f"✅ Task Check Interval: {config.TASK_CHECK_INTERVAL}s")
print(f"✅ Cache TTL: {config.CACHE_TTL}s")

print("\n🎯 Production Configuration Successfully Loaded!")
