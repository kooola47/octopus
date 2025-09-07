#!/usr/bin/env python3
"""
🎯 IMPROVED USER PARAMETERS DEMO
===============================

Demonstrates the improved user parameters system with simplified access methods.
No need to specify username - automatically detects current user.
"""

PLUGIN_NAME = "user_params_demo_improved"
PLUGIN_DESCRIPTION = "Improved user parameters demo with simplified access"
PLUGIN_VERSION = "2.0.0"

def demo_simplified_access():
    """
    Demo simplified user parameters access without specifying username
    
    Returns:
        dict: Demo results showing simplified parameter access
    """
    try:
        import time
        
        # Import simplified parameter access functions
        from global_cache_manager import (
            get_param,
            get_params,
            get_api_credentials,
            get_notifications_config,
            get_integrations_config,
            get_params_summary,
            list_param_categories
        )
        
        result = {
            "plugin": PLUGIN_NAME,
            "demo": "simplified_user_params_access",
            "timestamp": time.time()
        }
        
        # === 1. GET SPECIFIC PARAMETERS ===
        result["specific_params"] = {
            "servicenow_api_key": get_param('api_credentials', 'servicenow_api_key', 'NOT_SET'),
            "email_address": get_param('notifications', 'email_address', 'no-email@example.com'),
            "servicenow_instance": get_param('integrations', 'servicenow_instance', 'NOT_SET'),
            "notify_on_completion": get_param('notifications', 'notify_on_completion', False)
        }
        
        # === 2. GET PARAMETERS BY CATEGORY ===
        result["by_category"] = {
            "api_credentials": get_api_credentials(),
            "notifications": get_notifications_config(),
            "integrations": get_integrations_config()
        }
        
        # === 3. GET ALL PARAMETERS ===
        all_params = get_params()
        result["all_categories"] = list(all_params.keys())
        result["total_params"] = sum(len(params) for params in all_params.values())
        
        # === 4. GET PARAMETERS SUMMARY ===
        summary = get_params_summary()
        result["summary"] = {
            "user": summary.get("user", "unknown"),
            "total_categories": summary.get("total_categories", 0),
            "category_names": list(summary.get("categories", {}).keys()),
            "last_sync": summary.get("last_sync", 0)
        }
        
        # === 5. CONFIGURATION STATUS CHECK ===
        result["config_status"] = {
            "servicenow_ready": bool(
                get_param('api_credentials', 'servicenow_api_key') and 
                get_param('integrations', 'servicenow_instance')
            ),
            "jira_ready": bool(
                get_param('api_credentials', 'jira_token') and 
                get_param('integrations', 'jira_base_url')
            ),
            "notifications_configured": bool(
                get_param('notifications', 'email_address')
            )
        }
        
        # === 6. LIST AVAILABLE CATEGORIES ===
        result["available_categories"] = list_param_categories()
        
        return {
            "status": "success",
            "result": result,
            "type": "simplified_user_params_demo"
        }
        
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Import error: {e}. Simplified user parameters functions not available.",
            "type": "import_error"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "unexpected_error"
        }


def demo_organized_display():
    """
    Demo organized display of user parameters by category
    
    Returns:
        dict: Organized parameters display
    """
    try:
        from global_cache_manager import get_params, get_params_summary
        
        # Get all parameters organized by category
        all_params = get_params()
        summary = get_params_summary()
        
        # Create organized display
        organized_display = {
            "user_info": {
                "username": summary.get("user", "unknown"),
                "total_categories": len(all_params),
                "total_parameters": sum(len(params) for params in all_params.values())
            },
            "categories": {}
        }
        
        # Process each category
        for category, params in all_params.items():
            category_info = {
                "param_count": len(params),
                "parameters": {}
            }
            
            for param_name, param_data in params.items():
                if isinstance(param_data, dict):
                    # Extract parameter information
                    param_info = {
                        "description": param_data.get("description", "No description"),
                        "type": param_data.get("type", "string"),
                        "has_value": param_data.get("value") is not None,
                        "is_sensitive": param_data.get("type") == "string" and len(str(param_data.get("value", ""))) > 20
                    }
                    
                    # Show value but mask sensitive data
                    value = param_data.get("value", "")
                    if param_info["is_sensitive"]:
                        param_info["value"] = f"{str(value)[:4]}...{str(value)[-4:]}" if len(str(value)) > 8 else "***"
                    else:
                        param_info["value"] = value
                        
                    category_info["parameters"][param_name] = param_info
                else:
                    category_info["parameters"][param_name] = {
                        "value": param_data,
                        "type": "unknown",
                        "description": "Legacy parameter format",
                        "has_value": param_data is not None,
                        "is_sensitive": False
                    }
            
            organized_display["categories"][category] = category_info
        
        return {
            "status": "success",
            "result": organized_display,
            "type": "organized_params_display"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "display_error"
        }


def demo_practical_usage():
    """
    Demo practical usage examples for common scenarios
    
    Returns:
        dict: Practical usage examples
    """
    try:
        from global_cache_manager import get_param, get_params
        
        # === SCENARIO 1: ServiceNow Integration Setup ===
        servicenow_config = {
            "api_key": get_param('api_credentials', 'servicenow_api_key'),
            "instance_url": get_param('integrations', 'servicenow_instance'),
            "default_priority": get_param('integrations', 'default_priority', 'medium'),
            "user_email": get_param('notifications', 'email_address', 'noreply@company.com')
        }
        
        servicenow_ready = all([
            servicenow_config["api_key"],
            servicenow_config["instance_url"]
        ])
        
        # === SCENARIO 2: Notification Settings ===
        notification_config = get_params('notifications')
        notifications_enabled = bool(notification_config.get('notify_on_completion', {}).get('value', False))
        
        # === SCENARIO 3: All API Credentials Status ===
        api_creds = get_params('api_credentials')
        available_apis = []
        for api_name, api_data in api_creds.items():
            if isinstance(api_data, dict) and api_data.get('value'):
                available_apis.append(api_name)
        
        return {
            "status": "success",
            "result": {
                "servicenow": {
                    "configured": servicenow_ready,
                    "config": servicenow_config
                },
                "notifications": {
                    "enabled": notifications_enabled,
                    "config": notification_config
                },
                "available_apis": available_apis,
                "total_configured_apis": len(available_apis)
            },
            "type": "practical_usage_demo"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "practical_usage_error"
        }
