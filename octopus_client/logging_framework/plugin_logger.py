"""
Simple Logging Framework for Octopus Plugins

A lightweight logging system designed for plugin development with 
automatic log management, formatting, and configuration.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

class PluginLogger:
    """
    Simple logger for plugins with automatic setup and configuration
    """
    
    def __init__(
        self,
        plugin_name: str,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_log_files: int = 10,
        console_output: bool = True
    ):
        """
        Initialize plugin logger
        
        Args:
            plugin_name: Name of the plugin (used in log filename)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory to store log files
            max_log_files: Maximum number of log files to keep
            console_output: Whether to also output to console
        """
        self.plugin_name = plugin_name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = Path(log_dir)
        self.max_log_files = max_log_files
        self.console_output = console_output
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup the logger with file and console handlers"""
        # Create logger
        logger = logging.getLogger(f"plugin.{self.plugin_name}")
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        log_file = self.log_dir / f"{self.plugin_name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler (if enabled)
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Clean up old log files
        self._cleanup_old_logs()
        
        return logger
    
    def _cleanup_old_logs(self):
        """Remove old log files to keep only max_log_files"""
        try:
            log_files = list(self.log_dir.glob(f"{self.plugin_name}_*.log"))
            if len(log_files) > self.max_log_files:
                # Sort by creation time and remove oldest
                log_files.sort(key=lambda x: x.stat().st_ctime)
                for old_file in log_files[:-self.max_log_files]:
                    old_file.unlink()
                    self.logger.info(f"Removed old log file: {old_file.name}")
        except Exception as e:
            print(f"Warning: Failed to cleanup old logs: {e}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def log_execution(self, action: str, status: str, duration: Optional[float] = None, **details):
        """
        Log plugin execution with structured format
        
        Args:
            action: What action was performed
            status: Status (SUCCESS, FAILED, TIMEOUT, etc.)
            duration: Execution duration in seconds
            **details: Additional details to log
        """
        log_data = {
            "action": action,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "plugin": self.plugin_name
        }
        
        if duration is not None:
            log_data["duration_seconds"] = round(duration, 3)
        
        log_data.update(details)
        
        # Log as structured JSON for easy parsing
        self.info(f"EXECUTION: {json.dumps(log_data, separators=(',', ':'))}")
    
    def log_error_with_context(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log error with additional context information
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "plugin": self.plugin_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            error_data["context"] = context
        
        self.error(f"ERROR: {json.dumps(error_data, separators=(',', ':'))}")
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with optional key-value pairs"""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{message} | {context}"
        return message

class LoggerManager:
    """
    Manages multiple plugin loggers with shared configuration
    """
    
    _instances: Dict[str, PluginLogger] = {}
    _default_config = {
        "log_level": "INFO",
        "log_dir": "logs",
        "max_log_files": 10,
        "console_output": True
    }
    
    @classmethod
    def get_logger(cls, plugin_name: str, **config_overrides) -> PluginLogger:
        """
        Get or create a logger for a plugin
        
        Args:
            plugin_name: Name of the plugin
            **config_overrides: Configuration overrides
            
        Returns:
            PluginLogger instance
        """
        if plugin_name not in cls._instances:
            config = cls._default_config.copy()
            config.update(config_overrides)
            cls._instances[plugin_name] = PluginLogger(plugin_name, **config)
        
        return cls._instances[plugin_name]
    
    @classmethod
    def configure_all(cls, **config):
        """
        Update default configuration for all future loggers
        
        Args:
            **config: Configuration parameters
        """
        cls._default_config.update(config)
    
    @classmethod
    def set_log_level_all(cls, log_level: str):
        """
        Set log level for all existing loggers
        
        Args:
            log_level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level = getattr(logging, log_level.upper(), logging.INFO)
        for logger in cls._instances.values():
            logger.logger.setLevel(level)
            for handler in logger.logger.handlers:
                handler.setLevel(level)
    
    @classmethod
    def get_all_loggers(cls) -> Dict[str, PluginLogger]:
        """Get all registered loggers"""
        return cls._instances.copy()

# Convenience function for quick logger access
def get_plugin_logger(plugin_name: str, **config) -> PluginLogger:
    """
    Quick access to plugin logger
    
    Args:
        plugin_name: Name of the plugin
        **config: Logger configuration
        
    Returns:
        PluginLogger instance
    """
    return LoggerManager.get_logger(plugin_name, **config)
