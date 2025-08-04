#!/usr/bin/env python3
"""
Notification Plugin
===================
Plugin for sending notifications and alerts (async examples)
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

def send_simple_notification(message: str, priority: str = "normal", recipient: str = "admin"):
    """
    Send a simple notification (synchronous).
    
    Args:
        message: Notification message
        priority: Priority level (low, normal, high, urgent)
        recipient: Recipient of the notification
    
    Returns:
        str: Notification status
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result = f"Notification Sent:\n"
        result += f"  Timestamp: {timestamp}\n"
        result += f"  Recipient: {recipient}\n"
        result += f"  Priority: {priority.upper()}\n"
        result += f"  Message: {message}\n"
        result += f"  Status: ✓ Delivered\n"
        
        return result
        
    except Exception as e:
        return f"Error sending notification: {str(e)}"

async def send_async_notification(message: str, delay: int = 0, retry_count: int = 1):
    """
    Send an asynchronous notification with optional delay and retry.
    
    Args:
        message: Notification message
        delay: Delay before sending in seconds (default: 0)
        retry_count: Number of retry attempts (default: 1)
    
    Returns:
        str: Notification status
    """
    try:
        if delay > 0:
            await asyncio.sleep(delay)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simulate async operation
        for attempt in range(retry_count):
            try:
                # Simulate network delay
                await asyncio.sleep(0.5)
                
                result = f"Async Notification Sent:\n"
                result += f"  Timestamp: {timestamp}\n"
                result += f"  Message: {message}\n"
                result += f"  Delay: {delay} seconds\n"
                result += f"  Attempt: {attempt + 1}/{retry_count}\n"
                result += f"  Status: ✓ Delivered (async)\n"
                
                return result
                
            except Exception as e:
                if attempt == retry_count - 1:
                    raise e
                await asyncio.sleep(1)  # Wait before retry
        
    except Exception as e:
        return f"Error sending async notification: {str(e)}"

def schedule_reminder(reminder_text: str, minutes: int = 5):
    """
    Schedule a reminder (demonstration of scheduling).
    
    Args:
        reminder_text: Text for the reminder
        minutes: Minutes from now to remind (default: 5)
    
    Returns:
        str: Scheduling confirmation
    """
    try:
        now = datetime.now()
        reminder_time = now.timestamp() + (minutes * 60)
        reminder_datetime = datetime.fromtimestamp(reminder_time)
        
        result = f"Reminder Scheduled:\n"
        result += f"  Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"  Reminder Time: {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"  Minutes from now: {minutes}\n"
        result += f"  Reminder Text: {reminder_text}\n"
        result += f"  Status: ✓ Scheduled\n"
        
        return result
        
    except Exception as e:
        return f"Error scheduling reminder: {str(e)}"

async def batch_notify(recipients: str, message: str, interval: float = 1.0):
    """
    Send notifications to multiple recipients with interval (async).
    
    Args:
        recipients: Comma-separated list of recipients
        message: Message to send to all recipients
        interval: Interval between sends in seconds (default: 1.0)
    
    Returns:
        str: Batch notification status
    """
    try:
        recipient_list = [r.strip() for r in recipients.split(',')]
        
        result = f"Batch Notification Started:\n"
        result += f"  Recipients: {len(recipient_list)}\n"
        result += f"  Message: {message}\n"
        result += f"  Interval: {interval}s\n\n"
        
        for i, recipient in enumerate(recipient_list):
            if i > 0:  # No delay for first recipient
                await asyncio.sleep(interval)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            result += f"  [{timestamp}] Sent to {recipient}\n"
        
        result += f"\n✓ All {len(recipient_list)} notifications sent"
        
        return result
        
    except Exception as e:
        return f"Error in batch notification: {str(e)}"

def create_alert(alert_type: str = "info", title: str = "Alert", message: str = "Default alert message"):
    """
    Create an alert message with different types.
    
    Args:
        alert_type: Type of alert (info, warning, error, success)
        title: Alert title
        message: Alert message content
    
    Returns:
        str: Formatted alert
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Define alert symbols
        symbols = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        symbol = symbols.get(alert_type.lower(), "📢")
        
        result = f"{symbol} {alert_type.upper()} ALERT {symbol}\n"
        result += f"=" * 40 + "\n"
        result += f"Title: {title}\n"
        result += f"Time: {timestamp}\n"
        result += f"Type: {alert_type.upper()}\n"
        result += f"Message: {message}\n"
        result += f"=" * 40 + "\n"
        
        return result
        
    except Exception as e:
        return f"Error creating alert: {str(e)}"

def log_event(event: str, category: str = "general", level: str = "info"):
    """
    Log an event with categorization.
    
    Args:
        event: Event description
        category: Event category (general, system, user, error)
        level: Log level (debug, info, warning, error)
    
    Returns:
        str: Log entry confirmation
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result = f"Event Logged:\n"
        result += f"  Timestamp: {timestamp}\n"
        result += f"  Category: {category.upper()}\n"
        result += f"  Level: {level.upper()}\n"
        result += f"  Event: {event}\n"
        result += f"  Status: ✓ Recorded\n"
        
        # Add level-specific formatting
        if level.lower() == "error":
            result = "🔴 " + result
        elif level.lower() == "warning":
            result = "🟡 " + result
        elif level.lower() == "info":
            result = "🔵 " + result
        else:
            result = "⚪ " + result
        
        return result
        
    except Exception as e:
        return f"Error logging event: {str(e)}"
