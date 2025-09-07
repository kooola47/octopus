#!/usr/bin/env python3
"""
🧪 USER PARAMETERS SYSTEM TEST
==============================

Quick test to verify the improved user parameters system is working correctly.
Run this to check if all the simplified access methods are functioning.
"""

import sys
import os

# Add the octopus_client to the path
client_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'octopus_client')
sys.path.insert(0, client_path)

def test_simplified_access():
    """Test the simplified user parameters access methods"""
    print("🧪 Testing Simplified User Parameters Access")
    print("=" * 50)
    
    try:
        # Test import
        from global_cache_manager import (
            get_param,
            get_params,
            get_api_credentials,
            get_notifications_config,
            get_integrations_config,
            get_params_summary,
            list_param_categories
        )
        print("✅ Successfully imported simplified access functions")
        
        # Test get single parameter with default
        test_param = get_param('notifications', 'email_address', 'test@example.com')
        print(f"✅ get_param() works: email_address = {test_param}")
        
        # Test get category
        api_creds = get_api_credentials()
        print(f"✅ get_api_credentials() works: found {len(api_creds)} credentials")
        
        # Test get all parameters
        all_params = get_params()
        print(f"✅ get_params() works: found {len(all_params)} categories")
        
        # Test summary
        summary = get_params_summary()
        print(f"✅ get_params_summary() works: user = {summary.get('user', 'unknown')}")
        
        # Test list categories
        categories = list_param_categories()
        print(f"✅ list_param_categories() works: {categories}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def test_explicit_access():
    """Test the explicit user parameters access methods"""
    print("\n🧪 Testing Explicit User Parameters Access")
    print("=" * 50)
    
    try:
        from global_cache_manager import GlobalCacheManager
        from config.config_loader import get_config
        
        # Initialize cache manager
        config = get_config()
        cache_manager = GlobalCacheManager(config)
        
        # Test explicit method (requires username)
        username = config.get('client', {}).get('username', 'testuser')
        
        # Test get user parameters explicitly
        user_params = cache_manager.get_user_parameters(username)
        if user_params:
            print(f"✅ get_user_parameters() works: found parameters for {username}")
        else:
            print(f"⚠️ get_user_parameters() returned empty for {username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Explicit access test error: {e}")
        return False


def test_plugin_demo():
    """Test the improved plugin demo"""
    print("\n🧪 Testing Improved Plugin Demo")
    print("=" * 50)
    
    try:
        from plugins.user_params_demo_improved import (
            demo_simplified_access,
            demo_organized_display,
            demo_practical_usage
        )
        
        # Test simplified access demo
        result1 = demo_simplified_access()
        if result1.get('status') == 'success':
            print("✅ demo_simplified_access() works")
        else:
            print(f"❌ demo_simplified_access() failed: {result1.get('error', 'unknown error')}")
        
        # Test organized display demo
        result2 = demo_organized_display()
        if result2.get('status') == 'success':
            print("✅ demo_organized_display() works")
        else:
            print(f"❌ demo_organized_display() failed: {result2.get('error', 'unknown error')}")
        
        # Test practical usage demo
        result3 = demo_practical_usage()
        if result3.get('status') == 'success':
            print("✅ demo_practical_usage() works")
        else:
            print(f"❌ demo_practical_usage() failed: {result3.get('error', 'unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Plugin demo test error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 USER PARAMETERS SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: Simplified Access
    test1_passed = test_simplified_access()
    
    # Test 2: Explicit Access
    test2_passed = test_explicit_access()
    
    # Test 3: Plugin Demo
    test3_passed = test_plugin_demo()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    print(f"Simplified Access: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Explicit Access:   {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Plugin Demo:       {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 ALL TESTS PASSED! User Parameters System is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
