"""
Logging Framework for Octopus Plugins

A simple and lightweight logging system for plugin development.
"""

from .plugin_logger import PluginLogger, LoggerManager, get_plugin_logger

__version__ = "1.0.0"
__author__ = "Octopus System"

__all__ = [
    "PluginLogger",
    "LoggerManager", 
    "get_plugin_logger"
]
