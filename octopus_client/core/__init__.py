"""
🐙 OCTOPUS CLIENT CORE MODULES
==============================

Core functionality modules for the client application.
"""

from .task_execution import TaskExecutor
from .server_communication import ServerCommunicator
from .status_manager import StatusManager

__all__ = ['TaskExecutor', 'ServerCommunicator', 'StatusManager']
