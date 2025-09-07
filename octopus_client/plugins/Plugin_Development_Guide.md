# 🐙 Octopus Plugin Development Guide

## Table of Contents
1. [Plugin Basics](#plugin-basics)
2. [User Parameters Access](#user-parameters-access)
3. [NLP Integration](#nlp-integration)
4. [Configuration Management](#configuration-management)
5. [Response Formats](#response-formats)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

---

## Plugin Basics

### Basic Plugin Structure
```python
#!/usr/bin/env python3
"""
🔌 YOUR PLUGIN NAME
===================

Plugin description here.
"""

PLUGIN_NAME = "your_plugin_name"
PLUGIN_DESCRIPTION = "Description of what your plugin does"
PLUGIN_VERSION = "1.0.0"

def your_function_name(param1="default", param2=None):
    """
    Function description
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        dict: Response following Octopus format
    """
    try:
        # Your plugin logic here
        result = {
            "data": "your_result_data",
            "message": "Operation completed successfully"
        }
        
        return {
            "status": "success",
            "result": result,
            "type": "your_response_type"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "your_response_type"
        }
```

---

## User Parameters Access

### Client-Side Parameter Access
```python
# Import user parameter functions (client-side)
from global_cache_manager import (
    get_user_parameter, 
    get_user_parameters_category, 
    get_all_user_parameters,
    force_sync_user_parameters,
    # Simplified methods (auto-detect current user)
    get_param,
    get_params,
    get_api_credentials,
    get_notifications_config,
    get_integrations_config,
    get_params_summary
)

def example_with_user_params():
    """Example showing how to use user parameters in client-side plugins"""
    
    # Force sync parameters from server (optional)
    sync_success = force_sync_user_parameters()
    
    # === SIMPLIFIED METHODS (Recommended) ===
    
    # Get specific parameter (no username needed)
    api_key = get_param('api_credentials', 'servicenow_api_key', 'default_key')
    
    # Get all credentials in a category
    credentials = get_params('api_credentials')
    
    # Get notification settings
    email = get_param('notifications', 'email_address', 'no-email@example.com')
    notify = get_param('notifications', 'notify_on_completion', False)
    
    # Get all parameters by category
    all_api_creds = get_api_credentials()
    notifications = get_notifications_config()
    integrations = get_integrations_config()
    
    # Get organized summary
    summary = get_params_summary()
    
    # === ORIGINAL METHODS (Still available) ===
    
    # Get specific parameter (explicit method)
    api_key_old = get_user_parameter('api_credentials', 'servicenow_api_key', 'default_key')
    
    # Get integration settings
    servicenow_url = get_user_parameter('integrations', 'servicenow_instance', 'https://dev.service-now.com')
    jira_url = get_user_parameter('integrations', 'jira_base_url', 'https://company.atlassian.net')
    
    return {
        "status": "success",
        "result": {
            "api_key_set": api_key != 'default_key',
            "email": email,
            "notifications_enabled": notify,
            "servicenow_configured": servicenow_url != 'https://dev.service-now.com',
            "available_categories": list(summary.get('categories', {}).keys()),
            "total_params": sum(cat['param_count'] for cat in summary.get('categories', {}).values())
        },
        "type": "user_params_example"
    }
```

### Simplified Usage Examples
```python
# Get API credentials without specifying username
def get_servicenow_config():
    """Get ServiceNow configuration using simplified methods"""
    
    # Get API key
    api_key = get_param('api_credentials', 'servicenow_api_key')
    
    # Get instance URL  
    instance_url = get_param('integrations', 'servicenow_instance')
    
    # Get user email for notifications
    user_email = get_param('notifications', 'email_address', 'noreply@company.com')
    
    # Or get all integration settings at once
    integrations = get_integrations_config()
    
    return {
        'api_key': api_key,
        'instance_url': instance_url,
        'user_email': user_email,
        'all_integrations': integrations
    }

# Access parameters by category
def check_user_configuration():
    """Check what parameters are configured for the user"""
    
    # Get summary of all parameters
    summary = get_params_summary()
    
    # Get specific categories
    api_creds = get_api_credentials()
    notifications = get_notifications_config()
    
    config_status = {
        'user': summary.get('user'),
        'categories_available': list(summary.get('categories', {}).keys()),
        'api_credentials_set': len(api_creds) > 0,
        'notifications_configured': len(notifications) > 0,
        'servicenow_ready': bool(
            get_param('api_credentials', 'servicenow_api_key') and 
            get_param('integrations', 'servicenow_instance')
        )
    }
    
    return config_status
```

### Server-Side Parameter Access
```python
# Import user parameter functions (server-side)
from routes.user_profile_routes import get_user_parameter, get_user_category_parameters

def example_server_params(username="current_user"):
    """Example showing how to use user parameters in server-side plugins"""
    
    # Get specific parameter for a user
    api_key = get_user_parameter(username, 'api_credentials', 'servicenow_api_key', 'not_found')
    
    # Get all parameters in a category
    api_credentials = get_user_category_parameters(username, 'api_credentials')
    
    return {
        "status": "success",
        "result": {
            "user": username,
            "api_key_configured": api_key != 'not_found',
            "available_credentials": list(api_credentials.keys()) if api_credentials else []
        },
        "type": "server_params_example"
    }
```

### Available Parameter Categories
- **`api_credentials`** - API keys, tokens (encrypted storage)
  - `servicenow_api_key`, `jira_token`, `slack_webhook`
- **`notifications`** - Email preferences, notification settings
  - `email_address`, `notify_on_completion`, `notification_channels`
- **`integrations`** - Third-party service configurations
  - `servicenow_instance`, `jira_base_url`, `default_priority`
- **`preferences`** - User preferences
  - `timezone`, `date_format`, `ui_theme`
- **`custom`** - User-defined parameters

---

## NLP Integration

### Using NLP for Natural Language Processing
```python
def nlp_example(user_input="create incident with high priority"):
    """Example showing how to use NLP in plugins"""
    try:
        # Import NLP processor (server-side)
        from nlp_processor import NLPProcessor
        
        nlp = NLPProcessor()
        
        # Parse user input
        parsed = nlp.parse_request(user_input)
        
        # Extract entities and intents
        intent = parsed.get('intent', 'unknown')
        entities = parsed.get('entities', {})
        priority = entities.get('priority', 'medium')
        
        # Use NLP results in your logic
        result = {
            "user_input": user_input,
            "detected_intent": intent,
            "extracted_entities": entities,
            "priority": priority
        }
        
        return {
            "status": "success",
            "result": result,
            "type": "nlp_example"
        }
        
    except ImportError:
        return {
            "status": "error",
            "error": "NLP functionality only available on server side",
            "type": "nlp_example"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "nlp_example"
        }
```

### NLP Features Available
- **Intent Detection**: Identify what the user wants to do
- **Entity Extraction**: Extract key information (dates, priorities, names)
- **Context Understanding**: Maintain conversation context
- **Command Parsing**: Parse complex commands into actionable parameters

---

## Configuration Management

### Accessing Configuration
```python
def config_example():
    """Example showing how to access configuration in plugins"""
    try:
        # Client-side configuration access
        from config import get_current_config
        config = get_current_config()
        
        # Access configuration values
        server_url = config.SERVER_URL
        environment = config.ENVIRONMENT
        debug_mode = config.DEBUG
        
        # Or access specific config sections
        database_config = {
            "db_file": config.DB_FILE,
            "plugins_folder": config.PLUGINS_FOLDER
        }
        
        return {
            "status": "success",
            "result": {
                "server_url": server_url,
                "environment": environment,
                "debug_mode": debug_mode,
                "database_config": database_config
            },
            "type": "config_example"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "config_example"
        }
```

### Configuration Categories
- **Environment Settings**: `ENVIRONMENT`, `DEBUG`, `LOG_LEVEL`
- **Server Configuration**: `SERVER_URL`, `SERVER_PORT`, `CLIENT_PORT`
- **Database Settings**: `DB_FILE`
- **Plugin Settings**: `PLUGINS_FOLDER`, `PLUGINS_UPDATE_INTERVAL`
- **Task Settings**: `TASK_CHECK_INTERVAL`, `RETRY_DELAY`

---

## Response Formats

### Standard Response Format
All plugin functions should return a dictionary with this structure:

```python
{
    "status": "success" | "error",
    "result": {},           # Only for success responses
    "error": "error_msg",   # Only for error responses  
    "type": "response_type" # Plugin-specific response type
}
```

### Success Response Examples
```python
# Simple success response
{
    "status": "success",
    "result": {
        "message": "Task completed successfully",
        "data": {"key": "value"}
    },
    "type": "task_completion"
}

# Data response
{
    "status": "success", 
    "result": {
        "records": [{"id": 1, "name": "Item 1"}],
        "total_count": 1,
        "query_time": 0.05
    },
    "type": "data_query"
}

# Action response
{
    "status": "success",
    "result": {
        "action": "incident_created",
        "incident_id": "INC0001234",
        "url": "https://instance.service-now.com/nav_to.do?uri=incident.do?sys_id=12345"
    },
    "type": "servicenow_incident"
}
```

### Error Response Examples
```python
# Simple error
{
    "status": "error",
    "error": "Invalid API key provided",
    "type": "authentication_error"
}

# Detailed error
{
    "status": "error",
    "error": "Failed to connect to ServiceNow instance",
    "type": "connection_error",
    "details": {
        "url": "https://dev.service-now.com",
        "timeout": 30,
        "retry_count": 3
    }
}
```

### Special Response Types
```python
# File response
{
    "status": "success",
    "result": {
        "file_path": "/path/to/generated/report.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf"
    },
    "type": "file_generation"
}

# Streaming response
{
    "status": "success",
    "result": {
        "stream_id": "stream_12345",
        "message": "Data streaming started",
        "expected_duration": 60
    },
    "type": "data_stream"
}

# Notification response
{
    "status": "success",
    "result": {
        "notification_sent": True,
        "recipients": ["user@example.com"],
        "method": "email"
    },
    "type": "notification"
}
```

---

## Best Practices

### 1. Error Handling
```python
def robust_plugin_function():
    try:
        # Your main logic
        result = perform_operation()
        
        return {
            "status": "success",
            "result": result,
            "type": "operation"
        }
        
    except ConnectionError as e:
        return {
            "status": "error",
            "error": f"Connection failed: {e}",
            "type": "connection_error"
        }
    except ValueError as e:
        return {
            "status": "error", 
            "error": f"Invalid input: {e}",
            "type": "validation_error"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {e}",
            "type": "unexpected_error"
        }
```

### 2. Logging
```python
import logging

def logged_plugin_function():
    logger = logging.getLogger(__name__)
    
    logger.info("Starting plugin operation")
    
    try:
        # Your logic
        logger.debug("Processing step 1")
        result = step_1()
        
        logger.debug("Processing step 2") 
        final_result = step_2(result)
        
        logger.info("Plugin operation completed successfully")
        return {
            "status": "success",
            "result": final_result,
            "type": "logged_operation"
        }
        
    except Exception as e:
        logger.error(f"Plugin operation failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "type": "logged_operation"
        }
```

### 3. Parameter Validation
```python
def validated_function(required_param, optional_param="default"):
    # Validate required parameters
    if not required_param:
        return {
            "status": "error",
            "error": "required_param is mandatory",
            "type": "validation_error"
        }
    
    # Validate parameter types
    if not isinstance(optional_param, str):
        return {
            "status": "error",
            "error": "optional_param must be a string", 
            "type": "validation_error"
        }
    
    # Your logic here
    return {
        "status": "success",
        "result": {"processed": True},
        "type": "validated_function"
    }
```

---

## Examples

### Complete Plugin Example
```python
#!/usr/bin/env python3
"""
🎯 INCIDENT MANAGER PLUGIN
==========================

Creates and manages ServiceNow incidents using user parameters.
"""

PLUGIN_NAME = "incident_manager"
PLUGIN_DESCRIPTION = "ServiceNow incident management with user parameters"
PLUGIN_VERSION = "1.0.0"

import logging
import requests

def create_incident(title, description="", priority="medium", category="general"):
    """
    Create a ServiceNow incident using user's API credentials
    
    Args:
        title: Incident title
        description: Incident description
        priority: Incident priority (low, medium, high, critical)
        category: Incident category
        
    Returns:
        dict: Creation result with incident details
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Get user parameters
        from global_cache_manager import get_user_parameter
        
        # Get user's ServiceNow configuration
        api_key = get_user_parameter('api_credentials', 'servicenow_api_key')
        instance_url = get_user_parameter('integrations', 'servicenow_instance')
        email = get_user_parameter('notifications', 'email_address', 'no-reply@company.com')
        
        # Validate configuration
        if not api_key or not instance_url:
            return {
                "status": "error",
                "error": "ServiceNow not configured. Please set API key and instance URL in user parameters.",
                "type": "configuration_error"
            }
        
        # Prepare incident data
        incident_data = {
            "short_description": title,
            "description": description,
            "priority": priority,
            "category": category,
            "caller_id": email,
            "state": "1"  # New
        }
        
        # Create incident via ServiceNow API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{instance_url}/api/now/table/incident",
            json=incident_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            incident = response.json()['result']
            
            # Send notification if enabled
            notify_enabled = get_user_parameter('notifications', 'notify_on_completion', True)
            if notify_enabled:
                # Send notification logic here
                pass
            
            logger.info(f"Incident created: {incident['number']}")
            
            return {
                "status": "success",
                "result": {
                    "incident_number": incident['number'],
                    "sys_id": incident['sys_id'],
                    "state": incident['state'],
                    "url": f"{instance_url}/nav_to.do?uri=incident.do?sys_id={incident['sys_id']}",
                    "created_by": email
                },
                "type": "incident_created"
            }
        else:
            logger.error(f"ServiceNow API error: {response.status_code}")
            return {
                "status": "error",
                "error": f"ServiceNow API returned {response.status_code}: {response.text}",
                "type": "servicenow_error"
            }
            
    except ImportError:
        return {
            "status": "error",
            "error": "User parameters not available in this environment",
            "type": "environment_error"
        }
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        return {
            "status": "error",
            "error": f"Network error: {e}",
            "type": "network_error"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "type": "unexpected_error"
        }


def get_incident_status(incident_number):
    """
    Get the status of a ServiceNow incident
    
    Args:
        incident_number: ServiceNow incident number
        
    Returns:
        dict: Incident status information
    """
    try:
        from global_cache_manager import get_user_parameter
        
        api_key = get_user_parameter('api_credentials', 'servicenow_api_key')
        instance_url = get_user_parameter('integrations', 'servicenow_instance')
        
        if not api_key or not instance_url:
            return {
                "status": "error",
                "error": "ServiceNow not configured",
                "type": "configuration_error"
            }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.get(
            f"{instance_url}/api/now/table/incident?sysparm_query=number={incident_number}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            incidents = response.json()['result']
            if incidents:
                incident = incidents[0]
                return {
                    "status": "success",
                    "result": {
                        "number": incident['number'],
                        "state": incident['state'],
                        "priority": incident['priority'],
                        "short_description": incident['short_description'],
                        "updated": incident['sys_updated_on']
                    },
                    "type": "incident_status"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Incident {incident_number} not found",
                    "type": "not_found"
                }
        else:
            return {
                "status": "error",
                "error": f"ServiceNow API error: {response.status_code}",
                "type": "servicenow_error"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "type": "unexpected_error"
        }
```

This guide provides comprehensive coverage of plugin development in the Octopus system, including user parameters, NLP, configuration, and proper response formats.
