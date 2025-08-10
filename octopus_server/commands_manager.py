"""
🔗 COMMANDS MANAGER
==================

Global command queue management for client communication.
"""

# Global command queue for client communication
COMMANDS = {}

def add_command(hostname, command):
    """Add a command to the queue for a specific hostname."""
    COMMANDS.setdefault(hostname, []).append(command)
    return True

def get_commands(hostname):
    """Get and clear commands for a specific hostname."""
    return COMMANDS.pop(hostname, [])

def get_pending_commands(hostname):
    """Get commands without clearing them."""
    return COMMANDS.get(hostname, [])

def clear_commands(hostname):
    """Clear all commands for a specific hostname."""
    COMMANDS.pop(hostname, None)

def get_all_commands():
    """Get all pending commands for debugging."""
    return COMMANDS.copy()
