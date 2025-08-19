#!/usr/bin/env python3
"""
Test user_ident based cache system
"""
import sys
import os

# Add server path
sys.path.append('./octopus_server')

def test_user_ident_cache():
    print("=== TESTING USER_IDENT BASED CACHE SYSTEM ===")
    
    try:
        from global_cache_manager import get_global_cache_manager
        cache_manager = get_global_cache_manager()
        
        # Test with different username formats that should resolve to the same user_ident
        usernames_to_test = ['aries', 'aries-7044', 'aries-15776', 'aries-36412']
        
        print("\n1. Testing user_ident resolution:")
        for username in usernames_to_test:
            user_ident = cache_manager._get_user_ident_from_username(username)
            print(f"   {username} -> user_ident: {user_ident}")
        
        print("\n2. Setting profile data with different username formats:")
        
        # Set profile data using base username
        profile_data = {
            'theme': 'dark',
            'language': 'en',
            'last_updated': '2025-08-20',
            'preferences': {'notifications': True}
        }
        
        cache_manager.set_user_profile_data('aries', profile_data, requesting_user='aries')
        print("   ✅ Profile data set using 'aries'")
        
        # Try to retrieve using different formats
        print("\n3. Retrieving profile data with different username formats:")
        for username in usernames_to_test:
            try:
                retrieved_data = cache_manager.get_user_profile_data(username, requesting_user=username)
                if retrieved_data:
                    print(f"   ✅ {username}: {retrieved_data}")
                else:
                    print(f"   ❌ {username}: No data found")
            except Exception as e:
                print(f"   ❌ {username}: {e}")
        
        print("\n4. Testing user settings:")
        
        # Set settings using different username formats
        cache_manager.set_user_setting('aries-7044', 'theme', 'light', requesting_user='aries-7044')
        cache_manager.set_user_setting('aries', 'auto_refresh', True, requesting_user='aries')
        
        print("   ✅ Settings set using different username formats")
        
        # Retrieve settings
        for username in ['aries', 'aries-7044']:
            theme = cache_manager.get_user_setting(username, 'theme', requesting_user=username)
            auto_refresh = cache_manager.get_user_setting(username, 'auto_refresh', requesting_user=username)
            print(f"   {username}: theme={theme}, auto_refresh={auto_refresh}")
        
        print("\n5. Testing security - cross-user access:")
        try:
            # Try to access with different user (should fail)
            cache_manager.get_user_profile_data('aries', requesting_user='admin')
            print("   ❌ Security issue: Cross-user access succeeded")
        except PermissionError as e:
            print(f"   ✅ Security working: {e}")
        except Exception as e:
            print(f"   ? Unexpected error: {e}")
        
        print("\n6. Cache statistics:")
        stats = cache_manager.get_stats()
        print(f"   Cache operations: {stats}")
        
        # List cache contents
        user_profiles_cache = cache_manager._caches.get('user_profiles', {})
        print(f"   Cache keys: {list(user_profiles_cache.keys())}")
        
    except ImportError as e:
        print(f"❌ Cannot import cache manager: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_ident_cache()
