"""
Example printer plugin for the Octopus framework
"""

import logging

def print_something():
    """Print a message using the logger"""
    logger = logging.getLogger("octopus_server.printer")   
    logger.info("This is a message from the printer module.")
    return "Message printed successfully"