"""
Example usage of the Octopus Plugin Logging Framework
"""

# Import the logging framework
from logging_framework.plugin_logger import get_plugin_logger, LoggerManager

# Example 1: Basic logging in a plugin
def example_plugin_basic_logging():
    """Example of basic logging usage in a plugin"""
    
    # Get a logger for your plugin
    logger = get_plugin_logger("create_incident")
    
    # Basic logging
    logger.info("Plugin started")
    logger.debug("Processing incident data", incident_id="INC001", priority="HIGH")
    logger.warning("API rate limit approaching", requests_remaining=10)
    logger.error("Failed to create incident", error_code="API_ERROR")
    
    # Log execution results
    logger.log_execution(
        action="create_incident",
        status="SUCCESS",
        duration=2.5,
        incident_id="INC001",
        api_endpoint="/incidents"
    )

# Example 2: Error logging with context
def example_plugin_error_logging():
    """Example of error logging with context"""
    
    logger = get_plugin_logger("create_incident")
    
    try:
        # Simulate some plugin operation
        raise ValueError("Invalid incident data format")
    except Exception as e:
        # Log error with context
        logger.log_error_with_context(
            error=e,
            context={
                "incident_data": {"title": "Test", "priority": "HIGH"},
                "api_url": "https://api.example.com",
                "retry_count": 3
            }
        )

# Example 3: Custom configuration
def example_plugin_custom_config():
    """Example of plugin with custom logging configuration"""
    
    # Create logger with custom settings
    logger = get_plugin_logger(
        "my_plugin",
        log_level="DEBUG",
        log_dir="custom_logs",
        console_output=False,  # Only log to file
        max_log_files=5
    )
    
    logger.debug("This will be logged to file only")
    logger.info("Plugin operation completed")

# Example 4: Using LoggerManager for global configuration
def example_global_configuration():
    """Example of configuring logging globally"""
    
    # Configure all loggers to use DEBUG level
    LoggerManager.configure_all(
        log_level="DEBUG",
        log_dir="logs/plugins",
        console_output=True
    )
    
    # Get loggers - they will use the global configuration
    logger1 = get_plugin_logger("plugin_one")
    logger2 = get_plugin_logger("plugin_two")
    
    logger1.debug("This will show because we set DEBUG globally")
    logger2.info("This plugin uses the same configuration")
    
    # Change log level for all existing loggers
    LoggerManager.set_log_level_all("WARNING")
    
    logger1.info("This won't show anymore")
    logger1.warning("But this will show")

# Example 5: Complete plugin example
class ExamplePlugin:
    """Example plugin class with integrated logging"""
    
    def __init__(self, plugin_name="example_plugin"):
        self.logger = get_plugin_logger(plugin_name)
        self.logger.info("Plugin initialized", plugin_name=plugin_name)
    
    def execute_task(self, task_data):
        """Execute a task with comprehensive logging"""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting task execution", task_id=task_data.get("id"))
            
            # Simulate task processing
            self.logger.debug("Processing task data", data_size=len(str(task_data)))
            
            # Simulate some work
            time.sleep(0.1)
            
            # Check for errors
            if task_data.get("simulate_error"):
                raise RuntimeError("Simulated task error")
            
            # Success
            duration = time.time() - start_time
            self.logger.log_execution(
                action="execute_task",
                status="SUCCESS",
                duration=duration,
                task_id=task_data.get("id"),
                result="Task completed successfully"
            )
            
            return {"status": "success", "duration": duration}
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error with context
            self.logger.log_error_with_context(
                error=e,
                context={
                    "task_data": task_data,
                    "duration": duration,
                    "execution_stage": "processing"
                }
            )
            
            # Log failed execution
            self.logger.log_execution(
                action="execute_task",
                status="FAILED",
                duration=duration,
                task_id=task_data.get("id"),
                error=str(e)
            )
            
            return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    # Run examples
    print("Running logging framework examples...")
    
    example_plugin_basic_logging()
    example_plugin_error_logging()
    example_plugin_custom_config()
    example_global_configuration()
    
    # Test plugin class
    plugin = ExamplePlugin()
    plugin.execute_task({"id": "task_001", "data": "test"})
    plugin.execute_task({"id": "task_002", "simulate_error": True})
    
    print("Examples completed. Check the logs directory for output files.")
