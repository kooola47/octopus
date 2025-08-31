#!/usr/bin/env python3

import requests
import json

def test_plugin_response():
    """Test the plugin response format"""
    try:
        # Make a request to the plugins endpoint
        response = requests.get('http://localhost:18900/plugins')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Parse the JSON response
        plugins_data = response.json()
        print(f"Response Data: {json.dumps(plugins_data, indent=2)}")
        
        # Check if the response has the expected format
        if isinstance(plugins_data, list) and len(plugins_data) > 0:
            plugin = plugins_data[0]
            print(f"\nFirst plugin keys: {list(plugin.keys())}")
            
            # Check for required keys
            required_keys = ['filename', 'md5']
            missing_keys = [key for key in required_keys if key not in plugin]
            
            if missing_keys:
                print(f"❌ Missing keys: {missing_keys}")
                return False
            else:
                print("✅ All required keys present")
                return True
        else:
            print("❌ Response is not a valid list of plugins")
            return False
            
    except Exception as e:
        print(f"❌ Error testing plugin response: {e}")
        return False

if __name__ == "__main__":
    test_plugin_response()