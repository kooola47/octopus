#!/usr/bin/env python3
"""
🧪 USER PARAMETERS TEST PLUGIN (SERVER SIDE)
==============================================

Test plugin to demonstrate user parameters functionality on server side.
Shows how plugins can access user-specific configuration parameters.
"""

PLUGIN_NAME = "user_params_test"
PLUGIN_DESCRIPTION = "Test plugin for user parameters functionality (server side)"
PLUGIN_VERSION = "1.0.0"

def test_user_parameters(username="aries"):
    """
    Test function to demonstrate user parameters access on server side
    
    Args:
        username: Username to test parameters for
        
    Returns:
        dict: Test results and user parameters data
    """
    try:
        import time
        
        result = {
            "plugin": PLUGIN_NAME,
            "test": "user_parameters_access_server",
            "username": username,
            "timestamp": time.time()
        }
        
        # Test server-side user parameter access
        try:
            from routes.user_profile_routes import get_user_parameter, get_user_category_parameters
            
            # Test 1: Get a specific user parameter
            api_key = get_user_parameter(username, 'api_credentials', 'servicenow_api_key', 'not_found')
            result["test_specific_param"] = {
                "category": "api_credentials",
                "param": "servicenow_api_key", 
                "value": api_key if api_key != 'not_found' else "NOT_SET"
            }
            
            # Test 2: Get all parameters in a category
            api_credentials = get_user_category_parameters(username, 'api_credentials')
            result["test_category_params"] = {
                "category": "api_credentials",
                "params_count": len(api_credentials) if api_credentials else 0,
                "param_names": list(api_credentials.keys()) if api_credentials else []
            }
            
            # Test 3: Get notification preferences  
            email = get_user_parameter(username, 'notifications', 'email_address', 'no_email@example.com')
            notify_on_completion = get_user_parameter(username, 'notifications', 'notify_on_completion', False)
            result["test_notifications"] = {
                "email": email,
                "notify_on_completion": notify_on_completion
            }
            
            # Test 4: Get integration settings
            servicenow_instance = get_user_parameter(username, 'integrations', 'servicenow_instance', 'no_instance')
            default_priority = get_user_parameter(username, 'integrations', 'default_priority', 'medium')
            result["test_integrations"] = {
                "servicenow_instance": servicenow_instance,
                "default_priority": default_priority
            }
            
            result["server_side_access"] = "success"
            
        except ImportError as e:
            result["server_side_access"] = f"Import error: {e}"
        except Exception as e:
            result["server_side_access"] = f"Error: {e}"
        
        return {
            "status": "success",
            "result": result,
            "type": "user_parameters_test"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "type": "user_parameters_test"
        }


def setup_sample_parameters(username="aries"):
    """
    Set up sample user parameters for testing
    
    Args:
        username: Username to set up parameters for
        
    Returns:
        dict: Setup results
    """
    try:
        from user_parameters import UserParametersManager
        from dbhelper import get_db_connection
        
        class DBHelper:
            def get_connection(self):
                return get_db_connection()
        
        params_manager = UserParametersManager(DBHelper())
        
        # Set up sample API credentials
        params_manager.set_parameter(
            username, 'api_credentials', 'servicenow_api_key', 
            'sample_key_12345', 'string', True, 'ServiceNow API Key'
        )
        
        params_manager.set_parameter(
            username, 'api_credentials', 'jira_token',
            'jira_token_67890', 'string', True, 'Jira API Token'
        )
        
        params_manager.set_parameter(
            username, 'api_credentials', 'slack_webhook',
            'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX', 
            'string', True, 'Slack Webhook URL'
        )
        
        # Set up notification preferences
        params_manager.set_parameter(
            username, 'notifications', 'email_address',
            'aries@example.com', 'string', False, 'Email for notifications'
        )
        
        params_manager.set_parameter(
            username, 'notifications', 'notify_on_completion',
            'true', 'bool', False, 'Send notifications when tasks complete'
        )
        
        params_manager.set_parameter(
            username, 'notifications', 'notification_channels',
            '["email", "slack"]', 'json', False, 'Preferred notification channels'
        )
        
        # Set up integration settings
        params_manager.set_parameter(
            username, 'integrations', 'servicenow_instance',
            'https://dev12345.service-now.com', 'string', False, 'ServiceNow instance URL'
        )
        
        params_manager.set_parameter(
            username, 'integrations', 'jira_base_url',
            'https://company.atlassian.net', 'string', False, 'Jira base URL'
        )
        
        params_manager.set_parameter(
            username, 'integrations', 'default_priority',
            'high', 'string', False, 'Default priority for tickets'
        )
        
        # Set up preferences
        params_manager.set_parameter(
            username, 'preferences', 'timezone',
            'UTC', 'string', False, 'User timezone'
        )
        
        params_manager.set_parameter(
            username, 'preferences', 'date_format',
            'YYYY-MM-DD', 'string', False, 'Preferred date format'
        )
        
        # Cache the parameters in global cache
        try:
            from services.global_cache_manager import get_global_cache_manager
            cache_manager = get_global_cache_manager()
            params_manager.cache_user_parameters(username, cache_manager)
            cache_status = "Parameters cached successfully"
        except Exception as e:
            cache_status = f"Cache error: {e}"
        
        return {
            "status": "success",
            "message": f"Sample parameters set up for user {username}",
            "cache_status": cache_status,
            "type": "setup"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "setup"
        }
