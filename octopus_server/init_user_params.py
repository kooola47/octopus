#!/usr/bin/env python3
"""
🚀 Initialize User Parameters System
===================================

Script to initialize the user parameters system with sample data.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def initialize_user_parameters():
    """Initialize user parameters system with sample data"""
    print("🚀 Initializing User Parameters System...")
    
    try:
        from user_parameters import UserParametersManager, DEFAULT_CATEGORIES
        import sqlite3
        
        # Use direct SQLite connection like the existing system
        class DBHelper:
            def get_connection(self):
                return sqlite3.connect('octopus.db')
        
        # Initialize manager
        params_manager = UserParametersManager(DBHelper())
        print("✅ User Parameters Manager initialized")
        
        # Create sample user
        sample_user = "admin"
        
        # Set up default categories
        print("📁 Setting up default categories...")
        for cat_name, cat_info in DEFAULT_CATEGORIES.items():
            success = params_manager.set_category(
                sample_user, cat_name, cat_info['display_name'],
                cat_info['description'], cat_info['icon'], cat_info['sort_order']
            )
            print(f"   {'✅' if success else '❌'} {cat_info['display_name']}")
        
        # Add some sample parameters
        print("🔧 Adding sample parameters...")
        
        # API Credentials (all sensitive)
        sample_params = [
            (sample_user, "api_credentials", "servicenow_api_key", "demo_sn_key_12345", "string", True, "ServiceNow API Key for demo"),
            (sample_user, "api_credentials", "jira_token", "demo_jira_token_67890", "string", True, "Jira API Token for demo"),
            (sample_user, "api_credentials", "slack_webhook", "https://hooks.slack.com/demo", "string", True, "Slack webhook URL"),
            
            # Integrations (non-sensitive)
            (sample_user, "integrations", "servicenow_instance", "https://demo.service-now.com", "string", False, "ServiceNow instance URL"),
            (sample_user, "integrations", "jira_base_url", "https://demo.atlassian.net", "string", False, "Jira base URL"),
            (sample_user, "integrations", "default_priority", "3", "string", False, "Default priority (1-5)"),
            
            # Notifications
            (sample_user, "notifications", "email_address", "admin@company.com", "string", False, "Primary email"),
            (sample_user, "notifications", "notify_on_completion", True, "bool", False, "Notify when tasks complete"),
            
            # Preferences  
            (sample_user, "preferences", "timezone", "America/New_York", "string", False, "User timezone"),
            (sample_user, "preferences", "task_refresh_interval", 30, "int", False, "Refresh interval in seconds"),
        ]
        
        for username, category, param_name, value, param_type, is_sensitive, description in sample_params:
            success = params_manager.set_parameter(
                username, category, param_name, value, param_type, is_sensitive, description
            )
            sensitive_marker = "🔒" if is_sensitive else "🔓"
            print(f"   {'✅' if success else '❌'} {sensitive_marker} {category}.{param_name}")
        
        print("\n📊 Summary:")
        all_params = params_manager.get_user_parameters(sample_user)
        for category, params in all_params.items():
            print(f"   📂 {category}: {len(params)} parameters")
        
        print(f"\n🎉 User Parameters System initialized successfully!")
        print(f"📝 Sample user created: {sample_user}")
        print("🌐 You can now:")
        print("   1. Start the Octopus server")
        print("   2. Login with user 'admin'")
        print("   3. Navigate to /profile to see the parameters")
        print("   4. Create plugins that use user parameters")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_user_parameters()
    if success:
        print("\n✅ Initialization complete!")
    else:
        print("\n❌ Initialization failed!")
        sys.exit(1)
