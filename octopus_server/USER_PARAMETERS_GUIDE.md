# 👤 User Profile Parameters System

## Overview

The User Profile Parameters system allows users to configure personal settings and credentials that plugins can automatically access. This enables standardized plugins to work with customized user-specific configurations like API keys, service URLs, preferences, and more.

## Features

✅ **Secure Storage** - Sensitive parameters (API keys, passwords) are encrypted  
✅ **Categorized Organization** - Parameters grouped by category (API Credentials, Integrations, etc.)  
✅ **Type Support** - String, Integer, Float, Boolean, and JSON parameter types  
✅ **Plugin Integration** - Plugins automatically access user parameters from cache  
✅ **Web Interface** - User-friendly web UI for managing parameters  
✅ **Import/Export** - Backup and restore parameter configurations  
✅ **Cache Integration** - Fast parameter access through caching system  

## System Architecture

### Database Tables

**user_parameters**
- Stores individual parameter values with encryption for sensitive data
- Fields: username, category, param_name, param_value, param_type, is_encrypted, is_sensitive, description

**user_parameter_categories**  
- Defines parameter categories with display information
- Fields: username, category_name, display_name, description, icon, sort_order

### Key Components

**UserParametersManager** (`user_parameters.py`)
- Core class for parameter CRUD operations
- Handles encryption/decryption of sensitive values
- Manages caching integration

**User Profile Routes** (`routes/user_profile_routes.py`)
- Flask routes for web UI and API endpoints
- Helper functions for plugins to access parameters

**User Profile Template** (`templates/user_profile.html`)
- Web interface for managing parameters
- Category organization and parameter editing

## Default Categories

| Category | Description | Icon | Use Cases |
|----------|-------------|------|-----------|
| **api_credentials** | API keys and authentication tokens | 🔑 | ServiceNow API key, Jira token, Slack webhook |
| **integrations** | Third-party service configurations | 🔌 | Service URLs, default priorities, instance names |
| **notifications** | Email and messaging preferences | 🔔 | Email addresses, notification channels, preferences |
| **preferences** | General user preferences | ⚙️ | Timezone, refresh intervals, UI settings |
| **custom** | User-defined custom parameters | 🔧 | Project-specific settings, custom workflows |

## Usage Guide

### 1. Web Interface

Navigate to `/profile` in the Octopus web interface to:

- **View Parameters**: See all parameters organized by category
- **Add Parameters**: Create new parameters with type and sensitivity settings
- **Edit Parameters**: Modify existing parameter values
- **Delete Parameters**: Remove unused parameters
- **Manage Categories**: Create custom categories for organization
- **Export/Import**: Backup and restore parameter configurations

### 2. Plugin Integration

Plugins can access user parameters using helper functions:

```python
# Import helper functions
from routes.user_profile_routes import get_user_parameter, get_user_category_parameters

def my_plugin_function(username="unknown"):
    # Get individual parameter
    api_key = get_user_parameter(username, "api_credentials", "servicenow_api_key", "default_key")
    
    # Get all parameters in a category
    integrations = get_user_category_parameters(username, "integrations")
    instance_url = integrations.get("servicenow_instance", "https://demo.service-now.com")
    
    # Use parameters in plugin logic
    return create_incident_with_config(api_key, instance_url)
```

### 3. Task Execution

When creating tasks, ensure the username is passed to plugins:

```json
{
    "name": "Create ServiceNow Incident",
    "plugin": "servicenow_example", 
    "action": "create_incident",
    "args": ["System issue", "Detailed description", "2", "john_doe"],
    "owner": "john_doe"
}
```

### 4. API Endpoints

**GET /api/profile/parameters**
- Retrieve user parameters (optionally filtered by category)

**POST /api/profile/parameters**
- Create or update a parameter
- Body: `{category, param_name, value, param_type, is_sensitive, description}`

**DELETE /api/profile/parameters/{category}/{param_name}**
- Delete a specific parameter

**POST /api/profile/cache-refresh**
- Refresh parameter cache for faster access

**GET /api/profile/export**
- Export all parameters as JSON

## Example Configurations

### ServiceNow Integration
```json
{
    "api_credentials": {
        "servicenow_api_key": {
            "value": "your_api_key_here",
            "type": "string",
            "sensitive": true,
            "description": "ServiceNow API Key for incident management"
        }
    },
    "integrations": {
        "servicenow_instance": {
            "value": "https://mycompany.service-now.com",
            "type": "string", 
            "sensitive": false,
            "description": "ServiceNow instance URL"
        },
        "default_priority": {
            "value": "2",
            "type": "string",
            "sensitive": false,
            "description": "Default priority for tickets (1-5)"
        }
    }
}
```

### Notification Preferences
```json
{
    "notifications": {
        "email_address": {
            "value": "user@company.com",
            "type": "string",
            "sensitive": false,
            "description": "Primary email for notifications"
        },
        "notify_on_completion": {
            "value": true,
            "type": "bool",
            "sensitive": false,
            "description": "Send notification when tasks complete"
        },
        "notification_channels": {
            "value": ["email", "slack", "teams"],
            "type": "json",
            "sensitive": false,
            "description": "Preferred notification channels"
        }
    }
}
```

## Plugin Development Guide

### 1. Updated Function Signatures

Add username parameter to plugin functions:

```python
# Before
def create_incident(summary, description="", priority="3"):
    # Plugin logic
    pass

# After  
def create_incident(summary, description="", priority="3", username="unknown"):
    # Get user parameters
    api_key = get_user_parameter(username, "api_credentials", "servicenow_api_key")
    instance = get_user_parameter(username, "integrations", "servicenow_instance")
    
    # Plugin logic with user-specific configuration
    pass
```

### 2. Parameter Access Patterns

**Get individual parameter with fallback:**
```python
api_key = get_user_parameter(username, "api_credentials", "api_key", "demo_key")
```

**Get category parameters:**
```python
creds = get_user_category_parameters(username, "api_credentials")
api_key = creds.get("servicenow_api_key", "demo_key")
```

**Handle missing parameters gracefully:**
```python
try:
    config = get_user_category_parameters(username, "integrations")
    instance_url = config.get("servicenow_instance", "https://demo.service-now.com")
except Exception as e:
    print(f"Warning: Could not load user parameters: {e}")
    instance_url = "https://demo.service-now.com"
```

### 3. Structured Response Integration

Combine user parameters with structured responses:

```python
def enhanced_plugin_function(username="unknown"):
    # Get user configuration
    config = get_user_category_parameters(username, "integrations")
    creds = get_user_category_parameters(username, "api_credentials")
    
    # Plugin logic
    result = perform_operation(config, creds)
    
    # Return structured response
    return {
        "status_code": 200,
        "message": f"Operation completed for {config.get('instance_name', 'default')}",
        "data": [
            {
                "type": "cache",
                "name": "last_operation_instance",
                "value": config.get("instance_url")
            },
            {
                "type": "db", 
                "name": "operation_result",
                "value": {
                    "username": username,
                    "instance": config.get("instance_url"),
                    "result": result,
                    "timestamp": time.time()
                }
            }
        ]
    }
```

## Security Considerations

### 1. Encryption
- Sensitive parameters are encrypted using XOR encryption with a generated key
- Encryption key is stored in `user_params_key.txt` (keep secure)
- Consider using stronger encryption (AES) for production environments

### 2. Access Control
- Parameters are user-specific - users can only access their own parameters
- Authentication required for all parameter operations
- Cache keys include username for isolation

### 3. Best Practices
- Mark API keys, passwords, and tokens as sensitive
- Use descriptive parameter names and descriptions
- Regularly review and update stored credentials
- Export configurations for backup purposes

## Performance Optimization

### 1. Caching Strategy
- Parameters cached for 1 hour by default
- Cache keys: `user_params_{username}_{category}`
- Individual parameter access hits cache first, falls back to database

### 2. Database Optimization
- Indexes on username, category, and parameter name
- Unique constraints prevent duplicate parameters
- Efficient queries for category-based retrieval

### 3. Plugin Performance
- Helper functions minimize database queries
- Category-based parameter retrieval reduces round trips
- Graceful fallbacks prevent plugin failures

## Migration Guide

### From Hard-coded Configuration

**Before:**
```python
def create_incident(summary):
    api_key = "hardcoded_key"
    instance = "https://company.service-now.com"
    # Plugin logic
```

**After:**
```python
def create_incident(summary, username="unknown"):
    api_key = get_user_parameter(username, "api_credentials", "servicenow_api_key", "demo_key")
    instance = get_user_parameter(username, "integrations", "servicenow_instance", "https://demo.service-now.com")
    # Plugin logic
```

### Task Creation Updates

**Before:**
```json
{
    "plugin": "servicenow",
    "action": "create_incident", 
    "args": ["System issue"]
}
```

**After:**
```json
{
    "plugin": "servicenow",
    "action": "create_incident",
    "args": ["System issue", "Description", "2", "john_doe"],
    "owner": "john_doe"
}
```

## Troubleshooting

### Common Issues

**1. Parameters not loading**
- Check if user parameters table exists
- Verify username is correct
- Check cache refresh status

**2. Encryption errors**
- Ensure encryption key file exists
- Check file permissions
- Verify parameter was marked as sensitive

**3. Plugin parameter access fails**
- Verify import paths are correct
- Check if parameter exists in database
- Ensure fallback values are provided

### Debug Commands

```python
# Test parameter manager
from user_parameters import UserParametersManager
from dbhelper import get_db_connection

class DBHelper:
    def get_connection(self):
        return get_db_connection()

params_manager = UserParametersManager(DBHelper())

# Check if parameter exists
param = params_manager.get_parameter("username", "category", "param_name")
print(f"Parameter value: {param}")

# List all user parameters
all_params = params_manager.get_user_parameters("username")
print(f"All parameters: {all_params}")
```

## Testing

Run the test suite to verify the system:

```bash
cd octopus_server
python test_user_parameters.py
```

The test will:
- Initialize parameter tables
- Create example categories and parameters
- Test parameter retrieval and caching
- Verify plugin access functions
- Test encryption/decryption of sensitive data

## Next Steps

1. **Set up your profile**: Navigate to `/profile` and configure your parameters
2. **Update plugins**: Modify existing plugins to use user parameters  
3. **Create custom categories**: Add categories specific to your use cases
4. **Test integration**: Create tasks and verify plugins use your configuration
5. **Export backup**: Save your parameter configuration for safekeeping

The User Profile Parameters system enables powerful customization while maintaining plugin standardization. Users can configure their tools once and have all plugins automatically use their personalized settings!
