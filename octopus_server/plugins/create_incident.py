#!/usr/bin/env python3
"""
Incident Creation Plugin for Octopus Task Management System

This plugin creates incident tickets for system issues, outages, and problems.
Supports priority levels, descriptions, and automatic notification.
"""

# NLP: keywords: incident, issue, problem, alert, ticket, bug, case, outage, down, failure, error
# NLP: example: create urgent incident for database server down
# NLP: example: report P1 issue with API gateway not responding  
# NLP: example: file critical ticket for payment system failure
# NLP: example: log problem with email service outage

import logging
import asyncio

logger = logging.getLogger("octopus_server")

def run(priority="P3", description="System issue detected", assignee=None, *args, **kwargs):
    """
    Create an incident ticket
    
    Args:
        priority (str): Priority level (P1-P4, where P1 is highest)
        description (str): Detailed description of the incident
        assignee (str): Who to assign the incident to (optional)
    
    Returns:
        str: Incident creation result
    """
    # If called synchronously, run the async logic in an event loop and return the result
    async def _run():
        logger.info(f"Creating incident - Priority: {priority}, Description: {description}")
        if assignee:
            logger.info(f"Assigning incident to: {assignee}")
        
        await asyncio.sleep(1)  # Simulate async work
        
        incident_id = f"INC-{hash(description) % 10000:04d}"
        result = f"Incident {incident_id} created successfully"
        
        logger.info(f"Incident creation complete: {result}")
        return result
    
    return asyncio.run(_run())
