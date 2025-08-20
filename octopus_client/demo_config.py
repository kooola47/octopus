#!/usr/bin/env python3
"""
🐙 Configuration System Demo
===========================

Demonstrates the new configuration package for Octopus Client.
"""

def demo_config_usage():
    print("🐙 OCTOPUS CLIENT CONFIGURATION SYSTEM DEMO")
    print("=" * 60)
    
    print("\n1. Testing Development Configuration:")
    print("   Command: python main.py dev")
    print("   " + "-" * 40)
    
    import sys
    sys.argv = ['main.py', 'dev']
    
    from config import load_config
    config = load_config()
    
    print(f"   Environment: {config.ENVIRONMENT}")
    print(f"   Server URL: {config.SERVER_URL}")
    print(f"   Debug Mode: {config.DEBUG}")
    print(f"   Log Level: {config.LOG_LEVEL}")
    print(f"   Heartbeat Interval: {config.HEARTBEAT_INTERVAL}s")
    print(f"   Task Check Interval: {config.TASK_CHECK_INTERVAL}s")
    print(f"   Cache TTL: {config.CACHE_TTL}s")
    print(f"   Username: {config.USERNAME}")
    
    print("\n2. Testing Production Configuration:")
    print("   Command: python main.py prod")
    print("   " + "-" * 40)
    
    sys.argv = ['main.py', 'prod']
    config = load_config()  # This will reload with prod config
    
    print(f"   Environment: {config.ENVIRONMENT}")
    print(f"   Server URL: {config.SERVER_URL}")
    print(f"   Debug Mode: {config.DEBUG}")
    print(f"   Log Level: {config.LOG_LEVEL}")
    print(f"   Heartbeat Interval: {config.HEARTBEAT_INTERVAL}s")
    print(f"   Task Check Interval: {config.TASK_CHECK_INTERVAL}s")
    print(f"   Cache TTL: {config.CACHE_TTL}s")
    print(f"   Username: {config.USERNAME}")
    
    print("\n3. Configuration Comparison:")
    print("   " + "-" * 40)
    print("   Feature              | Dev        | Prod")
    print("   " + "-" * 40)
    print("   Heartbeat Interval   | 10s        | 60s")
    print("   Task Check Interval  | 5s         | 30s")
    print("   Log Level           | DEBUG      | WARNING")
    print("   Debug Mode          | True       | False")
    print("   Cache TTL           | 300s       | 1800s")
    print("   Server URL          | localhost  | production-server")
    
    print("\n4. Environment Detection:")
    print("   " + "-" * 40)
    from config.config_loader import determine_environment
    
    # Test different scenarios
    test_cases = [
        (['main.py'], 'default'),
        (['main.py', 'dev'], 'dev argument'),
        (['main.py', 'prod'], 'prod argument'),
        (['main.py', 'development'], 'development argument'),
        (['main.py', 'production'], 'production argument')
    ]
    
    for argv, description in test_cases:
        sys.argv = argv
        env = determine_environment()
        print(f"   {description:20} -> {env}")
    
    print("\n✅ Configuration System Ready!")
    print("\nUsage Examples:")
    print("   python main.py          # Development mode")
    print("   python main.py dev      # Development mode")
    print("   python main.py prod     # Production mode")
    print("   python main.py --help   # Show help")

if __name__ == "__main__":
    demo_config_usage()
