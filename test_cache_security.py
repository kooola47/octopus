#!/usr/bin/env python3
"""
Test script to verify global cache security features
"""

import sys
import os
import requests
import json

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add server path for testing server-side functionality
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'octopus_server'))

def test_server_side_security():
    """Test server-side cache security"""
    print("🔒 Testing Server-Side Cache Security")
    print("=" * 50)
    
    try:
        from global_cache_manager import get_global_cache_manager
        cache_manager = get_global_cache_manager()
        
        # Test 1: User can access their own data
        print("\n✅ Test 1: User accessing own profile data")
        try:
            cache_manager.set_user_profile_data('testuser1', {'theme': 'dark'}, requesting_user='testuser1')
            profile = cache_manager.get_user_profile_data('testuser1', requesting_user='testuser1')
            print(f"   SUCCESS: User can access own data: {profile}")
        except Exception as e:
            print(f"   FAILED: {e}")
        
        # Test 2: User cannot access another user's data
        print("\n❌ Test 2: User trying to access another user's data")
        try:
            cache_manager.set_user_profile_data('testuser2', {'theme': 'light'}, requesting_user='testuser2')
            profile = cache_manager.get_user_profile_data('testuser2', requesting_user='testuser1')  # Wrong user!
            print(f"   SECURITY BREACH: Unauthorized access succeeded: {profile}")
        except PermissionError as e:
            print(f"   SUCCESS: Unauthorized access blocked: {e}")
        except Exception as e:
            print(f"   UNEXPECTED ERROR: {e}")
        
        # Test 3: Admin can access any user's data
        print("\n🔧 Test 3: Admin accessing any user's data")
        try:
            # Set up an admin user in the startup cache (this would normally be configured)
            cache_manager.set('admin_users', ['admin_user'], 'startup')
            profile = cache_manager.get_user_profile_data('testuser2', requesting_user='admin_user')
            print(f"   SUCCESS: Admin can access any user's data: {profile}")
        except Exception as e:
            print(f"   FAILED: {e}")
        
        # Test 4: User settings security
        print("\n🔧 Test 4: User settings security")
        try:
            cache_manager.set_user_setting('testuser1', 'notifications', True, requesting_user='testuser1')
            setting = cache_manager.get_user_setting('testuser1', 'notifications', requesting_user='testuser1')
            print(f"   SUCCESS: User can access own settings: {setting}")
            
            # Try unauthorized access
            try:
                setting = cache_manager.get_user_setting('testuser1', 'notifications', requesting_user='testuser3')
                print(f"   SECURITY BREACH: Unauthorized settings access: {setting}")
            except PermissionError:
                print(f"   SUCCESS: Unauthorized settings access blocked")
                
        except Exception as e:
            print(f"   FAILED: {e}")
            
    except ImportError as e:
        print(f"❌ Cannot test server-side security: {e}")

def test_api_security():
    """Test API endpoint security"""
    print("\n🌐 Testing API Endpoint Security")
    print("=" * 50)
    
    server_url = "http://localhost:8000"
    
    # Test 1: Valid headers
    print("\n✅ Test 1: Valid authentication headers")
    headers = {
        'X-Client-ID': 'test_client_123',
        'X-Username': 'testuser1',
        'Content-Type': 'application/json'
    }
    
    try:
        # Try to set profile data
        response = requests.post(
            f"{server_url}/api/cache/user/testuser1/profile",
            headers=headers,
            json={'theme': 'dark', 'language': 'en'}
        )
        
        if response.status_code == 200:
            print(f"   SUCCESS: Profile data set with valid headers")
        else:
            print(f"   INFO: Server response {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   INFO: Server not running, skipping API tests")
        return
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Missing headers
    print("\n❌ Test 2: Missing authentication headers")
    try:
        response = requests.post(
            f"{server_url}/api/cache/user/testuser1/profile",
            json={'theme': 'dark'}
        )
        
        if response.status_code == 403:
            print(f"   SUCCESS: Missing headers blocked (403)")
        else:
            print(f"   POTENTIAL ISSUE: Expected 403, got {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   INFO: Server not running")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Wrong username
    print("\n❌ Test 3: Username mismatch")
    headers_wrong = {
        'X-Client-ID': 'test_client_123',
        'X-Username': 'testuser1',  # Claims to be testuser1
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/cache/user/testuser2/profile",  # But trying to access testuser2's data
            headers=headers_wrong,
            json={'theme': 'dark'}
        )
        
        if response.status_code == 403:
            print(f"   SUCCESS: Username mismatch blocked (403)")
        else:
            print(f"   POTENTIAL ISSUE: Expected 403, got {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   INFO: Server not running")
    except Exception as e:
        print(f"   ERROR: {e}")

def test_client_side_security():
    """Test client-side cache security"""
    print("\n💻 Testing Client-Side Cache Security")
    print("=" * 50)
    
    try:
        # Add client path for testing
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'octopus_client'))
        from global_cache_manager import ClientGlobalCacheManager
        
        # Create a test client
        client_cache = ClientGlobalCacheManager()
        client_cache.set_user_identity('testuser1')
        
        print(f"✅ Client identity set: {client_cache.get_current_username()}")
        print(f"   Client ID: {client_cache.get_current_client_id()}")
        
        # Test sync with identity headers
        print("   Testing identity header inclusion in requests...")
        headers = client_cache._get_identity_headers()
        print(f"   Identity headers: {headers}")
        
        if 'X-Username' in headers and 'X-Client-ID' in headers:
            print("   SUCCESS: Identity headers properly formatted")
        else:
            print("   ISSUE: Missing identity headers")
            
    except ImportError as e:
        print(f"❌ Cannot test client-side security: {e}")

def main():
    """Run all security tests"""
    print("🔒 OCTOPUS GLOBAL CACHE SECURITY TEST SUITE")
    print("=" * 60)
    
    test_server_side_security()
    test_api_security()
    test_client_side_security()
    
    print("\n" + "=" * 60)
    print("🏁 Security testing completed!")
    print("\nTo fully test API security, ensure the Octopus server is running:")
    print("   cd octopus_server && python main.py")

if __name__ == "__main__":
    main()
