# Simple Logging Framework for Octopus Plugins

A lightweight and easy-to-use logging system for Octopus plugin development.

## Features

- **Simple Setup**: One-line logger initialization
- **Automatic Log Management**: Automatic file rotation and cleanup
- **Structured Logging**: Built-in support for execution logging and error context
- **Flexible Configuration**: Global and per-plugin configuration options
- **Multiple Outputs**: Log to files and/or console
- **JSON Support**: Structured logging for easy parsing

## Quick Start

### Basic Usage

```python
from logging_framework.plugin_logger import get_plugin_logger

# Get a logger for your plugin
logger = get_plugin_logger("my_plugin")

# Start logging
logger.info("Plugin started")
logger.debug("Processing data", item_count=10)
logger.warning("Rate limit approaching", requests_left=5)
logger.error("Failed to connect to API")
```

### Plugin Integration

```python
class MyPlugin:
    def __init__(self):
        self.logger = get_plugin_logger("my_plugin")
        self.logger.info("Plugin initialized")
    
    def execute_task(self, task_data):
        try:
            self.logger.info("Starting task", task_id=task_data["id"])
            
            # Your plugin logic here
            result = self.process_task(task_data)
            
            # Log successful execution
            self.logger.log_execution(
                action="execute_task",
                status="SUCCESS",
                duration=2.5,
                task_id=task_data["id"]
            )
            
            return result
            
        except Exception as e:
            # Log error with context
            self.logger.log_error_with_context(
                error=e,
                context={"task_data": task_data}
            )
            raise
```

## Configuration Options

### Per-Plugin Configuration

```python
logger = get_plugin_logger(
    "my_plugin",
    log_level="DEBUG",           # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_dir="custom_logs",       # Directory for log files
    console_output=False,        # Disable console output
    max_log_files=5             # Keep only 5 log files
)
```

### Global Configuration

```python
from logging_framework.plugin_logger import LoggerManager

# Configure all future loggers
LoggerManager.configure_all(
    log_level="DEBUG",
    log_dir="logs/plugins",
    console_output=True
)

# Change log level for all existing loggers
LoggerManager.set_log_level_all("WARNING")
```

## Log Output Format

### Standard Logs
```
2024-01-15 10:30:45 - plugin.my_plugin - INFO - Plugin started
2024-01-15 10:30:46 - plugin.my_plugin - DEBUG - Processing data | item_count=10
2024-01-15 10:30:47 - plugin.my_plugin - WARNING - Rate limit approaching | requests_left=5
```

### Execution Logs (JSON format)
```
2024-01-15 10:30:48 - plugin.my_plugin - INFO - EXECUTION: {"action":"execute_task","status":"SUCCESS","timestamp":"2024-01-15T10:30:48","plugin":"my_plugin","duration_seconds":2.5,"task_id":"task_001"}
```

### Error Logs (JSON format)
```
2024-01-15 10:30:49 - plugin.my_plugin - ERROR - ERROR: {"error_type":"ValueError","error_message":"Invalid data format","plugin":"my_plugin","timestamp":"2024-01-15T10:30:49","context":{"task_data":{"id":"task_001"}}}
```

## Log Files

- **Location**: `logs/` directory (configurable)
- **Naming**: `{plugin_name}_{YYYYMMDD}.log`
- **Rotation**: Daily rotation with automatic cleanup
- **Retention**: Configurable number of files to keep (default: 10)

## API Reference

### PluginLogger Methods

- `debug(message, **kwargs)` - Log debug message
- `info(message, **kwargs)` - Log info message  
- `warning(message, **kwargs)` - Log warning message
- `error(message, **kwargs)` - Log error message
- `critical(message, **kwargs)` - Log critical message
- `log_execution(action, status, duration=None, **details)` - Log structured execution info
- `log_error_with_context(error, context=None)` - Log error with additional context

### LoggerManager Methods

- `get_logger(plugin_name, **config)` - Get or create plugin logger
- `configure_all(**config)` - Set default configuration for all loggers
- `set_log_level_all(log_level)` - Change log level for all existing loggers
- `get_all_loggers()` - Get all registered loggers

## Examples

See `example_usage.py` for complete examples including:
- Basic logging
- Error handling with context
- Custom configuration
- Global configuration management
- Complete plugin integration

## Installation

Simply copy the `logging_framework` directory to your project and import:

```python
from logging_framework.plugin_logger import get_plugin_logger
```

No additional dependencies required - uses only Python standard library.
