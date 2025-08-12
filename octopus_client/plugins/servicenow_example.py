#!/usr/bin/env python3
"""
📋 EXAMPLE PLUGIN: ServiceNow Integration
========================================

Example plugin that demonstrates the structured response format.
Shows how to create incidents and store results in cache/db/files.
"""

import json
import time
import random


def create_incident(summary: str, description: str = "", priority: str = "3", username: str = "unknown") -> dict:
    """
    Create a ServiceNow incident and return structured response.
    Now uses user parameters for API credentials and instance configuration.
    
    Args:
        summary: Brief description of the incident
        description: Detailed description 
        priority: Priority level (1-5)
        username: Username for parameter lookup
    
    Returns:
        Structured plugin response
    """
    
    # Get user parameters for ServiceNow configuration
    try:
        # Import the helper function
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'octopus_server', 'routes'))
        from user_profile_routes import get_user_parameter, get_user_category_parameters
        
        # Get ServiceNow configuration from user parameters
        api_credentials = get_user_category_parameters(username, 'api_credentials')
        integrations = get_user_category_parameters(username, 'integrations')
        
        # Get specific parameters with defaults
        api_key = api_credentials.get('servicenow_api_key', 'demo_key')
        instance_url = integrations.get('servicenow_instance', 'https://demo.service-now.com')
        default_priority = integrations.get('default_priority', priority)
        
        # Use the configured priority if not specified
        if priority == "3":  # Default priority
            priority = default_priority
            
    except Exception as e:
        # Fallback to demo values if parameter system not available
        api_key = 'demo_key'
        instance_url = 'https://demo.service-now.com'
        print(f"Warning: Could not load user parameters, using demo values: {e}")
    
    # Simulate API call
    time.sleep(1)  # Simulate network delay
    
    # Simulate success/failure
    if random.random() < 0.9:  # 90% success rate
        # Success case
        incident_id = f"INC{random.randint(1000000, 9999999)}"
        incident_number = f"INC{random.randint(100000, 999999)}"
        
        response = {
            "status_code": 201,
            "message": f"Incident {incident_number} created successfully in {instance_url}",
            "data": [
                {
                    "type": "cache",
                    "name": "last_incident_id",
                    "value": incident_id
                },
                {
                    "type": "cache", 
                    "name": "last_incident_number",
                    "value": incident_number
                },
                {
                    "type": "cache",
                    "name": "servicenow_instance",
                    "value": instance_url
                },
                {
                    "type": "file",
                    "name": f"incident_{incident_number}.json",
                    "value": {
                        "incident_id": incident_id,
                        "incident_number": incident_number,
                        "summary": summary,
                        "description": description,
                        "priority": priority,
                        "instance_url": instance_url,
                        "api_key_used": api_key[:8] + "..." if len(api_key) > 8 else "demo",
                        "created_at": time.time(),
                        "status": "New"
                    }
                },
                {
                    "type": "db",
                    "name": "incident_creation",
                    "value": {
                        "incident_id": incident_id,
                        "incident_number": incident_number,
                        "summary": summary,
                        "priority": priority,
                        "instance": instance_url,
                        "created_at": time.time(),
                        "username": username
                    }
                }
            ]
        }
    else:
        # Failure case
        response = {
            "status_code": 500,
            "message": f"Failed to create incident in {instance_url}: ServiceNow API timeout",
            "data": [
                {
                    "type": "cache",
                    "name": "last_error",
                    "value": f"API timeout at {time.time()}"
                },
                {
                    "type": "file",
                    "name": "error_log.txt",
                    "value": f"ServiceNow API timeout occurred at {time.ctime()}\nInstance: {instance_url}\nSummary: {summary}"
                }
            ]
        }
    
    return response


def update_incident(incident_id: str, status: str = "In Progress", notes: str = "") -> dict:
    """
    Update an existing ServiceNow incident.
    
    Args:
        incident_id: The incident ID to update
        status: New status for the incident
        notes: Additional notes to add
    
    Returns:
        Structured plugin response
    """
    
    # Simulate API call
    time.sleep(0.5)
    
    if random.random() < 0.95:  # 95% success rate
        response = {
            "status_code": 200,
            "message": f"Incident {incident_id} updated to {status}",
            "data": [
                {
                    "type": "cache",
                    "name": f"incident_{incident_id}_status",
                    "value": status
                },
                {
                    "type": "file",
                    "name": f"incident_{incident_id}_update.json",
                    "value": {
                        "incident_id": incident_id,
                        "new_status": status,
                        "notes": notes,
                        "updated_at": time.time()
                    }
                },
                {
                    "type": "db",
                    "name": "incident_update",
                    "value": {
                        "incident_id": incident_id,
                        "status": status,
                        "notes": notes,
                        "updated_at": time.time()
                    }
                }
            ]
        }
    else:
        response = {
            "status_code": 404,
            "message": f"Incident {incident_id} not found",
            "data": [
                {
                    "type": "cache",
                    "name": "last_error",
                    "value": f"Incident {incident_id} not found"
                }
            ]
        }
    
    return response


def get_incident_stats() -> dict:
    """
    Get incident statistics and store in various formats.
    
    Returns:
        Structured plugin response with statistics
    """
    
    # Simulate gathering stats
    stats = {
        "total_incidents": random.randint(100, 1000),
        "open_incidents": random.randint(10, 100),
        "critical_incidents": random.randint(0, 5),
        "generated_at": time.time()
    }
    
    response = {
        "status_code": 200,
        "message": f"Retrieved {stats['total_incidents']} incident statistics",
        "data": [
            {
                "type": "cache",
                "name": "incident_stats",
                "value": stats
            },
            {
                "type": "file", 
                "name": "daily_incident_report.json",
                "value": {
                    "report_date": time.strftime("%Y-%m-%d"),
                    "statistics": stats,
                    "summary": f"Total: {stats['total_incidents']}, Open: {stats['open_incidents']}, Critical: {stats['critical_incidents']}"
                }
            },
            {
                "type": "db",
                "name": "daily_stats",
                "value": stats
            }
        ]
    }
    
    return response


# Backward compatibility - simple string return
def legacy_create_incident(summary: str) -> str:
    """Legacy function that returns simple string (for backward compatibility)"""
    incident_number = f"INC{random.randint(100000, 999999)}"
    return f"Created incident {incident_number}: {summary}"


if __name__ == "__main__":
    # Test the functions
    print("=== Testing ServiceNow Plugin ===\n")
    
    # Test structured response
    result = create_incident("Test incident", "This is a test", "2")
    print("Structured Response:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test legacy response
    result = legacy_create_incident("Legacy test incident")
    print("Legacy Response:")
    print(result)
