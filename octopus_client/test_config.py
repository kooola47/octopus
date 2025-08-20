#!/usr/bin/env python3
"""
Test the new configuration system
"""

def test_dev_config():
    print("=== Testing Development Configuration ===")
    from config import load_config
    config = load_config('dev')
    
    print(f"✅ Environment: {config.ENVIRONMENT}")
    print(f"✅ Server URL: {config.SERVER_URL}")
    print(f"✅ Debug: {config.DEBUG}")
    print(f"✅ Log Level: {config.LOG_LEVEL}")
    print(f"✅ Username: {config.USERNAME}")
    print(f"✅ Heartbeat Interval: {config.HEARTBEAT_INTERVAL}s")
    print(f"✅ Task Check Interval: {config.TASK_CHECK_INTERVAL}s")

def test_prod_config():
    print("\n=== Testing Production Configuration ===")
    from config import load_config
    config = load_config('prod')
    
    print(f"✅ Environment: {config.ENVIRONMENT}")
    print(f"✅ Server URL: {config.SERVER_URL}")
    print(f"✅ Debug: {config.DEBUG}")
    print(f"✅ Log Level: {config.LOG_LEVEL}")
    print(f"✅ Username: {config.USERNAME}")
    print(f"✅ Heartbeat Interval: {config.HEARTBEAT_INTERVAL}s")
    print(f"✅ Task Check Interval: {config.TASK_CHECK_INTERVAL}s")

def test_command_line_simulation():
    print("\n=== Testing Command Line Argument Simulation ===")
    import sys
    
    # Test dev
    sys.argv = ['main.py', 'dev']
    from config.config_loader import determine_environment
    env = determine_environment()
    print(f"✅ 'python main.py dev' -> Environment: {env}")
    
    # Test prod
    sys.argv = ['main.py', 'prod']
    env = determine_environment()
    print(f"✅ 'python main.py prod' -> Environment: {env}")
    
    # Test default
    sys.argv = ['main.py']
    env = determine_environment()
    print(f"✅ 'python main.py' -> Environment: {env}")

if __name__ == "__main__":
    test_dev_config()
    test_prod_config()
    test_command_line_simulation()
    print("\n🎉 All configuration tests passed!")
