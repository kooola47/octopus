#!/usr/bin/env python3
"""
👤 Test User Parameters System
=============================

Script to test the user parameters system with example data.
"""

import time
import json

def test_user_parameters():
    """Test the user parameters system"""
    print("🧪 Testing User Parameters System")
    print("=" * 50)
    
    try:
        # Initialize the user parameters manager
        from user_parameters import UserParametersManager, DEFAULT_CATEGORIES, EXAMPLE_PARAMETERS
        from dbhelper import get_db_connection
        
        class DBHelper:
            def get_connection(self):
                return get_db_connection()
        
        params_manager = UserParametersManager(DBHelper())
        test_username = "test_user"
        
        print(f"✅ User Parameters Manager initialized for user: {test_username}")
        
        # Step 1: Set up default categories
        print("\n📁 Setting up default categories...")
        for cat_name, cat_info in DEFAULT_CATEGORIES.items():
            success = params_manager.set_category(
                test_username, cat_name, cat_info['display_name'],
                cat_info['description'], cat_info['icon'], cat_info['sort_order']
            )
            if success:
                print(f"   ✅ Created category: {cat_info['display_name']}")
            else:
                print(f"   ❌ Failed to create category: {cat_name}")
        
        # Step 2: Add example parameters
        print("\n🔧 Adding example parameters...")
        
        # API Credentials (sensitive)
        params_manager.set_parameter(
            test_username, "api_credentials", "servicenow_api_key",
            "sn_demo_key_12345", "string", True, "ServiceNow API Key for incident management"
        )
        params_manager.set_parameter(
            test_username, "api_credentials", "jira_token", 
            "jira_demo_token_67890", "string", True, "Jira API Token for ticket creation"
        )
        params_manager.set_parameter(
            test_username, "api_credentials", "slack_webhook",
            "https://hooks.slack.com/services/demo/webhook", "string", True, "Slack webhook for notifications"
        )
        
        # Integrations (non-sensitive)
        params_manager.set_parameter(
            test_username, "integrations", "servicenow_instance",
            "https://mycompany.service-now.com", "string", False, "ServiceNow instance URL"
        )
        params_manager.set_parameter(
            test_username, "integrations", "jira_base_url",
            "https://mycompany.atlassian.net", "string", False, "Jira base URL"
        )
        params_manager.set_parameter(
            test_username, "integrations", "default_priority",
            "2", "string", False, "Default priority for tickets (1-5)"
        )
        
        # Notifications
        params_manager.set_parameter(
            test_username, "notifications", "email_address",
            "user@company.com", "string", False, "Primary email for notifications"
        )
        params_manager.set_parameter(
            test_username, "notifications", "notify_on_completion",
            True, "bool", False, "Send notification when tasks complete"
        )
        params_manager.set_parameter(
            test_username, "notifications", "notification_channels",
            ["email", "slack"], "json", False, "Preferred notification channels"
        )
        
        # Preferences
        params_manager.set_parameter(
            test_username, "preferences", "timezone",
            "America/New_York", "string", False, "User timezone"
        )
        params_manager.set_parameter(
            test_username, "preferences", "task_refresh_interval",
            30, "int", False, "Task refresh interval in seconds"
        )
        
        print("   ✅ Added example parameters")
        
        # Step 3: Retrieve and display parameters
        print("\n📋 Retrieving user parameters...")
        all_params = params_manager.get_user_parameters(test_username)
        
        for category, params in all_params.items():
            print(f"\n📂 {category.upper()}:")
            for param_name, param_info in params.items():
                value_display = "••••••••" if category == "api_credentials" else param_info['value']
                print(f"   • {param_name}: {value_display} ({param_info['type']})")
                if param_info['description']:
                    print(f"     └─ {param_info['description']}")
        
        # Step 4: Test individual parameter retrieval
        print("\n🔍 Testing individual parameter retrieval...")
        
        # Test getting a non-sensitive parameter
        instance_url = params_manager.get_parameter(test_username, "integrations", "servicenow_instance")
        print(f"   ServiceNow Instance: {instance_url}")
        
        # Test getting a sensitive parameter
        api_key = params_manager.get_parameter(test_username, "api_credentials", "servicenow_api_key")
        print(f"   API Key (decrypted): {api_key[:8]}..." if api_key else "   API Key: Not found")
        
        # Test getting JSON parameter
        channels = params_manager.get_parameter(test_username, "notifications", "notification_channels")
        print(f"   Notification Channels: {channels}")
        
        # Test default value
        missing_param = params_manager.get_parameter(test_username, "custom", "missing_param", "default_value")
        print(f"   Missing Parameter (with default): {missing_param}")
        
        # Step 5: Test caching
        print("\n💾 Testing parameter caching...")
        
        # Create a simple cache manager for testing
        class SimpleCacheManager:
            def __init__(self):
                self.cache = {}
            
            def get(self, key):
                return self.cache.get(key)
            
            def set(self, key, value, ttl=None):
                self.cache[key] = value
                print(f"   📝 Cached: {key}")
                return True
        
        cache_manager = SimpleCacheManager()
        success = params_manager.cache_user_parameters(test_username, cache_manager)
        
        if success:
            print("   ✅ Parameters cached successfully")
            
            # Test retrieving from cache
            cached_params = cache_manager.get(f"user_params_{test_username}_integrations")
            if cached_params:
                print(f"   📥 Retrieved from cache: integrations category has {len(cached_params)} parameters")
        
        # Step 6: Test categories
        print("\n📁 Testing categories...")
        categories = params_manager.get_categories(test_username)
        print(f"   Total categories: {len(categories)}")
        for cat in categories:
            print(f"   • {cat['display_name']} ({cat['name']}) - {cat['description']}")
        
        # Step 7: Test parameter deletion
        print("\n🗑️ Testing parameter deletion...")
        success = params_manager.delete_parameter(test_username, "preferences", "timezone")
        if success:
            print("   ✅ Deleted timezone parameter")
        
        # Verify deletion
        deleted_param = params_manager.get_parameter(test_username, "preferences", "timezone", "NOT_FOUND")
        print(f"   Deleted parameter check: {deleted_param}")
        
        print("\n🎯 User Parameters System Test Complete!")
        print("\nNext steps:")
        print("1. Start the Octopus server")
        print("2. Navigate to /profile in the web interface")
        print("3. Add/edit user parameters through the UI")
        print("4. Create tasks that use plugins with user parameters")
        print("5. Verify plugins access user-specific configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plugin_parameter_access():
    """Test how plugins access user parameters"""
    print("\n🔌 Testing Plugin Parameter Access")
    print("=" * 50)
    
    try:
        # Test the helper functions
        from routes.user_profile_routes import get_user_parameter, get_user_category_parameters
        
        test_username = "test_user"
        
        # Test getting individual parameter
        api_key = get_user_parameter(test_username, "api_credentials", "servicenow_api_key", "fallback_key")
        print(f"Plugin got API key: {api_key[:8]}..." if api_key != "fallback_key" else f"Plugin got fallback: {api_key}")
        
        # Test getting category parameters
        integrations = get_user_category_parameters(test_username, "integrations")
        print(f"Plugin got integrations: {integrations}")
        
        # Test with non-existent user
        missing_params = get_user_category_parameters("nonexistent_user", "api_credentials")
        print(f"Non-existent user parameters: {missing_params}")
        
        print("✅ Plugin parameter access test complete")
        return True
        
    except Exception as e:
        print(f"❌ Plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 User Parameters System Test Suite")
    print("====================================")
    
    # Test 1: Basic user parameters functionality
    test1_success = test_user_parameters()
    
    # Test 2: Plugin parameter access
    test2_success = test_plugin_parameter_access()
    
    print(f"\n📊 Test Results:")
    print(f"   User Parameters: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Plugin Access: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! User parameters system is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
