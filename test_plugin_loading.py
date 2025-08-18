#!/usr/bin/env python3
"""
Test script to verify plugin loading improvements
"""
import sys
import os

# Add the octopus_client directory to sys.path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'octopus_client'))

def test_client_plugin_loading():
    print("Testing client-side plugin loading...")
    
    try:
        from pluginhelper import reload_plugins
        print("✓ Successfully imported pluginhelper")
        
        # Test the reload_plugins function
        print("✓ Testing plugin reload...")
        reload_plugins()
        print("✓ Plugin reload completed successfully")
        
    except Exception as e:
        print(f"✗ Client plugin loading failed: {e}")
        import traceback
        traceback.print_exc()

def test_server_plugin_import():
    print("\nTesting server-side plugin import helper...")
    
    try:
        # Add server paths
        server_path = os.path.join(os.path.dirname(__file__), 'octopus_server')
        sys.path.insert(0, os.path.join(server_path, 'routes'))
        
        from plugin_api_routes import _import_plugin_with_fallback, _setup_plugin_paths
        print("✓ Successfully imported server plugin helpers")
        
        # Setup paths
        _setup_plugin_paths()
        print("✓ Plugin paths configured successfully")
        
        # Test importing a simple plugin
        test_plugins = ['system_info', 'web_utils', 'notifications']
        for plugin in test_plugins:
            try:
                module = _import_plugin_with_fallback(plugin)
                if module:
                    print(f"✓ Successfully imported plugin: {plugin}")
                else:
                    print(f"✗ Failed to import plugin: {plugin}")
            except Exception as e:
                print(f"✗ Error importing plugin {plugin}: {e}")
        
    except Exception as e:
        print(f"✗ Server plugin import test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client_plugin_loading()
    test_server_plugin_import()
    print("\nPlugin loading test completed!")
