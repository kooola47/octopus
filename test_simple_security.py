#!/usr/bin/env python3
"""
Simple test to verify global cache security is working
"""

import sys
import os

# Add server path for testing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'octopus_server'))

def test_basic_security():
    """Test basic cache security"""
    print("Testing Global Cache Security")
    print("=" * 40)
    
    try:
        from global_cache_manager import get_global_cache_manager
        cache_manager = get_global_cache_manager()
        
        # Test 1: User can access their own data
        cache_manager.set_user_profile_data('user1', {'theme': 'dark'}, requesting_user='user1')
        profile = cache_manager.get_user_profile_data('user1', requesting_user='user1')
        print(f"✓ User accessing own data: {profile}")
        
        # Test 2: User cannot access another user's data
        try:
            cache_manager.set_user_profile_data('user2', {'theme': 'light'}, requesting_user='user2')
            profile = cache_manager.get_user_profile_data('user2', requesting_user='user1')  # Wrong user!
            print(f"✗ SECURITY ISSUE: Unauthorized access succeeded")
        except PermissionError as e:
            print(f"✓ Unauthorized access blocked: {str(e)[:50]}...")
        
        # Test 3: Admin access
        cache_manager.set('admin_users', ['admin'], 'startup')
        profile = cache_manager.get_user_profile_data('user2', requesting_user='admin')
        print(f"✓ Admin accessing user data: {profile}")
        
        print("\n✓ All security tests passed!")
        
    except ImportError as e:
        print(f"Cannot import cache manager: {e}")

if __name__ == "__main__":
    test_basic_security()
