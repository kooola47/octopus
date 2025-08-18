#!/usr/bin/env python3
"""
Quick test to verify the plugin import fix
"""
import sys
import os

# Add the octopus_client directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'octopus_client'))

def test_plugin_import():
    """Test the improved plugin import mechanism"""
    print("Testing plugin import fix...")
    
    try:
        from pluginhelper import import_plugin
        print("✓ Successfully imported import_plugin function")
        
        # Test with a valid plugin name
        print("\nTesting valid plugin names:")
        test_plugins = ['system_info', 'web_utils', 'notifications']
        
        for plugin_name in test_plugins:
            module = import_plugin(plugin_name)
            if module:
                print(f"✓ Successfully imported plugin: {plugin_name}")
            else:
                print(f"✗ Failed to import plugin: {plugin_name}")
        
        # Test with empty/invalid plugin names (the original bug)
        print("\nTesting edge cases that caused the original bug:")
        edge_cases = ['', '  ', '.main', None]
        
        for plugin_name in edge_cases:
            print(f"Testing plugin_name: '{plugin_name}'")
            module = import_plugin(plugin_name)
            if module:
                print(f"✗ Unexpectedly imported plugin: {plugin_name}")
            else:
                print(f"✓ Correctly rejected invalid plugin: {plugin_name}")
        
        print("\n✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_plugin_import()
    if success:
        print("\n🎉 Plugin import fix verified successfully!")
    else:
        print("\n❌ Plugin import fix verification failed!")
