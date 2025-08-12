# 🔌 Plugin Response Specification

## Overview

The Octopus system now supports structured plugin responses that allow plugins to return not just simple results, but also perform automatic data operations like caching, file writing, and database storage.

## Response Format

Plugins can return either:
1. **Simple responses** (backward compatible): strings, numbers, etc.
2. **Structured responses**: JSON objects with specific format

### Structured Response Schema

```json
{
    "status_code": 200,           // HTTP-style status code
    "message": "Task completed",  // Human-readable message
    "data": [                     // Array of data operations (optional)
        {
            "type": "cache",      // Operation type: cache, file, db
            "name": "key_name",   // Key/path/identifier
            "value": "data"       // Value to store
        }
    ]
}
```

## Status Code Translation

The system automatically translates HTTP-style status codes to execution status:

| Status Code Range | Execution Status | Description |
|------------------|------------------|-------------|
| 200-299 | `Completed` | Success |
| 400-499 | `Failed` | Client errors |
| 500-599 | `Failed` | Server errors |
| Other | `Failed` | Unknown errors |

## Data Operation Types

### 1. Cache Operations

Store data in system cache for quick access.

```json
{
    "type": "cache",
    "name": "incident_id",
    "value": "INC123456"
}
```

**Client-side behavior:**
- Creates local cache files in `cache/` directory
- Files named with task context: `plugin_{task_id}_{name}.json`
- Includes timestamp and execution context

### 2. File Operations

Write data to files for persistence.

```json
{
    "type": "file", 
    "name": "report.json",
    "value": {"key": "data"}
}
```

**Client-side behavior:**
- Creates files in `plugin_outputs/{task_id}/{client}/` directory
- Supports JSON objects (auto-formatted) and strings
- Automatically creates directory structure

### 3. Database Operations

Store data in the execution database.

```json
{
    "type": "db",
    "name": "operation_result", 
    "value": {"status": "completed"}
}
```

**Client-side behavior:**
- Prepares data for server-side database insertion
- Creates operation files in `db_operations/` directory
- Server can process these for actual database storage

## Example Plugin Implementations

### Simple Success Response

```python
def create_ticket():
    return {
        "status_code": 201,
        "message": "Ticket #12345 created successfully",
        "data": [
            {
                "type": "cache",
                "name": "last_ticket_id", 
                "value": "12345"
            }
        ]
    }
```

### Complex Data Operations

```python
def scrape_website(url):
    scraped_data = perform_scraping(url)
    
    return {
        "status_code": 200,
        "message": f"Scraped {len(scraped_data)} items from {url}",
        "data": [
            {
                "type": "cache",
                "name": "last_scrape_timestamp",
                "value": time.time()
            },
            {
                "type": "file",
                "name": f"scrape_results_{int(time.time())}.json",
                "value": scraped_data
            },
            {
                "type": "db", 
                "name": "scrape_summary",
                "value": {
                    "url": url,
                    "items_count": len(scraped_data),
                    "scraped_at": time.time()
                }
            }
        ]
    }
```

### Error Response

```python
def api_call():
    try:
        result = make_api_request()
        return {
            "status_code": 200,
            "message": "API call successful",
            "data": [...]
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"API call failed: {str(e)}",
            "data": [
                {
                    "type": "cache",
                    "name": "last_error",
                    "value": str(e)
                },
                {
                    "type": "file",
                    "name": "error_log.txt", 
                    "value": f"{time.ctime()}: {str(e)}"
                }
            ]
        }
```

## Backward Compatibility

Existing plugins that return simple strings/values continue to work without changes:

```python
# This still works
def legacy_function():
    return "Task completed successfully"

# This also works
def another_legacy():
    return 42
```

The system automatically detects whether a response is structured or simple.

## Best Practices

### 1. Use Appropriate Status Codes
- `200`: Success
- `201`: Created (for creation operations)
- `400`: Bad input/validation errors
- `404`: Resource not found
- `500`: Internal/unexpected errors

### 2. Provide Clear Messages
- Make messages human-readable
- Include relevant details (IDs, counts, etc.)
- Keep them concise but informative

### 3. Use Meaningful Data Operations
- **Cache**: For data that might be referenced by other tasks
- **File**: For reports, logs, or structured data exports
- **DB**: For audit trails, statistics, or relationship data

### 4. Handle Errors Gracefully
- Return appropriate error status codes
- Log errors to files for debugging
- Cache error information for monitoring

### 5. Security Considerations
- File operations are sandboxed to safe directories
- No directory traversal allowed
- Database operations are prepared but not executed directly

## Migration Guide

To update existing plugins to use structured responses:

1. **Identify data to persist**: What should be cached, logged, or stored?
2. **Wrap your return value**: Instead of `return result`, use the structured format
3. **Add appropriate data operations**: Cache important values, log to files, store summaries in DB
4. **Set proper status codes**: Use HTTP-style codes to indicate success/failure
5. **Test thoroughly**: Ensure both success and error paths work correctly

## Example: Converting a Legacy Plugin

**Before:**
```python
def create_incident(summary):
    incident_id = call_api(summary)
    return f"Created incident {incident_id}"
```

**After:**
```python
def create_incident(summary):
    try:
        incident_id = call_api(summary)
        return {
            "status_code": 201,
            "message": f"Created incident {incident_id}",
            "data": [
                {
                    "type": "cache",
                    "name": "last_incident_id",
                    "value": incident_id
                },
                {
                    "type": "db",
                    "name": "incident_creation",
                    "value": {
                        "incident_id": incident_id,
                        "summary": summary,
                        "created_at": time.time()
                    }
                }
            ]
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Failed to create incident: {str(e)}",
            "data": [
                {
                    "type": "cache",
                    "name": "last_error",
                    "value": str(e)
                }
            ]
        }
```

## Testing

The system includes test examples in:
- `octopus_client/plugins/servicenow_example.py`
- `octopus_client/plugins/webscraping_example.py`
- `octopus_server/plugin_response_spec.py`

Run these to see the structured response format in action.
