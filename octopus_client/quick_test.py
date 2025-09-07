#!/usr/bin/env python3
"""Simple test of the user parameters system"""

try:
    from global_cache_manager import (
        get_param,
        get_params,
        get_api_credentials,
        get_notifications_config,
        get_integrations_config,
        get_params_summary,
        list_param_categories
    )
    
    print("✅ Successfully imported all simplified access functions")
    
    # Test basic functionality
    print("\n🧪 Testing basic functionality:")
    
    # Test get_param with default
    test_param = get_param('notifications', 'email_address', 'test@example.com')
    print(f"✅ get_param test: {test_param}")
    
    # Test category listing
    categories = list_param_categories()
    print(f"✅ Available categories: {categories}")
    
    # Test get all parameters
    all_params = get_params()
    print(f"✅ Total categories found: {len(all_params)}")
    
    # Test get API credentials
    api_creds = get_api_credentials()
    print(f"✅ API credentials found: {len(api_creds)} items")
    
    # Test summary
    summary = get_params_summary()
    print(f"✅ Summary for user: {summary.get('user', 'unknown')}")
    
    print("\n🎉 All tests passed! User parameters system is working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
